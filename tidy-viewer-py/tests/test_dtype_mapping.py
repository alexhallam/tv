"""
Tests for data type mapping functionality.
"""

import pytest
from tidy_viewer_py import (
    map_dtype, map_dtypes, auto_map_dtypes, detect_library_from_dtypes,
    PANDAS_DTYPE_MAPPING, POLARS_DTYPE_MAPPING, ARROW_DTYPE_MAPPING
)


class TestDtypeMapping:
    """Test basic data type mapping functionality."""
    
    def test_pandas_basic_types(self):
        """Test mapping of basic pandas data types."""
        assert map_dtype('object', 'pandas') == '<str>'
        assert map_dtype('int64', 'pandas') == '<i64>'
        assert map_dtype('float64', 'pandas') == '<f64>'
        assert map_dtype('bool', 'pandas') == '<bool>'
        assert map_dtype('datetime64[ns]', 'pandas') == '<dt>'
        assert map_dtype('category', 'pandas') == '<cat>'
    
    def test_polars_basic_types(self):
        """Test mapping of basic polars data types."""
        assert map_dtype('String', 'polars') == '<str>'
        assert map_dtype('Int64', 'polars') == '<i64>'
        assert map_dtype('Float64', 'polars') == '<f64>'
        assert map_dtype('Boolean', 'polars') == '<bool>'
        assert map_dtype('Datetime', 'polars') == '<dt>'
        assert map_dtype('Categorical', 'polars') == '<cat>'
    
    def test_arrow_basic_types(self):
        """Test mapping of basic arrow data types."""
        assert map_dtype('Utf8', 'arrow') == '<str>'
        assert map_dtype('Int64', 'arrow') == '<i64>'
        assert map_dtype('Float64', 'arrow') == '<f64>'
        assert map_dtype('Boolean', 'arrow') == '<bool>'
        assert map_dtype('Timestamp', 'arrow') == '<dt>'
        assert map_dtype('List', 'arrow') == '<list>'
    
    def test_complex_types(self):
        """Test mapping of complex data types."""
        # List types
        assert map_dtype('List<Int64>') == '<list<i64>>'
        assert map_dtype('Array<Float64>') == '<arr<f64>>'
        
        # Struct types
        assert map_dtype('Struct<field1: String, field2: Int64>') == '<struct>'
        
        # Map types
        assert map_dtype('Map<String, Int64>') == '<map>'
        
        # Dictionary types
        assert map_dtype('Dictionary<Int8, String>') == '<dict>'
        
        # Union types
        assert map_dtype('Union<Int64, String>') == '<union>'
        
        # Nullable types
        assert map_dtype('Int64?') == '<i64>'
        assert map_dtype('String?') == '<str>'
        
        # Timestamp with timezone
        assert map_dtype('Timestamp<ns, UTC>') == '<dt>'
        
        # Duration with unit
        assert map_dtype('Duration<ns>') == '<td>'
        
        # Decimal with precision
        assert map_dtype('Decimal128(10, 2)') == '<dec>'
    
    def test_unknown_types(self):
        """Test handling of unknown data types."""
        assert map_dtype('UnknownType') == '<unknowntype>'
        assert map_dtype('CustomType', 'pandas') == '<customtype>'
    
    def test_list_mapping(self):
        """Test mapping lists of data types."""
        pandas_dtypes = ['object', 'int64', 'float64', 'bool']
        expected = ['<str>', '<i64>', '<f64>', '<bool>']
        assert map_dtypes(pandas_dtypes, 'pandas') == expected
        
        polars_dtypes = ['String', 'Int64', 'Float64', 'Boolean']
        expected = ['<str>', '<i64>', '<f64>', '<bool>']
        assert map_dtypes(polars_dtypes, 'polars') == expected
    
    def test_auto_detection(self):
        """Test automatic library detection."""
        # Pandas patterns
        pandas_dtypes = ['object', 'int64', 'float64', 'bool']
        assert detect_library_from_dtypes(pandas_dtypes) == 'pandas'
        
        # Polars patterns
        polars_dtypes = ['String', 'Int64', 'Float64', 'Boolean']
        assert detect_library_from_dtypes(polars_dtypes) == 'polars'
        
        # Arrow patterns
        arrow_dtypes = ['Utf8', 'LargeString', 'Date32', 'Time32']
        assert detect_library_from_dtypes(arrow_dtypes) == 'arrow'
        
        # Unknown patterns
        unknown_dtypes = ['CustomType1', 'CustomType2']
        assert detect_library_from_dtypes(unknown_dtypes) is None
    
    def test_auto_mapping(self):
        """Test automatic mapping with library detection."""
        pandas_dtypes = ['object', 'int64', 'float64', 'bool']
        expected = ['<str>', '<i64>', '<f64>', '<bool>']
        assert auto_map_dtypes(pandas_dtypes) == expected
        
        polars_dtypes = ['String', 'Int64', 'Float64', 'Boolean']
        expected = ['<str>', '<i64>', '<f64>', '<bool>']
        assert auto_map_dtypes(polars_dtypes) == expected


