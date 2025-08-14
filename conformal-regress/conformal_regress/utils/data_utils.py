"""
Data preparation and validation utilities.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Optional, Any, List
import warnings


def prepare_data(data: pd.DataFrame, 
                formula: str,
                date_col: Optional[str] = None,
                dropna: bool = True) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Prepare data for regression analysis.
    
    Parameters
    ----------
    data : pd.DataFrame
        Raw input data
    formula : str
        Regression formula to determine required variables
    date_col : str, optional
        Name of date column for time series analysis
    dropna : bool, default True
        Whether to drop rows with missing values
        
    Returns
    -------
    pd.DataFrame
        Cleaned and prepared data
    dict
        Metadata about the preparation process
    """
    # Make a copy to avoid modifying original
    prepared_data = data.copy()
    
    metadata = {
        'original_shape': data.shape,
        'dropped_rows': 0,
        'date_col': date_col,
        'time_series': date_col is not None,
        'transformations_applied': []
    }
    
    # Extract variables needed from formula
    if '~' in formula:
        target_str, predictors_str = formula.split('~', 1)
        target_str = target_str.strip()
        
        # Get all variable names (simplified extraction)
        import re
        # Remove function calls and operators to find base variables
        cleaned = re.sub(r'[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)', '', predictors_str)
        cleaned = re.sub(r'[+\-*/:()^]', ' ', cleaned)
        predictor_vars = [token.strip() for token in cleaned.split() 
                         if token.strip() and not token.isdigit()]
        
        required_vars = [target_str] + predictor_vars
        if date_col:
            required_vars.append(date_col)
        
        # Check that all required variables exist
        missing_vars = [var for var in required_vars if var not in prepared_data.columns]
        if missing_vars:
            raise ValueError(f"Variables not found in data: {missing_vars}")
    
    # Handle date column if specified
    if date_col:
        if date_col not in prepared_data.columns:
            raise ValueError(f"Date column '{date_col}' not found in data")
        
        # Convert to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(prepared_data[date_col]):
            try:
                prepared_data[date_col] = pd.to_datetime(prepared_data[date_col])
                metadata['transformations_applied'].append(f"Converted {date_col} to datetime")
            except Exception as e:
                warnings.warn(f"Could not convert {date_col} to datetime: {e}")
        
        # Sort by date
        prepared_data = prepared_data.sort_values(date_col)
        metadata['transformations_applied'].append(f"Sorted by {date_col}")
    
    # Handle missing values
    if dropna:
        initial_rows = len(prepared_data)
        if date_col:
            # Only drop NAs in the subset of variables we need, keep date ordering
            subset_vars = [var for var in required_vars if var != date_col]
            prepared_data = prepared_data.dropna(subset=subset_vars)
        else:
            prepared_data = prepared_data.dropna()
        
        rows_dropped = initial_rows - len(prepared_data)
        metadata['dropped_rows'] = rows_dropped
        
        if rows_dropped > 0:
            metadata['transformations_applied'].append(f"Dropped {rows_dropped} rows with missing values")
    
    # Reset index after any filtering
    prepared_data = prepared_data.reset_index(drop=True)
    metadata['final_shape'] = prepared_data.shape
    
    return prepared_data, metadata


def validate_data(data: pd.DataFrame, 
                 formula: str,
                 min_samples: int = 10,
                 check_target_variance: bool = True) -> Dict[str, Any]:
    """
    Validate data for regression analysis.
    
    Parameters
    ----------
    data : pd.DataFrame
        Data to validate
    formula : str
        Regression formula
    min_samples : int, default 10
        Minimum number of samples required
    check_target_variance : bool, default True
        Whether to check that target has non-zero variance
        
    Returns
    -------
    dict
        Validation results with 'valid' bool, 'errors' list, and 'warnings' list
    """
    errors = []
    warnings_list = []
    
    # Basic data checks
    if len(data) < min_samples:
        errors.append(f"Insufficient data: {len(data)} samples, minimum {min_samples} required")
    
    if data.empty:
        errors.append("Data is empty")
        return {'valid': False, 'errors': errors, 'warnings': warnings_list}
    
    # Extract target and predictor variables from formula
    try:
        if '~' not in formula:
            errors.append("Formula must contain '~' separator")
            return {'valid': False, 'errors': errors, 'warnings': warnings_list}
        
        target_str, predictors_str = formula.split('~', 1)
        target_str = target_str.strip()
        
        # Check target variable
        if target_str not in data.columns:
            errors.append(f"Target variable '{target_str}' not found in data")
        else:
            target_data = data[target_str]
            
            # Check target is numeric
            if not pd.api.types.is_numeric_dtype(target_data):
                errors.append(f"Target variable '{target_str}' must be numeric")
            
            # Check for variance in target
            if check_target_variance and pd.api.types.is_numeric_dtype(target_data):
                if target_data.var() == 0:
                    errors.append(f"Target variable '{target_str}' has zero variance")
                elif target_data.var() < 1e-10:
                    warnings_list.append(f"Target variable '{target_str}' has very low variance")
            
            # Check for infinite or extremely large values
            if pd.api.types.is_numeric_dtype(target_data):
                if np.any(np.isinf(target_data)):
                    errors.append(f"Target variable '{target_str}' contains infinite values")
                
                if np.any(np.abs(target_data) > 1e15):
                    warnings_list.append(f"Target variable '{target_str}' contains very large values")
        
        # Extract and check predictor variables
        import re
        cleaned = re.sub(r'[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)', '', predictors_str)
        cleaned = re.sub(r'[+\-*/:()^]', ' ', cleaned)
        predictor_vars = [token.strip() for token in cleaned.split() 
                         if token.strip() and not token.isdigit()]
        
        for var in predictor_vars:
            if var not in data.columns:
                errors.append(f"Predictor variable '{var}' not found in data")
            else:
                var_data = data[var]
                
                # Check for infinite values
                if pd.api.types.is_numeric_dtype(var_data):
                    if np.any(np.isinf(var_data)):
                        errors.append(f"Variable '{var}' contains infinite values")
                    
                    # Check for zero variance (constant variables)
                    if var_data.var() == 0:
                        warnings_list.append(f"Variable '{var}' is constant (zero variance)")
                    
                    # Check for very large values
                    if np.any(np.abs(var_data) > 1e15):
                        warnings_list.append(f"Variable '{var}' contains very large values")
        
        # Check for multicollinearity (basic check)
        numeric_predictors = [var for var in predictor_vars 
                            if var in data.columns and pd.api.types.is_numeric_dtype(data[var])]
        
        if len(numeric_predictors) > 1:
            corr_matrix = data[numeric_predictors].corr()
            high_corr_pairs = []
            
            for i in range(len(numeric_predictors)):
                for j in range(i+1, len(numeric_predictors)):
                    corr_val = abs(corr_matrix.iloc[i, j])
                    if corr_val > 0.95:
                        high_corr_pairs.append((numeric_predictors[i], numeric_predictors[j], corr_val))
            
            if high_corr_pairs:
                for var1, var2, corr in high_corr_pairs:
                    warnings_list.append(f"High correlation ({corr:.3f}) between '{var1}' and '{var2}'")
        
    except Exception as e:
        errors.append(f"Error validating formula: {str(e)}")
    
    # Check missing values
    missing_info = data.isnull().sum()
    variables_with_missing = missing_info[missing_info > 0]
    
    if len(variables_with_missing) > 0:
        total_missing = missing_info.sum()
        warnings_list.append(f"Data contains {total_missing} missing values across {len(variables_with_missing)} variables")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings_list,
        'n_samples': len(data),
        'n_variables': len(data.columns),
        'missing_values': missing_info.to_dict()
    }


