"""
Basic tests for conformal-regress package.
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

# Add package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import conformal_regress as cr


class TestBasicFunctionality:
    """Test basic package functionality."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        np.random.seed(42)
        n = 100
        x1 = np.random.normal(0, 1, n)
        x2 = np.random.normal(0, 1, n)
        y = 2 + 3*x1 + 4*x2 + np.random.normal(0, 1, n)
        
        return pd.DataFrame({
            'y': y,
            'x1': x1,
            'x2': x2
        })
    
    def test_package_import(self):
        """Test that package imports correctly."""
        assert hasattr(cr, 'regress')
        assert hasattr(cr, 'get_example_data')
        assert hasattr(cr, 'view')
    
    def test_basic_regression(self, sample_data):
        """Test basic linear regression."""
        model = cr.regress("y ~ x1 + x2", data=sample_data)
        
        # Check model was fitted
        assert model.backend_model_ is not None
        assert model.r_squared is not None
        assert model.coefficients is not None
        
        # Check reasonable R-squared
        assert 0.5 < model.r_squared < 1.0
        
        # Check predictions work
        predictions = model.predict()
        assert len(predictions) == len(sample_data)
        assert 'prediction' in predictions.columns
    
    def test_conformal_prediction(self, sample_data):
        """Test conformal prediction intervals."""
        model = cr.regress("y ~ x1 + x2", data=sample_data)
        predictions = model.predict()
        
        # Check uncertainty bands are present
        assert 'lower_90' in predictions.columns
        assert 'upper_90' in predictions.columns
        assert 'lower_95' in predictions.columns
        assert 'upper_95' in predictions.columns
        
        # Check intervals are reasonable
        band_width_90 = predictions['upper_90'] - predictions['lower_90']
        band_width_95 = predictions['upper_95'] - predictions['lower_95']
        
        # 95% bands should be wider than 90%
        assert np.all(band_width_95 > band_width_90)
        
        # Bands should be positive
        assert np.all(band_width_90 > 0)
        assert np.all(band_width_95 > 0)
    
    def test_formula_parsing(self, sample_data):
        """Test formula parsing functionality."""
        # Basic formula
        model1 = cr.regress("y ~ x1", data=sample_data)
        assert model1.formula_metadata_['n_features'] == 2  # x1 + intercept
        
        # Multiple variables
        model2 = cr.regress("y ~ x1 + x2", data=sample_data)
        assert model2.formula_metadata_['n_features'] == 3  # x1 + x2 + intercept
        
        # No intercept
        model3 = cr.regress("y ~ x1 + x2", data=sample_data, fit_intercept=False)
        assert model3.formula_metadata_['n_features'] == 2  # x1 + x2, no intercept
    
    def test_data_thinning_detection(self, sample_data):
        """Test data thinning eligibility detection."""
        model = cr.regress("y ~ x1 + x2", data=sample_data)
        
        # Should detect data thinning eligibility for Gaussian data
        assert model.data_thinning_eligible is not None
        assert model.data_thinning_reason is not None
        
        # Check conformal method was selected
        assert model.conformal_method in ['data_thinning', 'split']
    
    def test_ridge_regression(self, sample_data):
        """Test ridge regression."""
        model = cr.regress("y ~ x1 + x2", data=sample_data, method="ridge", alpha=1.0)
        
        # Should still work and have reasonable fit
        assert model.r_squared is not None
        assert 0.3 < model.r_squared < 1.0
        
        # Should have predictions
        predictions = model.predict()
        assert len(predictions) == len(sample_data)
    
    def test_example_data(self):
        """Test example data generation."""
        # Housing data
        housing = cr.get_example_data("housing")
        assert isinstance(housing, pd.DataFrame)
        assert len(housing) > 0
        assert 'price' in housing.columns
        assert 'bedrooms' in housing.columns
        
        # Sales data
        sales = cr.get_example_data("sales")
        assert isinstance(sales, pd.DataFrame)
        assert 'sales' in sales.columns
        assert 'advertising' in sales.columns
        
        # Time series data
        ts_data = cr.get_example_data("timeseries")
        assert isinstance(ts_data, pd.DataFrame)
        assert 'date' in ts_data.columns
        assert pd.api.types.is_datetime64_any_dtype(ts_data['date'])
    
    def test_model_properties(self, sample_data):
        """Test R-like model properties."""
        model = cr.regress("y ~ x1 + x2", data=sample_data)
        
        # Test all properties are accessible
        assert model.r_squared is not None
        assert model.adj_r_squared is not None
        assert model.residual_std_error is not None
        assert model.f_statistic is not None
        assert model.aic is not None
        assert model.bic is not None
        assert model.n_obs == len(sample_data)
        assert model.n_params > 0
        
        # Test coefficients table
        coef_table = model.coefficients
        assert isinstance(coef_table, pd.DataFrame)
        assert 'Estimate' in coef_table.columns
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Invalid formula
        with pytest.raises(ValueError):
            cr.regress("invalid formula", data=pd.DataFrame({'x': [1, 2, 3]}))
        
        # Non-existent variables
        data = pd.DataFrame({'y': [1, 2, 3], 'x': [1, 2, 3]})
        with pytest.raises(ValueError):
            cr.regress("y ~ z", data=data)  # z doesn't exist
        
        # Invalid method
        with pytest.raises(ValueError):
            cr.regress("y ~ x", data=data, method="invalid_method")


