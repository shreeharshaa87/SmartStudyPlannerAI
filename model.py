import os
import joblib
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from dataset import load_or_generate_dataset

def train_model():
    """
    Train the ML model for predicting study completion probability.
    Returns: model, scaler
    """
    # Load dataset
    df = load_or_generate_dataset('study_data.csv')
    
    # Features and target
    X = df[['total_hours', 'avg_difficulty', 'days_left', 'hours_per_day']]
    y = df['completed']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train_scaled, y_train)
    
    # Print accuracy
    train_accuracy = model.score(X_train_scaled, y_train)
    test_accuracy = model.score(X_test_scaled, y_test)
    print(f"Model trained - Train Accuracy: {train_accuracy:.2f}, Test Accuracy: {test_accuracy:.2f}")
    
    return model, scaler

def load_model():
    """
    Load model from file or train new one if not exists.
    Returns: model, scaler
    """
    model_path = 'model.pkl'
    scaler_path = 'scaler.pkl'
    
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        try:
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            print("Model loaded from file")
            return model, scaler
        except Exception as e:
            print(f"Error loading model: {e}, training new one...")
    
    # Train new model
    model, scaler = train_model()
    
    # Save model
    try:
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        print(f"Model saved to {model_path}")
    except Exception as e:
        print(f"Error saving model: {e}")
    
    return model, scaler

def predict_completion_probability(total_hours, avg_difficulty, days_left, hours_per_day):
    """
    Predict probability of syllabus completion.
    
    Args:
        total_hours: Total study hours required
        avg_difficulty: Average difficulty level (1-10)
        days_left: Number of days until exam
        hours_per_day: Hours allocated per day
    
    Returns:
        probability: Probability of completion (0-100)
    """
    try:
        # Load or train model
        model, scaler = load_model()
        
        # Prepare features
        features = np.array([[total_hours, avg_difficulty, days_left, hours_per_day]])
        features_scaled = scaler.transform(features)
        
        # Get probability
        probability = model.predict_proba(features_scaled)[0][1]
        
        # Convert to percentage (0-100)
        probability_percent = probability * 100
        
        return round(probability_percent, 2)
    
    except Exception as e:
        print(f"Error in prediction: {e}")
        # Return a default probability based on simple heuristic
        workload = (total_hours * avg_difficulty) / (days_left * hours_per_day)
        if workload < 5:
            return 85.0
        elif workload < 10:
            return 65.0
        elif workload < 15:
            return 45.0
        else:
            return 25.0

if __name__ == "__main__":
    # Test the model
    prob = predict_completion_probability(50, 5, 10, 5)
    print(f"Completion probability: {prob}%")
