# Conformal Regress

A beginner-friendly, speed-first conformal regression package with R-like ergonomics.

## 🎯 Core Philosophy

- **Beginner-friendly formulas**: Clear documentation with examples, gentle learning curve
- **Speed-first**: Optimize training and conformal calibration time above all
- **Minimal dependencies**: JAX + NumPy + LAPACK core, avoid heavy ecosystems
- **R-like ergonomics**: Familiar outputs and workflows for R users transitioning to Python
- **Default to Data Thinning**: Use generalized data thinning when possible to avoid data splitting

## 🚀 Quick Start

```python
import conformal_regress as cr
import pandas as pd

# Create sample data
df = pd.DataFrame({
    'sales': [100, 120, 140, 160, 180],
    'price': [10, 12, 14, 16, 18],
    'advertising': [5, 6, 7, 8, 9]
})

# Fit model with conformal prediction
model = cr.regress("sales ~ price + advertising", data=df)
print(model)  # R-like summary

# Make predictions with uncertainty
new_data = pd.DataFrame({
    'price': [15, 17],
    'advertising': [7.5, 8.5]
})
predictions = model.predict(new_data)
cr.view(predictions)  # Beautiful display
```

## 📦 Installation

```bash
pip install conformal-regress
```

For development:
```bash
git clone https://github.com/conformal-regress/conformal-regress.git
cd conformal-regress
pip install -e .
```

## 🎨 Features

### Formula Syntax

**R-compatible basics:**
```python
# Linear terms
cr.regress("y ~ x1 + x2", data=df)

# Interactions
cr.regress("y ~ x1 * x2", data=df)  # Expands to x1 + x2 + x1:x2

# Transformations
cr.regress("y ~ I(x^2) + log(z)", data=df)

# GLM-style family specification
cr.regress("y ~ x1 + x2", data=df, family="gaussian")
cr.regress("y ~ x1 + x2", data=df, family="poisson")
```

### Model Types

**Core models (all using LAPACK):**
```python
# Linear regression (default)
cr.regress("y ~ x1 + x2", data=df)

# Quantile regression 
cr.regress("y ~ x1 + x2", data=df, method="quantile", tau=0.9)

# Robust regression
cr.regress("y ~ x1 + x2", data=df, method="robust", loss="huber")

# Regularized (Lasso/Ridge)
cr.regress("y ~ x1 + x2", data=df, method="lasso", alpha=0.1)
cr.regress("y ~ x1 + x2", data=df, method="ridge", alpha=0.1)
```

### Conformal Prediction

**Automatic detection:**
```python
# Auto-detect if data thinning applicable
cr.regress("y ~ x1 + x2", data=df, 
          uncertainty="conformal",  # Auto-chooses thinning vs splitting
          family="gaussian")        # Helps with detection

# Manual override
cr.regress("y ~ x1 + x2", data=df,
          uncertainty="conformal_thinning")  # Force thinning
cr.regress("y ~ x1 + x2", data=df, 
          uncertainty="conformal_split")     # Force traditional split
```

**Fallback Strategy:**
1. Try data thinning if residuals are convolution-closed
2. Fall back to efficient train/calibration split (80/20)
3. For small samples (<100), use cross-conformal (slower but better coverage)

### Time Series Handling

```python
# User provides data with date column
df = pd.DataFrame({
    'date': pd.date_range('2020-01-01', periods=100),
    'sales': [...],
    'price': [...] 
})

# Package handles temporal ordering internally
model = cr.regress("sales ~ price", data=df, date_col="date")

# Rolling origin validation with data thinning
model = cr.regress("sales ~ price", data=df, 
                  date_col="date",
                  uncertainty="conformal_temporal",
                  cv_method="rolling_origin")

# Forecast with uncertainty
forecasts = model.forecast(horizon=30)
```

## 📊 Output Format

### Prediction Output

```python
predictions = model.predict(new_data)
# Returns DataFrame:
# | prediction | lower_90 | upper_90 | lower_95 | upper_95 | samples |
# |    12.5    |   10.2   |   14.8   |    9.8   |   15.2   | [12.1,12.3,12.7,...] |
```

### Model Summary (R-style)

```python
print(model)
# Output:
# Formula: sales ~ price + advertising
# 
# Coefficients:
#              Estimate Std. Error t value Pr(>|t|)    
# (Intercept)   100.234      5.123  19.561  < 2e-16 ***
# price          -0.521      0.089  -5.854 1.23e-07 ***
# advertising     2.345      0.234  10.021  < 2e-16 ***
# 
# Conformal Coverage: 95% (method: data_thinning)
# Residual standard error: 12.34 on 97 degrees of freedom
```

### Easy Access

```python
model.coefficients  # DataFrame with coef info
model.formula      # Original formula string  
model.coverage     # Actual coverage achieved
model.method       # "data_thinning" or "split" etc.
```

## 🎯 Example Workflows

### Beginner

```python
import conformal_regress as cr

# Simple prediction with uncertainty
model = cr.regress("price ~ bedrooms + sqft", data=housing)
print(model)  # See R-like summary

# Make predictions  
predictions = model.predict(new_houses)
cr.view(predictions)  # Uses tidy-viewer-py
```

### Time Series

```python
# Time series with conformal bands
model = cr.regress("sales ~ price + advertising", 
                   data=ts_data, 
                   date_col="date",
                   uncertainty="conformal_temporal")

# Forecast with uncertainty
forecasts = model.forecast(horizon=30)
```

### Advanced

```python
# Robust quantile regression with manual conformal
model = cr.regress("y ~ x1 + x2", 
                   data=df,
                   method="quantile", 
                   tau=0.9,
                   uncertainty="conformal_thinning",
                   family="gamma")
```

## 🔧 Performance Optimizations

**Speed Targets:**
- Linear regression: Sub-second for 10k samples
- Conformal calibration: <10% overhead vs base model
- Memory: Lazy evaluation where possible

**JAX Integration:**
- JIT compile prediction functions
- Vectorized conformal score computation
- GPU support for large datasets (optional)

## 📚 Documentation

For detailed documentation, visit: [docs.conformal-regress.org](https://docs.conformal-regress.org)

### Key Concepts

**Data Thinning vs Data Splitting:**
- **Data Thinning**: Uses the full dataset when residuals are convolution-closed
- **Data Splitting**: Traditional train/calibration split when thinning not applicable

**Convolution-Closed Distributions:**
- Gaussian, Student's t, Cauchy, and other location-scale families
- Allows for more efficient conformal prediction without data splitting

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/conformal-regress/conformal-regress.git
cd conformal-regress
pip install -e ".[dev]"
pytest  # Run tests
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by R's `lm()` and `glm()` functions
- Data thinning approach based on Daniella Witten's research
- Built with JAX for speed and GPU support
- Formula parsing powered by `formulaic`

## 📞 Support

- 📧 Email: team@conformal-regress.org
- 💬 Discussions: [GitHub Discussions](https://github.com/conformal-regress/conformal-regress/discussions)
- 🐛 Issues: [GitHub Issues](https://github.com/conformal-regress/conformal-regress/issues)

---

**Made with ❤️ for the Python data science community**
