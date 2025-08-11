"""
Tidy Viewer Py - Beautiful terminal table formatting powered by Rust

This package provides fast, beautiful table formatting with features like:
- Automatic column width optimization
- Intelligent data type detection
- Color themes (nord, gruvbox, dracula, etc.)
- Support for CSV, Parquet, and pandas DataFrames
- Significant figures formatting for numbers
- NA/missing value handling
"""

from typing import List, Optional, Union, Any, Dict
import os
import sys

try:
    from ._core import (
        format_data as _format_data, 
        format_csv as _format_csv, 
        format_parquet as _format_parquet,
        format_arrow as _format_arrow,
        format_dict_of_lists as _format_dict_of_lists,
        format_list_of_dicts as _format_list_of_dicts,
        PyFormatOptions
    )
    RUST_AVAILABLE = True
except ImportError as e:
    RUST_AVAILABLE = False
    _import_error = e

__version__ = "0.2.93"
__all__ = [
    "print_table", "print_csv", "print_parquet", "print_arrow", "print_dataframe", 
    "format_table", "format_csv", "format_parquet", "format_arrow", "format_dataframe",
    "FormatOptions", "TV", "tv"
]


class FormatOptions:
    """
    Configuration options for table formatting.
    
    Args:
        max_rows: Maximum number of rows to display (None for all)
        max_col_width: Maximum width for columns (default: 20)
        min_col_width: Minimum width for columns (default: 2)
        use_color: Whether to use colored output (default: True)
        color_theme: Color theme to use ('nord', 'one_dark', 'gruvbox', 'dracula', 'solarized_light')
        delimiter: CSV delimiter (default: ',')
        significant_figures: Number of significant figures for floats (default: 3)
        preserve_scientific: Preserve scientific notation in input (default: False)
        max_decimal_width: Max width before switching to scientific notation (default: 13)
        no_dimensions: Don't show table dimensions (default: False)
        no_row_numbering: Don't show row numbers (default: False)
        extend_width_length: Extend beyond terminal width (default: False)
        force_all_rows: Force display of all rows (default: False)
        title: Optional table title
        footer: Optional table footer
    
    Examples:
        >>> # Basic usage
        >>> opts = FormatOptions(max_rows=10, color_theme="gruvbox")
        
        >>> # Disable colors for piping
        >>> opts = FormatOptions(use_color=False)
    """
    
    def __init__(
        self,
        max_rows: Optional[int] = None,
        max_col_width: int = 20,
        min_col_width: int = 2,
        use_color: bool = True,
        color_theme: str = "nord",
        delimiter: str = ",",
        significant_figures: int = 3,
        preserve_scientific: bool = False,
        max_decimal_width: int = 13,
        no_dimensions: bool = False,
        no_row_numbering: bool = False,  # Match Rust tv CLI terminal behavior (show row numbers by default)

        title: Optional[str] = None,
        footer: Optional[str] = None,
    ):
        if not RUST_AVAILABLE:
            raise ImportError(f"Rust extension not available: {_import_error}")
            
        self._options = PyFormatOptions(
            max_rows=max_rows,
            max_col_width=max_col_width,
            min_col_width=min_col_width,
            use_color=use_color,
            color_theme=color_theme,
            delimiter=delimiter,
            significant_figures=significant_figures,
            preserve_scientific=preserve_scientific,
            max_decimal_width=max_decimal_width,
            no_dimensions=no_dimensions,
            no_row_numbering=no_row_numbering,

            title=title,
            footer=footer,
        )
    
    def set_color_theme(self, theme: str) -> None:
        """
        Set the color theme.
        
        Args:
            theme: One of 'nord', 'one_dark', 'gruvbox', 'dracula', 'solarized_light'
        """
        self._options.set_color_theme(theme)


