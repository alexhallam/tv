# conformal-regress

Fast, beginner-friendly conformal regression with R-like ergonomics and automatic data thinning.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

**conformal-regress** brings the familiar feel of R regression modeling to Python with modern conformal prediction capabilities. The package automatically detects when data thinning can be used for faster conformal intervals, falling back to traditional methods when needed.

### Key Features

- **R-like ergonomics**: Familiar formula syntax and model output
- **Automatic conformal prediction**: Built-in uncertainty quantification with minimal overhead
- **Data thinning**: Automatically detects when data thinning can replace data splitting (faster!)
- **Speed-optimized**: JAX + LAPACK backends for sub-second fitting on 10k+ samples
- **Beginner-friendly**: Clear documentation and gentle learning curve
- **Time series support**: Temporal conformal prediction for time-aware analysis

## Quick Start

### Installation

```bash
pip install conformal-regress
```

### Basic Usage

```python
import conformal_regress as cr

# Get example data
housing = cr.get_example_data("housing")

# Fit model with automatic conformal prediction
model = cr.regress("price ~ bedrooms + sqft", data=housing)

# R-style summary
print(model)
# Formula: price ~ bedrooms + sqft
# 
# Coefficients:
#              Estimate Std. Error t value Pr(>|t|)    
# (Intercept)   100.234      5.123  19.561  < 2e-16 ***
# bedrooms       50.123      2.234  22.442  < 2e-16 ***
# sqft            0.145      0.012  12.083  < 2e-16 ***
# 
# Multiple R-squared: 0.8234
# Conformal method: data_thinning

# Make predictions with uncertainty
predictions = model.predict(new_data)
cr.view(predictions)  # Beautiful table display
```

## Core Philosophy

### 1. Beginner-Friendly Formulas
Clear R-style syntax that's easy to learn:

```python
# Basic regression
cr.regress("sales ~ price + advertising", data=df)

# Interactions
cr.regress("sales ~ price * advertising", data=df)  # Expands to price + advertising + price:advertising

# Transformations
cr.regress("y ~ I(x^2) + log(z)", data=df)
```

### 2. Speed-First Architecture

- **JAX JIT compilation**: Sub-second fitting for 10k samples
- **Efficient LAPACK**: QR, SVD, and Cholesky solvers
- **Data thinning**: Skip data splitting when mathematically valid
- **Minimal dependencies**: Core functionality with lightweight stack

### 3. Default to Data Thinning

Traditional conformal prediction requires splitting your data into training and calibration sets. This package implements **generalized data thinning** (following Wittens et al.) which can provide valid conformal intervals without data splitting for convolution-closed distributions:

```python
model = cr.regress("y ~ x1 + x2", data=df)
print(f"Method used: {model.conformal_method}")  # Often 'data_thinning'
print(f"Eligible: {model.data_thinning_eligible}")  # True for Gaussian residuals
```

When data thinning isn't applicable, the package automatically falls back to traditional split conformal methods.

## API Examples

### Basic Regression

```python
import conformal_regress as cr

# Linear regression
model = cr.regress("price ~ bedrooms + sqft + garage", data=housing)
print(model.summary())

# Access R-like properties
print(f"R²: {model.r_squared:.3f}")
print(f"AIC: {model.aic:.1f}")
print(model.coefficients)  # Coefficient table with p-values
```

### Uncertainty Quantification

```python
# Automatic conformal method selection
model = cr.regress("sales ~ price + advertising", data=sales_data)

# Manual method selection
model = cr.regress("sales ~ price + advertising", 
                  data=sales_data,
                  uncertainty="conformal_thinning")  # Force data thinning

# Traditional split conformal
model = cr.regress("sales ~ price + advertising", 
                  data=sales_data,
                  uncertainty="conformal_split")

# No uncertainty quantification
model = cr.regress("sales ~ price + advertising", 
                  data=sales_data,
                  uncertainty="none")
```

### Time Series Analysis

