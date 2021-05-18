use regex::Regex;
use lazy_static::lazy_static;


pub fn is_logical(text: &str) -> bool {
    // col_logical -l, T,F,TRUE,FALSE,True,False,true,false,t,f,1,0
    lazy_static! {
        static ref R: Regex = Regex::new(r"^true$|^false$|^t$|^f$|TRUE$|^FALSE$|^T$|^F$|^True|^False").unwrap();
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
        static ref R: Regex = Regex::new(r"[+-]?[0-9]+(\.[0-9]+)?([Ee][+-]?[0-9]+)?").unwrap();
    }
    let lgl = R.is_match(&text);
    return lgl;
}
pub fn is_time(text: &str) -> bool {
    //let time = "11:59:37 UTC";
    //https://stackoverflow.com/a/25873711
    lazy_static! {
        static ref R: Regex = Regex::new(r"^(?:[01][0-9]|2[0123]):(?:[012345][0-9]):(?:[012345][0-9])$").unwrap();
    }
    let lgl = R.is_match(&text);
    return lgl;
}
pub fn is_date(text: &str) -> bool{
    lazy_static! {
        static ref R: Regex = Regex::new(r"\d{4}-\d{2}-\d{2}").unwrap();
    }
    let lgl = R.is_match(&text);
    return lgl;
    //https://mkyong.com/regular-expressions/how-to-validate-date-with-regular-expression/
}
pub fn is_date_time(text: &str) -> bool {
    //let datetime = "2020-10-09 11:59:37 UTC";
    //https://stackoverflow.com/a/25873711
    lazy_static! {
        static ref R: Regex = Regex::new(r"^(?:[01][0-9]|2[0123]):(?:[012345][0-9]):(?:[012345][0-9])").unwrap();
    }
    let lgl = R.is_match(&text);
    return lgl;
}

pub fn is_na(text: &String) -> bool {
    lazy_static! {
        static ref R: Regex = Regex::new(r"^$|^(?:N(?:(?:(?:one|AN|a[Nn]|/A)|[Aa])|ull)|n(?:ull|an?|/a?)|(?:missing))$").unwrap();
    }
    let lgl = R.is_match(&text);
    return lgl;
}

pub fn is_na_string(text: String) -> bool {
    lazy_static! {
        static ref R: Regex = Regex::new(r"^$|^(?:N(?:(?:(?:one|AN|a[Nn]|/A)|[Aa])|ull)|n(?:ull|an?)|(?:missing))$").unwrap();
    }
    let lgl = R.is_match(&text);
    return lgl;
}

