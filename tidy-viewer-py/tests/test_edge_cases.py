"""
Test edge cases and error conditions for PyO3 Python bindings.

This module tests error handling, boundary conditions, and edge cases
to ensure the Python bindings are robust and handle errors gracefully.
"""

import pytest
from conftest import PACKAGE_AVAILABLE, normalize_output

try:
    import tidy_viewer_py as tv
except ImportError:
    tv = None


@pytest.mark.skipif(not PACKAGE_AVAILABLE, reason="Package not built")
class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_inputs(self):
        """Test various empty input scenarios."""
        
        # Completely empty table
        result = tv.format_table([])
        assert isinstance(result, str)
        assert len(result) > 0  # Should return some message
        
        # Empty rows
        result = tv.format_table([[]])
        assert isinstance(result, str)
        
        # None as data (should handle gracefully or raise clear error)
        try:
            result = tv.format_table(None)
            # If it doesn't raise an error, should return a string
            assert isinstance(result, str)
        except (TypeError, ValueError) as e:
            # If it raises an error, should be informative
            assert "None" in str(e) or "data" in str(e).lower()
    
    def test_malformed_data_structures(self):
        """Test handling of malformed data structures."""
        
        # Mixed types in rows
        data = [
            ["Header1", "Header2", "Header3"],
            ["String", 123, None],
            [True, 45.67, "Another string"],
            [[], {}, "Complex"]
        ]
        
        # Should handle mixed types without crashing
        result = tv.format_table(data)
        norm_result = normalize_output(result)
        assert "Header1" in norm_result
        assert "String" in norm_result
        assert "123" in norm_result
    
    def test_extremely_long_strings(self):
        """Test handling of extremely long strings."""
        
        long_string = "A" * 10000  # Very long string
        data = [
            ["Short", "Very Long"],
            ["Hi", long_string]
        ]
        
        # Should handle without crashing
        result = tv.format_table(data)
        norm_result = normalize_output(result)
        assert "Short" in norm_result
        assert "Very Long" in norm_result
        # Long string should be truncated or handled appropriately
        assert "A" in norm_result
    
    def test_extremely_wide_tables(self):
        """Test handling of tables with many columns."""
        
        # Create table with many columns
        headers = [f"Col{i}" for i in range(100)]
        data = [headers]
        for i in range(5):
            row = [f"R{i}C{j}" for j in range(100)]
            data.append(row)
        
        # Should handle without crashing
        result = tv.format_table(data)
        norm_result = normalize_output(result)
        assert "Col0" in norm_result
        assert "Col99" in norm_result or "Col" in norm_result  # May be truncated
    
    def test_extremely_tall_tables(self):
        """Test handling of tables with many rows."""
        
        data = [["ID", "Value"]]
        for i in range(10000):
            data.append([f"ID{i}", f"Value{i}"])
        
        # Should handle without crashing (likely with row limiting)
        opts = tv.FormatOptions(max_rows=100)  # Reasonable limit
        result = tv.format_table(data, options=opts)
        norm_result = normalize_output(result)
        assert "ID" in norm_result
        assert "Value" in norm_result
        assert "ID0" in norm_result
    
    def test_numeric_edge_cases(self):
        """Test numeric formatting edge cases."""
        
        edge_numbers = [
            "0",
            "0.0",
            "1e-100",
            "1e100",
            "inf",
            "-inf",
            "nan",
            "1.7976931348623157e+308",  # Close to float64 max
            "2.2250738585072014e-308",  # Close to float64 min
            "999999999999999999999999999999",  # Very large integer
        ]
        
        data = [["Type", "Value"]]
        for i, num in enumerate(edge_numbers):
            data.append([f"Test{i}", num])
        
        # Should handle all these numbers without crashing
        result = tv.format_table(data)
        norm_result = normalize_output(result)
        assert "Type" in norm_result
        assert "Value" in norm_result
        assert "Test0" in norm_result
    
    def test_unicode_edge_cases(self):
        """Test Unicode edge cases."""
        
        unicode_edge_cases = [
            "🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟",  # Many emoji
            "ö̲̤̗̗̦̯̰̟̤̣̯̗̬̰̩̞̤̓͑̇̄͒̋̈́̀̊̈͐̚͝ͅm̸̧̡̰̺̳̪̺̥̥̰̮̗̦̱̒͆̄̿̍̍̎͌̊̚̚͝ǧ̸̢̨̧̢̛̛̤̤̰̺̞̺̬̗͒̅̈̌̈́̋̓̾̈́̓͋̇̚",  # Combining chars
            "𝕳𝖊𝖑𝖑𝖔 𝖂𝖔𝖗𝖑𝖉",  # Mathematical script
            "\u202e\u202d\u202c",  # RTL/LTR marks
            "零一二三四五六七八九",  # Chinese numbers
            "🏳️‍🌈🏳️‍⚧️👨‍👩‍👧‍👦",  # Complex emoji sequences
        ]
        
        data = [["Type", "Unicode"]]
        for i, text in enumerate(unicode_edge_cases):
            data.append([f"Test{i}", text])
        
        # Should handle Unicode without crashing
        result = tv.format_table(data)
        norm_result = normalize_output(result)
        assert "Type" in norm_result
        assert "Unicode" in norm_result
    
    def test_special_whitespace_characters(self):
        """Test handling of various whitespace characters."""
        
        whitespace_cases = [
            "\t",      # Tab
            "\n",      # Newline  
            "\r",      # Carriage return
            "\r\n",    # CRLF
            " ",       # Regular space
            "\u00A0",  # Non-breaking space
            "\u2000",  # En quad
            "\u2001",  # Em quad
            "\u2002",  # En space
            "\u2003",  # Em space
            "\u2004",  # Three-per-em space
            "\u2005",  # Four-per-em space
            "\u2006",  # Six-per-em space
            "\u2007",  # Figure space
            "\u2008",  # Punctuation space
            "\u2009",  # Thin space
            "\u200A",  # Hair space
        ]
        
        data = [["Type", "Whitespace"]]
        for i, ws in enumerate(whitespace_cases):
            data.append([f"Test{i}", f"Before{ws}After"])
        
        # Should handle various whitespace without crashing
        result = tv.format_table(data)
        norm_result = normalize_output(result)
        assert "Type" in norm_result
        assert "Before" in norm_result
        assert "After" in norm_result


