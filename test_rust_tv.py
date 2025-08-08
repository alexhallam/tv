#!/usr/bin/env python3
"""
Test script for Rust tv CLI
"""

import subprocess
import sys
import os

def run_tv_command(csv_file, *args):
    """Run tv command with arguments"""
    cmd = ['tv', csv_file] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Exception: {e}"

def main():
    csv_file = "../data/iris.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return
    
    print("🚀 Testing Rust tv CLI")
    print("=" * 50)
    
    # Test 1: Basic viewing
    print("\n1️⃣ Basic CSV viewing:")
    print(run_tv_command(csv_file))
    
    # Test 2: Limited rows
    print("\n2️⃣ Limited rows (5):")
    print(run_tv_command(csv_file, "-n", "5"))
    
    # Test 3: Different color theme
    print("\n3️⃣ Gruvbox theme:")
    print(run_tv_command(csv_file, "-c", "3"))
    
    # Test 4: No row numbers
    print("\n4️⃣ No row numbers:")
    print(run_tv_command(csv_file, "-R"))
    
    # Test 5: No dimensions
    print("\n5️⃣ No dimensions:")
    print(run_tv_command(csv_file, "-D"))
    
    # Test 6: Custom significant figures
    print("\n6️⃣ 5 significant figures:")
    print(run_tv_command(csv_file, "-g", "5"))

if __name__ == "__main__":
    main()
