def calculate_priority(difficulty, hours_required, days_left):
    """
    Calculate priority score for a topic.
    
    Priority formula: (difficulty × hours_required) / days_left
    Higher priority = more urgent/important to study
    
    Args:
        difficulty: Difficulty level (1-10)
        hours_required: Total hours needed to complete the topic
        days_left: Number of days available
    
    Returns:
        priority: Priority score (higher = more urgent)
    """
    if days_left <= 0:
        days_left = 1
    
    priority = (difficulty * hours_required) / days_left
    return priority

def generate_timetable(topics, days_left, hours_per_day):
    """
    Generate daily study timetable based on priority.
    
    Args:
        topics: List of topic dictionaries with keys:
                - subject: subject name
                - topic: topic name
                - difficulty: difficulty level (1-10)
                - hours_required: hours needed for this topic
        days_left: Number of days available
        hours_per_day: Hours available per day
    
    Returns:
        timetable: List of daily study plans
    """
    if not topics:
        return []
    
    # Calculate priority for each topic
    for topic in topics:
        topic['priority'] = calculate_priority(
            topic.get('difficulty', 5),
            topic.get('hours_required', 1),
            days_left
        )
    
    # Sort by priority (highest first)
    sorted_topics = sorted(topics, key=lambda x: x['priority'], reverse=True)
    
    # Generate timetable
    timetable = []
    remaining_hours = {i: hours_per_day for i in range(1, days_left + 1)}
    
    for day in range(1, days_left + 1):
        day_plan = {
            'day': day,
            'subjects': [],
            'total_hours': 0
        }
        
        for topic in sorted_topics:
            if remaining_hours[day] <= 0:
                break
            
            topic_name = topic.get('topic', 'Unknown')
            hours_needed = topic.get('hours_required', 1)
            subject = topic.get('subject', 'General')
            
            # Allocate hours for this topic on this day
            hours_to_allocate = min(hours_needed, remaining_hours[day])
            
            if hours_to_allocate > 0:
                day_plan['subjects'].append({
                    'subject': subject,
                    'topic': topic_name,
                    'hours': hours_to_allocate,
                    'difficulty': topic.get('difficulty', 5)
                })
                day_plan['total_hours'] += hours_to_allocate
                remaining_hours[day] -= hours_to_allocate
                topic['hours_required'] -= hours_to_allocate
        
        timetable.append(day_plan)
    
    return timetable

def validate_input(subject, topic, difficulty, hours_required, days_left, hours_per_day):
    """
    Validate user input and return error messages.
    
    Returns:
        error: Error message string or None if valid
    """
    if not subject or subject.strip() == '':
        return "Subject is required"
    
    if not topic or topic.strip() == '':
        return "Topic is required"
    
    try:
        difficulty = int(difficulty)
        if difficulty < 1 or difficulty > 10:
            return "Difficulty must be between 1 and 10"
    except (ValueError, TypeError):
        return "Invalid difficulty value"
    
    try:
        hours_required = float(hours_required)
        if hours_required <= 0:
            return "Hours required must be greater than 0"
    except (ValueError, TypeError):
        return "Invalid hours required value"
    
    try:
        days_left = int(days_left)
        if days_left <= 0:
            return "Days left must be greater than 0"
    except (ValueError, TypeError):
        return "Invalid days left value"
    
    try:
        hours_per_day = float(hours_per_day)
        if hours_per_day <= 0:
            return "Hours per day must be greater than 0"
    except (ValueError, TypeError):
        return "Invalid hours per day value"
    
    return None

if __name__ == "__main__":
    # Test scheduler
    topics = [
        {'subject': 'Mathematics', 'topic': 'Calculus', 'difficulty': 8, 'hours_required': 20},
        {'subject': 'Physics', 'topic': 'Mechanics', 'difficulty': 6, 'hours_required': 15},
        {'subject': 'Chemistry', 'topic': 'Organic', 'difficulty': 7, 'hours_required': 12},
    ]
    
    timetable = generate_timetable(topics, 5, 4)
    for day in timetable:
        print(f"Day {day['day']}: {day['subjects']}")
