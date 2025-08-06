

1.6.2 (2025-01-27)
==================

* **Bug Fix** **JSON File Graceful Error Handling** - Added proper detection and graceful error handling for JSON files to prevent crashes and provide helpful guidance.

  **Issues Fixed:**
  - **JSON File Crashes**: Previously crashed with `UnequalLengths` error when trying to parse JSON as CSV
  - **Poor User Experience**: No clear indication of why JSON files failed or what alternatives to use
  - **Missing File Type Detection**: No detection of JSON files by extension or content

  **Changes Made:**
  - **JSON Detection**: Added detection of JSON files by `.json` extension and content validation
  - **Graceful Error Messages**: Clear, helpful error messages explaining JSON is not supported
  - **Alternative Suggestions**: Provides guidance on using `jq` for JSON processing
  - **Maintained Compatibility**: All existing CSV, TSV, PSV, and Parquet functionality preserved

  **Technical Details:**
  - Added `serde_json` dependency for JSON content validation
  - Implemented `is_json_file()` function for extension-based detection
  - Added `validate_json_content()` function for content-based validation
  - Created `handle_json_file()` function with comprehensive error messaging
  - Integrated JSON detection into main file processing pipeline

  **Benefits:**
  - **No More Crashes**: JSON files now handled gracefully instead of causing panics
  - **Better UX**: Clear error messages guide users to appropriate tools
  - **Educational**: Helps users understand supported formats and alternatives
  - **Robust**: Works with both valid and invalid JSON files

* **Bug Fix** **Streaming Mode Display Consistency** - Fixed inconsistent row count reporting in streaming mode that was showing three different row counts for the same file.

  **Issues Fixed:**
  - **Inconsistent Row Counts**: Previously showed conflicting numbers between dimension line, ellipsis footer, and streaming footer
  - **Streaming Indicator Placement**: Moved streaming indicator from separate footer to integrated dimension line display
  - **Calculation Accuracy**: Fixed remaining row calculation in `read_parquet_streaming` function to match ellipsis logic

  **Changes Made:**
  - **Unified Display**: Streaming mode now shows `tv dim: ~[total_rows] x [cols]` with tilde prefix instead of separate footer
  - **Consistent Calculations**: Remaining row count now correctly calculated as `total_rows - actual_displayed_rows`
  - **Cleaner Output**: Removed redundant "Streaming mode: showing sample" footer for cleaner display
  - **Better UX**: Tilde prefix (~) clearly indicates streaming mode without cluttering output

  **Technical Details:**
  - Fixed `remaining` calculation in `read_parquet_streaming` to use `actual_displayed_rows` instead of `displayed_data_rows`
  - Updated dimension line display logic to include tilde prefix when streaming is active
  - Removed streaming footer display code entirely
  - Ensures consistency between ellipsis calculation and streaming remaining calculation

  **Benefits:**
  - **Consistent Output**: All row count references now show the same numbers
  - **Cleaner Interface**: Single streaming indicator instead of multiple conflicting messages
  - **Better UX**: Clear visual distinction between streaming and full file modes
  - **Maintained Functionality**: All existing features work exactly as before

1.6.1 (2025-08-06)
==================

* **Major Feature** **Parquet File Support** - Added native support for reading and displaying Apache Parquet files with full compatibility with existing CSV visualization features.

  **New Capabilities:**
  - **Automatic File Detection**: Parquet files are automatically detected by `.parquet` extension
  - **Schema-based Headers**: Column names extracted from Parquet schema metadata
  - **Consistent Formatting**: String values display without quotes, matching CSV behavior
  - **Index Column Filtering**: Automatically excludes common index columns (`id`, `index`, `__index_level_0__`) that are often added by external tools like pandas, for clean display
  - **Full Feature Compatibility**: All existing tv features work with Parquet files (colors, column width limits, row limits, etc.)

  **Usage Examples:**
  ```sh
  # View a Parquet file (same as CSV usage)
  tv data.parquet
  
  # Use with all existing options
  tv data.parquet -n 50 --color 2 --title "My Parquet Data"
  
  # Extended width for large datasets
  tv large_dataset.parquet -e -f | less -S
  ```

  **Technical Implementation:**
  - Integrated `parquet` crate v53.0 with `arrow-*` dependencies v53.4.1
  - Unified processing pipeline supporting both CSV and Parquet inputs
  - Memory-efficient row iteration for large Parquet files
  - Maintains backward compatibility - no changes to existing CSV functionality

  **Benefits:**
  - Access to compressed columnar data format without external tools
  - Seamless workflow for data scientists using both CSV and Parquet
  - Leverages tv's superior visualization for Parquet data exploration
  - Significant performance benefits for large datasets via Parquet's columnar storage

