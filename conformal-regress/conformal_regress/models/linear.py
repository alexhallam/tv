"""
Linear regression implementation using JAX for speed.
"""

import jax
import jax.numpy as jnp
import numpy as np
import pandas as pd
from typing import Tuple, Optional, Dict, Any
import scipy.linalg
from scipy import stats


class LinearRegression:
    """
    Linear regression using JAX for fast computation.
    
    This implementation prioritizes speed using JAX JIT compilation
    and efficient LAPACK routines via SciPy.
    """
    
    def __init__(self, fit_intercept: bool = True, 
                 method: str = "qr",
                 regularization: Optional[float] = None):
        """
        Initialize linear regression model.
        
        Parameters
        ----------
        fit_intercept : bool, default True
            Whether to fit an intercept term
        method : str, default "qr"
            Solver method: "qr", "svd", or "cholesky"
        regularization : float, optional
            Ridge regularization parameter (L2 penalty)
        """
        self.fit_intercept = fit_intercept
        self.method = method
        self.regularization = regularization
        
        # Model state
        self.coefficients_ = None
        self.intercept_ = None
        self.covariance_matrix_ = None
        self.residuals_ = None
        self.fitted_values_ = None
        
        # Statistics
        self.r_squared_ = None
        self.adj_r_squared_ = None
        self.residual_std_error_ = None
        self.f_statistic_ = None
        self.f_pvalue_ = None
        self.aic_ = None
        self.bic_ = None
        
        # Data info
        self.n_features_ = None
        self.n_samples_ = None
        self.feature_names_ = None
        
        # JIT compiled functions
        self._predict_jit = jax.jit(self._predict_core)
        self._residuals_jit = jax.jit(self._compute_residuals)
    
    def fit(self, X: np.ndarray, y: np.ndarray, 
            feature_names: Optional[list] = None,
            sample_weight: Optional[np.ndarray] = None) -> 'LinearRegression':
        """
        Fit linear regression model.
        
        Parameters
        ----------
        X : np.ndarray
            Feature matrix of shape (n_samples, n_features)
        y : np.ndarray
            Target vector of shape (n_samples,)
        feature_names : list, optional
            Names of features
        sample_weight : np.ndarray, optional
            Sample weights
            
        Returns
        -------
        self : LinearRegression
            Fitted model
        """
        X = np.asarray(X)
        y = np.asarray(y)
        
        if X.ndim != 2:
            raise ValueError("X must be 2-dimensional")
        if y.ndim != 1:
            raise ValueError("y must be 1-dimensional")
        if X.shape[0] != y.shape[0]:
            raise ValueError("X and y must have same number of samples")
        
        self.n_samples_, self.n_features_ = X.shape
        self.feature_names_ = feature_names or [f"x{i}" for i in range(self.n_features_)]
        
        # Handle sample weights
        if sample_weight is not None:
            sample_weight = np.asarray(sample_weight)
            if sample_weight.shape[0] != self.n_samples_:
                raise ValueError("sample_weight must have same length as X")
            # Apply weights by scaling
            sqrt_weights = np.sqrt(sample_weight)
            X = X * sqrt_weights[:, np.newaxis]
            y = y * sqrt_weights
        
        # Add intercept column if needed
        if self.fit_intercept:
            X_with_intercept = np.column_stack([np.ones(self.n_samples_), X])
        else:
            X_with_intercept = X
        
        # Solve linear system
        if self.method == "qr":
            coeffs, residuals_sum_sq = self._solve_qr(X_with_intercept, y)
        elif self.method == "svd":
            coeffs, residuals_sum_sq = self._solve_svd(X_with_intercept, y)
        elif self.method == "cholesky":
            coeffs, residuals_sum_sq = self._solve_cholesky(X_with_intercept, y)
        else:
            raise ValueError(f"Unknown method: {self.method}")
        
        # Extract intercept and coefficients
        if self.fit_intercept:
            self.intercept_ = coeffs[0]
            self.coefficients_ = coeffs[1:]
        else:
            self.intercept_ = 0.0
            self.coefficients_ = coeffs
        
        # Compute predictions and residuals
        self.fitted_values_ = self.predict(X)
        self.residuals_ = y - self.fitted_values_
        
        # Compute model statistics
        self._compute_statistics(X_with_intercept, y, residuals_sum_sq)
        
        return self
    
    def _solve_qr(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, float]:
        """Solve using QR decomposition (most stable)."""
        if self.regularization:
            # Ridge regression via augmented system
            n_features = X.shape[1]
            reg_matrix = np.sqrt(self.regularization) * np.eye(n_features)
            X_aug = np.vstack([X, reg_matrix])
            y_aug = np.concatenate([y, np.zeros(n_features)])
            
            Q, R = scipy.linalg.qr(X_aug, mode='economic')
            coeffs = scipy.linalg.solve_triangular(R, Q.T @ y_aug)
            
            # Compute residuals on original data
            residuals = y - X @ coeffs
            residuals_sum_sq = np.sum(residuals**2)
        else:
            # Standard least squares
            Q, R = scipy.linalg.qr(X, mode='economic')
            coeffs = scipy.linalg.solve_triangular(R, Q.T @ y)
            residuals_sum_sq = np.sum((y - X @ coeffs)**2)
        
        return coeffs, residuals_sum_sq
    
    def _solve_svd(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, float]:
        """Solve using SVD (handles rank deficiency)."""
        U, s, Vt = scipy.linalg.svd(X, full_matrices=False)
        
        # Threshold for numerical stability
        rcond = np.finfo(X.dtype).eps * max(X.shape)
        cutoff = rcond * s[0]
        
        if self.regularization:
            # Ridge regression
            s_reg = s**2 + self.regularization
            coeffs = Vt.T @ (s / s_reg * (U.T @ y))
        else:
            # Standard least squares with pseudoinverse
            s_inv = np.where(s > cutoff, 1.0 / s, 0.0)
            coeffs = Vt.T @ (s_inv * (U.T @ y))
        
        residuals_sum_sq = np.sum((y - X @ coeffs)**2)
        return coeffs, residuals_sum_sq
    
    def _solve_cholesky(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, float]:
        """Solve using Cholesky decomposition (fastest for well-conditioned problems)."""
        XtX = X.T @ X
        Xty = X.T @ y
        
        if self.regularization:
            # Add ridge penalty
            XtX += self.regularization * np.eye(XtX.shape[0])
        
        try:
            # Cholesky decomposition
            L = scipy.linalg.cholesky(XtX, lower=True)
            coeffs = scipy.linalg.solve_triangular(
                L.T, scipy.linalg.solve_triangular(L, Xty, lower=True)
            )
        except scipy.linalg.LinAlgError:
            # Fall back to SVD if Cholesky fails
            return self._solve_svd(X, y)
        
        residuals_sum_sq = np.sum((y - X @ coeffs)**2)
        return coeffs, residuals_sum_sq
    
    def _compute_statistics(self, X: np.ndarray, y: np.ndarray, 
                           residuals_sum_sq: float) -> None:
        """Compute regression statistics."""
        n, p = X.shape
        
        # Degrees of freedom
        df_resid = n - p
        df_model = p - 1 if self.fit_intercept else p
        
        # R-squared
        y_mean = np.mean(y)
        tss = np.sum((y - y_mean)**2)  # Total sum of squares
        self.r_squared_ = 1 - residuals_sum_sq / tss if tss > 0 else 0.0
        
        # Adjusted R-squared
        if df_resid > 0:
            self.adj_r_squared_ = 1 - (residuals_sum_sq / df_resid) / (tss / (n - 1))
        else:
            self.adj_r_squared_ = np.nan
        
        # Residual standard error
        if df_resid > 0:
            self.residual_std_error_ = np.sqrt(residuals_sum_sq / df_resid)
        else:
            self.residual_std_error_ = np.nan
        
        # F-statistic
        if df_model > 0 and df_resid > 0:
            mss = (tss - residuals_sum_sq) / df_model  # Model sum of squares
            mse = residuals_sum_sq / df_resid          # Mean squared error
            self.f_statistic_ = mss / mse
            self.f_pvalue_ = 1 - stats.f.cdf(self.f_statistic_, df_model, df_resid)
        else:
            self.f_statistic_ = np.nan
            self.f_pvalue_ = np.nan
        
        # Information criteria
        log_likelihood = -0.5 * n * (np.log(2 * np.pi) + np.log(residuals_sum_sq / n)) - 0.5 * n
        self.aic_ = 2 * p - 2 * log_likelihood
        self.bic_ = np.log(n) * p - 2 * log_likelihood
        
        # Covariance matrix for coefficient standard errors
        try:
            if not self.regularization:  # Standard errors not well-defined for ridge
                XtX_inv = scipy.linalg.pinv(X.T @ X)
                self.covariance_matrix_ = self.residual_std_error_**2 * XtX_inv
        except:
            self.covariance_matrix_ = None
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions on new data.
        
        Parameters
        ----------
        X : np.ndarray
            Feature matrix of shape (n_samples, n_features)
            
        Returns
        -------
        np.ndarray
            Predicted values
        """
        if self.coefficients_ is None:
            raise ValueError("Model must be fitted before making predictions")
        
        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        if X.shape[1] != self.n_features_:
            raise ValueError(f"X has {X.shape[1]} features, expected {self.n_features_}")
        
        # Use JIT compiled prediction for speed
        return self._predict_jit(jnp.array(X), jnp.array(self.coefficients_), 
                                self.intercept_)
    
    @staticmethod
    def _predict_core(X: jnp.ndarray, coeffs: jnp.ndarray, intercept: float) -> jnp.ndarray:
        """Core prediction function (JIT compiled)."""
        return X @ coeffs + intercept
    
    @staticmethod  
    def _compute_residuals(y_true: jnp.ndarray, y_pred: jnp.ndarray) -> jnp.ndarray:
        """Compute residuals (JIT compiled)."""
        return y_true - y_pred
    
    def get_coefficient_stats(self) -> Optional[pd.DataFrame]:
        """
        Get coefficient statistics including standard errors and t-tests.
        
        Returns
        -------
        pd.DataFrame or None
            Coefficient statistics if covariance matrix available
        """
        if self.covariance_matrix_ is None:
            return None
        
        # Extract diagonal for standard errors
        std_errors = np.sqrt(np.diag(self.covariance_matrix_))
        
        # Combine intercept and coefficients
        if self.fit_intercept:
            all_coeffs = np.concatenate([[self.intercept_], self.coefficients_])
            all_names = ['(Intercept)'] + list(self.feature_names_)
        else:
            all_coeffs = self.coefficients_
            all_names = list(self.feature_names_)
        
        # t-statistics and p-values
        t_values = all_coeffs / std_errors
        df = self.n_samples_ - len(all_coeffs)
        p_values = 2 * (1 - stats.t.cdf(np.abs(t_values), df))
        
        return pd.DataFrame({
            'Estimate': all_coeffs,
            'Std. Error': std_errors,
            't value': t_values,
            'Pr(>|t|)': p_values
        }, index=all_names)
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Return R² score.
        
        Parameters
        ----------
        X : np.ndarray
            Feature matrix
        y : np.ndarray
            Target values
            
        Returns
        -------
        float
            R² score
        """
        y_pred = self.predict(X)
        ss_res = np.sum((y - y_pred)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0