//! # Data Type Module
//! 
//! This module provides data type inference, formatting, and validation functions
//! for tabular data processing. It handles various data types including numbers,
//! dates, times, logical values, and missing values.
//! 
//! ## Key Functions
//! 
//! - **Type Detection**: Functions to identify data types (`is_integer`, `is_double`, etc.)
//! - **Formatting**: Functions to format data with significant figures and width constraints
//! - **Column Analysis**: Functions to analyze entire columns for type consistency
//! - **Width Calculation**: Functions to calculate optimal column widths
//! 
//! ## Usage Examples
//! 
//! ```rust
//! use tidy_viewer_core::datatype::{is_integer, is_double, format_strings, ValueType};
//! 
//! // Detect data types
//! assert!(is_integer("123"));
//! assert!(is_double("123.45"));
//! 
//! // Format a column of data
//! let data = vec!["123", "456.78", "NA"];
//! let formatted = format_strings(&data, 2, 20, 3, false, 13);
//! 
//! // Infer column type
//! let col_type = tidy_viewer_core::get_col_data_type(&data);
//! ```

use itertools::Itertools;
use lazy_static::lazy_static;
use regex::Regex;
use std::str::FromStr;
use unicode_truncate::UnicodeTruncateStr;
use unicode_width::UnicodeWidthStr;

pub mod sigfig;

/// Represents the type of a value in tabular data.
/// 
/// This enum is used to classify the data type of individual values
/// or entire columns in tabular data.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ValueType {
    /// Boolean/logical values (true/false, T/F, 1/0)
    Boolean,
    /// Integer numbers
    Integer,
    /// Floating-point numbers
    Double,
    /// Date values (YYYY-MM-DD format)
    Date,
    /// Time values (HH:MM:SS format)
    Time,
    /// Date and time values
    DateTime,
    /// Text/character data
    Character,
    /// Missing or null values
    Na,
}

/// Checks if a string represents a logical/boolean value.
/// 
/// Recognizes various boolean representations:
/// - `true`, `false`, `TRUE`, `FALSE`
/// - `t`, `f`, `T`, `F`
/// - `True`, `False`
/// - `1`, `0`
/// 
/// # Examples
/// 
/// ```rust
/// use tidy_viewer_core::datatype::is_logical;
/// 
/// assert!(is_logical("true"));
/// assert!(is_logical("FALSE"));
/// assert!(is_logical("1"));
/// assert!(is_logical("0"));
/// assert!(!is_logical("hello"));
/// ```
pub fn is_logical(text: &str) -> bool {
    // col_logical -l, T,F,TRUE,FALSE,True,False,true,false,t,f,1,0
    lazy_static! {
        static ref R: Regex =
            Regex::new(r"^true$|^false$|^t$|^f$|TRUE$|^FALSE$|^T$|^F$|^True|^False|^1$|^0$")
                .unwrap();
    }
    R.is_match(text)
}

/// Checks if a string represents an integer value.
/// 
/// Recognizes integers with optional leading sign and whitespace.
/// 
/// # Examples
/// 
/// ```rust
/// use tidy_viewer_core::datatype::is_integer;
/// 
/// assert!(is_integer("123"));
/// assert!(is_integer("-456"));
/// assert!(is_integer(" 789 "));
/// assert!(!is_integer("123.45"));
/// assert!(!is_integer("abc"));
/// ```
pub fn is_integer(text: &str) -> bool {
    //let integer = "5";
    lazy_static! {
        static ref R: Regex = Regex::new(r"^\s*([+-]?[1-9][0-9]*|0)\s*$").unwrap();
    }
    R.is_match(text)
}

/// Checks if a string represents any numeric value (integer or double).
/// 
/// # Examples
/// 
/// ```rust
/// use tidy_viewer_core::datatype::is_number;
/// 
/// assert!(is_number("123"));
/// assert!(is_number("123.45"));
/// assert!(is_number("-456.78"));
/// assert!(!is_number("abc"));
/// ```
pub fn is_number(text: &str) -> bool {
    is_integer(text) || is_double(text)
}

/// Checks if a string represents a negative number.
/// 
/// # Examples
/// 
/// ```rust
/// use tidy_viewer_core::datatype::is_negative_number;
/// 
/// assert!(is_negative_number("-123"));
/// assert!(is_negative_number("-123.45"));
/// assert!(!is_negative_number("123"));
/// assert!(!is_negative_number("abc"));
/// ```
pub fn is_negative_number(text: &str) -> bool {
    lazy_static! {
        static ref R: Regex = Regex::new(r"^\s*-[0-9]*.?[0-9]*\s*$").unwrap();
    }
    R.is_match(text)
}