def format_table(
    data: Union[List[List[Any]], Dict[str, List[Any]], List[Dict[str, Any]]], 
    headers: Optional[List[str]] = None,
    options: Optional[FormatOptions] = None,
) -> str:
    """
    Format tabular data as a string.
    
    Args:
        data: List of lists, dict of lists, or list of dicts containing table data
        headers: Optional list of column headers (only used with list of lists)
        options: Formatting options
    
    Returns:
        Formatted table as a string
    
    Examples:
        >>> data = [["Alice", 25], ["Bob", 30]]
        >>> print(format_table(data, headers=["Name", "Age"]))
        
        >>> # Dict of lists
        >>> data = {"Name": ["Alice", "Bob"], "Age": [25, 30]}
        >>> print(format_table(data))
        
        >>> # List of dicts
        >>> data = [{"Name": "Alice", "Age": 25}, {"Name": "Bob", "Age": 30}]
        >>> print(format_table(data))
    """
    if not RUST_AVAILABLE:
        raise ImportError(f"Rust extension not available: {_import_error}")
    
    opts = options._options if options else None
    
    # Handle different input types
    if isinstance(data, dict):
        # Dict of lists - convert all values to strings
        str_data = {k: [str(v) for v in v_list] for k, v_list in data.items()}
        return _format_dict_of_lists(str_data, opts)
    elif data and isinstance(data[0], dict):
        # List of dicts - convert all values to strings
        str_data = [{k: str(v) for k, v in d.items()} for d in data]
        return _format_list_of_dicts(str_data, opts)
    else:
        # List of lists
        str_data = [[str(cell) for cell in row] for row in data]
        str_headers = [str(h) for h in headers] if headers else None
        return _format_data(str_data, str_headers, opts)


