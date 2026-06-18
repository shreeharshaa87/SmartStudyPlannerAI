import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models import db, Subject, Topic, ScheduleItem, UserSettings
from scheduler import generate_timetable, validate_input
from model import predict_completion_probability, load_model
from dataset import load_or_generate_dataset
from datetime import datetime, date, timedelta

app = Flask(__name__)
# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

db.init_app(app)

# Initialize function for model and dataset
def initialize_app():
    """Initialize model, dataset and DB on startup"""
    with app.app_context():
        db.create_all()
        
        # Initialize UserSettings if empty
        if not UserSettings.query.first():
            settings = UserSettings(study_start_time="09:00", hours_per_day=6.0)
            db.session.add(settings)
            db.session.commit()
            
    try:
        load_or_generate_dataset('study_data.csv')
        print("Dataset loaded successfully")
    except Exception as e:
        print(f"Dataset initialization error: {e}")
    
    try:
        load_model()
        print("Model loaded successfully")
    except Exception as e:
        print(f"Model initialization error: {e}")

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/settings', methods=['GET', 'POST'])
def handle_settings():
    settings = UserSettings.query.first()
    if request.method == 'POST':
        data = request.get_json()
        settings.study_start_time = data.get('study_start_time', settings.study_start_time)
        settings.hours_per_day = float(data.get('hours_per_day', settings.hours_per_day))
        
        target_date_str = data.get('target_date')
        if target_date_str:
            settings.target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({
        'study_start_time': settings.study_start_time,
        'hours_per_day': settings.hours_per_day,
        'target_date': settings.target_date.isoformat() if settings.target_date else None
    })

@app.route('/topics', methods=['GET', 'POST'])
def handle_topics():
    if request.method == 'POST':
        data = request.get_json()
        subject_name = data.get('subject')
        topic_name = data.get('topic')
        difficulty = int(data.get('difficulty', 5))
        hours_required = float(data.get('hours_required', 0))

        subject = Subject.query.filter_by(name=subject_name).first()
        if not subject:
            subject = Subject(name=subject_name)
            db.session.add(subject)
            db.session.commit()
        
        new_topic = Topic(
            subject_id=subject.id,
            name=topic_name,
            difficulty=difficulty,
            total_hours_required=hours_required
        )
        db.session.add(new_topic)
        db.session.commit()
        return jsonify({'success': True, 'topic_id': new_topic.id})

    # GET: Return all topics grouped by subject
    subjects = Subject.query.all()
    results = []
    for s in subjects:
        results.append({
            'subject': s.name,
            'topics': [{'id': t.id, 'name': t.name, 'difficulty': t.difficulty, 'hours': t.total_hours_required} for t in s.topics]
        })
    return jsonify(results)

@app.route('/topics/<int:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    subject = topic.subject_ref
    
    db.session.delete(topic)
    db.session.commit()
    
    # Clean up subject if no topics left
    if not subject.topics:
        db.session.delete(subject)
        db.session.commit()
        
    return jsonify({'success': True})

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    try:
        data = request.get_json()
        topics_data = data.get('topics', [])
        settings = UserSettings.query.first()
        
        target_date = datetime.strptime(data.get('target_date'), '%Y-%m-%d').date() if data.get('target_date') else settings.target_date
        
        if not target_date:
            return jsonify({'success': False, 'error': 'Target date is required'}), 400
            
        days_left = (target_date - date.today()).days
        if days_left <= 0:
            return jsonify({'success': False, 'error': 'Target date must be in the future'}), 400

        hours_per_day = settings.hours_per_day
        
        # Calculate total hours and avg difficulty for ML prediction
        total_hours = sum(t.get('hours_required', 0) for t in topics_data)
        avg_difficulty = sum(t.get('difficulty', 5) for t in topics_data) / len(topics_data) if topics_data else 5
        
        probability = predict_completion_probability(total_hours, avg_difficulty, days_left, hours_per_day)
        
        # Generate timetable logic with SRS
        timetable = generate_timetable(topics_data, days_left, hours_per_day, settings.study_start_time)
        
        # Save to database
        ScheduleItem.query.delete()
        for day in timetable:
            day_date = date.today() + timedelta(days=day['day'])
            for sub in day['subjects']:
                # Find or create topic id
                # For simplicity in this demo, we'll assume topics are passed with IDs or we match by name
                topic_record = Topic.query.filter_by(name=sub['topic']).first()
                if topic_record:
                    start_dt = datetime.combine(day_date, datetime.strptime(sub['start_time'], '%H:%M').time())
                    end_dt = datetime.combine(day_date, datetime.strptime(sub['end_time'], '%H:%M').time())
                    
                    item = ScheduleItem(
                        day_number=day['day'],
                        date=day_date,
                        start_time=start_dt,
                        end_time=end_dt,
                        topic_id=topic_record.id,
                        type=sub.get('type', 'learn'),
                        status='pending'
                    )
                    db.session.add(item)
        
        db.session.commit()
        
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

@app.route('/schedule/<int:item_id>/toggle', methods=['PATCH'])
def toggle_item(item_id):
    item = ScheduleItem.query.get_or_404(item_id)
    item.status = 'completed' if item.status == 'pending' else 'pending'
    db.session.commit()
    return jsonify({'success': True, 'status': item.status})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    initialize_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
