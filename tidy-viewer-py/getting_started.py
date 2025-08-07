#!/usr/bin/env python3
"""
Getting Started with tidy-viewer-py

This script demonstrates how to use the tv package to format and display
tabular data from various sources including CSVs, pandas DataFrames, and Polars DataFrames.
"""

import os

try:
    import tidy_viewer_py as tv
    print("✅ Successfully imported tidy_viewer_py")
except ImportError as e:
    print(f"❌ Failed to import tidy_viewer_py: {e}")
    print("Make sure you've built the package with: uv run maturin develop")
    exit(1)

def demo_basic_usage():
    """Demonstrate basic usage with simple data structures."""
    print("\n" + "="*60)
    print("BASIC USAGE")
    print("="*60)
    
    # Simple list of lists
    data = [
        ['Alice', 25, 'Engineer'],
        ['Bob', 30, 'Designer'],
        ['Charlie', 35, 'Manager']
    ]
    headers = ['Name', 'Age', 'Role']
    
    print("📊 Formatting a simple list of lists:")
    result = tv.format_table(data, headers=headers)
    print(result)
    
    # Dictionary of lists
    data_dict = {
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'Role': ['Engineer', 'Designer', 'Manager']
    }
    
    print("\n📊 Formatting a dictionary of lists:")
    # Convert all values to strings to avoid type conversion issues
    data_dict_str = {k: [str(v) for v in vals] for k, vals in data_dict.items()}
    result = tv.format_table(data_dict_str)
    print(result)

def demo_csv_handling():
    """Demonstrate CSV file handling."""
    print("\n" + "="*60)
    print("CSV HANDLING")
    print("="*60)
    
    # Check if iris.csv exists
    iris_path = "../data/iris.csv"
    if os.path.exists(iris_path):
        print(f"📁 Reading CSV file: {iris_path}")
        result = tv.format_csv(iris_path)
        print(result)
    else:
        print(f"⚠️  File not found: {iris_path}")
        print("Creating a sample CSV for demonstration...")
        
        # Create a sample CSV
        sample_data = [
            ['Name', 'Age', 'City'],
            ['Alice', 25, 'New York'],
            ['Bob', 30, 'Los Angeles'],
            ['Charlie', 35, 'Chicago']
        ]
        
        with open('sample.csv', 'w') as f:
            for row in sample_data:
                f.write(','.join(map(str, row)) + '\n')
        
        print("📁 Reading sample CSV file:")
        result = tv.format_csv('sample.csv')
        print(result)
        
        # Clean up
        os.remove('sample.csv')

def demo_pandas_integration():
    """Demonstrate pandas DataFrame integration."""
    print("\n" + "="*60)
    print("PANDAS INTEGRATION")
    print("="*60)
    
    try:
        import pandas as pd
        import numpy as np
        
        # Create sample pandas DataFrame
        df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
            'Age': [25, 30, 35, 28],
            'Salary': [75000, 85000, 95000, 80000],
            'Department': ['Engineering', 'Design', 'Management', 'Engineering'],
            'Start_Date': pd.to_datetime(['2020-01-15', '2019-03-20', '2018-07-10', '2021-02-28'])
        })
        
        print("📊 Formatting pandas DataFrame:")
        result = tv.format_dataframe(df)
        print(result)
        
        # Demonstrate with numeric data
        numeric_df = pd.DataFrame({
            'ID': range(1, 11),
            'Value': np.random.randn(10) * 100,
            'Percentage': np.random.rand(10) * 100,
            'Integer': np.random.randint(1, 1000, 10)
        })
        
        print("\n📊 Formatting numeric pandas DataFrame:")
        result = tv.format_dataframe(numeric_df)
        print(result)
        
    except ImportError:
        print("⚠️  pandas not available. Install with: uv add pandas")