/// Checks if a string represents a floating-point number.
/// 
/// # Examples
/// 
/// ```rust
/// use tidy_viewer_core::datatype::is_double;
/// 
/// assert!(is_double("123.45"));
/// assert!(is_double("-456.78"));
/// assert!(is_double("123"));
/// assert!(!is_double("abc"));
/// ```
pub fn is_double(text: &str) -> bool {
    f64::from_str(text.trim()).is_ok()
}

/// Checks if a string represents a number in scientific notation.
/// 
/// # Examples
/// 
/// ```rust
/// use tidy_viewer_core::datatype::is_scientific_notation;
/// 
/// assert!(is_scientific_notation("1.23e-4"));
/// assert!(is_scientific_notation("1.23E+4"));
/// assert!(!is_scientific_notation("123.45"));
/// assert!(!is_scientific_notation("abc"));
/// ```
pub fn is_scientific_notation(text: &str) -> bool {
    lazy_static! {
        static ref R: Regex = Regex::new(r"^[+-]?[0-9]*\.?[0-9]+[eE][+-]?[0-9]+$").unwrap();
    }
    R.is_match(text.trim())
}

/// Checks if a string represents a time value (HH:MM:SS format).
/// 
/// # Examples
/// 
/// ```rust
/// use tidy_viewer_core::datatype::is_time;
/// 
/// assert!(is_time("11:59:37"));
/// assert!(is_time("23:45:12"));
/// assert!(!is_time("25:00:00")); // Invalid hour
/// assert!(!is_time("abc"));
/// ```
pub fn is_time(text: &str) -> bool {
    //let time = "11:59:37 UTC";
    //https://stackoverflow.com/a/25873711
    lazy_static! {
        static ref R: Regex =
            Regex::new(r"^(?:[01][0-9]|2[0123]):(?:[012345][0-9]):(?:[012345][0-9])$").unwrap();
    }
    R.is_match(text)
}

/// Checks if a string represents a date value (YYYY-MM-DD format).
/// 
/// # Examples
/// 
/// ```rust
/// use tidy_viewer_core::datatype::is_date;
/// 
/// assert!(is_date("2020-10-09"));
/// assert!(is_date("1999-12-31"));
/// assert!(!is_date("2020/10/09")); // Wrong format
/// assert!(!is_date("abc"));
/// ```
pub fn is_date(text: &str) -> bool {
    lazy_static! {
        static ref R: Regex = Regex::new(r"\d{4}-\d{2}-\d{2}").unwrap();
    }
    R.is_match(text)
}

/// Checks if a string represents a date-time value.
/// 
/// # Examples
/// 
/// ```rust
/// use tidy_viewer_core::datatype::is_date_time;
/// 
/// assert!(is_date_time("11:59:37"));
/// assert!(is_date_time("23:45:12"));
/// assert!(!is_date_time("25:00:00")); // Invalid hour
/// assert!(!is_date_time("abc"));
/// ```
pub fn is_date_time(text: &str) -> bool {
    //let datetime = "2020-10-09 11:59:37 UTC";
    //https://stackoverflow.com/a/25873711
    lazy_static! {
        static ref R: Regex =
            Regex::new(r"^(?:[01][0-9]|2[0123]):(?:[012345][0-9]):(?:[012345][0-9])").unwrap();
    }
    R.is_match(text)
}

/// Checks if a string represents a missing/null value.
/// 
/// Recognizes various NA representations:
/// - Empty strings
/// - `NA`, `N/A`, `NaN`, `null`
/// - Case variations: `na`, `Na`, `NULL`, etc.
/// 
/// # Examples
/// 
/// ```rust
/// use tidy_viewer_core::datatype::is_na;
/// 
/// assert!(is_na(""));
/// assert!(is_na("NA"));
/// assert!(is_na("null"));
/// assert!(is_na("N/A"));
/// assert!(!is_na("hello"));
/// ```
pub fn is_na(text: &str) -> bool {
    lazy_static! {
        static ref R: Regex = Regex::new(
            r"^$|^(?:N(?:(?:(?:one|AN|a[Nn]|/A)|[Aa])|ull)|n(?:ull|an?|/a?)|(?:missing))$"
        )
        .unwrap();
    }
    R.is_match(text)
}

