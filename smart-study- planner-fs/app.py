from flask import Flask, render_template, request, jsonify
import os
from scheduler import generate_timetable, validate_input
from model import predict_completion_probability, load_model
from dataset import load_or_generate_dataset

app = Flask(__name__)

# Initialize function for model and dataset
def initialize_app():
    """Initialize model and dataset on startup"""
    try:
        # Try to load/generate dataset
        load_or_generate_dataset('study_data.csv')
        print("Dataset loaded successfully")
    except Exception as e:
        print(f"Dataset initialization error: {e}")
    
    try:
        # Try to load/train model
        load_model()
        print("Model loaded successfully")
    except Exception as e:
        print(f"Model initialization error: {e}")

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    """
    Generate study plan based on user input.
    
    Expected POST data:
    - topics: List of topic objects with subject, topic, difficulty, hours_required
    - days_left: Number of days until exam
    - hours_per_day: Hours available per day
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        topics = data.get('topics', [])
        days_left = data.get('days_left', 1)
        hours_per_day = data.get('hours_per_day', 1)
        
        # Validate inputs
        if not topics:
            return jsonify({'success': False, 'error': 'No topics provided'}), 400
        
        try:
            days_left = int(days_left)
            hours_per_day = float(hours_per_day)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Invalid days_left or hours_per_day'}), 400
        
        if days_left <= 0 or hours_per_day <= 0:
            return jsonify({'success': False, 'error': 'Days and hours must be positive'}), 400
        
        # Calculate total hours and average difficulty
        total_hours = sum(topic.get('hours_required', 0) for topic in topics)
        avg_difficulty = sum(topic.get('difficulty', 5) for topic in topics) / len(topics) if topics else 5
        
        # Get completion probability
        try:
            probability = predict_completion_probability(
                total_hours, 
                avg_difficulty, 
                days_left, 
                hours_per_day
            )
        except Exception as e:
            print(f"Prediction error: {e}")
            probability = 50.0  # Default fallback
        
        # Generate timetable
        try:
            timetable = generate_timetable(topics, days_left, hours_per_day)
        except Exception as e:
            print(f"Scheduler error: {e}")
            return jsonify({'success': False, 'error': 'Failed to generate timetable'}), 500
        
        return jsonify({
            'success': True,
            'timetable': timetable,
            'probability': probability,
            'total_hours': total_hours,
            'avg_difficulty': round(avg_difficulty, 1)
        })
    
    except Exception as e:
        print(f"Error in generate-plan: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/add-topic', methods=['POST'])
def add_topic():
    """
    Validate a single topic and return validation result.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        subject = data.get('subject', '')
        topic = data.get('topic', '')
        difficulty = data.get('difficulty', 5)
        hours_required = data.get('hours_required', 1)
        days_left = data.get('days_left', 1)
        hours_per_day = data.get('hours_per_day', 1)
        
        # Validate
        error = validate_input(subject, topic, difficulty, hours_required, days_left, hours_per_day)
        
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        return jsonify({
            'success': True,
            'valid': True,
            'topic': {
                'subject': subject,
                'topic': topic,
                'difficulty': int(difficulty),
                'hours_required': float(hours_required)
            }
        })
    
    except Exception as e:
        print(f"Error in add-topic: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # Initialize on startup
    try:
        load_or_generate_dataset('study_data.csv')
        load_model()
    except Exception as e:
        print(f"Initialization warning: {e}")
    
    # Run app
    app.run(debug=True, host='0.0.0.0', port=5000)
