use csv;
use itertools::Itertools;
use owo_colors::OwoColorize;
use std::io::{self};
use structopt::StructOpt;
//use std::io::Write;
//use tabwriter::TabWriter;

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
        return "ts-t";
    } else if datatype::is_integer(text) {
        return "int";
    } else if datatype::is_date_time(text) {
        return "ts-dt";
    } else if datatype::is_date(text) {
        return "ts-d";
    } else if datatype::is_double(text) {
        return "dbl";
    } else if datatype::is_logical(text) {
        return "lgl";
    } else {
        return "char";
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
    // --dtype debug
    //println!("{:?}", vec_datatypes);

    let mut vf: Vec<Vec<String>> = vec![vec!["#".to_string(); rows as usize]; cols as usize];
   
    // make vector of formatted values
    for i in 0..cols{
        if vec_datatypes[i] == "char"{
     //   println!("{:?}",trunc_strings(v[i].clone(),6));
        vf[i] = trunc_strings(v[i].clone(),6);
        }else if vec_datatypes[i] == "dbl"{
      //  println!("{:?}",prep_dbl(v[i].clone()));
        vf[i] = prep_dbl(v[i].clone());
        }else{
      //  println!("{:?}",trunc_strings(v[i].clone(),6));
        vf[i] = trunc_strings(v[i].clone(),10);
        }
    }

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

    // printing
    let mut s = String::new();
    for i in 0..rows{
        let a = vp[i].join("\t").to_string() + "\n";
        s.push_str(&a);
    }
    // tab writter
    // let s_slice: &str = &s[..];  // take a full slice of the string
    // let mut tw = TabWriter::new(vec![]);
    // write!(&mut tw, "{}",s_slice).unwrap();
    // tw.flush().unwrap();
    // let tabbed_data = String::from_utf8(tw.into_inner().unwrap()).unwrap();
    // tab writter
    let meta_text = "tv dim:";
    let div = "x";
    println!(
        "\t{} {} {} {}",
        meta_text.truecolor(143, 188, 187),
        rows.truecolor(143, 188, 187),
        div.truecolor(143, 188, 187),
        cols.truecolor(143, 188, 187),
    );
    // put col headers here
    let vec_datatypes_joined = vec_datatypes.join(">\t<");
    println!("\t\t{}{}{}","<".truecolor(143, 188, 187).dimmed(),vec_datatypes_joined.truecolor(143, 188, 187).dimmed(),">".truecolor(143, 188, 187).dimmed());
//    println!("{}",tabbed_data.truecolor(143, 188, 187));
        for row in 0..rows{
                print!("\t{}\t",(row+1).truecolor(143, 188, 187).dimmed());
            for col in 0..cols{
                let text = vp[row].get(col).unwrap().to_string();
                print!("{}\t",
                    if datatype::is_na_string(vp[row].get(col).unwrap().to_string()){
                        text.truecolor(94, 129, 172)
                    }else{
                        text.truecolor(216, 222, 233)
                    }
                    );
        }
                println!();
    }


} // end main

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
