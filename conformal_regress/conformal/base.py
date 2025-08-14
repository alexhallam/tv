"""
Base classes for conformal prediction methods.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from abc import ABC, abstractmethod
import jax
import jax.numpy as jnp
from scipy import stats

from ..models.base import BaseModel
from ..formula.parser import ParsedFormula


class BaseConformalMethod(ABC):
    """Abstract base class for conformal prediction methods."""
    
    def __init__(self, method_name: str = "conformal"):
        self.method_name = method_name
        self.calibrated = False
        self.coverage = None
        self.quantiles = {}
        
    @abstractmethod
    def calibrate(
        self,
        model: BaseModel,
        formula: ParsedFormula,
        data: pd.DataFrame,
        date_col: Optional[str] = None
    ) -> None:
        """Calibrate the conformal method."""
        pass
    
    @abstractmethod
    def predict_intervals(
        self,
        model: BaseModel,
        new_data: pd.DataFrame,
        confidence_levels: List[float]
    ) -> Dict[str, np.ndarray]:
        """Predict conformal intervals."""
        pass


class DataThinningConformal(BaseConformalMethod):
    """
    Conformal prediction using data thinning.
    
    This method uses the generalized data thinning approach from
    Daniella Witten's paper to avoid data splitting when residuals
    are convolution-closed.
    """
    
    def __init__(self):
        super().__init__("data_thinning")
        self.residual_quantiles = {}
        self.thinning_weights = None
        
    def calibrate(
        self,
        model: BaseModel,
        formula: ParsedFormula,
        data: pd.DataFrame,
        date_col: Optional[str] = None
    ) -> None:
        """Calibrate using data thinning."""
        # Get residuals from fitted model
        residuals = model.residuals
        
        # Check if residuals are approximately convolution-closed
        if not self._is_convolution_closed(residuals):
            raise ValueError("Residuals are not convolution-closed. Use data splitting instead.")
        
        # Compute thinning weights
        self.thinning_weights = self._compute_thinning_weights(residuals)
        
        # Store residual quantiles for different confidence levels
        self.residual_quantiles = self._compute_residual_quantiles(residuals)
        
        self.calibrated = True
        
    def _is_convolution_closed(self, residuals: np.ndarray, threshold: float = 0.1) -> bool:
        """
        Check if residuals are approximately convolution-closed.
        
        This is a simplified check - in practice, you'd use more sophisticated
        tests for convolution-closed distributions.
        """
        # Simple test: check if residuals are approximately symmetric
        # and have similar variance across different subsets
        n = len(residuals)
        mid = n // 2
        
        left_residuals = residuals[:mid]
        right_residuals = residuals[mid:]
        
        # Check variance similarity
        var_ratio = np.var(left_residuals) / np.var(right_residuals)
        
        # Check symmetry (skewness close to 0)
        skewness = stats.skew(residuals)
        
        return (0.5 < var_ratio < 2.0) and (abs(skewness) < threshold)
    
    def _compute_thinning_weights(self, residuals: np.ndarray) -> np.ndarray:
        """Compute data thinning weights."""
        # Simplified implementation
        # In practice, you'd implement the full data thinning algorithm
        n = len(residuals)
        weights = np.ones(n) / n  # Equal weights for now
        return weights
    
    def _compute_residual_quantiles(self, residuals: np.ndarray) -> Dict[float, float]:
        """Compute residual quantiles for different confidence levels."""
        quantiles = {}
        for alpha in [0.1, 0.05, 0.01]:  # 90%, 95%, 99% confidence
            lower_quantile = np.percentile(residuals, alpha * 100 / 2)
            upper_quantile = np.percentile(residuals, (1 - alpha / 2) * 100)
            quantiles[alpha] = (lower_quantile, upper_quantile)
        return quantiles
    
    def predict_intervals(
        self,
        model: BaseModel,
        new_data: pd.DataFrame,
        confidence_levels: List[float]
    ) -> Dict[str, np.ndarray]:
        """Predict conformal intervals using data thinning."""
        if not self.calibrated:
            raise ValueError("Method must be calibrated before making predictions")
        
        # Get base predictions
        predictions = model.predict(new_data)
        
        # Compute intervals
        intervals = {}
        for level in confidence_levels:
            alpha = 1 - level
            if alpha in self.residual_quantiles:
                lower_quantile, upper_quantile = self.residual_quantiles[alpha]
                
                intervals[f'lower_{int(alpha*100)}'] = predictions + lower_quantile
                intervals[f'upper_{int(alpha*100)}'] = predictions + upper_quantile
        
        return intervals


class DataSplittingConformal(BaseConformalMethod):
    """
    Traditional conformal prediction using data splitting.
    
    This method splits the data into training and calibration sets.
    """
    
    def __init__(self, train_ratio: float = 0.8):
        super().__init__("data_splitting")
        self.train_ratio = train_ratio
        self.calibration_residuals = None
        
    def calibrate(
        self,
        model: BaseModel,
        formula: ParsedFormula,
        data: pd.DataFrame,
        date_col: Optional[str] = None
    ) -> None:
        """Calibrate using data splitting."""
        n = len(data)
        n_train = int(n * self.train_ratio)
        
        if date_col is not None:
            # Time series: use first n_train observations for training
            train_data = data.iloc[:n_train]
            cal_data = data.iloc[n_train:]
        else:
            # Random split
            indices = np.random.permutation(n)
            train_indices = indices[:n_train]
            cal_indices = indices[n_train:]
            
            train_data = data.iloc[train_indices]
            cal_data = data.iloc[cal_indices]
        
        # Fit model on training data
        train_model = model.__class__()
        train_model.fit(formula, train_data)
        
        # Get residuals on calibration data
        cal_predictions = train_model.predict(cal_data)
        cal_actual = cal_data[formula.response].values
        self.calibration_residuals = cal_actual - cal_predictions
        
        self.calibrated = True
        
    def predict_intervals(
        self,
        model: BaseModel,
        new_data: pd.DataFrame,
        confidence_levels: List[float]
    ) -> Dict[str, np.ndarray]:
        """Predict conformal intervals using data splitting."""
        if not self.calibrated:
            raise ValueError("Method must be calibrated before making predictions")
        
        # Get base predictions
        predictions = model.predict(new_data)
        
        # Compute intervals
        intervals = {}
        for level in confidence_levels:
            alpha = 1 - level
            quantile = np.percentile(self.calibration_residuals, (1 - alpha) * 100)
            
            intervals[f'lower_{int(alpha*100)}'] = predictions - quantile
            intervals[f'upper_{int(alpha*100)}'] = predictions + quantile
        
        return intervals


class TemporalConformal(BaseConformalMethod):
    """
    Conformal prediction for time series data.
    
    This method uses rolling origin validation with data thinning
    when possible, falling back to traditional splitting.
    """
    
    def __init__(self, window_size: int = 100):
        super().__init__("temporal_conformal")
        self.window_size = window_size
        self.residuals_history = []
        
    def calibrate(
        self,
        model: BaseModel,
        formula: ParsedFormula,
        data: pd.DataFrame,
        date_col: Optional[str] = None
    ) -> None:
        """Calibrate using temporal validation."""
        if date_col is None:
            raise ValueError("date_col must be specified for temporal conformal")
        
        # Sort data by date
        data_sorted = data.sort_values(date_col).reset_index(drop=True)
        
        # Rolling origin validation
        n = len(data_sorted)
        residuals_list = []
        
        for i in range(self.window_size, n):
            # Training window
            train_data = data_sorted.iloc[:i]
            
            # Validation point
            val_data = data_sorted.iloc[i:i+1]
            
            # Fit model on training window
            train_model = model.__class__()
            train_model.fit(formula, train_data)
            
            # Get residual for validation point
            val_prediction = train_model.predict(val_data)[0]
            val_actual = val_data[formula.response].iloc[0]
            residual = val_actual - val_prediction
            
            residuals_list.append(residual)
        
        self.residuals_history = np.array(residuals_list)
        
        # Check if residuals are convolution-closed for data thinning
        if self._is_convolution_closed(self.residuals_history):
            # Use data thinning approach
            self.method_name = "temporal_thinning"
            self._calibrate_thinning()
        else:
            # Use traditional approach
            self.method_name = "temporal_splitting"
            self._calibrate_splitting()
        
        self.calibrated = True
        
    def _is_convolution_closed(self, residuals: np.ndarray) -> bool:
        """Check if temporal residuals are convolution-closed."""
        # Similar to data thinning, but adapted for time series
        # Check for stationarity and similar distribution across time windows
        n = len(residuals)
        mid = n // 2
        
        early_residuals = residuals[:mid]
        late_residuals = residuals[mid:]
        
        # Check variance stability
        var_ratio = np.var(early_residuals) / np.var(late_residuals)
        
        # Check for trend in residuals
        trend = np.polyfit(np.arange(n), residuals, 1)[0]
        
        return (0.5 < var_ratio < 2.0) and (abs(trend) < 0.01)
    
    def _calibrate_thinning(self):
        """Calibrate using data thinning approach."""
        # Similar to DataThinningConformal but for temporal data
        self.residual_quantiles = self._compute_residual_quantiles(self.residuals_history)
        
    def _calibrate_splitting(self):
        """Calibrate using traditional splitting approach."""
        # Use the residuals history directly
        pass
    
    def _compute_residual_quantiles(self, residuals: np.ndarray) -> Dict[float, Tuple[float, float]]:
        """Compute residual quantiles."""
        quantiles = {}
        for alpha in [0.1, 0.05, 0.01]:
            lower_quantile = np.percentile(residuals, alpha * 100 / 2)
            upper_quantile = np.percentile(residuals, (1 - alpha / 2) * 100)
            quantiles[alpha] = (lower_quantile, upper_quantile)
        return quantiles
    
    def predict_intervals(
        self,
        model: BaseModel,
        new_data: pd.DataFrame,
        confidence_levels: List[float]
    ) -> Dict[str, np.ndarray]:
        """Predict temporal conformal intervals."""
        if not self.calibrated:
            raise ValueError("Method must be calibrated before making predictions")
        
        predictions = model.predict(new_data)
        intervals = {}
        
        if self.method_name == "temporal_thinning":
            # Use quantile-based intervals
            for level in confidence_levels:
                alpha = 1 - level
                if alpha in self.residual_quantiles:
                    lower_quantile, upper_quantile = self.residual_quantiles[alpha]
                    intervals[f'lower_{int(alpha*100)}'] = predictions + lower_quantile
                    intervals[f'upper_{int(alpha*100)}'] = predictions + upper_quantile
        else:
            # Use traditional approach
            for level in confidence_levels:
                alpha = 1 - level
                quantile = np.percentile(self.residuals_history, (1 - alpha) * 100)
                intervals[f'lower_{int(alpha*100)}'] = predictions - quantile
                intervals[f'upper_{int(alpha*100)}'] = predictions + quantile
        
        return intervals


class ConformalDetector:
    """Detector for choosing appropriate conformal method."""
    
    def __init__(self):
        self.methods = {
            'conformal_thinning': DataThinningConformal,
            'conformal_split': DataSplittingConformal,
            'conformal_temporal': TemporalConformal,
        }
    
    def detect_method(
        self,
        data: pd.DataFrame,
        formula: ParsedFormula,
        family: str,
        date_col: Optional[str] = None
    ) -> str:
        """
        Automatically detect the best conformal method.
        
        Parameters
        ----------
        data : pd.DataFrame
            Input data
        formula : ParsedFormula
            Parsed formula
        family : str
            Distribution family
        date_col : str, optional
            Date column for time series
            
        Returns
        -------
        str
            Recommended conformal method
        """
        if date_col is not None:
            return 'conformal_temporal'
        
        # For now, default to data splitting
        # In practice, you'd implement more sophisticated detection
        return 'conformal_split'
    
    def create_method(self, method_name: str, **kwargs) -> BaseConformalMethod:
        """Create a conformal method instance."""
        if method_name not in self.methods:
            raise ValueError(f"Unknown method: {method_name}")
        
        method_class = self.methods[method_name]
        return method_class(**kwargs)