class TestTimeSeriesFunctionality:
    """Test time series specific functionality."""
    
    @pytest.fixture
    def ts_data(self):
        """Create time series data for testing."""
        np.random.seed(42)
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        trend = np.linspace(10, 20, 100)
        noise = np.random.normal(0, 1, 100)
        y = trend + noise
        x = np.random.normal(0, 1, 100)
        
        return pd.DataFrame({
            'date': dates,
            'y': y,
            'x': x
        })
    
    def test_temporal_regression(self, ts_data):
        """Test temporal regression functionality."""
        model = cr.regress("y ~ x", data=ts_data, date_col="date")
        
        # Check temporal features were detected
        assert model.date_col == "date"
        assert hasattr(model, 'date_values')
        assert hasattr(model, 'date_range')
        
        # Check predictions work
        predictions = model.predict()
        assert len(predictions) == len(ts_data)
    
    def test_temporal_conformal(self, ts_data):
        """Test temporal conformal prediction."""
        model = cr.regress("y ~ x", data=ts_data, 
                          date_col="date", 
                          uncertainty="conformal_temporal")
        
        assert model.conformal_method == "temporal"
        assert model.temporal_conformal is True
        
        predictions = model.predict()
        assert 'lower_95' in predictions.columns
        assert 'upper_95' in predictions.columns


if __name__ == "__main__":
    # Run tests manually if pytest not available
    import traceback
    
    print("Running basic tests for conformal-regress...")
    
    # Create test data
    np.random.seed(42)
    n = 100
    x1 = np.random.normal(0, 1, n)
    x2 = np.random.normal(0, 1, n)
    y = 2 + 3*x1 + 4*x2 + np.random.normal(0, 1, n)
    sample_data = pd.DataFrame({'y': y, 'x1': x1, 'x2': x2})
    
    try:
        # Test basic regression
        print("Testing basic regression...")
        model = cr.regress("y ~ x1 + x2", data=sample_data)
        assert model.r_squared > 0.5
        print(f"✓ Basic regression: R² = {model.r_squared:.3f}")
        
        # Test predictions
        print("Testing predictions...")
        predictions = model.predict()
        assert len(predictions) == len(sample_data)
        assert 'prediction' in predictions.columns
        assert 'lower_95' in predictions.columns
        print("✓ Predictions with uncertainty bands")
        
        # Test data thinning detection
        print("Testing data thinning detection...")
        assert model.data_thinning_eligible is not None
        print(f"✓ Data thinning eligible: {model.data_thinning_eligible}")
        
        # Test example data
        print("Testing example data...")
        housing = cr.get_example_data("housing")
        assert len(housing) > 0
        print(f"✓ Example data: {len(housing)} housing records")
        
        print("\n✅ All basic tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        traceback.print_exc()