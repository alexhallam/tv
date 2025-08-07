#[derive(Debug, Clone)]
pub struct FormatOptions {
    pub max_rows: Option<usize>,
    pub max_col_width: usize,
    pub min_col_width: usize,
    pub use_color: bool,
    pub colors: ColorScheme,
    pub delimiter: String,
    pub significant_figures: usize,
    pub preserve_scientific: bool,
    pub max_decimal_width: usize,
    pub no_dimensions: bool,
    pub no_row_numbering: bool,
    pub title: Option<String>,
    pub footer: Option<String>,
}

impl Default for FormatOptions {
    fn default() -> Self {
        Self {
            max_rows: Some(25),
            max_col_width: 20,
            min_col_width: 2,
            use_color: true,
            colors: ColorScheme::default(),
            delimiter: ",".to_string(),
            significant_figures: 3,
            preserve_scientific: false,
            max_decimal_width: 13,
            no_dimensions: false,
            no_row_numbering: false,  // Match Rust tv CLI terminal behavior (show row numbers by default)
            title: None,
            footer: None,
        }
    }
}

#[derive(Debug, Clone)]
pub struct ColorScheme {
    pub meta_color: [u8; 3],
    pub header_color: [u8; 3],
    pub std_color: [u8; 3],
    pub na_color: [u8; 3],
    pub neg_num_color: [u8; 3],
}

impl Default for ColorScheme {
    fn default() -> Self {
        Self::nord()
    }
}

impl ColorScheme {
    pub fn nord() -> Self {
        Self {
            meta_color: [143, 188, 187],
            header_color: [94, 129, 172],
            std_color: [216, 222, 233],
            na_color: [191, 97, 106],
            neg_num_color: [208, 135, 112],
        }
    }
    
    pub fn one_dark() -> Self {
        Self {
            meta_color: [152, 195, 121],
            header_color: [97, 175, 239],
            std_color: [171, 178, 191],
            na_color: [224, 108, 117],
            neg_num_color: [229, 192, 123],
        }
    }
    
    pub fn gruvbox() -> Self {
        Self {
            meta_color: [184, 187, 38],
            header_color: [215, 153, 33],
            std_color: [235, 219, 178],
            na_color: [204, 36, 29],
            neg_num_color: [251, 73, 52],
        }
    }
    
    pub fn dracula() -> Self {
        Self {
            meta_color: [98, 114, 164],
            header_color: [80, 250, 123],
            std_color: [248, 248, 242],
            na_color: [255, 121, 198],
            neg_num_color: [188, 63, 60],
        }
    }
    
    pub fn solarized_light() -> Self {
        Self {
            meta_color: [108, 113, 193],
            header_color: [88, 110, 117],
            std_color: [131, 148, 150],
            na_color: [220, 50, 47],
            neg_num_color: [42, 161, 152],
        }
    }
}



