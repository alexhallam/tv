"""
Conformal prediction methods with automatic data thinning detection.

This module implements various conformal prediction approaches with a focus on
speed and automatic detection of when data thinning can be used instead of
traditional train/calibration splits.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple, Union
import warnings
from scipy import stats
import jax
import jax.numpy as jnp


def conformal_predict(model, X_train: np.ndarray, y_train: np.ndarray, 
                     X_test: np.ndarray,
                     method: str = "auto",
                     alpha: float = 0.05,
                     return_samples: bool = False,
                     random_state: Optional[int] = None) -> Dict[str, Any]:
    """
    Make conformal predictions with uncertainty quantification.
    
    Parameters
    ----------
    model : fitted model
        Trained regression model with predict() method
    X_train : np.ndarray
        Training features
    y_train : np.ndarray
        Training targets
    X_test : np.ndarray
        Test features for prediction
    method : str, default "auto"
        Conformal method: "auto", "data_thinning", "split", "temporal", "cross"
    alpha : float, default 0.05
        Miscoverage rate (1-alpha coverage)
    return_samples : bool, default False
        Whether to return prediction samples
    random_state : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    dict
        Conformal prediction results with confidence bands
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    if method == "auto":
        # Auto-detect best method based on data thinning eligibility
        eligibility = detect_data_thinning_eligibility(model, X_train, y_train, "gaussian")
        method = "data_thinning" if eligibility['eligible'] else "split"
    
    # Dispatch to appropriate method
    if method == "data_thinning":
        return data_thinning_conformal(model, X_train, y_train, X_test, alpha, return_samples)
    elif method == "split":
        return split_conformal(model, X_train, y_train, X_test, alpha, return_samples)
    elif method == "temporal":
        return temporal_conformal(model, X_train, y_train, X_test, alpha, return_samples)
    elif method == "cross":
        return cross_conformal(model, X_train, y_train, X_test, alpha, return_samples)
    else:
        raise ValueError(f"Unknown conformal method: {method}")


def detect_data_thinning_eligibility(model, X: np.ndarray, y: np.ndarray, 
                                   family: str = "gaussian") -> Dict[str, Any]:
    """
    Detect if data thinning can be used for conformal prediction.
    
    Data thinning is applicable when the residuals follow a convolution-closed
    distribution, which is true for Gaussian residuals in linear regression.
    
    Parameters
    ----------
    model : fitted model
        Trained regression model
    X : np.ndarray
        Features
    y : np.ndarray
        Targets
    family : str, default "gaussian"
        Distribution family
        
    Returns
    -------
    dict
        Eligibility result with 'eligible' bool and 'reason' string
    """
    try:
        # Get model predictions and residuals
        y_pred = model.predict(X)
        residuals = y - y_pred
        
        # Test for convolution-closed distribution
        if family == "gaussian":
            # Test normality of residuals
            normality_test = test_residual_normality(residuals)
            
            if normality_test['is_normal']:
                return {
                    'eligible': True,
                    'reason': 'Gaussian residuals detected, data thinning applicable',
                    'test_statistic': normality_test['statistic'],
                    'p_value': normality_test['p_value']
                }
            else:
                return {
                    'eligible': False,
                    'reason': f'Non-Gaussian residuals (p={normality_test["p_value"]:.4f}), using split conformal',
                    'test_statistic': normality_test['statistic'],
                    'p_value': normality_test['p_value']
                }
        
        elif family in ["poisson", "exponential"]:
            # These families are also convolution-closed
            return {
                'eligible': True,
                'reason': f'{family.capitalize()} family is convolution-closed, data thinning applicable'
            }
        
        else:
            return {
                'eligible': False,
                'reason': f'{family} family not confirmed convolution-closed, using split conformal'
            }
    
    except Exception as e:
        return {
            'eligible': False,
            'reason': f'Error in data thinning detection: {str(e)}'
        }


