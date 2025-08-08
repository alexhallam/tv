# Fix Formatting Differences Plan

Based on the output parity test, here are the key differences that need to be fixed:

## 1. Row Numbering Issue
**Problem**: Python port shows row numbers (1, 2, 3...), Rust tv CLI doesn't
**Solution**: Disable row numbering in Python port by default

## 2. Column Alignment Differences
**Problem**: Rust tv CLI uses different spacing and alignment
**Solution**: Match the exact spacing and alignment from Rust tv CLI

## 3. Cargo Build Output
**Problem**: Rust output includes cargo build messages
**Solution**: Filter out cargo build messages from comparison

## 4. Specific Formatting Issues

### Row Numbering
- Rust: No row numbers
- Python: Shows row numbers (1, 2, 3...)
- **Fix**: Set `no_row_numbering=True` by default in Python port

### Column Spacing
- Rust: Uses specific spacing between columns
- Python: Different spacing
- **Fix**: Match exact spacing from Rust implementation

### Header Formatting
- Rust: Headers are aligned differently
- Python: Different header alignment
- **Fix**: Match header formatting exactly

### Data Alignment
- Rust: Left-aligned data
- Python: Different alignment
- **Fix**: Ensure left-aligned data matching Rust

## Implementation Steps

### Step 1: Fix Row Numbering
1. Modify `FormatOptions` default to have `no_row_numbering=True`
2. Update Python port to match Rust behavior

### Step 2: Fix Column Spacing
1. Analyze Rust tv CLI spacing exactly
2. Update Python formatting to match
3. Ensure consistent spacing between columns

### Step 3: Fix Header Formatting
1. Match header alignment from Rust
2. Ensure consistent header spacing

### Step 4: Fix Data Alignment
1. Ensure left-aligned data
2. Match exact spacing from Rust

### Step 5: Update Test Script
1. Filter out cargo build messages
2. Improve comparison logic
3. Add specific test cases

## Files to Modify

1. `tidy-viewer-py/src/types.rs` - Update FormatOptions defaults
2. `tidy-viewer-py/src/formatting.rs` - Fix spacing and alignment
3. `tidy-viewer-py/src/tidy_viewer_py/__init__.py` - Update Python defaults
4. `test_output_parity.py` - Improve test script

## Expected Result
After fixes, the Python port should produce output identical to the Rust tv CLI.