```python
# Time series with temporal conformal prediction
ts_model = cr.regress("sales ~ price + day_of_week", 
                     data=ts_data,
                     date_col="date",
                     uncertainty="conformal_temporal")

# Forecast with uncertainty
forecasts = ts_model.forecast(horizon=30)
cr.view(forecasts)
```

### Advanced Methods

```python
# Ridge regression
ridge_model = cr.regress("y ~ x1 + x2 + x3", 
                        data=df, 
                        method="ridge", 
                        alpha=1.0)

# Quantile regression (when implemented)
quantile_model = cr.regress("y ~ x1 + x2", 
                           data=df, 
                           method="quantile", 
                           tau=0.9)

# Robust regression (when implemented)
robust_model = cr.regress("y ~ x1 + x2", 
                         data=df, 
                         method="robust")
```

## Formula Syntax

### Supported Patterns

```python
# Basic terms
"y ~ x1 + x2 + x3"

# Interactions
"y ~ x1 * x2"          # Expands to: x1 + x2 + x1:x2
"y ~ x1 + x2 + x1:x2"  # Explicit interaction

# Transformations
"y ~ I(x^2) + log(z)"  # Power and log transforms
"y ~ poly(x, 2)"       # Polynomial terms (when implemented)

# No intercept
"y ~ x1 + x2 - 1"      # Or use fit_intercept=False
```

### GLM-Style Family Specification

```python
# Helps with conformal method detection
cr.regress("y ~ x1 + x2", data=df, family="gaussian")    # Default
cr.regress("y ~ x1 + x2", data=df, family="poisson")     # Poisson GLM
cr.regress("y ~ x1 + x2", data=df, family="gamma")       # Gamma GLM
```

## Conformal Prediction Methods

### Automatic Detection

The package automatically chooses the best conformal method:

```python
model = cr.regress("y ~ x1 + x2", data=df, uncertainty="conformal")

# Check what was chosen
print(f"Method: {model.conformal_method}")        # 'data_thinning' or 'split'
print(f"Eligible: {model.data_thinning_eligible}") # True/False
print(f"Reason: {model.data_thinning_reason}")     # Explanation
```

### Method Details

1. **Data Thinning** (`conformal_thinning`): Uses theoretical properties of convolution-closed distributions. Faster, no data splitting required.

2. **Split Conformal** (`conformal_split`): Traditional train/calibration split approach. Works for any distribution.

3. **Temporal Conformal** (`conformal_temporal`): Respects time series structure using rolling windows.

4. **Cross Conformal** (`conformal_cross`): Better coverage for small datasets using cross-validation.

### Coverage Guarantees

All methods provide finite-sample coverage guarantees:

```python
predictions = model.predict(new_data, alpha=0.05)  # 95% coverage
print(f"Achieved coverage: {model.coverage_achieved:.1%}")
```

## Performance

### Speed Targets

- **Linear regression**: Sub-second for 10k samples
- **Conformal calibration**: <10% overhead vs base model
- **Memory**: Lazy evaluation, minimal memory footprint

### Backends

- **JAX**: JIT-compiled prediction functions
- **LAPACK**: QR, SVD, Cholesky decomposition via SciPy
- **Optional GPU**: Large dataset support via JAX

### Benchmarks

```python
import time
import conformal_regress as cr

# Generate large dataset
large_data = cr.get_example_data("housing")  # 1k samples
large_data = pd.concat([large_data] * 10)     # 10k samples

# Time fitting
start = time.time()
model = cr.regress("price ~ bedrooms + sqft + garage", data=large_data)
fit_time = time.time() - start

print(f"Fit time: {fit_time:.2f}s")  # Typically <1s

# Time prediction
start = time.time()
predictions = model.predict()
pred_time = time.time() - start

print(f"Prediction time: {pred_time:.3f}s")  # Typically <0.1s
```

## Examples and Tutorials

### Complete Workflow Example