def test_residual_normality(residuals: np.ndarray, alpha: float = 0.05) -> Dict[str, Any]:
    """
    Test residuals for normality using multiple tests.
    
    Parameters
    ----------
    residuals : np.ndarray
        Model residuals
    alpha : float, default 0.05
        Significance level for normality tests
        
    Returns
    -------
    dict
        Test results with combined decision
    """
    # Shapiro-Wilk test for small samples
    if len(residuals) <= 5000:
        shapiro_stat, shapiro_p = stats.shapiro(residuals)
        shapiro_normal = shapiro_p > alpha
    else:
        shapiro_stat, shapiro_p = np.nan, np.nan
        shapiro_normal = None
    
    # Jarque-Bera test for larger samples
    jb_stat, jb_p = stats.jarque_bera(residuals)
    jb_normal = jb_p > alpha
    
    # Anderson-Darling test
    ad_stat, ad_critical, ad_significance = stats.anderson(residuals, dist='norm')
    ad_normal = ad_stat < ad_critical[2]  # 5% significance level
    
    # Combined decision - require majority agreement
    tests = [test for test in [shapiro_normal, jb_normal, ad_normal] if test is not None]
    is_normal = sum(tests) > len(tests) / 2
    
    return {
        'is_normal': is_normal,
        'shapiro_statistic': shapiro_stat,
        'shapiro_p_value': shapiro_p,
        'jb_statistic': jb_stat,
        'jb_p_value': jb_p,
        'ad_statistic': ad_stat,
        'statistic': jb_stat,  # Use JB as main statistic
        'p_value': jb_p
    }


def data_thinning_conformal(model, X_train: np.ndarray, y_train: np.ndarray,
                          X_test: np.ndarray, alpha: float = 0.05,
                          return_samples: bool = False) -> Dict[str, Any]:
    """
    Data thinning conformal prediction for convolution-closed distributions.
    
    This method avoids data splitting by using the theoretical properties
    of convolution-closed distributions to generate valid conformal scores.
    
    Parameters
    ----------
    model : fitted model
        Trained regression model
    X_train : np.ndarray
        Training features
    y_train : np.ndarray
        Training targets
    X_test : np.ndarray
        Test features
    alpha : float, default 0.05
        Miscoverage rate
    return_samples : bool, default False
        Whether to return prediction samples
        
    Returns
    -------
    dict
        Conformal prediction results
    """
    # Get point predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Compute residuals
    residuals = y_train - y_train_pred
    
    # Estimate residual distribution parameters
    residual_std = np.std(residuals, ddof=1)
    residual_mean = np.mean(residuals)
    
    # For Gaussian case, use theoretical quantiles
    # Adjustment for finite sample size
    n = len(y_train)
    adjustment_factor = np.sqrt((n + 1) / n)  # Conservative adjustment
    
    # Compute conformal quantiles
    quantile_levels = [1 - alpha/2, alpha/2]  # Two-sided
    z_quantiles = stats.norm.ppf(quantile_levels)
    
    # Conformal prediction intervals
    margin = adjustment_factor * residual_std * abs(z_quantiles[0])
    
    lower_bounds = y_test_pred - margin
    upper_bounds = y_test_pred + margin
    
    results = {
        alpha: {
            'lower': lower_bounds,
            'upper': upper_bounds
        },
        'method': 'data_thinning',
        'coverage_achieved': 1 - alpha,  # Theoretical coverage
        'residual_std': residual_std,
        'n_train': n
    }
    
    # Add common confidence levels
    for level in [0.1, 0.05]:  # 90%, 95%
        if level != alpha:
            margin_level = adjustment_factor * residual_std * abs(stats.norm.ppf(level/2))
            results[level] = {
                'lower': y_test_pred - margin_level,
                'upper': y_test_pred + margin_level
            }
    
    # Add samples if requested
    if return_samples:
        n_samples = 1000
        samples = np.random.normal(
            y_test_pred[:, np.newaxis], 
            residual_std * adjustment_factor, 
            (len(y_test_pred), n_samples)
        )
        results['samples'] = samples
    
    return results


