// Smart Study Planner AI - Frontend JavaScript

// Global state
let topics = [];
let workloadChart = null;

// DOM Elements
const subjectInput = document.getElementById('subject');
const topicInput = document.getElementById('topic');
const difficultyInput = document.getElementById('difficulty');
const hoursRequiredInput = document.getElementById('hours_required');
const daysLeftInput = document.getElementById('days_left');
const hoursPerDayInput = document.getElementById('hours_per_day');
const addTopicBtn = document.getElementById('addTopicBtn');
const generatePlanBtn = document.getElementById('generatePlanBtn');
const topicsList = document.getElementById('topicsList');
const resultsSection = document.getElementById('resultsSection');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');

// Event Listeners
addTopicBtn.addEventListener('click', addTopic);
generatePlanBtn.addEventListener('click', generatePlan);

// Add topic to list
function addTopic() {
    const subject = subjectInput.value.trim();
    const topic = topicInput.value.trim();
    const difficulty = parseInt(difficultyInput.value) || 5;
    const hoursRequired = parseFloat(hoursRequiredInput.value) || 5;
    const daysLeft = parseInt(daysLeftInput.value) || 1;
    const hoursPerDay = parseFloat(hoursPerDayInput.value) || 1;

    // Validate inputs
    if (!subject) {
        showError('Please enter a subject name');
        return;
    }
    if (!topic) {
        showError('Please enter a topic name');
        return;
    }
    if (difficulty < 1 || difficulty > 10) {
        showError('Difficulty must be between 1 and 10');
        return;
    }
    if (hoursRequired <= 0) {
        showError('Hours required must be greater than 0');
        return;
    }

    // Add to topics array
    topics.push({
        subject: subject,
        topic: topic,
        difficulty: difficulty,
        hours_required: hoursRequired
    });

    // Update UI
    renderTopicsList();

    // Clear inputs
    subjectInput.value = '';
    topicInput.value = '';
    difficultyInput.value = '5';
    hoursRequiredInput.value = '5';
    subjectInput.focus();
}

// Render topics list
function renderTopicsList() {
    if (topics.length === 0) {
        topicsList.innerHTML = '<li class="empty-message">No topics added yet</li>';
        return;
    }

    topicsList.innerHTML = topics.map((t, index) => `
        <li class="topic-item">
            <div class="topic-info">
                <span class="topic-subject">${t.subject}</span>
                <span>${t.topic}</span>
                <span class="topic-difficulty">Difficulty: ${t.difficulty}</span>
                <span>${t.hours_required} hours</span>
            </div>
            <button class="remove-topic" onclick="removeTopic(${index})">Remove</button>
        </li>
    `).join('');
}

// Remove topic from list
function removeTopic(index) {
    topics.splice(index, 1);
    renderTopicsList();
}

// Generate study plan
async function generatePlan() {
    if (topics.length === 0) {
        showError('Please add at least one topic');
        return;
    }

    const daysLeft = parseInt(daysLeftInput.value);
    const hoursPerDay = parseFloat(hoursPerDayInput.value);

    if (!daysLeft || daysLeft <= 0) {
        showError('Please enter valid days left');
        return;
    }
    if (!hoursPerDay || hoursPerDay <= 0) {
        showError('Please enter valid hours per day');
        return;
    }

    // Show loading state
    generatePlanBtn.disabled = true;
    generatePlanBtn.textContent = 'Generating...';

    try {
        const response = await fetch('/generate-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topics: topics,
                days_left: daysLeft,
                hours_per_day: hoursPerDay
            })
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data);
        } else {
            showError(data.error || 'Failed to generate plan');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        generatePlanBtn.disabled = false;
        generatePlanBtn.textContent = '🚀 Generate Smart Plan';
    }
}

// Display results
function displayResults(data) {
    // Show results section
    resultsSection.style.display = 'block';

    // Update probability
    const probabilityValue = document.getElementById('probabilityValue');
    probabilityValue.textContent = data.probability + '%';
    
    // Color code based on probability
    if (data.probability >= 70) {
        probabilityValue.style.color = '#28a745';
    } else if (data.probability >= 40) {
        probabilityValue.style.color = '#ffc107';
    } else {
        probabilityValue.style.color = '#dc3545';
    }

    // Update stats
    document.getElementById('totalHours').textContent = data.total_hours;
    document.getElementById('avgDifficulty').textContent = data.avg_difficulty;

    // Render chart
    renderChart(data.timetable);

    // Render timetable
    renderTimetable(data.timetable);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Render workload chart
function renderChart(timetable) {
    const ctx = document.getElementById('workloadChart').getContext('2d');
    
    const labels = timetable.map(d => 'Day ' + d.day);
    const data = timetable.map(d => d.total_hours);

    // Destroy previous chart if exists
    if (workloadChart) {
        workloadChart.destroy();
    }

    workloadChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Study Hours',
                data: data,
                backgroundColor: 'rgba(102, 126, 234, 0.7)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Daily Study Hours',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Hours'
                    },
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Day'
                    }
                }
            }
        }
    });
}

// Render timetable
function renderTimetable(timetable) {
    const timetableContainer = document.getElementById('timetable');
    
    if (!timetable || timetable.length === 0) {
        timetableContainer.innerHTML = '<p>No schedule generated</p>';
        return;
    }

    timetableContainer.innerHTML = timetable.map(day => `
        <div class="day-card">
            <div class="day-header">
                <span class="day-title">Day ${day.day}</span>
                <span class="day-hours">${day.total_hours} hours</span>
            </div>
            <div class="day-subjects">
                ${day.subjects && day.subjects.length > 0 ? day.subjects.map(s => `
                    <div class="subject-item">
                        <div>
                            <span class="subject-name">${s.subject}</span>
                            <span class="subject-topic"> - ${s.topic}</span>
                        </div>
                        <span class="subject-hours">${s.hours}h</span>
                    </div>
                `).join('') : '<p>No study planned for this day</p>'}
            </div>
        </div>
    `).join('');
}

// Show error message
function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

// Hide error message
function hideError() {
    errorMessage.style.display = 'none';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Smart Study Planner AI loaded');
});
