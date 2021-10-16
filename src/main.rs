use csv::{Reader, ReaderBuilder};
use owo_colors::OwoColorize;
use std::fs::File;
use std::io::{self, BufReader, Read};
use std::path::PathBuf;
use structopt::StructOpt;
mod datatype;
use calm_io::stdout;
use calm_io::stdoutln;
use crossterm::terminal::size;
use directories::BaseDirs;
use serde::Deserialize;
use serde::Serialize;
use std::convert::TryInto;
use toml;

#[derive(StructOpt)]
#[structopt(
    name = "tv",
    about = "Tidy Viewer (tv) is a csv pretty printer that uses column styling to maximize viewer enjoyment.✨✨📺✨✨\n
    Example Usage:
    wget https://raw.githubusercontent.com/tidyverse/ggplot2/master/data-raw/diamonds.csv
    cat diamonds.csv | head -n 35 | tv

    Configuration File Support:
    An example config is printed to make it easy to copy/paste to `tv.toml`.
    The config (tv.toml) location is dependent on OS:
        * Linux: $XDG_CONFIG_HOME or $HOME/.config/tv.toml
        * macOS: $HOME/Library/Application Support/tv.toml
        * Windows: {FOLDERID_RoamingAppData}\\tv.toml

        ## ==Tidy-Viewer Config Example==
        ## Remove the first column of comments for valid toml file
        ## The delimiter separating the columns. [default: ,]
        #delimiter = \",\"
        ## Add a title to your tv. Example \'Test Data\' [default: NA (\"\")]
        #title = \"\"
        ## Add a footer to your tv. Example \'footer info\' [default: NA (\"\")]
        #footer = \"\"
        ## The upper (maxiumum) width of columns. [default: 20]
        #upper_column_width = 20
        ## The minimum width of columns. Must be 2 or larger. [default: 2]
        #lower_column_width = 2
        ## head number of rows to output <row-display> [default: 25]
        #number = 35
        ## meta_color = [R,G,B] color for row index and \"tv dim: rowsxcols\"
        #meta_color = [64, 179, 162]
        ## header_color = [R,G,B] color for column headers
        #header_color = [232, 168, 124]
        ## std_color = [R,G,B] color for standard cell data values
        #std_color = [133, 205, 202]
        ## na_color = [R,G,B] color for NA values
        #na_color = [226, 125, 95]
"
)]
struct Cli {
    #[structopt(
        short = "c",
        long = "color",
        default_value = "0",
        help = "There are 5 preconfigured color palettes:
                (1)nord
                (2)one_dark
                (3)gruvbox
                (4)dracula
                (5)uncolor (Coming Soon)\nAn input of (5)uncolor will remove color properties. Note that colors will make it difficult to pipe output to other utilities.The default value of (0) is reserved to make config/option coloring logic easier."
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
    // toml struct
    #[derive(Deserialize, Serialize, Debug, Clone)]
    struct Data {
        delimiter: String,
        title: String,
        footer: String,
        upper_column_width: usize,
        lower_column_width: usize,
        number: usize,
        meta_color: toml::value::Array,
        header_color: toml::value::Array,
        std_color: toml::value::Array,
        na_color: toml::value::Array,
    }

    let base_dir = BaseDirs::new();
    let config_base_dir = base_dir.clone().unwrap();
    let config_dir = config_base_dir.config_dir();
    let conf_file = PathBuf::from("tv.toml");
    let conf_dir_file: PathBuf = config_dir.join(conf_file.clone());
    let file_contents: Option<String> = std::fs::read_to_string(conf_dir_file).ok();
    //println!("file_contents {:?}", file_contents);
    let config: Option<Data> = match file_contents {
        Some(x) => toml::from_str(&x.to_owned()).ok(),
        None => None,
    };
    //println!("config {:#?}", config);

