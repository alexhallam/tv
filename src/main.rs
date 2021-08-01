use csv;
use csv::ReaderBuilder;
use owo_colors::OwoColorize;
use std::io::{self};
use structopt::StructOpt;
mod datatype;
mod term_attr;

#[derive(Debug, StructOpt)]
#[structopt(
    name = "tv",
    about = "Tidy Viewer (tv) is a csv pretty printer that uses column styling to maximize viewer enjoyment.✨✨📺✨✨\n
    Example Usage:
    wget https://raw.githubusercontent.com/tidyverse/ggplot2/master/data-raw/diamonds.csv
    cat diamonds.csv | head -n 35 | tv"
)]
struct Cli {
    #[structopt(
        short = "c",
        long = "color",
        default_value = "1",
        help = "There are 4 colors (1)nord, (2)one_dark, (3)gruvbox, and (4)dracula. An input of (0)bw will remove color properties. Note that colors will make it difficult to pipe output to other utilities"
    )]
    color: usize,
    #[structopt(
        short = "t",
        long = "title",
        default_value = "NA",
        help = "Add a title to your tv. Example 'Test Data'"
    )]
    title: String,
    #[structopt(
        short = "f",
        long = "footer",
        default_value = "NA",
        help = "Add a title to your tv. Example 'footer info'"
    )]
    footer: String,
    #[structopt(
        short = "n",
        long = "number of rows to output",
        default_value = "25",
        help = "Show how many rows to display. Default 25"
    )]
    row_display: usize,
}