* **Major Feature** **Streaming Mode for Large Files** - Added intelligent streaming/lazy loading to dramatically reduce memory usage when viewing large datasets.

  **New Capabilities:**
  - **Automatic File Size Detection**: Files larger than 5MB automatically use streaming mode
  - **Adaptive Sampling**: Smart sample sizes (1K-10K rows) based on file size for optimal performance
  - **Memory Efficiency**: Load only sample data for display instead of entire file
  - **Streaming Indicator**: Clear visual feedback when in streaming mode with remaining row count
  - **Dual Format Support**: Works seamlessly with both CSV and Parquet files

  **New Command-Line Options:**
  - `--streaming-threshold <MB>`: Custom file size threshold for streaming (default: 5MB)
  - `--no-streaming`: Disable streaming mode even for large files

  **Usage Examples:**
  ```sh
  # Automatic streaming for files >5MB
  tv large_dataset.csv
  
  # Custom threshold - stream files >10MB
  tv data.csv --streaming-threshold 10
  
  # Force full file loading even for large files
  tv huge_file.csv --no-streaming
  
  # Works with Parquet files too
  tv large_data.parquet --streaming-threshold 3
  ```

  **Streaming Mode Output:**
  ```
  📊 Streaming Mode: Showing sample of data (~95000 more rows not shown)
          tv dim: 100000 x 5
          id name    value1  value2  category
       1  0  user_0   0.245  -0.497  A
       ...
  ```

  **Technical Implementation:**
  - Intelligent row counting for CSV files using line-based estimation
  - Exact row counts for Parquet files using metadata
  - Graceful fallback to full loading for small files regardless of threshold
  - Memory usage reduced from O(n) to O(sample_size) for large files
  - Zero performance impact for files below threshold

  **Benefits:**
  - **Dramatic Memory Reduction**: 100MB file uses ~1MB memory in streaming mode
  - **Faster Load Times**: Sample-based loading is significantly faster than full file parsing
  - **Large File Support**: Handle multi-GB files that previously caused memory issues
  - **Preserves All Features**: Full tv functionality maintained in streaming mode

1.6.0 (2025-08-06)
==================

* **Feature** **Scientific Notation Formatting Override** - Added comprehensive support for handling scientific notation in CSV data to address cases where tv was converting pre-formatted scientific notation (like p-values) to hard-to-read decimal format.

  **New Command-Line Options:**
  - `--preserve-scientific`: Preserves existing scientific notation from input data (e.g., `7.55e-15` stays as `7.55e-15` instead of being converted to `0.000000000000008`)
  - `--max-decimal-width N`: Auto-converts to scientific notation when decimal representation exceeds N characters (default: 13), similar to R's pillar package behavior

  **Configuration File Support:**
  Both options can be configured in `tv.toml`:
  ```toml
  preserve_scientific = true
  max_decimal_width = 10
  ```

  **Examples:**
  ```sh
  # Preserve scientific notation from input
  tv data.csv --preserve-scientific
  
  # Auto-convert long decimals to scientific notation
  tv data.csv --max-decimal-width 8
  
  # Use both features together
  tv data.csv --preserve-scientific --max-decimal-width 10
  ```

  **Benefits:**
  - Scientific data with p-values and coefficients remains readable
  - Maintains tv's excellent visual formatting while respecting input format
  - Configurable thresholds for automatic conversion
  - Backward compatible - existing behavior unchanged when flags not used

* **Testing** Added comprehensive test suite with 8 new unit and integration tests covering scientific notation functionality, including regression protection for real-world data scenarios.

1.5.2 (2023-07-04) 
==================

* **Feature** A new flag and associated output is available. The new flat is `--config-details` or `-C`. This will allow users to see the current configuration of `tv`. This is useful for debugging. Here is an example of the output:

```sh
> tidy-viewer -C

tv.toml
[+] delimiter = ","
[+] title = ""
[-] footer = None
[+] upper_column_width = 20
[+] lower_column_width = 2
[+] number = 35
[-] extend_width_length = None
[+] meta_color = [Integer(255), Integer(0), Integer(0)]
[+] header_color = [Integer(232), Integer(168), Integer(124)]
[+] std_color = [Integer(133), Integer(205), Integer(202)]
[+] na_color = [Integer(226), Integer(125), Integer(95)]
[-] neg_num_color = None
```

- The `[+]` indicates that the values was found in the `tv.toml` file. 

- The `[-]` indicates that the value was not found in the `tv.toml` file and the default value was used.

