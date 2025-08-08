#!/usr/bin/env python3
"""
Test script for Python tv port
"""

import sys
import os

def main():
    csv_file = "../data/iris.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return
    
    try:
        import tidy_viewer_py as tv
    except ImportError as e:
        print(f"❌ Failed to import tidy_viewer_py: {e}")
        return
    
    print("🐍 Testing Python tv port")
    print("=" * 50)
    
    # Test 1: Basic CSV viewing
    print("\n1️⃣ Basic CSV viewing:")
    print(tv.format_csv(csv_file))
    
    # Test 2: Limited rows
    print("\n2️⃣ Limited rows (5):")
    opts = tv.FormatOptions(max_rows=5)
    print(tv.format_csv(csv_file, opts))
    
    # Test 3: Different color theme
    print("\n3️⃣ Gruvbox theme:")
    opts = tv.FormatOptions(color_theme="gruvbox")
    print(tv.format_csv(csv_file, opts))
    
    # Test 4: No row numbers
    print("\n4️⃣ No row numbers:")
    opts = tv.FormatOptions(no_row_numbering=True)
    print(tv.format_csv(csv_file, opts))
    
    # Test 5: No dimensions
    print("\n5️⃣ No dimensions:")
    opts = tv.FormatOptions(no_dimensions=True)
    print(tv.format_csv(csv_file, opts))
    
    # Test 6: Custom significant figures
    print("\n6️⃣ 5 significant figures:")
    opts = tv.FormatOptions(significant_figures=5)
    print(tv.format_csv(csv_file, opts))
    
    # Test 7: TV class method chaining
    print("\n7️⃣ Method chaining:")
    tv.TV().max_rows(3).color_theme("dracula").print_csv(csv_file)
    
    # Test 8: Pandas DataFrame (if available)
    try:
        import pandas as pd
        print("\n8️⃣ Pandas DataFrame:")
        df = pd.read_csv(csv_file)
        print(tv.format_dataframe(df.head(3)))
    except ImportError:
        print("\n8️⃣ Pandas not available, skipping DataFrame test")

if __name__ == "__main__":
    main()
