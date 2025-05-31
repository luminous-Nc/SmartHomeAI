import os
import pandas as pd
import numpy as np
from pathlib import Path
import threading
import time

from .ml_algorithms.linear_regression import LinearRegressionModel
from .ml_algorithms.random_forest import RandomForestModel  
from .ml_algorithms.bayes_theorem import BayesTheoremModel
from .ml_algorithms.mlp import MLPModel
from .our_model import OurModel

class ModelManager:
    def __init__(self):
        # Data path - calculate relative path from current file location to project root ml_data
        current_file = Path(__file__)
        project_root = current_file.parent.parent  # Go back to root directory from ml_models/
        self.data_dir = project_root / "ml_data"
        
        # Person type to filename mapping
        self.person_data_files = {
            "Normal Person": "normal_person_data.csv",
            "Hot Person": "hot_person_data.csv",
            "Cold Person": "cold_person_data.csv"
        }
        
        # Currently active person type and models
        self.current_person_type = "Normal Person"
        self.models = {}
        
        # Model class mapping
        self.model_classes = {
            'linear_regression': LinearRegressionModel,
            'random_forest': RandomForestModel,
            'bayes_theorem': BayesTheoremModel,
            'mlp': MLPModel,
            'our_model': OurModel
        }
        
        # Training status
        self.is_training = False
        self.training_progress = {}
        
        # Callback functions
        self.on_training_complete = None
        self.on_training_progress = None
        
    def set_callbacks(self, training_complete_callback=None, training_progress_callback=None):
        """Set training callback functions"""
        self.on_training_complete = training_complete_callback
        self.on_training_progress = training_progress_callback
        
    def load_person_data(self, person_type: str):
        """Load training data for specified person type"""
        if person_type not in self.person_data_files:
            raise ValueError(f"Unknown person type: {person_type}")
            
        data_file = self.data_dir / self.person_data_files[person_type]
        
        if not data_file.exists():
            raise FileNotFoundError(f"Data file not found: {data_file}")
            
        # Read CSV data
        df = pd.read_csv(data_file)
        
        # Separate features and labels
        X = df[['temperature', 'humidity']].values
        y = df['comfort_label'].values
        
        return X, y
    
    def switch_person_type(self, new_person_type: str):
        """Switch person type and retrain all models"""
        if new_person_type == self.current_person_type:
            return  # If it's the same type, no need to retrain
            
        if new_person_type not in self.person_data_files:
            raise ValueError(f"Unknown person type: {new_person_type}")
            
        self.current_person_type = new_person_type
        
        # Retrain models in background thread
        training_thread = threading.Thread(
            target=self._train_models_for_person_type,
            args=(new_person_type,),
            daemon=True
        )
        training_thread.start()
    
    def _train_models_for_person_type(self, person_type: str):
        """Train all models for specified person type"""
        self.is_training = True
        self.training_progress = {}
        
        try:
            # Load data
            if self.on_training_progress:
                try:
                    self.on_training_progress(f"Loading {person_type} data...")
                except Exception as callback_error:
                    print(f"Training progress callback error: {callback_error}")
                
            X, y = self.load_person_data(person_type)
            
            # Train each model
            trained_models = {}
            total_models = len(self.model_classes)
            
            for i, (model_name, model_class) in enumerate(self.model_classes.items()):
                if self.on_training_progress:
                    try:
                        self.on_training_progress(f"Training {model_name} for {person_type}... ({i+1}/{total_models})")
                    except Exception as callback_error:
                        # If callback fails (usually due to threading), continue training
                        print(f"Training progress callback error: {callback_error}")
                
                try:
                    # Create and train model
                    model = model_class()
                    
                    # Train model directly with X, y arrays
                    model.train(X, y)
                    trained_models[model_name] = model
                    
                    self.training_progress[model_name] = "✓ Complete"
                    
                except Exception as e:
                    print(f"Error training {model_name}: {e}")
                    self.training_progress[model_name] = f"✗ Error: {str(e)}"
            
            # Update model dictionary
            self.models = trained_models
            
            if self.on_training_progress:
                try:
                    self.on_training_progress(f"Training complete for {person_type}!")
                except Exception as callback_error:
                    print(f"Training progress callback error: {callback_error}")
                
            if self.on_training_complete:
                try:
                    self.on_training_complete(person_type, len(trained_models))
                except Exception as callback_error:
                    print(f"Training complete callback error: {callback_error}")
                
        except Exception as e:
            print(f"Error during model training: {e}")
            if self.on_training_progress:
                try:
                    self.on_training_progress(f"Training failed: {str(e)}")
                except Exception as callback_error:
                    print(f"Training progress callback error: {callback_error}")
        finally:
            self.is_training = False
    
    def predict(self, temperature: float, humidity: float):
        """Use currently trained models to make predictions"""
        if not self.models:
            return {
                'linear_regression': 'N/A',
                'random_forest': 'N/A', 
                'bayes_theorem': 'N/A',
                'mlp': 'N/A',
                'our_model': 'N/A'
            }
            
        predictions = {}
        
        for model_name, model in self.models.items():
            try:
                prediction = model.predict(temperature, humidity)
                predictions[model_name] = prediction
            except Exception as e:
                print(f"Error predicting with {model_name}: {e}")
                predictions[model_name] = 'Error'
                
        return predictions
    
    def get_voting_decision(self, predictions: dict):
        """Make voting decision based on all model predictions"""
        if not predictions or all(pred in ['N/A', 'Error'] for pred in predictions.values()):
            return 'N/A'
            
        # Count valid predictions
        valid_predictions = [pred for pred in predictions.values() if pred not in ['N/A', 'Error']]
        
        if not valid_predictions:
            return 'N/A'
            
        # Simple majority voting
        from collections import Counter
        vote_counts = Counter(valid_predictions)
        
        # Return prediction with most votes
        most_common = vote_counts.most_common(1)
        if most_common:
            return most_common[0][0]
        else:
            return 'N/A'
    
    def get_current_person_type(self):
        """Get current person type"""
        return self.current_person_type
    
    def is_model_ready(self):
        """Check if models are ready"""
        return bool(self.models) and not self.is_training
    
    def get_training_status(self):
        """Get training status"""
        return {
            'is_training': self.is_training,
            'current_person_type': self.current_person_type,
            'progress': self.training_progress.copy(),
            'models_ready': len(self.models)
        }
    
    def initialize_default_models(self):
        """Initialize default models (Normal Person)"""
        # Train default person type directly, avoid same type check in switch_person_type
        training_thread = threading.Thread(
            target=self._train_models_for_person_type,
            args=(self.current_person_type,),
            daemon=True
        )
        training_thread.start()
    
    def get_our_model_prediction(self, temperature: float, humidity: float):
        """Get prediction from our custom model"""
        if 'our_model' not in self.models:
            return 'N/A'
            
        try:
            return self.models['our_model'].predict(temperature, humidity)
        except Exception as e:
            print(f"Error predicting with our_model: {e}")
            return 'Error' 