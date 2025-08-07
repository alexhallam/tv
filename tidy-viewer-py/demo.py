#!/usr/bin/env python3
"""Demo script for tidy-viewer-py."""

import sys

try:
    import tidy_viewer_py as tv
except ImportError:
    print("Error: tidy-viewer-py not installed. Run 'maturin develop' first.")
    sys.exit(1)


def main():
    print("🌟 Tidy Viewer Py Demo 🌟\n")
    
    # Basic table
    print("1. Basic Table:")
    print("-" * 50)
    data = [
        ["Alice Johnson", 28, "Engineer", 75000.50],
        ["Bob Smith", 35, "Manager", 85000.00],
        ["Charlie Brown", 23, "Intern", 45000.00],
        ["Diana Prince", 42, "Director", 120000.00],
    ]
    headers = ["Name", "Age", "Role", "Salary"]
    tv.print_table(data, headers)
    
    # With options
    print("\n2. With Custom Options (Gruvbox theme, max 3 rows):")
    print("-" * 50)
    options = tv.FormatOptions(
        max_rows=3,
        color_theme="gruvbox",
        title="Employee Data",
        footer="Showing top 3 employees"
    )
    tv.print_table(data, headers, options)
    
    # Method chaining
    print("\n3. Method Chaining API:")
    print("-" * 50)
    tv.tv().color_theme("dracula").no_row_numbers().print_table(data, headers)
    
    # Different data types
    print("\n4. Mixed Data Types:")
    print("-" * 50)
    mixed_data = [
        ["Product A", 123.456789, True, "2024-01-15", "NA"],
        ["Product B", 0.0001234, False, "2024-02-20", "Active"],
        ["Product C", 9876543210, True, "NA", "Pending"],
        ["Product D", -42.5, "NA", "2024-03-10", ""],
    ]
    mixed_headers = ["Product", "Value", "Available", "Date", "Status"]
    
    tv.tv().color_theme("one_dark").significant_figures(4).print_table(mixed_data, mixed_headers)
    
    # No color (for piping)
    print("\n5. No Color Output (for piping/redirecting):")
    print("-" * 50)
    output = tv.tv().no_color().format_table(data[:2], headers)
    print(output)
    
    # Large numbers
    print("\n6. Large Numbers with Scientific Notation:")
    print("-" * 50)
    large_data = [
        ["Tiny", 0.000000123],
        ["Small", 0.123],
        ["Medium", 123456.789],
        ["Large", 123456789012345],
        ["Huge", 9.876543210e15],
    ]
    tv.print_table(large_data, ["Size", "Value"])
    
    print("\n✨ Demo complete! ✨")


if __name__ == "__main__":
    main()