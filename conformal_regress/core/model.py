"""
Main model class for conformal regression.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
import jax
import jax.numpy as jnp
from dataclasses import dataclass

from ..formula.parser import ParsedFormula
from ..models.base import BaseModel
from ..conformal.base import BaseConformalMethod, DataThinningConformal, DataSplittingConformal, TemporalConformal


@dataclass
class ModelSummary:
    """Model summary statistics in R-like format."""
    formula: str
    coefficients: pd.DataFrame
    residual_std_error: float
    degrees_of_freedom: int
    r_squared: float
    adj_r_squared: float
    f_statistic: float
    f_pvalue: float
    conformal_coverage: Optional[float] = None
    conformal_method: Optional[str] = None


class ConformalModel:
    """
    Main model class for conformal regression.
    
    This class combines a base regression model with conformal prediction
    uncertainty quantification.
    """
    
    def __init__(
        self,
        base_model: BaseModel,
        conformal_method: Optional[BaseConformalMethod] = None,
        date_col: Optional[str] = None
    ):
        self.base_model = base_model
        self.conformal_method = conformal_method
        self.date_col = date_col
        self.fitted = False
        self.summary = None
        
    def fit(self, formula: ParsedFormula, data: pd.DataFrame) -> 'ConformalModel':
        """
        Fit the model with conformal calibration.
        
        Parameters
        ----------
        formula : ParsedFormula
            Parsed formula object
        data : pd.DataFrame
            Training data
            
        Returns
        -------
        self
        """
        # Fit base model
        self.base_model.fit(formula, data)
        
        # Calibrate conformal method if specified
        if self.conformal_method is not None:
            self.conformal_method.calibrate(
                self.base_model, 
                formula, 
                data,
                date_col=self.date_col
            )
        
        self.fitted = True
        self._compute_summary(formula, data)
        
        return self
    
    def predict(
        self, 
        new_data: pd.DataFrame,
        confidence_levels: List[float] = [0.9, 0.95]
    ) -> pd.DataFrame:
        """
        Make predictions with conformal uncertainty intervals.
        
        Parameters
        ----------
        new_data : pd.DataFrame
            New data for prediction
        confidence_levels : List[float]
            Confidence levels for intervals (default: [0.9, 0.95])
            
        Returns
        -------
        pd.DataFrame
            Predictions with uncertainty intervals
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        # Get base predictions
        predictions = self.base_model.predict(new_data)
        
        # Add conformal intervals if available
        if self.conformal_method is not None:
            intervals = self.conformal_method.predict_intervals(
                self.base_model,
                new_data,
                confidence_levels
            )
            
            # Combine predictions with intervals
            result = pd.DataFrame({
                'prediction': predictions
            })
            
            for level in confidence_levels:
                alpha = int((1 - level) * 100)
                result[f'lower_{alpha}'] = intervals[f'lower_{alpha}']
                result[f'upper_{alpha}'] = intervals[f'upper_{alpha}']
            
            # Add samples if available
            if hasattr(self.conformal_method, 'predict_samples'):
                samples = self.conformal_method.predict_samples(
                    self.base_model,
                    new_data
                )
                result['samples'] = [list(s) for s in samples]
            
            return result
        
        return pd.DataFrame({'prediction': predictions})
    
    def forecast(
        self, 
        horizon: int,
        confidence_levels: List[float] = [0.9, 0.95]
    ) -> pd.DataFrame:
        """
        Make time series forecasts with conformal uncertainty.
        
        Parameters
        ----------
        horizon : int
            Number of periods to forecast
        confidence_levels : List[float]
            Confidence levels for intervals
            
        Returns
        -------
        pd.DataFrame
            Forecasts with uncertainty intervals
        """
        if self.date_col is None:
            raise ValueError("date_col must be specified for forecasting")
        
        if not self.fitted:
            raise ValueError("Model must be fitted before forecasting")
        
        # Generate future dates
        last_date = self.base_model.last_date
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=horizon,
            freq='D'
        )
        
        # Create future data frame
        future_data = pd.DataFrame({self.date_col: future_dates})
        
        # Add any required features (this would need to be implemented based on the model)
        # For now, we'll assume the model can handle missing features
        
        return self.predict(future_data, confidence_levels)
    
    def _compute_summary(self, formula: ParsedFormula, data: pd.DataFrame):
        """Compute model summary statistics."""
        # Get base model summary
        base_summary = self.base_model.summary()
        
        # Add conformal information
        conformal_coverage = None
        conformal_method = None
        
        if self.conformal_method is not None:
            conformal_coverage = self.conformal_method.coverage
            conformal_method = self.conformal_method.method_name
        
        self.summary = ModelSummary(
            formula=str(formula),
            coefficients=base_summary.coefficients,
            residual_std_error=base_summary.residual_std_error,
            degrees_of_freedom=base_summary.degrees_of_freedom,
            r_squared=base_summary.r_squared,
            adj_r_squared=base_summary.adj_r_squared,
            f_statistic=base_summary.f_statistic,
            f_pvalue=base_summary.f_pvalue,
            conformal_coverage=conformal_coverage,
            conformal_method=conformal_method
        )
    
    def __str__(self) -> str:
        """R-like model summary string."""
        if not self.fitted:
            return "Unfitted ConformalModel"
        
        lines = []
        lines.append(f"Formula: {self.summary.formula}")
        lines.append("")
        
        # Coefficients table
        lines.append("Coefficients:")
        coef_df = self.summary.coefficients.copy()
        coef_df['Pr(>|t|)'] = coef_df['p_value'].apply(
            lambda x: f"{x:.2e}" if x < 0.001 else f"{x:.3f}"
        )
        coef_df['Significance'] = coef_df['p_value'].apply(
            lambda x: '***' if x < 0.001 else '**' if x < 0.01 else '*' if x < 0.05 else ''
        )
        
        # Format the coefficients table
        coef_str = coef_df.to_string(
            columns=['Estimate', 'Std_Error', 't_value', 'Pr(>|t|)', 'Significance'],
            index=True,
            float_format='%.3f'
        )
        lines.append(coef_str)
        lines.append("")
        
        # Model statistics
        lines.append(f"Residual standard error: {self.summary.residual_std_error:.2f} on {self.summary.degrees_of_freedom} degrees of freedom")
        lines.append(f"Multiple R-squared: {self.summary.r_squared:.4f}")
        lines.append(f"Adjusted R-squared: {self.summary.adj_r_squared:.4f}")
        lines.append(f"F-statistic: {self.summary.f_statistic:.2f} on {len(self.summary.coefficients)-1} and {self.summary.degrees_of_freedom} DF, p-value: {self.summary.f_pvalue:.2e}")
        
        # Conformal information
        if self.summary.conformal_coverage is not None:
            lines.append(f"Conformal Coverage: {self.summary.conformal_coverage:.1%} (method: {self.summary.conformal_method})")
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return self.__str__()
    
    @property
    def coefficients(self) -> pd.DataFrame:
        """Get model coefficients."""
        if not self.fitted:
            raise ValueError("Model must be fitted first")
        return self.summary.coefficients
    
    @property
    def formula(self) -> str:
        """Get the original formula string."""
        if not self.fitted:
            raise ValueError("Model must be fitted first")
        return self.summary.formula
    
    @property
    def coverage(self) -> Optional[float]:
        """Get actual conformal coverage achieved."""
        if not self.fitted or self.summary.conformal_coverage is None:
            return None
        return self.summary.conformal_coverage
    
    @property
    def method(self) -> Optional[str]:
        """Get the conformal method used."""
        if not self.fitted or self.summary.conformal_method is None:
            return None
        return self.summary.conformal_method