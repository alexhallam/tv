use csv;
use itertools::Itertools;
use owo_colors::OwoColorize;
use std::io;
use structopt::StructOpt;

mod datatype;

/// Search for a pattern in a file and display the lines that contain it.
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
        return "time";
    } else if datatype::is_integer(text) {
        return "int";
    } else if datatype::is_date_time(text) {
        return "DT";
    } else if datatype::is_double(text) {
        return "double";
    } else if datatype::is_logical(text) {
        return "logical";
    } else {
        return "character";
    }
}

fn trunc_strings(vec_col: Vec<&str>, width: usize) -> Vec<String> {
    let ellipsis = '\u{2026}'.to_string();
    let v = vec_col
        .into_iter()
        .map(String::from)
        .map(|mut string| {
            if string.len() > width {
                string.truncate(width);
                [string, ellipsis.to_string()].join("")
            } else {
                string.truncate(width);
                string
            }
        })
        .map(|string| format_if_na(&string))
        .collect::<Vec<String>>();
    return v;
}
fn format_if_na(text: &String) -> String {
    let s = datatype::is_na(&text);
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
    //   let args = Cli::from_args();
    let rdr = csv::Reader::from_reader(io::stdin())
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
    //println!("{:?}", vec_datatypes);

    // prep doubles
    let vec_len = v[1]
        .clone()
        .into_iter()
        .map(String::from)
        .map(|string| get_decimal_len(&string))
        .collect::<Vec<usize>>();

    let max_len: &usize = vec_len.iter().max().unwrap();
    let dbl = v[1]
        .clone()
        .into_iter()
        .map(String::from)
        .map(|string| float_format(&string, *max_len))
        .collect::<Vec<String>>();

    // prep characters
    let chr = trunc_strings(v[0].clone(), 6); //max_len

    let meta_text = "tv dim:";
    let div = "x";
    println!(
        "\t{} {} {} {}",
        meta_text.truecolor(143, 188, 187).dimmed(),
        rows.truecolor(143, 188, 187).dimmed(),
        div.truecolor(143, 188, 187).dimmed(),
        cols.truecolor(143, 188, 187).dimmed()
    );
    println!(
        "\t{} {}",
        "<pillar>".truecolor(129, 161, 193),
        "<pillar>".truecolor(129, 161, 193)
    );
    println!(
        "\t{}\t {}",
        "<char>".truecolor(143, 188, 187).dimmed(),
        "<dbl>".truecolor(143, 188, 187).dimmed()
    );
    for i in 0..rows {
        if datatype::is_na(&chr[i]) & datatype::is_na(&dbl[i]) {
            println!(
                "\t{}\t {}",
                chr[i].truecolor(180, 142, 173),
                dbl[i].truecolor(180, 142, 173)
            );
        } else if datatype::is_na(&chr[i]) & !datatype::is_na(&dbl[i]) {
            println!(
                "\t{}\t {}",
                chr[i].truecolor(180, 142, 173),
                dbl[i].truecolor(240, 248, 255)
            );
        } else if datatype::is_na(&dbl[i]) & !datatype::is_na(&chr[i]) {
            println!(
                "\t{}\t {}",
                chr[i].truecolor(240, 248, 255),
                dbl[i].truecolor(180, 142, 173)
            );
        } else {
            println!(
                "\t{}\t {}",
                chr[i].truecolor(240, 248, 255),
                dbl[i].truecolor(240, 248, 255)
            );
        }
    }
}



//#[cfg(test)]
//mod tests {
//    #[test]
//    fn test_is_logical() {
//        mod datatype;
//        assert_eq!(datatype::is_logical("T"),true);
//    }
//}
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
