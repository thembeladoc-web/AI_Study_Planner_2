import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { toast } from 'react-toastify';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBrain, faCheck, faPlay, faChartLine, faCalendar } from '@fortawesome/free-solid-svg-icons';

const StudyPlan = () => {
  const [plans, setPlans] = useState([]);
  const [currentPlan, setCurrentPlan] = useState(null);
  const [stats, setStats] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [weekStart, setWeekStart] = useState('');
  const [weekEnd, setWeekEnd] = useState('');

  useEffect(() => {
    fetchPlans();
    // Set default week dates
    const today = new Date();
    const monday = new Date(today.setDate(today.getDate() - today.getDay() + 1));
    const sunday = new Date(today.setDate(today.getDate() + 6));
    setWeekStart(monday.toISOString().split('T')[0]);
    setWeekEnd(sunday.toISOString().split('T')[0]);
  }, []);

  const fetchPlans = async () => {
    try {
      const res = await api.get('/scheduler/plans/');
      setPlans(res.data.results || []);
      if (res.data.results?.length > 0) {
        setCurrentPlan(res.data.results[0]);
        fetchStats(res.data.results[0].id);
      }
    } catch (error) {
      console.log('No study plans yet');
    }
  };

  const fetchStats = async (planId) => {
    try {
      const res = await api.get(`/scheduler/plans/${planId}/stats/`);
      setStats(res.data);
    } catch (error) {
      console.log('No stats available');
    }
  };

  const generatePlan = async () => {
    setGenerating(true);
    try {
      const res = await api.post('/scheduler/generate/', {
        week_start: weekStart,
        week_end: weekEnd,
        preferences: {
          max_hours_per_day: 6,
          min_break_minutes: 30
        }
      });
      toast.success(`Study plan generated! ${res.data.sessions_created} sessions created`);
      fetchPlans();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to generate study plan');
    } finally {
      setGenerating(false);
    }
  };

  const markComplete = async (sessionId, actualMinutes) => {
    try {
      await api.post(`/scheduler/sessions/${sessionId}/complete/`, {
        actual_duration_minutes: actualMinutes,
        notes: ''
      });
      toast.success('Session marked as complete');
      fetchPlans();
    } catch (error) {
      toast.error('Failed to update session');
    }
  };

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  return (
    <div className="study-plan-page">
      <div className="page-header">
        <h1><FontAwesomeIcon icon={faBrain} /> Study Plan</h1>
        <div className="header-actions">
          <input
            type="date"
            value={weekStart}
            onChange={e => setWeekStart(e.target.value)}
            className="date-input"
          />
          <span>to</span>
          <input
            type="date"
            value={weekEnd}
            onChange={e => setWeekEnd(e.target.value)}
            className="date-input"
          />
          <button className="btn-primary" onClick={generatePlan} disabled={generating}>
            <FontAwesomeIcon icon={faPlay} />
            {generating ? 'Generating...' : 'Generate Plan'}
          </button>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="stats-bar">
          <div className="stat-item">
            <FontAwesomeIcon icon={faChartLine} />
            <span>{stats.completion_rate}% Complete</span>
          </div>
          <div className="stat-item">
            <FontAwesomeIcon icon={faCalendar} />
            <span>{stats.total_planned_hours}h Planned</span>
          </div>
          <div className="stat-item">
            <span>{stats.completed_sessions}/{stats.total_sessions} Sessions</span>
          </div>
        </div>
      )}

      {/* Study Sessions */}
      {currentPlan ? (
        <div className="study-sessions">
          {days.map((day, dayIndex) => {
            const daySessions = currentPlan.sessions?.filter(s => s.day_of_week === dayIndex) || [];
            if (daySessions.length === 0) return null;

            return (
              <div key={day} className="day-section">
                <h3>{day}</h3>
                <div className="session-list">
                  {daySessions.map(session => (
                    <div key={session.id} className={`session-card ${session.is_completed ? 'completed' : ''}`}>
                      <div className="session-time">
                        {session.start_time} - {session.end_time}
                      </div>
                      <div className="session-details">
                        <strong>{session.course.code}</strong>
                        <span className="session-type">{session.session_type}</span>
                        <span className="duration">{session.duration_minutes} min</span>
                      </div>
                      <div className="session-actions">
                        {!session.is_completed ? (
                          <button
                            className="btn-complete"
                            onClick={() => markComplete(session.id, session.duration_minutes)}
                          >
                            <FontAwesomeIcon icon={faCheck} /> Done
                          </button>
                        ) : (
                          <span className="completed-badge">
                            <FontAwesomeIcon icon={faCheck} /> Completed
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="empty-state">
          <FontAwesomeIcon icon={faBrain} className="empty-icon" />
          <p>No study plan yet. Generate one to get started!</p>
        </div>
      )}
    </div>
  );
};

export default StudyPlan;
