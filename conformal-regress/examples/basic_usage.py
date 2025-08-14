"""
Basic usage examples for conformal-regress package.

This file demonstrates the main functionality and R-like ergonomics of the package.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pandas as pd
import conformal_regress as cr


def example_1_basic_regression():
    """Example 1: Basic linear regression with conformal prediction."""
    print("=" * 60)
    print("Example 1: Basic Linear Regression")
    print("=" * 60)
    
    # Get example housing data
    housing = cr.get_example_data("housing")
    print(f"Dataset shape: {housing.shape}")
    print("\nFirst few rows:")
    print(housing.head())
    
    # Fit basic model
    print("\nFitting model: price ~ bedrooms + sqft + garage")
    model = cr.regress("price ~ bedrooms + sqft + garage", data=housing)
    
    # Print R-style summary
    print("\nModel Summary:")
    print(model.summary())
    
    # Make predictions
    new_houses = housing.iloc[:5].copy()  # Use first 5 rows as "new" data
    predictions = model.predict(new_houses)
    
    print("\nPredictions with uncertainty bands:")
    cr.view(predictions)
    
    return model, predictions


def example_2_interactions():
    """Example 2: Regression with interactions."""
    print("\n" + "=" * 60)
    print("Example 2: Interactions and Transformations")
    print("=" * 60)
    
    # Get sales data
    sales = cr.get_example_data("sales")
    
    # Model with interaction
    print("\nFitting model: sales ~ price * advertising")
    model = cr.regress("sales ~ price * advertising", data=sales)
    
    print("\nModel with interaction:")
    print(model.summary())
    
    # Check conformal method used
    print(f"\nConformal method: {model.conformal_method}")
    print(f"Data thinning eligible: {model.data_thinning_eligible}")
    
    return model


def example_3_manual_conformal():
    """Example 3: Manual conformal method selection."""
    print("\n" + "=" * 60)
    print("Example 3: Manual Conformal Method Selection")
    print("=" * 60)
    
    housing = cr.get_example_data("housing")
    
    # Force data thinning
    print("\nForcing data thinning conformal:")
    model_thinning = cr.regress("price ~ bedrooms + sqft", 
                               data=housing, 
                               uncertainty="conformal_thinning")
    
    predictions_thinning = model_thinning.predict(housing.iloc[:3])
    print("Data thinning results:")
    print(predictions_thinning)
    
    # Force split conformal
    print("\nForcing split conformal:")
    model_split = cr.regress("price ~ bedrooms + sqft", 
                            data=housing, 
                            uncertainty="conformal_split")
    
    predictions_split = model_split.predict(housing.iloc[:3])
    print("\nSplit conformal results:")
    print(predictions_split)
    
    # Compare band widths
    width_thinning = predictions_thinning['upper_95'] - predictions_thinning['lower_95']
    width_split = predictions_split['upper_95'] - predictions_split['lower_95']
    
    print(f"\nAverage band width (data thinning): {width_thinning.mean():.2f}")
    print(f"Average band width (split): {width_split.mean():.2f}")
    
    return model_thinning, model_split


def example_4_time_series():
    """Example 4: Time series regression."""
    print("\n" + "=" * 60)
    print("Example 4: Time Series Regression")
    print("=" * 60)
    
    # Get time series data
    ts_data = cr.get_example_data("timeseries")
    print(f"Time series shape: {ts_data.shape}")
    print("\nTime range:", ts_data['date'].min(), "to", ts_data['date'].max())
    
    # Fit time series model
    print("\nFitting temporal model: sales ~ price + day_of_week")
    model = cr.regress("sales ~ price + day_of_week", 
                      data=ts_data,
                      date_col="date",
                      uncertainty="conformal_temporal")
    
    print("\nTime series model summary:")
    print(model.summary())
    
    # Make predictions on recent data
    recent_data = ts_data.tail(10)
    predictions = model.predict(recent_data)
    
    print("\nRecent predictions:")
    print(predictions)
    
    return model


def example_5_ridge_regression():
    """Example 5: Ridge regression."""
    print("\n" + "=" * 60)
    print("Example 5: Ridge Regression")
    print("=" * 60)
    
    housing = cr.get_example_data("housing")
    
    # Ridge regression
    print("\nFitting ridge regression: price ~ bedrooms + sqft + garage")
    model = cr.regress("price ~ bedrooms + sqft + garage", 
                      data=housing,
                      method="ridge", 
                      alpha=1.0)
    
    print("\nRidge regression summary:")
    print(model.summary())
    
    # Compare with linear
    linear_model = cr.regress("price ~ bedrooms + sqft + garage", 
                             data=housing,
                             method="linear")
    
    print(f"\nR-squared comparison:")
    print(f"Linear: {linear_model.r_squared:.4f}")
    print(f"Ridge:  {model.r_squared:.4f}")
    
    return model


def example_6_model_diagnostics():
    """Example 6: Model diagnostics and properties."""
    print("\n" + "=" * 60)
    print("Example 6: Model Diagnostics")
    print("=" * 60)
    
    housing = cr.get_example_data("housing")
    model = cr.regress("price ~ bedrooms + sqft", data=housing)
    
    # Access model properties (R-like)
    print("Model properties:")
    print(f"R-squared: {model.r_squared:.4f}")
    print(f"Adjusted R-squared: {model.adj_r_squared:.4f}")
    print(f"Residual std error: {model.residual_std_error:.2f}")
    print(f"F-statistic: {model.f_statistic:.2f}")
    print(f"AIC: {model.aic:.2f}")
    print(f"BIC: {model.bic:.2f}")
    print(f"Number of observations: {model.n_obs}")
    print(f"Number of parameters: {model.n_params}")
    
    # Coefficients table
    print("\nCoefficients table:")
    print(model.coefficients)
    
    # Residual analysis
    residuals = model.residuals
    print(f"\nResidual statistics:")
    print(f"Mean: {np.mean(residuals):.6f}")
    print(f"Std: {np.std(residuals):.4f}")
    print(f"Min: {np.min(residuals):.2f}")
    print(f"Max: {np.max(residuals):.2f}")
    
    return model


def run_all_examples():
    """Run all examples."""
    print("Running conformal-regress examples...")
    print("This demonstrates R-like ergonomics with automatic conformal prediction")
    
    try:
        # Example 1: Basic usage
        model1, pred1 = example_1_basic_regression()
        
        # Example 2: Interactions
        model2 = example_2_interactions()
        
        # Example 3: Manual conformal selection
        model3a, model3b = example_3_manual_conformal()
        
        # Example 4: Time series
        model4 = example_4_time_series()
        
        # Example 5: Ridge regression
        model5 = example_5_ridge_regression()
        
        # Example 6: Diagnostics
        model6 = example_6_model_diagnostics()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
        return {
            'basic': model1,
            'interactions': model2,
            'thinning': model3a,
            'split': model3b,
            'timeseries': model4,
            'ridge': model5,
            'diagnostics': model6
        }
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    models = run_all_examples()
    
    if models:
        print("\nExample models created:")
        for name, model in models.items():
            print(f"- {name}: {model}")
        
        print("\nTry exploring the models:")
        print("- models['basic'].summary()")
        print("- models['basic'].predict(new_data)")
        print("- models['basic'].coefficients")
        print("- models['timeseries'].forecast(horizon=30)")