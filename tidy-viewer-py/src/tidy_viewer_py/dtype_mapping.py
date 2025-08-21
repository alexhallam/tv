"""
Data type mapping utilities for tidy-viewer-py.

This module provides functions to convert data types from various dataframe libraries
(pandas, polars, arrow) into abbreviated format for display in formatted tables.
"""

from typing import Dict, List, Optional, Union
import re


# Mapping dictionaries for different library data types
PANDAS_DTYPE_MAPPING = {
    # Basic types
    'object': '<str>',
    'string': '<str>',
    'str': '<str>',
    'int64': '<i64>',
    'int32': '<i32>',
    'int16': '<i16>',
    'int8': '<i8>',
    'uint64': '<u64>',
    'uint32': '<u32>',
    'uint16': '<u16>',
    'uint8': '<u8>',
    'float64': '<f64>',
    'float32': '<f32>',
    'bool': '<bool>',
    'boolean': '<bool>',
    'datetime64[ns]': '<dt>',
    'datetime64[us]': '<dt>',
    'datetime64[ms]': '<dt>',
    'datetime64[s]': '<dt>',
    'timedelta64[ns]': '<td>',
    'timedelta64[us]': '<td>',
    'timedelta64[ms]': '<td>',
    'timedelta64[s]': '<td>',
    'category': '<cat>',
    'complex128': '<cplx>',
    'complex64': '<cplx>',
    'bytes': '<bytes>',
    'decimal': '<dec>',
    'period': '<per>',
    'interval': '<intv>',
    'sparse': '<sparse>',
    'datetimetz': '<dt>',
    'time': '<time>',
    'date': '<date>',
}

POLARS_DTYPE_MAPPING = {
    # String types
    'String': '<str>',
    'Utf8': '<str>',
    
    # Numeric types
    'Int8': '<i8>',
    'Int16': '<i16>',
    'Int32': '<i32>',
    'Int64': '<i64>',
    'Int128': '<i128>',
    'UInt8': '<u8>',
    'UInt16': '<u16>',
    'UInt32': '<u32>',
    'UInt64': '<u64>',
    'Float32': '<f32>',
    'Float64': '<f64>',
    'Decimal': '<dec>',
    
    # Boolean types
    'Boolean': '<bool>',
    'Bool': '<bool>',
    
    # Temporal types
    'Date': '<date>',
    'Datetime': '<dt>',
    'Time': '<time>',
    'Duration': '<td>',
    
    # String encoding types
    'Categorical': '<cat>',
    'Enum': '<enum>',
    
    # Nested types
    'List': '<list>',
    'Array': '<arr>',
    'Struct': '<struct>',
    'Field': '<field>',
    
    # Other types
    'Binary': '<bin>',
    'Object': '<obj>',
    'Null': '<null>',
    'Unknown': '<unk>',
}

ARROW_DTYPE_MAPPING = {
    # Basic types
    'Utf8': '<str>',
    'String': '<str>',
    'LargeString': '<str>',
    'Int64': '<i64>',
    'Int32': '<i32>',
    'Int16': '<i16>',
    'Int8': '<i8>',
    'UInt64': '<u64>',
    'UInt32': '<u32>',
    'UInt16': '<u16>',
    'UInt8': '<u8>',
    'Float64': '<f64>',
    'Float32': '<f32>',
    'Boolean': '<bool>',
    'Bool': '<bool>',
    'Timestamp': '<dt>',
    'Date32': '<date>',
    'Date64': '<date>',
    'Time32': '<time>',
    'Time64': '<time>',
    'Duration': '<td>',
    'Binary': '<bin>',
    'LargeBinary': '<bin>',
    'FixedSizeBinary': '<bin>',
    'List': '<list>',
    'LargeList': '<list>',
    'FixedSizeList': '<list>',
    'Struct': '<struct>',
    'Map': '<map>',
    'Dictionary': '<dict>',
    'Decimal128': '<dec>',
    'Decimal256': '<dec>',
    'Null': '<null>',
    'Unknown': '<unk>',
    'Union': '<union>',
    'DenseUnion': '<union>',
    'SparseUnion': '<union>',
    'Extension': '<ext>',
    'Interval': '<intv>',
    'MonthDayNanoInterval': '<intv>',
    'DayTimeInterval': '<intv>',
    'MonthInterval': '<intv>',
    'RunEndEncoded': '<run>',
    'HalfFloat': '<f16>',
    'Float16': '<f16>',
}

