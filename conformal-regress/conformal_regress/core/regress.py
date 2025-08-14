"""
Main user-facing regress function.
"""

import pandas as pd
from typing import Optional, Union, Dict, Any

from .model import RegressModel


def regress(formula: str, 
           data: pd.DataFrame,
           method: str = "linear",
           uncertainty: str = "conformal",
           family: str = "gaussian",
           date_col: Optional[str] = None,
           alpha: Optional[float] = None,
           tau: Optional[float] = None,
           fit_intercept: bool = True,
           solver: str = "qr",
           **kwargs) -> RegressModel:
    """
    Fit regression model with automatic conformal prediction.
    
    This is the main user-facing function that provides R-like ergonomics
    for regression analysis with conformal uncertainty quantification.
    
    Parameters
    ----------
    formula : str
        R-style formula string, e.g., "y ~ x1 + x2" or "sales ~ price * advertising"
        Supports:
        - Linear terms: y ~ x1 + x2
        - Interactions: y ~ x1 * x2 (expands to x1 + x2 + x1:x2)
        - Transformations: y ~ I(x^2) + log(z)
        
    data : pd.DataFrame
        Input data containing all variables in the formula
        
    method : str, default "linear"
        Regression method to use:
        - "linear": Ordinary least squares (default)
        - "quantile": Quantile regression (requires tau parameter)
        - "robust": Robust regression with Huber loss
        - "lasso": Lasso regularization (requires alpha parameter)
        - "ridge": Ridge regularization (requires alpha parameter)
        
    uncertainty : str, default "conformal"
        Uncertainty quantification method:
        - "conformal": Auto-detect best conformal method (data thinning vs splitting)
        - "conformal_thinning": Force data thinning conformal prediction
        - "conformal_split": Force train/calibration split conformal prediction
        - "conformal_temporal": Temporal conformal for time series
        - "bootstrap": Bootstrap prediction intervals
        - "none": No uncertainty quantification
        
    family : str, default "gaussian"
        Distribution family (helps with conformal method selection):
        - "gaussian": Normal distribution (linear regression)
        - "poisson": Poisson distribution
        - "gamma": Gamma distribution
        - "binomial": Binomial distribution
        
    date_col : str, optional
        Name of date column for time series analysis. When specified:
        - Enables temporal conformal prediction
        - Allows forecasting with model.forecast()
        - Respects temporal ordering in data splits
        
    alpha : float, optional
        Regularization parameter for lasso/ridge regression
        
    tau : float, optional
        Quantile level for quantile regression (e.g., 0.5 for median, 0.9 for 90th percentile)
        
    fit_intercept : bool, default True
        Whether to fit an intercept term
        
    solver : str, default "qr"
        Numerical solver method:
        - "qr": QR decomposition (most stable)
        - "svd": Singular value decomposition (handles rank deficiency)
        - "cholesky": Cholesky decomposition (fastest for well-conditioned problems)
        
    **kwargs
        Additional arguments passed to the underlying model
        
    Returns
    -------
    RegressModel
        Fitted regression model with the following methods:
        - predict(new_data): Make predictions with uncertainty bands
        - summary(): R-style model summary
        - forecast(horizon): Time series forecasting (if date_col specified)
        
    Examples
    --------
    Basic linear regression:
    >>> model = regress("price ~ bedrooms + sqft", data=housing)
    >>> print(model)  # R-style summary
    >>> predictions = model.predict(new_houses)
    
    With interactions:
    >>> model = regress("sales ~ price * advertising", data=sales_data)
    
    Time series with conformal prediction:
    >>> model = regress("sales ~ price + advertising", 
    ...                 data=ts_data, 
    ...                 date_col="date",
    ...                 uncertainty="conformal_temporal")
    >>> forecasts = model.forecast(horizon=30)
    
    Quantile regression:
    >>> model = regress("y ~ x1 + x2", data=df, method="quantile", tau=0.9)
    
    Ridge regression:
    >>> model = regress("y ~ x1 + x2", data=df, method="ridge", alpha=1.0)
    
    Manual conformal method:
    >>> model = regress("y ~ x1 + x2", data=df, uncertainty="conformal_thinning")
    
    Notes
    -----
    The package automatically detects when data thinning can be used for conformal
    prediction, which is faster than traditional train/calibration splits. This
    follows the generalized data thinning framework for convolution-closed
    distributions.
    
    For small datasets (<100 samples), the package may use cross-conformal
    prediction for better coverage guarantees.
    
    Time series analysis automatically handles temporal ordering and provides
    specialized conformal methods that respect the time structure.
    """
    
    # Validate basic inputs
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    
    if not isinstance(formula, str):
        raise TypeError("formula must be a string")
    
    # Handle method-specific parameters
    model_kwargs = kwargs.copy()
    model_kwargs.update({
        'fit_intercept': fit_intercept,
        'solver': solver
    })
    
    # Add method-specific parameters
    if method in ["lasso", "ridge"] and alpha is not None:
        model_kwargs['alpha'] = alpha
    elif method == "quantile" and tau is not None:
        model_kwargs['tau'] = tau
    
    # Create and fit model
    model = RegressModel(
        formula=formula,
        data=data,
        method=method,
        uncertainty=uncertainty,
        family=family,
        date_col=date_col,
        **model_kwargs
    )
    
    # Fit the model
    model.fit()
    
    return model


# Convenience functions for specific methods
def linear_regress(formula: str, data: pd.DataFrame, **kwargs) -> RegressModel:
    """Convenience function for linear regression."""
    return regress(formula, data, method="linear", **kwargs)


def quantile_regress(formula: str, data: pd.DataFrame, tau: float = 0.5, **kwargs) -> RegressModel:
    """Convenience function for quantile regression."""
    return regress(formula, data, method="quantile", tau=tau, **kwargs)


def robust_regress(formula: str, data: pd.DataFrame, **kwargs) -> RegressModel:
    """Convenience function for robust regression.""" 
    return regress(formula, data, method="robust", **kwargs)


def ridge_regress(formula: str, data: pd.DataFrame, alpha: float = 1.0, **kwargs) -> RegressModel:
    """Convenience function for ridge regression."""
    return regress(formula, data, method="ridge", alpha=alpha, **kwargs)


def lasso_regress(formula: str, data: pd.DataFrame, alpha: float = 1.0, **kwargs) -> RegressModel:
    """Convenience function for lasso regression."""
    return regress(formula, data, method="lasso", alpha=alpha, **kwargs)


def ts_regress(formula: str, data: pd.DataFrame, date_col: str, **kwargs) -> RegressModel:
    """Convenience function for time series regression."""
    return regress(formula, data, date_col=date_col, 
                  uncertainty="conformal_temporal", **kwargs)