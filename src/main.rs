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

#[derive(StructOpt)]
#[structopt(
    name = "tv",
    about = "Tidy Viewer (tv) is a csv pretty printer that uses column styling to maximize viewer enjoyment.✨✨📺✨✨\n
    Example Usage:
    wget https://raw.githubusercontent.com/tidyverse/ggplot2/master/data-raw/diamonds.csv
    cat diamonds.csv | head -n 35 | tv
    tv diamonds.csv

    Configuration File Support:
    An example config is printed to make it easy to copy/paste to `tv.toml`.
    Check the parameters you have changed with `tv --config-details`.
    The config (tv.toml) location is dependent on OS:
        * Linux: $XDG_CONFIG_HOME or $HOME/.config/tv.toml
        * macOS: $HOME/Library/Application Support/tv.toml
        * Windows: {FOLDERID_RoamingAppData}\\tv.toml

        ## ==Tidy-Viewer Config Example==
        ## Remove the first column of comments for valid toml file
        ## All fields must be defined. Partial files will not be read.
        ## The delimiter separating the columns. [default: ,]
        #delimiter = \",\"
        ## Add a title to your tv. Example \'Test Data\' [default: NA (\"\")]
        #title = \"\"
        ## Add a footer to your tv. Example \'footer info\' [default: NA (\"\")]
        #footer = \"\"
        ## The upper (maximum) width of columns. [default: 20]
        #upper_column_width = 20
        ## The minimum width of columns. Must be 2 or larger. [default: 2]
        #lower_column_width = 2
        ## head number of rows to output <row-display> [default: 25]
        #number = 35
        ## extend width and length in terms of the number of rows and columns displayed beyond term width [default: false]
        # extend_width_length = true
        ## meta_color = [R,G,B] color for row index and \"tv dim: rows x cols\"
        #meta_color = [64, 179, 162]
        ## header_color = [R,G,B] color for column headers
        #header_color = [232, 168, 124]
        ## std_color = [R,G,B] color for standard cell data values
        #std_color = [133, 205, 202]
        ## na_color = [R,G,B] color for NA values
        #na_color = [226, 125, 95]
        ## neg_num_color = [R,G,B] color for negative values
        #neg_num_color = [226, 125, 95]
"
)]
struct Cli {
    #[structopt(
        short = "c",
        long = "color",
        default_value = "0",
        help = "There are 5 preconfigured color palettes (Defaults to nord):
                (1)nord
                (2)one_dark
                (3)gruvbox
                (4)dracula
                (5)solarized light"
    )]
    color: usize,
    #[structopt(
        short = "f",
        long = "force-all-rows",
        help = "Print all rows in file. May be piped to 'less -S'. Example `tidy-viewer data/diamonds.csv -f -a | less -R`"
    )]
    force_all_rows: bool,
    #[structopt(
        short = "j",
        long = "jump-invalid-rows",
        help = "Jump over (skip) invalid rows in the file. This includes rows with the incorrect number of columns."
    )]
    skip_invalid_rows: bool,
    #[structopt(
        short = "p",
        long = "pedantic",
        help = "Crashes when csv input is malformed. Useful to check for valid csv data."
    )]
    pedantic: bool,
    #[structopt(
        short = "t",
        long = "title",
        default_value = "NA",
        help = "Add a title to your tv. Example 'Test Data'"
    )]
    title: String,
    #[structopt(
        short = "F",
        long = "footer",
        default_value = "NA",
        help = "Add a footer to your tv. Example 'footer info'"
    )]
    footer: String,
    #[structopt(
        short = "n",
        long = "number-of-rows-to-output",
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
        help = "The upper (maximum) width of columns."
    )]
    upper_column_width: usize,
    #[structopt(
        short = "s",
        long = "delimiter",
        parse(try_from_str = datatype::parse_delimiter),
        help = "The delimiter separating the columns."
    )]
    delimiter: Option<u8>,
    #[structopt(
        short = "g",
        long = "sigfig",
        default_value = "3",
        help = "Significant Digits. Default 3. Max is 7"
    )]
    sigfig: i64,
    #[structopt(
        short = "e",
        long = "extend-width-and-length",
        help = "Extended width beyond term width (do not truncate). Useful with `less -S`."
    )]
    extend_width_length: bool,
    #[structopt(
        short = "d",
        long = "debug-mode",
        help = "Print object details to make it easier for the maintainer to find and resolve bugs."
    )]
    debug_mode: bool,
    #[structopt(
        short = "a",
        long = "color-always",
        help = "Always force color output. Example `tv -a starwars.csv | less -R` or `tv -a starwars.csv | bat -p`. The `less` cli has the `-R` flag to parse colored output."
    )]
    force_color: bool,

    #[structopt(
        short = "D",
        long = "no-dimensions",
        help = "Turns off dimensions of the data"
    )]
    no_dimensions: bool,

    #[structopt(
        short = "R",
        long = "no-row-numbering",
        help = "Turns off row numbering"
    )]
    no_row_numbering: bool,

    #[structopt(
        short = "C",
        long = "config-details",
        help = "Show the current config details"
    )]
    config_details: bool,

    #[structopt(name = "FILE", parse(from_os_str), help = "File to process")]
    file: Option<PathBuf>,
}

