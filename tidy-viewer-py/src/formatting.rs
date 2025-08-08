use csv::ReaderBuilder;
use owo_colors::OwoColorize;
use std::error::Error;
use std::fs::File;
use std::io::BufReader;
use unicode_width::UnicodeWidthStr;

use crate::types::{ColorScheme, FormatOptions};
use tidy_viewer_core::{calculate_column_width, format_strings, is_na, is_negative_number};

/// Main entry point for formatting tabular data
pub fn format_table(
    data: Vec<Vec<String>>,
    headers: Option<Vec<String>>,
    options: &FormatOptions,
) -> Result<String, Box<dyn Error>> {
    if data.is_empty() {
        return Ok("No data to display".to_string());
    }

    let mut output = String::new();

    // Add title if provided
    if let Some(ref title) = options.title {
        output.push_str(&format!("{}\n\n", title));
    }

    // Calculate dimensions
    let rows = data.len();
    let cols = data.get(0).map(|row| row.len()).unwrap_or(0);

    // Add dimensions info if enabled
    if !options.no_dimensions {
        // Align with first column (same as row numbers)
        if !options.no_row_numbering {
            output.push_str("        ");
        }

        let dims_line = if options.use_color {
            format_dimensions_colored(rows, cols, &options.colors)
        } else {
            format!("tv dim: {} x {}\n", rows, cols)
        };
        output.push_str(&dims_line);
    }

    // Limit rows if max_rows is set
    let display_rows = if let Some(max) = options.max_rows {
        rows.min(max)
    } else {
        rows
    };

    // Transpose data for column-wise operations
    let mut columns: Vec<Vec<&str>> = vec![vec![]; cols];
    for row in data.iter().take(display_rows) {
        for (col_idx, cell) in row.iter().enumerate() {
            if col_idx < cols {
                columns[col_idx].push(cell.as_str());
            }
        }
    }

    // Format columns
    let formatted_columns: Vec<Vec<String>> = columns
        .iter()
        .map(|col| {
            format_strings(
                col,
                options.min_col_width,
                options.max_col_width,
                options.significant_figures as i64,
                options.preserve_scientific,
                options.max_decimal_width,
            )
        })
        .collect();

    // Calculate column widths
    let column_widths: Vec<usize> = formatted_columns
        .iter()
        .enumerate()
        .map(|(idx, col)| {
            let header_width = if let Some(ref h) = headers {
                h.get(idx)
                    .map(|s| UnicodeWidthStr::width(s.as_str()))
                    .unwrap_or(0)
            } else {
                0
            };
            let content_width =
                calculate_column_width(col, options.min_col_width, options.max_col_width);
            header_width.max(content_width)
        })
        .collect();

    // Add row numbers column if enabled
    let _total_width = if !options.no_row_numbering {
        let row_num_width = format!("{}", display_rows).len() + 1;
        column_widths.iter().sum::<usize>() + column_widths.len() * 3 + row_num_width
    } else {
        column_widths.iter().sum::<usize>() + column_widths.len() * 3
    };

    // Format header using the same logic as data rows
    if let Some(ref headers) = headers {
        // Format headers using the same logic as data
        let header_cols: Vec<Vec<&str>> = headers.iter().map(|h| vec![h.as_str()]).collect();
        let formatted_headers: Vec<Vec<String>> = header_cols
            .iter()
            .map(|col| {
                format_strings(
                    col,
                    options.min_col_width,
                    options.max_col_width,
                    options.significant_figures as i64,
                    options.preserve_scientific,
                    options.max_decimal_width,
                )
            })
            .collect();

        let header_row = format_data_row_from_columns(
            &formatted_headers,
            0, // First (and only) row
            0, // No row number for header
            &column_widths,
            options,
        );
        output.push_str(&header_row);
        output.push('\n');
    }

    // Format data rows using the pre-formatted columns
    for row_idx in 0..display_rows {
        let formatted_row = format_data_row_from_columns(
            &formatted_columns,
            row_idx,
            row_idx + 1,
            &column_widths,
            options,
        );
        output.push_str(&formatted_row);
        output.push('\n');
    }

    // Add footer if provided
    if let Some(ref footer) = options.footer {
        output.push_str(&format!("\n{}", footer));
    }

    // Add "more rows" indicator if truncated
    if display_rows < rows {
        let remaining = rows - display_rows;
        output.push_str(&format!("… with {} more rows", remaining));
    }

    Ok(output)
}

