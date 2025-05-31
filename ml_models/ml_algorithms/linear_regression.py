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
    
    def predict(self, temperature: float, humidity: float) -> str:
        """Use scikit-learn LinearRegression for prediction"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Prepare input features
        features = np.array([[temperature, humidity]])
        
        # Predict using trained model
        prediction_encoded = self.model.predict(features)[0]
        
        # Convert prediction to nearest class
        prediction_rounded = int(round(prediction_encoded))
        
        # Ensure prediction is within valid range
        prediction_rounded = max(0, min(2, prediction_rounded))  # Clamp to valid range
        
        # Decode prediction
        prediction = self.label_encoder.inverse_transform([prediction_rounded])[0]
        
        return prediction
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train linear regression model using scikit-learn"""
        
        # Encode labels to numbers
        self.label_encoder.fit(['cold', 'comfortable', 'hot'])
        y_encoded = self.label_encoder.transform(y)
        
        # Train the model
        self.model.fit(X, y_encoded)
        self.is_trained = True
    
   