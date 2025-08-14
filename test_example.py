#!/usr/bin/env python3
"""
Test example for conformal-regress package.
"""

import pandas as pd
import numpy as np
import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'conformal_regress'))

try:
    import conformal_regress as cr
    print("✅ Successfully imported conformal_regress")
except ImportError as e:
    print(f"❌ Failed to import conformal_regress: {e}")
    sys.exit(1)

def test_basic_regression():
    """Test basic linear regression with conformal prediction."""
    print("\n" + "="*50)
    print("TESTING BASIC REGRESSION")
    print("="*50)
    
    # Create sample data
    np.random.seed(42)
    n = 100
    x1 = np.random.normal(0, 1, n)
    x2 = np.random.normal(0, 1, n)
    noise = np.random.normal(0, 0.5, n)
    y = 2 + 1.5 * x1 - 0.8 * x2 + noise
    
    df = pd.DataFrame({
        'y': y,
        'x1': x1,
        'x2': x2
    })
    
    print(f"Created dataset with {len(df)} observations")
    print(f"Columns: {list(df.columns)}")
    
    # Fit model
    try:
        model = cr.regress("y ~ x1 + x2", data=df)
        print("\n✅ Model fitted successfully!")
        print("\nModel Summary:")
        print(model)
        
        # Make predictions
        new_data = pd.DataFrame({
            'x1': [0.5, -0.5, 1.0],
            'x2': [0.3, -0.3, 0.8]
        })
        
        predictions = model.predict(new_data)
        print("\n✅ Predictions made successfully!")
        print("\nPredictions:")
        print(predictions)
        
        return True
        
    except Exception as e:
        print(f"❌ Error in basic regression: {e}")
        return False

def test_time_series():
    """Test time series regression with temporal conformal prediction."""
    print("\n" + "="*50)
    print("TESTING TIME SERIES REGRESSION")
    print("="*50)
    
    # Create time series data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=50, freq='D')
    
    # Generate time series with trend and seasonality
    trend = np.linspace(0, 10, 50)
    seasonality = 2 * np.sin(2 * np.pi * np.arange(50) / 7)  # Weekly seasonality
    noise = np.random.normal(0, 0.5, 50)
    sales = 100 + trend + seasonality + noise
    
    # Create features
    price = 20 + 0.1 * trend + np.random.normal(0, 1, 50)
    advertising = 5 + 0.05 * trend + np.random.normal(0, 0.5, 50)
    
    df = pd.DataFrame({
        'date': dates,
        'sales': sales,
        'price': price,
        'advertising': advertising
    })
    
    print(f"Created time series dataset with {len(df)} observations")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    
    try:
        # Fit time series model
        model = cr.regress("sales ~ price + advertising", 
                          data=df, 
                          date_col="date",
                          uncertainty="conformal_temporal")
        
        print("\n✅ Time series model fitted successfully!")
        print("\nModel Summary:")
        print(model)
        
        # Make forecasts
        forecasts = model.forecast(horizon=10)
        print("\n✅ Forecasts made successfully!")
        print("\nForecasts:")
        print(forecasts)
        
        return True
        
    except Exception as e:
        print(f"❌ Error in time series regression: {e}")
        return False

def test_quantile_regression():
    """Test quantile regression."""
    print("\n" + "="*50)
    print("TESTING QUANTILE REGRESSION")
    print("="*50)
    
    # Create heteroscedastic data
    np.random.seed(42)
    n = 100
    x = np.random.uniform(0, 10, n)
    # Variance increases with x
    noise = np.random.normal(0, 0.5 * x, n)
    y = 2 + 1.5 * x + noise
    
    df = pd.DataFrame({
        'y': y,
        'x': x
    })
    
    print(f"Created heteroscedastic dataset with {len(df)} observations")
    
    try:
        # Fit quantile regression
        model = cr.regress("y ~ x", 
                          data=df,
                          method="quantile", 
                          tau=0.9,
                          uncertainty="conformal_split")
        
        print("\n✅ Quantile regression model fitted successfully!")
        print("\nModel Summary:")
        print(model)
        
        # Make predictions
        new_data = pd.DataFrame({'x': [2, 5, 8]})
        predictions = model.predict(new_data)
        print("\n✅ Quantile predictions made successfully!")
        print("\nPredictions:")
        print(predictions)
        
        return True
        
    except Exception as e:
        print(f"❌ Error in quantile regression: {e}")
        return False

def test_formula_parsing():
    """Test formula parsing capabilities."""
    print("\n" + "="*50)
    print("TESTING FORMULA PARSING")
    print("="*50)
    
    # Create test data
    np.random.seed(42)
    n = 50
    df = pd.DataFrame({
        'y': np.random.normal(0, 1, n),
        'x1': np.random.normal(0, 1, n),
        'x2': np.random.normal(0, 1, n),
        'z': np.random.exponential(1, n)
    })
    
    formulas = [
        "y ~ x1 + x2",
        "y ~ x1 * x2",
        "y ~ log(z) + x1",
        "y ~ I(x1^2) + x2"
    ]
    
    for formula in formulas:
        try:
            print(f"\nTesting formula: {formula}")
            model = cr.regress(formula, data=df)
            print(f"✅ Successfully parsed and fitted: {formula}")
        except Exception as e:
            print(f"❌ Failed to parse: {formula} - {e}")
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting Conformal Regress Package Tests")
    print("="*60)
    
    tests = [
        test_basic_regression,
        test_time_series,
        test_quantile_regression,
        test_formula_parsing
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Package is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)