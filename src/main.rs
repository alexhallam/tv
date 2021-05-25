use csv;
use csv::ReaderBuilder;
use itertools::Itertools;
use owo_colors::OwoColorize;
use std::io::{self};
use structopt::StructOpt;
// Nord
// nord5 - white
// .truecolor(216, 222, 233)
// Red
// .truecolor(191, 97, 106)
// nord8 - light blue
// .truecolor(136, 192, 208)
// nord10 - dark blue
// .truecolor(94, 129, 172)
// .truecolor(191, 97, 106)

mod datatype;

#[derive(StructOpt)]
#[structopt(
    name = "tv",
    about = "Tidy Viewer (tv) is a csv pretty printer that uses column styling maximize viewer enjoyment.
"
)]
struct Cli {
//    #[structopt(parse(from_os_str),short = "i", long = "input")]
//    input_csv_file_path: std::path::PathBuf,
//    #[structopt(short = "c",long = "col_types")]
//    column_types_override: String,
}

fn infer_type_from_string(text: &str) -> &str {
    if datatype::is_time(text) {
        return "<tst>";
    } else if datatype::is_integer(text) {
        return "<int>";
    } else if datatype::is_date_time(text) {
        return "<tdt>";
    } else if datatype::is_date(text) {
        return "<tsd>";
    } else if datatype::is_double(text) {
        return "<dbl>";
    } else if datatype::is_logical(text) {
        return "<lgl>";
    } else {
        return "<chr>";
    }
}

