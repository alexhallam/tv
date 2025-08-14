"""
Display utilities for conformal regression results.
"""

import pandas as pd
from typing import Optional, Union, Any
import warnings

try:
    from tidy_viewer_py import view as tidy_view
    TIDY_VIEWER_AVAILABLE = True
except ImportError:
    TIDY_VIEWER_AVAILABLE = False
    warnings.warn("tidy-viewer-py not available. Install with: pip install tidy-viewer-py")


def view(data: Union[pd.DataFrame, Any], **kwargs) -> None:
    """
    Display data using tidy-viewer-py if available, otherwise use pandas display.
    
    Parameters
    ----------
    data : Union[pd.DataFrame, Any]
        Data to display
    **kwargs
        Additional arguments passed to the viewer
    """
    if TIDY_VIEWER_AVAILABLE:
        tidy_view(data, **kwargs)
    else:
        # Fallback to pandas display
        if isinstance(data, pd.DataFrame):
            print(data.to_string())
        else:
            print(data)


def format_predictions(predictions: pd.DataFrame, confidence_levels: list = [0.9, 0.95]) -> pd.DataFrame:
    """
    Format predictions for display.
    
    Parameters
    ----------
    predictions : pd.DataFrame
        Predictions with uncertainty intervals
    confidence_levels : list
        Confidence levels to include
        
    Returns
    -------
    pd.DataFrame
        Formatted predictions
    """
    # Create a copy for formatting
    formatted = predictions.copy()
    
    # Round numeric columns
    numeric_cols = formatted.select_dtypes(include=['float64', 'int64']).columns
    formatted[numeric_cols] = formatted[numeric_cols].round(3)
    
    # Add confidence level information
    if 'prediction' in formatted.columns:
        formatted['prediction'] = formatted['prediction'].astype(str)
        
        # Add interval information
        for level in confidence_levels:
            alpha = int((1 - level) * 100)
            lower_col = f'lower_{alpha}'
            upper_col = f'upper_{alpha}'
            
            if lower_col in formatted.columns and upper_col in formatted.columns:
                formatted[f'{level*100:.0f}%_CI'] = (
                    f"[{formatted[lower_col]}, {formatted[upper_col]}]"
                )
    
    return formatted


def print_model_summary(model, detailed: bool = False) -> None:
    """
    Print a formatted model summary.
    
    Parameters
    ----------
    model : ConformalModel
        Fitted model
    detailed : bool
        Whether to print detailed information
    """
    print(str(model))
    
    if detailed and hasattr(model, 'summary'):
        summary = model.summary
        print("\n" + "="*50)
        print("DETAILED SUMMARY")
        print("="*50)
        
        # Print additional statistics
        if hasattr(summary, 'aic'):
            print(f"AIC: {summary.aic:.2f}")
        if hasattr(summary, 'bic'):
            print(f"BIC: {summary.bic:.2f}")
        
        # Print conformal information
        if summary.conformal_coverage is not None:
            print(f"\nConformal Prediction:")
            print(f"  Method: {summary.conformal_method}")
            print(f"  Coverage: {summary.conformal_coverage:.1%}")
            print(f"  Calibration: {'✓' if model.conformal_method.calibrated else '✗'}")


def plot_predictions(predictions: pd.DataFrame, actual: Optional[pd.Series] = None, 
                   confidence_levels: list = [0.9, 0.95], **kwargs) -> None:
    """
    Plot predictions with uncertainty intervals.
    
    Parameters
    ----------
    predictions : pd.DataFrame
        Predictions with uncertainty intervals
    actual : pd.Series, optional
        Actual values for comparison
    confidence_levels : list
        Confidence levels to plot
    **kwargs
        Additional plotting arguments
    """
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        print("matplotlib and seaborn required for plotting. Install with: pip install matplotlib seaborn")
        return
    
    # Set style
    plt.style.use('seaborn-v0_8')
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot predictions
    x = range(len(predictions))
    ax.plot(x, predictions['prediction'], 'b-', label='Prediction', linewidth=2)
    
    # Plot confidence intervals
    colors = ['lightblue', 'lightgreen']
    for i, level in enumerate(confidence_levels):
        alpha = int((1 - level) * 100)
        lower_col = f'lower_{alpha}'
        upper_col = f'upper_{alpha}'
        
        if lower_col in predictions.columns and upper_col in predictions.columns:
            ax.fill_between(x, predictions[lower_col], predictions[upper_col], 
                          alpha=0.3, color=colors[i], 
                          label=f'{level*100:.0f}% Confidence')
    
    # Plot actual values if provided
    if actual is not None:
        ax.plot(x, actual, 'ro', label='Actual', markersize=4)
    
    # Customize plot
    ax.set_xlabel('Observation')
    ax.set_ylabel('Value')
    ax.set_title('Predictions with Conformal Uncertainty Intervals')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def create_summary_table(model) -> pd.DataFrame:
    """
    Create a summary table for the model.
    
    Parameters
    ----------
    model : ConformalModel
        Fitted model
        
    Returns
    -------
    pd.DataFrame
        Summary table
    """
    if not hasattr(model, 'summary'):
        return pd.DataFrame()
    
    summary = model.summary
    
    # Create summary table
    summary_data = {
        'Metric': [
            'Formula',
            'Method',
            'Family',
            'Observations',
            'Parameters',
            'R-squared',
            'Adjusted R-squared',
            'Residual Std Error',
            'F-statistic',
            'F p-value',
            'Conformal Method',
            'Conformal Coverage'
        ],
        'Value': [
            summary.formula,
            getattr(model.base_model, '__class__.__name__', 'Unknown'),
            getattr(model.base_model, 'family', 'Unknown'),
            len(model.base_model.y) if hasattr(model.base_model, 'y') else 'Unknown',
            len(summary.coefficients),
            f"{summary.r_squared:.4f}",
            f"{summary.adj_r_squared:.4f}",
            f"{summary.residual_std_error:.3f}",
            f"{summary.f_statistic:.2f}",
            f"{summary.f_pvalue:.2e}",
            summary.conformal_method or 'None',
            f"{summary.conformal_coverage:.1%}" if summary.conformal_coverage else 'None'
        ]
    }
    
    return pd.DataFrame(summary_data)


def export_results(model, predictions: pd.DataFrame, filename: str, format: str = 'csv') -> None:
    """
    Export model results and predictions.
    
    Parameters
    ----------
    model : ConformalModel
        Fitted model
    predictions : pd.DataFrame
        Predictions to export
    filename : str
        Output filename
    format : str
        Export format ('csv', 'excel', 'json')
    """
    if format == 'csv':
        predictions.to_csv(filename, index=False)
    elif format == 'excel':
        with pd.ExcelWriter(filename) as writer:
            predictions.to_excel(writer, sheet_name='Predictions', index=False)
            create_summary_table(model).to_excel(writer, sheet_name='Summary', index=False)
            model.coefficients.to_excel(writer, sheet_name='Coefficients')
    elif format == 'json':
        results = {
            'predictions': predictions.to_dict('records'),
            'summary': create_summary_table(model).to_dict('records'),
            'coefficients': model.coefficients.to_dict('index')
        }
        import json
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    print(f"Results exported to {filename}")