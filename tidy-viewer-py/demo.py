#!/usr/bin/env python3
"""
Comprehensive demo script for tidy-viewer-py package

This script demonstrates all the features of the tidy-viewer-py package:
- Basic table formatting
- Different data structures (lists, dicts, DataFrames)
- File format support (CSV, Parquet, Arrow)
- Method chaining
- Error handling
- Advanced formatting options
"""

import sys
import os
import tempfile
import pandas as pd
import numpy as np

# Try to import polars (optional)
try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    print("⚠️  Polars not available - skipping polars examples")

def demo_basic_usage():
    """Demonstrate basic table formatting."""
    print("=" * 60)
    print("📊 BASIC USAGE")
    print("=" * 60)
    
    import tidy_viewer_py as tv
    
    # List of lists
    data = [
        ["Alice", "25", "Engineer", "New York"],
        ["Bob", "30", "Designer", "San Francisco"],
        ["Charlie", "35", "Manager", "Chicago"],
        ["Diana", "28", "Developer", "Boston"]
    ]
    headers = ["Name", "Age", "Job", "City"]
    
    print("\n1. Basic table formatting:")
    result = tv.format_table(data, headers)
    print(result)
    
    # Dictionary of lists
    dict_data = {
        "Name": ["Alice", "Bob", "Charlie", "Diana"],
        "Age": ["25", "30", "35", "28"],
        "Job": ["Engineer", "Designer", "Manager", "Developer"],
        "City": ["New York", "San Francisco", "Chicago", "Boston"]
    }
    
    print("\n2. Dictionary of lists:")
    result = tv.format_table(dict_data)
    print(result)
    
    # List of dictionaries
    list_dict_data = [
        {"Name": "Alice", "Age": "25", "Job": "Engineer", "City": "New York"},
        {"Name": "Bob", "Age": "30", "Job": "Designer", "City": "San Francisco"},
        {"Name": "Charlie", "Age": "35", "Job": "Manager", "City": "Chicago"},
        {"Name": "Diana", "Age": "28", "Job": "Developer", "City": "Boston"}
    ]
    
    print("\n3. List of dictionaries:")
    result = tv.format_table(list_dict_data)
    print(result)


def demo_pandas_dataframe():
    """Demonstrate pandas DataFrame support."""
    print("\n" + "=" * 60)
    print("🐼 PANDAS DATAFRAME SUPPORT")
    print("=" * 60)
    
    import tidy_viewer_py as tv
    
    # Create a pandas DataFrame
    df = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'Age': [25, 30, 35, 28],
        'Salary': [75000.123, 85000.456, 95000.789, 80000.321],
        'Department': ['Engineering', 'Design', 'Management', 'Engineering'],
        'Start_Date': ['2020-01-15', '2019-03-20', '2018-07-10', '2021-02-28']
    })
    
    print("\n1. Basic DataFrame formatting:")
    result = tv.format_dataframe(df)
    print(result)
    
    print("\n2. DataFrame with custom options:")
    options = tv.FormatOptions(
        max_rows=3,
        color_theme="dracula",
        significant_figures=2,
        title="Employee Data"
    )
    result = tv.format_dataframe(df, options)
    print(result)


def demo_numpy_array():
    """Demonstrate numpy array support."""
    print("\n" + "=" * 60)
    print("🔢 NUMPY ARRAY SUPPORT")
    print("=" * 60)
    
    import tidy_viewer_py as tv
    
    # Create a numpy array
    arr = np.array([
        [1.23456789, 2.34567890, 3.45678901],
        [4.56789012, 5.67890123, 6.78901234],
        [7.89012345, 8.90123456, 9.01234567],
        [10.12345678, 11.23456789, 12.34567890]
    ])
    
    print("\n1. Basic numpy array formatting:")
    result = tv.format_numpy_array(arr)
    print(result)
    
    print("\n2. Numpy array with scientific notation preserved:")
    options = tv.FormatOptions(
        preserve_scientific=True,
        color_theme="gruvbox",
        title="Scientific Data"
    )
    result = tv.format_numpy_array(arr, options)
    print(result)


def demo_file_formats():
    """Demonstrate file format support."""
    print("\n" + "=" * 60)
    print("📁 FILE FORMAT SUPPORT")
    print("=" * 60)
    
    import tidy_viewer_py as tv
    
    # Create test data
    test_data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'Age': [25, 30, 35, 28],
        'Salary': [75000.123, 85000.456, 95000.789, 80000.321],
        'Department': ['Engineering', 'Design', 'Management', 'Engineering']
    }
    df = pd.DataFrame(test_data)
    
    # Test CSV
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        csv_file = f.name
    
    try:
        print("\n1. CSV file formatting:")
        result = tv.format_csv(csv_file)
        print(result)
    except Exception as e:
        print(f"❌ CSV error: {e}")
    
    # Test Parquet
    with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as f:
        df.to_parquet(f.name, index=False)
        parquet_file = f.name
    
    try:
        print("\n2. Parquet file formatting:")
        result = tv.format_parquet(parquet_file)
        print(result)
    except Exception as e:
        print(f"❌ Parquet error: {e}")
    
    # Cleanup
    try:
        os.unlink(csv_file)
        os.unlink(parquet_file)
    except:
        pass


