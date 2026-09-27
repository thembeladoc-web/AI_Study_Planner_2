import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { toast } from 'react-toastify';
import '../styles/Assignments.css';

const Assignments = () => {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchAssignments();
  }, []);

  const fetchAssignments = async () => {
    try {
      const response = await api.get('/timetable/assignments/');
      setAssignments(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to load assignments');
    } finally {
      setLoading(false);
    }
  };

  const filteredAssignments = assignments.filter(a => {
    if (filter === 'all') return true;
    if (filter === 'upcoming') return a.days_until_due > 0;
    if (filter === 'overdue') return a.days_until_due <= 0;
    if (filter === 'high') return a.priority >= 3;
    return true;
  });

  const getPriorityColor = (priority) => {
    const colors = { 1: 'low', 2: 'medium', 3: 'high', 4: 'critical' };
    return colors[priority] || 'medium';
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading assignments...</p>
      </div>
    );
  }

  return (
    <div className="assignments-page">
      <header className="page-header">
        <h1>📝 Assignments</h1>
        <p>Track your upcoming assessments and deadlines</p>
      </header>

      <div className="filter-bar">
        <button className={`filter-btn ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>
          All
        </button>
        <button className={`filter-btn ${filter === 'upcoming' ? 'active' : ''}`} onClick={() => setFilter('upcoming')}>
          Upcoming
        </button>
        <button className={`filter-btn ${filter === 'overdue' ? 'active' : ''}`} onClick={() => setFilter('overdue')}>
          Overdue
        </button>
        <button className={`filter-btn ${filter === 'high' ? 'active' : ''}`} onClick={() => setFilter('high')}>
          High Priority
        </button>
      </div>

      <div className="assignments-list">
        {filteredAssignments.length === 0 ? (
          <div className="empty-state">
            <p>No assignments found in this category.</p>
          </div>
        ) : (
          filteredAssignments.map(assignment => (
            <div key={assignment.id} className={`assignment-card priority-${getPriorityColor(assignment.priority)}`}>
              <div className="assignment-header">
                <div className="assignment-title">
                  <h3>{assignment.title}</h3>
                  <span className="course-badge">{assignment.course?.code}</span>
                </div>
                <span className={`priority-badge ${getPriorityColor(assignment.priority)}`}>
                  {assignment.priority_label}
                </span>
              </div>

              <p className="assignment-description">{assignment.description}</p>

              <div className="assignment-footer">
                <div className="due-info">
                  <span className={`due-date ${assignment.days_until_due <= 2 ? 'urgent' : ''}`}>
                    📅 Due: {new Date(assignment.due_date).toLocaleDateString()}
                  </span>
                  <span className="days-left">
                    {assignment.days_until_due <= 0 
                      ? '⚠️ OVERDUE' 
                      : `${assignment.days_until_due} days left`}
                  </span>
                </div>
                <div className="assignment-meta">
                  <span className="weight-badge">Weight: {assignment.weight_percentage}%</span>
                  <span className="hours-badge">Est: {assignment.estimated_hours}h</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Assignments;
