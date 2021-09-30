use itertools::Itertools;
use lazy_static::lazy_static;
use regex::Regex;
use unicode_truncate::UnicodeTruncateStr;

mod sigfig;

pub fn is_logical(text: &str) -> bool {
    // col_logical -l, T,F,TRUE,FALSE,True,False,true,false,t,f,1,0
    lazy_static! {
        static ref R: Regex =
            Regex::new(r"^true$|^false$|^t$|^f$|TRUE$|^FALSE$|^T$|^F$|^True|^False|^1$|^0$").unwrap();
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
    lazy_static! {
        // for exp values, but seems to match other strings also
        //static ref R: Regex = Regex::new(r"[+-]?[0-9]+(\.[0-9]+)?([Ee][+-]?[0-9]+)?").unwrap();
        static ref R: Regex = Regex::new(r"^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$").unwrap();

    }
    R.is_match(text)
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

pub fn infer_type_from_string(text: &str) -> &'static str {
    if is_time(text) {
        "<tst>"
    } else if is_logical(text) {
        "<lgl>"
    } else if is_integer(text) {
        "<int>"
    } else if is_date_time(text) {
        "<tdt>"
    } else if is_date(text) {
        "<tsd>"
    } else if is_double(text) {
        "<dbl>"
    } else {
        "<chr>"
    }
}

pub fn trunc_strings(vec_col: &[&str], width: usize) -> Vec<String> {
    let ellipsis = '\u{2026}';
    vec_col
        .iter()
        .map(|&string| format_if_na(string))
        // add
        .map(|string| format_if_num(&string))
        .map(|string| {
            let len = string.chars().count();
            if len > width {
                let (rv, _) = string.unicode_truncate(width - 1);
                let spacer: &str = &" ";
                let string_and_ellipses = [rv.to_string(), ellipsis.to_string()].join("");
                [string_and_ellipses, spacer.to_string()].join("")
            } else {
                let add_space = width - len + 1;
                let borrowed_string: &str = &" ".repeat(add_space);
                [string, "".to_string()].join(borrowed_string)
            }
        })
        .collect()
}

pub fn header_len_str(vec_col: &[&str]) -> Vec<usize> {
    vec_col
        .iter()
        .map(|&string| string.chars().count())
        .collect::<Vec<usize>>()
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

fn format_if_num(text: &str) -> String {
    if is_double(text) {
        let xf = text.to_string().parse::<f64>().unwrap();
        let x = sigfig::DecimalSplits { val: xf, sigfig: 3 };
        let list = sigfig::DecimalSplitsList {
            val: x.value(),
            sigfig: x.sig_fig(),
            neg: x.neg(),
            lhs: x.lhs(),
            rhs: x.rhs(),
            dec: x.dec(),
            final_string: x.final_string(),
            sigfig_index_lhs_or_rhs: x.sigfig_index_lhs_or_rhs(),
            sigfig_index_from: x.sigfig_index_from(),
            sigfig_index_to: x.sigfig_index_to(),
        };
        list.final_string
    } else {
        text.to_string()
    }
}

pub fn get_col_data_type(col: &[&str]) -> &'static str {
    // counts the frequency of the datatypes in the column
    // returns the most frequent. todo-make na not count and handle ties
    col.iter()
        .map(|x| infer_type_from_string(x))
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
