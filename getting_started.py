#!/usr/bin/env python3
"""
Getting Started with tidy-viewer-py

This script demonstrates how to use the tv package to format and display
tabular data from various sources including CSVs, pandas DataFrames, and Polars DataFrames.
"""

import sys
import os
import tempfile

# Try to import tidy_viewer_py - works when package is installed
try:
    import tidy_viewer_py as tv
    print("✅ Successfully imported tidy_viewer_py")
except ImportError:
    # Fallback for development: try multiple possible paths
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'tidy-viewer-py'),  # From root
        os.path.join(os.path.dirname(__file__), '..', 'tidy-viewer-py'),  # From tidy-viewer-py
        os.path.join(os.path.dirname(__file__), '..', '..', 'tidy-viewer-py'),  # From subdir
    ]
    
    imported = False
    for path in possible_paths:
        try:
            if os.path.exists(path):
                sys.path.insert(0, path)
                import tidy_viewer_py as tv
                print(f"✅ Successfully imported tidy_viewer_py (development mode from {path})")
                imported = True
                break
        except ImportError:
            continue
    
    if not imported:
        print("❌ Failed to import tidy_viewer_py")
        print("Make sure you've installed the package with: uv pip install .")
        print("Or for development: uv run maturin develop")
        sys.exit(1)

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
    result = tv.format_table(data_dict)
    print(result)

def demo_csv_with_pandas():
    """Demonstrate reading CSV with pandas then formatting."""
    print("\n" + "="*60)
    print("CSV WITH PANDAS")
    print("="*60)
    
    try:
        import pandas as pd
        
        # Create sample CSV data
        csv_data = """Name,Age,City,Salary
Alice,25,New York,75000
Bob,30,Los Angeles,85000
Charlie,35,Chicago,95000
Diana,28,Boston,80000
Eve,32,Seattle,90000"""
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            temp_csv_path = f.name
        
        try:
            # Read with pandas
            print("📁 Reading CSV with pandas:")
            df = pd.read_csv(temp_csv_path)
            print("Pandas DataFrame:")
            print(df)
            
            # Format with tidy-viewer
            print("\n📊 Formatted with tidy-viewer:")
            result = tv.format_dataframe(df)
            print(result)
            
        finally:
            # Clean up temp file
            os.unlink(temp_csv_path)
            
    except ImportError:
        print("⚠️  pandas not available. Install with: uv add pandas")

def demo_csv_with_polars():
    """Demonstrate reading CSV with polars then formatting."""
    print("\n" + "="*60)
    print("CSV WITH POLARS")
    print("="*60)
    
    try:
        import polars as pl
        
        # Create sample CSV data
        csv_data = """Name,Age,City,Salary
Alice,25,New York,75000
Bob,30,Los Angeles,85000
Charlie,35,Chicago,95000
Diana,28,Boston,80000
Eve,32,Seattle,90000"""
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            temp_csv_path = f.name
        
        try:
            # Read with polars
            print("📁 Reading CSV with polars:")
            df = pl.read_csv(temp_csv_path)
            print("Polars DataFrame:")
            print(df)
            
            # Format with tidy-viewer
            print("\n📊 Formatted with tidy-viewer:")
            result = tv.format_polars_dataframe(df)
            print(result)
            
        finally:
            # Clean up temp file
            os.unlink(temp_csv_path)
            
    except ImportError:
        print("⚠️  polars not available. Install with: uv add polars")

def demo_csv_direct():
    """Demonstrate reading CSV directly with tidy-viewer."""
    print("\n" + "="*60)
    print("CSV DIRECT WITH TIDY-VIEWER")
    print("="*60)
    
    # Create sample CSV data
    csv_data = """Name,Age,City,Salary
Alice,25,New York,75000
Bob,30,Los Angeles,85000
Charlie,35,Chicago,95000
Diana,28,Boston,80000
Eve,32,Seattle,90000"""
    
    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_data)
        temp_csv_path = f.name
    
    try:
        print("📁 Reading CSV directly with tidy-viewer:")
        result = tv.format_csv(temp_csv_path)
        print(result)
        
    finally:
        # Clean up temp file
        os.unlink(temp_csv_path)