fn main() {
    let opt = Cli::from_args();
    let color_option = opt.color;
    let title_option = opt.title;
    let footer_option = opt.footer;
    let row_display_option = opt.row_display;
    // nord
    let nord_meta_color = (143, 188, 187);
    let nord_header_color = (94, 129, 172);
    let nord_std_color = (216, 222, 233);
    let nord_na_color = (191, 97, 106);
    // one dark
    let one_dark_meta_color = (152, 195, 121);
    let one_dark_header_color = (97, 175, 239);
    let one_dark_std_color = (171, 178, 191);
    let one_dark_na_color = (224, 108, 117);
    //// gruv
    let gruvbox_meta_color = (184, 187, 38);
    let gruvbox_header_color = (215, 153, 33);
    let gruvbox_std_color = (235, 219, 178);
    let gruvbox_na_color = (204, 36, 29);
    //// dracula
    let dracula_meta_color = (98, 114, 164);
    let dracula_header_color = (80, 250, 123);
    let dracula_std_color = (248, 248, 242);
    let dracula_na_color = (255, 121, 198);

    let (meta_color, header_color, std_color, na_color) = match color_option {
        1 => (
            nord_meta_color,
            nord_header_color,
            nord_std_color,
            nord_na_color,
        ),
        2 => (
            one_dark_meta_color,
            one_dark_header_color,
            one_dark_std_color,
            one_dark_na_color,
        ),
        3 => (
            gruvbox_meta_color,
            gruvbox_header_color,
            gruvbox_std_color,
            gruvbox_na_color,
        ),
        4 => (
            dracula_meta_color,
            dracula_header_color,
            dracula_std_color,
            dracula_na_color,
        ),
        _ => (
            nord_meta_color,
            nord_header_color,
            nord_std_color,
            nord_na_color,
        ),
    };

    //   colname reader
    let mut r = ReaderBuilder::new()
        .has_headers(false)
        .from_reader(io::stdin());
    let rdr = r
        .records()
        .into_iter()
        //.take(row_display_option + 1)
        .map(|x| x.expect("a csv record"))
        .collect::<Vec<_>>();

    let cols: usize = rdr[0].len();
    let rows: usize = if rdr.len() > row_display_option + 1 {row_display_option + 1}else{rdr.len()};
    let rows_in_file: usize = rdr.len();
    let rows_remaining: usize = rows_in_file - rows;
    let ellipsis = '\u{2026}'.to_string();
    let row_remaining_text: String = format!("{} with {} more rows", ellipsis, rows_remaining);

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
        vec_datatypes[i] = datatype::get_col_data_type(v[i].clone());
    }

    // vector of formatted values
    let mut vf: Vec<Vec<String>> = vec![vec!["#".to_string(); rows as usize]; cols as usize];

    // get max width in columns
    let mut col_largest_width = Vec::new();
    for i in 0..cols {
        let size: usize = datatype::header_len_str(v[i].clone())
            .into_iter()
            .max()
            .unwrap();
        col_largest_width.push(size);
    }

    // format datatypes spaces
    // let mut vec_format_datatypes: Vec<_> = vec!["#"; cols as usize];
    //for i in 0..cols {
    //    let add_space = col_largest_width[i] - vec_datatypes[i].len();
    //    let borrowed_string = " ".repeat(add_space);
    //    let string = vec_datatypes[i].to_string();
    //}

    // make vector of formatted values
    for i in 0..cols {
        if vec_datatypes[i] == "<chr>" {
            vf[i] = datatype::trunc_strings(v[i].clone(), col_largest_width[i]);
        } else if vec_datatypes[i] == "<dbl>" {
            vf[i] = datatype::trunc_strings(v[i].clone(), col_largest_width[i]);
        } else {
            vf[i] = datatype::trunc_strings(v[i].clone(), col_largest_width[i]);
        }
    }

    println!();
    let mut vp: Vec<Vec<String>> = vec![vec!["#".to_string(); cols as usize]; rows as usize];
    for col in 0..cols {
        for row in 0..rows {
            vp[row][col] = vf[col].get(row).unwrap().to_string();
        }
    }

    // how wide will the print be?
    //fn get_num_cols_to_print(cols: usize, vp: Vec<Vec<String>>, term_tuple: (u16, u16)) -> usize {
    //    let mut j = format!("{: <6}", "");
    //    for col in 0..cols {
    //        let text = vp[0].get(col).unwrap().to_string();
    //        j.push_str(&text);
    //        let total_width = j.chars().count();
    //        let term_width = term_tuple.1 as usize;
    //        if total_width < term_width {
    //            println!("{:?}", col);
    //            return col;
    //        }
    //    }
    //    return 999;
    //}

    //let num_cols_to_print = get_num_cols_to_print(cols, vp.clone(), term_tuple);
    //println!("{:?}", num_cols_to_print);

    if color_option < 1 {
        let meta_text = "tv dim:";
        let div = "x";
        print!("{: <6}", "");
        println!("{} {} {} {}", meta_text, (rows - 1), div, cols);
        if !datatype::is_na(&title_option.to_string()) {
            print!("{: <6}", "");
            println!("{}", title_option);
        }
        print!("{: <6}", "");
        for col in 0..cols {
            let text = vp[0].get(col).unwrap().to_string();
            print!("{}", text);
        }
        println!();
        for row in 1..rows {
            print!("{: <6}", (row));
            for col in 0..cols {
                let text = vp[row].get(col).unwrap().to_string();
                let tmp;
                print!(
                    "{}",
                    if datatype::is_na_string_padded(vp[row].get(col).unwrap().to_string()) {
                        tmp = text;
                        tmp
                    } else {
                        tmp = text;
                        tmp
                    }
                );
            }
            println!();
        }
        if !datatype::is_na(&footer_option.to_string()) {
            print!("{: <6}", "");
            println!("{}", footer_option);
        }

        println!();
    }
    //end if
    else {
        // color
        let meta_text = "tv dim:";
        let div = "x";
        print!("{: <6}", "");
        println!(
            "{} {} {} {}",
            meta_text.truecolor(meta_color.0, meta_color.1, meta_color.2),
            (rows_in_file - 1).truecolor(meta_color.0, meta_color.1, meta_color.2),
            div.truecolor(meta_color.0, meta_color.1, meta_color.2),
            cols.truecolor(meta_color.0, meta_color.1, meta_color.2),
        );
        // title
        if !datatype::is_na(&title_option.to_string()) {
            print!("{: <6}", "");
            println!(
                "{}",
                title_option
                    .truecolor(meta_color.0, meta_color.1, meta_color.2)
                    .underline()
                    .bold()
            );
        }

        // header
        print!("{: <6}", "");
        for col in 0..cols {
            let text = vp[0].get(col).unwrap().to_string();
            print!(
                "{}",
                text.truecolor(header_color.0, header_color.1, header_color.2)
                    .bold()
            );
        }
        //println!();
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
        for row in 1..rows {
            print!(
                "{: <6}",
                (row).truecolor(meta_color.0, meta_color.1, meta_color.2)
            );
            for col in 0..cols {
                let text = vp[row].get(col).unwrap().to_string();
                let tmp;
                print!(
                    "{}",
                    if datatype::is_na_string_padded(vp[row].get(col).unwrap().to_string()) {
                        tmp = text.truecolor(na_color.0, na_color.1, na_color.2);
                        tmp
                    } else {
                        tmp = text.truecolor(std_color.0, std_color.1, std_color.2);
                        tmp
                    }
                );
            }
            println!();
        }

        // additional row info
        
        if rows_remaining > 0 {
            print!("{: <6}", "");
            println!(
                "{}",
                row_remaining_text.truecolor(meta_color.0, meta_color.1, meta_color.2)
            );
        }


        // footer
        if !datatype::is_na(&footer_option.to_string()) {
            print!("{: <6}", "");
            println!(
                "{}",
                footer_option.truecolor(meta_color.0, meta_color.1, meta_color.2)
            );
        }

        println!();
    } //end color else
} // end main

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_logical() {
        assert_eq!(datatype::is_logical("T"), true);
        assert_eq!(datatype::is_logical("t"), true);
        assert_eq!(datatype::is_logical("F"), true);
        assert_eq!(datatype::is_logical("f"), true);
        assert_eq!(datatype::is_logical("TRUE"), true);
        assert_eq!(datatype::is_logical("FALSE"), true);
        assert_eq!(datatype::is_logical("True"), true);
        assert_eq!(datatype::is_logical("False"), true);
        assert_eq!(datatype::is_logical("true"), true);
        assert_eq!(datatype::is_logical("false"), true);
    }
    #[test]
    fn test_is_na() {
        assert_eq!(datatype::is_na(&"".to_string()), true);
        assert_eq!(datatype::is_na(&"NA".to_string()), true);
        assert_eq!(datatype::is_na(&"missing".to_string()), true);
        assert_eq!(datatype::is_na(&"na".to_string()), true);
    }
}
