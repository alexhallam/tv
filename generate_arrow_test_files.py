#!/usr/bin/env python3
"""
Generate Arrow IPC test files for tidy-viewer testing.
These files will be used to test Arrow IPC support.
"""

import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
import os
from pathlib import Path

def generate_arrow_file(filename, rows, cols=10):
    """Generate an Arrow IPC file with specified dimensions."""
    print(f"Generating {filename} with {rows:,} rows x {cols} columns...")
    
    # Create realistic test data
    data = {
        'id': range(1, rows + 1),
        'name': [f'Person_{i}' for i in range(1, rows + 1)],
        'age': np.random.randint(18, 80, rows),
        'salary': np.random.normal(50000, 15000, rows).round(2),
        'score': np.random.uniform(0, 100, rows).round(3),
        'is_active': np.random.choice([True, False], rows),
        'department': np.random.choice(['Engineering', 'Sales', 'Marketing', 'HR'], rows),
        'join_date': pd.date_range('2010-01-01', periods=rows, freq='1D')[:rows],
        'notes': [f'Note for person {i} with some longer text content' for i in range(1, rows + 1)],
        'value': np.random.exponential(2, rows)
    }
    
    df = pd.DataFrame(data)
    
    # Convert to Arrow table and save
    table = pa.Table.from_pandas(df)
    feather.write_feather(table, filename, compression=None)
    
    # Print file size
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    print(f"  Created {filename}: {size_mb:.1f} MB")
    return size_mb

def main():
    """Generate Arrow IPC test files of various sizes."""
    
    # Create test directory
    test_dir = Path("data")
    test_dir.mkdir(exist_ok=True)
    
    print("Generating Arrow IPC test files...")
    print("=" * 50)
    
    # Test file configurations: (name_suffix, rows, description)
    test_configs = [
        ("small", 100, "Small Arrow file - should not trigger streaming"),
        ("medium", 1000, "Medium Arrow file - right at threshold"),
        ("large", 5000, "Large Arrow file - should trigger streaming"),
    ]
    
    total_size = 0
    
    for suffix, rows, description in test_configs:
        print(f"\n{description}")
        print("-" * len(description))
        
        # Generate Arrow IPC files with different extensions
        extensions = ['feather', 'arrow', 'ipc']
        for ext in extensions:
            arrow_file = test_dir / f"test_{suffix}.{ext}"
            arrow_size = generate_arrow_file(arrow_file, rows)
            total_size += arrow_size
    
    print(f"\n" + "=" * 50)
    print(f"Total size generated: {total_size:.1f} MB")
    print(f"Files created in: {test_dir.absolute()}")
    print("\nTest files created:")
    for suffix, _, _ in test_configs:
        for ext in ['feather', 'arrow', 'ipc']:
            print(f"  - data/test_{suffix}.{ext}")

if __name__ == "__main__":
    main()