pub fn is_na_string_padded(text: &str) -> bool {
    lazy_static! {
        static ref R: Regex = Regex::new(
            r"^$|(^|\s)(?:N(?:(?:(?:AN|a[Nn]|/A)|[Aa])|ull)|n(?:ull|an?|/a?)|(?:missing))\s*$"
        )
        .unwrap();
    }
    R.is_match(text)
}

// utilities

/// Infers the data type of a string value.
/// 
/// This function analyzes a string and returns the most appropriate `ValueType`.
/// The inference follows a priority order: NA → Boolean → Integer → Double → Date → Time → Character.
/// 
/// # Examples
/// 
/// ```rust
/// use tidy_viewer_core::datatype::{infer_type_from_string, ValueType};
/// 
/// assert_eq!(infer_type_from_string(""), ValueType::Na);
/// assert_eq!(infer_type_from_string("true"), ValueType::Boolean);
/// assert_eq!(infer_type_from_string("123"), ValueType::Integer);
/// assert_eq!(infer_type_from_string("123.45"), ValueType::Double);
/// assert_eq!(infer_type_from_string("2020-10-09"), ValueType::Date);
/// assert_eq!(infer_type_from_string("11:59:37"), ValueType::Time);
/// assert_eq!(infer_type_from_string("hello"), ValueType::Character);
/// ```
pub fn infer_type_from_string(text: &str) -> ValueType {
    if is_time(text) {
        ValueType::Time
    } else if is_logical(text) {
        ValueType::Boolean
    } else if is_integer(text) {
        ValueType::Integer
    } else if is_date_time(text) {
        ValueType::DateTime
    } else if is_date(text) {
        ValueType::Date
    } else if is_double(text) {
        ValueType::Double
    } else if text.is_empty() | is_na(text) {
        ValueType::Na
    } else {
        ValueType::Character
    }
}

/// Formats a column of strings with consistent width and significant figures.
/// 
/// This is the main formatting function that processes an entire column of data.
/// It applies significant figure formatting to numeric values, handles NA values,
/// and ensures all strings fit within the specified width constraints.
/// 
/// # Arguments
/// 
/// * `vec_col` - Vector of string references representing the column data
/// * `lower_column_width` - Minimum column width
/// * `upper_column_width` - Maximum column width
/// * `sigfig` - Number of significant figures for numeric values
/// * `preserve_scientific` - Whether to preserve scientific notation
/// * `max_decimal_width` - Maximum width for decimal places
/// 
/// # Returns
/// 
/// A vector of formatted strings with consistent width and formatting.
/// 
/// # Examples
/// 
/// ```rust
/// use tidy_viewer_core::datatype::format_strings;
/// 
/// let data = vec!["123.456", "NA", "-42.1", "hello"];
/// let formatted = format_strings(&data, 2, 20, 3, false, 13);
/// 
/// // All formatted strings will have consistent width and formatting
/// assert_eq!(formatted.len(), 4);
/// ```
pub fn format_strings(
    vec_col: &[&str],
    lower_column_width: usize,
    upper_column_width: usize,
    sigfig: i64,
    preserve_scientific: bool,
    max_decimal_width: usize,
) -> Vec<String> {
    let ellipsis = '\u{2026}';

    let strings_and_fracts: Vec<(String, usize, usize)> = vec_col
        .iter()
        .map(|&string| format_if_na(string))
        .map(|string| format_if_num(&string, sigfig, preserve_scientific, max_decimal_width))
        .map(|string| {
            // the string, and the length of its fractional digits if any
            let (lhs, rhs) = if is_double(&string) {
                let mut split = string.split('.');
                (
                    split.next().map(|lhs| lhs.len()).unwrap_or_default(),
                    split.next().map(|rhs| rhs.len()).unwrap_or_default(),
                )
            } else {
                (0, 0)
            };
            (string, lhs, rhs)
        })
        .collect();

    let max_fract: usize = strings_and_fracts
        .iter()
        .map(|(_, _, fract)| *fract)
        .max()
        .unwrap_or_default();
    let max_whole: usize = strings_and_fracts
        .iter()
        .map(|(_, whole, _)| *whole)
        .max()
        .unwrap_or_default();

    let strings_and_widths: Vec<(String, usize)> = strings_and_fracts
        .into_iter()
        .map(|(mut string, whole, fract)| {
            if max_fract > 0 && is_double(&string) {
                if whole < max_whole {
                    let mut s = String::new();
                    s.push_str(&" ".repeat(max_whole - whole));
                    s.push_str(&string);
                    string = s;
                }

                string.push_str(&" ".repeat(max_fract - fract));
            } else if max_fract > 0 && is_na(&string) {
                if 2 < max_whole {
                    let mut s = String::new();
                    s.push_str(&" ".repeat(max_whole - 2));
                    s.push_str(&string);
                    string = s;
                }

                string.push_str(&" ".repeat(max_fract - fract));
            }
            let len = UnicodeWidthStr::width(string.as_str());
            // the string and its length
            (string, len)
        })
        .collect();

    let max_width: usize = strings_and_widths
        .iter()
        .map(|(_, width)| *width)
        .max()
        .unwrap_or_default()
        .clamp(lower_column_width, upper_column_width);

    strings_and_widths
        .into_iter()
        .map(|(string, len)| {
            if len > max_width {
                let (rv, _) = string.unicode_truncate(max_width - 1);
                let spacer: &str = " ";
                let string_and_ellipses = [rv.to_string(), ellipsis.to_string()].join("");
                [string_and_ellipses, spacer.to_string()].join("")
            } else {
                let add_space = max_width - len + 1;
                let borrowed_string: &str = &" ".repeat(add_space);
                [string, "".to_string()].join(borrowed_string)
            }
        })
        .collect()
}

