import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { toast } from 'react-toastify';
import '../styles/Attendance.css';

const Attendance = () => {
  const [summaries, setSummaries] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [markingMode, setMarkingMode] = useState(false);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [attendanceStatus, setAttendanceStatus] = useState('present');
  const [attendanceDate, setAttendanceDate] = useState(new Date().toISOString().split('T')[0]);

  useEffect(() => {
    fetchAttendanceData();
  }, []);

  const fetchAttendanceData = async () => {
    try {
      const [summariesRes, alertsRes] = await Promise.all([
        api.get('/attendance/summaries/'),
        api.get('/attendance/alerts/')
      ]);

      setSummaries(summariesRes.data.results || summariesRes.data);
      setAlerts(alertsRes.data);
    } catch (error) {
      toast.error('Failed to load attendance data');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAttendance = async () => {
    if (!selectedSchedule) {
      toast.error('Please select a class schedule');
      return;
    }

    try {
      await api.post('/attendance/mark/', {
        class_schedule_id: selectedSchedule,
        date: attendanceDate,
        status: attendanceStatus,
        check_in_time: new Date().toTimeString().slice(0, 5)
      });

      toast.success('Attendance marked successfully!');
      setMarkingMode(false);
      setSelectedSchedule(null);
      fetchAttendanceData();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to mark attendance');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'good': '#4CAF50',
      'warning': '#FF9800',
      'critical': '#F44336'
    };
    return colors[status] || '#9E9E9E';
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading attendance data...</p>
      </div>
    );
  }

  return (
    <div className="attendance-page">
      <header className="page-header">
        <h1>📊 Attendance Tracker</h1>
        <p>Monitor your class attendance and stay above minimum requirements</p>
      </header>

      {/* Alerts Section */}
      {alerts.alerts && alerts.alerts.length > 0 && (
        <div className="alerts-panel">
          <h3>⚠️ Attendance Alerts ({alerts.total_alerts})</h3>
          {alerts.alerts.map((alert, idx) => (
            <div key={idx} className={`alert-item ${alert.type}`}>
              <div className="alert-icon">
                {alert.type === 'critical' ? '🔴' : '🟡'}
              </div>
              <div className="alert-content">
                <h4>{alert.course} - {alert.course_name}</h4>
                <p>{alert.message}</p>
                <p className="alert-action-needed">
                  You need {alert.sessions_needed} more consecutive present sessions to reach minimum
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Mark Attendance Button */}
      <div className="action-bar">
        <button 
          className="mark-attendance-btn"
          onClick={() => setMarkingMode(!markingMode)}
        >
          {markingMode ? 'Cancel' : '📝 Mark Attendance'}
        </button>
      </div>

      {/* Mark Attendance Form */}
      {markingMode && (
        <div className="marking-form">
          <h3>Mark Today's Attendance</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Date</label>
              <input 
                type="date" 
                value={attendanceDate} 
                onChange={(e) => setAttendanceDate(e.target.value)} 
              />
            </div>
            <div className="form-group">
              <label>Status</label>
              <select value={attendanceStatus} onChange={(e) => setAttendanceStatus(e.target.value)}>
                <option value="present">Present</option>
                <option value="absent">Absent</option>
                <option value="late">Late</option>
                <option value="excused">Excused</option>
              </select>
            </div>
          </div>
          <button className="submit-btn" onClick={handleMarkAttendance}>
            Submit Attendance
          </button>
        </div>
      )}

      {/* Attendance Summaries */}
      <div className="summaries-grid">
        <h2>Course Attendance</h2>
        {summaries.length === 0 ? (
          <div className="empty-state">
            <p>No attendance records yet. Start marking attendance for your classes.</p>
          </div>
        ) : (
          summaries.map(summary => (
            <div key={summary.id} className={`summary-card status-${summary.status}`}>
              <div className="summary-header">
                <h3>{summary.course?.code}</h3>
                <span 
                  className="percentage-badge"
                  style={{ backgroundColor: getStatusColor(summary.status) }}
                >
                  {summary.attendance_percentage}%
                </span>
              </div>
              <p className="course-name">{summary.course?.name}</p>

              <div className="attendance-bar">
                <div 
                  className="attendance-fill"
                  style={{ 
                    width: `${Math.min(summary.attendance_percentage, 100)}%`,
                    backgroundColor: getStatusColor(summary.status)
                  }}
                ></div>
              </div>

              <div className="summary-stats">
                <div className="stat">
                  <span className="stat-value present">{summary.present_count}</span>
                  <span className="stat-label">Present</span>
                </div>
                <div className="stat">
                  <span className="stat-value absent">{summary.absent_count}</span>
                  <span className="stat-label">Absent</span>
                </div>
                <div className="stat">
                  <span className="stat-value late">{summary.late_count}</span>
                  <span className="stat-label">Late</span>
                </div>
                <div className="stat">
                  <span className="stat-value total">{summary.total_sessions}</span>
                  <span className="stat-label">Total</span>
                </div>
              </div>

              <div className="threshold-info">
                <p>Minimum required: {summary.minimum_required_percentage}%</p>
                <p>Sessions needed: {summary.sessions_needed_for_minimum}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Attendance;
