use csv::ReaderBuilder;
use owo_colors::OwoColorize;
use std::error::Error;
use std::fs::File;
use std::io::BufReader;
use crossterm::terminal::size as term_size;

use crate::types::{ColorScheme, FormatOptions};
use tidy_viewer_core::{format_strings, is_na_string_padded, is_negative_number};

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

    // Build columns including header (if provided) followed by data rows
    let mut columns: Vec<Vec<&str>> = vec![vec![]; cols];

    if let Some(ref hdrs) = headers {
        for (col_idx, header) in hdrs.iter().enumerate().take(cols) {
            columns[col_idx].push(header.as_str());
        }
    }

    for row in data.iter().take(display_rows) {
        for (col_idx, cell) in row.iter().enumerate() {
            if col_idx < cols {
                columns[col_idx].push(cell.as_str());
            }
        }
    }

    // Format columns using core format_strings (ensures uniform widths across header+data)
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

    // Determine how many columns fit on the current terminal width (like CLI)
    let term_width: usize = term_size().map(|(w, _)| w as usize).unwrap_or(80);
    let mut calc_width = String::new();
    if !options.no_row_numbering {
        calc_width.push_str(&format!("{: >6}  ", ""));
    }
    let mut num_cols_to_print = 0usize;
    for col in 0..cols {
        // header row if present, else the first data row (index 0)
        let top_row_idx = 0usize;
        let cell = formatted_columns
            .get(col)
            .and_then(|c| c.get(top_row_idx))
            .map(|s| s.as_str())
            .unwrap_or("");
        calc_width.push_str(cell);
        let total_width = calc_width.chars().count();
        if total_width > term_width {
            break;
        }
        num_cols_to_print = col + 1;
    }
    // If nothing fit (very narrow terminal), still show at least one column if possible
    if num_cols_to_print == 0 && cols > 0 {
        num_cols_to_print = 1;
    }

    // Helper to append a pre-formatted row at row_idx
    let mut push_formatted_row = |row_idx: usize, row_num: usize| {
        if !options.no_row_numbering {
            if row_num > 0 {
                let row_num_str = format!("{: >6}  ", row_num);
                if options.use_color {
                    let [r, g, b] = options.colors.meta_color;
                    output.push_str(&row_num_str.truecolor(r, g, b).to_string());
                } else {
                    output.push_str(&row_num_str);
                }
            } else {
                // header spacing
                output.push_str("        ");
            }
        }

        for (col_idx, col) in formatted_columns.iter().enumerate() {
            if col_idx >= num_cols_to_print {
                break;
            }
            // Safe access (columns are uniform post-format)
            let cell = col.get(row_idx).map(|s| s.as_str()).unwrap_or("NA");

            if options.use_color {
                let colored = if row_num == 0 {
                    let [r, g, b] = options.colors.header_color;
                    cell.truecolor(r, g, b).to_string()
                } else if is_na_string_padded(cell) {
                    let [r, g, b] = options.colors.na_color;
                    cell.truecolor(r, g, b).to_string()
                } else if is_negative_number(cell) {
                    let [r, g, b] = options.colors.neg_num_color;
                    cell.truecolor(r, g, b).to_string()
                } else {
                    let [r, g, b] = options.colors.std_color;
                    cell.truecolor(r, g, b).to_string()
                };
                output.push_str(&colored);
            } else {
                output.push_str(cell);
            }
        }

        output.push('\n');
    };

    // Header row (only if headers were provided)
    if headers.is_some() {
        push_formatted_row(0, 0);
    }

    // Data rows: start after header if present
    let data_start_idx = if headers.is_some() { 1 } else { 0 };
    let data_end_idx = data_start_idx + display_rows;
    for (row_idx, row_num) in (data_start_idx..data_end_idx).zip(1..) {
        push_formatted_row(row_idx, row_num);
    }

    // Add "more rows" indicator if truncated (placed before footer, like the CLI)
    let mut appended_meta_line = false;
    if display_rows < rows {
        if !options.no_row_numbering {
            output.push_str("        ");
        }
        let remaining = rows - display_rows;
        output.push_str(&format!("… with {} more rows", remaining));
        appended_meta_line = true;
    }

    // Add "and N more variables: …" if columns are truncated
    if num_cols_to_print < cols {
        if !appended_meta_line {
            if !options.no_row_numbering {
                output.push_str("        ");
            }
            // start the meta line even if rows are not truncated
            output.push_str("…");
            appended_meta_line = true;
        }
        let remainder_cols = cols - num_cols_to_print;
        if options.use_color {
            let [r, g, b] = options.colors.meta_color;
            output.push_str(&format!(
                " and {} more variables:",
                remainder_cols.truecolor(r, g, b)
            ));
        } else {
            output.push_str(&format!(" and {} more variables:", remainder_cols));
        }
        if let Some(ref hdrs) = headers {
            for (i, name) in hdrs.iter().enumerate().skip(num_cols_to_print) {
                if options.use_color {
                    let [r, g, b] = options.colors.meta_color;
                    output.push_str(" ");
                    output.push_str(&name.truecolor(r, g, b).to_string());
                } else {
                    output.push_str(" ");
                    output.push_str(name);
                }
                if i + 1 < cols {
                    if options.use_color {
                        let [r, g, b] = options.colors.meta_color;
                        output.push_str(&",".truecolor(r, g, b).to_string());
                    } else {
                        output.push_str(",");
                    }
                }
            }
        }
    }

    // Footer
    if let Some(ref footer) = options.footer {
        if !options.no_row_numbering {
            output.push_str("        ");
        }
        if options.use_color {
            let [r, g, b] = options.colors.meta_color;
            output.push_str(&footer.truecolor(r, g, b).to_string());
        } else {
            output.push_str(footer);
        }
        output.push('\n');
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






