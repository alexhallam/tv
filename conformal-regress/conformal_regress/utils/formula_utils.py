"""
Formula parsing utilities for R-style regression formulas.

This module extends formulaic to support R-compatible syntax including:
- Basic terms: y ~ x1 + x2
- Interactions: y ~ x1 * x2 (expands to x1 + x2 + x1:x2)
- Transformations: y ~ I(x^2) + log(z)
- Categorical handling and more
"""

import re
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from formulaic import model_matrix
from formulaic.parser.types import Factor
import warnings


def parse_formula(formula: str, data: pd.DataFrame, 
                 include_intercept: bool = True) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Parse R-style formula and return design matrix and target vector.
    
    Parameters
    ----------
    formula : str
        R-style formula string like "y ~ x1 + x2" or "y ~ x1 * x2"
    data : pd.DataFrame
        Input data containing all variables in formula
    include_intercept : bool, default True
        Whether to include intercept term
        
    Returns
    -------
    X : np.ndarray
        Design matrix (features)
    y : np.ndarray  
        Target vector
    metadata : dict
        Information about the parsed formula including:
        - 'terms': list of term names
        - 'formula_str': original formula
        - 'intercept': whether intercept was included
        - 'transformations': any transformations applied
    """
    try:
        # Validate formula format
        if '~' not in formula:
            raise ValueError("Formula must contain '~' separator (e.g., 'y ~ x1 + x2')")
        
        # Split into target and predictors
        target_str, predictors_str = formula.split('~', 1)
        target_str = target_str.strip()
        predictors_str = predictors_str.strip()
        
        # Handle special transformations that formulaic might not support
        predictors_str = _preprocess_transformations(predictors_str, data)
        
        # Parse with formulaic
        try:
            # Create the full formula for formulaic
            full_formula = f"{target_str} ~ {predictors_str}"
            
            # Get model matrices
            model_spec = model_matrix(full_formula, data, ensure_full_rank=True)
            
            # Extract target
            y = data[target_str].values
            
            # Extract design matrix  
            X = model_spec.values
            
            # Handle intercept
            if not include_intercept and 'Intercept' in model_spec.columns:
                # Remove intercept column
                intercept_idx = list(model_spec.columns).index('Intercept')
                X = np.delete(X, intercept_idx, axis=1)
                columns = [col for col in model_spec.columns if col != 'Intercept']
            else:
                columns = list(model_spec.columns)
            
            # Create metadata
            metadata = {
                'terms': columns,
                'formula_str': formula,
                'intercept': include_intercept,
                'transformations': _extract_transformations(predictors_str),
                'target_name': target_str,
                'n_features': X.shape[1],
                'feature_names': columns
            }
            
            return X, y, metadata
            
        except Exception as e:
            # Fallback to manual parsing for complex cases
            warnings.warn(f"Formulaic parsing failed ({e}), falling back to manual parsing")
            return _manual_formula_parse(formula, data, include_intercept)
            
    except Exception as e:
        raise ValueError(f"Error parsing formula '{formula}': {str(e)}")


def validate_formula(formula: str, data: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate that a formula is well-formed and variables exist in data.
    
    Parameters
    ----------
    formula : str
        Formula to validate
    data : pd.DataFrame
        Data to check against
        
    Returns
    -------
    dict
        Validation results with 'valid' bool and 'errors' list
    """
    errors = []
    
    try:
        # Basic format check
        if '~' not in formula:
            errors.append("Formula must contain '~' separator")
            return {'valid': False, 'errors': errors}
        
        target_str, predictors_str = formula.split('~', 1)
        target_str = target_str.strip()
        predictors_str = predictors_str.strip()
        
        # Check target variable exists
        if target_str not in data.columns:
            errors.append(f"Target variable '{target_str}' not found in data")
        
        # Extract variable names from predictors
        variables = _extract_variable_names(predictors_str)
        
        # Check all variables exist
        for var in variables:
            if var not in data.columns:
                errors.append(f"Variable '{var}' not found in data")
        
        # Check for numeric target
        if target_str in data.columns:
            if not pd.api.types.is_numeric_dtype(data[target_str]):
                errors.append(f"Target variable '{target_str}' must be numeric")
        
        return {'valid': len(errors) == 0, 'errors': errors}
        
    except Exception as e:
        errors.append(f"Formula parsing error: {str(e)}")
        return {'valid': False, 'errors': errors}