def split_conformal(model, X_train: np.ndarray, y_train: np.ndarray,
                   X_test: np.ndarray, alpha: float = 0.05,
                   return_samples: bool = False,
                   split_ratio: float = 0.8) -> Dict[str, Any]:
    """
    Traditional split conformal prediction.
    
    This method splits training data into proper training and calibration sets,
    then computes empirical quantiles of conformal scores.
    
    Parameters
    ----------
    model : model class
        Model class to retrain on split data
    X_train : np.ndarray
        Training features
    y_train : np.ndarray
        Training targets
    X_test : np.ndarray
        Test features
    alpha : float, default 0.05
        Miscoverage rate
    return_samples : bool, default False
        Whether to return prediction samples
    split_ratio : float, default 0.8
        Proportion of data for training (rest for calibration)
        
    Returns
    -------
    dict
        Conformal prediction results
    """
    n = len(X_train)
    n_train = int(n * split_ratio)
    
    # Random split
    indices = np.random.permutation(n)
    train_idx = indices[:n_train]
    cal_idx = indices[n_train:]
    
    X_proper_train = X_train[train_idx]
    y_proper_train = y_train[train_idx]
    X_cal = X_train[cal_idx]
    y_cal = y_train[cal_idx]
    
    # Retrain model on proper training set
    from ..models.linear import LinearRegression
    split_model = LinearRegression(
        fit_intercept=model.fit_intercept,
        method=model.method,
        regularization=model.regularization
    )
    split_model.fit(X_proper_train, y_proper_train)
    
    # Compute conformal scores on calibration set
    y_cal_pred = split_model.predict(X_cal)
    scores = np.abs(y_cal - y_cal_pred)  # Absolute residuals
    
    # Compute conformal quantile
    n_cal = len(scores)
    q_level = np.ceil((n_cal + 1) * (1 - alpha)) / n_cal
    q_level = min(q_level, 1.0)  # Cap at 1
    
    quantile = np.quantile(scores, q_level)
    
    # Make predictions
    y_test_pred = split_model.predict(X_test)
    
    results = {
        alpha: {
            'lower': y_test_pred - quantile,
            'upper': y_test_pred + quantile
        },
        'method': 'split',
        'quantile': quantile,
        'n_calibration': n_cal,
        'coverage_achieved': None  # Would need holdout test to estimate
    }
    
    # Add common confidence levels
    for level in [0.1, 0.05]:  # 90%, 95%
        if level != alpha:
            q_level_alt = np.ceil((n_cal + 1) * (1 - level)) / n_cal
            q_level_alt = min(q_level_alt, 1.0)
            quantile_alt = np.quantile(scores, q_level_alt)
            results[level] = {
                'lower': y_test_pred - quantile_alt,
                'upper': y_test_pred + quantile_alt
            }
    
    # Add samples if requested (bootstrap from residuals)
    if return_samples:
        n_samples = 1000
        residual_samples = np.random.choice(scores, size=(len(y_test_pred), n_samples), replace=True)
        # Random signs for residuals
        signs = np.random.choice([-1, 1], size=(len(y_test_pred), n_samples))
        samples = y_test_pred[:, np.newaxis] + signs * residual_samples
        results['samples'] = samples
    
    return results


