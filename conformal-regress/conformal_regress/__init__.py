"""
conformal-regress: Fast, beginner-friendly conformal regression with R-like ergonomics

This package provides:
- R-style formula syntax for regression
- Automatic conformal prediction with data thinning when possible
- Speed-optimized backends using JAX and LAPACK
- Beginner-friendly output formats
"""

__version__ = "0.1.0"
__author__ = "Conformal Regress Team"

from .core.regress import regress
from .core.model import RegressModel
from .utils.display import view
from .conformal.methods import (
    conformal_predict,
    detect_data_thinning_eligibility,
)

# Main API exports
__all__ = [
    "regress",
    "RegressModel", 
    "view",
    "conformal_predict",
    "detect_data_thinning_eligibility",
]

# Convenience imports for users
import pandas as pd
import numpy as np

def get_example_data(dataset="housing"):
    """
    Get example datasets for testing and learning.
    
    Parameters
    ----------
    dataset : str, default "housing"
        Dataset name. Options: "housing", "sales", "timeseries"
        
    Returns
    -------
    pd.DataFrame
        Example dataset with appropriate columns
    """
    if dataset == "housing":
        np.random.seed(42)
        n = 1000
        bedrooms = np.random.randint(1, 6, n)
        sqft = np.random.normal(2000, 500, n)
        price = 100000 + 50000 * bedrooms + 150 * sqft + np.random.normal(0, 20000, n)
        
        return pd.DataFrame({
            'price': price,
            'bedrooms': bedrooms,
            'sqft': sqft,
            'garage': np.random.choice([0, 1, 2], n, p=[0.3, 0.5, 0.2])
        })
    
    elif dataset == "sales":
        np.random.seed(42)
        n = 500
        advertising = np.random.normal(1000, 300, n)
        price = np.random.normal(50, 15, n) 
        sales = 1000 + 2.5 * advertising - 20 * price + np.random.normal(0, 100, n)
        
        return pd.DataFrame({
            'sales': sales,
            'advertising': advertising,
            'price': price,
            'season': np.random.choice(['spring', 'summer', 'fall', 'winter'], n)
        })
        
    elif dataset == "timeseries":
        np.random.seed(42)
        dates = pd.date_range('2020-01-01', periods=365, freq='D')
        trend = np.linspace(100, 200, 365)
        seasonal = 20 * np.sin(2 * np.pi * np.arange(365) / 365.25)
        noise = np.random.normal(0, 10, 365)
        sales = trend + seasonal + noise
        
        price = 50 + 0.1 * sales + np.random.normal(0, 5, 365)
        
        return pd.DataFrame({
            'date': dates,
            'sales': sales,
            'price': price,
            'day_of_week': dates.dayofweek
        })
    
    else:
        raise ValueError(f"Unknown dataset: {dataset}. Options: 'housing', 'sales', 'timeseries'")