"""
Test Polars data type mapping functionality.

This module tests the improved Polars data type mapping based on the official
Polars documentation: https://docs.pola.rs/api/python/stable/reference/datatypes.html
"""

import pytest
from tidy_viewer_py import map_dtype, map_dtypes, auto_map_dtypes, detect_library_from_dtypes


class TestPolarsDataTypes:
    """Test Polars data type mapping functionality."""
    
    def test_basic_polars_types(self):
        """Test basic Polars data types."""
        # String types
        assert map_dtype('String', 'polars') == '<str>'
        assert map_dtype('Utf8', 'polars') == '<str>'
        
        # Numeric types
        assert map_dtype('Int8', 'polars') == '<i8>'
        assert map_dtype('Int16', 'polars') == '<i16>'
        assert map_dtype('Int32', 'polars') == '<i32>'
        assert map_dtype('Int64', 'polars') == '<i64>'
        assert map_dtype('Int128', 'polars') == '<i128>'
        assert map_dtype('UInt8', 'polars') == '<u8>'
        assert map_dtype('UInt16', 'polars') == '<u16>'
        assert map_dtype('UInt32', 'polars') == '<u32>'
        assert map_dtype('UInt64', 'polars') == '<u64>'
        assert map_dtype('Float32', 'polars') == '<f32>'
        assert map_dtype('Float64', 'polars') == '<f64>'
        
        # Boolean types
        assert map_dtype('Boolean', 'polars') == '<bool>'
        assert map_dtype('Bool', 'polars') == '<bool>'
        
        # Temporal types
        assert map_dtype('Date', 'polars') == '<date>'
        assert map_dtype('Datetime', 'polars') == '<dt>'
        assert map_dtype('Time', 'polars') == '<time>'
        assert map_dtype('Duration', 'polars') == '<td>'
        
        # String encoding types
        assert map_dtype('Categorical', 'polars') == '<cat>'
        assert map_dtype('Enum', 'polars') == '<enum>'
        
        # Other types
        assert map_dtype('Binary', 'polars') == '<bin>'
        assert map_dtype('Object', 'polars') == '<obj>'
        assert map_dtype('Null', 'polars') == '<null>'
        assert map_dtype('Unknown', 'polars') == '<unk>'
    
    def test_complex_polars_types(self):
        """Test complex Polars data types with parameters."""
        # Datetime with timezone/unit
        assert map_dtype('Datetime<ns>', 'polars') == '<dt>'
        assert map_dtype('Datetime<us>', 'polars') == '<dt>'
        assert map_dtype('Datetime<ms>', 'polars') == '<dt>'
        assert map_dtype('Datetime<ns, UTC>', 'polars') == '<dt>'
        assert map_dtype('Datetime<us, America/New_York>', 'polars') == '<dt>'
        
        # Duration with unit
        assert map_dtype('Duration<ns>', 'polars') == '<td>'
        assert map_dtype('Duration<us>', 'polars') == '<td>'
        assert map_dtype('Duration<ms>', 'polars') == '<td>'
        
        # Decimal with precision
        assert map_dtype('Decimal(10, 2)', 'polars') == '<dec>'
        assert map_dtype('Decimal(38, 0)', 'polars') == '<dec>'
        
        # Array with fixed size
        assert map_dtype('Array<Float64, 3>', 'polars') == '<arr<f64,3>>'
        assert map_dtype('Array<Int64, 10>', 'polars') == '<arr<i64,10>>'
        assert map_dtype('Array<String, 5>', 'polars') == '<arr<str,5>>'
        
        # List with inner type
        assert map_dtype('List<Int64>', 'polars') == '<list<i64>>'
        assert map_dtype('List<String>', 'polars') == '<list<str>>'
        assert map_dtype('List<Float64>', 'polars') == '<list<f64>>'
        
        # Struct with fields
        assert map_dtype('Struct<field1: String, field2: Int64>', 'polars') == '<struct>'
        assert map_dtype('Struct<name: String, age: Int32, active: Boolean>', 'polars') == '<struct>'
        
        # Nested complex types
        assert map_dtype('List<Struct<name: String, age: Int32>>', 'polars') == '<list<struct>>'
        assert map_dtype('Array<List<Int64>, 3>', 'polars') == '<arr<list<i64>,3>>'
    
    def test_nullable_types(self):
        """Test nullable Polars data types."""
        # Nullable basic types
        assert map_dtype('Int64?', 'polars') == '<i64>'
        assert map_dtype('String?', 'polars') == '<str>'
        assert map_dtype('Boolean?', 'polars') == '<bool>'
        assert map_dtype('Float64?', 'polars') == '<f64>'
        
        # Nullable complex types
        assert map_dtype('List<Int64>?', 'polars') == '<list<i64>>'
        assert map_dtype('Struct<name: String>?', 'polars') == '<struct>'
        assert map_dtype('Datetime<ns>?', 'polars') == '<dt>'
    
    def test_library_detection(self):
        """Test automatic library detection for Polars types."""
        # Basic Polars types
        dtypes = ['String', 'Int64', 'Float64', 'Boolean']
        assert detect_library_from_dtypes(dtypes) == 'polars'
        
        # Complex Polars types
        dtypes = ['List<Int64>', 'Datetime<ns>', 'Array<Float64, 3>']
        assert detect_library_from_dtypes(dtypes) == 'polars'
        
        # Mixed with other libraries (should detect Polars due to specific patterns)
        dtypes = ['String', 'int64', 'Datetime<ns>', 'object']
        assert detect_library_from_dtypes(dtypes) == 'polars'
    
    def test_auto_mapping(self):
        """Test automatic mapping of Polars data types."""
        # Basic types
        dtypes = ['String', 'Int64', 'Float64', 'Boolean', 'Datetime<ns>']
        expected = ['<str>', '<i64>', '<f64>', '<bool>', '<dt>']
        assert auto_map_dtypes(dtypes) == expected
        
        # Complex types
        dtypes = ['List<Int64>', 'Array<Float64, 3>', 'Struct<name: String>']
        expected = ['<list<i64>>', '<arr<f64,3>>', '<struct>']
        assert auto_map_dtypes(dtypes) == expected
        
        # Mixed types
        dtypes = ['String', 'Int64?', 'List<Float64>', 'Datetime<ns, UTC>']
        expected = ['<str>', '<i64>', '<list<f64>>', '<dt>']
        assert auto_map_dtypes(dtypes) == expected
    
    def test_edge_cases(self):
        """Test edge cases and unusual Polars data types."""
        # Very large integers
        assert map_dtype('Int128', 'polars') == '<i128>'
        
        # Decimal with different precision
        assert map_dtype('Decimal(38, 0)', 'polars') == '<dec>'
        assert map_dtype('Decimal(10, 5)', 'polars') == '<dec>'
        
        # Complex nested structures
        assert map_dtype('List<Array<Struct<name: String, age: Int32>, 5>>', 'polars') == '<list<arr<struct,5>>>'
        
        # Unknown types should fall back gracefully
        assert map_dtype('CustomType', 'polars') == '<customtype>'
        assert map_dtype('VerySpecificType<param>', 'polars') == '<veryspecifictype<param>>'


if __name__ == "__main__":
    pytest.main([__file__])
