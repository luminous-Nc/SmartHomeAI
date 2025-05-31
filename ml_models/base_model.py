"""
Base Model Class - Defines unified interface for all machine learning algorithms
"""

from abc import ABC, abstractmethod
import numpy as np

class BaseComfortModel(ABC):
    """Base class for comfort prediction models"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.is_trained = False
    
    @abstractmethod
    def predict(self, temperature: float, humidity: float) -> str:
        """
        Predict comfort level
        
        Args:
            temperature: Current temperature (°C)
            humidity: Current humidity (%)
        
        Returns:
            str: "hot", "comfortable", or "cold"
        """
        pass
    
    @abstractmethod 
    def train(self, X: np.ndarray, y: np.ndarray):
        """
        Train model
        
        Args:
            X: Feature matrix of shape (n_samples, 2) containing [temperature, humidity]
            y: Target labels of shape (n_samples,) containing comfort labels
        """
        pass
    
    