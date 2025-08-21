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
    
    # Example 1: Basic types with abbreviations
    print("📊 EXAMPLE 1: Basic Types with Abbreviations")
    print("-" * 50)
    data1 = [
        ['Alice', 25, 75000.50, True, '2023-01-15'],
        ['Bob', 30, 85000.75, False, '2023-02-20'],
        ['Charlie', 35, 95000.25, True, '2023-03-10'],
    ]
    headers1 = ['Name', 'Age', 'Salary', 'Active', 'HireDate']
    dtypes1_full = ['String', 'Int32', 'Float64', 'Boolean', 'Date']
    dtypes1_abbrev = [map_dtype(dt, 'polars') for dt in dtypes1_full]
    
    print(f"Full types: {dtypes1_full}")
    print(f"Abbreviated: {dtypes1_abbrev}")
    print()
    
    formatted1 = tv.format_table(data1, headers1, dtypes1_abbrev)
    print(formatted1)
    
    # Example 2: Date and time types
    print("\n📅 EXAMPLE 2: Date and Time Types")
    print("-" * 50)
    data2 = [
        ['2023-01-15', '2023-01-15 10:30:00', '10:30:00', '2023-01-15 10:30:00 UTC'],
        ['2023-02-20', '2023-02-20 14:45:00', '14:45:00', '2023-02-20 14:45:00 UTC'],
        ['2023-03-10', '2023-03-10 09:15:00', '09:15:00', '2023-03-10 09:15:00 UTC'],
    ]
    headers2 = ['Date', 'Datetime', 'Time', 'DatetimeUTC']
    dtypes2_full = ['Date', 'Datetime<ns>', 'Time', 'Datetime<ns, UTC>']
    dtypes2_abbrev = [map_dtype(dt, 'polars') for dt in dtypes2_full]
    
    print(f"Full types: {dtypes2_full}")
    print(f"Abbreviated: {dtypes2_abbrev}")
    print()
    
    formatted2 = tv.format_table(data2, headers2, dtypes2_abbrev)
    print(formatted2)
    
    # Example 3: List types
    print("\n📋 EXAMPLE 3: List Types")
    print("-" * 50)
    data3 = [
        ['Alice', [1.5, 2.3, 4.1], ['apple', 'banana'], [85, 92, 78]],
        ['Bob', [3.2, 1.8, 5.7], ['orange', 'grape'], [75, 88]],
        ['Charlie', [2.1, 4.5, 3.9], ['mango', 'kiwi', 'pear'], [92, 79, 86]],
    ]
    headers3 = ['Name', 'Scores', 'Fruits', 'Grades']
    dtypes3_full = ['String', 'List<Float64>', 'List<String>', 'List<Int64>']
    dtypes3_abbrev = [map_dtype(dt, 'polars') for dt in dtypes3_full]
    
    print(f"Full types: {dtypes3_full}")
    print(f"Abbreviated: {dtypes3_abbrev}")
    print()
    
    formatted3 = tv.format_table(data3, headers3, dtypes3_abbrev)
    print(formatted3)
    
    # Example 4: Struct types
    print("\n🏗️ EXAMPLE 4: Struct Types")
    print("-" * 50)
    data4 = [
        ['Alice', {'name': 'Alice', 'age': 25, 'active': True}],
        ['Bob', {'name': 'Bob', 'age': 30, 'active': False}],
        ['Charlie', {'name': 'Charlie', 'age': 35, 'active': True}],
    ]
    headers4 = ['ID', 'Profile']
    dtypes4 = ['String', 'Struct<name: String, age: Int32, active: Boolean>']
    
    formatted4 = tv.format_table(data4, headers4, dtypes4)
    print(formatted4)
    
    # Example 5: Array types with fixed sizes
    print("\n🔢 EXAMPLE 5: Array Types with Fixed Sizes")
    print("-" * 50)
    data5 = [
        ['Alice', [1.5, 2.3, 4.1], [85, 92, 78]],
        ['Bob', [3.2, 1.8, 5.7], [75, 88, 91]],
        ['Charlie', [2.1, 4.5, 3.9], [92, 79, 86]],
    ]
    headers5 = ['Name', 'Scores', 'Grades']
    dtypes5_full = ['String', 'Array<Float64, 3>', 'Array<Int64, 3>']
    dtypes5_abbrev = [map_dtype(dt, 'polars') for dt in dtypes5_full]
    
    print(f"Full types: {dtypes5_full}")
    print(f"Abbreviated: {dtypes5_abbrev}")
    print()
    
    formatted5 = tv.format_table(data5, headers5, dtypes5_abbrev)
    print(formatted5)
    
    # Example 6: Mixed complex types
    print("\n🔄 EXAMPLE 6: Mixed Complex Types")
    print("-" * 50)
    data6 = [
        ['Alice', [1.5, 2.3, 4.1], {'name': 'Alice', 'scores': [85, 92, 78]}],
        ['Bob', [3.2, 1.8, 5.7], {'name': 'Bob', 'scores': [75, 88]}],
        ['Charlie', [2.1, 4.5, 3.9], {'name': 'Charlie', 'scores': [92, 79, 86]}],
    ]
    headers6 = ['Name', 'Scores', 'Profile']
    dtypes6 = ['String', 'List<Float64>', 'Struct<name: String, scores: List<Int64>>']
    
    formatted6 = tv.format_table(data6, headers6, dtypes6)
    print(formatted6)
    
    # Example 7: Nullable types
    print("\n❓ EXAMPLE 7: Nullable Types")
    print("-" * 50)
    data7 = [
        ['Alice', 25, 75000.50, True],
        ['Bob', None, None, False],
        ['Charlie', 35, 95000.25, None],
    ]
    headers7 = ['Name', 'Age', 'Salary', 'Active']
    dtypes7 = ['String', 'Int64?', 'Float64?', 'Boolean?']
    
    formatted7 = tv.format_table(data7, headers7, dtypes7)
    print(formatted7)
    
    # Example 8: Decimal types
    print("\n💰 EXAMPLE 8: Decimal Types")
    print("-" * 50)
    data8 = [
        ['Product A', 19.99, 0.123456789],
        ['Product B', 29.99, 0.987654321],
        ['Product C', 39.99, 0.555555555],
    ]
    headers8 = ['Product', 'Price', 'Precision']
    dtypes8 = ['String', 'Decimal(10, 2)', 'Decimal(38, 9)']
    
    formatted8 = tv.format_table(data8, headers8, dtypes8)
    print(formatted8)
    
    # Example 9: Duration types
    print("\n⏱️ EXAMPLE 9: Duration Types")
    print("-" * 50)
    data9 = [
        ['Task A', '1h 30m', '45m', '2h 15m'],
        ['Task B', '2h 45m', '1h 20m', '3h 30m'],
        ['Task C', '1h 15m', '30m', '1h 45m'],
    ]
    headers9 = ['Task', 'Estimated', 'Actual', 'Total']
    dtypes9 = ['String', 'Duration<ns>', 'Duration<ns>', 'Duration<ns>']
    
    formatted9 = tv.format_table(data9, headers9, dtypes9)
    print(formatted9)
    
    # Example 10: Categorical and Enum types
    print("\n🏷️ EXAMPLE 10: Categorical and Enum Types")
    print("-" * 50)
    data10 = [
        ['Alice', 'Engineer', 'Active', 'High'],
        ['Bob', 'Designer', 'Inactive', 'Medium'],
        ['Charlie', 'Manager', 'Active', 'High'],
    ]
    headers10 = ['Name', 'Role', 'Status', 'Priority']
    dtypes10 = ['String', 'Categorical', 'Enum', 'Categorical']
    
    formatted10 = tv.format_table(data10, headers10, dtypes10)
    print(formatted10)
    
    # Example 11: Nested List and Array combinations
    print("\n🎯 EXAMPLE 11: Nested List and Array Combinations")
    print("-" * 50)
    data11 = [
        ['Alice', [[1, 2], [3, 4]], [1.5, 2.3, 4.1]],
        ['Bob', [[5, 6], [7, 8]], [3.2, 1.8, 5.7]],
        ['Charlie', [[9, 10], [11, 12]], [2.1, 4.5, 3.9]],
    ]
    headers11 = ['Name', 'Matrix', 'Scores']
    dtypes11 = ['String', 'List<List<Int64>>', 'Array<Float64, 3>']
    
    formatted11 = tv.format_table(data11, headers11, dtypes11)
    print(formatted11)
    
    # Example 12: Complex Struct with Lists
    print("\n🏛️ EXAMPLE 12: Complex Struct with Lists")
    print("-" * 50)
    data12 = [
        ['Alice', {'name': 'Alice', 'grades': [85, 92, 78], 'subjects': ['Math', 'Science']}],
        ['Bob', {'name': 'Bob', 'grades': [75, 88], 'subjects': ['English', 'History']}],
        ['Charlie', {'name': 'Charlie', 'grades': [92, 79, 86], 'subjects': ['Art', 'Music', 'PE']}],
    ]
    headers12 = ['ID', 'Student']
    dtypes12 = ['String', 'Struct<name: String, grades: List<Int64>, subjects: List<String>>']
    
    formatted12 = tv.format_table(data12, headers12, dtypes12)
    print(formatted12)
    
    print()