class TestDataFrameIntegration:
    """Test integration with actual dataframes."""
    
    def test_pandas_dataframe_with_dtypes(self):
        """Test pandas DataFrame formatting with data types."""
        try:
            import pandas as pd
            
            # Create a test DataFrame
            df = pd.DataFrame({
                'name': ['Alice', 'Bob', 'Charlie'],
                'age': [25, 30, 35],
                'salary': [50000.0, 60000.0, 70000.0],
                'active': [True, False, True]
            })
            
            from tidy_viewer_py import format_dataframe
            
            # Test with data types
            result = format_dataframe(df, show_dtypes=True)
            assert '<str>' in result
            assert '<i64>' in result
            assert '<f64>' in result
            assert '<bool>' in result
            
            # Test without data types
            result_no_dtypes = format_dataframe(df, show_dtypes=False)
            assert '<str>' not in result_no_dtypes
            assert '<i64>' not in result_no_dtypes
            
        except ImportError:
            pytest.skip("pandas not available")
    
    def test_polars_dataframe_with_dtypes(self):
        """Test polars DataFrame formatting with data types."""
        try:
            import polars as pl
            
            # Create a test DataFrame
            df = pl.DataFrame({
                'name': ['Alice', 'Bob', 'Charlie'],
                'age': [25, 30, 35],
                'salary': [50000.0, 60000.0, 70000.0],
                'active': [True, False, True]
            })
            
            from tidy_viewer_py import format_polars_dataframe
            
            # Test with data types
            result = format_polars_dataframe(df, show_dtypes=True)
            assert '<str>' in result
            assert '<i64>' in result
            assert '<f64>' in result
            assert '<bool>' in result
            
            # Test without data types
            result_no_dtypes = format_polars_dataframe(df, show_dtypes=False)
            assert '<str>' not in result_no_dtypes
            assert '<i64>' not in result_no_dtypes
            
        except ImportError:
            pytest.skip("polars not available")


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_dtype_list(self):
        """Test handling of empty dtype lists."""
        assert map_dtypes([]) == []
        assert detect_library_from_dtypes([]) is None
        assert auto_map_dtypes([]) == []
    
    def test_none_dtype(self):
        """Test handling of None values."""
        assert map_dtype(None) == '<none>'
        assert map_dtypes([None, 'int64']) == ['<none>', '<i64>']
    
    def test_mixed_library_dtypes(self):
        """Test handling of mixed library data types."""
        mixed_dtypes = ['object', 'String', 'Int64', 'Utf8']
        # Should default to combined mapping
        result = auto_map_dtypes(mixed_dtypes)
        assert all(dtype.startswith('<') and dtype.endswith('>') for dtype in result)
    
    def test_complex_nested_types(self):
        """Test handling of deeply nested complex types."""
        # Nested list
        assert map_dtype('List<List<Int64>>') == '<list<list<i64>>>'
        
        # Complex struct
        assert map_dtype('Struct<field1: List<Int64>, field2: Map<String, Float64>>') == '<struct>'
        
        # Mixed complex types
        assert map_dtype('Union<List<Int64>, Struct<field: String>>') == '<union>'


class TestMappingTables:
    """Test the mapping tables themselves."""
    
    def test_pandas_mapping_table(self):
        """Test that pandas mapping table contains expected mappings."""
        assert 'object' in PANDAS_DTYPE_MAPPING
        assert 'int64' in PANDAS_DTYPE_MAPPING
        assert 'float64' in PANDAS_DTYPE_MAPPING
        assert 'bool' in PANDAS_DTYPE_MAPPING
        assert 'datetime64[ns]' in PANDAS_DTYPE_MAPPING
        assert PANDAS_DTYPE_MAPPING['object'] == '<str>'
        assert PANDAS_DTYPE_MAPPING['int64'] == '<i64>'
    
    def test_polars_mapping_table(self):
        """Test that polars mapping table contains expected mappings."""
        assert 'String' in POLARS_DTYPE_MAPPING
        assert 'Int64' in POLARS_DTYPE_MAPPING
        assert 'Float64' in POLARS_DTYPE_MAPPING
        assert 'Boolean' in POLARS_DTYPE_MAPPING
        assert 'Datetime' in POLARS_DTYPE_MAPPING
        assert POLARS_DTYPE_MAPPING['String'] == '<str>'
        assert POLARS_DTYPE_MAPPING['Int64'] == '<i64>'
    
    def test_arrow_mapping_table(self):
        """Test that arrow mapping table contains expected mappings."""
        assert 'Utf8' in ARROW_DTYPE_MAPPING
        assert 'Int64' in ARROW_DTYPE_MAPPING
        assert 'Float64' in ARROW_DTYPE_MAPPING
        assert 'Boolean' in ARROW_DTYPE_MAPPING
        assert 'Timestamp' in ARROW_DTYPE_MAPPING
        assert ARROW_DTYPE_MAPPING['Utf8'] == '<str>'
        assert ARROW_DTYPE_MAPPING['Int64'] == '<i64>'
