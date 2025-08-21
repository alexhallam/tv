# Tidy Viewer Py

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

## Data Type Display

Tidy Viewer Py can display data types from various dataframe libraries in an abbreviated format. Data types appear as a row below the headers with slightly dimmed styling.

### Automatic Data Type Detection

```python
import pandas as pd
import tidy_viewer_py as tv

# Pandas DataFrame with automatic data type display
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'salary': [50000.0, 60000.0, 70000.0],
    'active': [True, False, True]
})

# Data types are automatically detected and displayed
tv.print_dataframe(df)
```

### Manual Data Type Specification

```python
import tidy_viewer_py as tv

data = [['Alice', '25', 'Engineer'], ['Bob', '30', 'Designer']]
headers = ['Name', 'Age', 'Role']
data_types = ['<str>', '<i64>', '<str>']

# Specify data types manually
tv.print_table(data, headers, data_types)
```

### Data Type Mapping

The library automatically maps data types from different dataframe libraries to abbreviated format:

#### Pandas Data Types
| Pandas Type | Abbreviated |
|-------------|-------------|
| `object` | `<str>` |
| `int64` | `<i64>` |
| `float64` | `<f64>` |
| `bool` | `<bool>` |
| `datetime64[ns]` | `<dt>` |
| `category` | `<cat>` |
| `complex128` | `<cplx>` |

#### Polars Data Types
Based on the [official Polars documentation](https://docs.pola.rs/api/python/stable/reference/datatypes.html):

| Polars Type | Abbreviated | Description |
|-------------|-------------|-------------|
| `String`, `Utf8` | `<str>` | UTF-8 encoded string type |
| `Int8`, `Int16`, `Int32`, `Int64`, `Int128` | `<i8>`, `<i16>`, `<i32>`, `<i64>`, `<i128>` | Signed integer types |
| `UInt8`, `UInt16`, `UInt32`, `UInt64` | `<u8>`, `<u16>`, `<u32>`, `<u64>` | Unsigned integer types |
| `Float32`, `Float64` | `<f32>`, `<f64>` | Floating point types |
| `Boolean`, `Bool` | `<bool>` | Boolean type |
| `Date` | `<date>` | Calendar date |
| `Datetime<ns>`, `Datetime<us>`, `Datetime<ms>` | `<dt>` | Date and time with timezone support |
| `Time` | `<time>` | Time of day |
| `Duration<ns>`, `Duration<us>`, `Duration<ms>` | `<td>` | Time duration |
| `Categorical`, `Enum` | `<cat>`, `<enum>` | String encoding types |
| `List<Type>` | `<list<type>>` | Variable length list |
| `Array<Type, size>` | `<arr<type,size>>` | Fixed length array |
| `Struct<field1: Type1, field2: Type2>` | `<struct>` | Struct composite type |
| `Decimal(precision, scale)` | `<dec>` | Decimal with precision |
| `Binary` | `<bin>` | Binary data |
| `Object` | `<obj>` | Arbitrary Python objects |
| `Null`, `Unknown` | `<null>`, `<unk>` | Null and unknown types |

#### Arrow Data Types
| Arrow Type | Abbreviated |
|------------|-------------|
| `Utf8` | `<str>` |
| `Int64` | `<i64>` |
| `Float64` | `<f64>` |
| `Boolean` | `<bool>` |
| `Timestamp` | `<dt>` |
| `List` | `<list>` |
| `Struct` | `<struct>` |

### Complex Type Handling

Complex data types are automatically simplified:

```python
# Polars complex types:
# List<Int64> → <list<i64>>
# Array<Float64, 3> → <arr<f64,3>>
# Struct<name: String, age: Int32> → <struct>
# Datetime<ns, UTC> → <dt>
# Duration<us> → <td>
# Decimal(10, 2) → <dec>
# Int64? → <i64> (nullable types)

# Pandas/Arrow complex types:
# Map<String, Int64> → <map>
# Union<Int64, String> → <union>
# Dictionary<Int8, String> → <dict>
```

### Data Type Utilities

```python
from tidy_viewer_py import map_dtype, map_dtypes, auto_map_dtypes

# Map individual data types
map_dtype('int64', 'pandas')  # Returns '<i64>'
map_dtype('String', 'polars')  # Returns '<str>'

# Map lists of data types
dtypes = ['object', 'int64', 'float64']
mapped = map_dtypes(dtypes, 'pandas')  # Returns ['<str>', '<i64>', '<f64>']

# Auto-detect library and map
auto_mapped = auto_map_dtypes(dtypes)  # Automatically detects pandas
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
