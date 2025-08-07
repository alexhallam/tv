use lazy_static::lazy_static;
use regex::Regex;
use std::str::FromStr;
use unicode_truncate::UnicodeTruncateStr;
use unicode_width::UnicodeWidthStr;

use crate::types::ValueType;

lazy_static! {
    static ref INTEGER_RE: Regex = Regex::new(r"^\s*([+-]?[1-9][0-9]*|0)\s*$").unwrap();
    static ref SCIENTIFIC_RE: Regex = Regex::new(r"^[+-]?[0-9]*\.?[0-9]+[eE][+-]?[0-9]+$").unwrap();
    static ref NEGATIVE_RE: Regex = Regex::new(r"^\s*-[0-9]*\.?[0-9]*\s*$").unwrap();
    static ref NA_RE: Regex = Regex::new(
        r"^$|^(?:N(?:(?:(?:one|AN|a[Nn]|/A)|[Aa])|ull)|n(?:ull|an?|/a?)|(?:missing))$"
    ).unwrap();
    static ref BOOLEAN_RE: Regex = 
        Regex::new(r"^true$|^false$|^t$|^f$|TRUE$|^FALSE$|^T$|^F$|^True|^False|^1$|^0$").unwrap();
}

pub fn is_integer(text: &str) -> bool {
    INTEGER_RE.is_match(text)
}

pub fn is_double(text: &str) -> bool {
    f64::from_str(text.trim()).is_ok()
}

pub fn is_scientific_notation(text: &str) -> bool {
    SCIENTIFIC_RE.is_match(text.trim())
}

pub fn is_negative_number(text: &str) -> bool {
    NEGATIVE_RE.is_match(text)
}

pub fn is_na(text: &str) -> bool {
    NA_RE.is_match(text)
}

pub fn is_boolean(text: &str) -> bool {
    BOOLEAN_RE.is_match(text)
}

pub fn get_value_type(text: &str) -> ValueType {
    if is_na(text) {
        ValueType::Na
    } else if is_boolean(text) {
        ValueType::Boolean
    } else if is_integer(text) {
        ValueType::Integer
    } else if is_double(text) {
        ValueType::Double
    } else {
        ValueType::Character
    }
}

/// Format a single string value based on column width constraints
pub fn format_string(
    text: &str,
    lower_column_width: usize,
    upper_column_width: usize,
    sigfig: u8,
    preserve_scientific: bool,
    max_decimal_width: usize,
) -> String {
    let value_type = get_value_type(text);
    
    match value_type {
        ValueType::Na => "NA".to_string(),
        ValueType::Boolean => text.to_string(),
        ValueType::Integer => text.trim().to_string(),
        ValueType::Double => {
            if preserve_scientific && is_scientific_notation(text) {
                text.trim().to_string()
            } else if let Ok(num) = f64::from_str(text.trim()) {
                format_float(num, sigfig, max_decimal_width)
            } else {
                text.to_string()
            }
        }
        ValueType::Character => {
            truncate_string(text, upper_column_width)
        }
        _ => text.to_string(),
    }
}

/// Format a float with significant figures
fn format_float(num: f64, sigfig: u8, max_decimal_width: usize) -> String {
    // Simple significant figures formatting
    let formatted = format!("{:.prec$}", num, prec = sigfig as usize);
    
    // Switch to scientific notation if too long
    if formatted.len() > max_decimal_width {
        format!("{:.prec$e}", num, prec = sigfig as usize)
    } else {
        formatted
    }
}

/// Truncate string to fit within column width
fn truncate_string(text: &str, max_width: usize) -> String {
    let width = UnicodeWidthStr::width(text);
    if width <= max_width {
        text.to_string()
    } else if max_width >= 3 {
        let truncated = text.unicode_truncate(max_width - 1);
        format!("{}…", truncated.0)
    } else {
        "…".to_string()
    }
}

/// Get the column data type by checking multiple values
pub fn get_col_data_type(column: &[&str]) -> ValueType {
    // Sample up to 100 non-NA values
    let sample: Vec<ValueType> = column
        .iter()
        .filter(|s| !is_na(s))
        .take(100)
        .map(|s| get_value_type(s))
        .collect();
    
    if sample.is_empty() {
        return ValueType::Na;
    }
    
    // If all are the same type, return that type
    let first_type = sample[0];
    if sample.iter().all(|t| *t == first_type) {
        return first_type;
    }
    
    // Mixed types default to Character
    ValueType::Character
}

/// Format a column of strings
pub fn format_strings(
    column: &[&str],
    lower_column_width: usize,
    upper_column_width: usize,
    sigfig: u8,
    preserve_scientific: bool,
    max_decimal_width: usize,
) -> Vec<String> {
    column
        .iter()
        .map(|s| format_string(
            s,
            lower_column_width,
            upper_column_width,
            sigfig,
            preserve_scientific,
            max_decimal_width,
        ))
        .collect()
}

/// Calculate the optimal column width based on content
pub fn calculate_column_width(
    column: &[String],
    min_width: usize,
    max_width: usize,
) -> usize {
    let max_content_width = column
        .iter()
        .map(|s| UnicodeWidthStr::width(s.as_str()))
        .max()
        .unwrap_or(min_width);
    
    max_content_width.clamp(min_width, max_width)
}