from datetime import datetime, timedelta

def calculate_priority(difficulty, hours_required, days_left):
    """Priority score: (difficulty × hours) / max(1, days_left)"""
    return (difficulty * hours_required) / max(1, days_left)

def generate_timetable(topics, days_left, hours_per_day, start_time_str="09:00"):
    """
    Generate a detailed timetable with specific timings, SRS, and Practice sessions.
    
    Logic:
    1. Learn: New content.
    2. Revise: 1, 3, 7 days after 'Learn'.
    3. Practice: Dedicated sessions for high-difficulty topics.
    """
    if not topics:
        return []

    # Prepare topics
    for t in topics:
        t['remaining'] = float(t.get('hours_required', 0))
        t['learned_days'] = [] # Track when we 'learned' this to trigger SRS

    timetable = []
    
    # Configuration
    SESSION_LENGTH = 1.5 # 90 min sessions
    BREAK_LENGTH = 0.25  # 15 min break
    
    for day in range(1, days_left + 1):
        day_plan = {
            'day': day,
            'subjects': [],
            'total_hours': 0.0
        }
        
        current_time = datetime.strptime(start_time_str, '%H:%M')
        hours_used = 0.0
        
        # 1. Revision Slots (Priority: High - SRS)
        for t in topics:
            for learned_day in t['learned_days']:
                # SRS intervals: +1, +3, +7
                if day in [learned_day + 1, learned_day + 3, learned_day + 7]:
                    if hours_used + 0.5 <= hours_per_day:
                        end_time = current_time + timedelta(minutes=30)
                        day_plan['subjects'].append({
                            'subject': t['subject'],
                            'topic': t['topic'],
                            'type': 'revise',
                            'start_time': current_time.strftime('%H:%M'),
                            'end_time': end_time.strftime('%H:%M'),
                            'hours': 0.5
                        })
                        current_time = end_time + timedelta(minutes=min(15, (hours_per_day - hours_used)*60))
                        hours_used += 0.5 + BREAK_LENGTH
        
        # 2. Practice Slots (Priority: Medium - Difficulty based)
        # Allocate practice for topics already started/completed
        for t in topics:
            if t['learned_days'] and t.get('difficulty', 5) > 6:
                if hours_used + 1.0 <= hours_per_day:
                    end_time = current_time + timedelta(hours=1)
                    day_plan['subjects'].append({
                        'subject': t['subject'],
                        'topic': t['topic'],
                        'type': 'practice',
                        'start_time': current_time.strftime('%H:%M'),
                        'end_time': end_time.strftime('%H:%M'),
                        'hours': 1.0
                    })
                    current_time = end_time + timedelta(minutes=15)
                    hours_used += 1.0 + BREAK_LENGTH

        # 3. Learning Slots (Priority: High - Progress)
        # Sort topics by priority
        sorted_topics = sorted([t for t in topics if t['remaining'] > 0], 
                              key=lambda x: calculate_priority(x['difficulty'], x['remaining'], days_left - day + 1), 
                              reverse=True)
        
        for t in sorted_topics:
            if hours_used >= hours_per_day:
                break
                
            session_h = min(t['remaining'], SESSION_LENGTH, hours_per_day - hours_used)
            if session_h < 0.25: # Too short to be useful
                continue
                
            end_time = current_time + timedelta(hours=session_h)
            day_plan['subjects'].append({
                'subject': t['subject'],
                'topic': t['topic'],
                'type': 'learn',
                'start_time': current_time.strftime('%H:%M'),
                'end_time': end_time.strftime('%H:%M'),
                'hours': session_h
            })
            
            # Record engagement
            if day not in t['learned_days']:
                t['learned_days'].append(day)
                
            t['remaining'] -= session_h
            current_time = end_time + timedelta(minutes=15)
            hours_used += session_h + BREAK_LENGTH
            
        day_plan['total_hours'] = round(sum(s['hours'] for s in day_plan['subjects']), 1)
        timetable.append(day_plan)
        
    return timetable

def validate_input(subject, topic, difficulty, hours_required, days_left, hours_per_day):
    if not subject or not topic:
        return "All fields are required"
    try:
        if int(difficulty) < 1 or int(difficulty) > 10:
            return "Difficulty must be 1-10"
        if float(hours_required) <= 0:
            return "Hours required must be positive"
    except ValueError:
        return "Invalid numeric values"
    return None
