"""
Linear Regression Algorithm - for comfort prediction
Uses scikit-learn LinearRegression for implementation
"""

import numpy as np
from typing import Dict, Any, List
from ..base_model import BaseComfortModel
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

class LinearRegressionModel(BaseComfortModel):
    """Linear regression comfort prediction model using scikit-learn"""
    
    def __init__(self):
        super().__init__("Linear Regression")
        self.model = LinearRegression()
        self.label_encoder = LabelEncoder()
        self.feature_names = ['temperature', 'humidity']
    
    def predict(self, temperature: float, humidity: float, user_preferences: Dict = None) -> str:
        """Use scikit-learn LinearRegression for prediction"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Prepare input features
        features = np.array([[temperature, humidity]])
        
        # Predict using trained model
        prediction_encoded = self.model.predict(features)[0]
        
        # Convert prediction to nearest class
        prediction_rounded = int(round(prediction_encoded))
        prediction_rounded = max(0, min(2, prediction_rounded))  # Clamp to valid range
        
        # Decode prediction
        prediction = self.label_encoder.inverse_transform([prediction_rounded])[0]
        
        return prediction
    
    def train(self, training_data: List[Dict[str, Any]]):
        """Train linear regression model using scikit-learn"""
        if not training_data:
            raise ValueError("No training data provided")
        
        print(f"Training Linear Regression model with {len(training_data)} data points")
        
        # Prepare training data
        X = []
        y = []
        
        for data in training_data:
            X.append([data['temperature'], data['humidity']])
            y.append(data.get('comfort_label', 'comfortable'))
        
        X = np.array(X)
        
        # Encode labels to numbers
        self.label_encoder.fit(['cold', 'comfortable', 'hot'])
        y_encoded = self.label_encoder.transform(y)
        
        # Train the model
        self.model.fit(X, y_encoded)
        self.is_trained = True
        
        # Get model coefficients
        coefficients = dict(zip(self.feature_names, self.model.coef_))
        
        print(f"Linear Regression model training completed.")
        print(f"Coefficients: {coefficients}")
        print(f"Intercept: {self.model.intercept_:.3f}")
        print(f"R² Score: {self.model.score(X, y_encoded):.3f}")
    
    