def _preprocess_transformations(predictors_str: str, data: pd.DataFrame) -> str:
    """Preprocess special transformations before formulaic parsing."""
    
    # Handle I() transformations
    # Convert I(x^2) to a new column in data and update formula
    i_pattern = r'I\(([^)]+)\)'
    matches = re.findall(i_pattern, predictors_str)
    
    processed_str = predictors_str
    for i, expr in enumerate(matches):
        # Create a unique column name for this transformation
        new_col_name = f"__I_transform_{i}__"
        
        # Evaluate the expression safely
        try:
            # Simple transformations for now
            if '^2' in expr:
                var_name = expr.replace('^2', '').strip()
                if var_name in data.columns:
                    # Note: We'll need to modify the data in the calling function
                    processed_str = processed_str.replace(f'I({expr})', new_col_name)
            elif 'log(' in expr:
                # Handle log transformations
                var_match = re.search(r'log\(([^)]+)\)', expr)
                if var_match:
                    var_name = var_match.group(1)
                    if var_name in data.columns:
                        processed_str = processed_str.replace(f'I({expr})', new_col_name)
        except:
            pass  # Keep original if transformation fails
    
    return processed_str


def _extract_transformations(predictors_str: str) -> List[str]:
    """Extract transformation functions used in the formula."""
    transformations = []
    
    # Look for I() transformations
    i_pattern = r'I\(([^)]+)\)'
    i_matches = re.findall(i_pattern, predictors_str)
    transformations.extend([f"I({match})" for match in i_matches])
    
    # Look for other function calls
    func_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
    func_matches = re.findall(func_pattern, predictors_str)
    for func in func_matches:
        if func not in ['I']:  # I() handled separately
            transformations.append(func)
    
    return transformations


def _extract_variable_names(predictors_str: str) -> List[str]:
    """Extract all variable names from predictor string."""
    # Remove transformations and operators to find base variables
    cleaned = predictors_str
    
    # Remove function calls
    cleaned = re.sub(r'[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)', '', cleaned)
    
    # Remove operators and whitespace
    cleaned = re.sub(r'[+\-*/:()^]', ' ', cleaned)
    
    # Extract remaining alphanumeric tokens
    variables = []
    for token in cleaned.split():
        token = token.strip()
        if token and not token.isdigit():
            variables.append(token)
    
    return list(set(variables))


def _manual_formula_parse(formula: str, data: pd.DataFrame, 
                         include_intercept: bool = True) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Manual formula parsing as fallback when formulaic fails.
    
    Handles basic cases like "y ~ x1 + x2".
    """
    target_str, predictors_str = formula.split('~', 1)
    target_str = target_str.strip()
    predictors_str = predictors_str.strip()
    
    # Get target
    y = data[target_str].values
    
    # Simple parsing - split by +
    terms = [term.strip() for term in predictors_str.split('+')]
    
    # Build design matrix
    X_cols = []
    feature_names = []
    
    if include_intercept:
        X_cols.append(np.ones(len(data)))
        feature_names.append('Intercept')
    
    for term in terms:
        if term in data.columns:
            X_cols.append(data[term].values)
            feature_names.append(term)
        else:
            warnings.warn(f"Variable '{term}' not found, skipping")
    
    X = np.column_stack(X_cols) if X_cols else np.empty((len(data), 0))
    
    metadata = {
        'terms': feature_names,
        'formula_str': formula,
        'intercept': include_intercept,
        'transformations': [],
        'target_name': target_str,
        'n_features': X.shape[1],
        'feature_names': feature_names
    }
    
    return X, y, metadata


def expand_interactions(formula: str) -> str:
    """
    Expand interaction notation like x1*x2 to x1 + x2 + x1:x2.
    
    Parameters
    ----------
    formula : str
        Formula with potential interactions
        
    Returns
    -------
    str
        Formula with interactions expanded
    """
    # Find interactions (terms with *)
    interaction_pattern = r'(\w+)\s*\*\s*(\w+)'
    
    def expand_interaction(match):
        var1, var2 = match.groups()
        return f"{var1} + {var2} + {var1}:{var2}"
    
    expanded = re.sub(interaction_pattern, expand_interaction, formula)
    return expanded