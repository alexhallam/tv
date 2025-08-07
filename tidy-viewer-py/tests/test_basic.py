"""Basic tests for tidy-viewer-py functionality."""

import pytest
import tempfile
import csv
import os

# This will fail until we build the package
try:
    import tidy_viewer_py as tv
    PACKAGE_AVAILABLE = True
except ImportError:
    PACKAGE_AVAILABLE = False


@pytest.mark.skipif(not PACKAGE_AVAILABLE, reason="Package not built")
class TestBasicFunctionality:
    
    def test_simple_table(self):
        """Test basic table formatting."""
        data = [["Alice", 25], ["Bob", 30]]
        headers = ["Name", "Age"]
        
        result = tv.format_table(data, headers)
        assert "Alice" in result
        assert "Bob" in result
        assert "Name" in result
        assert "Age" in result
        assert "tv dim: 2 x 2" in result
    
    def test_options(self):
        """Test formatting options."""
        data = [["Test", 123.456789]]
        
        # Test significant figures
        opts = tv.FormatOptions(significant_figures=2)
        result = tv.format_table(data, options=opts)
        assert "123" in result or "1.2e+02" in result
        
        # Test no dimensions
        opts = tv.FormatOptions(no_dimensions=True)
        result = tv.format_table(data, options=opts)
        assert "tv dim:" not in result
    
    def test_csv_file(self):
        """Test CSV file formatting."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Value", "Status"])
            writer.writerow(["Item1", "100", "Active"])
            writer.writerow(["Item2", "200", "Inactive"])
            csv_path = f.name
        
        try:
            result = tv.format_csv(csv_path)
            assert "Item1" in result
            assert "Item2" in result
            assert "100" in result
            assert "200" in result
        finally:
            os.unlink(csv_path)
    
    def test_method_chaining(self):
        """Test the TV method chaining API."""
        data = [["A", 1], ["B", 2]]
        
        # Test chaining
        result = tv.tv().no_dimensions().max_rows(1).format_table(data)
        assert "tv dim:" not in result
        assert "A" in result
        assert "B" not in result  # Max rows = 1
    
    def test_color_themes(self):
        """Test different color themes."""
        data = [["Test"]]
        
        themes = ["nord", "gruvbox", "dracula", "one_dark", "solarized_light"]
        for theme in themes:
            opts = tv.FormatOptions(color_theme=theme)
            result = tv.format_table(data, options=opts)
            assert "Test" in result  # Basic check that it doesn't crash
    
    def test_missing_values(self):
        """Test NA value handling."""
        data = [["Alice", "NA"], ["Bob", ""], ["Charlie", "None"]]
        headers = ["Name", "Value"]
        
        result = tv.format_table(data, headers)
        assert "NA" in result  # Should be formatted as NA
    
    def test_large_numbers(self):
        """Test scientific notation for large numbers."""
        data = [["Small", 123], ["Large", 123456789012345]]
        
        opts = tv.FormatOptions(max_decimal_width=10)
        result = tv.format_table(data, options=opts)
        assert "e+" in result.lower()  # Should use scientific notation


@pytest.mark.skipif(not PACKAGE_AVAILABLE, reason="Package not built")
class TestEdgeCases:
    
    def test_empty_data(self):
        """Test empty data handling."""
        result = tv.format_table([])
        assert "No data" in result
    
    def test_uneven_rows(self):
        """Test handling of uneven row lengths."""
        data = [["A", "B", "C"], ["D", "E"], ["F"]]
        result = tv.format_table(data)
        assert "A" in result
        assert "F" in result
    
    def test_unicode_handling(self):
        """Test Unicode character handling."""
        data = [["🌟", "測試"], ["Hello", "世界"]]
        result = tv.format_table(data)
        assert "🌟" in result
        assert "測試" in result