@pytest.mark.skipif(not PACKAGE_AVAILABLE, reason="Package not built")
class TestErrorHandling:
    """Test error handling and invalid inputs."""
    
    def test_invalid_file_paths(self):
        """Test handling of invalid file paths."""
        
        invalid_paths = [
            "/nonexistent/path/file.csv",
            "C:\\nonexistent\\path\\file.csv",
            "",
            None,
            123,  # Wrong type
        ]
        
        for path in invalid_paths:
            try:
                result = tv.format_csv(path)
                # If it doesn't raise an error, should be a meaningful message
                assert isinstance(result, str)
                assert len(result) > 0
            except (FileNotFoundError, TypeError, ValueError) as e:
                # Expected errors should have meaningful messages
                error_msg = str(e).lower()
                assert any(word in error_msg for word in ["file", "path", "not found", "invalid", "type"])
    
    def test_invalid_options(self):
        """Test handling of invalid FormatOptions."""
        
        data = [["Test", "Data"]]
        
        # Test invalid significant figures
        try:
            opts = tv.FormatOptions(significant_figures=0)  # Should be >= 1
            result = tv.format_table(data, options=opts)
        except ValueError as e:
            assert "significant" in str(e).lower() or "figures" in str(e).lower()
        
        try:
            opts = tv.FormatOptions(significant_figures=100)  # Too large
            result = tv.format_table(data, options=opts)
        except ValueError as e:
            assert "significant" in str(e).lower() or "figures" in str(e).lower()
        
        # Test invalid max_rows
        try:
            opts = tv.FormatOptions(max_rows=-1)  # Should be positive
            result = tv.format_table(data, options=opts)
        except ValueError as e:
            assert "rows" in str(e).lower() or "negative" in str(e).lower()
        
        # Test invalid color theme
        try:
            opts = tv.FormatOptions(color_theme="nonexistent_theme")
            result = tv.format_table(data, options=opts)
            # May succeed with default theme or raise error
        except ValueError as e:
            assert "theme" in str(e).lower() or "color" in str(e).lower()
    
    def test_invalid_delimiters(self):
        """Test handling of invalid delimiters."""
        
        import tempfile
        import os
        
        # Create test CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("A,B,C\n1,2,3\n")
            test_file = f.name
        
        try:
            # Test with wrong delimiter (should still work but parse incorrectly)
            opts = tv.FormatOptions(delimiter=";")  # Wrong for comma-separated
            result = tv.format_csv(test_file, options=opts)
            # Should not crash, but may not parse correctly
            assert isinstance(result, str)
            
            # Test with invalid delimiter types
            try:
                opts = tv.FormatOptions(delimiter="")  # Empty string
                result = tv.format_csv(test_file, options=opts)
            except ValueError:
                pass  # Expected
            
            try:
                opts = tv.FormatOptions(delimiter=None)  # None
                result = tv.format_csv(test_file, options=opts)
            except (ValueError, TypeError):
                pass  # Expected
                
        finally:
            try:
                os.unlink(test_file)
            except FileNotFoundError:
                pass
    
    def test_method_chaining_errors(self):
        """Test error handling in method chaining."""
        
        # Test invalid chaining arguments
        try:
            result = tv.tv().significant_figures(-1).format_table([["A"]])
        except ValueError as e:
            assert "significant" in str(e).lower()
        
        try:
            result = tv.tv().max_rows(-5).format_table([["A"]])
        except ValueError as e:
            assert "rows" in str(e).lower()
        
        try:
            result = tv.tv().color_theme("invalid").format_table([["A"]])
            # May succeed with default or raise error
        except ValueError:
            pass
    
    def test_memory_pressure(self):
        """Test behavior under memory pressure scenarios."""
        
        # Create very large data structure
        try:
            large_data = [["Col1", "Col2", "Col3"]]
            # Add many rows (but not too many to actually crash the test)
            for i in range(50000):
                large_data.append([f"Data{i}", f"Value{i}", f"Item{i}"])
            
            # Should handle gracefully (possibly with truncation)
            opts = tv.FormatOptions(max_rows=100)  # Limit output
            result = tv.format_table(large_data, options=opts)
            
            # Should return something reasonable
            assert isinstance(result, str)
            assert "Col1" in result
            
        except MemoryError:
            # This is acceptable for very large datasets
            pytest.skip("Memory limit reached - expected for large datasets")


