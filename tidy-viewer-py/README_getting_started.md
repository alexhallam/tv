# Getting Started with tidy-viewer-py

This directory contains a comprehensive getting started script that demonstrates how to use the `tidy-viewer-py` package.

## Running the Getting Started Script

```bash
# From the tidy-viewer-py directory
uv run python getting_started.py
```

## What the Script Demonstrates

### 1. Basic Usage
- Formatting simple lists of lists
- Formatting dictionaries of lists
- Basic table formatting with headers

### 2. CSV Handling
- Reading and formatting CSV files directly
- Automatic handling of various CSV formats
- Error handling for malformed CSV files

### 3. Pandas Integration
- Formatting pandas DataFrames
- Handling different data types (strings, numbers, dates)
- Numeric data with scientific notation

### 4. Polars Integration
- Formatting Polars DataFrames
- Large dataset handling
- Efficient data processing

### 5. Advanced Features
- Custom formatting options
- Color themes
- Method chaining with the TV class
- Disabling colors and dimensions

### 6. File Format Support
- CSV files (.csv)
- Parquet files (.parquet)
- Arrow files (.arrow, .feather, .ipc)

## Key Functions Demonstrated

- `tv.format_table()` - Basic data structure formatting
- `tv.format_csv()` - CSV file formatting
- `tv.format_dataframe()` - Pandas DataFrame formatting
- `tv.format_polars_dataframe()` - Polars DataFrame formatting
- `tv.FormatOptions()` - Custom formatting options
- `tv.TV()` - Method chaining class

## Dependencies

The script will work with the following dependencies:
- `pandas` - For DataFrame support
- `polars` - For Polars DataFrame support
- `pyarrow` - For Parquet/Arrow file support

Install them with:
```bash
uv add pandas polars pyarrow
```

## Output Examples

The script demonstrates various formatting styles including:
- Colored output with themes
- Row numbering
- Dimension display
- Custom column widths
- Significant figure handling
- Scientific notation

## Error Handling

The script includes robust error handling for:
- Missing dependencies
- File not found errors
- CSV parsing errors
- Type conversion issues

This makes it a great reference for understanding how to use the package in real-world scenarios.