* **Bug** [#165](https://github.com/alexhallam/tv/issues/165) The `tv.toml` has had a long history of being buggy. This is because users must provide entries for every key. I removed this constraint. Now, if a key is not provided, the default value is used. This should make the `tv.toml` more user friendly. Thanks @winter-again for the bug report.
* **Bug** [#163](https://github.com/alexhallam/tv/issues/163) Option `--number of rows to output` requires spaces between words instead of dashes. All other long form options use a dash to delimit words. Thanks @derekmahar for bug report.


1.4.30 (2022-08-23) 
==================

`tv` is 1 year old 🎉🥳🎉.

* **Bug** I noticed that `tv` would not print remaining columns if the number of rows was less than `n`.

Changed `if rows_remaining > 0` to `if rows_remaining > 0 || (cols - num_cols_to_print) > 0` as the 
condition needed to get the footer to kick in.

Also, I was looking through the changelog and saw that I never gave credit to @burntsushi for holding
my hand as I was starting this project 1 year ago. I had a vision for this CLI, but was struggling with
some basics as I was learning Rust. Thank You!

Note: Yes, I know there are a lot of versions skipped! I was struggling with getting some automated builds for
one of the releases. One quark is that builds are triggered with git tags. I used up a lot of git tags to test
things out. Which reminds me, thanks @certifiedloud for making the most recent builds possible. I could not 
have done it without you.


1.4.6 (2022-07-23)
==================

This update was mainly focused on feature enhancements. I also did some `clippy` formatting.

* **Bug** [#141](https://github.com/alexhallam/tv/issues/141) Right alignment of row numbers might make it easier for users to quickly scan the output.

I did not realize that I had the alignment wrong. I was doing left alignment, but it was brought to my attention that `tibble` uses right alignment.
This is now corrected. Thanks for the sharp eye @briandconnelly.

* **Bug** [#140](https://github.com/alexhallam/tv/issues/140)  `-n` option doesn't work when combined with `--extend-rows`

This was a bug I was not aware of that I wanted to knock out. Thanks @atsalolikhin-spokeo for using this package and reporting the issue. Your
report made the cli a little better.
  
* **Enhancement, Good first issue** [#139](https://github.com/alexhallam/tv/issues/139)  Is it possible to turn off row numbering?

As requested I implemented `-R`, `--no-row-numbering` for this functionality
  
* **Enhancement, Good first issue** [#138](https://github.com/alexhallam/tv/issues/138)  Is it possible to turn off dimensions printing?

As requested I implemented `-D`, `--no-dimensions` for this functionality

1.4.5 (2021-05-10)
==================

* **Bug 1**  Though `-e` was added as an option I found that it was not overriding the `-n` argument. The fix was made with a simple if/else statement. 

It may seem odd to bump the version with such a small bug, but I did not want to have something in the help file that was not functional in
the CLI. 

1.4.4 (2021-05-02)
==================

* **Feature 1**  Added `-e` flag to extend rows (don't truncate).

This new version gives a flag option to extend rows rather than truncate. This is especially useful for wide csv files that would overflow the terminal width. When using the extend mode, pipe output to `less -S` to enables scrolling right and left with arrow keys.

I also did some clean up work. I removed a binary I was not using.

1.4.3 (2021-11-17)
==================

* **Feature 1**  Added forced color flag for color pager support [Issue #112](https://github.com/alexhallam/tv/issues/112)

I was not aware of this until @ismaelgv opened the issue. `less -R` and `bat -p` can do color comprehension. In previous versions of `tv` we just stripped the color if the output was piped to programs like less. Now the user can override this behavior with a `-a` flag.


1.4.2 (2021-10-28)
==================

### Version 1 🎉🥳🎉

We made it!! Version #1!!

Technically it is version 1.4.2. The [42](https://hitchhikers.fandom.com/wiki/42) is a homage to Geek culture.

What makes this release version 1? My view is that version 1 should encapsulate the original vision of the software. The features of the current package is what I imagined when I started drawing up the project. Of course, as I have continued to work on the package I have found many additional enhancements. Also, if it were not for users of the software I would not have had additional feedback which has improved on this package tremendously. I will continue to work on enhancements. There are currently a list of issues I plan to address. I will also address bugs as they are reported. A special thanks goes to all of the contributors. Not only has `tv` been improved by smart contributors, but my own learning experience has been enhanced. Thank you!

* **Feature 1** Added the option to modify the `sigfig` from the command line with the `g` option. [PR #107](https://github.com/alexhallam/tv/pull/107). Thanks to @rlewicki for this fantastic contribution🎉
* **Bug 1** Added NA alignment. If an NA is in a double or int column then the NA string is right aligned. If it is in a char or any other type it is left aligned. NA stings in double columns do not pass the decimal.[Bug #105](https://github.com/alexhallam/tv/issues/105)


0.0.22 (2021-10-18)
==================

Thanks to @Lireer and @rlewicki for the fantastic contributions in this release 🎉

* **Feature 1** Color negative numbers [PR #98](https://github.com/alexhallam/tv/pull/98)
* **Feature 2** Parse `\t` as tab delimiter [PR #99](https://github.com/alexhallam/tv/pull/99)
* **Feature 3** Check file extensions to choose a delimiter [PR #100](https://github.com/alexhallam/tv/pull/100)
* **Feature 4** Use atty to omit text coloring and decorations  [PR #95](https://github.com/alexhallam/tv/pull/95). 

Along with these new features came additional tests. 

Since [PR #98](https://github.com/alexhallam/tv/pull/98) was a aesthetic change it was also added as an additional parameter to be tweaked with a config file.

0.0.21 (2021-10-09)
==================

* **Feature 1** Add configuration via `tv.toml`
* **Feature 2** Decimal alignment. Correct formatting with a single pass. General code clean up. Thanks @jacobmischka!

We also saw @namitaarya fix a help file typo.

0.0.20 (2021-10-02)
==================

* **Feature 1** Detect floats with `f64::from_str`
* **Feature 2** Add the ability to pass file as argument. Not just stdin only.
* [bug #75](https://github.com/alexhallam/tv/issues/75):
Cut space from really long doubles.
* [bug #25](https://github.com/alexhallam/tv/issues/25):
Exponential notation is not captured as a float. Fixed with above feature 1.

We also saw some code quality improvements in this release. [PR #82](https://github.com/alexhallam/tv/pull/82)


0.0.19 (2021-09-29)
==================

The version number jump was due to testing out github actions on automated releases using git tags as the release name. It took a few tries to get right.

* **Feature 1** Add package to `snapcraft` to increase accessibility.
* [bug #55](https://github.com/alexhallam/tv/issues/55):
fix panic on unicode string truncation
* [BUG #40](https://github.com/alexhallam/tv/issues/30):
Remove trailing comma.
* [BUG #48](https://github.com/alexhallam/tv/issues/48):
Logicals 1/0 were mentioned in comments, but not implemented.
* [BUG #60](https://github.com/alexhallam/tv/issues/60):
Ellipsis then space, not space then ellipsis.

The rest of the updates had to do with README updates and spelling errors in code comments.

0.0.13 (2021-09-27)
==================
This version was made possible by the contributions of @Lireer! Thank You!

* [PR #40](https://github.com/alexhallam/tv/pull/40) Allow users to specify the deliminator with the `delimiter` option.
* [PR #42](https://github.com/alexhallam/tv/pull/42) `clippy` warnings and code refactoring. 
* [PR #41](https://github.com/alexhallam/tv/pull/41) change `.len()` to `.chars().count()` to avoid potential column widths if the value contains code points consisting of multiple bytes.

0.0.12 (2021-09-09)
==================
* [BUG #33](https://github.com/alexhallam/tv/issues/33) Ellipses used when NA should replace on unquoted string missingness #33
This problem was caused by all of the columns being width 1. When width is 1 the length of the string "NA" is 2. Since 2 was greater
than 1 NA was converted to ellipses. To fix this problem I added a min width of 2 and while I was at it I included a new option `lower-column-width`
* [BUG #32](https://github.com/alexhallam/tv/issues/32) Column with integer 1 and 0 returns NaN for 0.
This bug was caused by logging 0s. I added a condition on the sigfig decision tree to fix.
* **Feature 1** `lower-column-width`: `The lower (minimum) width of columns. Must be 2 or larger. Default 2. `
* **Feature 2** `upper-column-width`: `The upper (maximum) width of columns. Default 20.`
* **Feature 2** `debug-mode`: `Print object details to make it easier for the maintainer to find and resolve bugs.` This is to save me time in the future :smile:

0.0.10 (2021-08-05)
==================
* [BUG #29](https://github.com/alexhallam/tv/issues/29) Turns out the column count was correct. `tv` was not printing the last column

0.0.9 (2021-08-05)
==================
Minor Mistakes:

* Added color format to additional footer data.
* [BUG #29](https://github.com/alexhallam/tv/issues/29):
Column count was wrong.
* [BUG #28](https://github.com/alexhallam/tv/issues/28):
Accidental extra info printed from debug.

0.0.8 (2021-08-05)
==================
Feature Enhancement:

* [BUG #23](https://github.com/alexhallam/tv/issues/23):
Simplified the regex for floats.
* [BUG #19](https://github.com/alexhallam/tv/issues/19):
Printing "wide" datasets with more columns than space in the terminal resulted in a poor viewer experience. This fix removes extra columns from the print and mentions them in the footer.
