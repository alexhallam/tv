# conformal-regress

Beginner-friendly, fast conformal regression with formula syntax and JAX acceleration.

## Quickstart

```python
import pandas as pd
import conformal_regress as cr

# Sample data
n = 200
rng = pd.Series(range(n))
df = pd.DataFrame({
    "y": rng * 0.5 + 3.0,
    "x": rng,
})

model = cr.regress("y ~ x", data=df, family="gaussian", uncertainty="conformal")
print(model)

new_data = pd.DataFrame({"x": [10, 20, 30]})
preds = model.predict(new_data)
print(preds)
```

## Features
- Formula syntax powered by `formulaic`
- OLS with conformal prediction intervals (thinning, split, or cross-conformal)
- Ridge, Lasso, Quantile, and Robust (Huber) options
- Time-aware splitting for temporal data
- Optional JAX acceleration for predictions

## Install (editable)
```bash
pip install -e .
```
