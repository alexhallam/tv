"""
Main regression model class that provides R-like interface.
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, List, Union, Tuple
import warnings

from ..models.linear import LinearRegression
from ..utils.display import format_summary, create_coefficient_table
from ..utils.formula_utils import parse_formula, validate_formula
from ..utils.data_utils import prepare_data, validate_data


class RegressModel:
    """
    Main regression model class with R-like interface.
    
    This class provides a unified interface for different regression methods
    with automatic conformal prediction capabilities.
    """
    
    def __init__(self, formula: str, data: pd.DataFrame,
                 method: str = "linear",
                 uncertainty: str = "conformal",
                 family: str = "gaussian", 
                 date_col: Optional[str] = None,
                 **kwargs):
        """
        Initialize regression model.
        
        Parameters
        ----------
        formula : str
            R-style formula string like "y ~ x1 + x2"
        data : pd.DataFrame
            Input data
        method : str, default "linear"
            Regression method: "linear", "quantile", "robust", "lasso", "ridge"
        uncertainty : str, default "conformal"
            Uncertainty quantification method: "conformal", "conformal_thinning", 
            "conformal_split", "conformal_temporal", "bootstrap", or "none"
        family : str, default "gaussian"
            Distribution family for GLM-style specification
        date_col : str, optional
            Date column for time series analysis
        **kwargs
            Additional arguments passed to the underlying model
        """
        self.formula = formula
        self.original_data = data.copy()
        self.method = method
        self.uncertainty = uncertainty
        self.family = family
        self.date_col = date_col
        self.kwargs = kwargs
        
        # Model state
        self.backend_model_ = None
        self.X_ = None
        self.y_ = None
        self.formula_metadata_ = None
        self.data_metadata_ = None
        
        # Conformal prediction state
        self.conformal_method = None
        self.conformal_alpha = 0.05  # Default 95% coverage
        self.coverage_achieved = None
        self.data_thinning_eligible = None
        self.data_thinning_reason = None
        
        # For time series
        self.temporal_conformal = False
        self.rolling_window_size = None
        
        # Validate inputs
        self._validate_inputs()
        
        # Prepare data and parse formula
        self._prepare_data()
        
        # Initialize backend model
        self._initialize_backend()
    
    def _validate_inputs(self):
        """Validate input parameters."""
        # Validate formula
        validation = validate_formula(self.formula, self.original_data)
        if not validation['valid']:
            raise ValueError(f"Invalid formula: {'; '.join(validation['errors'])}")
        
        # Validate data
        data_validation = validate_data(self.original_data, self.formula)
        if not data_validation['valid']:
            raise ValueError(f"Invalid data: {'; '.join(data_validation['errors'])}")
        
        if data_validation['warnings']:
            for warning in data_validation['warnings']:
                warnings.warn(warning)
        
        # Validate method
        valid_methods = ["linear", "quantile", "robust", "lasso", "ridge"]
        if self.method not in valid_methods:
            raise ValueError(f"Method must be one of {valid_methods}")
        
        # Validate uncertainty method
        valid_uncertainty = ["conformal", "conformal_thinning", "conformal_split", 
                           "conformal_temporal", "bootstrap", "none"]
        if self.uncertainty not in valid_uncertainty:
            raise ValueError(f"Uncertainty method must be one of {valid_uncertainty}")
        
        # Check date column if specified
        if self.date_col and self.date_col not in self.original_data.columns:
            raise ValueError(f"Date column '{self.date_col}' not found in data")
    
    def _prepare_data(self):
        """Prepare data for modeling."""
        # Prepare and clean data
        prepared_data, self.data_metadata_ = prepare_data(
            self.original_data, 
            self.formula, 
            date_col=self.date_col
        )
        
        # Parse formula and create design matrix
        self.X_, self.y_, self.formula_metadata_ = parse_formula(
            self.formula, 
            prepared_data,
            include_intercept=self.kwargs.get('fit_intercept', True)
        )
        
        # Store date information if applicable
        if self.date_col:
            self.date_values = prepared_data[self.date_col].values
            self.date_range = (prepared_data[self.date_col].min(), 
                             prepared_data[self.date_col].max())
            
            # Enable temporal conformal if requested
            if self.uncertainty == "conformal_temporal":
                self.temporal_conformal = True
    
    def _initialize_backend(self):
        """Initialize the appropriate backend model."""
        if self.method == "linear":
            self.backend_model_ = LinearRegression(
                fit_intercept=self.kwargs.get('fit_intercept', True),
                method=self.kwargs.get('solver', 'qr')
            )
        elif self.method == "ridge":
            self.backend_model_ = LinearRegression(
                fit_intercept=self.kwargs.get('fit_intercept', True),
                method=self.kwargs.get('solver', 'qr'),
                regularization=self.kwargs.get('alpha', 1.0)
            )
        else:
            # For now, fall back to linear for other methods
            # TODO: Implement other methods
            warnings.warn(f"Method '{self.method}' not yet implemented, using linear regression")
            self.backend_model_ = LinearRegression(
                fit_intercept=self.kwargs.get('fit_intercept', True)
            )
    
    def fit(self):
        """Fit the regression model."""
        # Fit backend model
        self.backend_model_.fit(
            self.X_, self.y_, 
            feature_names=self.formula_metadata_['feature_names']
        )
        
        # Determine conformal method if needed
        if self.uncertainty.startswith('conformal'):
            self._setup_conformal_prediction()
        
        return self
    
    def _setup_conformal_prediction(self):
        """Set up conformal prediction method."""
        from ..conformal.methods import detect_data_thinning_eligibility
        
        # Auto-detect data thinning eligibility if method is "conformal"
        if self.uncertainty == "conformal":
            eligibility = detect_data_thinning_eligibility(
                self.backend_model_, self.X_, self.y_, self.family
            )
            self.data_thinning_eligible = eligibility['eligible']
            self.data_thinning_reason = eligibility['reason']
            
            if self.data_thinning_eligible:
                self.conformal_method = "data_thinning"
            else:
                self.conformal_method = "split"
        elif self.uncertainty == "conformal_thinning":
            self.conformal_method = "data_thinning"
            self.data_thinning_eligible = True
        elif self.uncertainty == "conformal_split":
            self.conformal_method = "split"
            self.data_thinning_eligible = False
        elif self.uncertainty == "conformal_temporal":
            self.conformal_method = "temporal"
            self.temporal_conformal = True
    
    def predict(self, new_data: Optional[pd.DataFrame] = None,
                alpha: float = 0.05,
                return_samples: bool = False) -> pd.DataFrame:
        """
        Make predictions with uncertainty quantification.
        
        Parameters
        ----------
        new_data : pd.DataFrame, optional
            New data for prediction. If None, uses training data
        alpha : float, default 0.05
            Significance level for confidence intervals (1-alpha coverage)
        return_samples : bool, default False
            Whether to return prediction samples
            
        Returns
        -------
        pd.DataFrame
            Predictions with uncertainty bands
        """
        if self.backend_model_ is None:
            raise ValueError("Model must be fitted before making predictions")
        
        # Use training data if no new data provided
        if new_data is None:
            X_pred = self.X_
        else:
            # Parse new data with same formula
            X_pred, _, _ = parse_formula(
                self.formula, new_data,
                include_intercept=self.kwargs.get('fit_intercept', True)
            )
        
        # Get point predictions
        point_predictions = self.backend_model_.predict(X_pred)
        
        # Create results DataFrame
        results = pd.DataFrame({
            'prediction': point_predictions
        })
        
        # Add uncertainty quantification if requested
        if self.uncertainty != "none":
            self._add_uncertainty_bands(results, X_pred, alpha, return_samples)
        
        return results
    
    def _add_uncertainty_bands(self, results: pd.DataFrame, X_pred: np.ndarray,
                              alpha: float, return_samples: bool):
        """Add uncertainty bands to predictions."""
        if self.uncertainty.startswith('conformal'):
            self._add_conformal_bands(results, X_pred, alpha, return_samples)
        elif self.uncertainty == "bootstrap":
            self._add_bootstrap_bands(results, X_pred, alpha, return_samples)
    
    def _add_conformal_bands(self, results: pd.DataFrame, X_pred: np.ndarray,
                           alpha: float, return_samples: bool):
        """Add conformal prediction bands."""
        from ..conformal.methods import conformal_predict
        
        conformal_results = conformal_predict(
            self.backend_model_, self.X_, self.y_, X_pred,
            method=self.conformal_method,
            alpha=alpha,
            return_samples=return_samples
        )
        
        # Add confidence bands
        confidence_levels = [90, 95]  # Always include these
        for level in confidence_levels:
            level_alpha = 1 - (level / 100)
            if level_alpha in conformal_results:
                results[f'lower_{level}'] = conformal_results[level_alpha]['lower']
                results[f'upper_{level}'] = conformal_results[level_alpha]['upper']
        
        # Add samples if requested
        if return_samples and 'samples' in conformal_results:
            results['samples'] = conformal_results['samples']
        
        # Store achieved coverage
        self.coverage_achieved = conformal_results.get('coverage_achieved')
        self.conformal_alpha = alpha
    
    def _add_bootstrap_bands(self, results: pd.DataFrame, X_pred: np.ndarray,
                           alpha: float, return_samples: bool):
        """Add bootstrap prediction bands."""
        # TODO: Implement bootstrap uncertainty
        warnings.warn("Bootstrap uncertainty not yet implemented")
    
    def forecast(self, horizon: int, **kwargs) -> pd.DataFrame:
        """
        Forecast future values (for time series).
        
        Parameters
        ----------
        horizon : int
            Number of periods to forecast
        **kwargs
            Additional arguments
            
        Returns
        -------
        pd.DataFrame
            Forecasted values with uncertainty
        """
        if not self.date_col:
            raise ValueError("Forecasting requires date_col to be specified")
        
        # TODO: Implement proper time series forecasting
        warnings.warn("Time series forecasting not yet fully implemented")
        
        # For now, return empty DataFrame with correct structure
        return pd.DataFrame({
            'prediction': [],
            'lower_95': [],
            'upper_95': []
        })
    
    def summary(self) -> str:
        """Get R-style model summary."""
        return format_summary(self)
    
    def __str__(self) -> str:
        """String representation of the model."""
        return self.summary()
    
    def __repr__(self) -> str:
        """Repr of the model."""
        return f"RegressModel(formula='{self.formula}', method='{self.method}')"
    
    # Properties for R-like access
    @property
    def coefficients(self) -> Optional[pd.DataFrame]:
        """Get coefficient table."""
        if self.backend_model_ is None:
            return None
        return self.backend_model_.get_coefficient_stats()
    
    @property
    def residuals(self) -> Optional[np.ndarray]:
        """Get residuals."""
        if self.backend_model_ is None:
            return None
        return self.backend_model_.residuals_
    
    @property
    def fitted_values(self) -> Optional[np.ndarray]:
        """Get fitted values."""
        if self.backend_model_ is None:
            return None
        return self.backend_model_.fitted_values_
    
    @property
    def r_squared(self) -> Optional[float]:
        """Get R-squared."""
        if self.backend_model_ is None:
            return None
        return self.backend_model_.r_squared_
    
    @property
    def adj_r_squared(self) -> Optional[float]:
        """Get adjusted R-squared."""
        if self.backend_model_ is None:
            return None
        return self.backend_model_.adj_r_squared_
    
    @property
    def residual_std_error(self) -> Optional[float]:
        """Get residual standard error."""
        if self.backend_model_ is None:
            return None
        return self.backend_model_.residual_std_error_
    
    @property
    def f_statistic(self) -> Optional[float]:
        """Get F-statistic."""
        if self.backend_model_ is None:
            return None
        return self.backend_model_.f_statistic_
    
    @property
    def aic(self) -> Optional[float]:
        """Get AIC."""
        if self.backend_model_ is None:
            return None
        return self.backend_model_.aic_
    
    @property
    def bic(self) -> Optional[float]:
        """Get BIC.""" 
        if self.backend_model_ is None:
            return None
        return self.backend_model_.bic_
    
    @property
    def n_obs(self) -> Optional[int]:
        """Get number of observations."""
        if self.backend_model_ is None:
            return None
        return self.backend_model_.n_samples_
    
    @property
    def n_params(self) -> Optional[int]:
        """Get number of parameters."""
        if self.backend_model_ is None:
            return None
        return len(self.backend_model_.coefficients_) + (1 if self.backend_model_.fit_intercept else 0)