"""
Training and Evaluation Script for Our Custom Model
Automatically trains and evaluates our custom model on all three person types
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import sys
import os
import time
import argparse

# Add project root to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

# Import all available models
from ml_models.our_model import OurModel
from ml_models.ml_algorithms.linear_regression import LinearRegressionModel
from ml_models.ml_algorithms.random_forest import RandomForestModel
from ml_models.ml_algorithms.bayes_theorem import BayesTheoremModel
from ml_models.ml_algorithms.mlp import MLPModel

# Model mapping
MODEL_CLASSES = {
    "our_model": OurModel,
    "linear": LinearRegressionModel,
    "bayes": BayesTheoremModel,
    "forest": RandomForestModel,
    "mlp": MLPModel
}

def load_person_data(data_dir: Path, person_type: str):
    """Load data for a specific person type"""
    person_data_files = {
        "normal_person": "normal_person_data.csv",
        "hot_person": "hot_person_data.csv", 
        "cold_person": "cold_person_data.csv"
    }
    
    if person_type not in person_data_files:
        raise ValueError(f"Unknown person type: {person_type}")
    
    data_file = data_dir / person_data_files[person_type]
    
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_file}")
    
    # Read CSV data
    df = pd.read_csv(data_file)
    
    # Separate features and labels
    X = df[['temperature', 'humidity']].values
    y = df['comfort_label'].values
    
    return X, y

def print_model_parameters(model, algorithm_type: str, X_train, y_train):
    """Print algorithm-specific parameters after training"""
    print(f"Algorithm Parameters ({algorithm_type}):")
    
    if algorithm_type == "linear":
        # Linear Regression parameters
        if hasattr(model, 'model') and hasattr(model.model, 'coef_'):
            coefficients = dict(zip(['temperature', 'humidity'], model.model.coef_))
            print(f"  Coefficients: {coefficients}")
            print(f"  Intercept: {model.model.intercept_:.3f}")
            
            # Calculate R² score if possible
            if hasattr(model, 'label_encoder'):
                y_encoded = model.label_encoder.transform(y_train)
                r2_score = model.model.score(X_train, y_encoded)
                print(f"  R² Score: {r2_score:.3f}")
        else:
            print("  Linear regression parameters not available")
        
    elif algorithm_type == "bayes":
        # Bayes parameters
        if hasattr(model, 'model') and hasattr(model.model, 'class_prior_'):
            print("  Class prior probabilities:")
            if hasattr(model, 'label_encoder'):
                class_priors = dict(zip(
                    model.label_encoder.inverse_transform(range(len(model.model.class_prior_))),
                    model.model.class_prior_
                ))
                for class_name, prior in class_priors.items():
                    print(f"    {class_name}: {prior:.3f}")
            else:
                print("    Prior probabilities available but label encoder not found")
        else:
            print("  Bayes parameters not available")
            
    elif algorithm_type == "forest":
        # Random Forest parameters
        if hasattr(model, 'model') and hasattr(model.model, 'feature_importances_'):
            feature_importance = dict(zip(['temperature', 'humidity'], model.model.feature_importances_))
            print(f"  Number of trees: {getattr(model.model, 'n_estimators', 'Unknown')}")
            print(f"  Feature importance: {feature_importance}")
            print(f"  Max depth: {getattr(model.model, 'max_depth', 'Unknown')}")
        else:
            print("  Random forest parameters not available")
        
    elif algorithm_type == "mlp":
        # MLP parameters
        if hasattr(model, 'model') and hasattr(model.model, 'hidden_layer_sizes'):
            print(f"  Network architecture: Input(2) -> Hidden{model.model.hidden_layer_sizes} -> Output(3)")
            print(f"  Learning rate: {getattr(model.model, 'learning_rate_init', 'Unknown')}")
            print(f"  Iterations completed: {getattr(model.model, 'n_iter_', 'Unknown')}")
            
            # Calculate training accuracy if possible
            if hasattr(model, 'scaler') and hasattr(model, 'label_encoder'):
                X_scaled = model.scaler.transform(X_train)
                y_encoded = model.label_encoder.transform(y_train)
                training_accuracy = model.model.score(X_scaled, y_encoded)
                print(f"  Training accuracy: {training_accuracy:.3f}")
        else:
            print("  MLP parameters not available")
    
    elif algorithm_type == "our_model":
        # Our custom algorithm parameters
        print(f"  Custom algorithm logic: Temperature thresholds")
        print(f"  Hot threshold: > 76.6°F")
        print(f"  Cold threshold: < 76.4°F")
        print(f"  Comfortable range: 76.4°F - 76.6°F")

def evaluate_model_on_dataset(X_train, X_test, y_train, y_test, person_type: str, algorithm_type: str = "our_model"):
    """Train and evaluate our model on a specific dataset"""
    print(f"\n{'='*50}")
    print(f"Training and Evaluating: {person_type.upper()}")
    print(f"{'='*50}")
    
    # Create and train our model
    model = MODEL_CLASSES[algorithm_type]()
    
    print(f"Training set size: {len(X_train)} samples")
    print(f"Test set size: {len(X_test)} samples")
    print(f"Algorithm type: {algorithm_type}")
    print("-" * 30)
    
    # Measure training time
    start_time = time.time()
    model.train(X_train, y_train)
    training_time = time.time() - start_time
    
    print(f"Training completed in {training_time:.4f} seconds")
    
    # Print model-specific parameters
    print_model_parameters(model, algorithm_type, X_train, y_train)
    
    print("-" * 30)
    
    # Make predictions on test set
    y_pred = []
    for i in range(len(X_test)):
        # All algorithms use the same temperature unit (Fahrenheit from CSV)
        temperature = X_test[i][0]
        humidity = X_test[i][1]
        prediction = model.predict(temperature, humidity)
        y_pred.append(prediction)
    
    y_pred = np.array(y_pred)
    
    # Calculate simple metrics
    correct = sum(y_test == y_pred)
    incorrect = len(y_test) - correct
    accuracy = correct / len(y_test)
    
    print("Evaluation Results:")
    print(f"  Correct predictions: {correct}")
    print(f"  Incorrect predictions: {incorrect}")
    print(f"  Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")
    
    return accuracy

def main():
    """Main training and evaluation function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Train and evaluate our custom model on comfort prediction data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available algorithm types:
  our_model  - Our custom algorithm (temperature threshold based)
  linear     - Linear Regression algorithm
  bayes      - Bayes' Theorem algorithm  
  forest     - Random Forest algorithm
  mlp        - Multi-Layer Perceptron algorithm

