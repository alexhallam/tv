pub mod config;
pub mod formatting;
pub mod readers;
pub mod types;

pub use config::*;
pub use formatting::*;
pub use readers::*;
pub use types::*;

use std::error::Error;

/// Main entry point for formatting tabular data
pub fn format_table(
    data: Vec<Vec<String>>,
    headers: Option<Vec<String>>,
    options: &FormatOptions,
) -> Result<String, Box<dyn Error>> {
    let mut output = String::new();
    
    // Add dimensions info if enabled
    if !options.no_dimensions {
        let rows = data.len();
        let cols = data.get(0).map(|row| row.len()).unwrap_or(0);
        if options.use_color {
            output.push_str(&format_dimensions_colored(rows, cols, &options.colors));
        } else {
            output.push_str(&format!("tv dim: {} x {}\n", rows, cols));
        }
    }
    
    // Format the table
    let formatted_table = format_data_table(data, headers, options)?;
    output.push_str(&formatted_table);
    
    Ok(output)
}

/// Format CSV file from path
pub fn format_csv_file(
    file_path: &str,
    options: &FormatOptions,
) -> Result<String, Box<dyn Error>> {
    let (headers, data) = readers::read_csv_file(file_path, options)?;
    format_table(data, Some(headers), options)
}

/// Format Parquet file from path
pub fn format_parquet_file(
    file_path: &str,
    options: &FormatOptions,
) -> Result<String, Box<dyn Error>> {
    let (headers, data) = readers::read_parquet_file(file_path, options)?;
    format_table(data, Some(headers), options)
}

fn format_dimensions_colored(rows: usize, cols: usize, colors: &ColorScheme) -> String {
    use owo_colors::OwoColorize;
    format!(
        "tv dim: {} x {}\n",
        rows.truecolor(colors.meta_color[0], colors.meta_color[1], colors.meta_color[2]),
        cols.truecolor(colors.meta_color[0], colors.meta_color[1], colors.meta_color[2])
    )
}