    let term_tuple = size().unwrap();
    let opt = Cli::from_args();
    let color_option = opt.color;
    //let sigfig = opt.sigfig;
    let debug_mode = opt.debug_mode;
    let is_title_defined = opt.title.chars().count() > 0;
    let is_footer_defined = opt.title.chars().count() > 0;
    let is_row_display_defined = !(opt.row_display == 25);
    let is_tty = atty::is(atty::Stream::Stdout);

    let title_option = match (&config, is_title_defined) {
        (Some(x), false) => &x.title,
        (Some(_x), true) => &opt.title,
        (None, false) => &opt.title,
        (None, true) => &opt.title,
    };
    let footer_option = match (&config, is_footer_defined) {
        (Some(x), false) => &x.footer,
        (Some(_x), true) => &opt.footer,
        (None, false) => &opt.footer,
        (None, true) => &opt.footer,
    };

    let row_display_option = match (&config, is_row_display_defined) {
        (Some(x), false) => &x.number,
        (Some(_x), true) => &opt.row_display,
        (None, false) => &opt.row_display,
        (None, true) => &opt.row_display,
    };

    // nord
    let nord_meta_color: [u8; 3] = [143, 188, 187];
    let nord_header_color: [u8; 3] = [94, 129, 172];
    let nord_std_color: [u8; 3] = [216, 222, 233];
    let nord_na_color: [u8; 3] = [191, 97, 106];
    // one dark
    let one_dark_meta_color: [u8; 3] = [152, 195, 121];
    let one_dark_header_color: [u8; 3] = [97, 175, 239];
    let one_dark_std_color: [u8; 3] = [171, 178, 191];
    let one_dark_na_color: [u8; 3] = [224, 108, 117];
    //// gruv
    let gruvbox_meta_color: [u8; 3] = [184, 187, 38];
    let gruvbox_header_color: [u8; 3] = [215, 153, 33];
    let gruvbox_std_color: [u8; 3] = [235, 219, 178];
    let gruvbox_na_color: [u8; 3] = [204, 36, 29];
    //// dracula
    let dracula_meta_color: [u8; 3] = [98, 114, 164];
    let dracula_header_color: [u8; 3] = [80, 250, 123];
    let dracula_std_color: [u8; 3] = [248, 248, 242];
    let dracula_na_color: [u8; 3] = [255, 121, 198];