pub fn format_if_na(text: &str) -> String {
    // todo add repeat strings for NA
    let missing_string_value = "NA";
    let string = if is_na(text) {
        missing_string_value
    } else {
        text
    };
    string.to_string()
}

pub fn format_if_num(
    text: &str,
    sigfig: i64,
    preserve_scientific: bool,
    max_decimal_width: usize,
) -> String {
    // If preserve_scientific is enabled and the input is already in scientific notation, keep it
    if preserve_scientific && is_scientific_notation(text) {
        return text.to_string();
    }

    if let Ok(val) = text.parse::<f64>() {
        let decimal_formatted = sigfig::DecimalSplits { val, sigfig }.final_string();

        // Check if we should auto-switch to scientific notation based on decimal width
        if decimal_formatted.len() > max_decimal_width {
            // Format in scientific notation with appropriate precision
            if val.abs() < 1e-4 || val.abs() >= 10f64.powi(sigfig as i32) {
                return format!(
                    "{:.precision$e}",
                    val,
                    precision = (sigfig - 1).max(0) as usize
                );
            }
        }

        decimal_formatted
    } else {
        text.to_string()
    }
}

pub fn get_col_data_type(col: &[&str]) -> ValueType {
    // counts the frequency of the datatypes in the column
    // returns the most frequent while ignoring NA values.
    col.iter()
        .map(|x| infer_type_from_string(x))
        .filter(|x| !matches!(x, &ValueType::Na))
        .group_by(|&x| x)
        .into_iter()
        .map(|(key, group)| (key, group.count()))
        .max_by_key(|&(_, count)| count)
        .map(|(key, _)| key)
        .unwrap()
}

pub fn parse_delimiter(src: &str) -> Result<u8, String> {
    let bytes = src.as_bytes();
    match *bytes {
        [del] => Ok(del),
        [b'\\', b't'] => Ok(b'\t'),
        _ => Err(format!(
            "expected one byte as delimiter, got {} bytes (\"{}\")",
            bytes.len(),
            src
        )),
    }
}

/// Calculates the optimal width for a column based on its content.
/// 
/// This function analyzes all strings in a column and determines the optimal width
/// that accommodates the content while respecting minimum and maximum constraints.
/// It uses Unicode width calculation to handle multi-byte characters correctly.
/// 
/// # Arguments
/// 
/// * `column` - Vector of formatted strings representing the column
/// * `min_width` - Minimum allowed column width
/// * `max_width` - Maximum allowed column width
/// 
/// # Returns
/// 
/// The calculated optimal width for the column.
/// 
/// # Examples
/// 
/// ```rust
/// use tidy_viewer_core::datatype::calculate_column_width;
/// 
/// let column = vec!["123".to_string(), "456.78".to_string(), "hello".to_string()];
/// let width = calculate_column_width(&column, 2, 20);
/// 
/// assert!(width >= 2 && width <= 20);
/// ```
pub fn calculate_column_width(
    column: &[String],
    min_width: usize,
    max_width: usize,
) -> usize {
    let max_content_width = column
        .iter()
        .map(|cell| unicode_width::UnicodeWidthStr::width(cell.as_str()))
        .max()
        .unwrap_or(0);
    
    max_content_width.clamp(min_width, max_width)
}