/// Format CSV file from path
pub fn format_csv_file(file_path: &str, options: &FormatOptions) -> Result<String, Box<dyn Error>> {
    let file = File::open(file_path)?;

    // Handle empty delimiter by using comma as default
    let delimiter = if options.delimiter.is_empty() {
        b','
    } else {
        options.delimiter.as_bytes()[0]
    };

    let mut reader = ReaderBuilder::new()
        .delimiter(delimiter)
        .from_reader(BufReader::new(file));

    // Read headers
    let headers = reader.headers()?.iter().map(|s| s.to_string()).collect();

    // Read data
    let mut data = Vec::new();
    for result in reader.records() {
        let record = result?;
        let row: Vec<String> = record.iter().map(|s| s.to_string()).collect();
        data.push(row);
    }

    format_table(data, Some(headers), options)
}

/// Format Parquet file from path
pub fn format_parquet_file(
    file_path: &str,
    options: &FormatOptions,
) -> Result<String, Box<dyn Error>> {
    use parquet::file::reader::{FileReader, SerializedFileReader};

    let file = File::open(file_path)?;
    let reader = SerializedFileReader::new(file)?;
    let iter = reader.get_row_iter(None)?;

    let mut data = Vec::new();
    let mut headers = Vec::new();

    // Extract column names from schema
    let schema = reader.metadata().file_metadata().schema_descr();
    let mut column_indices_to_include = Vec::new();

    for i in 0..schema.num_columns() {
        let column = schema.column(i);
        let column_name = column.name().to_lowercase();

        // Skip columns that are likely pandas index columns
        if column_name == "id" || column_name == "index" || column_name == "__index_level_0__" {
            continue;
        }

        headers.push(column.name().to_string());
        column_indices_to_include.push(i);
    }

    // Process all data rows
    for row_result in iter {
        let row = row_result?;
        let mut record_fields = Vec::new();

        for &col_index in &column_indices_to_include {
            if let Some(field) = row.get_column_iter().nth(col_index) {
                let value_str = format!("{}", field.1);
                // Remove quotes from string values to match CSV behavior
                let clean_value = if value_str.starts_with('"')
                    && value_str.ends_with('"')
                    && value_str.len() > 1
                {
                    value_str[1..value_str.len() - 1].to_string()
                } else {
                    value_str
                };
                record_fields.push(clean_value);
            } else {
                record_fields.push(String::new());
            }
        }
        data.push(record_fields);
    }

    format_table(data, Some(headers), options)
}

