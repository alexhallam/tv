# Tidy Viewer Py

Beautiful terminal table formatting powered by Rust. A Python package that provides fast, feature-rich table pretty-printing with automatic column width optimization, data type detection, and gorgeous color themes.

## Features

- 🚀 **Blazing fast** - Rust-powered performance
- 🎨 **Beautiful themes** - Nord, Gruvbox, Dracula, One Dark, and more
- 📊 **Smart formatting** - Automatic column width optimization
- 🔢 **Type detection** - Intelligent handling of numbers, dates, and missing values
- 📁 **Multiple formats** - CSV, Parquet, and pandas DataFrames
- 🌈 **Colored output** - Customizable color themes
- 📏 **Configurable** - Fine-tune every aspect of the output

## Installation

```bash
pip install tidy-viewer-py
```

## Quick Start


```python
import tidy_viewer_py as tv

# Print a CSV file
tv.print_csv("data.csv")

# With custom options
options = tv.FormatOptions(
    max_rows=50,
    color_theme="gruvbox",
    significant_figures=4
)
tv.print_csv("data.csv", options)
```

### Pandas DataFrames

```python
import pandas as pd
import tidy_viewer_py as tv

df = pd.read_csv("large_dataset.csv")

# Pretty print with automatic truncation
tv.print_dataframe(df)

# Or with custom settings
tv.print_dataframe(df, tv.FormatOptions(max_rows=100))
```

### Method Chaining API

```python
import tidy_viewer_py as tv

# Fluent interface for quick formatting
tv.tv().color_theme("dracula").max_rows(50).print_csv("data.csv")

# One-liner with multiple options
tv.tv().no_dimensions().no_row_numbers().title("Sales Report").print_table(data, headers)
```

### Format to String

```python
# Get formatted output as string instead of printing
output = tv.format_table(data, headers)
print(f"Formatted output:\n{output}")

# Save to file
with open("report.txt", "w") as f:
    f.write(tv.format_csv("data.csv", tv.FormatOptions(use_color=False)))
```

## Configuration Options

```python
options = tv.FormatOptions(
    # Display options
    max_rows=25,              # Maximum rows to display (None for all)
    max_col_width=20,         # Maximum column width
    min_col_width=2,          # Minimum column width
    
    # Styling
    use_color=True,           # Enable/disable colored output
    color_theme="nord",       # Color theme
    
    # Data formatting
    delimiter=",",            # CSV delimiter
    significant_figures=3,    # Number of significant figures
    preserve_scientific=False,# Preserve scientific notation
    max_decimal_width=13,     # Max width before scientific notation
    
    # Table elements
    no_dimensions=False,      # Hide table dimensions
    no_row_numbering=False,   # Hide row numbers
    title="My Table",         # Table title
    footer="End of data",     # Table footer
)
```

## Color Themes

Available themes:
- `nord` (default) - Arctic, north-bluish color palette
- `gruvbox` - Retro groove color scheme
- `dracula` - Dark theme with vibrant colors
- `one_dark` - Atom One Dark inspired
- `solarized_light` - Precision colors for readability

## Performance

Tidy Viewer Py leverages Rust for exceptional performance:

- 10-100x faster than pure Python implementations
- Handles large datasets efficiently
- Minimal memory overhead
- Streaming support for huge files (coming soon)

## Development

### Building from Source

Requirements:
- Python 3.8+
- Rust 1.70+
- maturin

```bash
git clone https://github.com/yourusername/tidy-viewer-py
cd tidy-viewer-py
maturin develop
```

### Running Tests

```bash
pytest tests/
```

## License

Licensed under either of:
- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE))
- MIT license ([LICENSE-MIT](LICENSE-MIT))

at your option.

## Credits

Inspired by the original [tidy-viewer](https://github.com/alexhallam/tv) project.