# Combined mapping for fallback
COMBINED_MAPPING = {**PANDAS_DTYPE_MAPPING, **POLARS_DTYPE_MAPPING, **ARROW_DTYPE_MAPPING}


def simplify_complex_type(dtype_str: str) -> str:
    """
    Simplify complex data types to basic abbreviated format.
    
    Args:
        dtype_str: The data type string to simplify
        
    Returns:
        Simplified abbreviated data type
    """
    dtype_str = str(dtype_str).strip()
    
    # Handle nullable types (e.g., "Int64?", "String?")
    if dtype_str.endswith('?'):
        base_type = dtype_str[:-1]
        # Use map_dtype to properly handle the base type
        return map_dtype(base_type)
    
    # Handle Polars Array with fixed size (e.g., "Array<Float64, 3>")
    array_fixed_match = re.match(r'Array<(.+),\s*(\d+)>', dtype_str, re.IGNORECASE)
    if array_fixed_match:
        inner_type = map_dtype(array_fixed_match.group(1))
        size = array_fixed_match.group(2)
        return f'<arr<{inner_type[1:-1]},{size}>>'
    
    # Handle List types (e.g., "List<Int64>", "Array<Float64>")
    list_match = re.match(r'List<(.+)>', dtype_str, re.IGNORECASE)
    if list_match:
        inner_type = map_dtype(list_match.group(1))
        return f'<list<{inner_type[1:-1]}>>'
    
    array_match = re.match(r'Array<(.+)>', dtype_str, re.IGNORECASE)
    if array_match:
        inner_type = map_dtype(array_match.group(1))
        return f'<arr<{inner_type[1:-1]}>>'
    
    # Handle Struct types (e.g., "Struct<field1: String, field2: Int64>")
    struct_match = re.match(r'Struct<(.+)>', dtype_str, re.IGNORECASE)
    if struct_match:
        return '<struct>'
    
    # Handle Map types (e.g., "Map<String, Int64>")
    map_match = re.match(r'Map<(.+)>', dtype_str, re.IGNORECASE)
    if map_match:
        return '<map>'
    
    # Handle Dictionary types (e.g., "Dictionary<Int8, String>")
    dict_match = re.match(r'Dictionary<(.+)>', dtype_str, re.IGNORECASE)
    if dict_match:
        return '<dict>'
    
    # Handle Union types (e.g., "Union<Int64, String>")
    union_match = re.match(r'Union<(.+)>', dtype_str, re.IGNORECASE)
    if union_match:
        return '<union>'
    
    # Handle FixedSize types (e.g., "FixedSizeList<Float64, 3>")
    fixed_match = re.match(r'FixedSize(.+)<(.+)>', dtype_str, re.IGNORECASE)
    if fixed_match:
        return f'<fixed_{fixed_match.group(1).lower()}>'
    
    # Handle Polars Datetime with timezone (e.g., "Datetime<ns, UTC>", "Datetime<us>")
    datetime_match = re.match(r'Datetime<(.+)>', dtype_str, re.IGNORECASE)
    if datetime_match:
        return '<dt>'
    
    # Handle Polars Duration with unit (e.g., "Duration<ns>", "Duration<us>")
    duration_match = re.match(r'Duration<(.+)>', dtype_str, re.IGNORECASE)
    if duration_match:
        return '<td>'
    
    # Handle Polars Decimal with precision (e.g., "Decimal(10, 2)")
    decimal_match = re.match(r'Decimal\((.+)\)', dtype_str, re.IGNORECASE)
    if decimal_match:
        return '<dec>'
    
    # Handle Arrow Decimal with precision (e.g., "Decimal128(10, 2)")
    decimal_arrow_match = re.match(r'Decimal\d*\((.+)\)', dtype_str, re.IGNORECASE)
    if decimal_arrow_match:
        return '<dec>'
    

    
    # Handle Arrow Timestamp with timezone (e.g., "Timestamp<ns, UTC>")
    timestamp_match = re.match(r'Timestamp<(.+)>', dtype_str, re.IGNORECASE)
    if timestamp_match:
        return '<dt>'
    
    return dtype_str