/// Format Arrow file from path
pub fn format_arrow_file(
    file_path: &str,
    options: &FormatOptions,
) -> Result<String, Box<dyn Error>> {
    use arrow::array::{Array, BooleanArray, Float64Array, Int64Array, StringArray};
    use arrow::datatypes::DataType;
    use arrow::error::ArrowError;
    use arrow::ipc::reader::FileReader as ArrowFileReader;

    let file = File::open(file_path)?;

    // Try to read as uncompressed first
    let reader = match ArrowFileReader::try_new(file, None) {
        Ok(reader) => reader,
        Err(ArrowError::InvalidArgumentError(msg)) if msg.contains("lz4") => {
            return Err("Arrow files with LZ4 compression are not supported".into());
        }
        Err(e) => return Err(e.into()),
    };

    let schema = reader.schema();

    let mut headers = Vec::new();
    let mut data = Vec::new();

    // Extract column names from schema
    for field in schema.fields() {
        headers.push(field.name().to_string());
    }

    // Read all batches and convert to StringRecords
    for batch_result in reader {
        let batch = batch_result?;
        let num_rows = batch.num_rows();
        let num_cols = batch.num_columns();

        for row_idx in 0..num_rows {
            let mut row_data = Vec::new();
            for col_idx in 0..num_cols {
                let array = batch.column(col_idx);
                let value = match array.data_type() {
                    DataType::Utf8 => {
                        let string_array = array.as_any().downcast_ref::<StringArray>().unwrap();
                        if array.is_null(row_idx) {
                            "NA".to_string()
                        } else {
                            string_array.value(row_idx).to_string()
                        }
                    }
                    DataType::Int64 => {
                        let int_array = array.as_any().downcast_ref::<Int64Array>().unwrap();
                        if array.is_null(row_idx) {
                            "NA".to_string()
                        } else {
                            int_array.value(row_idx).to_string()
                        }
                    }
                    DataType::Float64 => {
                        let float_array = array.as_any().downcast_ref::<Float64Array>().unwrap();
                        if array.is_null(row_idx) {
                            "NA".to_string()
                        } else {
                            float_array.value(row_idx).to_string()
                        }
                    }
                    DataType::Boolean => {
                        let bool_array = array.as_any().downcast_ref::<BooleanArray>().unwrap();
                        if array.is_null(row_idx) {
                            "NA".to_string()
                        } else {
                            bool_array.value(row_idx).to_string()
                        }
                    }
                    _ => {
                        // For other types, convert to string representation
                        "NA".to_string()
                    }
                };
                row_data.push(value);
            }
            data.push(row_data);
        }
    }

    format_table(data, Some(headers), options)
}

fn format_dimensions_colored(rows: usize, cols: usize, colors: &ColorScheme) -> String {
    let [r, g, b] = colors.meta_color;
    format!(
        "tv dim: {} x {}\n",
        rows.truecolor(r, g, b),
        cols.truecolor(r, g, b)
    )
}

fn format_header_row(headers: &[String], widths: &[usize], options: &FormatOptions) -> String {
    let mut row = String::new();

    if !options.no_row_numbering {
        row.push_str("     ");
    }

    for (idx, (header, width)) in headers.iter().zip(widths.iter()).enumerate() {
        let padded = format!("{:^width$}", header, width = width);
        if options.use_color {
            let [r, g, b] = options.colors.header_color;
            row.push_str(&padded.truecolor(r, g, b).to_string());
        } else {
            row.push_str(&padded);
        }
    }

    row
}

fn format_data_row_from_columns(
    formatted_columns: &[Vec<String>],
    row_idx: usize,
    row_num: usize,
    widths: &[usize],
    options: &FormatOptions,
) -> String {
    let mut output = String::new();

    if !options.no_row_numbering && row_num > 0 {
        let row_num_str = format!("{: >6}  ", row_num);
        if options.use_color {
            let [r, g, b] = options.colors.meta_color;
            output.push_str(&row_num_str.truecolor(r, g, b).to_string());
        } else {
            output.push_str(&row_num_str);
        }
    } else if !options.no_row_numbering {
        // For headers, add the same spacing as row numbers
        output.push_str("        ");
    }

    for (col_idx, formatted_col) in formatted_columns.iter().enumerate() {
        // Handle uneven rows by providing a default value if the cell doesn't exist
        let cell = if row_idx < formatted_col.len() {
            &formatted_col[row_idx]
        } else {
            "NA" // Default value for missing cells
        };

        let width = widths.get(col_idx).unwrap_or(&0);

        let padded = format!("{:<width$}", cell, width = width);

        if options.use_color {
            let colored = if row_num == 0 {
                // Header row - use header color
                let [r, g, b] = options.colors.header_color;
                padded.truecolor(r, g, b).to_string()
            } else if is_na(cell) {
                let [r, g, b] = options.colors.na_color;
                padded.truecolor(r, g, b).to_string()
            } else if is_negative_number(cell) {
                let [r, g, b] = options.colors.neg_num_color;
                padded.truecolor(r, g, b).to_string()
            } else {
                let [r, g, b] = options.colors.std_color;
                padded.truecolor(r, g, b).to_string()
            };
            output.push_str(&colored);
        } else {
            output.push_str(&padded);
        }
    }

    output
}
