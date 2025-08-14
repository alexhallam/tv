#!/usr/bin/env python3
"""
Simple example demonstrating conformal-regress package usage.
"""

import pandas as pd
import numpy as np
import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'conformal_regress'))

try:
    import conformal_regress as cr
except ImportError as e:
    print(f"Error importing conformal_regress: {e}")
    print("Make sure you're in the correct directory and the package is installed.")
    sys.exit(1)

def main():
    """Run a simple example."""
    print("🚀 Conformal Regress Example")
    print("="*40)
    
    # Create sample data
    print("Creating sample data...")
    np.random.seed(42)
    n = 100
    
    # Generate features
    price = np.random.uniform(10, 50, n)
    advertising = np.random.uniform(1, 20, n)
    
    # Generate target with some noise
    sales = 100 - 0.5 * price + 2.0 * advertising + np.random.normal(0, 5, n)
    
    # Create DataFrame
    df = pd.DataFrame({
        'sales': sales,
        'price': price,
        'advertising': advertising
    })
    
    print(f"Dataset created with {len(df)} observations")
    print(f"Columns: {list(df.columns)}")
    print(f"Sales range: {df['sales'].min():.1f} to {df['sales'].max():.1f}")
    
    # Fit model
    print("\nFitting regression model...")
    model = cr.regress("sales ~ price + advertising", data=df)
    
    # Display model summary
    print("\nModel Summary:")
    print(model)
    
    # Make predictions
    print("\nMaking predictions...")
    new_data = pd.DataFrame({
        'price': [20, 30, 40],
        'advertising': [10, 15, 5]
    })
    
    predictions = model.predict(new_data)
    print("\nPredictions with uncertainty intervals:")
    print(predictions)
    
    # Display using the view function
    print("\nFormatted predictions:")
    try:
        cr.view(predictions)
    except Exception as e:
        print(f"Note: tidy-viewer-py not available, using standard display: {e}")
        print(predictions.to_string())
    
    # Show model properties
    print(f"\nModel Properties:")
    print(f"Formula: {model.formula}")
    print(f"Method: {model.method}")
    print(f"Coverage: {model.coverage}")
    
    print("\n✅ Example completed successfully!")

if __name__ == "__main__":
    main()