def format_csv(
    file_path: str,
    options: Optional[FormatOptions] = None,
) -> str:
    """
    Format a CSV file as a string.
    
    Args:
        file_path: Path to the CSV file
        options: Formatting options
    
    Returns:
        Formatted table as a string
    """
    if not RUST_AVAILABLE:
        raise ImportError(f"Rust extension not available: {_import_error}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    opts = options._options if options else None
    return _format_csv(file_path, opts)


def format_parquet(
    file_path: str,
    options: Optional[FormatOptions] = None,
) -> str:
    """
    Format a Parquet file as a string.
    
    Args:
        file_path: Path to the Parquet file
        options: Formatting options
    
    Returns:
        Formatted table as a string
    """
    if not RUST_AVAILABLE:
        raise ImportError(f"Rust extension not available: {_import_error}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    opts = options._options if options else None
    return _format_parquet(file_path, opts)


def format_arrow(
    file_path: str,
    options: Optional[FormatOptions] = None,
) -> str:
    """
    Format an Arrow file as a string.
    
    Args:
        file_path: Path to the Arrow file (.arrow, .feather, .ipc)
        options: Formatting options
    
    Returns:
        Formatted table as a string
    """
    if not RUST_AVAILABLE:
        raise ImportError(f"Rust extension not available: {_import_error}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    opts = options._options if options else None
    return _format_arrow(file_path, opts)


def format_dataframe(
    df,
    options: Optional[FormatOptions] = None,
) -> str:
    """
    Format a pandas DataFrame as a string.
    
    Args:
        df: pandas DataFrame
        options: Formatting options
    
    Returns:
        Formatted table as a string
    """
    if not RUST_AVAILABLE:
        raise ImportError(f"Rust extension not available: {_import_error}")
    
    # Check if it's a pandas DataFrame
    if not hasattr(df, 'columns') or not hasattr(df, 'values'):
        raise TypeError("Expected a pandas DataFrame")
    
    # Convert DataFrame to string format before passing to Rust
    headers = [str(col) for col in df.columns]
    data = [[str(cell) for cell in row] for row in df.values]
    
    opts = options._options if options else None
    return _format_data(data, headers, opts)


def format_numpy_array(
    arr,
    options: Optional[FormatOptions] = None,
) -> str:
    """
    Format a numpy array as a string.
    
    Args:
        arr: numpy array (2D only)
        options: Formatting options
    
    Returns:
        Formatted table as a string
    """
    if not RUST_AVAILABLE:
        raise ImportError(f"Rust extension not available: {_import_error}")
    
    # Check if it's a numpy array
    if not hasattr(arr, 'shape') or not hasattr(arr, 'tolist'):
        raise TypeError("Expected a numpy array")
    
    # Convert numpy array to string format before passing to Rust
    if len(arr.shape) != 2:
        raise ValueError("Only 2D numpy arrays are supported")
    
    data = [[str(cell) for cell in row] for row in arr.tolist()]
    headers = [f"col_{i}" for i in range(arr.shape[1])]
    
    opts = options._options if options else None
    return _format_data(data, headers, opts)


def format_polars_dataframe(
    df,
    options: Optional[FormatOptions] = None,
) -> str:
    """
    Format a polars DataFrame as a string.
    
    Args:
        df: polars DataFrame
        options: Formatting options
    
    Returns:
        Formatted table as a string
    """
    if not RUST_AVAILABLE:
        raise ImportError(f"Rust extension not available: {_import_error}")
    
    # Check if it's a polars DataFrame
    if not hasattr(df, 'columns') or not hasattr(df, 'to_numpy'):
        raise TypeError("Expected a polars DataFrame")
    
    # Convert polars DataFrame to string format before passing to Rust
    headers = [str(col) for col in df.columns]
    data = [[str(cell) for cell in row] for row in df.to_numpy().tolist()]
    
    opts = options._options if options else None
    return _format_data(data, headers, opts)


def print_table(
    data: Union[List[List[Any]], Dict[str, List[Any]], List[Dict[str, Any]]], 
    headers: Optional[List[str]] = None,
    options: Optional[FormatOptions] = None,
    file=None
) -> None:
    """
    Pretty print tabular data.
    
    Args:
        data: List of lists, dict of lists, or list of dicts containing table data
        headers: Optional list of column headers (only used with list of lists)
        options: Formatting options
        file: Output file (if None, prints to stdout)
    
    Examples:
        >>> data = [["Alice", 25, "Engineer"], ["Bob", 30, "Designer"]]
        >>> headers = ["Name", "Age", "Role"]
        >>> print_table(data, headers)
        
        >>> # Dict of lists
        >>> data = {"Name": ["Alice", "Bob"], "Age": [25, 30]}
        >>> print_table(data)
    """
    result = format_table(data, headers, options)
    print(result, file=file)


def print_csv(
    file_path: str,
    options: Optional[FormatOptions] = None,
    file=None
) -> None:
    """
    Pretty print a CSV file.
    
    Args:
        file_path: Path to the CSV file
        options: Formatting options
        file: Output file (if None, prints to stdout)
    """
    result = format_csv(file_path, options)
    print(result, file=file)


def print_parquet(
    file_path: str,
    options: Optional[FormatOptions] = None,
    file=None
) -> None:
    """
    Pretty print a Parquet file.
    
    Args:
        file_path: Path to the Parquet file
        options: Formatting options
        file: Output file (if None, prints to stdout)
    """
    result = format_parquet(file_path, options)
    print(result, file=file)


def print_arrow(
    file_path: str,
    options: Optional[FormatOptions] = None,
    file=None
) -> None:
    """
    Pretty print an Arrow file.
    
    Args:
        file_path: Path to the Arrow file (.arrow, .feather, .ipc)
        options: Formatting options
        file: Output file (if None, prints to stdout)
    """
    result = format_arrow(file_path, options)
    print(result, file=file)


def print_dataframe(
    df,
    options: Optional[FormatOptions] = None,
    file=None
) -> None:
    """
    Pretty print a pandas DataFrame.
    
    Args:
        df: pandas DataFrame
        options: Formatting options
        file: Output file (if None, prints to stdout)
    """
    result = format_dataframe(df, options)
    print(result, file=file)


def print_numpy_array(
    arr,
    options: Optional[FormatOptions] = None,
    file=None
) -> None:
    """
    Pretty print a numpy array.
    
    Args:
        arr: numpy array (2D only)
        options: Formatting options
        file: Output file (if None, prints to stdout)
    """
    result = format_numpy_array(arr, options)
    print(result, file=file)


def print_polars_dataframe(
    df,
    options: Optional[FormatOptions] = None,
    file=None
) -> None:
    """
    Pretty print a polars DataFrame.
    
    Args:
        df: polars DataFrame
        options: Formatting options
        file: Output file (if None, prints to stdout)
    """
    result = format_polars_dataframe(df, options)
    print(result, file=file)


class TV:
    """
    Tidy Viewer class for method chaining and configuration.
    
    Examples:
        >>> tv = TV().color_theme("dracula").max_rows(50)
        >>> tv.print_csv("data.csv")
        
        >>> # One-liner
        >>> TV().no_dimensions().print_table(data, headers)
    """
    
    def __init__(self):
        self._max_rows = None
        self._max_col_width = 20
        self._min_col_width = 2
        self._use_color = True
        self._color_theme = "nord"
        self._delimiter = ","
        self._significant_figures = 3
        self._preserve_scientific = False
        self._max_decimal_width = 13
        self._no_dimensions = False
        self._no_row_numbering = False

        self._title = None
        self._footer = None
    
    def _build_options(self) -> FormatOptions:
        """Build FormatOptions from current settings."""
        return FormatOptions(
            max_rows=self._max_rows,
            max_col_width=self._max_col_width,
            min_col_width=self._min_col_width,
            use_color=self._use_color,
            color_theme=self._color_theme,
            delimiter=self._delimiter,
            significant_figures=self._significant_figures,
            preserve_scientific=self._preserve_scientific,
            max_decimal_width=self._max_decimal_width,
            no_dimensions=self._no_dimensions,
            no_row_numbering=self._no_row_numbering,

            title=self._title,
            footer=self._footer,
        )
    
    def color_theme(self, theme: str) -> 'TV':
        """Set color theme and return self for chaining."""
        self._color_theme = theme
        return self
    
    def max_rows(self, rows: Optional[int]) -> 'TV':
        """Set max rows and return self for chaining."""
        self._max_rows = rows
        return self
    
    def max_col_width(self, width: int) -> 'TV':
        """Set max column width and return self for chaining."""
        self._max_col_width = width
        return self
    
    def no_color(self) -> 'TV':
        """Disable colors and return self for chaining."""
        self._use_color = False
        return self
    
    def no_dimensions(self) -> 'TV':
        """Hide dimensions and return self for chaining."""
        self._no_dimensions = True
        return self
    
    def no_row_numbers(self) -> 'TV':
        """Hide row numbers and return self for chaining."""
        self._no_row_numbering = True
        return self
    
    def title(self, title: str) -> 'TV':
        """Set title and return self for chaining."""
        self._title = title
        return self
    
    def footer(self, footer: str) -> 'TV':
        """Set footer and return self for chaining."""
        self._footer = footer
        return self
    
    def significant_figures(self, figures: int) -> 'TV':
        """Set significant figures and return self for chaining."""
        self._significant_figures = figures
        return self
    
    def print_table(self, data: Union[List[List[Any]], Dict[str, List[Any]], List[Dict[str, Any]]], headers: Optional[List[str]] = None, file=None):
        """Print table with current options."""
        print_table(data, headers, self._build_options(), file)
    
    def print_csv(self, file_path: str, file=None):
        """Print CSV with current options."""
        print_csv(file_path, self._build_options(), file)
    
    def print_parquet(self, file_path: str, file=None):
        """Print Parquet with current options."""
        print_parquet(file_path, self._build_options(), file)
    
    def print_arrow(self, file_path: str, file=None):
        """Print Arrow with current options."""
        print_arrow(file_path, self._build_options(), file)
    
    def print_dataframe(self, df, file=None):
        """Print DataFrame with current options."""
        print_dataframe(df, self._build_options(), file)
    
    def print_numpy_array(self, arr, file=None):
        """Print numpy array with current options."""
        print_numpy_array(arr, self._build_options(), file)
    
    def print_polars_dataframe(self, df, file=None):
        """Print polars DataFrame with current options."""
        print_polars_dataframe(df, self._build_options(), file)
    
    def format_table(self, data: Union[List[List[Any]], Dict[str, List[Any]], List[Dict[str, Any]]], headers: Optional[List[str]] = None) -> str:
        """Format table with current options."""
        return format_table(data, headers, self._build_options())
    
    def format_csv(self, file_path: str) -> str:
        """Format CSV with current options."""
        return format_csv(file_path, self._build_options())
    
    def format_parquet(self, file_path: str) -> str:
        """Format Parquet with current options."""
        return format_parquet(file_path, self._build_options())
    
    def format_arrow(self, file_path: str) -> str:
        """Format Arrow with current options."""
        return format_arrow(file_path, self._build_options())
    
    def format_dataframe(self, df) -> str:
        """Format DataFrame with current options."""
        return format_dataframe(df, self._build_options())
    
    def format_numpy_array(self, arr) -> str:
        """Format numpy array with current options."""
        return format_numpy_array(arr, self._build_options())
    
    def format_polars_dataframe(self, df) -> str:
        """Format polars DataFrame with current options."""
        return format_polars_dataframe(df, self._build_options())


# Convenience function for quick access
def tv() -> TV:
    """Create a new TV instance for method chaining."""
    return TV()


