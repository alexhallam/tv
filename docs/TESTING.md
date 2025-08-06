# Testing Guide for Tidy-Viewer

This document provides instructions for generating test files and testing the various features of `tidy-viewer`.

## 🗂️ Test File Generation

### Arrow IPC (Feather) Files

Generate Arrow IPC test files using the provided Python script:

```bash
# Install required Python packages
pip install pandas pyarrow numpy

# Generate Arrow IPC test files
python generate_arrow_test_files.py
```

This will create:
- `data/test_small.feather`, `data/test_small.arrow`, `data/test_small.ipc`
- `data/test_medium.feather`, `data/test_medium.arrow`, `data/test_medium.ipc`
- `data/test_large.feather`, `data/test_large.arrow`, `data/test_large.ipc`

### Performance Test Files

Generate performance test files for benchmarking:

```bash
# Generate performance test files
python generate_performance_test_files.py
```

This creates various CSV files with different sizes and characteristics for performance testing.

## 🧪 Feature Testing Commands

### Arrow IPC (Feather) File Support

Test the new Arrow IPC file support with different extensions:

```bash
# Test uncompressed Arrow files
tv data/uncompressed_small.feather
tv data/uncompressed_small.arrow
tv data/uncompressed_small.ipc

# Test compressed Arrow files (LZ4 support)
tv data/compressed_test.feather
tv data/compressed_test.arrow
tv data/compressed_test.ipc

# Test larger Arrow files
tv data/uncompressed_medium.feather -n 10
tv data/uncompressed_large.feather -n 5
```

### Streaming Mode with Arrow Files

Test streaming mode with large Arrow files:

```bash
# Test streaming with large Arrow files
tv data/uncompressed_large.feather
tv data/uncompressed_large.arrow

# Force streaming mode
tv data/uncompressed_medium.feather --no-streaming
```

### JSON File Graceful Error Handling

Test the new JSON error handling:

```bash
# Create a test JSON file
echo '{"name": "test", "value": 123}' > test.json

# Test JSON error handling
tv test.json

# Clean up
rm test.json
```

### Arrow File Detection

Test that Arrow files are properly detected:

```bash
# Test different Arrow extensions
tv data/test_small.feather
tv data/test_small.arrow
tv data/test_small.ipc

# Compare with other file types
tv data/diamonds.csv
tv data/taxi_sample.parquet
```

### Advanced Arrow Testing

Test Arrow files with various options:

```bash
# Test with color options
tv data/uncompressed_small.feather -c 1
tv data/uncompressed_small.feather -c 2

# Test with different row limits
tv data/uncompressed_medium.feather -n 5
tv data/uncompressed_medium.feather -n 50

# Test with column width options
tv data/uncompressed_small.feather -l 5 -u 15

# Test with scientific notation options
tv data/uncompressed_small.feather --preserve-scientific
```

### Performance Testing

Test performance with large files:

```bash
# Test large Arrow files
tv data/uncompressed_large.feather

# Test streaming threshold
tv data/uncompressed_large.arrow --streaming-threshold 1

# Test without streaming
tv data/uncompressed_large.arrow --no-streaming
```

### Color and Display Testing

Test the visual features:

```bash
# Test different color palettes
tv data/uncompressed_small.feather -c 1  # nord
tv data/uncompressed_small.feather -c 2  # one_dark
tv data/uncompressed_small.feather -c 3  # gruvbox

# Test with always color
tv data/uncompressed_small.feather -a

# Test with extended width
tv data/uncompressed_small.feather -e
```

### Debug and Config Testing

Test debugging and configuration:

```bash
# Show config details
tv data/uncompressed_small.feather -C

# Debug mode
tv data/uncompressed_small.feather -d

# Test with title and footer
tv data/uncompressed_small.feather -t "Arrow Test" -F "Footer Info"
```

### CSV File Testing

Test various CSV file formats:

```bash
# Test basic CSV files
tv data/diamonds.csv
tv data/titanic.csv
tv data/iris.csv

# Test CSV with different delimiters
tv data/tab_sep.csv -s tab

# Test CSV with scientific notation
tv data/test_scientific.csv

# Test CSV with unicode characters
tv data/unicode_pr55.csv

# Test large CSV files
tv data/large_test.csv
```

### Parquet File Testing

Test Parquet file support:

```bash
# Test basic Parquet files
tv data/basic_test.parquet
tv data/taxi_sample.parquet

# Test Parquet with different data types
tv data/scientific_notation.parquet
tv data/unicode_test.parquet
tv data/nulls_test.parquet
tv data/long_strings.parquet
```

## 🚀 Quick Feature Summary Test

Here's a comprehensive test command that covers all major features:

```bash
# Test all major features in one go
echo "Testing Arrow IPC support, streaming, and error handling..."
tv data/uncompressed_small.feather -n 3 -c 1 -t "Arrow Test"
```

## 🔧 Development Testing

### Running Tests

```bash
# Run all tests
cargo test

# Run specific test
cargo test tests::unicode_pr55_csv -- --nocapture
cargo test tests::test_arrow_file_reading -- --nocapture

# Run tests with output
cargo test -- --nocapture
```

### Building and Installing

```bash
# Build the project
cargo build

# Build in release mode
cargo build --release

# Install the latest version
cargo install --path .

# Check installed version
tv --version
```

## 📋 Test File Inventory

### Arrow IPC Files
- `data/uncompressed_small.feather/.arrow/.ipc` - Small uncompressed files
- `data/uncompressed_medium.feather/.arrow/.ipc` - Medium uncompressed files
- `data/uncompressed_large.feather/.arrow/.ipc` - Large uncompressed files
- `data/compressed_test.feather/.arrow/.ipc` - LZ4 compressed files
- `data/test_small.feather/.arrow/.ipc` - Generated test files
- `data/test_medium.feather/.arrow/.ipc` - Generated test files
- `data/test_large.feather/.arrow/.ipc` - Generated test files

### CSV Files
- `data/diamonds.csv` - Large dataset for performance testing
- `data/titanic.csv` - Medium dataset with mixed data types
- `data/iris.csv` - Small dataset with numeric data
- `data/unicode_pr55.csv` - Unicode character testing
- `data/test_scientific.csv` - Scientific notation testing
- `data/large_test.csv` - Large file for streaming testing

### Parquet Files
- `data/taxi_sample.parquet` - Large Parquet file
- `data/basic_test.parquet` - Basic Parquet testing
- `data/scientific_notation.parquet` - Scientific notation in Parquet
- `data/unicode_test.parquet` - Unicode in Parquet
- `data/nulls_test.parquet` - Null value handling
- `data/long_strings.parquet` - Long string handling

## 🐛 Troubleshooting

### Common Issues

1. **Arrow files not found**: Run `python generate_arrow_test_files.py` to create test files
2. **Python dependencies missing**: Run `pip install pandas pyarrow numpy`
3. **Compression errors**: Ensure Arrow files are properly generated with correct compression settings
4. **Unicode display issues**: Test with `data/unicode_pr55.csv` to verify Unicode handling

### Debug Commands

```bash
# Debug Arrow file reading
tv data/uncompressed_small.feather -d

# Show configuration
tv data/uncompressed_small.feather -C

# Force verbose output
cargo run -- data/uncompressed_small.feather -d
```

## 📝 Notes

- Arrow IPC files support `.feather`, `.arrow`, and `.ipc` extensions
- LZ4 compression is supported for Arrow files
- JSON files show graceful error messages with helpful suggestions
- Streaming mode automatically activates for large files (>5MB by default)
- Unicode characters are properly handled and truncated with ellipsis when needed
