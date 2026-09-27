import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { toast } from 'react-toastify';
import '../styles/StudyPlanner.css';

const StudyPlanner = () => {
  const [studyPlans, setStudyPlans] = useState([]);
  const [currentPlan, setCurrentPlan] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [weekStart, setWeekStart] = useState('');
  const [weekEnd, setWeekEnd] = useState('');
  const [maxHours, setMaxHours] = useState(6);
  const [selectedDay, setSelectedDay] = useState(0);

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  useEffect(() => {
    // Set default week (current week)
    const today = new Date();
    const monday = new Date(today.setDate(today.getDate() - today.getDay() + 1));
    const sunday = new Date(today.setDate(monday.getDate() + 6));

    setWeekStart(monday.toISOString().split('T')[0]);
    setWeekEnd(sunday.toISOString().split('T')[0]);

    fetchStudyPlans();
  }, []);

  const fetchStudyPlans = async () => {
    try {
      setLoading(true);
      const response = await api.get('/scheduler/plans/');
      setStudyPlans(response.data.results || response.data);
      if (response.data.length > 0) {
        setCurrentPlan(response.data[0]);
        fetchPlanSessions(response.data[0].id);
      }
    } catch (error) {
      console.error('Failed to fetch study plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPlanSessions = async (planId) => {
    try {
      const response = await api.get(`/scheduler/plans/${planId}/`);
      setSessions(response.data.sessions || []);
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const response = await api.post('/scheduler/generate/', {
        week_start: weekStart,
        week_end: weekEnd,
        preferences: {
          max_hours_per_day: maxHours,
          min_break_minutes: 30
        }
      });

      toast.success(response.data.message);
      setCurrentPlan(response.data.study_plan);
      setSessions(response.data.study_plan.sessions || []);
      fetchStudyPlans();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to generate study plan');
    } finally {
      setGenerating(false);
    }
  };

  const handleMarkComplete = async (sessionId) => {
    try {
      await api.post(`/scheduler/sessions/${sessionId}/complete/`, {
        actual_duration_minutes: null,
        notes: ''
      });
      toast.success('Session marked as complete!');
      if (currentPlan) {
        fetchPlanSessions(currentPlan.id);
      }
    } catch (error) {
      toast.error('Failed to mark session as complete');
    }
  };

  const getSessionsForDay = (dayIndex) => {
    return sessions.filter(s => s.day_of_week === dayIndex);
  };

  const getSessionPosition = (startTime) => {
    const [hours, minutes] = startTime.split(':').map(Number);
    return (hours - 6) * 60 + minutes;
  };

  const getSessionHeight = (durationMinutes) => {
    return durationMinutes;
  };

  const getSessionTypeIcon = (type) => {
    const icons = {
      'review': '🔄',
      'deep_study': '📖',
      'practice': '✏️',
      'reading': '📚',
      'memorization': '🧠',
      'group_study': '👥'
    };
    return icons[type] || '📖';
  };

  return (
    <div className="study-planner-page">
      <header className="page-header">
        <h1>🤖 AI Study Planner</h1>
        <p>Generate optimized study schedules using AI</p>
      </header>

      {/* Generate Panel */}
      <div className="generate-panel">
        <h3>Generate New Study Plan</h3>
        <div className="generate-form">
          <div className="form-row">
            <div className="form-group">
              <label>Week Start</label>
              <input 
                type="date" 
                value={weekStart} 
                onChange={(e) => setWeekStart(e.target.value)} 
              />
            </div>
            <div className="form-group">
              <label>Week End</label>
              <input 
                type="date" 
                value={weekEnd} 
                onChange={(e) => setWeekEnd(e.target.value)} 
              />
            </div>
            <div className="form-group">
              <label>Max Hours/Day</label>
              <input 
                type="number" 
                min="1" 
                max="12" 
                value={maxHours} 
                onChange={(e) => setMaxHours(Number(e.target.value))} 
              />
            </div>
          </div>
          <button 
            className="generate-btn" 
            onClick={handleGenerate} 
            disabled={generating}
          >
            {generating ? (
              <>
                <span className="spinner-small"></span>
                Generating AI Plan...
              </>
            ) : (
              <>🤖 Generate Study Plan</>
            )}
          </button>
        </div>
      </div>

      {/* Current Plan Stats */}
      {currentPlan && (
        <div className="plan-stats">
          <div className="stat-card">
            <h4>{currentPlan.session_count}</h4>
            <p>Sessions</p>
          </div>
          <div className="stat-card">
            <h4>{currentPlan.total_study_hours}h</h4>
            <p>Total Hours</p>
          </div>
          <div className="stat-card">
            <h4>{currentPlan.optimization_score || 'N/A'}</h4>
            <p>Optimization Score</p>
          </div>
          <div className="stat-card">
            <h4>{currentPlan.generation_time_ms}ms</h4>
            <p>Generation Time</p>
          </div>
        </div>
      )}

      {/* Day Selector */}
      <div className="day-selector">
        {days.map((day, index) => (
          <button
            key={day}
            className={`day-btn ${selectedDay === index ? 'active' : ''}`}
            onClick={() => setSelectedDay(index)}
          >
            {day}
          </button>
        ))}
      </div>

      {/* Study Sessions Grid */}
      <div className="sessions-timeline">
        <div className="time-ruler">
          {Array.from({ length: 18 }, (_, i) => i + 6).map(hour => (
            <div key={hour} className="time-mark">
              {hour}:00
            </div>
          ))}
        </div>
        <div className="sessions-container">
          {getSessionsForDay(selectedDay).map(session => (
            <div
              key={session.id}
              className={`session-card ${session.is_completed ? 'completed' : ''}`}
              style={{
                top: `${getSessionPosition(session.start_time)}px`,
                height: `${getSessionHeight(session.duration_minutes)}px`
              }}
            >
              <div className="session-icon">{getSessionTypeIcon(session.session_type)}</div>
              <div className="session-info">
                <h4>{session.course?.code}</h4>
                <p>{session.session_type.replace('_', ' ')}</p>
                <p className="session-topic">{session.topic}</p>
              </div>
              <div className="session-meta">
                <span className="time-badge">
                  {session.start_time?.slice(0, 5)} - {session.end_time?.slice(0, 5)}
                </span>
                <span className="duration-badge">{session.duration_minutes} min</span>
                <span className="priority-badge">Score: {session.priority_score}</span>
              </div>
              {!session.is_completed && (
                <button 
                  className="complete-btn"
                  onClick={() => handleMarkComplete(session.id)}
                >
                  ✓ Done
                </button>
              )}
              {session.is_completed && (
                <span className="completed-badge">✅ Completed</span>
              )}
            </div>
          ))}
          {getSessionsForDay(selectedDay).length === 0 && (
            <div className="empty-day">
              <p>No study sessions scheduled for {days[selectedDay]}</p>
              <p>Generate a study plan to see AI recommendations</p>
            </div>
          )}
        </div>
      </div>

      {/* Previous Plans */}
      {studyPlans.length > 1 && (
        <div className="previous-plans">
          <h3>Previous Study Plans</h3>
          <div className="plans-list">
            {studyPlans.slice(1).map(plan => (
              <div key={plan.id} className="plan-card" onClick={() => { setCurrentPlan(plan); fetchPlanSessions(plan.id); }}>
                <h4>{plan.name}</h4>
                <p>{plan.week_start} to {plan.week_end}</p>
                <span className="status-badge">{plan.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default StudyPlanner;
