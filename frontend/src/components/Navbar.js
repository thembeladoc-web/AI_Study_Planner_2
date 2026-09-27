import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import '../styles/Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Don't show navbar on login/register pages
  if (location.pathname === '/login' || location.pathname === '/register') {
    return null;
  }

  if (!user) {
    return (
      <nav className="navbar">
        <div className="nav-brand">
          <Link to="/">
            <img src="/pace-logo.jpeg" alt="Pace AI Study Planner" className="brand-logo" />
            <span>Pace AI Study Planner</span>
          </Link>
        </div>
        <div className="nav-links">
          <Link to="/login" className="nav-link">Login</Link>
          <Link to="/register" className="nav-link">Register</Link>
        </div>
      </nav>
    );
  }

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <Link to="/">
          <img src="/pace-logo.jpeg" alt="Pace AI Study Planner" className="brand-logo" />
          <span>Pace AI Study Planner</span>
        </Link>
      </div>
      <div className="nav-links">
        <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>
          Dashboard
        </Link>
        <Link to="/timetable" className={`nav-link ${location.pathname === '/timetable' ? 'active' : ''}`}>
          Timetable
        </Link>
        <Link to="/assignments" className={`nav-link ${location.pathname === '/assignments' ? 'active' : ''}`}>
          Assignments
        </Link>
        <Link to="/study-planner" className={`nav-link ${location.pathname === '/study-planner' ? 'active' : ''}`}>
          Study Plan
        </Link>
        <Link to="/attendance" className={`nav-link ${location.pathname === '/attendance' ? 'active' : ''}`}>
          Attendance
        </Link>
        <Link to="/study-groups" className={`nav-link ${location.pathname === '/study-groups' ? 'active' : ''}`}>
          Groups
        </Link>
        {user.is_staff && (
          <Link to="/admin-dashboard" className={`nav-link ${location.pathname === '/admin-dashboard' ? 'active' : ''}`}>
            Admin
          </Link>
        )}
      </div>
      <div className="nav-user">
        <Link to="/profile" className="nav-link user-name">
          👤 {user.first_name || user.username}
        </Link>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
