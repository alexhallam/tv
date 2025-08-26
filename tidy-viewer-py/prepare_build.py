#!/usr/bin/env python3
"""
Prepare the package for building by copying tidy-viewer-core into the package directory.
This ensures that the relative path dependency works when building from PyPI.
"""

import shutil
import os
import sys
from pathlib import Path

def prepare_build():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Paths
    source_core_dir = script_dir.parent / "tidy-viewer-core"
    target_core_dir = script_dir / "tidy-viewer-core"
    
    # Check if source exists
    if not source_core_dir.exists():
        print(f"Error: tidy-viewer-core not found at {source_core_dir}")
        sys.exit(1)
    
    # Remove existing directory if it exists
    if target_core_dir.exists():
        print(f"Removing existing {target_core_dir}")
        shutil.rmtree(target_core_dir)
    
    # Copy the directory
    print(f"Copying {source_core_dir} to {target_core_dir}")
    shutil.copytree(source_core_dir, target_core_dir)
    
    # Update the Cargo.toml files to remove workspace dependencies
    # First, fix tidy-viewer-core/Cargo.toml
    cargo_toml_path = target_core_dir / "Cargo.toml"
    if cargo_toml_path.exists():
        print(f"Updating {cargo_toml_path} to remove workspace dependencies")
        
        # Read the file
        with open(cargo_toml_path, 'r') as f:
            content = f.read()
        
        # Replace workspace dependencies with concrete versions
        # These versions match the workspace Cargo.toml
        replacements = {
            'lazy_static = { workspace = true }': 'lazy_static = "1.4.0"',
            'regex = { workspace = true }': 'regex = "1.5.4"',
            'unicode-truncate = { workspace = true }': 'unicode-truncate = "0.2.0"',
            'unicode-width = { workspace = true }': 'unicode-width = "0.1.11"',
            'itertools = { workspace = true }': 'itertools = "0.10.0"',
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Write back
        with open(cargo_toml_path, 'w') as f:
            f.write(content)
    
    # Also fix the main tidy-viewer-py/Cargo.toml
    main_cargo_toml = script_dir / "Cargo.toml"
    if main_cargo_toml.exists():
        print(f"Updating {main_cargo_toml} to remove workspace dependencies")
        
        with open(main_cargo_toml, 'r') as f:
            content = f.read()
        
        # Replace workspace dependencies
        workspace_deps = {
            'csv = { workspace = true }': 'csv = "1.1.6"',
            'serde = { workspace = true }': 'serde = { version = "1.0", features = ["derive"] }',
            'serde_json = { workspace = true }': 'serde_json = "1.0"',
            'arrow = { workspace = true }': 'arrow = "56.0"',
            'parquet = { workspace = true }': 'parquet = "56.0"',
            'owo-colors = { workspace = true }': 'owo-colors = "3.0.1"',
            'unicode-width = { workspace = true }': 'unicode-width = "0.1.11"',
            'unicode-truncate = { workspace = true }': 'unicode-truncate = "0.2.0"',
            'lazy_static = { workspace = true }': 'lazy_static = "1.4.0"',
            'regex = { workspace = true }': 'regex = "1.5.4"',
            'crossterm = { workspace = true }': 'crossterm = "0.22.1"',
        }
        
        for old, new in workspace_deps.items():
            content = content.replace(old, new)
        
        with open(main_cargo_toml, 'w') as f:
            f.write(content)
    
    print("Build preparation complete!")

if __name__ == "__main__":
    prepare_build()