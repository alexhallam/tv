use std::error::Error;
use std::fs::File;
use std::io::BufReader;
use csv::ReaderBuilder;
use owo_colors::OwoColorize;
use unicode_width::UnicodeWidthStr;

use crate::types::{FormatOptions, ColorScheme, ValueType};
use crate::datatype::{format_strings, calculate_column_width, is_negative_number, is_na};

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
                options.significant_figures as u8,
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
                h.get(idx).map(|s| UnicodeWidthStr::width(s.as_str())).unwrap_or(0)
            } else {
                0
            };
            let content_width = calculate_column_width(col, options.min_col_width, options.max_col_width);
            header_width.max(content_width)
        })
        .collect();
    
    // Add row numbers column if enabled
    let total_width = if !options.no_row_numbering {
        let row_num_width = format!("{}", display_rows).len() + 1;
        column_widths.iter().sum::<usize>() + column_widths.len() * 3 + row_num_width
    } else {
        column_widths.iter().sum::<usize>() + column_widths.len() * 3
    };
    
    // Format header
    if let Some(ref headers) = headers {
        output.push_str(&format_header_row(headers, &column_widths, options));
        output.push('\n');
        output.push_str(&format_separator_row(&column_widths, options));
        output.push('\n');
    }
    
    // Format data rows
    for (row_idx, row) in data.iter().take(display_rows).enumerate() {
        let formatted_row = format_data_row(row, row_idx + 1, &column_widths, options);
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
        output.push_str(&format!("\n... {} more rows", remaining));
    }
    
    Ok(output)
}

/// Format CSV file from path
pub fn format_csv_file(
    file_path: &str,
    options: &FormatOptions,
) -> Result<String, Box<dyn Error>> {
    let file = File::open(file_path)?;
    let mut reader = ReaderBuilder::new()
        .delimiter(options.delimiter.as_bytes()[0])
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
        row.push_str("  # ");
    }
    
    for (idx, (header, width)) in headers.iter().zip(widths.iter()).enumerate() {
        if idx > 0 {
            row.push_str(" │ ");
        }
        
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

fn format_separator_row(widths: &[usize], options: &FormatOptions) -> String {
    let mut row = String::new();
    
    if !options.no_row_numbering {
        row.push_str("────");
    }
    
    for (idx, width) in widths.iter().enumerate() {
        if idx > 0 {
            row.push_str("─┼─");
        }
        row.push_str(&"─".repeat(*width));
    }
    
    row
}

fn format_data_row(
    row: &[String],
    row_num: usize,
    widths: &[usize],
    options: &FormatOptions,
) -> String {
    let mut output = String::new();
    
    if !options.no_row_numbering {
        output.push_str(&format!("{:3} ", row_num));
    }
    
    for (idx, (cell, width)) in row.iter().zip(widths.iter()).enumerate() {
        if idx > 0 {
            output.push_str(" │ ");
        }
        
        let padded = format!("{:>width$}", cell, width = width);
        
        if options.use_color {
            let colored = if is_na(cell) {
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