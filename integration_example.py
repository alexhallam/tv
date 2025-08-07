# Example: How to integrate tidy-viewer into your existing Python package

# Option 1: Add as a dependency in your package

# your_package/pyproject.toml
"""
[project]
name = "your-package"
dependencies = [
    "py-tidy-viewer>=0.1.0",
    # ... your other dependencies
]
"""

# your_package/data_utils.py
"""
Your existing package with enhanced pretty printing capabilities
"""

import pandas as pd
from typing import List, Any, Optional
try:
    import tidy_viewer
    TIDY_VIEWER_AVAILABLE = True
except ImportError:
    TIDY_VIEWER_AVAILABLE = False
    # Fallback to another solution like Rich or basic printing


class DataProcessor:
    """Your existing data processing class"""
    
    def __init__(self):
        self.data = []
        
    def load_csv(self, file_path: str):
        """Load CSV data"""
        self.data = pd.read_csv(file_path)
        return self
        
    def filter_data(self, condition):
        """Your existing data filtering logic"""
        self.data = self.data[condition]
        return self
        
    def pretty_print(self, use_color: bool = True, max_rows: int = 25):
        """Enhanced pretty printing with tidy-viewer"""
        if TIDY_VIEWER_AVAILABLE:
            # Use tidy-viewer for beautiful output
            options = tidy_viewer.FormatOptions(
                max_rows=max_rows,
                use_color=use_color,
                color_theme="nord"
            )
            tidy_viewer.print_dataframe(self.data, options)
        else:
            # Fallback to basic pandas display
            print(self.data.to_string())
            
    def to_beautiful_string(self, theme: str = "nord") -> str:
        """Return formatted string for logging or saving"""
        if TIDY_VIEWER_AVAILABLE:
            options = tidy_viewer.FormatOptions(color_theme=theme, use_color=False)
            return tidy_viewer.print_dataframe(self.data, options, file=None)
        else:
            return self.data.to_string()


# Option 2: Conditional enhancement of existing functions

def enhanced_print_table(data: List[List[Any]], headers: Optional[List[str]] = None):
    """Enhanced table printing function"""
    if TIDY_VIEWER_AVAILABLE:
        tidy_viewer.print_table(data, headers)
    else:
        # Fallback implementation
        if headers:
            print("\t".join(headers))
            print("-" * (len(headers) * 8))
        for row in data:
            print("\t".join(str(cell) for cell in row))


# Option 3: Factory pattern for different output formats

class TableFormatter:
    """Factory for creating table formatters"""
    
    @classmethod
    def create(cls, format_type: str = "auto"):
        if format_type == "auto":
            return TidyViewerFormatter() if TIDY_VIEWER_AVAILABLE else BasicFormatter()
        elif format_type == "tidy":
            if not TIDY_VIEWER_AVAILABLE:
                raise ImportError("tidy-viewer not available")
            return TidyViewerFormatter()
        else:
            return BasicFormatter()


class TidyViewerFormatter:
    """Tidy-viewer based formatter"""
    
    def __init__(self, theme: str = "nord"):
        self.options = tidy_viewer.FormatOptions(color_theme=theme)
        
    def format_dataframe(self, df: pd.DataFrame) -> str:
        return tidy_viewer.print_dataframe(df, self.options, file=None)
        
    def format_csv(self, file_path: str) -> str:
        return tidy_viewer.print_csv(file_path, self.options, file=None)


class BasicFormatter:
    """Basic fallback formatter"""
    
    def format_dataframe(self, df: pd.DataFrame) -> str:
        return df.to_string()
        
    def format_csv(self, file_path: str) -> str:
        df = pd.read_csv(file_path)
        return df.to_string()


# Usage examples in your existing code:

def main():
    # Example 1: Using the enhanced DataProcessor
    processor = DataProcessor()
    processor.load_csv("data.csv").filter_data(lambda x: x['value'] > 100).pretty_print()
    
    # Example 2: Direct function usage
    sample_data = [
        ["Name", "Age", "City"],
        ["Alice", 30, "New York"],
        ["Bob", 25, "San Francisco"],
        ["Charlie", 35, "Chicago"]
    ]
    enhanced_print_table(sample_data[1:], sample_data[0])
    
    # Example 3: Factory pattern
    formatter = TableFormatter.create("auto")
    df = pd.read_csv("data.csv")
    output = formatter.format_dataframe(df)
    print(output)
    
    # Example 4: Integration with existing logging
    import logging
    logger = logging.getLogger(__name__)
    if TIDY_VIEWER_AVAILABLE:
        formatted_output = tidy_viewer.print_dataframe(df, file=None)
        logger.info(f"Data summary:\n{formatted_output}")


if __name__ == "__main__":
    main()