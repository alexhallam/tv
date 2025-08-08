#!/usr/bin/env python3
"""
Compare Rust tidy-viewer and Python port side by side
"""

import subprocess
import sys
import os

def run_rust_tv(csv_file, *args):
    """Run Rust tidy-viewer"""
    cmd = ['tidy-viewer', csv_file] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Exception: {e}"

def run_python_tv(csv_file, max_rows=None):
    """Run Python tv port"""
    try:
        import tidy_viewer_py as tv
        if max_rows:
            opts = tv.FormatOptions(max_rows=max_rows)
            return tv.format_csv(csv_file, opts)
        else:
            return tv.format_csv(csv_file)
    except Exception as e:
        return f"Exception: {e}"

def main():
    csv_file = "../data/iris.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return
    
    print("🔄 Comparing Rust tidy-viewer vs Python port")
    print("=" * 60)
    
    # Test 1: Basic viewing
    print("\n📊 Test 1: Basic CSV viewing")
    print("-" * 40)
    
    print("🔧 Rust tidy-viewer:")
    print(run_rust_tv(csv_file))
    
    print("\n🐍 Python port:")
    print(run_python_tv(csv_file))
    
    # Test 2: Limited rows
    print("\n📊 Test 2: Limited rows (5)")
    print("-" * 40)
    
    print("🔧 Rust tidy-viewer:")
    print(run_rust_tv(csv_file, "-n", "5"))
    
    print("\n🐍 Python port:")
    print(run_python_tv(csv_file, max_rows=5))
    
    # Test 3: No row numbers
    print("\n📊 Test 3: No row numbers")
    print("-" * 40)
    
    print("🔧 Rust tidy-viewer:")
    print(run_rust_tv(csv_file, "-R"))
    
    print("\n🐍 Python port:")
    try:
        import tidy_viewer_py as tv
        opts = tv.FormatOptions(no_row_numbering=True)
        print(tv.format_csv(csv_file, opts))
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()
