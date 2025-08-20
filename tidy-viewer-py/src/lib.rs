use pyo3::prelude::*;
use pyo3::types::{PyAny, PyModule};
use std::collections::HashMap;

// Import from core library
use tidy_viewer_core::format_strings;

mod formatting;
mod types;

use crate::formatting::{format_csv_file, format_table};
use crate::types::{ColorScheme, FormatOptions};

/// Python class for formatting options
#[pyclass]
#[derive(Clone)]
pub struct PyFormatOptions {
    inner: FormatOptions,
}

#[pymethods]
impl PyFormatOptions {
    #[new]
    #[pyo3(signature = (
        max_rows=None,
        max_col_width=20,
        min_col_width=2,
        use_color=true,
        color_theme="nord",
        delimiter=",",
        significant_figures=3,
        preserve_scientific=false,
        max_decimal_width=13,
        no_dimensions=false,
        no_row_numbering=false,
        title=None,
        footer=None
    ))]
    pub fn new(
        max_rows: Option<usize>,
        max_col_width: usize,
        min_col_width: usize,
        use_color: bool,
        color_theme: &str,
        delimiter: &str,
        significant_figures: usize,
        preserve_scientific: bool,
        max_decimal_width: usize,
        no_dimensions: bool,
        no_row_numbering: bool,

        title: Option<String>,
        footer: Option<String>,
    ) -> PyResult<Self> {
        let colors = match color_theme {
            "nord" => ColorScheme::nord(),
            "one_dark" => ColorScheme::one_dark(),
            "gruvbox" => ColorScheme::gruvbox(),
            "dracula" => ColorScheme::dracula(),
            "solarized_light" => ColorScheme::solarized_light(),
            _ => ColorScheme::nord(),
        };

        Ok(PyFormatOptions {
            inner: FormatOptions {
                max_rows,
                max_col_width,
                min_col_width,
                use_color,
                colors,
                delimiter: delimiter.to_string(),
                significant_figures,
                preserve_scientific,
                max_decimal_width,
                no_dimensions,
                no_row_numbering,

                title,
                footer,
            },
        })
    }

    /// Set color theme
    pub fn set_color_theme(&mut self, theme: &str) -> PyResult<()> {
        self.inner.colors = match theme {
            "nord" => ColorScheme::nord(),
            "one_dark" => ColorScheme::one_dark(),
            "gruvbox" => ColorScheme::gruvbox(),
            "dracula" => ColorScheme::dracula(),
            "solarized_light" => ColorScheme::solarized_light(),
            _ => {
                return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                    "Unknown color theme: {}",
                    theme
                )))
            }
        };
        Ok(())
    }
}

/// Format tabular data from Python lists
#[pyfunction]
#[pyo3(signature = (data, headers=None, data_types=None, options=None))]
pub fn format_data(
    data: Vec<Vec<String>>,
    headers: Option<Vec<String>>,
    data_types: Option<Vec<String>>,
    options: Option<&PyFormatOptions>,
) -> PyResult<String> {
    let format_options = if let Some(opts) = options {
        &opts.inner
    } else {
        &FormatOptions::default()
    };

    format_table(data, headers, data_types, format_options)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
}

/// Format a CSV file
#[pyfunction]
#[pyo3(signature = (file_path, options=None))]
pub fn format_csv(file_path: &str, options: Option<&PyFormatOptions>) -> PyResult<String> {
    let format_options = if let Some(opts) = options {
        &opts.inner
    } else {
        &FormatOptions::default()
    };

    format_csv_file(file_path, format_options)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
}

/// Format a Parquet file
#[pyfunction]
#[pyo3(signature = (file_path, options=None))]
pub fn format_parquet(file_path: &str, options: Option<&PyFormatOptions>) -> PyResult<String> {
    let format_options = if let Some(opts) = options {
        &opts.inner
    } else {
        &FormatOptions::default()
    };

    crate::formatting::format_parquet_file(file_path, format_options)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
}

/// Format an Arrow file
#[pyfunction]
#[pyo3(signature = (file_path, options=None))]
pub fn format_arrow(file_path: &str, options: Option<&PyFormatOptions>) -> PyResult<String> {
    let format_options = if let Some(opts) = options {
        &opts.inner
    } else {
        &FormatOptions::default()
    };

    crate::formatting::format_arrow_file(file_path, format_options)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
}

/// Format a dictionary of lists
#[pyfunction]
pub fn format_dict_of_lists(
    data_dict: &Bound<'_, PyAny>,
    options: Option<&PyFormatOptions>,
) -> PyResult<String> {
    let dict: HashMap<String, Vec<String>> = data_dict.extract()?;

    if dict.is_empty() {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Dictionary is empty",
        ));
    }

    // Get headers (keys)
    let headers: Vec<String> = dict.keys().cloned().collect();

    // Get maximum length
    let max_len = dict.values().map(|v| v.len()).max().unwrap_or(0);

    // Convert to list of lists
    let mut data = Vec::new();
    for i in 0..max_len {
        let mut row = Vec::new();
        for header in &headers {
            let na_value = "NA".to_string();
            let value = dict.get(header).and_then(|v| v.get(i)).unwrap_or(&na_value);
            row.push(value.clone());
        }
        data.push(row);
    }

    format_data(data, Some(headers), None, options)
}

/// Format a list of dictionaries
#[pyfunction]
pub fn format_list_of_dicts(
    data_list: &Bound<'_, PyAny>,
    options: Option<&PyFormatOptions>,
) -> PyResult<String> {
    let list: Vec<HashMap<String, String>> = data_list.extract()?;

    if list.is_empty() {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "List is empty",
        ));
    }

    // Get all unique keys
    let mut all_keys = std::collections::HashSet::new();
    for dict in &list {
        all_keys.extend(dict.keys().cloned());
    }
    let headers: Vec<String> = all_keys.into_iter().collect();

    // Convert to list of lists
    let mut data = Vec::new();
    for dict in &list {
        let mut row = Vec::new();
        for header in &headers {
            let na_value = "NA".to_string();
            let value = dict.get(header).unwrap_or(&na_value);
            row.push(value.clone());
        }
        data.push(row);
    }

    format_data(data, Some(headers), None, options)
}

/// Module initialization
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyFormatOptions>()?;
    m.add_function(wrap_pyfunction!(format_data, m)?)?;
    m.add_function(wrap_pyfunction!(format_csv, m)?)?;
    m.add_function(wrap_pyfunction!(format_parquet, m)?)?;
    m.add_function(wrap_pyfunction!(format_arrow, m)?)?;
    m.add_function(wrap_pyfunction!(format_dict_of_lists, m)?)?;
    m.add_function(wrap_pyfunction!(format_list_of_dicts, m)?)?;
    Ok(())
}