def demo_parquet_with_pandas():
    """Demonstrate reading Parquet with pandas then formatting."""
    print("\n" + "="*60)
    print("PARQUET WITH PANDAS")
    print("="*60)
    
    try:
        import pandas as pd
        
        # Create sample data
        data = {
            'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
            'Age': [25, 30, 35, 28],
            'Salary': [75000, 85000, 95000, 80000],
            'Department': ['Engineering', 'Design', 'Management', 'Engineering']
        }
        
        # Create temporary parquet file
        with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as f:
            temp_parquet_path = f.name
        
        try:
            # Create DataFrame and save as parquet
            df = pd.DataFrame(data)
            df.to_parquet(temp_parquet_path)
            
            # Read with pandas
            print("📁 Reading Parquet with pandas:")
            df_read = pd.read_parquet(temp_parquet_path)
            print("Pandas DataFrame:")
            print(df_read)
            
            # Format with tidy-viewer
            print("\n📊 Formatted with tidy-viewer:")
            result = tv.format_dataframe(df_read)
            print(result)
            
        finally:
            # Clean up temp file
            os.unlink(temp_parquet_path)
            
    except ImportError:
        print("⚠️  pandas not available. Install with: uv add pandas")

def demo_parquet_direct():
    """Demonstrate reading Parquet directly with tidy-viewer."""
    print("\n" + "="*60)
    print("PARQUET DIRECT WITH TIDY-VIEWER")
    print("="*60)
    
    try:
        import pandas as pd
        
        # Create sample data
        data = {
            'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
            'Age': [25, 30, 35, 28],
            'Salary': [75000, 85000, 95000, 80000],
            'Department': ['Engineering', 'Design', 'Management', 'Engineering']
        }
        
        # Create temporary parquet file
        with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as f:
            temp_parquet_path = f.name
        
        try:
            # Create DataFrame and save as parquet
            df = pd.DataFrame(data)
            df.to_parquet(temp_parquet_path)
            
            # Read directly with tidy-viewer
            print("📁 Reading Parquet directly with tidy-viewer:")
            result = tv.format_parquet(temp_parquet_path)
            print(result)
            
        finally:
            # Clean up temp file
            os.unlink(temp_parquet_path)
            
    except ImportError:
        print("⚠️  pandas not available for creating parquet. Install with: uv add pandas")

def demo_feather_with_pandas():
    """Demonstrate reading Feather with pandas then formatting."""
    print("\n" + "="*60)
    print("FEATHER WITH PANDAS")
    print("="*60)
    
    try:
        import pandas as pd
        
        # Create sample data
        data = {
            'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
            'Age': [25, 30, 35, 28],
            'Salary': [75000, 85000, 95000, 80000],
            'Department': ['Engineering', 'Design', 'Management', 'Engineering']
        }
        
        # Create temporary feather file
        with tempfile.NamedTemporaryFile(suffix='.feather', delete=False) as f:
            temp_feather_path = f.name
        
        try:
            # Create DataFrame and save as feather
            df = pd.DataFrame(data)
            df.to_feather(temp_feather_path, compression=None)  # No compression
            
            # Read with pandas
            print("📁 Reading Feather with pandas:")
            df_read = pd.read_feather(temp_feather_path)
            print("Pandas DataFrame:")
            print(df_read)
            
            # Format with tidy-viewer
            print("\n📊 Formatted with tidy-viewer:")
            result = tv.format_dataframe(df_read)
            print(result)
            
        finally:
            # Clean up temp file
            os.unlink(temp_feather_path)
            
    except ImportError:
        print("⚠️  pandas not available. Install with: uv add pandas")

