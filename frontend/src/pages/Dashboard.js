import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../utils/api';
import { useAuth } from '../utils/AuthContext';
import { toast } from 'react-toastify';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [conflicts, setConflicts] = useState(null);
  const [upcomingAssignments, setUpcomingAssignments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, conflictsRes, assignmentsRes] = await Promise.all([
        api.get('/timetable/dashboard/'),
        api.get('/timetable/conflicts/'),
        api.get('/timetable/assignments/upcoming/')
      ]);

      setStats(statsRes.data);
      setConflicts(conflictsRes.data);

      // Django REST Framework paginates list endpoints by default, returning
      // { count, next, previous, results }. Support both that shape and a
      // plain array so the dashboard remains compatible with either setting.
      const assignments = Array.isArray(assignmentsRes.data)
        ? assignmentsRes.data
        : assignmentsRes.data?.results || [];
      setUpcomingAssignments(assignments);
    } catch (error) {
      toast.error('Failed to load dashboard data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Welcome back, {user?.first_name || user?.username}! 👋</h1>
        <p>Here's what's happening with your academic schedule</p>
      </header>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📚</div>
          <div className="stat-info">
            <h3>{stats?.total_courses || 0}</h3>
            <p>Enrolled Courses</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📅</div>
          <div className="stat-info">
            <h3>{stats?.upcoming_classes_today || 0}</h3>
            <p>Classes Today</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-info">
            <h3>{stats?.assignments_this_week || 0}</h3>
            <p>Due This Week</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-info">
            <h3>{stats?.upcoming_exams || 0}</h3>
            <p>Upcoming Exams</p>
          </div>
        </div>
      </div>

      {/* Conflicts Alert */}
      {conflicts && conflicts.total_conflicts > 0 && (
        <div className="alert-banner alert-critical">
          <div className="alert-content">
            <span className="alert-icon">⚠️</span>
            <div>
              <h4>Schedule Conflicts Detected!</h4>
              <p>
                {conflicts.overlapping_classes.length} overlapping classes, 
                {conflicts.back_to_back_exams.length} back-to-back exams, 
                {conflicts.deadline_clustering.length} deadline clusters
              </p>
            </div>
          </div>
          <Link to="/timetable" className="alert-action">View Details</Link>
        </div>
      )}

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="action-buttons">
          <Link to="/study-planner" className="action-btn primary">
            <span>🤖</span>
            <div>
              <h4>Generate Study Plan</h4>
              <p>AI-optimized schedule</p>
            </div>
          </Link>
          <Link to="/timetable" className="action-btn">
            <span>📅</span>
            <div>
              <h4>View Timetable</h4>
              <p>Check your classes</p>
            </div>
          </Link>
          <Link to="/study-groups" className="action-btn">
            <span>👥</span>
            <div>
              <h4>Find Study Groups</h4>
              <p>Match with classmates</p>
            </div>
          </Link>
          <Link to="/attendance" className="action-btn">
            <span>📊</span>
            <div>
              <h4>Check Attendance</h4>
              <p>Monitor your progress</p>
            </div>
          </Link>
        </div>
      </div>

      {/* Upcoming Assignments */}
      <div className="upcoming-section">
        <h2>Upcoming Assignments</h2>
        {upcomingAssignments.length === 0 ? (
          <p className="empty-state">No upcoming assignments. Great job! 🎉</p>
        ) : (
          <div className="assignments-list">
            {upcomingAssignments.map((assignment) => (
              <div key={assignment.id} className={`assignment-item priority-${assignment.priority}`}>
                <div className="assignment-info">
                  <h4>{assignment.title}</h4>
                  <p>{assignment.course?.code} • {assignment.assessment_type}</p>
                </div>
                <div className="assignment-meta">
                  <span className={`due-badge ${assignment.days_until_due <= 2 ? 'urgent' : ''}`}>
                    {assignment.days_until_due <= 0 ? 'Overdue!' : 
                     assignment.days_until_due === 1 ? 'Due tomorrow' :
                     `${assignment.days_until_due} days left`}
                  </span>
                  <span className="weight-badge">{assignment.weight_percentage}%</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
