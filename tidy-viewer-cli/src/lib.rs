//! # Tidy-Viewer Core Library
//!
//! This crate contains the core formatting logic for tidy-viewer,
//! shared between the CLI and Python bindings.
//!
//! ## Overview
//!
//! The core library provides data type inference, string formatting, and significant figure
//! handling for tabular data. It's designed to be used by both the command-line interface
//! and Python bindings to ensure consistent behavior across all interfaces.
//!
//! ## Key Features
//!
//! - **Data Type Inference**: Automatically detect and format different data types
//! - **Significant Figure Formatting**: Intelligent number formatting with configurable precision
//! - **Column Width Calculation**: Smart column width calculation with Unicode support
//! - **NA Handling**: Consistent handling of missing values across all formats
//! - **Unicode Support**: Full Unicode character width calculation and truncation
//!
//! ## Usage
//!
//! ```rust
//! use tidy_viewer::{format_strings, calculate_column_width, is_na};
//!
//! // Format a column of strings
//! let data = vec!["123.456", "NA", "-42.1", "hello"];
//! let formatted = format_strings(
//!     &data,
//!     2,    // min_col_width
//!     20,   // max_col_width
//!     3,    // significant_figures
//!     false, // preserve_scientific
//!     13,   // max_decimal_width
//! );
//!
//! // Calculate optimal column width
//! let width = calculate_column_width(&formatted, 2, 20);
//!
//! // Check if a value is NA
//! let is_missing = is_na("NA");
//! ```
//!
//! ## Data Types Supported
//!
//! - **Numbers**: Integers, floats, scientific notation
//! - **Dates**: Various date formats
//! - **Times**: Time formats
//! - **Logical**: Boolean values (true/false)
//! - **Text**: General string data
//! - **NA**: Missing values
//!
//! ## Significant Figures
//!
//! The library provides intelligent significant figure formatting through the `DecimalSplits` struct:
//!
//! ```rust
//! use tidy_viewer::{DecimalSplits, get_final_string};
//!
//! // Create a DecimalSplits instance for formatting
//! let splits = DecimalSplits {
//!     val: 123.456,
//!     sigfig: 3,
//! };
//!
//! // Get the formatted string
//! let result = splits.final_string();
//! assert_eq!(result, "123.");
//! ```

pub mod datatype;

// Re-export main functions
pub use datatype::calculate_column_width;
pub use datatype::format_if_na;
pub use datatype::format_if_num;
pub use datatype::format_strings;
pub use datatype::get_col_data_type;
pub use datatype::infer_type_from_string;
pub use datatype::is_date;
pub use datatype::is_date_time;
pub use datatype::is_double;
pub use datatype::is_integer;
pub use datatype::is_logical;
pub use datatype::is_na;
pub use datatype::is_na_string_padded;
pub use datatype::is_negative_number;
pub use datatype::is_scientific_notation;
pub use datatype::is_time;
pub use datatype::parse_delimiter;
pub use datatype::ValueType;

// Re-export sigfig module
pub use datatype::sigfig::{get_final_string, DecimalSplits};
