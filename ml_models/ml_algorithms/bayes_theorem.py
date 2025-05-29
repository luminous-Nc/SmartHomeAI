"""
Bayes' Theorem Algorithm - for comfort prediction
Uses scikit-learn GaussianNB for implementation
"""

import numpy as np
from typing import Dict, Any, List
from ..base_model import BaseComfortModel
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder

class BayesTheoremModel(BaseComfortModel):
    """Bayes' theorem comfort prediction model using scikit-learn"""
    
    def __init__(self):
        super().__init__("Bayes' Theorem")
        self.model = GaussianNB()
        self.label_encoder = LabelEncoder()
        self.feature_names = ['temperature', 'humidity']
    
    def predict(self, temperature: float, humidity: float, user_preferences: Dict[str, Any] = None) -> str:
        """
        Use scikit-learn GaussianNB to predict comfort level
        
        Calculate posterior probability for each class, choose the one with maximum probability
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Prepare input features
        features = np.array([[temperature, humidity]])
        
        # Predict using trained model
        prediction_encoded = self.model.predict(features)[0]
        prediction = self.label_encoder.inverse_transform([prediction_encoded])[0]
        
        return prediction
    
    def train(self, training_data: List[Dict[str, Any]]):
        """
        Train Bayes model using scikit-learn
        
        Estimate prior probabilities and feature distribution parameters from training data
        """
        if not training_data:
            raise ValueError("No training data provided")
        
        print(f"Training Bayes' Theorem model with {len(training_data)} data points")
        
        # Prepare training data
        X = []
        y = []
        
        for data in training_data:
            X.append([data['temperature'], data['humidity']])
            y.append(data.get('comfort_label', 'comfortable'))
        
        X = np.array(X)
        
        # Encode labels
        self.label_encoder.fit(['cold', 'comfortable', 'hot'])
        y_encoded = self.label_encoder.transform(y)
        
        # Train the model
        self.model.fit(X, y_encoded)
        self.is_trained = True
        
        print(f"Bayes' Theorem model training completed.")
        print("Class prior probabilities:")
        
        # Get class priors
        class_priors = dict(zip(
            self.label_encoder.inverse_transform(range(len(self.model.class_prior_))),
            self.model.class_prior_
        ))
        
        for class_name, prior in class_priors.items():
            print(f"  {class_name}: {prior:.3f}")
        
        print("Feature distribution parameters updated")
        print(f"Training accuracy: {self.model.score(X, y_encoded):.3f}") 