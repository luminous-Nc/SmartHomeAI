"""
Random Forest Algorithm - for comfort prediction
Uses scikit-learn RandomForestClassifier for implementation
"""

import numpy as np
from typing import Dict, Any, List
from ..base_model import BaseComfortModel
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

class RandomForestModel(BaseComfortModel):
    """Random forest comfort prediction model using scikit-learn"""
    
    def __init__(self):
        super().__init__("Random Forest")
        self.model = RandomForestClassifier(
            n_estimators=10,  # Number of trees
            random_state=42,  # For reproducible results
            max_depth=5,      # Prevent overfitting
        )
        self.label_encoder = LabelEncoder()
        self.feature_names = ['temperature', 'humidity']
    
    def predict(self, temperature: float, humidity: float) -> str:
        """Use scikit-learn RandomForestClassifier for prediction"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Prepare input features
        features = np.array([[temperature, humidity]])
        
        # Predict using trained model
        prediction_encoded = self.model.predict(features)[0]
        prediction = self.label_encoder.inverse_transform([prediction_encoded])[0]
        
        return prediction
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train random forest model using scikit-learn"""
        if X.size == 0 or y.size == 0:
            raise ValueError("No training data provided")
        
        # Encode labels
        self.label_encoder.fit(['cold', 'comfortable', 'hot'])
        y_encoded = self.label_encoder.transform(y)
        
        # Train the model
        self.model.fit(X, y_encoded)
        self.is_trained = True