def demo_feather_direct():
    """Demonstrate reading Feather directly with tidy-viewer."""
    print("\n" + "="*60)
    print("FEATHER DIRECT WITH TIDY-VIEWER")
    print("="*60)
    
    try:
        import pandas as pd
        
        # Create sample data
        data = {
            'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
            'Age': [25, 30, 35, 28],
            'Salary': [75000, 85000, 95000, 80000],
            'Department': ['Engineering', 'Design', 'Management', 'Engineering']
        }
        
        # Create temporary feather file
        with tempfile.NamedTemporaryFile(suffix='.feather', delete=False) as f:
            temp_feather_path = f.name
        
        try:
            # Create DataFrame and save as feather
            df = pd.DataFrame(data)
            df.to_feather(temp_feather_path, compression=None)  # No compression
            
            # Read directly with tidy-viewer
            print("📁 Reading Feather directly with tidy-viewer:")
            result = tv.format_arrow(temp_feather_path)
            print(result)
            
        finally:
            # Clean up temp file
            os.unlink(temp_feather_path)
            
    except ImportError:
        print("⚠️  pandas not available for creating feather. Install with: uv add pandas")
    except Exception as e:
        print(f"⚠️  Feather demo failed: {e}")
        print("This might be due to compression settings or missing dependencies.")

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
    
    # Custom color scheme (using built-in themes)
    print("\n📊 Custom color scheme (gruvbox theme):")
    options = tv.FormatOptions(
        use_color=True,
        color_theme="gruvbox"
    )
    result = tv.format_table(data, headers=headers, options=options)
    print(result)

def demo_numeric_formatting():
    """Demonstrate numeric formatting features."""
    print("\n" + "="*60)
    print("NUMERIC FORMATTING")
    print("="*60)
    
    # Create data with various numeric types
    data = [
        ['Small', 1.23456789, 0.00123456, 1234567.89],
        ['Medium', 12.3456789, 0.0123456, 123456.789],
        ['Large', 123.456789, 0.123456, 12345.6789],
        ['Scientific', 1.23e-5, 1.23e5, 1.23e10],
        ['Integers', 123, 12345, 123456789],
        ['Mixed', 1.23, 123, 1.23e6, 'Text']
    ]
    headers = ['Type', 'Float1', 'Float2', 'Float3']
    
    print("📊 Default numeric formatting:")
    result = tv.format_table(data, headers=headers)
    print(result)
    
    print("\n📊 With 2 significant figures:")
    options = tv.FormatOptions(significant_figures=2)
    result = tv.format_table(data, headers=headers, options=options)
    print(result)
    
    print("\n📊 With 5 significant figures:")
    options = tv.FormatOptions(significant_figures=5)
    result = tv.format_table(data, headers=headers, options=options)
    print(result)

def main():
    """Run all demonstrations."""
    print("🚀 Getting Started with tidy-viewer-py")
    print("="*60)
    
    # Run all demos
    demo_basic_usage()
    demo_csv_with_pandas()
    demo_csv_with_polars()
    demo_csv_direct()
    demo_parquet_with_pandas()
    demo_parquet_direct()
    demo_feather_with_pandas()
    demo_feather_direct()
    demo_advanced_features()
    demo_numeric_formatting()
    
    print("\n" + "="*60)
    print("✅ Getting Started Demo Complete!")
    print("="*60)
    print("\n📚 Key takeaways:")
    print("   • Use format_table() for basic data structures")
    print("   • Use format_csv() for CSV files")
    print("   • Use format_parquet() for Parquet files")
    print("   • Use format_arrow() for Arrow/Feather files")
    print("   • Use format_dataframe() for pandas DataFrames")
    print("   • Use format_polars_dataframe() for Polars DataFrames")
    print("   • Use FormatOptions for custom styling")
    print("   • Use TV class for method chaining")
    print("\n🔧 To install dependencies:")
    print("   uv add pandas polars pyarrow")

if __name__ == "__main__":
    main()