fn main() {
    // toml struct
    #[derive(Deserialize, Serialize, Debug, Clone)]
    struct Config {
        delimiter: Option<String>,
        title: Option<String>,
        footer: Option<String>,
        upper_column_width: Option<usize>,
        lower_column_width: Option<usize>,
        number: Option<usize>,
        extend_width_length: Option<bool>,
        meta_color: Option<toml::value::Array>,
        header_color: Option<toml::value::Array>,
        std_color: Option<toml::value::Array>,
        na_color: Option<toml::value::Array>,
        neg_num_color: Option<toml::value::Array>,
    }

    let base_dir: Option<BaseDirs> = BaseDirs::new();
    let config_base_dir: BaseDirs = base_dir.unwrap();
    let config_dir = config_base_dir.config_dir();
    let conf_file: PathBuf = PathBuf::from("tv.toml");
    let conf_dir_file: PathBuf = config_dir.join(conf_file);
    let file_contents: Option<String> = std::fs::read_to_string(conf_dir_file).ok();
    let config: Config = match toml::from_str(file_contents.as_ref().unwrap_or(&String::new())) {
        // return 'Ok' if the file was successfully parsed
        // else return Config with all None values
        Ok(x) => x,
        Err(_) => Config {
            delimiter: None,
            title: None,
            footer: None,
            upper_column_width: None,
            lower_column_width: None,
            number: None,
            extend_width_length: None,
            meta_color: None,
            header_color: None,
            std_color: None,
            na_color: None,
            neg_num_color: None,
        },
    };
    // load cli args
    let opt = Cli::from_args();

    // print helpful config details
    match opt.config_details {
        true => {
            println!("");
            println!("{:}", "tv.toml".to_string().truecolor(94, 129, 172));
            match config.clone().delimiter {
                Some(x) => println!(
                    "{}{}{:?}",
                    "[+]".to_string().truecolor(143, 188, 187), // green
                    " delimiter = ".to_string().truecolor(216, 222, 233), // white
                    x.truecolor(216, 222, 233)                  // white
                ),
                None => println!(
                    "{}{}",
                    "[-]".truecolor(191, 97, 106),                // red
                    " delimiter = None".truecolor(216, 222, 233)  // white
                ),
            }
            // match title
            match config.clone().title {
                Some(x) => println!(
                    "{}{}{:?}",
                    "[+]".to_string().truecolor(143, 188, 187), // green
                    " title = ".to_string().truecolor(216, 222, 233), // white
                    x.truecolor(216, 222, 233)                  // white
                ),
                None => println!(
                    "{}{}",
                    "[-]".truecolor(191, 97, 106),            // red
                    " title = None".truecolor(216, 222, 233)  // white
                ),
            }

            // match footer
            match config.clone().footer {
                Some(x) => println!(
                    "{}{}{:?}",
                    "[+]".to_string().truecolor(143, 188, 187), // green
                    " footer = ".to_string().truecolor(216, 222, 233), // white
                    x.truecolor(216, 222, 233)                  // white
                ),
                None => println!(
                    "{}{}",
                    "[-]".truecolor(191, 97, 106),             // red
                    " footer = None".truecolor(216, 222, 233)  // white
                ),
            }

            // match upper_column_width
            match config.clone().upper_column_width {
                Some(x) => println!(
                    "{}{}{:?}",
                    "[+]".to_string().truecolor(143, 188, 187), // green
                    " upper_column_width = "
                        .to_string()
                        .truecolor(216, 222, 233), // white
                    x.truecolor(216, 222, 233)                  // white
                ),
                None => println!(
                    "{}{}",
                    "[-]".truecolor(191, 97, 106), // red
                    " upper_column_width = None".truecolor(216, 222, 233)  // white
                ),
            }

            // match lower_column_width
            match config.clone().lower_column_width {
                Some(x) => println!(
                    "{}{}{:?}",
                    "[+]".to_string().truecolor(143, 188, 187), // green
                    " lower_column_width = "
                        .to_string()
                        .truecolor(216, 222, 233), // white
                    x.truecolor(216, 222, 233)                  // white
                ),
                None => println!(
                    "{}{}",
                    "[-]".truecolor(191, 97, 106), // red
                    " lower_column_width = None".truecolor(216, 222, 233)  // white
                ),
            }

            // match number
            match config.clone().number {
                Some(x) => println!(
                    "{}{}{:?}",
                    "[+]".to_string().truecolor(143, 188, 187), // green
                    " number = ".to_string().truecolor(216, 222, 233), // white
                    x.truecolor(216, 222, 233)                  // white
                ),
                None => println!(
                    "{}{}",
                    "[-]".truecolor(191, 97, 106),             // red
                    " number = None".truecolor(216, 222, 233)  // white
                ),
            }

            // match extend_width_length
            match config.clone().extend_width_length {
                Some(x) => println!(
                    "{}{}{:?}",
                    "[+]".to_string().truecolor(143, 188, 187), // green
                    " extend_width_length = "
                        .to_string()
                        .truecolor(216, 222, 233), // white
                    x.truecolor(216, 222, 233)                  // white
                ),
                None => println!(
                    "{}{}",
                    "[-]".truecolor(191, 97, 106), // red
                    " extend_width_length = None".truecolor(216, 222, 233)  // white
                ),
            }
            // match meta_color
            match config.clone().meta_color {
                Some(x) => println!(
                    "{}{}{:?}",
                    "[+]".to_string().truecolor(143, 188, 187), // green
                    " meta_color = ".to_string().truecolor(216, 222, 233), // white
                    x.truecolor(216, 222, 233)                  // white
                ),
                None => println!(
                    "{}{}",
                    "[-]".truecolor(191, 97, 106), // red
                    " meta_color = None".truecolor(216, 222, 233)  // white
                ),
            }

            // match header_color
            match config.clone().header_color {
                Some(x) => println!(
                    "{}{}{:?}",
                    "[+]".to_string().truecolor(143, 188, 187), // green
                    " header_color = ".to_string().truecolor(216, 222, 233), // white
                    x.truecolor(216, 222, 233)                  // white
                ),
                None => println!(
                    "{}{}",
                    "[-]".truecolor(191, 97, 106), // red
                    " header_color = None".truecolor(216, 222, 233)  // white
                ),
            }

            // match std_color
            match config.clone().std_color {
                Some(x) => println!(
                    "{}{}{:?}",
                    "[+]".to_string().truecolor(143, 188, 187), // green
                    " std_color = ".to_string().truecolor(216, 222, 233), // white
                    x.truecolor(216, 222, 233)                  // white
                ),
                None => println!(
                    "{}{}",
                    "[-]".truecolor(191, 97, 106),                // red
                    " std_color = None".truecolor(216, 222, 233)  // white
                ),
            }

            // match na_color
            match config.clone().na_color {
                Some(x) => println!(
                    "{}{}{:?}",
                    "[+]".to_string().truecolor(143, 188, 187), // green
                    " na_color = ".to_string().truecolor(216, 222, 233), // white
                    x.truecolor(216, 222, 233)                  // white
                ),
                None => println!(
                    "{}{}",
                    "[-]".truecolor(191, 97, 106),               // red
                    " na_color = None".truecolor(216, 222, 233)  // white
                ),
            }

            // match neg_num_color
            match config.clone().neg_num_color {
                Some(x) => println!(
                    "{}{}{:?}",
                    "[+]".to_string().truecolor(143, 188, 187), // green
                    " neg_num_color = ".to_string().truecolor(216, 222, 233), // white
                    x.truecolor(216, 222, 233)                  // white
                ),
                None => println!(
                    "{}{}",
                    "[-]".truecolor(191, 97, 106), // red
                    " neg_num_color = None".truecolor(216, 222, 233)  // white
                ),
            }

            std::process::exit(0);
        }
        false => {}
    }

    let term_tuple: (u16, u16) = size().unwrap();
    let color_option = opt.color;
    let sigfig: i64 = if opt.sigfig >= 3 && opt.sigfig <= 7 {
        opt.sigfig
    } else {
        panic!("sigfig range must be between 3 and 7")
    };
    let debug_mode: bool = opt.debug_mode;
    let is_title_defined: bool = opt.title.chars().count() > 0;
    let is_footer_defined: bool = opt.title.chars().count() > 0;
    let is_row_display_defined: bool = opt.row_display != 25;
    let is_tty: bool = atty::is(atty::Stream::Stdout);
    let is_force_color: bool = opt.force_color;
    let is_no_dimensions: bool = opt.no_dimensions;
    let is_no_row_numbering: bool = opt.no_row_numbering;
    let is_force_all_rows: bool = opt.force_all_rows;
    let is_extend_width_length: bool = opt.extend_width_length;

    // The options below all follow the same logic:
    //   If the user provides a config file and no cli argument, use the config file
    //   If the user provides a cli argument, override the config file
    //   If the user provides no cli argument, use the config file
    //   If the user provides no cli argument and no config file, use the default value
    let extend_width_length_option: bool =
        match (config.extend_width_length, is_extend_width_length) {
            (Some(x), false) => x,
            (Some(_x), true) => opt.extend_width_length,
            (None, false) => opt.extend_width_length,
            (None, true) => opt.extend_width_length,
        };
    let title_option: &String = match (&config.title, &is_title_defined) {
        (Some(ref x), false) => &x,
        (Some(_x), true) => &opt.title,
        (None, false) => &opt.title,
        (None, true) => &opt.title,
    };

    let footer_option: &String = match (&config.footer, &is_footer_defined) {
        (Some(ref x), false) => &x,
        (Some(_x), true) => &opt.footer,
        (None, false) => &opt.footer,
        (None, true) => &opt.footer,
    };

    let row_display_option: &usize = match (&config.number, &is_footer_defined) {
        (Some(ref x), false) => x,
        (Some(_x), true) => &opt.row_display,
        (None, false) => &opt.row_display,
        (None, true) => &opt.row_display,
    };

    // nord
    let nord_meta_color: [u8; 3] = [143, 188, 187];
    let nord_header_color: [u8; 3] = [94, 129, 172];
    let nord_std_color: [u8; 3] = [216, 222, 233];
    let nord_na_color: [u8; 3] = [191, 97, 106];
    let nord_neg_num_color: [u8; 3] = [208, 135, 112];
    // one dark
    let one_dark_meta_color: [u8; 3] = [152, 195, 121];
    let one_dark_header_color: [u8; 3] = [97, 175, 239];
    let one_dark_std_color: [u8; 3] = [171, 178, 191];
    let one_dark_na_color: [u8; 3] = [224, 108, 117];
    let one_dark_neg_num_color: [u8; 3] = [229, 192, 123];
    //// gruv
    let gruvbox_meta_color: [u8; 3] = [184, 187, 38];
    let gruvbox_header_color: [u8; 3] = [215, 153, 33];
    let gruvbox_std_color: [u8; 3] = [235, 219, 178];
    let gruvbox_na_color: [u8; 3] = [204, 36, 29];
    let gruvbox_neg_num_color: [u8; 3] = [251, 73, 52];
    //// dracula
    let dracula_meta_color: [u8; 3] = [98, 114, 164];
    let dracula_header_color: [u8; 3] = [80, 250, 123];
    let dracula_std_color: [u8; 3] = [248, 248, 242];
    let dracula_na_color: [u8; 3] = [255, 121, 198];
    let dracula_neg_num_color: [u8; 3] = [188, 63, 60];
    //// solarized light
    let solarized_meta_color: [u8; 3] = [108, 113, 193];
    let solarized_header_color: [u8; 3] = [88, 110, 117];
    let solarized_std_color: [u8; 3] = [131, 148, 150];
    let solarized_na_color: [u8; 3] = [220, 50, 47];
    let solarized_neg_num_color: [u8; 3] = [42, 161, 152];

    // user args
    let lower_column_width_defined: bool = opt.lower_column_width != 2;
    let upper_column_width_defined: bool = opt.lower_column_width != 20;
    let lower_column_width: usize = match (&config.lower_column_width, &lower_column_width_defined)
    {
        (Some(ref x), false) => *x,
        (Some(_x), true) => opt.lower_column_width,
        (None, false) => opt.lower_column_width,
        (None, true) => opt.lower_column_width,
    };
    let lower_column_width: usize = if lower_column_width < 2 {
        panic!("lower-column-width must be larger than 2")
    } else {
        lower_column_width
    };

    let upper_column_width: usize = match (&config.upper_column_width, &upper_column_width_defined)
    {
        (Some(ref x), false) => *x,
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
    let (meta_color, header_color, std_color, na_color, neg_num_color) = match color_option {
        1 => (
            nord_meta_color,
            nord_header_color,
            nord_std_color,
            nord_na_color,
            nord_neg_num_color,
        ),
        2 => (
            one_dark_meta_color,
            one_dark_header_color,
            one_dark_std_color,
            one_dark_na_color,
            one_dark_neg_num_color,
        ),
        3 => (
            gruvbox_meta_color,
            gruvbox_header_color,
            gruvbox_std_color,
            gruvbox_na_color,
            gruvbox_neg_num_color,
        ),
        4 => (
            dracula_meta_color,
            dracula_header_color,
            dracula_std_color,
            dracula_na_color,
            dracula_neg_num_color,
        ),
        5 => (
            solarized_meta_color,
            solarized_header_color,
            solarized_std_color,
            solarized_na_color,
            solarized_neg_num_color,
        ),
        _ => (
            nord_meta_color,
            nord_header_color,
            nord_std_color,
            nord_na_color,
            nord_neg_num_color,
        ),
    };
    let is_color_defined = opt.color > 0;

    let meta_color = match (&config.meta_color, &is_color_defined) {
        (Some(x), false) => get_color_from_config(&x.clone()),
        (Some(_x), true) => meta_color,
        (None, false) => nord_meta_color,
        (None, true) => meta_color,
    };
    let header_color = match (&config.header_color, &is_color_defined) {
        (Some(x), false) => get_color_from_config(&x.clone()),
        (Some(_x), true) => header_color,
        (None, false) => nord_header_color,
        (None, true) => header_color,
    };
    let std_color = match (&config.std_color, &is_color_defined) {
        (Some(x), false) => get_color_from_config(&x.clone()),
        (Some(_x), true) => std_color,
        (None, false) => nord_std_color,
        (None, true) => std_color,
    };
    let na_color = match (&config.na_color, &is_color_defined) {
        (Some(x), false) => get_color_from_config(&x.clone()),
        (Some(_x), true) => na_color,
        (None, false) => nord_na_color,
        (None, true) => na_color,
    };
    let neg_num_color = match (&config.neg_num_color, &is_color_defined) {
        (Some(x), false) => get_color_from_config(&x.clone()),
        (Some(_x), true) => neg_num_color,
        (None, false) => nord_neg_num_color,
        (None, true) => neg_num_color,
    };
    // let meta_color = match (&config, is_color_defined) {
    //     (Some(x), false) => get_color_from_config(&x.clone().meta_color),
    //     (Some(_x), true) => meta_color,
    //     (None, false) => nord_meta_color,
    //     (None, true) => meta_color,
    // };
    // let header_color = match (&config, is_color_defined) {
    //     (Some(x), false) => get_color_from_config(&x.clone().header_color),
    //     (Some(_x), true) => header_color,
    //     (None, false) => nord_header_color,
    //     (None, true) => header_color,
    // };
    // let std_color = match (&config, is_color_defined) {
    //     (Some(x), false) => get_color_from_config(&x.clone().std_color),
    //     (Some(_x), true) => std_color,
    //     (None, false) => nord_std_color,
    //     (None, true) => std_color,
    // };
    // let na_color = match (&config, is_color_defined) {
    //     (Some(x), false) => get_color_from_config(&x.clone().na_color),
    //     (Some(_x), true) => na_color,
    //     (None, false) => nord_na_color,
    //     (None, true) => na_color,
    // };
    // let neg_num_color = match (&config, is_color_defined) {
    //     (Some(x), false) => get_color_from_config(&x.clone().neg_num_color),
    //     (Some(_x), true) => neg_num_color,
    //     (None, false) => nord_neg_num_color,
    //     (None, true) => neg_num_color,
    // };

    //   colname reader
    let reader_result = build_reader(&opt);
    let mut r = if let Ok(reader) = reader_result {
        reader
    } else {
        // We can safely use unwrap, because if file in case when file is None
        // build_reader would return reader created from stdin
        let path_buf = opt.file.unwrap();
        let path = path_buf.as_path();
        if let Some(path) = path.to_str() {
            eprintln!("Failed to open file: {}", path);
        } else {
            eprintln!("Failed to open file.")
        }
        return;
    };

    let rdr = r.records().collect::<Vec<_>>();
    //.take(row_display_option + 1);

    let rdr = if opt.skip_invalid_rows {
        rdr.into_iter()
            .filter_map(|record| record.ok())
            .collect::<Vec<_>>()
    } else {
        rdr.into_iter()
            .map(|record| record.expect("valid csv data"))
            .collect::<Vec<_>>()
    };

    if debug_mode {
        println!("{:?}", "StringRecord");
        println!("{:?}", rdr);
    }

    if rdr.is_empty() {
        panic!("🤖 Looks like the file exists, but is empty. No data to read. 🤖")
    };
    let cols: usize = rdr[0].len();
    let rows_in_file: usize = rdr.len();
    let rows: usize = if extend_width_length_option {
        // if extend_width_length_option print rows in file unless -n is set (issue #140)
        if is_row_display_defined {
            rdr.len().min(row_display_option + 1)
        } else {
            rdr.len().min(rows_in_file + 1)
        }
    } else {
        rdr.len().min(row_display_option + 1)
    };

    //let rows_remaining: usize = rows_in_file - rows;
    let rows_remaining: usize = match is_force_all_rows {
        true => 0,
        false => rows_in_file - rows,
    };

    let rows = match is_force_all_rows {
        true => rows_in_file,
        false => rows,
    };

    let ellipsis = '\u{2026}'.to_string();
    let row_remaining_text: String = format!("{} with {} more rows", ellipsis, rows_remaining);

    // csv gets records in rows. This makes them cols
    let mut v: Vec<Vec<&str>> = Vec::new(); //vec![vec!["#"; rows as usize]; cols as usize];
    for col in 0..cols {
        let column = rdr
            .iter()
            .take(rows)
            .map(|row| row.get(col).unwrap_or_default())
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
            vec_datatypes.push(datatype::get_col_data_type(column))
        }
        println!("{:?}", "vec_datatypes");
        println!("{:?}", vec_datatypes);
    }

    // vector of formatted values
    let vf: Vec<Vec<String>> = v
        .iter()
        .map(|col| datatype::format_strings(col, lower_column_width, upper_column_width, sigfig))
        .collect();

    if debug_mode {
        println!("{:?}", "Transposed Vector of Elements");
        println!("{:?}", v);
        println!("{:?}", "Formatted: Vector of Elements");
        println!("{:?}", vf);
    }

    println!();
    let mut vp: Vec<Vec<String>> = Vec::new();
    for r in 0..rows {
        let row = vf.iter().map(|col| col[r].to_string()).collect();
        vp.push(row);
    }

    let num_cols_to_print = if extend_width_length_option {
        cols
    } else {
        get_num_cols_to_print(cols, vp.clone(), term_tuple)
    };

    // color
    let meta_text: &str = "tv dim:";
    let div: &str = "x";
    let _ = match stdout!("{: >6}  ", "") {
        Ok(_) => Ok(()),
        Err(e) => match e.kind() {
            std::io::ErrorKind::BrokenPipe => Ok(()),
            _ => Err(e),
        },
    };
    if !is_no_dimensions {
        if is_tty || is_force_color {
            let _ = match stdoutln!(
                "{} {} {} {}",
                meta_text.truecolor(meta_color[0], meta_color[1], meta_color[2]), // tv dim:
                (rows_in_file - 1).truecolor(meta_color[0], meta_color[1], meta_color[2]), // rows
                div.truecolor(meta_color[0], meta_color[1], meta_color[2]),       // x
                (cols).truecolor(meta_color[0], meta_color[1], meta_color[2]),    // cols
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
    } else if is_tty || is_force_color {
        let _ = match stdoutln!(
            "{} {} {} {}",
            "", // tv dim:
            "", // rows
            "", // x
            "", // cols
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
        let _ = match stdout!("{: >6}  ", "") {
            Ok(_) => Ok(()),
            Err(e) => match e.kind() {
                std::io::ErrorKind::BrokenPipe => Ok(()),
                _ => Err(e),
            },
        };
        if is_tty || is_force_color {
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
    let _ = match stdout!("{: >6}  ", "") {
        Ok(_) => Ok(()),
        Err(e) => match e.kind() {
            std::io::ErrorKind::BrokenPipe => Ok(()),
            _ => Err(e),
        },
    };
    //for col in 0..cols {
    for col in 0..num_cols_to_print {
        let text = vp[0].get(col).unwrap().to_string();
        if is_tty || is_force_color {
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
    //print!("{: >6}  ", "");
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
    // main body rows after the column names
    vp.iter()
        .enumerate()
        .take(rows)
        .skip(1)
        .for_each(|(i, row)| {
            if is_tty || is_force_color {
                if is_no_row_numbering {
                    let _ = match stdout!(
                        "{: >6}  ",
                        "".truecolor(meta_color[0], meta_color[1], meta_color[2]) // this prints the row number
                    ) {
                        Ok(_) => Ok(()),
                        Err(e) => match e.kind() {
                            std::io::ErrorKind::BrokenPipe => Ok(()),
                            _ => Err(e),
                        },
                    };
                } else {
                    let _ = match stdout!(
                        "{: >6}  ",
                        i.truecolor(meta_color[0], meta_color[1], meta_color[2]) // this prints the row number
                    ) {
                        Ok(_) => Ok(()),
                        Err(e) => match e.kind() {
                            std::io::ErrorKind::BrokenPipe => Ok(()),
                            _ => Err(e),
                        },
                    };
                }
            } else if is_no_row_numbering {
                let _ = match stdout!("{: >6}  ",
                ""                                                           // this prints the row number
            ) {
                    Ok(_) => Ok(()),
                    Err(e) => match e.kind() {
                        std::io::ErrorKind::BrokenPipe => Ok(()),
                        _ => Err(e),
                    },
                };
            } else {
                let _ = match stdout!("{: >6}  ",
                ""                                                           // this prints the row number
            ) {
                    Ok(_) => Ok(()),
                    Err(e) => match e.kind() {
                        std::io::ErrorKind::BrokenPipe => Ok(()),
                        _ => Err(e),
                    },
                };
            }
            row.iter().take(num_cols_to_print).for_each(|col| {
                if is_tty || is_force_color {
                    let _ = match stdout!(
                        "{}",
                        if datatype::is_na_string_padded(col) {
                            col.truecolor(na_color[0], na_color[1], na_color[2])
                        } else if datatype::is_number(col) && datatype::is_negative_number(col) {
                            col.truecolor(neg_num_color[0], neg_num_color[1], neg_num_color[2])
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
    if rows_remaining > 0 || (cols - num_cols_to_print) > 0 {
        let _ = match stdout!("{: >6}  ", "") {
            Ok(_) => Ok(()),
            Err(e) => match e.kind() {
                std::io::ErrorKind::BrokenPipe => Ok(()),
                _ => Err(e),
            },
        };
        if is_tty || is_force_color {
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
        let extra_cols_to_mention = num_cols_to_print;
        let remainder_cols = cols - extra_cols_to_mention;
        if extra_cols_to_mention < cols {
            let meta_text_and = "and";
            let meta_text_var = "more variables";
            let meta_text_comma = ",";
            let meta_text_colon = ":";
            if is_tty || is_force_color {
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
                if is_tty || is_force_color {
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
                    if is_tty || is_force_color {
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
            } // end extra cols mentioned in footer
        }
    }

    // footer
    if !datatype::is_na(&footer_option.clone()) {
        let _ = match stdout!("{: >6}  ", "") {
            Ok(_) => Ok(()),
            Err(e) => match e.kind() {
                std::io::ErrorKind::BrokenPipe => Ok(()),
                _ => Err(e),
            },
        };
        if is_tty || is_force_color {
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
    let mut j = format!("{: >6}  ", "");
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
    let mut delimiter = b',';

    let source: Box<dyn Read> = if let Some(path) = &opt.file {
        let file = File::open(path)?;

        // Update the default delimiter by checking the file extension.
        delimiter = match path.extension() {
            Some(ext) if ext == "tsv" => b'\t',
            Some(ext) if ext == "psv" => b'|',
            _ => delimiter,
        };

        Box::new(BufReader::new(file))
    } else {
        Box::new(io::stdin())
    };

    // Cli options take precedence.
    if let Some(del) = opt.delimiter {
        delimiter = del;
    }

    let reader = ReaderBuilder::new()
        .flexible(!(opt.pedantic || opt.skip_invalid_rows))
        .has_headers(false)
        .delimiter(delimiter)
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
        assert_eq!(datatype::is_na(""), true);
        assert_eq!(datatype::is_na("NA"), true);
        assert_eq!(datatype::is_na("missing"), true);
        assert_eq!(datatype::is_na("na"), true);
        assert_eq!(datatype::is_na("1"), false);
        assert_eq!(datatype::is_na("0"), false);
    }
    // the following tests look messy, but the formatting is a necessary condition.
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
        let mut vf: Vec<Vec<String>> = vec![vec!["#".to_string(); 13_usize]; 4_usize];
        for i in 0..col_largest_width_post_proc.len() {
            vf[i] = datatype::format_strings(
                &v[i],
                col_largest_width_post_proc[i],
                col_largest_width_post_proc[i],
                3,
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
                    " NA           ",
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
        let mut vf: Vec<Vec<String>> = vec![vec!["#".to_string(); 3_usize]; 4_usize];
        for i in 0..col_largest_width_post_proc.len() {
            vf[i] = datatype::format_strings(
                &v[i],
                col_largest_width_post_proc[i],
                col_largest_width_post_proc[i],
                3,
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
        let mut vf: Vec<Vec<String>> = vec![vec!["#".to_string(); 2_usize]; 7_usize];
        for i in 0..col_largest_width_post_proc.len() {
            vf[i] = datatype::format_strings(
                &v[i],
                col_largest_width_post_proc[i],
                col_largest_width_post_proc[i],
                3,
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

    #[test]
    fn test_is_number() {
        // Integers
        assert_eq!(datatype::is_number("12345"), true);
        assert_eq!(datatype::is_number("   12345"), true);
        assert_eq!(datatype::is_number("12345   "), true);
        assert_eq!(datatype::is_number("   12345   "), true);
        assert_eq!(datatype::is_number("-12345"), true);
        assert_eq!(datatype::is_number("   -12345"), true);
        assert_eq!(datatype::is_number("-12345   "), true);
        assert_eq!(datatype::is_number("   -12345   "), true);

        // Doubles
        assert_eq!(datatype::is_number("123.45"), true);
        assert_eq!(datatype::is_number("   123.45"), true);
        assert_eq!(datatype::is_number("123.45   "), true);
        assert_eq!(datatype::is_number("   123.45   "), true);
        assert_eq!(datatype::is_number("0."), true);
        assert_eq!(datatype::is_number(".0"), true);
        assert_eq!(datatype::is_number("-123.45"), true);
        assert_eq!(datatype::is_number("   -123.45"), true);
        assert_eq!(datatype::is_number("-123.45   "), true);
        assert_eq!(datatype::is_number("   -123.45   "), true);

        // Misc
        assert_eq!(datatype::is_number("123text"), false);
        assert_eq!(datatype::is_number("text123"), false);
        assert_eq!(datatype::is_number("123.123.123"), false);
    }

    #[test]
    fn test_is_negative_number() {
        assert_eq!(datatype::is_negative_number("-12345"), true);
        assert_eq!(datatype::is_negative_number("   -12345"), true);
        assert_eq!(datatype::is_negative_number("-12345   "), true);
        assert_eq!(datatype::is_negative_number("   -12345   "), true);
        assert_eq!(datatype::is_negative_number("-12.345"), true);
        assert_eq!(datatype::is_negative_number("   -12.345"), true);
        assert_eq!(datatype::is_negative_number("-12.345   "), true);
        assert_eq!(datatype::is_negative_number("   -12.345   "), true);
        assert_eq!(datatype::is_negative_number("0.0"), false);
        assert_eq!(datatype::is_negative_number("0."), false);
        assert_eq!(datatype::is_negative_number("text"), false);
        assert_eq!(datatype::is_negative_number("-123.123.123"), false);
    }

    #[test]
    fn test_flag_f() {
        // don't have a convenient way to push data through tv
        // just want to make sure that all rows of data are printed
        // as opposed to the default 25
        let _v: Vec<Vec<&str>> = vec![
            vec!["norm1"],
            vec!["0.13985051995067665"],
            vec!["1.421378935825573"],
            vec!["0.1785258179751344"],
            vec!["0.1799228728368547"],
            vec!["-0.3601770130525013"],
            vec!["1.8513345120712446"],
            vec!["-1.0265053128729604"],
            vec!["1.1303482682646326"],
            vec!["0.3757364188183757"],
            vec!["-0.18402628567217905"],
            vec!["1.4289001286164538"],
            vec!["1.2662178084324671"],
            vec!["-1.5551459999848616"],
            vec!["-0.08176843684626088"],
            vec!["-1.253797781969998"],
            vec!["0.13521771358169038"],
            vec!["0.45934792507298405"],
            vec!["1.4218768209890322"],
            vec!["-1.8053819464500829"],
            vec!["0.14685455231223585"],
            vec!["-1.6059052140400474"],
            vec!["-0.7531078472058763"],
            vec!["1.5402633909248478"],
            vec!["0.3425162134540953"],
            vec!["-1.1338832231790217"],
            vec!["0.7680488518188675"],
            vec!["0.7707182008280404"],
            vec!["0.21419017294796816"],
            vec!["0.11186073081091127"],
            vec!["0.7042713299033002"],
            vec!["0.07309669153428934"],
            vec!["-2.277812709325943"],
            vec!["-0.7600438986427108"],
            vec!["-0.14008262537120889"],
            vec!["0.15503065800645952"],
        ];
    }
}