def demo_data_type_abbreviations():
    """Demonstrate data type abbreviations comparison."""
    print("=" * 60)
    print("DATA TYPE ABBREVIATIONS COMPARISON")
    print("=" * 60)
    
    # Comprehensive comparison data
    comparison_data = [
        # Basic types
        ['String', '<str>', 'UTF-8 encoded string type'],
        ['Utf8', '<str>', 'UTF-8 encoded string type (alias)'],
        ['Int64', '<i64>', '64-bit signed integer'],
        ['Int32', '<i32>', '32-bit signed integer'],
        ['Int16', '<i16>', '16-bit signed integer'],
        ['Int8', '<i8>', '8-bit signed integer'],
        ['UInt64', '<u64>', '64-bit unsigned integer'],
        ['Float64', '<f64>', '64-bit floating point'],
        ['Float32', '<f32>', '32-bit floating point'],
        ['Boolean', '<bool>', 'Boolean type'],
        ['Date', '<date>', 'Calendar date'],
        ['Datetime', '<dt>', 'Date and time'],
        ['Time', '<time>', 'Time of day'],
        ['Duration', '<td>', 'Time duration'],
        ['Categorical', '<cat>', 'String encoding type'],
        ['Enum', '<enum>', 'Fixed categorical encoding'],
        ['Binary', '<bin>', 'Binary data'],
        ['Object', '<obj>', 'Arbitrary Python objects'],
        ['Null', '<null>', 'Null values'],
        ['Unknown', '<unk>', 'Unknown type'],
        
        # Complex types
        ['List<String>', '<list<str>>', 'Variable length list of strings'],
        ['List<Int64>', '<list<i64>>', 'Variable length list of integers'],
        ['List<Float64>', '<list<f64>>', 'Variable length list of floats'],
        ['Array<Float64, 3>', '<arr<f64,3>>', 'Fixed-size array of 3 floats'],
        ['Array<Int64, 10>', '<arr<i64,10>>', 'Fixed-size array of 10 integers'],
        ['Struct<name: String, age: Int32>', '<struct>', 'Struct with name and age fields'],
        ['Struct<field1: String, field2: Int64>', '<struct>', 'Struct with generic field names'],
        
        # Parameterized types
        ['Datetime<ns>', '<dt>', 'Datetime with nanosecond precision'],
        ['Datetime<us>', '<dt>', 'Datetime with microsecond precision'],
        ['Datetime<ns, UTC>', '<dt>', 'Datetime with timezone'],
        ['Duration<ns>', '<td>', 'Duration with nanosecond precision'],
        ['Duration<us>', '<td>', 'Duration with microsecond precision'],
        ['Decimal(10, 2)', '<dec>', 'Decimal with 10 precision, 2 scale'],
        ['Decimal(38, 0)', '<dec>', 'Decimal with 38 precision, 0 scale'],
        
        # Nested complex types
        ['List<List<String>>', '<list<list<str>>>', 'List of lists of strings'],
        ['List<Struct<name: String, age: Int32>>', '<list<struct>>', 'List of structs'],
        ['Array<List<Int64>, 3>', '<arr<list<i64>,3>>', 'Fixed array of 3 lists of integers'],
        ['List<Array<Float64, 2>>', '<list<arr<f64,2>>>', 'List of fixed arrays of 2 floats'],
        
        # Nullable types
        ['Int64?', '<i64>', 'Nullable 64-bit integer'],
        ['String?', '<str>', 'Nullable string'],
        ['List<Int64>?', '<list<i64>>', 'Nullable list of integers'],
        ['Struct<name: String>?', '<struct>', 'Nullable struct'],
    ]
    
    headers = ['Polars Type', 'Abbreviated', 'Description']
    
    print("📊 COMPREHENSIVE DATA TYPE COMPARISON")
    print()
    
    # Format the comparison table
    formatted = tv.format_table(comparison_data, headers)
    print(formatted)
    
    print()
    print("🎯 QUICK REFERENCE - MOST COMMON TYPES:")
    print("=" * 50)
    common_types = [
        ('String', '<str>'),
        ('Int64', '<i64>'),
        ('Float64', '<f64>'),
        ('Boolean', '<bool>'),
        ('Datetime<ns>', '<dt>'),
        ('List<String>', '<list<str>>'),
        ('List<Int64>', '<list<i64>>'),
        ('Struct<name: String, age: Int32>', '<struct>'),
        ('Array<Float64, 3>', '<arr<f64,3>>'),
        ('Decimal(10, 2)', '<dec>'),
    ]
    
    for polars_type, abbreviated in common_types:
        print(f"  {polars_type:35} → {abbreviated}")
    
    print()
    print("🔍 AUTO-MAPPING EXAMPLE:")
    print("=" * 30)
    sample_types = ['String', 'Int64', 'List<Float64>', 'Struct<name: String>', 'Datetime<ns>']
    mapped = auto_map_dtypes(sample_types)
    print("Input types:")
    for dtype in sample_types:
        print(f"  {dtype}")
    print()
    print("Mapped to:")
    for mapped_type in mapped:
        print(f"  {mapped_type}")
    
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
    demo_data_type_abbreviations()
    
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
    print("• Data type abbreviations for clean display")


if __name__ == "__main__":
    main()
