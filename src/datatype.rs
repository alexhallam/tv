use itertools::Itertools;
use lazy_static::lazy_static;
use regex::Regex;
mod sigfig;

pub fn is_logical(text: &str) -> bool {
    // col_logical -l, T,F,TRUE,FALSE,True,False,true,false,t,f,1,0
    lazy_static! {
        static ref R: Regex =
            Regex::new(r"^true$|^false$|^t$|^f$|TRUE$|^FALSE$|^T$|^F$|^True|^False").unwrap();
    }
    //let r = Regex::new(rgex).unwrap();
    let lgl = R.is_match(&text);
    return lgl;
}
pub fn is_integer(text: &str) -> bool {
    //let integer = "5";
    lazy_static! {
        static ref R: Regex = Regex::new(r"^([+-]?[1-9][0-9]*|0)$").unwrap();
    }
    let lgl = R.is_match(&text);
    return lgl;
}
pub fn is_double(text: &str) -> bool {
    lazy_static! {
        // for exp values, but seems to match other strings also
        //static ref R: Regex = Regex::new(r"[+-]?[0-9]+(\.[0-9]+)?([Ee][+-]?[0-9]+)?").unwrap();
        static ref R: Regex = Regex::new(r"^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$").unwrap();

    }
    let lgl = R.is_match(&text);
    return lgl;
}
pub fn is_time(text: &str) -> bool {
    //let time = "11:59:37 UTC";
    //https://stackoverflow.com/a/25873711
    lazy_static! {
        static ref R: Regex =
            Regex::new(r"^(?:[01][0-9]|2[0123]):(?:[012345][0-9]):(?:[012345][0-9])$").unwrap();
    }
    let lgl = R.is_match(&text);
    return lgl;
}
pub fn is_date(text: &str) -> bool {
    lazy_static! {
        static ref R: Regex = Regex::new(r"\d{4}-\d{2}-\d{2}").unwrap();
    }
    let lgl = R.is_match(&text);
    return lgl;
}
pub fn is_date_time(text: &str) -> bool {
    //let datetime = "2020-10-09 11:59:37 UTC";
    //https://stackoverflow.com/a/25873711
    lazy_static! {
        static ref R: Regex =
            Regex::new(r"^(?:[01][0-9]|2[0123]):(?:[012345][0-9]):(?:[012345][0-9])").unwrap();
    }
    let lgl = R.is_match(&text);
    return lgl;
}

pub fn is_na(text: &String) -> bool {
    lazy_static! {
        static ref R: Regex = Regex::new(
            r"^$|^(?:N(?:(?:(?:one|AN|a[Nn]|/A)|[Aa])|ull)|n(?:ull|an?|/a?)|(?:missing))$"
        )
        .unwrap();
    }
    let lgl = R.is_match(&text);
    return lgl;
}

//pub fn is_na_string(text: String) -> bool {
//    lazy_static! {
//        static ref R: Regex = Regex::new(
//            r"^$|^(?:N(?:(?:(?:one|AN|a[Nn]|/A)|[Aa])|ull)|n(?:ull|an?|/a?)|(?:missing))$"
//        )
//        .unwrap();
//    }
//    let lgl = R.is_match(&text);
//    return lgl;
//}

pub fn is_na_string_padded(text: String) -> bool {
    lazy_static! {
        static ref R: Regex = Regex::new(
            r"^$|^(?:N(?:(?:(?:one|AN|a[Nn]|/A)|[Aa])|ull)|n(?:ull|an?|/a?)|(?:missing))\s*$"
        )
        .unwrap();
    }
    let lgl = R.is_match(&text);
    return lgl;
}

// utilities

pub fn infer_type_from_string(text: &str) -> &str {
    if is_time(text) {
        return "<tst>";
    } else if is_integer(text) {
        return "<int>";
    } else if is_date_time(text) {
        return "<tdt>";
    } else if is_date(text) {
        return "<tsd>";
    } else if is_double(text) {
        return "<dbl>";
    } else if is_logical(text) {
        return "<lgl>";
    } else {
        return "<chr>";
    }
}

pub fn trunc_strings(vec_col: Vec<&str>, width: usize) -> Vec<String> {
    let ellipsis = '\u{2026}'.to_string();
    let v = vec_col
        .into_iter()
        .map(String::from)
        .map(|string| format_if_na(&string))
        // add
        .map(|string| format_if_num(&string))
        .map(|mut string| {
            if string.len() > width {
                string.truncate(width - 1);
                [string, ellipsis.to_string()].join(" ")
            } else {
                let l = string.len();
                let add_space = width - l + 1;
                let borrowed_string: &str = &" ".repeat(add_space);
                [string, "".to_string()].join(borrowed_string)
            }
        })
        .collect::<Vec<String>>();
    return v;
}
pub fn header_len_str(vec_col: Vec<&str>) -> Vec<usize> {
    let v = vec_col
        .into_iter()
        .map(String::from)
        .map(|string| string.len())
        .collect::<Vec<usize>>();
    return v;
}
pub fn format_if_na(text: &String) -> String {
    let s = is_na(text);
    // todo add repeat strings for NA
    let missing_string_value: String = "NA".to_string();
    let string: String = if s {
        missing_string_value
    } else {
        text.to_string()
    };
    return string;
}

fn format_if_num(text: &str) -> String {
    let s = is_double(text);
    if s {
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

pub fn get_col_data_type(col: Vec<&str>) -> &str {
    // counts the frequency of the datatypes in the column
    // returns the most frequent. todo-make na not count and handle ties
    let s = col
        .into_iter()
        .map(|x| infer_type_from_string(x))
        .group_by(|&x| x)
        .into_iter()
        .map(|(key, group)| (key, group.count()))
        .max_by_key(|&(_, count)| count)
        .unwrap()
        .0;
    return s;
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
