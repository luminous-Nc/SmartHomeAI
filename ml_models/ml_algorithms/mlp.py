"""
Multi-Layer Perceptron (MLP) Algorithm - for comfort prediction
Uses scikit-learn MLPClassifier for implementation
"""

import numpy as np
from typing import Dict, Any, List
from ..base_model import BaseComfortModel
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler

class MLPModel(BaseComfortModel):
    """Multi-layer perceptron comfort prediction model using scikit-learn"""
    
    def __init__(self):
        super().__init__("MLP (Neural Network)")
        self.model = MLPClassifier(
            hidden_layer_sizes=(8, 6),  # Two hidden layers with 8 and 6 neurons
            activation='relu',          # ReLU activation function
            solver='adam',              # Adam optimizer
            learning_rate_init=0.01,    # Learning rate
            max_iter=500,               # Maximum iterations (increased to reduce convergence warnings)
            random_state=42             # For reproducible results
        )
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()  # For input normalization
        self.feature_names = ['temperature', 'humidity']
    
    def predict(self, temperature: float, humidity: float) -> str:
        """
        Use scikit-learn MLPClassifier to predict comfort level
        
        Forward propagation to get probabilities for each class, choose the class with highest probability
        """
        if not self.is_trained:
            # If not trained, use base prediction
            raise ValueError("Model must be trained before making predictions")
        
        # Prepare and normalize input features
        features = np.array([[temperature, humidity]])
        features_scaled = self.scaler.transform(features)
        
        # Predict using trained model
        prediction_encoded = self.model.predict(features_scaled)[0]
        prediction = self.label_encoder.inverse_transform([prediction_encoded])[0]
        
        return prediction
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train MLP model using scikit-learn
        
        Uses backpropagation algorithm implemented in scikit-learn
        """
        if X.size == 0 or y.size == 0:
            raise ValueError("No training data provided")
        
        # Encode labels
        self.label_encoder.fit(['cold', 'comfortable', 'hot'])
        y_encoded = self.label_encoder.transform(y)
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train the model
        self.model.fit(X_scaled, y_encoded)
        self.is_trained = True 