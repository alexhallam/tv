"""
Display utilities for R-style output formatting.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import warnings


def view(data: pd.DataFrame, **kwargs) -> None:
    """
    Display DataFrame using tidy-viewer-py if available, fallback to standard display.
    
    Parameters
    ----------
    data : pd.DataFrame
        Data to display
    **kwargs
        Additional arguments passed to tidy-viewer
    """
    try:
        import tidy_viewer
        tidy_viewer.view(data, **kwargs)
    except ImportError:
        print("tidy-viewer-py not available, using standard display")
        print(data.to_string())


def format_summary(model) -> str:
    """
    Format model summary in R-style output.
    
    Parameters
    ----------
    model : RegressModel
        Fitted regression model
        
    Returns
    -------
    str
        Formatted summary string
    """
    lines = []
    
    # Header
    lines.append(f"Formula: {model.formula}")
    lines.append("")
    
    # Coefficients table
    if hasattr(model, 'coefficients') and model.coefficients is not None:
        lines.append("Coefficients:")
        coef_df = model.coefficients.copy()
        
        # Format numbers for display
        for col in ['Estimate', 'Std. Error', 't value']:
            if col in coef_df.columns:
                coef_df[col] = coef_df[col].apply(lambda x: f"{x:>10.4f}" if pd.notnull(x) else "     NA")
        
        if 'Pr(>|t|)' in coef_df.columns:
            coef_df['Pr(>|t|)'] = coef_df['Pr(>|t|)'].apply(_format_p_value)
        
        # Create formatted table
        col_widths = {col: max(len(col), coef_df[col].astype(str).str.len().max()) + 2 
                     for col in coef_df.columns}
        
        # Header row
        header = "".join(col.rjust(col_widths[col]) for col in coef_df.columns)
        lines.append(f"{'':15}" + header)
        
        # Data rows
        for idx, row in coef_df.iterrows():
            row_str = f"{str(idx):15}"
            for col in coef_df.columns:
                row_str += str(row[col]).rjust(col_widths[col])
            lines.append(row_str)
        
        lines.append("")
    
    # Model statistics
    if hasattr(model, 'r_squared') and model.r_squared is not None:
        lines.append(f"Multiple R-squared: {model.r_squared:.4f}")
    
    if hasattr(model, 'adj_r_squared') and model.adj_r_squared is not None:
        lines.append(f"Adjusted R-squared: {model.adj_r_squared:.4f}")
    
    if hasattr(model, 'residual_std_error') and model.residual_std_error is not None:
        df_resid = model.n_obs - model.n_params if hasattr(model, 'n_obs') and hasattr(model, 'n_params') else None
        df_str = f" on {df_resid} degrees of freedom" if df_resid else ""
        lines.append(f"Residual standard error: {model.residual_std_error:.3f}{df_str}")
    
    if hasattr(model, 'f_statistic') and model.f_statistic is not None:
        lines.append(f"F-statistic: {model.f_statistic:.3f}")
    
    # Conformal prediction info
    if hasattr(model, 'conformal_method') and model.conformal_method:
        lines.append("")
        lines.append(f"Conformal method: {model.conformal_method}")
        
        if hasattr(model, 'coverage_achieved') and model.coverage_achieved is not None:
            lines.append(f"Achieved coverage: {model.coverage_achieved:.1%}")
        
        if hasattr(model, 'conformal_alpha') and model.conformal_alpha is not None:
            target_coverage = 1 - model.conformal_alpha
            lines.append(f"Target coverage: {target_coverage:.1%}")
    
    return "\n".join(lines)


def _format_p_value(p_val):
    """Format p-value with significance stars."""
    if pd.isnull(p_val):
        return "      NA    "
    
    # Determine significance level
    if p_val < 0.001:
        stars = " ***"
    elif p_val < 0.01:
        stars = " ** "
    elif p_val < 0.05:
        stars = " *  "
    elif p_val < 0.1:
        stars = " .  "
    else:
        stars = "    "
    
    # Format number
    if p_val < 2e-16:
        return "< 2e-16 ***"
    elif p_val < 0.001:
        return f"{p_val:.2e}{stars}"
    else:
        return f"{p_val:.6f}{stars}"


def format_prediction_summary(predictions: pd.DataFrame, 
                            confidence_levels: List[float] = [0.90, 0.95]) -> str:
    """
    Format prediction summary statistics.
    
    Parameters
    ----------
    predictions : pd.DataFrame
        Prediction results with uncertainty bands
    confidence_levels : list of float
        Confidence levels to summarize
        
    Returns
    -------
    str
        Formatted summary
    """
    lines = []
    lines.append("Prediction Summary:")
    lines.append("=" * 50)
    
    if 'prediction' in predictions.columns:
        pred_stats = predictions['prediction'].describe()
        lines.append("\nPredicted values:")
        for stat, value in pred_stats.items():
            lines.append(f"  {stat.capitalize():>10}: {value:>10.3f}")
    
    # Uncertainty band coverage
    for level in confidence_levels:
        lower_col = f'lower_{int(level*100)}'
        upper_col = f'upper_{int(level*100)}'
        
        if lower_col in predictions.columns and upper_col in predictions.columns:
            band_width = predictions[upper_col] - predictions[lower_col]
            avg_width = band_width.mean()
            lines.append(f"\n{level:.0%} Confidence bands:")
            lines.append(f"  Average width: {avg_width:.3f}")
            lines.append(f"  Min width:     {band_width.min():.3f}")
            lines.append(f"  Max width:     {band_width.max():.3f}")
    
    return "\n".join(lines)


def format_diagnostic_summary(model) -> str:
    """
    Format model diagnostic information.
    
    Parameters
    ----------
    model : RegressModel
        Fitted model
        
    Returns
    -------
    str
        Formatted diagnostic summary
    """
    lines = []
    lines.append("Model Diagnostics:")
    lines.append("=" * 50)
    
    # Residual statistics
    if hasattr(model, 'residuals') and model.residuals is not None:
        residuals = model.residuals
        lines.append("\nResidual statistics:")
        lines.append(f"  Min:        {np.min(residuals):>10.3f}")
        lines.append(f"  1Q:         {np.percentile(residuals, 25):>10.3f}")
        lines.append(f"  Median:     {np.median(residuals):>10.3f}")
        lines.append(f"  3Q:         {np.percentile(residuals, 75):>10.3f}")
        lines.append(f"  Max:        {np.max(residuals):>10.3f}")
    
    # Model fit statistics
    if hasattr(model, 'aic') and model.aic is not None:
        lines.append(f"\nAIC: {model.aic:.2f}")
    
    if hasattr(model, 'bic') and model.bic is not None:
        lines.append(f"BIC: {model.bic:.2f}")
    
    # Data thinning eligibility
    if hasattr(model, 'data_thinning_eligible') and model.data_thinning_eligible is not None:
        lines.append(f"\nData thinning eligible: {model.data_thinning_eligible}")
        
        if hasattr(model, 'data_thinning_reason') and model.data_thinning_reason:
            lines.append(f"Reason: {model.data_thinning_reason}")
    
    return "\n".join(lines)


def create_coefficient_table(coefficients: np.ndarray,
                           feature_names: List[str],
                           std_errors: Optional[np.ndarray] = None,
                           t_values: Optional[np.ndarray] = None,
                           p_values: Optional[np.ndarray] = None) -> pd.DataFrame:
    """
    Create a coefficients table in R-style format.
    
    Parameters
    ----------
    coefficients : np.ndarray
        Model coefficients
    feature_names : list of str
        Names of features/terms
    std_errors : np.ndarray, optional
        Standard errors of coefficients
    t_values : np.ndarray, optional
        t-statistics
    p_values : np.ndarray, optional
        p-values
        
    Returns
    -------
    pd.DataFrame
        Formatted coefficients table
    """
    coef_dict = {
        'Estimate': coefficients
    }
    
    if std_errors is not None:
        coef_dict['Std. Error'] = std_errors
    
    if t_values is not None:
        coef_dict['t value'] = t_values
    
    if p_values is not None:
        coef_dict['Pr(>|t|)'] = p_values
    
    df = pd.DataFrame(coef_dict, index=feature_names)
    return df


def print_fitting_progress(step: str, details: str = ""):
    """
    Print progress updates during model fitting.
    
    Parameters
    ----------
    step : str
        Current step description
    details : str, optional
        Additional details
    """
    if details:
        print(f"[conformal-regress] {step}: {details}")
    else:
        print(f"[conformal-regress] {step}")


def format_time_series_summary(model) -> str:
    """
    Format time series specific summary information.
    
    Parameters
    ----------
    model : RegressModel
        Fitted time series model
        
    Returns
    -------
    str
        Formatted time series summary
    """
    lines = []
    
    if hasattr(model, 'date_col') and model.date_col:
        lines.append(f"Time series regression (date column: {model.date_col})")
        
        if hasattr(model, 'n_obs') and model.n_obs:
            lines.append(f"Observations: {model.n_obs}")
        
        if hasattr(model, 'date_range'):
            lines.append(f"Date range: {model.date_range[0]} to {model.date_range[1]}")
        
        # Temporal conformal info
        if hasattr(model, 'temporal_conformal') and model.temporal_conformal:
            lines.append("Temporal conformal prediction enabled")
            
            if hasattr(model, 'rolling_window_size'):
                lines.append(f"Rolling window size: {model.rolling_window_size}")
    
    return "\n".join(lines) if lines else ""