#[cfg(test)]
mod tests {
    use crate::datatype::{format_if_num, is_scientific_notation, parse_delimiter};

    #[test]
    fn one_byte_delimiter() {
        assert_eq!(parse_delimiter(","), Ok(b','));
        assert_eq!(parse_delimiter(";"), Ok(b';'));
        assert_eq!(parse_delimiter("|"), Ok(b'|'));
        assert_eq!(parse_delimiter(" "), Ok(b' '));
        assert_eq!(parse_delimiter("\t"), Ok(b'\t'));
    }

    #[test]
    fn tab_delimiter() {
        assert_eq!(parse_delimiter("\\t"), Ok(b'\t'));
    }

    #[test]
    fn delimiter_wrong_length() {
        assert_eq!(
            parse_delimiter(""),
            Err("expected one byte as delimiter, got 0 bytes (\"\")".to_string())
        );
        assert_eq!(
            parse_delimiter("too long"),
            Err("expected one byte as delimiter, got 8 bytes (\"too long\")".to_string())
        );
        assert_eq!(
            parse_delimiter("\\n"),
            Err("expected one byte as delimiter, got 2 bytes (\"\\n\")".to_string())
        );
    }

    #[test]
    fn test_is_scientific_notation() {
        // Valid scientific notation
        assert_eq!(is_scientific_notation("1.23e-7"), true);
        assert_eq!(is_scientific_notation("5.67e15"), true);
        assert_eq!(is_scientific_notation("-4.56e-10"), true);
        assert_eq!(is_scientific_notation("+2.34e8"), true);
        assert_eq!(is_scientific_notation("1e5"), true);
        assert_eq!(is_scientific_notation("3.14E-2"), true);
        assert_eq!(is_scientific_notation("7.849613446523261e-05"), true);

        // Invalid scientific notation (should be false)
        assert_eq!(is_scientific_notation("1.23"), false);
        assert_eq!(is_scientific_notation("123"), false);
        assert_eq!(is_scientific_notation("0.0001"), false);
        assert_eq!(is_scientific_notation("e5"), false);
        assert_eq!(is_scientific_notation("1.23e"), false);
        assert_eq!(is_scientific_notation("text"), false);
        assert_eq!(is_scientific_notation(""), false);
    }

    #[test]
    fn test_format_if_num_preserve_scientific() {
        // Test preserve scientific functionality
        assert_eq!(format_if_num("1.23e-7", 3, true, 13), "1.23e-7");
        assert_eq!(format_if_num("5.67e15", 3, true, 13), "5.67e15");
        assert_eq!(format_if_num("-4.56e-10", 3, true, 13), "-4.56e-10");

        // Test normal numbers with preserve scientific (should use sigfig)
        assert_eq!(format_if_num("1.23456", 3, true, 13), "1.23");
        assert_eq!(format_if_num("123.456", 3, true, 13), "123.");

        // Test without preserve scientific (should convert to decimal)
        assert_eq!(format_if_num("1.23e-7", 3, false, 13), "0.000000123");
    }

    #[test]
    fn test_format_if_num_max_decimal_width() {
        // Test auto-conversion based on decimal width
        // Very small number should be converted to scientific notation
        assert_eq!(format_if_num("0.000000123", 3, false, 8), "1.23e-7");

        // Large number should be converted to scientific notation
        assert_eq!(format_if_num("123456789012345", 3, false, 8), "1.23e14");

        // Normal number within threshold should stay decimal
        assert_eq!(format_if_num("3.14159", 3, false, 8), "3.14");

        // Test with higher threshold
        assert_eq!(format_if_num("0.000000123", 3, false, 15), "0.000000123");
    }

    #[test]
    fn test_format_if_num_combined_flags() {
        // Test both preserve_scientific and max_decimal_width together
        // Scientific notation input should be preserved regardless of width
        assert_eq!(format_if_num("1.23e-7", 3, true, 5), "1.23e-7");

        // Long decimal should be auto-converted even with preserve_scientific
        assert_eq!(format_if_num("0.000000123", 3, true, 8), "1.23e-7");
    }
}