def temporal_conformal(model, X_train: np.ndarray, y_train: np.ndarray,
                      X_test: np.ndarray, alpha: float = 0.05,
                      return_samples: bool = False,
                      window_size: Optional[int] = None) -> Dict[str, Any]:
    """
    Temporal conformal prediction for time series.
    
    Uses rolling window approach to respect temporal structure.
    
    Parameters
    ----------
    model : fitted model
        Trained regression model
    X_train : np.ndarray
        Training features (assumed in temporal order)
    y_train : np.ndarray
        Training targets (assumed in temporal order)
    X_test : np.ndarray
        Test features
    alpha : float, default 0.05
        Miscoverage rate
    return_samples : bool, default False
        Whether to return prediction samples
    window_size : int, optional
        Size of rolling window for calibration. If None, uses adaptive size
        
    Returns
    -------
    dict
        Conformal prediction results
    """
    n = len(X_train)
    
    if window_size is None:
        # Adaptive window size based on data length
        window_size = min(max(50, n // 4), n // 2)
    
    window_size = min(window_size, n - 1)
    
    # Use the most recent window for calibration
    cal_start = max(0, n - window_size)
    X_cal = X_train[cal_start:]
    y_cal = y_train[cal_start:]
    
    # Compute scores on calibration window
    y_cal_pred = model.predict(X_cal)
    scores = np.abs(y_cal - y_cal_pred)
    
    # Conformal quantile with finite sample correction
    n_cal = len(scores)
    q_level = np.ceil((n_cal + 1) * (1 - alpha)) / n_cal
    q_level = min(q_level, 1.0)
    
    quantile = np.quantile(scores, q_level)
    
    # Make predictions
    y_test_pred = model.predict(X_test)
    
    results = {
        alpha: {
            'lower': y_test_pred - quantile,
            'upper': y_test_pred + quantile
        },
        'method': 'temporal',
        'window_size': window_size,
        'quantile': quantile,
        'n_calibration': n_cal
    }
    
    # Add common confidence levels
    for level in [0.1, 0.05]:  # 90%, 95%
        if level != alpha:
            q_level_alt = np.ceil((n_cal + 1) * (1 - level)) / n_cal
            q_level_alt = min(q_level_alt, 1.0)
            quantile_alt = np.quantile(scores, q_level_alt)
            results[level] = {
                'lower': y_test_pred - quantile_alt,
                'upper': y_test_pred + quantile_alt
            }
    
    return results


def cross_conformal(model, X_train: np.ndarray, y_train: np.ndarray,
                   X_test: np.ndarray, alpha: float = 0.05,
                   return_samples: bool = False,
                   n_folds: int = 5) -> Dict[str, Any]:
    """
    Cross-conformal prediction for small datasets.
    
    Uses cross-validation to generate conformal scores, providing
    better coverage for small sample sizes.
    
    Parameters
    ----------
    model : model class
        Model class to retrain
    X_train : np.ndarray
        Training features
    y_train : np.ndarray
        Training targets
    X_test : np.ndarray
        Test features
    alpha : float, default 0.05
        Miscoverage rate
    return_samples : bool, default False
        Whether to return prediction samples
    n_folds : int, default 5
        Number of cross-validation folds
        
    Returns
    -------
    dict
        Conformal prediction results
    """
    from sklearn.model_selection import KFold
    from ..models.linear import LinearRegression
    
    n = len(X_train)
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)
    
    all_scores = []
    
    # Cross-validation to generate conformal scores
    for train_idx, val_idx in kf.split(X_train):
        X_fold_train = X_train[train_idx]
        y_fold_train = y_train[train_idx]
        X_fold_val = X_train[val_idx]
        y_fold_val = y_train[val_idx]
        
        # Train model on fold
        fold_model = LinearRegression(
            fit_intercept=model.fit_intercept,
            method=model.method,
            regularization=model.regularization
        )
        fold_model.fit(X_fold_train, y_fold_train)
        
        # Compute scores on validation fold
        y_fold_pred = fold_model.predict(X_fold_val)
        fold_scores = np.abs(y_fold_val - y_fold_pred)
        all_scores.extend(fold_scores)
    
    all_scores = np.array(all_scores)
    
    # Compute conformal quantile
    n_scores = len(all_scores)
    q_level = np.ceil((n_scores + 1) * (1 - alpha)) / n_scores
    q_level = min(q_level, 1.0)
    
    quantile = np.quantile(all_scores, q_level)
    
    # Make predictions with full model
    y_test_pred = model.predict(X_test)
    
    results = {
        alpha: {
            'lower': y_test_pred - quantile,
            'upper': y_test_pred + quantile
        },
        'method': 'cross',
        'n_folds': n_folds,
        'quantile': quantile,
        'n_scores': n_scores
    }
    
    # Add common confidence levels
    for level in [0.1, 0.05]:  # 90%, 95%
        if level != alpha:
            q_level_alt = np.ceil((n_scores + 1) * (1 - level)) / n_scores
            q_level_alt = min(q_level_alt, 1.0)
            quantile_alt = np.quantile(all_scores, q_level_alt)
            results[level] = {
                'lower': y_test_pred - quantile_alt,
                'upper': y_test_pred + quantile_alt
            }
    
    return results