    // user args
    let lower_column_width_defined = !(opt.lower_column_width == 2);
    let upper_column_width_defined = !(opt.lower_column_width == 20);
    let lower_column_width = match (&config, lower_column_width_defined) {
        (Some(x), false) => x.lower_column_width,
        (Some(_x), true) => opt.lower_column_width,
        (None, false) => opt.lower_column_width,
        (None, true) => opt.lower_column_width,
    };
    let lower_column_width = if lower_column_width.to_owned() < 2 {
        panic!("lower-column-width must be larger than 2")
    } else {
        lower_column_width
    };
    let upper_column_width = match (&config, upper_column_width_defined) {
        (Some(x), false) => x.upper_column_width,
        (Some(_x), true) => opt.upper_column_width,
        (None, false) => opt.upper_column_width,
        (None, true) => opt.upper_column_width,
    };
    let upper_column_width = if upper_column_width <= lower_column_width {
        panic!("upper-column-width must be larger than lower-column-width")
    } else {
        upper_column_width
    };
    // logic for picking colors given config and user arguments
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
    let is_color_defined = opt.color > 0;
    let meta_color = match (&config, is_color_defined) {
        (Some(x), false) => get_color_from_config(&x.clone().meta_color),
        (Some(_x), true) => meta_color,
        (None, false) => nord_meta_color,
        (None, true) => meta_color,
    };
    let header_color = match (&config, is_color_defined) {
        (Some(x), false) => get_color_from_config(&x.clone().header_color),
        (Some(_x), true) => header_color,
        (None, false) => nord_header_color,
        (None, true) => header_color,
    };
    let std_color = match (&config, is_color_defined) {
        (Some(x), false) => get_color_from_config(&x.clone().std_color),
        (Some(_x), true) => std_color,
        (None, false) => nord_std_color,
        (None, true) => std_color,
    };
    let na_color = match (&config, is_color_defined) {
        (Some(x), false) => get_color_from_config(&x.clone().na_color),
        (Some(_x), true) => na_color,
        (None, false) => nord_na_color,
        (None, true) => na_color,
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
    let vf: Vec<Vec<String>> = v
        .iter()
        .map(|col| datatype::format_strings(col, lower_column_width, upper_column_width))
        .collect();

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

    let num_cols_to_print = get_num_cols_to_print(cols, vp.clone(), term_tuple);

    // color
    let meta_text = "tv dim:";
    let div = "x";
    let _ = match stdout!("{: <6}", "") {
        Ok(_) => Ok(()),
        Err(e) => match e.kind() {
            std::io::ErrorKind::BrokenPipe => Ok(()),
            _ => Err(e),
        },
    };
    if is_tty {
        let _ = match stdout!(
            "{} {} {} {}",
            meta_text.truecolor(meta_color[0], meta_color[1], meta_color[2]),
            (rows_in_file - 1).truecolor(meta_color[0], meta_color[1], meta_color[2]),
            div.truecolor(meta_color[0], meta_color[1], meta_color[2]),
            (cols).truecolor(meta_color[0], meta_color[1], meta_color[2]),
        ) {
            Ok(_) => Ok(()),
            Err(e) => match e.kind() {
                std::io::ErrorKind::BrokenPipe => Ok(()),
                _ => Err(e),
            },
        };
    } else {
        let _ = match stdoutln!("{} {} {} {}", meta_text, rows_in_file - 1, div, cols) {
            Ok(_) => Ok(()),
            Err(e) => match e.kind() {
                std::io::ErrorKind::BrokenPipe => Ok(()),
                _ => Err(e),
            },
        };
    }
    // title
    if !datatype::is_na(&title_option.clone()) {
        let _ = match stdout!("{: <6}", "") {
            Ok(_) => Ok(()),
            Err(e) => match e.kind() {
                std::io::ErrorKind::BrokenPipe => Ok(()),
                _ => Err(e),
            },
        };
        if is_tty {
            let _ = match stdoutln!(
                "{}",
                title_option
                    .truecolor(meta_color[0], meta_color[1], meta_color[2])
                    .underline()
                    .bold()
            ) {
                Ok(_) => Ok(()),
                Err(e) => match e.kind() {
                    std::io::ErrorKind::BrokenPipe => Ok(()),
                    _ => Err(e),
                },
            };
        } else {
            let _ = match stdoutln!("{}", title_option) {
                Ok(_) => Ok(()),
                Err(e) => match e.kind() {
                    std::io::ErrorKind::BrokenPipe => Ok(()),
                    _ => Err(e),
                },
            };
        }
    }

    // header
    let _ = match stdout!("{: <6}", "") {
        Ok(_) => Ok(()),
        Err(e) => match e.kind() {
            std::io::ErrorKind::BrokenPipe => Ok(()),
            _ => Err(e),
        },
    };
    //for col in 0..cols {
    for col in 0..num_cols_to_print {
        let text = vp[0].get(col).unwrap().to_string();
        if is_tty {
            let _ = match stdout!(
                "{}",
                text.truecolor(header_color[0], header_color[1], header_color[2])
                    .bold()
            ) {
                Ok(_) => Ok(()),
                Err(e) => match e.kind() {
                    std::io::ErrorKind::BrokenPipe => Ok(()),
                    _ => Err(e),
                },
            };
        } else {
            let _ = match stdout!("{}", text) {
                Ok(_) => Ok(()),
                Err(e) => match e.kind() {
                    std::io::ErrorKind::BrokenPipe => Ok(()),
                    _ => Err(e),
                },
            };
        }
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
    let _ = match stdoutln!() {
        Ok(_) => Ok(()),
        Err(e) => match e.kind() {
            std::io::ErrorKind::BrokenPipe => Ok(()),
            _ => Err(e),
        },
    };
    vp.iter()
        .enumerate()
        .take(rows)
        .skip(1)
        .for_each(|(i, row)| {
            if is_tty {
                let _ = match stdout!(
                    "{: <6}",
                    i.truecolor(meta_color[0], meta_color[1], meta_color[2])
                ) {
                    Ok(_) => Ok(()),
                    Err(e) => match e.kind() {
                        std::io::ErrorKind::BrokenPipe => Ok(()),
                        _ => Err(e),
                    },
                };
            } else {
                let _ = match stdout!("{: <6}", i) {
                    Ok(_) => Ok(()),
                    Err(e) => match e.kind() {
                        std::io::ErrorKind::BrokenPipe => Ok(()),
                        _ => Err(e),
                    },
                };
            }
            //for col in 0..cols {
            row.iter().take(num_cols_to_print).for_each(|col| {
                if is_tty {
                    let _ = match stdout!(
                        "{}",
                        if datatype::is_na_string_padded(col) {
                            col.truecolor(na_color[0], na_color[1], na_color[2])
                        } else {
                            col.truecolor(std_color[0], std_color[1], std_color[2])
                        }
                    ) {
                        Ok(_) => Ok(()),
                        Err(e) => match e.kind() {
                            std::io::ErrorKind::BrokenPipe => Ok(()),
                            _ => Err(e),
                        },
                    };
                } else {
                    let _ = match stdout!("{}", col) {
                        Ok(_) => Ok(()),
                        Err(e) => match e.kind() {
                            std::io::ErrorKind::BrokenPipe => Ok(()),
                            _ => Err(e),
                        },
                    };
                }
            });
            let _ = match stdoutln!() {
                Ok(_) => Ok(()),
                Err(e) => match e.kind() {
                    std::io::ErrorKind::BrokenPipe => Ok(()),
                    _ => Err(e),
                },
            };
        });

    // additional row info

    if rows_remaining > 0 {
        let _ = match stdout!("{: <6}", "") {
            Ok(_) => Ok(()),
            Err(e) => match e.kind() {
                std::io::ErrorKind::BrokenPipe => Ok(()),
                _ => Err(e),
            },
        };
        if is_tty {
            let _ = match stdout!(
                "{}",
                row_remaining_text.truecolor(meta_color[0], meta_color[1], meta_color[2])
            ) {
                Ok(_) => Ok(()),
                Err(e) => match e.kind() {
                    std::io::ErrorKind::BrokenPipe => Ok(()),
                    _ => Err(e),
                },
            };
        } else {
            let _ = match stdout!("{}", row_remaining_text) {
                Ok(_) => Ok(()),
                Err(e) => match e.kind() {
                    std::io::ErrorKind::BrokenPipe => Ok(()),
                    _ => Err(e),
                },
            };
        }
        //println!("num_cols_to_print {:?} cols {:?}", num_cols_to_print, cols);
        let extra_cols_to_mention = num_cols_to_print;
        let remainder_cols = cols - extra_cols_to_mention;
        if extra_cols_to_mention < cols {
            let meta_text_and = "and";
            let meta_text_var = "more variables";
            let meta_text_comma = ",";
            let meta_text_colon = ":";
            if is_tty {
                let _ = match stdout!(
                    " {} {} {}{}",
                    meta_text_and.truecolor(meta_color[0], meta_color[1], meta_color[2]),
                    remainder_cols.truecolor(meta_color[0], meta_color[1], meta_color[2]),
                    meta_text_var.truecolor(meta_color[0], meta_color[1], meta_color[2]),
                    meta_text_colon.truecolor(meta_color[0], meta_color[1], meta_color[2])
                ) {
                    Ok(_) => Ok(()),
                    Err(e) => match e.kind() {
                        std::io::ErrorKind::BrokenPipe => Ok(()),
                        _ => Err(e),
                    },
                };
            } else {
                let _ = match stdout!(
                    " {} {} {}{}",
                    meta_text_and,
                    remainder_cols,
                    meta_text_var,
                    meta_text_colon
                ) {
                    Ok(_) => Ok(()),
                    Err(e) => match e.kind() {
                        std::io::ErrorKind::BrokenPipe => Ok(()),
                        _ => Err(e),
                    },
                };
            }
            for col in extra_cols_to_mention..cols {
                let text = rdr[0].get(col).unwrap();
                if is_tty {
                    let _ = match stdout!(
                        " {}",
                        text.truecolor(meta_color[0], meta_color[1], meta_color[2])
                    ) {
                        Ok(_) => Ok(()),
                        Err(e) => match e.kind() {
                            std::io::ErrorKind::BrokenPipe => Ok(()),
                            _ => Err(e),
                        },
                    };
                } else {
                    let _ = match stdout!(" {}", text) {
                        Ok(_) => Ok(()),
                        Err(e) => match e.kind() {
                            std::io::ErrorKind::BrokenPipe => Ok(()),
                            _ => Err(e),
                        },
                    };
                }

                // The last column mentioned in foot should not be followed by a comma
                if col + 1 < cols {
                    if is_tty {
                        let _ = match stdout!(
                            "{}",
                            meta_text_comma.truecolor(meta_color[0], meta_color[1], meta_color[2])
                        ) {
                            Ok(_) => Ok(()),
                            Err(e) => match e.kind() {
                                std::io::ErrorKind::BrokenPipe => Ok(()),
                                _ => Err(e),
                            },
                        };
                    } else {
                        let _ = match stdout!("{}", meta_text_comma) {
                            Ok(_) => Ok(()),
                            Err(e) => match e.kind() {
                                std::io::ErrorKind::BrokenPipe => Ok(()),
                                _ => Err(e),
                            },
                        };
                    }
                }
            }
        }
    }

    // footer
    if !datatype::is_na(&footer_option.clone()) {
        let _ = match stdout!("{: <6}", "") {
            Ok(_) => Ok(()),
            Err(e) => match e.kind() {
                std::io::ErrorKind::BrokenPipe => Ok(()),
                _ => Err(e),
            },
        };
        if is_tty {
            let _ = match stdoutln!(
                "{}",
                footer_option.truecolor(meta_color[0], meta_color[1], meta_color[2])
            ) {
                Ok(_) => Ok(()),
                Err(e) => match e.kind() {
                    std::io::ErrorKind::BrokenPipe => Ok(()),
                    _ => Err(e),
                },
            };
        } else {
            let _ = match stdoutln!("{}", footer_option) {
                Ok(_) => Ok(()),
                Err(e) => match e.kind() {
                    std::io::ErrorKind::BrokenPipe => Ok(()),
                    _ => Err(e),
                },
            };
        }
    }

    let _ = match stdoutln!() {
        Ok(_) => Ok(()),
        Err(e) => match e.kind() {
            std::io::ErrorKind::BrokenPipe => Ok(()),
            _ => Err(e),
        },
    };
} // end main

fn get_color_from_config(a: &toml::value::Array) -> [u8; 3] {
    let i32_array: [u8; 3] = a
        .clone()
        .iter()
        .map(|v| {
            v.as_integer()
                .expect("Not an integer")
                .try_into()
                .expect("Does not fit in a `i32`")
        })
        .collect::<Vec<_>>()
        .try_into()
        .expect("Not 3 elements");
    i32_array
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
            vf[i] = datatype::format_strings(
                &v[i],
                col_largest_width_post_proc[i],
                col_largest_width_post_proc[i],
            );
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
                    "  0.00000001  ",
                    "  0.0000001   ",
                    "  0.000001    ",
                    "  0.00001     ",
                    "  0.0001      ",
                    "  0.001       ",
                    "  0.01        ",
                    "  0.1         ",
                    "  1           ",
                    " 10           ",
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
            vf[i] = datatype::format_strings(
                &v[i],
                col_largest_width_post_proc[i],
                col_largest_width_post_proc[i],
            );
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
            vf[i] = datatype::format_strings(
                &v[i],
                col_largest_width_post_proc[i],
                col_largest_width_post_proc[i],
            );
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
