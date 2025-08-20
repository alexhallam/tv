#!/usr/bin/env python3
"""
Demonstration of tidy-viewer-py with data type mapping functionality.

This script creates various dataframes and shows how data types are automatically
detected and displayed in formatted tables.
"""

import sys
import os

# Add the current directory to the path so we can import tidy_viewer_py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import tidy_viewer_py as tv
    from tidy_viewer_py import format_table, map_dtype, map_dtypes, auto_map_dtypes
    print("✅ Successfully imported tidy_viewer_py")
except ImportError as e:
    print(f"❌ Failed to import tidy_viewer_py: {e}")
    print("Make sure you've run 'maturin develop' to build the module")
    sys.exit(1)

def demo_basic_dataframe():
    """Demonstrate basic DataFrame formatting with data types."""
    print("\n" + "="*60)
    print("1. BASIC PANDAS DATAFRAME WITH DATA TYPES")
    print("="*60)
    
    try:
        import pandas as pd
        
        # Create a simple DataFrame
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
            'age': [25, 30, 35, 28],
            'salary': [50000.0, 60000.0, 70000.0, 55000.0],
            'active': [True, False, True, True],
            'department': ['Engineering', 'Design', 'Management', 'Engineering']
        })
        
        print("DataFrame with automatic data type detection:")
        tv.print_dataframe(df)
        
        print("\nSame DataFrame without data types:")
        tv.print_dataframe(df, show_dtypes=False)
        
    except ImportError:
        print("❌ pandas not available - skipping pandas demo")

def demo_polars_dataframe():
    """Demonstrate Polars DataFrame formatting with data types."""
    print("\n" + "="*60)
    print("2. POLARS DATAFRAME WITH DATA TYPES")
    print("="*60)
    
    try:
        import polars as pl
        
        # Create a Polars DataFrame
        df = pl.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
            'age': [25, 30, 35, 28],
            'salary': [50000.0, 60000.0, 70000.0, 55000.0],
            'active': [True, False, True, True],
            'department': ['Engineering', 'Design', 'Management', 'Engineering']
        })
        
        print("Polars DataFrame with automatic data type detection:")
        tv.print_polars_dataframe(df)
        
        print("\nSame Polars DataFrame without data types:")
        tv.print_polars_dataframe(df, show_dtypes=False)
        
    except ImportError:
        print("❌ polars not available - skipping polars demo")

def demo_complex_dataframe():
    """Demonstrate DataFrame with more complex data types."""
    print("\n" + "="*60)
    print("3. COMPLEX DATAFRAME WITH VARIOUS DATA TYPES")
    print("="*60)
    
    try:
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # Create a DataFrame with various data types
        df = pd.DataFrame({
            'id': [1, 2, 3, 4],
            'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
            'age': [25, 30, 35, 28],
            'salary': [50000.50, 60000.75, 70000.25, 55000.00],
            'active': [True, False, True, True],
            'hire_date': [
                datetime(2020, 1, 15),
                datetime(2019, 6, 20),
                datetime(2018, 3, 10),
                datetime(2021, 9, 5)
            ],
            'last_login': [
                datetime.now() - timedelta(hours=2),
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(hours=5),
                datetime.now() - timedelta(minutes=30)
            ],
            'department': ['Engineering', 'Design', 'Management', 'Engineering'],
            'skills': [['Python', 'Rust'], ['Design', 'UI/UX'], ['Leadership', 'Strategy'], ['Python', 'JavaScript']],
            'metadata': [{'level': 'Senior'}, {'level': 'Mid'}, {'level': 'Senior'}, {'level': 'Junior'}]
        })
        
        print("Complex DataFrame with various data types:")
        tv.print_dataframe(df)
        
    except ImportError:
        print("❌ pandas not available - skipping complex demo")

def demo_manual_data_types():
    """Demonstrate manual data type specification."""
    print("\n" + "="*60)
    print("4. MANUAL DATA TYPE SPECIFICATION")
    print("="*60)
    
    # Sample data
    data = [
        ['Alice', '25', 'Engineer', '75000.50', 'True'],
        ['Bob', '30', 'Designer', '65000.25', 'False'],
        ['Charlie', '35', 'Manager', '95000.75', 'True'],
        ['Diana', '28', 'Developer', '80000.00', 'True']
    ]
    
    headers = ['Name', 'Age', 'Role', 'Salary', 'Active']
    
    # Different data type specifications
    print("With pandas-style data types:")
    pandas_dtypes = ['object', 'int64', 'object', 'float64', 'bool']
    tv.print_table(data, headers, pandas_dtypes)
    
    print("\nWith polars-style data types:")
    polars_dtypes = ['String', 'Int64', 'String', 'Float64', 'Boolean']
    tv.print_table(data, headers, polars_dtypes)
    
    print("\nWith custom abbreviated types:")
    custom_dtypes = ['<str>', '<i64>', '<str>', '<f64>', '<bool>']
    tv.print_table(data, headers, custom_dtypes)