def demo_polars_integration():
    """Demonstrate Polars DataFrame integration."""
    print("\n" + "="*60)
    print("POLARS INTEGRATION")
    print("="*60)
    
    try:
        import polars as pl
        
        # Create sample Polars DataFrame
        df = pl.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
            'Age': [25, 30, 35, 28],
            'Salary': [75000, 85000, 95000, 80000],
            'Department': ['Engineering', 'Design', 'Management', 'Engineering']
        })
        
        print("📊 Formatting Polars DataFrame:")
        result = tv.format_polars_dataframe(df)
        print(result)
        
        # Demonstrate with larger dataset
        large_df = pl.DataFrame({
            'ID': range(1, 21),
            'Category': ['A', 'B', 'C', 'D'] * 5,
            'Value': [i * 1.5 for i in range(1, 21)],
            'Status': ['Active', 'Inactive'] * 10
        })
        
        print("\n📊 Formatting larger Polars DataFrame:")
        result = tv.format_polars_dataframe(large_df)
        print(result)
        
    except ImportError:
        print("⚠️  polars not available. Install with: uv add polars")

def demo_advanced_features():
    """Demonstrate advanced formatting features."""
    print("\n" + "="*60)
    print("ADVANCED FEATURES")
    print("="*60)
    
    # Create sample data
    data = [
        ['Product A', 1234.5678, 99.99, 'In Stock'],
        ['Product B', 987.6543, 149.99, 'Low Stock'],
        ['Product C', 456.7890, 299.99, 'Out of Stock']
    ]
    headers = ['Product', 'SKU', 'Price', 'Status']
    
    # Basic formatting
    print("📊 Basic formatting:")
    result = tv.format_table(data, headers=headers)
    print(result)
    
    # Custom options
    print("\n📊 Custom formatting (no colors, no dimensions):")
    options = tv.FormatOptions(
        use_color=False,
        no_dimensions=True,
        no_row_numbering=True
    )
    result = tv.format_table(data, headers=headers, options=options)
    print(result)
    
    # Method chaining with TV class
    print("\n📊 Using TV class for method chaining:")
    tv_instance = tv.TV()
    result = tv_instance.format_table(data, headers=headers)
    print(result)
    
    # Custom color theme
    print("\n📊 Custom color theme:")
    options = tv.FormatOptions(
        use_color=True,
        color_theme="gruvbox"
    )
    result = tv.format_table(data, headers=headers, options=options)
    print(result)

def demo_file_formats():
    """Demonstrate different file format support."""
    print("\n" + "="*60)
    print("FILE FORMAT SUPPORT")
    print("="*60)
    
    # Check for various file formats in the data directory
    data_dir = "../data"
    if os.path.exists(data_dir):
        print(f"📁 Checking for files in {data_dir}:")
        
        for file in os.listdir(data_dir):
            file_path = os.path.join(data_dir, file)
            if file.endswith('.csv'):
                print(f"\n📄 CSV file: {file}")
                try:
                    result = tv.format_csv(file_path)
                    print(result[:500] + "..." if len(result) > 500 else result)
                except Exception as e:
                    print(f"❌ Error reading {file}: {e}")
    
    print("\n💡 Supported file formats:")
    print("   • CSV files (.csv)")
    print("   • Parquet files (.parquet)")
    print("   • Arrow files (.arrow, .feather, .ipc)")

def main():
    """Run all demonstrations."""
    print("🚀 Getting Started with tidy-viewer-py")
    print("="*60)
    
    # Run all demos
    demo_basic_usage()
    demo_csv_handling()
    demo_pandas_integration()
    demo_polars_integration()
    demo_advanced_features()
    demo_file_formats()
    
    print("\n" + "="*60)
    print("✅ Getting Started Demo Complete!")
    print("="*60)
    print("\n📚 Key takeaways:")
    print("   • Use format_table() for basic data structures")
    print("   • Use format_csv() for CSV files")
    print("   • Use format_dataframe() for pandas DataFrames")
    print("   • Use format_polars_dataframe() for Polars DataFrames")
    print("   • Use FormatOptions for custom styling")
    print("   • Use TV class for method chaining")
    print("\n🔧 To install dependencies:")
    print("   uv add pandas polars pyarrow")

if __name__ == "__main__":
    main()
