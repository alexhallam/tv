use csv::{Reader, ReaderBuilder};
use owo_colors::OwoColorize;
use std::fs::File;
use std::io::{self, BufReader, Read};
use std::path::PathBuf;
use structopt::StructOpt;
mod datatype;
use crossterm::terminal::size;

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
        help = "Add a footer to your tv. Example 'footer info'"
    )]
    footer: String,
    #[structopt(
        short = "n",
        long = "number of rows to output",
        default_value = "25",
        help = "Show how many rows to display."
    )]
    row_display: usize,
    #[structopt(
        short = "l",
        long = "lower-column-width",
        default_value = "2",
        help = "The lower (minimum) width of columns. Must be 2 or larger."
    )]
    lower_column_width: usize,
    #[structopt(
        short = "u",
        long = "upper-column-width",
        default_value = "20",
        help = "The upper (maxiumum) width of columns."
    )]
    upper_column_width: usize,
    #[structopt(
        short = "s",
        long = "delimiter",
        default_value = ",",
        parse(try_from_str = datatype::parse_delimiter),
        help = "The delimiter separating the columns."
    )]
    delimiter: u8,
    //#[structopt(
    //    short = "sig",
    //    long = "sigfig",
    //    default_value = "3",
    //    help = "Significant Digits. Default 3. (Comming Soon!)"
    //)]
    //sigfig: usize,
    #[structopt(
        short = "d",
        long = "debug-mode",
        help = "Print object details to make it easier for the maintainer to find and resolve bugs."
    )]
    debug_mode: bool,

    #[structopt(name = "FILE", parse(from_os_str), help = "File to process")]
    file: Option<PathBuf>,
}