def demo_method_chaining():
    """Demonstrate method chaining with TV class."""
    print("\n" + "=" * 60)
    print("🔗 METHOD CHAINING")
    print("=" * 60)
    
    import tidy_viewer_py as tv
    
    data = [
        ["Alice", "25", "Engineer", "New York"],
        ["Bob", "30", "Designer", "San Francisco"],
        ["Charlie", "35", "Manager", "Chicago"],
        ["Diana", "28", "Developer", "Boston"],
        ["Eve", "32", "Analyst", "Seattle"],
        ["Frank", "29", "Designer", "Austin"]
    ]
    headers = ["Name", "Age", "Job", "City"]
    
    print("\n1. Method chaining example:")
    result = (tv.tv()
             .color_theme("dracula")
             .max_rows(3)
             .no_dimensions()
             .title("Employee Overview")
             .format_table(data, headers))
    print(result)
    
    print("\n2. One-liner with method chaining:")
    tv.tv().color_theme("gruvbox").max_rows(2).print_table(data, headers)


def demo_error_handling():
    """Demonstrate error handling."""
    print("\n" + "=" * 60)
    print("⚠️  ERROR HANDLING")
    print("=" * 60)
    
    import tidy_viewer_py as tv
    
    # Test with empty data
    try:
        result = tv.format_table([])
        print("Empty data handled gracefully")
    except Exception as e:
        print(f"Empty data error: {e}")
    
    # Test with non-existent file
    try:
        result = tv.format_csv("non_existent_file.csv")
    except Exception as e:
        print(f"File not found error: {e}")
    
    # Test with invalid data structure
    try:
        result = tv.format_table("not a list or dict")
    except Exception as e:
        print(f"Invalid data type error: {e}")


def demo_advanced_features():
    """Demonstrate advanced formatting features."""
    print("\n" + "=" * 60)
    print("🎨 ADVANCED FEATURES")
    print("=" * 60)
    
    import tidy_viewer_py as tv
    
    # Data with scientific notation and NA values
    data = [
        ["Alice", "25", "1.23e+06", "Engineer"],
        ["Bob", "30", "2.45e+05", "Designer"],
        ["Charlie", "NA", "3.67e+04", "Manager"],
        ["Diana", "28", "4.89e+03", "Developer"],
        ["Eve", "32", "NA", "Analyst"]
    ]
    headers = ["Name", "Age", "Salary", "Job"]
    
    print("\n1. Scientific notation preserved:")
    options = tv.FormatOptions(
        preserve_scientific=True,
        color_theme="solarized_light",
        significant_figures=4
    )
    result = tv.format_table(data, headers, options)
    print(result)
    
    print("\n2. No colors (for piping):")
    options = tv.FormatOptions(
        use_color=False,
        no_dimensions=True,
        no_row_numbering=True
    )
    result = tv.format_table(data, headers, options)
    print(result)


def demo_polars_dataframe():
    """Demonstrate polars DataFrame support (if available)."""
    if not POLARS_AVAILABLE:
        print("\n" + "=" * 60)
        print("🚀 POLARS DATAFRAME SUPPORT (SKIPPED)")
        print("=" * 60)
        print("Polars not available. Install with: pip install polars")
        return
    
    print("\n" + "=" * 60)
    print("🚀 POLARS DATAFRAME SUPPORT")
    print("=" * 60)
    
    import tidy_viewer_py as tv
    
    # Create a polars DataFrame
    df = pl.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'Age': [25, 30, 35, 28],
        'Salary': [75000.123, 85000.456, 95000.789, 80000.321],
        'Department': ['Engineering', 'Design', 'Management', 'Engineering']
    })
    
    print("\n1. Basic polars DataFrame formatting:")
    result = tv.format_polars_dataframe(df)
    print(result)
    
    print("\n2. Polars DataFrame with custom options:")
    options = tv.FormatOptions(
        max_rows=2,
        color_theme="one_dark",
        title="Polars Data"
    )
    result = tv.format_polars_dataframe(df, options)
    print(result)


def main():
    """Run all demos."""
    print("🎯 TIDY-VIEWER-PY COMPREHENSIVE DEMO")
    print("=" * 60)
    
    try:
        demo_basic_usage()
        demo_pandas_dataframe()
        demo_numpy_array()
        demo_file_formats()
        demo_method_chaining()
        demo_error_handling()
        demo_advanced_features()
        demo_polars_dataframe()
        
        print("\n" + "=" * 60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n🎉 The tidy-viewer-py package is working correctly!")
        print("📚 Check the documentation for more examples.")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

