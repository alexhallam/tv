#!/usr/bin/env python3
"""
Demo script showcasing improved Polars data type mapping.

This script demonstrates the enhanced Polars data type mapping based on the
official Polars documentation: https://docs.pola.rs/api/python/stable/reference/datatypes.html
"""

import tidy_viewer_py as tv
from tidy_viewer_py import map_dtype, map_dtypes, auto_map_dtypes, detect_library_from_dtypes


def demo_basic_polars_types():
    """Demonstrate basic Polars data type mapping."""
    print("=" * 60)
    print("BASIC POLARS DATA TYPES")
    print("=" * 60)
    
    # Basic types
    basic_types = [
        'String', 'Utf8',           # String types
        'Int8', 'Int16', 'Int32', 'Int64', 'Int128',  # Signed integers
        'UInt8', 'UInt16', 'UInt32', 'UInt64',        # Unsigned integers
        'Float32', 'Float64',       # Floating point
        'Boolean', 'Bool',          # Boolean
        'Date', 'Datetime', 'Time', 'Duration',       # Temporal
        'Categorical', 'Enum',      # String encoding
        'Binary', 'Object', 'Null', 'Unknown'         # Other
    ]
    
    print("Basic Polars types and their mappings:")
    for dtype in basic_types:
        mapped = map_dtype(dtype, 'polars')
        print(f"  {dtype:12} → {mapped}")
    
    print()


def demo_complex_polars_types():
    """Demonstrate complex Polars data type mapping."""
    print("=" * 60)
    print("COMPLEX POLARS DATA TYPES")
    print("=" * 60)
    
    # Complex types with parameters
    complex_types = [
        # Datetime with timezone/unit
        'Datetime<ns>', 'Datetime<us>', 'Datetime<ns, UTC>',
        # Duration with unit
        'Duration<ns>', 'Duration<us>', 'Duration<ms>',
        # Decimal with precision
        'Decimal(10, 2)', 'Decimal(38, 0)',
        # Array with fixed size
        'Array<Float64, 3>', 'Array<Int64, 10>', 'Array<String, 5>',
        # List with inner type
        'List<Int64>', 'List<String>', 'List<Float64>',
        # Struct with fields
        'Struct<name: String, age: Int32>',
        'Struct<field1: String, field2: Int64, active: Boolean>',
        # Nested complex types
        'List<Struct<name: String, age: Int32>>',
        'Array<List<Int64>, 3>'
    ]
    
    print("Complex Polars types and their mappings:")
    for dtype in complex_types:
        mapped = map_dtype(dtype, 'polars')
        print(f"  {dtype:35} → {mapped}")
    
    print()


def demo_nullable_types():
    """Demonstrate nullable Polars data type mapping."""
    print("=" * 60)
    print("NULLABLE POLARS DATA TYPES")
    print("=" * 60)
    
    # Nullable types
    nullable_types = [
        'Int64?', 'String?', 'Boolean?', 'Float64?',
        'List<Int64>?', 'Struct<name: String>?', 'Datetime<ns>?'
    ]
    
    print("Nullable Polars types and their mappings:")
    for dtype in nullable_types:
        mapped = map_dtype(dtype, 'polars')
        print(f"  {dtype:25} → {mapped}")
    
    print()


def demo_library_detection():
    """Demonstrate automatic library detection."""
    print("=" * 60)
    print("AUTOMATIC LIBRARY DETECTION")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        (['String', 'Int64', 'Float64', 'Boolean'], 'polars'),
        (['List<Int64>', 'Datetime<ns>', 'Array<Float64, 3>'], 'polars'),
        (['object', 'int64', 'float64', 'bool'], 'pandas'),
        (['Utf8', 'LargeString', 'Timestamp', 'Date32'], 'arrow'),
        (['String', 'int64', 'Datetime<ns>', 'object'], 'polars'),  # Mixed, should detect Polars
    ]
    
    print("Library detection examples:")
    for dtypes, expected in test_cases:
        detected = detect_library_from_dtypes(dtypes)
        status = "✓" if detected == expected else "✗"
        print(f"  {status} {dtypes} → {detected} (expected: {expected})")
    
    print()


def demo_auto_mapping():
    """Demonstrate automatic data type mapping."""
    print("=" * 60)
    print("AUTOMATIC DATA TYPE MAPPING")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        (['String', 'Int64', 'Float64', 'Boolean', 'Datetime<ns>'],
         ['<str>', '<i64>', '<f64>', '<bool>', '<dt>']),
        (['List<Int64>', 'Array<Float64, 3>', 'Struct<name: String>'],
         ['<list<i64>>', '<arr<f64,3>>', '<struct>']),
        (['String', 'Int64?', 'List<Float64>', 'Datetime<ns, UTC>'],
         ['<str>', '<i64>', '<list<f64>>', '<dt>']),
    ]
    
    print("Automatic mapping examples:")
    for dtypes, expected in test_cases:
        mapped = auto_map_dtypes(dtypes)
        status = "✓" if mapped == expected else "✗"
        print(f"  {status} {dtypes}")
        print(f"      → {mapped}")
        if mapped != expected:
            print(f"      Expected: {expected}")
        print()
    
    print()


def demo_dataframe_formatting():
    """Demonstrate DataFrame formatting with data types."""
    print("=" * 60)
    print("DATAFRAME FORMATTING WITH DATA TYPES")
    print("=" * 60)
    
    # Sample data
    data = [
        ['Alice', 25, 75000.50, True, '2023-01-15'],
        ['Bob', 30, 85000.75, False, '2023-02-20'],
        ['Charlie', 35, 95000.25, True, '2023-03-10'],
    ]
    
    headers = ['Name', 'Age', 'Salary', 'Active', 'HireDate']
    
    # Polars-style data types
    polars_dtypes = ['String', 'Int32', 'Float64', 'Boolean', 'Date']
    
    print("Sample data with Polars data types:")
    print(f"Headers: {headers}")
    print(f"Data types: {polars_dtypes}")
    print()
    
    # Format with data types
    formatted = tv.format_table(data, headers, polars_dtypes)
    print(formatted)
    
    print()


def main():
    """Run all demos."""
    print("POLARS DATA TYPE MAPPING DEMO")
    print("Based on official Polars documentation")
    print("https://docs.pola.rs/api/python/stable/reference/datatypes.html")
    print()
    
    demo_basic_polars_types()
    demo_complex_polars_types()
    demo_nullable_types()
    demo_library_detection()
    demo_auto_mapping()
    demo_dataframe_formatting()
    
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("The improved Polars data type mapping now supports:")
    print("• All basic Polars data types (String, Int64, Float64, etc.)")
    print("• Complex types with parameters (Datetime<ns>, Array<Type, size>)")
    print("• Nested types (List<Struct<...>>)")
    print("• Nullable types (Int64?)")
    print("• Automatic library detection")
    print("• Comprehensive mapping tables")


if __name__ == "__main__":
    main()
