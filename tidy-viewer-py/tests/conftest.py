"""
Test configuration and utilities for tidy-viewer-py tests.
"""

try:
    import tidy_viewer_py as tv
    PACKAGE_AVAILABLE = True
except ImportError:
    PACKAGE_AVAILABLE = False


def normalize_output(output: str) -> str:
    """Normalize test output by removing color codes and extra whitespace."""
    import re
    
    # Remove ANSI color codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    output = ansi_escape.sub('', output)
    
    # Normalize whitespace
    output = re.sub(r'\s+', ' ', output)
    
    return output.strip()
