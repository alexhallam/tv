"""
Base model classes and factory for regression methods.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
import jax
import jax.numpy as jnp
from scipy import stats

from ..formula.parser import ParsedFormula


@dataclass
class ModelSummary:
    """Base model summary statistics."""
    coefficients: pd.DataFrame
    residual_std_error: float
    degrees_of_freedom: int
    r_squared: float
    adj_r_squared: float
    f_statistic: float
    f_pvalue: float


class BaseModel(ABC):
    """Abstract base class for regression models."""
    
    def __init__(self, family: str = "gaussian", **kwargs):
        self.family = family
        self.fitted = False
        self.coefficients = None
        self.feature_names = None
        self.last_date = None
        
    @abstractmethod
    def fit(self, formula: ParsedFormula, data: pd.DataFrame) -> 'BaseModel':
        """Fit the model."""
        pass
    
    @abstractmethod
    def predict(self, new_data: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        pass
    
    @abstractmethod
    def summary(self) -> ModelSummary:
        """Get model summary."""
        pass


class LinearModel(BaseModel):
    """Linear regression model using LAPACK."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.X = None
        self.y = None
        self.residuals = None
        self.fitted_values = None
        
    def fit(self, formula: ParsedFormula, data: pd.DataFrame) -> 'LinearModel':
        """Fit linear regression model."""
        from ..formula.parser import FormulaParser
        
        # Create design matrix
        parser = FormulaParser()
        X, feature_names = parser.create_design_matrix(formula, data)
        y = data[formula.response].values
        
        # Store data
        self.X = X
        self.y = y
        self.feature_names = feature_names
        
        # Fit using LAPACK (QR decomposition)
        self.coefficients = self._fit_lapack(X, y)
        
        # Compute residuals and fitted values
        self.fitted_values = X @ self.coefficients
        self.residuals = y - self.fitted_values
        
        # Store last date if available
        if hasattr(data, 'index') and isinstance(data.index, pd.DatetimeIndex):
            self.last_date = data.index[-1]
        
        self.fitted = True
        return self
    
    def _fit_lapack(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Fit using LAPACK QR decomposition."""
        # Use scipy's lstsq which uses LAPACK
        coefficients, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
        return coefficients
    
    def predict(self, new_data: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        if not self.fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        # Create design matrix for new data
        from ..formula.parser import FormulaParser
        parser = FormulaParser()
        
        # For prediction, we need to create a formula with the same structure
        # This is a simplified version - in practice, you'd need to handle this more carefully
        X_new = self._create_prediction_matrix(new_data)
        
        return X_new @ self.coefficients
    
    def _create_prediction_matrix(self, new_data: pd.DataFrame) -> np.ndarray:
        """Create design matrix for prediction."""
        # This is a simplified implementation
        # In practice, you'd need to handle the formula parsing and matrix creation
        # For now, we'll assume the new_data has the same columns as the original features
        
        # Create a simple design matrix with intercept
        n_samples = len(new_data)
        X_new = np.ones((n_samples, len(self.feature_names)))
        
        # Fill in the features (this is simplified)
        for i, feature in enumerate(self.feature_names[1:], 1):  # Skip intercept
            if feature in new_data.columns:
                X_new[:, i] = new_data[feature].values
        
        return X_new
    
    def summary(self) -> ModelSummary:
        """Get model summary statistics."""
        if not self.fitted:
            raise ValueError("Model must be fitted before getting summary")
        
        n = len(self.y)
        p = len(self.coefficients)
        df = n - p
        
        # Residual standard error
        residual_std_error = np.sqrt(np.sum(self.residuals**2) / df)
        
        # R-squared
        ss_res = np.sum(self.residuals**2)
        ss_tot = np.sum((self.y - np.mean(self.y))**2)
        r_squared = 1 - (ss_res / ss_tot)
        adj_r_squared = 1 - (1 - r_squared) * (n - 1) / df
        
        # F-statistic
        ss_reg = ss_tot - ss_res
        f_statistic = (ss_reg / (p - 1)) / (ss_res / df)
        f_pvalue = 1 - stats.f.cdf(f_statistic, p - 1, df)
        
        # Standard errors and t-statistics
        # This is a simplified calculation - in practice, you'd use the full covariance matrix
        XtX_inv = np.linalg.inv(self.X.T @ self.X)
        se_coefficients = np.sqrt(np.diag(XtX_inv) * residual_std_error**2)
        t_values = self.coefficients / se_coefficients
        
        # P-values for coefficients
        p_values = 2 * (1 - stats.t.cdf(np.abs(t_values), df))
        
        # Create coefficients DataFrame
        coef_df = pd.DataFrame({
            'Estimate': self.coefficients,
            'Std_Error': se_coefficients,
            't_value': t_values,
            'p_value': p_values
        }, index=self.feature_names)
        
        return ModelSummary(
            coefficients=coef_df,
            residual_std_error=residual_std_error,
            degrees_of_freedom=df,
            r_squared=r_squared,
            adj_r_squared=adj_r_squared,
            f_statistic=f_statistic,
            f_pvalue=f_pvalue
        )


class QuantileModel(BaseModel):
    """Quantile regression model."""
    
    def __init__(self, tau: float = 0.5, **kwargs):
        super().__init__(**kwargs)
        self.tau = tau
        self.X = None
        self.y = None
        
    def fit(self, formula: ParsedFormula, data: pd.DataFrame) -> 'QuantileModel':
        """Fit quantile regression model."""
        from ..formula.parser import FormulaParser
        
        # Create design matrix
        parser = FormulaParser()
        X, feature_names = parser.create_design_matrix(formula, data)
        y = data[formula.response].values
        
        self.X = X
        self.y = y
        self.feature_names = feature_names
        
        # Fit using linear programming
        self.coefficients = self._fit_quantile(X, y)
        
        self.fitted = True
        return self
    
    def _fit_quantile(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Fit quantile regression using linear programming."""
        # This is a simplified implementation
        # In practice, you'd use a proper quantile regression solver
        from scipy.optimize import minimize
        
        def objective(beta):
            residuals = y - X @ beta
            return np.sum(np.where(residuals >= 0, self.tau * residuals, (1 - self.tau) * (-residuals)))
        
        # Initial guess using OLS
        beta_init = np.linalg.lstsq(X, y, rcond=None)[0]
        
        result = minimize(objective, beta_init, method='L-BFGS-B')
        return result.x
    
    def predict(self, new_data: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        if not self.fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        X_new = self._create_prediction_matrix(new_data)
        return X_new @ self.coefficients
    
    def _create_prediction_matrix(self, new_data: pd.DataFrame) -> np.ndarray:
        """Create design matrix for prediction."""
        # Simplified implementation
        n_samples = len(new_data)
        X_new = np.ones((n_samples, len(self.feature_names)))
        
        for i, feature in enumerate(self.feature_names[1:], 1):
            if feature in new_data.columns:
                X_new[:, i] = new_data[feature].values
        
        return X_new
    
    def summary(self) -> ModelSummary:
        """Get model summary statistics."""
        if not self.fitted:
            raise ValueError("Model must be fitted before getting summary")
        
        # For quantile regression, we'll return simplified statistics
        n = len(self.y)
        p = len(self.coefficients)
        df = n - p
        
        # Create coefficients DataFrame
        coef_df = pd.DataFrame({
            'Estimate': self.coefficients,
            'Std_Error': np.nan,  # Would need bootstrap for proper SE
            't_value': np.nan,
            'p_value': np.nan
        }, index=self.feature_names)
        
        return ModelSummary(
            coefficients=coef_df,
            residual_std_error=np.nan,
            degrees_of_freedom=df,
            r_squared=np.nan,
            adj_r_squared=np.nan,
            f_statistic=np.nan,
            f_pvalue=np.nan
        )


class ModelFactory:
    """Factory for creating regression models."""
    
    def __init__(self):
        self.models = {
            'linear': LinearModel,
            'quantile': QuantileModel,
        }
    
    def create_model(
        self,
        method: str = "linear",
        family: str = "gaussian",
        uncertainty: Optional[str] = None,
        date_col: Optional[str] = None,
        **kwargs
    ) -> BaseModel:
        """
        Create a regression model.
        
        Parameters
        ----------
        method : str
            Regression method
        family : str
            Distribution family
        uncertainty : str, optional
            Uncertainty method
        date_col : str, optional
            Date column for time series
        **kwargs
            Additional arguments
            
        Returns
        -------
        BaseModel
            Created model instance
        """
        if method not in self.models:
            raise ValueError(f"Unknown method: {method}. Available: {list(self.models.keys())}")
        
        model_class = self.models[method]
        return model_class(family=family, **kwargs)
    
    def register_model(self, name: str, model_class: type):
        """Register a new model class."""
        self.models[name] = model_class