```python
import conformal_regress as cr
import pandas as pd

# 1. Load and explore data
housing = cr.get_example_data("housing")
print(housing.describe())

# 2. Fit model with automatic conformal prediction
model = cr.regress("price ~ bedrooms + sqft + garage", data=housing)

# 3. Examine model
print(model)  # R-style summary
print(f"\nConformal method: {model.conformal_method}")
print(f"Data thinning eligible: {model.data_thinning_eligible}")

# 4. Make predictions
new_houses = pd.DataFrame({
    'bedrooms': [3, 4, 2],
    'sqft': [1800, 2200, 1400],
    'garage': [1, 2, 1]
})

predictions = model.predict(new_houses)
cr.view(predictions)

# 5. Access model diagnostics
print(f"\nModel fit:")
print(f"R²: {model.r_squared:.3f}")
print(f"RMSE: {model.residual_std_error:.0f}")
print(f"AIC: {model.aic:.1f}")
```

### Time Series Example

```python
# Generate time series data
ts_data = cr.get_example_data("timeseries")

# Fit temporal model
ts_model = cr.regress("sales ~ price + day_of_week", 
                     data=ts_data,
                     date_col="date",
                     uncertainty="conformal_temporal")

# Examine temporal conformal setup
print(f"Rolling window size: {ts_model.rolling_window_size}")
print(f"Date range: {ts_model.date_range}")

# Forecast future values
future_forecasts = ts_model.forecast(horizon=30)
print(future_forecasts)
```

## Installation and Setup

### Requirements

- Python 3.8+
- JAX >= 0.4.0
- NumPy >= 1.21.0
- pandas >= 1.3.0
- formulaic >= 0.6.0
- SciPy >= 1.7.0

### Optional Dependencies

```bash
# For enhanced display
pip install tidy-viewer-py

# For development
pip install conformal-regress[dev]

# For documentation
pip install conformal-regress[docs]
```

### Development Installation

```bash
git clone https://github.com/your-username/conformal-regress.git
cd conformal-regress
pip install -e .
```

## Comparison with Other Packages

### vs. scikit-learn

| Feature | conformal-regress | scikit-learn |
|---------|------------------|--------------|
| Formula syntax | ✅ R-style | ❌ Manual X, y |
| Conformal prediction | ✅ Built-in | ❌ Separate package |
| Data thinning | ✅ Automatic | ❌ Not available |
| Speed | ✅ JAX-optimized | ⚡ Fast |
| R-like output | ✅ Native | ❌ Manual |

### vs. statsmodels

| Feature | conformal-regress | statsmodels |
|---------|------------------|-------------|
| Conformal prediction | ✅ Built-in | ❌ Not available |
| Speed | ✅ JAX-optimized | ⚡ Moderate |
| Formula syntax | ✅ Compatible | ✅ Patsy-based |
| Time series | ✅ Conformal | ✅ Traditional |
| Beginner-friendly | ✅ Designed for | ⚡ Learning curve |

## Contributing

We welcome contributions! Areas of particular interest:

1. **Additional regression methods**: Quantile, robust, Bayesian
2. **Enhanced formula parsing**: Splines, polynomials, custom transformations
3. **RandLAPack integration**: For extremely large datasets
4. **GPU acceleration**: Enhanced JAX utilization
5. **Additional conformal methods**: Jackknife+, CV+, etc.

### Development Setup

```bash
git clone https://github.com/your-username/conformal-regress.git
cd conformal-regress
pip install -e .[dev]

# Run tests
python -m pytest tests/

# Run examples
python examples/basic_usage.py
```

## Citation

If you use conformal-regress in your research, please cite:

```bibtex
@software{conformal_regress,
  title={conformal-regress: Fast conformal prediction with data thinning},
  author={Conformal Regress Team},
  year={2024},
  url={https://github.com/your-username/conformal-regress}
}
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## References

- Wittens, D. et al. "Generalized Data Thinning for Conformal Prediction"
- Vovk, V. et al. "Algorithmic Learning in a Random World" (2005)
- Shafer, G. & Vovk, V. "A Tutorial on Conformal Prediction" (2008)
- Lei, J. et al. "Distribution-Free Prediction Intervals for Regression" (2013)