def demo_data_type_mapping():
    """Demonstrate the data type mapping utilities."""
    print("\n" + "="*60)
    print("5. DATA TYPE MAPPING UTILITIES")
    print("="*60)
    
    print("Individual type mapping:")
    print(f"map_dtype('int64', 'pandas') → {map_dtype('int64', 'pandas')}")
    print(f"map_dtype('String', 'polars') → {map_dtype('String', 'polars')}")
    print(f"map_dtype('Utf8', 'arrow') → {map_dtype('Utf8', 'arrow')}")
    
    print("\nComplex type mapping:")
    print(f"map_dtype('List<Int64>') → {map_dtype('List<Int64>')}")
    print(f"map_dtype('Struct<field1: String, field2: Int64>') → {map_dtype('Struct<field1: String, field2: Int64>')}")
    print(f"map_dtype('Int64?') → {map_dtype('Int64?')}")
    
    print("\nList mapping:")
    pandas_dtypes = ['object', 'int64', 'float64', 'bool', 'datetime64[ns]']
    print(f"Input: {pandas_dtypes}")
    print(f"Output: {map_dtypes(pandas_dtypes, 'pandas')}")
    
    print("\nAuto-detection:")
    print(f"Auto-detected pandas: {auto_map_dtypes(pandas_dtypes)}")
    
    polars_dtypes = ['String', 'Int64', 'Float64', 'Boolean', 'Datetime']
    print(f"Auto-detected polars: {auto_map_dtypes(polars_dtypes)}")

def demo_method_chaining():
    """Demonstrate method chaining with data types."""
    print("\n" + "="*60)
    print("6. METHOD CHAINING WITH DATA TYPES")
    print("="*60)
    
    try:
        import pandas as pd
        
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank'],
            'age': [25, 30, 35, 28, 32, 29],
            'salary': [50000.0, 60000.0, 70000.0, 55000.0, 65000.0, 58000.0],
            'department': ['Engineering', 'Design', 'Management', 'Engineering', 'Sales', 'Marketing']
        })
        
        print("Method chaining with custom options:")
        tv.tv().color_theme("gruvbox").max_rows(3).title("Employee Data").print_dataframe(df)
        
        print("\nMethod chaining without data types:")
        tv.tv().color_theme("dracula").max_rows(3).title("Employee Data (No Types)").print_dataframe(df, show_dtypes=False)
        
    except ImportError:
        print("❌ pandas not available - skipping method chaining demo")

def demo_edge_cases():
    """Demonstrate edge cases and error handling."""
    print("\n" + "="*60)
    print("7. EDGE CASES AND ERROR HANDLING")
    print("="*60)
    
    print("Data types without headers:")
    data = [['Alice', '25'], ['Bob', '30']]
    data_types = ['<str>', '<i64>']
    tv.print_table(data, None, data_types)
    
    print("\nValidation error (wrong data types length):")
    try:
        wrong_dtypes = ['<str>']  # Only 1 type for 2 columns
        tv.print_table(data, ['Name', 'Age'], wrong_dtypes)
    except Exception as e:
        print(f"✅ Correctly caught error: {e}")
    
    print("\nEmpty data types list:")
    tv.print_table(data, ['Name', 'Age'], [])

def main():
    """Run all demonstrations."""
    print("🚀 Tidy Viewer Py - Data Type Mapping Demo")
    print("This demo shows how data types are automatically detected and displayed")
    
    # Run all demos
    demo_basic_dataframe()
    demo_polars_dataframe()
    demo_complex_dataframe()
    demo_manual_data_types()
    demo_data_type_mapping()
    demo_method_chaining()
    demo_edge_cases()
    
    print("\n" + "="*60)
    print("🎉 Demo Complete!")
    print("="*60)
    print("Key features demonstrated:")
    print("• Automatic data type detection from pandas/polars DataFrames")
    print("• Manual data type specification")
    print("• Complex type handling (Lists, Structs, etc.)")
    print("• Data type mapping utilities")
    print("• Method chaining with data type control")
    print("• Error handling and validation")

if __name__ == "__main__":
    main()
