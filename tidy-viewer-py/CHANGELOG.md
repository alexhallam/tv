# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

0.3.1 (2024-08-20)

### Added
- **Comprehensive DataFrame Examples**: Added 12 detailed examples to `demo_polars_dtypes.py` covering all major Polars data types
  - Basic types (String, Int32, Float64, Boolean, Date)
  - Date and time types (Date, Datetime<ns>, Time, Datetime<ns, UTC>)
  - List types (List<Float64>, List<String>, List<Int64>)
  - Array types with fixed sizes (Array<Float64, 3>, Array<Int64, 3>)
  - Struct types with complex field definitions
  - Nullable types (Int64?, Float64?, Boolean?)
  - Decimal types with precision (Decimal(10, 2), Decimal(38, 9))
  - Duration types (Duration<ns>)
  - Categorical and Enum types
  - Nested complex types (List<List<Int64>>, List<Struct<...>>)
  - Complex structs with lists

### Enhanced
- **Visual Verification**: All examples now show both full Polars types and abbreviated forms
- **Abbreviated Data Types Display**: Formatted tables now properly display abbreviated data types in the data type row
- **Demo Output**: Enhanced demo script to clearly show the difference between full and abbreviated type names
- **Documentation**: Updated README.md with comprehensive Polars data type mapping table

### Fixed
- **Data Type Row Display**: Ensured abbreviated data types are correctly passed to `format_table` for display
- **Type Mapping Accuracy**: Improved mapping for complex nested types and nullable types

### Technical
- **Test Coverage**: Added comprehensive tests for all new functionality in `test_polars_dtypes.py`
- **Library Detection**: Enhanced auto-detection logic for Polars vs Arrow vs Pandas data types
- **Complex Type Handling**: Improved regex patterns for parsing complex Polars type strings

0.3.0 (2024-08-20)

### Added
- **Data Type Display**: New optional `data_type` argument to `format_table` function
  - Displays data types as a separate row below headers
  - Slightly off-color relative to headers for visual distinction
  - Only shows when data types are provided
  - No row numbering for data type row

- **Data Type Mapping System**: New `dtype_mapping.py` module
  - Maps data types from Pandas, Polars, and Arrow to consistent abbreviated format
  - Abbreviated format uses angle brackets: `['<str>', '<u8>', '<i16>', '<f64>']`
  - Automatic library detection from data type strings
  - Complex type simplification (e.g., `List<Int64>` → `<list<i64>>`)

- **Enhanced Polars Support**: Improved data type mapping based on official Polars documentation
  - Comprehensive mapping for all Polars data types
  - Support for parameterized types (Datetime, Duration, Decimal, Array)
  - Handling of nullable types and complex nested structures
  - Proper abbreviation of complex types with parameters

- **Python Interface Enhancements**:
  - `format_dataframe()` and `format_polars_dataframe()` now support `show_dtypes=True`
  - Automatic data type extraction and mapping from DataFrame objects
  - New utility functions: `map_dtype()`, `map_dtypes()`, `auto_map_dtypes()`

### Changed
- **Row Numbering**: Data rows now always start from 1, regardless of headers or data types presence
- **Coloring Logic**: First data row is now colored as standard data, not as header
- **Function Names**: `format_data` renamed to `format_table` for consistency

### Technical
- **Validation**: Added length validation for `data_type` vector against headers
- **Error Handling**: Graceful handling of missing optional dependencies
- **Documentation**: Comprehensive README updates with mapping tables and examples
- **Testing**: Added extensive test coverage for new functionality

0.2.94 (2024-08-19)

### Added
- Initial release with basic table formatting functionality
- Support for CSV, Parquet, Pandas, and Arrow DataFrames
- Cross-platform terminal formatting with column styling
- Basic data type detection and display

### Technical
- Rust core with PyO3 bindings
- Terminal size detection and responsive formatting
- Color support using owo_colors
- Comprehensive test suite
