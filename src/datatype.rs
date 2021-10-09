use itertools::Itertools;
use lazy_static::lazy_static;
use regex::Regex;
use std::str::FromStr;
use unicode_truncate::UnicodeTruncateStr;

mod sigfig;

/// Represents the type of a value.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ValueType {
    Boolean,
    Integer,
    Double,
    Date,
    Time,
    DateTime,
    Character,
    /// A missing value.
    Na,
}

pub fn is_logical(text: &str) -> bool {
    // col_logical -l, T,F,TRUE,FALSE,True,False,true,false,t,f,1,0
    lazy_static! {
        static ref R: Regex =
            Regex::new(r"^true$|^false$|^t$|^f$|TRUE$|^FALSE$|^T$|^F$|^True|^False|^1$|^0$")
                .unwrap();
    }
    R.is_match(text)
}

pub fn is_integer(text: &str) -> bool {
    //let integer = "5";
    lazy_static! {
        static ref R: Regex = Regex::new(r"^([+-]?[1-9][0-9]*|0)$").unwrap();
    }
    R.is_match(text)
}

pub fn is_double(text: &str) -> bool {
    f64::from_str(text).is_ok()
}

pub fn is_time(text: &str) -> bool {
    //let time = "11:59:37 UTC";
    //https://stackoverflow.com/a/25873711
    lazy_static! {
        static ref R: Regex =
            Regex::new(r"^(?:[01][0-9]|2[0123]):(?:[012345][0-9]):(?:[012345][0-9])$").unwrap();
    }
    R.is_match(text)
}

pub fn is_date(text: &str) -> bool {
    lazy_static! {
        static ref R: Regex = Regex::new(r"\d{4}-\d{2}-\d{2}").unwrap();
    }
    R.is_match(text)
}

pub fn is_date_time(text: &str) -> bool {
    //let datetime = "2020-10-09 11:59:37 UTC";
    //https://stackoverflow.com/a/25873711
    lazy_static! {
        static ref R: Regex =
            Regex::new(r"^(?:[01][0-9]|2[0123]):(?:[012345][0-9]):(?:[012345][0-9])").unwrap();
    }
    R.is_match(text)
}

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
            r"^$|^(?:N(?:(?:(?:one|AN|a[Nn]|/A)|[Aa])|ull)|n(?:ull|an?|/a?)|(?:missing))\s*$"
        )
        .unwrap();
    }
    R.is_match(text)
}

// utilities

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

pub fn format_strings(
    vec_col: &[&str],
    lower_column_width: usize,
    upper_column_width: usize,
) -> Vec<String> {
    let ellipsis = '\u{2026}';

    let strings_and_fracts: Vec<(String, usize, usize)> = vec_col
        .iter()
        .map(|&string| format_if_na(string))
        .map(|string| format_if_num(&string))
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
            }
            let len = string.chars().count();
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
                let spacer: &str = &" ";
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

pub fn format_if_num(text: &str) -> String {
    if let Ok(val) = text.parse::<f64>() {
        sigfig::DecimalSplits { val, sigfig: 3 }.final_string()
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
    match bytes.len() {
        1 => Ok(bytes[0]),
        _ => Err(format!(
            "expected one byte as a delimiter, got {} bytes (\"{}\")",
            bytes.len(),
            src
        )),
    }
}
