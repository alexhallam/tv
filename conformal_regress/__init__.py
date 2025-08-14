"""
Conformal Regress: A beginner-friendly, speed-first conformal regression package.

This package provides R-like ergonomics for regression with conformal prediction
uncertainty quantification, optimized for speed and ease of use.
"""

__version__ = "0.1.0"
__author__ = "Conformal Regress Team"

# Main API
from .core.regress import regress
from .core.model import ConformalModel

# Utility functions
from .utils.display import view

# Re-export main classes
__all__ = [
    "regress",
    "ConformalModel", 
    "view",
]