#!/usr/bin/env python3
"""
Test Output Parity between Rust tv CLI and Python Port

This script compares the output of the original Rust tv CLI with the Python port
to ensure they produce identical formatting for the same CSV files.
"""

import subprocess
import sys
import os
import difflib
import tempfile
import shutil
from pathlib import Path

def run_rust_tv(csv_file):
    """Run the original Rust tv CLI on a CSV file and capture output."""
    try:
        # Convert relative path to absolute path for Rust tv
        csv_path = os.path.abspath(csv_file)
        
        # Run the Rust tv command with terminal-like environment to show row numbers
        env = os.environ.copy()
        env['TERM'] = 'xterm-256color'  # Simulate terminal environment
        
        result = subprocess.run(
            ['tidy-viewer', csv_path],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        
        if result.returncode != 0:
            print(f"❌ Rust tv failed for {csv_file}: {result.stderr}")
            return None
            
        return result.stdout.strip()
        
    except subprocess.TimeoutExpired:
        print(f"⏰ Rust tv timed out for {csv_file}")
        return None
    except FileNotFoundError:
        print(f"❌ Rust tv executable not found. Make sure you're in the correct directory.")
        return None
    except Exception as e:
        print(f"❌ Error running Rust tv for {csv_file}: {e}")
        return None

def run_python_tv(csv_file):
    """Run the Python tv port on a CSV file and capture output."""
    try:
        # Import the Python package
        import tidy_viewer_py as tv
        
        # Format the CSV file with default behavior (shows row numbers)
        result = tv.format_csv(csv_file)
        return result.strip()
        
    except ImportError as e:
        print(f"❌ Failed to import tidy_viewer_py: {e}")
        return None
    except Exception as e:
        print(f"❌ Error running Python tv for {csv_file}: {e}")
        return None

def normalize_output(output):
    """Normalize output by removing ANSI color codes and normalizing whitespace."""
    import re
    
    if not output:
        return ""
    
    # Remove ANSI color codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    output = ansi_escape.sub('', output)
    
    # Normalize line endings
    output = output.replace('\r\n', '\n').replace('\r', '\n')
    
    # Normalize whitespace (but preserve structure)
    lines = output.split('\n')
    normalized_lines = []
    
    for line in lines:
        # Preserve leading/trailing spaces but normalize internal whitespace
        normalized_line = ' '.join(line.split())
        normalized_lines.append(normalized_line)
    
    return '\n'.join(normalized_lines)

def compare_outputs(rust_output, python_output, csv_file):
    """Compare Rust and Python outputs and return detailed differences."""
    rust_normalized = normalize_output(rust_output)
    python_normalized = normalize_output(python_output)
    
    if rust_normalized == python_normalized:
        return True, None
    
    # Create detailed diff
    diff = list(difflib.unified_diff(
        rust_normalized.splitlines(keepends=True),
        python_normalized.splitlines(keepends=True),
        fromfile=f'Rust tv ({csv_file})',
        tofile=f'Python tv ({csv_file})',
        lineterm=''
    ))
    
    return False, ''.join(diff)

def test_csv_files():
    """Test all CSV files in the data directory."""
    data_dir = Path("../data")
    
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    csv_files = list(data_dir.glob("*.csv"))
    
    if not csv_files:
        print("❌ No CSV files found in data directory")
        return
    
    print(f"🔍 Testing {len(csv_files)} CSV files for output parity...")
    print("=" * 80)
    
    passed = 0
    failed = 0
    total = len(csv_files)
    
    for csv_file in csv_files:
        print(f"\n📄 Testing: {csv_file.name}")
        print("-" * 40)
        
        # Run both versions
        rust_output = run_rust_tv(str(csv_file))
        python_output = run_python_tv(str(csv_file))
        
        if rust_output is None or python_output is None:
            print(f"❌ Failed to get output for {csv_file.name}")
            failed += 1
            continue
        
        # Compare outputs
        is_identical, diff = compare_outputs(rust_output, python_output, csv_file.name)
        
        if is_identical:
            print(f"✅ PASS: {csv_file.name} - Outputs are identical")
            passed += 1
        else:
            print(f"❌ FAIL: {csv_file.name} - Outputs differ")
            print("\n📊 Differences:")
            print(diff)
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"📊 Test Results: {passed}/{total} passed, {failed}/{total} failed")
    
    if failed > 0:
        print("\n🔧 Next steps:")
        print("1. Analyze the differences above")
        print("2. Fix formatting issues in the Python port")
        print("3. Re-run tests until all outputs match")
        return False
    else:
        print("\n🎉 All tests passed! Outputs are identical.")
        return True

def test_specific_formatting():
    """Test specific formatting aspects that are known to be problematic."""
    print("\n🔍 Testing specific formatting aspects...")
    print("=" * 80)
    
    # Test with a simple CSV that we can control
    test_csv = "test_parity.csv"
    test_data = [
        "name,age,salary",
        "Alice,25,75000.50",
        "Bob,30,85000.75",
        "Charlie,35,95000.25"
    ]
    
    # Create test CSV
    with open(test_csv, 'w') as f:
        f.write('\n'.join(test_data))
    
    try:
        rust_output = run_rust_tv(test_csv)
        python_output = run_python_tv(test_csv)
        
        if rust_output and python_output:
            print("📄 Test CSV content:")
            print('\n'.join(test_data))
            
            print("\n📊 Rust tv output:")
            print(rust_output)
            
            print("\n📊 Python tv output:")
            print(python_output)
            
            is_identical, diff = compare_outputs(rust_output, python_output, test_csv)
            
            if is_identical:
                print("\n✅ PASS: Specific formatting test")
            else:
                print("\n❌ FAIL: Specific formatting test")
                print("\n📊 Differences:")
                print(diff)
        
    finally:
        # Clean up
        if os.path.exists(test_csv):
            os.remove(test_csv)

def main():
    """Run all parity tests."""
    print("🚀 Testing Output Parity between Rust tv CLI and Python Port")
    print("=" * 80)
    
    # Check if we're in the right directory
    if not os.path.exists("../Cargo.toml"):
        print("❌ Cargo.toml not found. Make sure you're in the tidy-viewer-py directory.")
        return False
    
    # Test all CSV files
    all_passed = test_csv_files()
    
    # Test specific formatting
    test_specific_formatting()
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