Example usage:
  python train.py our_model
  python train.py linear
  python train.py bayes
  python train.py forest
        """
    )
    parser.add_argument(
        'algorithm_type', 
        choices=["our_model", "linear", "bayes", "forest", "mlp"],
        help='Algorithm type to train and evaluate'
    )
    
    args = parser.parse_args()
    algorithm_type = args.algorithm_type
    
    print(f"🤖 {MODEL_CLASSES[algorithm_type]().model_name} Training and Evaluation")
    print(f"Algorithm Type: {algorithm_type.upper()}")
    print("=" * 60)
    
    # Set up data directory (ml_data is at same level as ml_models)
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "ml_data"
    
    # Person types to evaluate
    person_types = ["normal_person", "hot_person", "cold_person"]
    
    # Store results
    results = {}
    
    # Train and evaluate each person type
    for person_type in person_types:
        try:
            # Load data
            X, y = load_person_data(data_dir, person_type)
            
            # Split into train/test sets (80/20 split)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, 
                test_size=0.2, 
                random_state=42, 
                stratify=y  # Ensure balanced splits across classes
            )
            
            # Train and evaluate using specified model type
            accuracy = evaluate_model_on_dataset(X_train, X_test, y_train, y_test, person_type, algorithm_type)
            results[person_type] = accuracy
            
        except Exception as e:
            print(f"\n❌ Error processing {person_type}: {e}")
            results[person_type] = 0.0
    
    # Print summary results
    print(f"\n{'='*60}")
    print("📊 SUMMARY RESULTS")
    print(f"{'='*60}")
    
    for person_type, accuracy in results.items():
        status = "✅" if accuracy > 0 else "❌"
        print(f"{status} {person_type.replace('_', ' ').title():>15}: {accuracy:.3f} ({accuracy*100:.1f}%)")
    
    # Calculate and print average accuracy
    valid_accuracies = [acc for acc in results.values() if acc > 0]
    if valid_accuracies:
        avg_accuracy = sum(valid_accuracies) / len(valid_accuracies)
        print(f"\n🎯 Average Accuracy: {avg_accuracy:.3f} ({avg_accuracy*100:.1f}%)")
    
    print(f"\n{'='*60}")
    print("Training and evaluation completed!")

if __name__ == "__main__":
    main() 