fn trunc_strings(vec_col: Vec<&str>, width: usize) -> Vec<String> {
    let ellipsis = '\u{2026}'.to_string();
    let v = vec_col
        .into_iter()
        .map(String::from)
        .map(|string| format_if_na(&string))
        .map(|mut string| {
            if string.len() > width {
                string.truncate(width-1);
                [string, ellipsis.to_string()].join(" ")
            } else {
                let l = string.len();
                let add_space = width-l+1;
                let owned_string: String = string.to_owned();
                let borrowed_string: &str = &" ".repeat(add_space);
                //[string, owned_string].join(borrowed_string)
                [string, "".to_string()].join(borrowed_string)
            }
        })
        .collect::<Vec<String>>();
    return v;
}
fn header_len(vec_col: Vec<String>) -> Vec<usize> {
    let v = vec_col
        .into_iter()
        .map(String::from)
        .map(|mut string| {string.len()})
        .collect::<Vec<usize>>();
    return v;
}
fn header_len_str(vec_col: Vec<&str>) -> Vec<usize> {
    let v = vec_col
        .into_iter()
        .map(String::from)
        .map(|mut string| {string.len()})
        .collect::<Vec<usize>>();
    return v;
}
fn format_if_na(text: &String) -> String {
    let s = datatype::is_na(text);
        // todo add repeat strings for NA
    let missing_string_value: String = "NA".to_string();
    let string: String = if s {
        missing_string_value
    } else {
        text.to_string()
    };
    return string;
}
fn float_has_point(text: &String) -> bool {
    let lgl: bool = text.contains(".");
    return lgl;
}
fn get_decimal_len(text: &String) -> usize {
    // if number is 1 as oppose to 1.0 then return 0
    let width: usize = if float_has_point(text) {
        text.split(".").collect::<Vec<&str>>()[1].len() + 1
    } else {
        0
    };
    return width;
}
fn get_left_decimal_len(text: &String) -> usize {
    // gets len of whole numbers to the left of the decimal
    // if number is 1 as oppose to 1.0 then return 0
    let width: usize = if float_has_point(text) {
        text.split(".").collect::<Vec<&str>>()[0].len()
    } else {
        text.len()
    };
    return width;
}
fn float_pad(text: &String, max_width: usize) -> String {
    let width = get_decimal_len(&text);
    let whole_number_width = get_left_decimal_len(&text);
    //todo pass width as arg
    //let width_to_append: usize = (max_width + width + whole_number_width + 1) - width;
    let width_to_append: usize = (max_width + width + whole_number_width) - whole_number_width - 1;
    //let width_to_append: usize = width + whole_number_width + max_width;
    let f = format!("{:>width$}", text, width = width_to_append).to_string();
    return f;
}
fn float_format(text: &String, max_width: usize) -> String {
    let is_na = datatype::is_na(&text);
    let string: String = if is_na {
        format_if_na(text)
    } else {
        float_pad(text, max_width)
    };
    return string;
}
fn get_col_data_type(col: Vec<&str>) -> &str {
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

fn main() {
    //let args = Cli::from_args();
    //   colname reader
    let mut r = ReaderBuilder::new()
        .has_headers(false)
        .from_reader(io::stdin());
    let rdr = r
        .records()
        .into_iter()
        .map(|x| x.expect("a csv record"))
        .collect::<Vec<_>>();

    let cols: usize = rdr[0].len();
    let rows: usize = rdr.len();

    // csv gets records in rows. This makes them cols
    let mut v: Vec<Vec<&str>> = vec![vec!["#"; rows as usize]; cols as usize];
    for col in 0..cols {
        for row in 0..rows {
            v[col][row] = &rdr[row].get(col).unwrap();
        }
    }

    // make datatypes vector
    let mut vec_datatypes: Vec<&str> = vec!["#"; cols as usize];
    for i in 0..cols {
        vec_datatypes[i] = get_col_data_type(v[i].clone());
    }

    // vector of formatted values
    let mut vf: Vec<Vec<String>> = vec![vec!["#".to_string(); rows as usize]; cols as usize];

    // get max width in columns
    let mut col_largest_width = Vec::new();
    for i in 0..cols{
        let size:usize = header_len_str(v[i].clone()).into_iter().max().unwrap();
        col_largest_width.push(size);
    }

    // format datatypes spaces 
    let mut vec_format_datatypes: Vec<_> = vec!["#"; cols as usize];
    //for i in 0..cols {
    //    let add_space = col_largest_width[i] - vec_datatypes[i].len();
    //    let borrowed_string = " ".repeat(add_space);
    //    let string = vec_datatypes[i].to_string();
    //}

    // make vector of formatted values
    for i in 0..cols{
        if vec_datatypes[i] == "<chr>"{
        //vf[i] = (v[i].clone(),col_largest_width[i]);
        vf[i] = trunc_strings(v[i].clone(),col_largest_width[i]);
        }else if vec_datatypes[i] == "<dbl>"{
        vf[i] = trunc_strings(v[i].clone(),col_largest_width[i]);
        //vf[i] = prep_dbl(v[i].clone());
        }else{
        vf[i] = trunc_strings(v[i].clone(),col_largest_width[i]);
        }
    }

    println!();
    let mut vp: Vec<Vec<String>> = vec![vec!["#".to_string(); cols as usize]; rows as usize];
    for col in 0..cols{
        for row in 0..rows{
            vp[row][col] = vf[col].get(row).unwrap().to_string();
        }
    }

    // prep doubles
    fn prep_dbl(vec_dbl: Vec<&str>) -> Vec<String>{
    let vec_len = vec_dbl
        .clone()
        .into_iter()
        .map(String::from)
        .map(|string| get_decimal_len(&string))
        .collect::<Vec<usize>>();
    let max_len: &usize = vec_len.iter().max().unwrap();
    let dbl = vec_dbl
        .clone()
        .into_iter()
        .map(String::from)
        .map(|string| float_format(&string, *max_len))
        .collect::<Vec<String>>();
    return dbl
    }

    let meta_text = "tv dim:";
    let div = "x";
    // meta
    print!("{: <6}", "");
    println!(
        "{} {} {} {}",
        meta_text.truecolor(143, 188, 187),
        (rows - 1).truecolor(143, 188, 187),
        div.truecolor(143, 188, 187),
        cols.truecolor(143, 188, 187),
    );
    // header
    print!("{: <6}", "");
    for col in 0..cols{
        let text = vp[0].get(col).unwrap().to_string();
        print!("{}",text.truecolor(216, 222, 233).bold());
    }
    println!();
    // datatypes
    //print!("{: <6}", "");
    //for col in 0..cols{
    //    let add_space = vec_datatypes[col].len() - col_largest_width[col];
    //    let mut owned_string: String = vec_datatypes[col].to_string();
    //    let borrowed_string: &str = &" ".repeat(add_space);
    //    owned_string.push_str(borrowed_string);
    //    print!("{}",owned_string.truecolor(143, 188, 187).bold());
    //}
    println!();
    for row in 1..rows{
        print!("{: <6}",(row).truecolor(143, 188, 187).dimmed());
        for col in 0..cols{
                let text = vp[row].get(col).unwrap().to_string();
                print!("{}",
                    if datatype::is_na_string_padded(vp[row].get(col).unwrap().to_string()){
                        text.truecolor(94, 129, 172)
                    }else{
                        text.truecolor(216, 222, 233)
                    }
                    );
        }
        println!();
    }

} // end main

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_logical() {
        assert_eq!(datatype::is_logical("T"),true);
        assert_eq!(datatype::is_logical("t"),true);
        assert_eq!(datatype::is_logical("F"),true);
        assert_eq!(datatype::is_logical("f"),true);
        assert_eq!(datatype::is_logical("TRUE"),true);
        assert_eq!(datatype::is_logical("FALSE"),true);
        assert_eq!(datatype::is_logical("True"),true);
        assert_eq!(datatype::is_logical("False"),true);
        assert_eq!(datatype::is_logical("true"),true);
        assert_eq!(datatype::is_logical("false"),true);
    }
    #[test]
    fn test_is_na() {
        assert_eq!(datatype::is_na(&"".to_string()),true);
        assert_eq!(datatype::is_na(&"NA".to_string()),true);
        assert_eq!(datatype::is_na(&"missing".to_string()),true);
        assert_eq!(datatype::is_na(&"na".to_string()),true);
    }
}
