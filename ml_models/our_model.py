"""
Our Model - Our own comfort prediction model
"""

from .base_model import BaseComfortModel
import numpy as np

class OurModel(BaseComfortModel):
    """Our custom comfort prediction model"""
    
    def __init__(self):
        super().__init__("our_model")
    
    def predict(self, temperature: float, humidity: float) -> str:
        """
        Predict comfort level using our custom algorithm
        
        Args:
            temperature: Current temperature (°F)
            humidity: Current humidity (%)
            user_preferences: User preference data (optional)
        
        Returns:
            str: "hot", "comfortable", or "cold"
        """
        # TODO: Implement our custom prediction logic here
       
        return "comfortable"
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """
        Train our custom model
        
        Args:
            X: Feature matrix of shape (n_samples, 2) containing [temperature, humidity]
            y: Target labels of shape (n_samples,) containing comfort labels
        """
        # TODO: Implement our custom training logic here
        
        self.is_trained = True 