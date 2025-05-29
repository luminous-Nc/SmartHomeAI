"""
Base Model Class - Defines unified interface for all machine learning algorithms
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseComfortModel(ABC):
    """Base class for comfort prediction models"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.is_trained = False
    
    @abstractmethod
    def predict(self, temperature: float, humidity: float, user_preferences: Optional[Dict] = None) -> str:
        """
        Predict comfort level
        
        Args:
            temperature: Current temperature (°C)
            humidity: Current humidity (%)
            user_preferences: User preference data (optional)
        
        Returns:
            str: "hot", "comfortable", or "cold"
        """
        pass
    
    @abstractmethod 
    def train(self, training_data: List[Dict[str, Any]]):
        """
        Train model
        
        Args:
            training_data: Training data list, each element contains temperature, humidity, comfort_label
        """
        pass
    
    