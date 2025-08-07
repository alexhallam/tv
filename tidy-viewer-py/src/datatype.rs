use lazy_static::lazy_static;
use regex::Regex;
use std::str::FromStr;
use unicode_truncate::UnicodeTruncateStr;
use unicode_width::UnicodeWidthStr;



mod sigfig;

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

/// Format a column of strings using the exact logic from original TV
pub fn format_strings(
    vec_col: &[&str],
    lower_column_width: usize,
    upper_column_width: usize,
    sigfig: u8,
    preserve_scientific: bool,
    max_decimal_width: usize,
) -> Vec<String> {
    let ellipsis = '\u{2026}';

    let strings_and_fracts: Vec<(String, usize, usize)> = vec_col
        .iter()
        .map(|&string| format_if_na(string))
        .map(|string| format_if_num(&string, sigfig as i64, preserve_scientific, max_decimal_width))
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

/// Calculate column width using the original TV logic
pub fn calculate_column_width(
    column: &[String],
    min_width: usize,
    max_width: usize,
) -> usize {
    let max_content_width = column
        .iter()
        .map(|s| UnicodeWidthStr::width(s.as_str()))
        .max()
        .unwrap_or(0);
    
    max_content_width.clamp(min_width, max_width)
}

