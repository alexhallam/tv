"""
Main regression function with conformal prediction support.
"""

import pandas as pd
from typing import Optional, Union, Dict, Any
import warnings

from .model import ConformalModel
from ..formula.parser import FormulaParser
from ..models.base import ModelFactory
from ..conformal.base import ConformalDetector


def regress(
    formula: str,
    data: pd.DataFrame,
    method: str = "linear",
    family: str = "gaussian",
    uncertainty: Optional[str] = "conformal",
    date_col: Optional[str] = None,
    **kwargs
) -> ConformalModel:
    """
    Fit a regression model with conformal prediction uncertainty.
    
    Parameters
    ----------
    formula : str
        R-style formula (e.g., "y ~ x1 + x2")
    data : pd.DataFrame
        Input data
    method : str, default="linear"
        Regression method: "linear", "quantile", "robust", "lasso", "ridge"
    family : str, default="gaussian"
        Distribution family: "gaussian", "poisson", "gamma", etc.
    uncertainty : str, optional
        Uncertainty method: "conformal", "conformal_thinning", "conformal_split", 
        "conformal_temporal", or None
    date_col : str, optional
        Date column for time series analysis
    **kwargs
        Additional arguments passed to the model
        
    Returns
    -------
    ConformalModel
        Fitted model with conformal prediction capabilities
        
    Examples
    --------
    >>> import conformal_regress as cr
    >>> model = cr.regress("sales ~ price + advertising", data=df)
    >>> print(model)
    >>> predictions = model.predict(new_data)
    """
    
    # Parse formula
    parser = FormulaParser()
    parsed_formula = parser.parse(formula)
    
    # Create model factory
    factory = ModelFactory()
    
    # Determine conformal method if auto-detection is requested
    if uncertainty == "conformal":
        detector = ConformalDetector()
        uncertainty = detector.detect_method(
            data=data,
            formula=parsed_formula,
            family=family,
            date_col=date_col
        )
    
    # Create base model
    base_model = factory.create_model(
        method=method,
        family=family,
        **kwargs
    )
    
    # Create conformal method if specified
    conformal_method = None
    if uncertainty and uncertainty != "none":
        detector = ConformalDetector()
        conformal_method = detector.create_method(uncertainty)
    
    # Create conformal model
    model = ConformalModel(
        base_model=base_model,
        conformal_method=conformal_method,
        date_col=date_col
    )
    
    # Fit the model
    model.fit(parsed_formula, data)
    
    return model