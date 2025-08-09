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

### CSV File Pretty Printing

```python
import tidy_viewer_py as tv
import pandas as pd
url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
pd.read_csv(url).to_csv("iris.csv", index=False)  # Save to csv for demo
filename = "iris.csv"
tv.print_csv(filename)
```

### Pandas DataFrames Pretty Printing

```python
import pandas as pd
import tidy_viewer_py as tv
df = pd.read_csv(filename)
tv.print_dataframe(df)
```

### Polars DataFrames Pretty Printing

```python

import polars as pl

df_pl = pl.read_csv(filename)
tv.print_polars_dataframe(df_pl)
```

### Method Chaining API

```python
import tidy_viewer_py as tv

tv.tv().color_theme("gruvbox").max_rows(10).print_dataframe(df)
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


### Building from Source

Requirements:
- Python 3.8+
- Rust 1.70+
- uv (recommended) or pip

```bash
git clone https://github.com/yourusername/tidy-viewer-py
cd tidy-viewer-py
uv pip install .
```