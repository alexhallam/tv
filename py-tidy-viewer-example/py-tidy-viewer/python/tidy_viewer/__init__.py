"""
Tidy Viewer - A beautiful data pretty printer for Python

This package provides fast, beautiful table formatting powered by Rust.
"""

from typing import List, Optional, Union, Any
import os
import sys

try:
    from ._core import format_data, format_csv, format_parquet, format_dataframe, PyFormatOptions
    RUST_AVAILABLE = True
except ImportError as e:
    RUST_AVAILABLE = False
    _import_error = e

__version__ = "0.1.0"
__all__ = [
    "print_table", "print_csv", "print_parquet", "print_dataframe", 
    "FormatOptions", "TV"
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
        no_row_numbering: bool = False,
        extend_width_length: bool = False,
        force_all_rows: bool = False,
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
            extend_width_length=extend_width_length,
            force_all_rows=force_all_rows,
            title=title,
            footer=footer,
        )
    
    def set_color_theme(self, theme: str) -> None:
        """Set the color theme."""
        self._options.set_color_theme(theme)


def print_table(
    data: List[List[Any]], 
    headers: Optional[List[str]] = None,
    options: Optional[FormatOptions] = None,
    file=None
) -> Optional[str]:
    """
    Pretty print tabular data.
    
    Args:
        data: List of lists containing table data
        headers: Optional list of column headers
        options: Formatting options
        file: Output file (if None, prints to stdout)
    
    Returns:
        Formatted string if file is None, otherwise None
    """
    if not RUST_AVAILABLE:
        raise ImportError(f"Rust extension not available: {_import_error}")
    
    # Convert data to strings
    str_data = [[str(cell) for cell in row] for row in data]
    str_headers = [str(h) for h in headers] if headers else None
    
    # Format the table
    opts = options._options if options else None
    result = format_data(str_data, str_headers, opts)
    
    if file is None:
        print(result)
        return result
    else:
        print(result, file=file)
        return None


def print_csv(
    file_path: str,
    options: Optional[FormatOptions] = None,
    file=None
) -> Optional[str]:
    """
    Pretty print a CSV file.
    
    Args:
        file_path: Path to the CSV file
        options: Formatting options
        file: Output file (if None, prints to stdout)
    
    Returns:
        Formatted string if file is None, otherwise None
    """
    if not RUST_AVAILABLE:
        raise ImportError(f"Rust extension not available: {_import_error}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    opts = options._options if options else None
    result = format_csv(file_path, opts)
    
    if file is None:
        print(result)
        return result
    else:
        print(result, file=file)
        return None


def print_parquet(
    file_path: str,
    options: Optional[FormatOptions] = None,
    file=None
) -> Optional[str]:
    """
    Pretty print a Parquet file.
    
    Args:
        file_path: Path to the Parquet file
        options: Formatting options
        file: Output file (if None, prints to stdout)
    
    Returns:
        Formatted string if file is None, otherwise None
    """
    if not RUST_AVAILABLE:
        raise ImportError(f"Rust extension not available: {_import_error}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    opts = options._options if options else None
    result = format_parquet(file_path, opts)
    
    if file is None:
        print(result)
        return result
    else:
        print(result, file=file)
        return None


def print_dataframe(
    df,
    options: Optional[FormatOptions] = None,
    file=None
) -> Optional[str]:
    """
    Pretty print a pandas DataFrame.
    
    Args:
        df: pandas DataFrame
        options: Formatting options
        file: Output file (if None, prints to stdout)
    
    Returns:
        Formatted string if file is None, otherwise None
    """
    if not RUST_AVAILABLE:
        raise ImportError(f"Rust extension not available: {_import_error}")
    
    # Check if it's a pandas DataFrame
    if not hasattr(df, 'columns') or not hasattr(df, 'values'):
        raise TypeError("Expected a pandas DataFrame")
    
    opts = options._options if options else None
    result = format_dataframe(df, opts)
    
    if file is None:
        print(result)
        return result
    else:
        print(result, file=file)
        return None


class TV:
    """
    Tidy Viewer class for method chaining and configuration.
    
    Example:
        tv = TV().color_theme("dracula").max_rows(50)
        tv.print_csv("data.csv")
    """
    
    def __init__(self):
        self.options = FormatOptions()
    
    def color_theme(self, theme: str) -> 'TV':
        """Set color theme and return self for chaining."""
        self.options.set_color_theme(theme)
        return self
    
    def max_rows(self, rows: Optional[int]) -> 'TV':
        """Set max rows and return self for chaining."""
        # Note: For full implementation, we'd need to rebuild the options
        # This is a simplified version
        return self
    
    def print_table(self, data: List[List[Any]], headers: Optional[List[str]] = None, file=None):
        """Print table with current options."""
        return print_table(data, headers, self.options, file)
    
    def print_csv(self, file_path: str, file=None):
        """Print CSV with current options."""
        return print_csv(file_path, self.options, file)
    
    def print_parquet(self, file_path: str, file=None):
        """Print Parquet with current options."""
        return print_parquet(file_path, self.options, file)
    
    def print_dataframe(self, df, file=None):
        """Print DataFrame with current options."""
        return print_dataframe(df, self.options, file)


# Convenience function for quick access
def tv():
    """Create a new TV instance for method chaining."""
    return TV()