def split_data(data: pd.DataFrame, 
               test_size: float = 0.2,
               random_state: Optional[int] = None,
               stratify: Optional[str] = None,
               date_col: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split data into training and testing sets.
    
    Parameters
    ----------
    data : pd.DataFrame
        Data to split
    test_size : float, default 0.2
        Proportion of data to use for testing
    random_state : int, optional
        Random seed for reproducibility
    stratify : str, optional
        Column name to stratify split by
    date_col : str, optional
        If provided, split respects temporal order (latest data for test)
        
    Returns
    -------
    train_data : pd.DataFrame
        Training data
    test_data : pd.DataFrame
        Testing data
    """
    if date_col:
        # Temporal split - latest data for test
        if date_col not in data.columns:
            raise ValueError(f"Date column '{date_col}' not found in data")
        
        # Sort by date
        data_sorted = data.sort_values(date_col)
        
        # Split based on time
        n_test = int(len(data_sorted) * test_size)
        train_data = data_sorted.iloc[:-n_test].copy()
        test_data = data_sorted.iloc[-n_test:].copy()
        
    else:
        # Random split
        if random_state:
            np.random.seed(random_state)
        
        if stratify and stratify in data.columns:
            # Stratified split (for categorical targets)
            from sklearn.model_selection import train_test_split
            train_idx, test_idx = train_test_split(
                range(len(data)), 
                test_size=test_size,
                random_state=random_state,
                stratify=data[stratify]
            )
            train_data = data.iloc[train_idx].copy()
            test_data = data.iloc[test_idx].copy()
        else:
            # Simple random split
            n_test = int(len(data) * test_size)
            indices = np.random.permutation(len(data))
            test_idx = indices[:n_test]
            train_idx = indices[n_test:]
            
            train_data = data.iloc[train_idx].copy()
            test_data = data.iloc[test_idx].copy()
    
    return train_data, test_data


def detect_outliers(data: pd.DataFrame, 
                   columns: Optional[List[str]] = None,
                   method: str = 'iqr',
                   threshold: float = 1.5) -> pd.DataFrame:
    """
    Detect outliers in the data.
    
    Parameters
    ----------
    data : pd.DataFrame
        Data to check for outliers
    columns : list of str, optional
        Columns to check. If None, checks all numeric columns
    method : str, default 'iqr'
        Method for outlier detection: 'iqr', 'zscore', or 'isolation'
    threshold : float, default 1.5
        Threshold for outlier detection
        
    Returns
    -------
    pd.DataFrame
        Boolean DataFrame indicating outliers
    """
    if columns is None:
        columns = data.select_dtypes(include=[np.number]).columns.tolist()
    
    outliers = pd.DataFrame(False, index=data.index, columns=columns)
    
    for col in columns:
        if col in data.columns and pd.api.types.is_numeric_dtype(data[col]):
            col_data = data[col].dropna()
            
            if method == 'iqr':
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outliers[col] = (data[col] < lower_bound) | (data[col] > upper_bound)
                
            elif method == 'zscore':
                z_scores = np.abs((data[col] - col_data.mean()) / col_data.std())
                outliers[col] = z_scores > threshold
                
            elif method == 'isolation':
                try:
                    from sklearn.ensemble import IsolationForest
                    iso_forest = IsolationForest(contamination=0.1, random_state=42)
                    outlier_labels = iso_forest.fit_predict(data[col].values.reshape(-1, 1))
                    outliers[col] = outlier_labels == -1
                except ImportError:
                    warnings.warn("sklearn not available, falling back to IQR method")
                    Q1 = col_data.quantile(0.25)
                    Q3 = col_data.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - threshold * IQR
                    upper_bound = Q3 + threshold * IQR
                    outliers[col] = (data[col] < lower_bound) | (data[col] > upper_bound)
    
    return outliers