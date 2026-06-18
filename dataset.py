import pandas as pd
import numpy as np
import os

def generate_dataset():
    """
    Generate synthetic dataset for training the ML model.
    Features:
    - total_hours: total study hours required
    - avg_difficulty: average difficulty level (1-10)
    - days_left: number of days until exam
    - hours_per_day: hours allocated per day
    
    Target:
    - completed: 1 if completed, 0 if not completed
    """
    np.random.seed(42)
    n_samples = 500
    
    # Generate random features
    total_hours = np.random.randint(10, 200, n_samples)
    avg_difficulty = np.random.randint(1, 11, n_samples)
    days_left = np.random.randint(1, 60, n_samples)
    hours_per_day = np.random.randint(1, 12, n_samples)
    
    # Calculate realistic completion probability
    # More hours needed with higher difficulty, less time available = lower completion
    workload_ratio = (total_hours * avg_difficulty) / (days_left * hours_per_day)
    
    # Add some noise and create target
    completion_score = np.random.random(n_samples)
    completed = ((workload_ratio < 8) & (completion_score > 0.3)).astype(int)
    
    # Create DataFrame
    df = pd.DataFrame({
        'total_hours': total_hours,
        'avg_difficulty': avg_difficulty,
        'days_left': days_left,
        'hours_per_day': hours_per_day,
        'completed': completed
    })
    
    return df

def load_or_generate_dataset(filepath='study_data.csv'):
    """
    Load dataset from file or generate if not exists.
    """
    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath)
            return df
        except Exception as e:
            print(f"Error loading dataset: {e}, generating new one...")
    
    # Generate new dataset
    df = generate_dataset()
    
    try:
        df.to_csv(filepath, index=False)
        print(f"Dataset saved to {filepath}")
    except Exception as e:
        print(f"Error saving dataset: {e}")
    
    return df

if __name__ == "__main__":
    df = load_or_generate_dataset()
    print(f"Dataset shape: {df.shape}")
    print(df.head())
