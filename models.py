from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    topics = db.relationship('Topic', backref='subject_ref', lazy=True, cascade="all, delete-orphan")

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.Integer, default=5) # 1-10
    total_hours_required = db.Column(db.Float, nullable=False)
    hours_completed = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending') # pending, in_progress, completed

class ScheduleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False) # learn, revise, practice
    status = db.Column(db.String(20), default='pending') # pending, completed, missed
    
    topic = db.relationship('Topic', backref=db.backref('schedule_items', cascade="all, delete-orphan"))

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    study_start_time = db.Column(db.String(5), default="09:00") # HH:MM
    hours_per_day = db.Column(db.Float, default=6.0)
    target_date = db.Column(db.Date, nullable=True)
