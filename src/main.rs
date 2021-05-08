use regex::Regex;
use owo_colors::OwoColorize;
use structopt::StructOpt;
extern crate csv;
use std::io;
use itertools::Itertools;

/// Search for a pattern in a file and display the lines that contain it.
#[derive(StructOpt)]
#[structopt(name = "tv", about = "Tidy Viewer (tv) uses column styling maximize viewing joy.")]
struct Cli {
//    #[structopt(parse(from_os_str),short = "i", long = "input")]
//    input_csv_file_path: std::path::PathBuf,
//    #[structopt(short = "c",long = "col_types")]
//    column_types_override: String,
}

fn main() {
 //   let args = Cli::from_args();
    let rdr = csv::Reader::from_reader(io::stdin())
        .records()
        .into_iter()
        .map(|x| x.expect("a csv record"))
        .collect::<Vec<_>>();

    // string to datatype inference
    fn is_logical(text: &str) -> bool{
    // col_logical -l, T,F,TRUE,FALSE,True,False,true,false,t,f,1,0
        let rgex = r"^true$|^false$|^t$|^f$|TRUE$|^FALSE$|^T$|^F$|^True|^False";
        let r = Regex::new(rgex).unwrap();
        let lgl = r.is_match(&text);
        return lgl
    }
    fn is_integer(text: &str) -> bool{
    //let integer = "5";
        let rgex = r"^([+-]?[1-9][0-9]*|0)$";
        let r = Regex::new(rgex).unwrap();
        let lgl = r.is_match(&text);
        return lgl
    }
    fn is_double(text: &str) -> bool{
    //let double = "0.01";
        //https://www.geeksforgeeks.org/check-given-string-valid-number-integer-floating-point-java-set-2-regular-expression-approach/
        let rgex = r"[+-]?\d+(\.\d+)?([Ee][+-]?\d+)?";
        let r = Regex::new(rgex).unwrap();
        let lgl = r.is_match(&text);
        return lgl
    }
    fn is_time(text: &str) -> bool{
    //let time = "11:59:37 UTC";
        //https://stackoverflow.com/a/25873711
        let rgex = r"^(?:[01]\d|2[0123]):(?:[012345]\d):(?:[012345]\d)$";
        let r = Regex::new(rgex).unwrap();
        let lgl = r.is_match(&text);
        return lgl
    }
    //fn is_date(text: &str) -> bool{
    //let date = "2020-01-01";
    //    //https://mkyong.com/regular-expressions/how-to-validate-date-with-regular-expression/
    //    return false 
    //}
    fn is_date_time(text: &str) -> bool{
    //let datetime = "2020-10-09 11:59:37 UTC";
        //https://stackoverflow.com/a/25873711
        let rgex = r"^(?:[01]\d|2[0123]):(?:[012345]\d):(?:[012345]\d)";
        let r = Regex::new(rgex).unwrap();
        let lgl = r.is_match(&text);
        return lgl
    }
    fn infer_type_from_string(text: &str) -> &str{
        if is_time(text) == true {
        return "time"
        }else if is_integer(text) == true {
        return "int"
        }else if is_date_time(text) == true {
        return "DT"
        }else if is_double(text) == true {
        return "double"
        }else if is_logical(text) == true {
        return "logical"
        }else {
        return "character"
        }
    }

    fn trunc_strings(vec_col: Vec<&str>, width: usize) -> Vec<String>{
        let ellipsis = '\u{2026}'.to_string();
        let v = vec_col
        .into_iter()
        .map(String::from)
        .map(|mut string| 
             if string.len() > width { string.truncate(width); [string, ellipsis.to_string()].join("") } 
             else {string.truncate(width); string})
        .map(|string| format_if_na(&string))
        .collect::<Vec<String>>();
        return v
    }
    fn is_na(text: &String) -> bool{
        //grex NA Null na null "" None Na N/A NaN NAN nan
        let rgex = r"^$|^(?:N(?:(?:(?:one|AN|a[Nn]|/A)|[Aa])|ull)|n(?:ull|an?)|(?:missing))$";
        let r = Regex::new(rgex).unwrap();
        let lgl = r.is_match(&text);
        return lgl
    }
    fn format_if_na(text: &String) -> String{
        let s = is_na(&text);
        let missing_string_value: String = "NA".to_string();
        let string: String = if s == true { missing_string_value } else {text.to_string()};
        return string
    }
    fn float_has_point(text: &String)-> bool{
        let lgl: bool = text.contains(".");
        return lgl
    }
    fn get_decimal_len(text: &String) -> usize{
        // if number is 1 as oppose to 1.0 then return 0
        let width: usize= if float_has_point(text) == true {text.split(".").collect::<Vec<&str>>()[1].len()+1} else{0};
        return width 
    }
    fn get_left_decimal_len(text: &String) -> usize{
        // gets len of whole numbers to the left of the decimal
        // if number is 1 as oppose to 1.0 then return 0
        let width: usize= if float_has_point(text) == true {text.split(".").collect::<Vec<&str>>()[0].len()} else{text.len()};
        return width 
    }
    //fn char_pad(text: &String, max_width: usize) -> String{
    //    let f = format!("{:>width$}", text, width = max_width).to_string();
    //    return f
    //}
    fn float_pad(text: &String, max_width: usize) -> String{
        let width = get_decimal_len(&text);
        let whole_number_width = get_left_decimal_len(&text);
        //todo pass width as arg
        //let width_to_append: usize = (max_width + width + whole_number_width + 1) - width;
        let width_to_append: usize = (max_width + width + whole_number_width) - whole_number_width - 1;
        //let width_to_append: usize = width + whole_number_width + max_width;
        let f = format!("{:>width$}", text, width = width_to_append).to_string();
        return f
    }
    fn float_format(text: &String, max_width: usize) -> String{
        let is_na = is_na(&text);
        let string: String = if is_na == true {format_if_na(text)} else {float_pad(text, max_width)};
        return string;
    }
    //let a = vec!["abc","abcde","abcdefgh","abcdefghijkl","","","abcdefghijklmnop"];
    //let b = vec!["0.0001","0.001","0.01","0.1","1","","100"];


    let cols:usize = rdr[0].len();
    let rows:usize = rdr.len();


    // function to return the data type of a single column
    //fn get_col_data_type(col: &csv::StringRecord){
    fn get_col_data_type(col: Vec<&str>) -> &str{
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

    // csv gets records in rows. This makes them cols
    let mut v:Vec<Vec<&str>> = vec![vec!["#"; rows as usize]; cols as usize];
    for col in 0..cols{
        for row in 0..rows{
            v[col][row] = &rdr[row].get(col).unwrap();
        }
    }

    // make datatypes vector
   let mut vec_datatypes: Vec<&str> = vec!["#"; cols as usize];
   for i in 0..cols{
    vec_datatypes[i] = get_col_data_type(v[i].clone());
    }
   println!("{:?}", vec_datatypes);

    // prep doubles
    let vec_len = v[1]
        .clone()
        .into_iter()
        .map(String::from)
        .map(|string| get_decimal_len(&string))
        .collect::<Vec<usize>>();

    let max_len:&usize = vec_len.iter().max().unwrap();
    let dbl = v[1].clone()
        .into_iter()
        .map(String::from)
        .map(|string| float_format(&string, *max_len))
        .collect::<Vec<String>>();

    // prep characters
    let chr = trunc_strings(v[0].clone(), 6);//max_len

    //println!("--debug----debug----debug----debug----debug----debug----debug----debug----debug----debug----debug--");
    //println!("original chars: {:?}",a.clone());
    //println!("original doubles: {:?}",b);
    //println!("original chars: {:?}",chr);
    //println!("original doubles: {:?}",dbl);
    //println!("--debug----debug----debug----debug----debug----debug----debug----debug----debug----debug----debug--");

    let meta_text = "tv dim:";
    let div = "x";
    println!("\t{} {} {} {}",meta_text.truecolor(143,188,187).dimmed(),
                            rows.truecolor(143,188,187).dimmed(), 
                            div.truecolor(143,188,187).dimmed(), 
                            cols.truecolor(143,188,187).dimmed());
    println!("\t{} {}", "<pillar>".truecolor(129,161,193), "<pillar>".truecolor(129,161,193));
    println!("\t{}\t {}", "<char>".truecolor(143,188,187).dimmed(), "<dbl>".truecolor(143,188,187).dimmed());
    for i in 0..rows{
        if is_na(&chr[i])&is_na(&dbl[i]){
        println!("\t{}\t {}",chr[i].truecolor(180,142,173),dbl[i].truecolor(180,142,173));
        }else if is_na(&chr[i])&!is_na(&dbl[i]){
        println!("\t{}\t {}",chr[i].truecolor(180,142,173),dbl[i].truecolor(240,248,255));
        }else if is_na(&dbl[i])&!is_na(&chr[i]){
        println!("\t{}\t {}",chr[i].truecolor(240,248,255),dbl[i].truecolor(180,142,173));
        }else{
        println!("\t{}\t {}",chr[i].truecolor(240,248,255),dbl[i].truecolor(240,248,255));
        }
    }

 //let vs = tv::StringType(dbl);
 //let vf = tv::StringType(chr);
 //println!("{:^} {:^}", vs, vf);

}