fn main() {
    let term_tuple = size().unwrap();

    //println!("rows {} cols {}", term_tuple.1, term_tuple.0);
    let opt = Cli::from_args();
    let color_option = opt.color;
    let title_option = &opt.title;
    let footer_option = &opt.footer;
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

    // user args
    let lower_column_width = if opt.lower_column_width < 2 {
        panic!("lower-column-width must be larger than 2")
    } else {
        opt.lower_column_width
    };
    let upper_column_width = if opt.upper_column_width <= lower_column_width {
        panic!("upper-column-width must be larger than lower-column-width")
    } else {
        opt.upper_column_width
    };
    //let sigfig = opt.sigfig;
    let debug_mode = opt.debug_mode;

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
    let reader_result = build_reader(&opt);
    let mut r = if let Ok(reader) = reader_result {
        reader
    } else {
        // We can safetly use unwrap, becouse if file in case when file is None
        // build_reader would return readeer created from stdin
        let path_buf = opt.file.unwrap();
        let path = path_buf.as_path();
        if let Some(path) = path.to_str() {
            eprintln!("Failed to open file: {}", path);
        } else {
            eprintln!("Failed to open file.")
        }
        return;
    };

    let rdr = r
        .records()
        .into_iter()
        //.take(row_display_option + 1)
        .map(|x| x.expect("a csv record"))
        .collect::<Vec<_>>();

    if debug_mode {
        println!("{:?}", "StringRecord");
        println!("{:?}", rdr);
    }

    let cols: usize = rdr[0].len();
    let rows: usize = rdr.len().min(row_display_option + 1);
    let rows_in_file: usize = rdr.len();
    let rows_remaining: usize = rows_in_file - rows;
    let ellipsis = '\u{2026}'.to_string();
    let row_remaining_text: String = format!("{} with {} more rows", ellipsis, rows_remaining);

    // csv gets records in rows. This makes them cols
    let mut v: Vec<Vec<&str>> = Vec::new(); //vec![vec!["#"; rows as usize]; cols as usize];
    for col in 0..cols {
        let column = rdr
            .iter()
            .take(rows)
            .map(|row| row.get(col).unwrap())
            .collect();
        v.push(column)
    }

    if debug_mode {
        println!("{:?}", "v");
        println!("{:?}", v);
    }

    if debug_mode {
        // make datatypes vector
        let mut vec_datatypes = Vec::with_capacity(cols);
        for column in &v {
            vec_datatypes.push(datatype::get_col_data_type(&column))
        }
        println!("{:?}", "vec_datatypes");
        println!("{:?}", vec_datatypes);
    }

    // vector of formatted values
    let mut vf: Vec<Vec<String>> = vec![vec!["#".to_string(); rows as usize]; cols as usize];

    // get max width in columns
    let mut col_largest_width = Vec::new();
    for column in &v {
        let size: usize = datatype::header_len_str(&column).into_iter().max().unwrap();
        col_largest_width.push(size);
    }
    if debug_mode {
        println!("{:?}", "col_largest_width");
        println!("{:?}", col_largest_width);
    }

    // column width must be between the specified sizes
    col_largest_width
        .iter_mut()
        .for_each(|width| *width = (*width).clamp(lower_column_width, upper_column_width));

    if debug_mode {
        println!("{:?}", "col_largest_width post-proc");
        println!("{:?}", col_largest_width);
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
        vf[i] = datatype::trunc_strings(&v[i], col_largest_width[i]);
    }
    if debug_mode {
        println!("{:?}", "Transposed Vector of Elements");
        println!("{:?}", v);
        println!("{:?}", "Formatted: Vector of Elements");
        println!("{:?}", vf);
    }

    println!();
    let mut vp = Vec::new();
    for r in 0..rows {
        let row = vf.iter().map(|col| col[r].to_string()).collect();
        vp.push(row);
    }

    // how wide will the print be?
    fn get_num_cols_to_print(cols: usize, vp: Vec<Vec<String>>, term_tuple: (u16, u16)) -> usize {
        let mut last = 0;
        let mut j = format!("{: <6}", "");
        for col in 0..cols {
            let text = vp[0].get(col).unwrap().to_string();
            j.push_str(&text);
            let total_width = j.chars().count();
            let term_width = term_tuple.0 as usize;
            if total_width > term_width {
                break;
            }
            last = col + 1;
        }
        last
    }

    let num_cols_to_print = get_num_cols_to_print(cols, vp.clone(), term_tuple);

    // color
    let meta_text = "tv dim:";
    let div = "x";
    print!("{: <6}", "");
    println!(
        "{} {} {} {}",
        meta_text.truecolor(meta_color.0, meta_color.1, meta_color.2),
        (rows_in_file - 1).truecolor(meta_color.0, meta_color.1, meta_color.2),
        div.truecolor(meta_color.0, meta_color.1, meta_color.2),
        (cols).truecolor(meta_color.0, meta_color.1, meta_color.2),
    );
    // title
    if !datatype::is_na(title_option) {
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
    //for col in 0..cols {
    for col in 0..num_cols_to_print {
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
    vp.iter()
        .enumerate()
        .take(rows)
        .skip(1)
        .for_each(|(i, row)| {
            print!(
                "{: <6}",
                i.truecolor(meta_color.0, meta_color.1, meta_color.2)
            );
            //for col in 0..cols {
            row.iter().take(num_cols_to_print).for_each(|col| {
                print!(
                    "{}",
                    if datatype::is_na_string_padded(col) {
                        col.truecolor(na_color.0, na_color.1, na_color.2)
                    } else {
                        col.truecolor(std_color.0, std_color.1, std_color.2)
                    }
                );
            });
            println!();
        });

    // additional row info

    if rows_remaining > 0 {
        print!("{: <6}", "");
        print!(
            "{}",
            row_remaining_text.truecolor(meta_color.0, meta_color.1, meta_color.2)
        );
        //println!("num_cols_to_print {:?} cols {:?}", num_cols_to_print, cols);
        let extra_cols_to_mention = num_cols_to_print;
        let remainder_cols = cols - extra_cols_to_mention;
        if extra_cols_to_mention < cols {
            let meta_text_and = "and";
            let meta_text_var = "more variables";
            let meta_text_comma = ",";
            let meta_text_colon = ":";
            print!(
                " {} {} {}{}",
                meta_text_and.truecolor(meta_color.0, meta_color.1, meta_color.2),
                remainder_cols.truecolor(meta_color.0, meta_color.1, meta_color.2),
                meta_text_var.truecolor(meta_color.0, meta_color.1, meta_color.2),
                meta_text_colon.truecolor(meta_color.0, meta_color.1, meta_color.2)
            );
            for col in extra_cols_to_mention..cols {
                let text = rdr[0].get(col).unwrap();
                print!(
                    " {}",
                    text.truecolor(meta_color.0, meta_color.1, meta_color.2)
                );

                // The last column mentioned in foot should not be followed by a comma
                if col + 1 < cols {
                    print!(
                        "{}",
                        meta_text_comma.truecolor(meta_color.0, meta_color.1, meta_color.2)
                    )
                }
            }
        }
    }

    // footer
    if !datatype::is_na(footer_option) {
        println!("{: <6}", "");
        println!(
            "{}",
            footer_option.truecolor(meta_color.0, meta_color.1, meta_color.2)
        );
    }

    println!();
} // end main

fn build_reader(opt: &Cli) -> Result<Reader<Box<dyn Read>>, std::io::Error> {
    let source: Box<dyn Read> = if let Some(path) = opt.file.clone() {
        let file = File::open(path)?;
        Box::new(BufReader::new(file))
    } else {
        Box::new(io::stdin())
    };

    let reader = ReaderBuilder::new()
        .has_headers(false)
        .delimiter(opt.delimiter)
        .from_reader(source);

    Ok(reader)
}

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
        assert_eq!(datatype::is_na(&"1".to_string()), false);
        assert_eq!(datatype::is_na(&"0".to_string()), false);
    }
    // the following tests look messy, but the formatting is a neccesary condition.
    #[test]
    fn a_csv() {
        let v: Vec<Vec<&str>> = vec![
            vec![
                "name",
                "abc",
                "abc",
                "abc",
                "abc",
                "abc",
                "abcde",
                "abcdefgh",
                "abcdefghijkl",
                "NA",
                "abcdefghijklmnop",
                "",
                "n/a",
                "floatlike",
            ],
            vec![
                "value",
                "0.00000001",
                "0.0000001",
                "0.000001",
                "0.00001",
                "0.0001",
                "0.001",
                "0.01",
                "0.1",
                "1",
                "10",
                "100",
                "",
                "2/ 2.5 Gallon",
            ],
            vec![
                "bool", "T", "T", "T", "T", "T", "F", "True", "F", "T", "F", "", "F", "F",
            ],
            vec![
                "date",
                "2021-01-01",
                "2021-01-01",
                "2021-01-01",
                "2021-01-01",
                "2021-01-01",
                "2021-01-01",
                "",
                "2021-01-01",
                "2021-01-01",
                "2021-01-01",
                "2021-01-01",
                "2021-01-01",
                "2021-01-01",
            ],
        ];
        let col_largest_width_post_proc: Vec<usize> = vec![16, 13, 4, 10];
        let mut vf: Vec<Vec<String>> = vec![vec!["#".to_string(); 13 as usize]; 4 as usize];
        for i in 0..col_largest_width_post_proc.len() {
            vf[i] = datatype::trunc_strings(&v[i], col_largest_width_post_proc[i]);
        }

        assert_eq!(
            vf,
            [
                [
                    "name             ",
                    "abc              ",
                    "abc              ",
                    "abc              ",
                    "abc              ",
                    "abc              ",
                    "abcde            ",
                    "abcdefgh         ",
                    "abcdefghijkl     ",
                    "NA               ",
                    "abcdefghijklmnop ",
                    "NA               ",
                    "NA               ",
                    "floatlike        "
                ],
                [
                    "value         ",
                    "0.00000001    ",
                    "0.0000001     ",
                    "0.000001      ",
                    "0.00001       ",
                    "0.0001        ",
                    "0.001         ",
                    "0.01          ",
                    "0.1           ",
                    "1             ",
                    "10            ",
                    "100           ",
                    "NA            ",
                    "2/ 2.5 Gallon "
                ],
                [
                    "bool ", "T    ", "T    ", "T    ", "T    ", "T    ", "F    ", "True ",
                    "F    ", "T    ", "F    ", "NA   ", "F    ", "F    "
                ],
                [
                    "date       ",
                    "2021-01-01 ",
                    "2021-01-01 ",
                    "2021-01-01 ",
                    "2021-01-01 ",
                    "2021-01-01 ",
                    "2021-01-01 ",
                    "NA         ",
                    "2021-01-01 ",
                    "2021-01-01 ",
                    "2021-01-01 ",
                    "2021-01-01 ",
                    "2021-01-01 ",
                    "2021-01-01 "
                ]
            ]
        );
    }

    #[test]
    fn long_doubles_74_csv() {
        let v: Vec<Vec<&str>> = vec![
            vec!["text", "row1", "row2"],
            vec!["col1", "3.333333333333333", "1.11111111111111111"],
            vec!["col2", "3.333333333333333", "1.11111111111111111"],
            vec!["col3", "3.333333333333333", "1.11111111111111111"],
        ];
        let col_largest_width_post_proc: Vec<usize> = vec![4, 4, 4, 4];
        let mut vf: Vec<Vec<String>> = vec![vec!["#".to_string(); 3 as usize]; 4 as usize];
        for i in 0..col_largest_width_post_proc.len() {
            vf[i] = datatype::trunc_strings(&v[i], col_largest_width_post_proc[i]);
        }

        assert_eq!(
            vf,
            [
                ["text ", "row1 ", "row2 "],
                ["col1 ", "3.33 ", "1.11 "],
                ["col2 ", "3.33 ", "1.11 "],
                ["col3 ", "3.33 ", "1.11 "]
            ]
        );
    }

    #[test]
    fn unicode_pr55_csv() {
        let v: Vec<Vec<&str>> = vec![
            vec!["aColumn", "1"],
            vec!["bColumn", "üÜğĞçÇşŞöÖ"],
            vec!["cColumn", "üÜğĞçÇşŞöÖ üÜğĞçÇşŞöÖ"],
            vec!["dColumn", "77"],
            vec!["eColumn", "TR"],
            vec!["fColumn", "77"],
            vec!["gColumn", "77"],
        ];
        let col_largest_width_post_proc: Vec<usize> = vec![7, 10, 20, 7, 7, 7, 7];
        let mut vf: Vec<Vec<String>> = vec![vec!["#".to_string(); 2 as usize]; 7 as usize];
        for i in 0..col_largest_width_post_proc.len() {
            vf[i] = datatype::trunc_strings(&v[i], col_largest_width_post_proc[i]);
        }

        assert_eq!(
            vf,
            [
                ["aColumn ", "1       "],
                ["bColumn    ", "üÜğĞçÇşŞöÖ "],
                ["cColumn              ", "üÜğĞçÇşŞöÖ üÜğĞçÇşŞ… "],
                ["dColumn ", "77      "],
                ["eColumn ", "TR      "],
                ["fColumn ", "77      "],
                ["gColumn ", "77      "]
            ]
        );
    }

    #[test]
    fn build_reader_can_create_reader_without_file_specified() {
        let cli = Cli::from_args();
        let reader = build_reader(&cli);
        assert!(reader.is_ok());
    }
}