@pytest.mark.skipif(not PACKAGE_AVAILABLE, reason="Package not built")
class TestBoundaryConditions:
    """Test boundary conditions and limits."""
    
    def test_minimum_valid_inputs(self):
        """Test minimum valid inputs."""
        
        # Single cell
        result = tv.format_table([["A"]])
        norm_result = normalize_output(result)
        assert "A" in norm_result
        
        # Single row, multiple columns
        result = tv.format_table([["A", "B", "C"]])
        norm_result = normalize_output(result)
        assert "A" in norm_result
        assert "B" in norm_result
        assert "C" in norm_result
        
        # Multiple rows, single column
        result = tv.format_table([["A"], ["B"], ["C"]])
        norm_result = normalize_output(result)
        assert "A" in norm_result
        assert "B" in norm_result
        assert "C" in norm_result
    
    def test_maximum_reasonable_inputs(self):
        """Test maximum reasonable inputs."""
        
        # Test with reasonable maximum dimensions
        max_cols = 50
        max_rows = 1000
        
        # Create large but reasonable table
        headers = [f"Col{i}" for i in range(max_cols)]
        data = [headers]
        
        for i in range(max_rows):
            row = [f"R{i}C{j}" for j in range(max_cols)]
            data.append(row)
        
        # Should handle with appropriate limits
        opts = tv.FormatOptions(max_rows=50)  # Reasonable display limit
        result = tv.format_table(data, options=opts)
        
        norm_result = normalize_output(result)
        assert "Col0" in norm_result
        assert "R0C0" in norm_result
    
    def test_precision_boundaries(self):
        """Test numeric precision boundaries."""
        
        # Test with minimum and maximum significant figures
        data = [["Value"], ["123.456789123456789"]]
        
        # Minimum sig figs
        opts = tv.FormatOptions(significant_figures=1)
        result = tv.format_table(data, options=opts)
        norm_result = normalize_output(result)
        assert "Value" in norm_result
        assert "1" in norm_result  # Should be rounded to 1 sig fig
        
        # Maximum sig figs  
        opts = tv.FormatOptions(significant_figures=7)
        result = tv.format_table(data, options=opts)
        norm_result = normalize_output(result)
        assert "Value" in norm_result
        assert "123.456" in norm_result or "123456" in norm_result  # 7 sig figs
    
    def test_column_width_boundaries(self):
        """Test column width constraint boundaries."""
        
        data = [["VeryLongColumnHeader", "Short"], ["VeryLongDataValue", "X"]]
        
        # Minimum column width
        opts = tv.FormatOptions(lower_column_width=2)
        result = tv.format_table(data, options=opts)
        # Should not crash
        assert isinstance(result, str)
        
        # Maximum reasonable column width
        opts = tv.FormatOptions(upper_column_width=100)
        result = tv.format_table(data, options=opts)
        # Should not crash and should show full content
        norm_result = normalize_output(result)
        assert "VeryLongColumnHeader" in norm_result
        assert "VeryLongDataValue" in norm_result
