use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::collections::HashMap;
use tidy_viewer_core::{FormatOptions, ColorScheme, format_table, format_csv_file, format_parquet_file};

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
        extend_width_length=false,
        force_all_rows=false,
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
        extend_width_length: bool,
        force_all_rows: bool,
        title: Option<String>,
        footer: Option<String>,
    ) -> PyResult<Self> {
        let colors = match color_theme {
            "nord" => ColorScheme::nord(),
            "one_dark" => ColorScheme::one_dark(),
            "gruvbox" => ColorScheme::gruvbox(),
            "dracula" => ColorScheme::dracula(),
            "solarized_light" => ColorScheme::solarized_light(),
            _ => ColorScheme::nord(), // default fallback
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
                extend_width_length,
                force_all_rows,
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
            _ => return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Unknown color theme: {}", theme)
            )),
        };
        Ok(())
    }
}

/// Format tabular data from Python lists
#[pyfunction]
#[pyo3(signature = (data, headers=None, options=None))]
pub fn format_data(
    data: &PyList,
    headers: Option<&PyList>,
    options: Option<&PyFormatOptions>,
) -> PyResult<String> {
    // Convert Python data to Rust format
    let mut rust_data = Vec::new();
    for row in data.iter() {
        let row_list = row.downcast::<PyList>()?;
        let mut rust_row = Vec::new();
        for cell in row_list.iter() {
            rust_row.push(cell.to_string());
        }
        rust_data.push(rust_row);
    }

    // Convert headers if provided
    let rust_headers = if let Some(h) = headers {
        let mut header_vec = Vec::new();
        for header in h.iter() {
            header_vec.push(header.to_string());
        }
        Some(header_vec)
    } else {
        None
    };

    // Use provided options or default
    let format_options = if let Some(opts) = options {
        &opts.inner
    } else {
        &FormatOptions::default()
    };

    // Format the table
    format_table(rust_data, rust_headers, format_options)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
}

/// Format a CSV file
#[pyfunction]
#[pyo3(signature = (file_path, options=None))]
pub fn format_csv(
    file_path: &str,
    options: Option<&PyFormatOptions>,
) -> PyResult<String> {
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
pub fn format_parquet(
    file_path: &str,
    options: Option<&PyFormatOptions>,
) -> PyResult<String> {
    let format_options = if let Some(opts) = options {
        &opts.inner
    } else {
        &FormatOptions::default()
    };

    format_parquet_file(file_path, format_options)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
}

/// Format a pandas DataFrame (requires conversion to lists first)
#[pyfunction]
pub fn format_dataframe(py: Python, df: &PyAny, options: Option<&PyFormatOptions>) -> PyResult<String> {
    // Get column names
    let columns = df.getattr("columns")?;
    let headers_list = columns.call_method0("tolist")?;
    
    // Get values as nested lists
    let values = df.getattr("values")?;
    let values_list = values.call_method0("tolist")?;
    
    // Convert to our format function
    format_data(
        values_list.downcast::<PyList>()?,
        Some(headers_list.downcast::<PyList>()?),
        options,
    )
}

/// Module initialization
#[pymodule]
fn _core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyFormatOptions>()?;
    m.add_function(wrap_pyfunction!(format_data, m)?)?;
    m.add_function(wrap_pyfunction!(format_csv, m)?)?;
    m.add_function(wrap_pyfunction!(format_parquet, m)?)?;
    m.add_function(wrap_pyfunction!(format_dataframe, m)?)?;
    Ok(())
}