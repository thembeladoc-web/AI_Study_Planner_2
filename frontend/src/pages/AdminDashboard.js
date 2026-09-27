import React, { useEffect, useMemo, useState } from 'react';
import api from '../utils/api';
import { toast } from 'react-toastify';
import '../styles/AdminDashboard.css';

const resources = {
  users: { label: 'Users', endpoint: '/admin/users/', columns: ['username', 'email', 'program', 'is_active', 'is_staff'] },
  courses: { label: 'Courses', endpoint: '/admin/courses/', columns: ['code', 'name', 'credits', 'difficulty_rating'] },
  schedules: { label: 'Schedules', endpoint: '/admin/schedules/', columns: ['course', 'session_type', 'day_name', 'start_time', 'end_time', 'venue'] },
  assignments: { label: 'Assignments', endpoint: '/admin/assignments/', columns: ['course', 'title', 'assessment_type', 'due_date', 'priority'] },
  exams: { label: 'Exams', endpoint: '/admin/exams/', columns: ['course', 'exam_type', 'date', 'start_time', 'venue'] },
  'study-groups': { label: 'Study Groups', endpoint: '/admin/study-groups/', columns: ['name', 'course', 'privacy', 'status', 'max_members'] },
  attendance: { label: 'Attendance', endpoint: '/admin/attendance/', columns: ['student', 'course_code', 'date', 'status', 'minutes_late'] }
};

const listFrom = (data) => Array.isArray(data) ? data : data?.results || [];
const displayValue = (item, key) => {
  const value = item[key];
  if (value && typeof value === 'object') return value.code || value.name || value.username || value.id;
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  return value ?? '—';
};

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [section, setSection] = useState('users');
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [courseForm, setCourseForm] = useState({ code: '', name: '', credits: 3, difficulty_rating: 3 });
  const resource = resources[section];

  const loadStats = async () => {
    const response = await api.get('/admin/stats/');
    setStats(response.data);
  };

  const loadRows = async (key = section) => {
    setLoading(true);
    try {
      const response = await api.get(resources[key].endpoint);
      setRows(listFrom(response.data));
    } catch (error) {
      toast.error('Could not load administrator data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats().catch(() => toast.error('Could not load dashboard statistics.'));
  }, []);

  useEffect(() => { loadRows(); }, [section]);

  const statCards = useMemo(() => stats ? [
    ['Users', stats.users], ['Active', stats.active_users], ['Courses', stats.courses],
    ['Schedules', stats.schedules], ['Assignments', stats.assignments], ['Exams', stats.exams],
    ['Study groups', stats.study_groups], ['Attendance records', stats.attendance_records]
  ] : [], [stats]);

  const deleteRow = async (id) => {
    if (!window.confirm('Delete this record? This cannot be undone.')) return;
    try {
      await api.delete(`${resource.endpoint}${id}/`);
      toast.success(`${resource.label.slice(0, -1) || resource.label} deleted.`);
      await Promise.all([loadRows(), loadStats()]);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Delete failed.');
    }
  };

  const updateUser = async (user, field) => {
    try {
      await api.patch(`/admin/users/${user.id}/`, { [field]: !user[field] });
      await Promise.all([loadRows(), loadStats()]);
      toast.success('User permissions updated.');
    } catch (error) {
      toast.error('Could not update user.');
    }
  };

  const createCourse = async (event) => {
    event.preventDefault();
    try {
      await api.post('/admin/courses/', courseForm);
      setCourseForm({ code: '', name: '', credits: 3, difficulty_rating: 3 });
      await Promise.all([loadRows(), loadStats()]);
      toast.success('Course created.');
    } catch (error) {
      toast.error(error.response?.data?.code?.[0] || 'Could not create course.');
    }
  };

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <div>
          <p className="eyebrow">PACE CONTROL CENTRE</p>
          <h1>Admin Dashboard</h1>
          <p>Monitor and manage the content that appears in Pace AI Study Planner.</p>
        </div>
        <a className="admin-django-link" href="http://127.0.0.1:8000/admin/" target="_blank" rel="noreferrer">Open Django Admin</a>
      </header>

      <section className="admin-stats">
        {statCards.map(([label, value]) => <div className="admin-stat" key={label}><strong>{value}</strong><span>{label}</span></div>)}
      </section>

      <div className="admin-layout">
        <aside className="admin-sidebar">
          {Object.entries(resources).map(([key, item]) => (
            <button key={key} className={section === key ? 'admin-nav active' : 'admin-nav'} onClick={() => setSection(key)}>{item.label}</button>
          ))}
        </aside>

        <main className="admin-panel">
          <div className="admin-panel-heading"><div><p className="eyebrow">MANAGEMENT</p><h2>{resource.label}</h2></div><button onClick={() => loadRows()} className="admin-refresh">Refresh</button></div>

          {section === 'courses' && <form className="admin-create-form" onSubmit={createCourse}>
            <input placeholder="Course code" value={courseForm.code} onChange={e => setCourseForm({ ...courseForm, code: e.target.value })} required />
            <input placeholder="Course name" value={courseForm.name} onChange={e => setCourseForm({ ...courseForm, name: e.target.value })} required />
            <input type="number" min="1" max="20" placeholder="Credits" value={courseForm.credits} onChange={e => setCourseForm({ ...courseForm, credits: Number(e.target.value) })} />
            <input type="number" min="1" max="5" placeholder="Difficulty" value={courseForm.difficulty_rating} onChange={e => setCourseForm({ ...courseForm, difficulty_rating: Number(e.target.value) })} />
            <button type="submit">Add course</button>
          </form>}

          {loading ? <div className="admin-empty">Loading…</div> : rows.length === 0 ? <div className="admin-empty">No {resource.label.toLowerCase()} found.</div> : <div className="admin-table-wrap"><table className="admin-table"><thead><tr>{resource.columns.map(column => <th key={column}>{column.replaceAll('_', ' ')}</th>)}<th>Actions</th></tr></thead><tbody>{rows.map(row => <tr key={row.id}>{resource.columns.map(column => <td key={column}>{displayValue(row, column)}</td>)}<td className="admin-actions">{section === 'users' && <><button onClick={() => updateUser(row, 'is_active')}>{row.is_active ? 'Disable' : 'Enable'}</button><button onClick={() => updateUser(row, 'is_staff')}>{row.is_staff ? 'Remove staff' : 'Make staff'}</button></>}<button className="danger" onClick={() => deleteRow(row.id)}>Delete</button></td></tr>)}</tbody></table></div>}
        </main>
      </div>
    </div>
  );
};

export default AdminDashboard;