def map_dtype(dtype: Union[str, object], library: Optional[str] = None) -> str:
    """
    Map a data type to abbreviated format.
    
    Args:
        dtype: The data type to map (string or object with __str__)
        library: Optional library hint ('pandas', 'polars', 'arrow', or None for auto-detect)
        
    Returns:
        Abbreviated data type string
        
    Examples:
        >>> map_dtype('int64', 'pandas')
        '<i64>'
        >>> map_dtype('String', 'polars')
        '<str>'
        >>> map_dtype('List<Int64>')
        '<list<i64>>'
    """
    dtype_str = str(dtype).strip()
    
    # First try to simplify complex types
    simplified = simplify_complex_type(dtype_str)
    
    # If simplification didn't change the type, try direct mapping
    if simplified == dtype_str:
        # Try library-specific mapping first
        if library == 'pandas':
            return PANDAS_DTYPE_MAPPING.get(dtype_str, f'<{dtype_str.lower()}>')
        elif library == 'polars':
            return POLARS_DTYPE_MAPPING.get(dtype_str, f'<{dtype_str.lower()}>')
        elif library == 'arrow':
            return ARROW_DTYPE_MAPPING.get(dtype_str, f'<{dtype_str.lower()}>')
        else:
            # Try combined mapping
            return COMBINED_MAPPING.get(dtype_str, f'<{dtype_str.lower()}>')
    
    return simplified


def map_dtypes(dtypes: List[Union[str, object]], library: Optional[str] = None) -> List[str]:
    """
    Map a list of data types to abbreviated format.
    
    Args:
        dtypes: List of data types to map
        library: Optional library hint ('pandas', 'polars', 'arrow', or None for auto-detect)
        
    Returns:
        List of abbreviated data type strings
        
    Examples:
        >>> map_dtypes(['int64', 'object', 'float64'], 'pandas')
        ['<i64>', '<str>', '<f64>']
    """
    return [map_dtype(dtype, library) for dtype in dtypes]


def detect_library_from_dtypes(dtypes: List[Union[str, object]]) -> Optional[str]:
    """
    Attempt to detect the dataframe library from data type patterns.
    
    Args:
        dtypes: List of data types
        
    Returns:
        Detected library ('pandas', 'polars', 'arrow') or None if uncertain
    """
    if not dtypes:
        return None
    
    dtype_strs = [str(dtype).strip() for dtype in dtypes]
    
    # Check for arrow patterns first (most specific to avoid conflicts)
    arrow_patterns = ['LargeString', 'LargeList', 'FixedSizeList', 'LargeBinary', 'FixedSizeBinary', 'Date32', 'Date64', 'Time32', 'Time64', 'Dictionary', 'Union', 'DenseUnion', 'SparseUnion', 'Utf8']
    if any(pattern in dtype_str for dtype_str in dtype_strs for pattern in arrow_patterns):
        return 'arrow'
    
    # Check for polars patterns (more specific than pandas)
    polars_patterns = ['String', 'Int64', 'Float64', 'Boolean', 'Datetime', 'Categorical', 'Duration', 'Enum', 'Array<', 'List<', 'Struct<', 'Field<']
    if any(pattern in dtype_str for dtype_str in dtype_strs for pattern in polars_patterns):
        return 'polars'
    
    # Check for pandas patterns (most generic, check last)
    pandas_patterns = ['object', 'int64', 'float64', 'bool', 'datetime64', 'category']
    if any(pattern in dtype_str for dtype_str in dtype_strs for pattern in pandas_patterns):
        return 'pandas'
    
    return None


def auto_map_dtypes(dtypes: List[Union[str, object]]) -> List[str]:
    """
    Automatically detect library and map data types to abbreviated format.
    
    Args:
        dtypes: List of data types to map
        
    Returns:
        List of abbreviated data type strings
        
    Examples:
        >>> auto_map_dtypes(['int64', 'object', 'float64'])
        ['<i64>', '<str>', '<f64>']
    """
    library = detect_library_from_dtypes(dtypes)
    return map_dtypes(dtypes, library)
