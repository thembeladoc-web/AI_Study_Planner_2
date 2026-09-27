import React from 'react';
import { NavLink } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faHome,
  faCalendarAlt,
  faBook,
  faTasks,
  faCheckCircle,
  faUsers,
  faCog
} from '@fortawesome/free-solid-svg-icons';

const Sidebar = () => {
  const menuItems = [
    { path: '/', label: 'Dashboard', icon: faHome },
    { path: '/timetable', label: 'Timetable', icon: faCalendarAlt },
    { path: '/study-planner', label: 'Study Plan', icon: faBook },
    { path: '/assignments', label: 'Assignments', icon: faTasks },
    { path: '/attendance', label: 'Attendance', icon: faCheckCircle },
    { path: '/study-groups', label: 'Study Groups', icon: faUsers },
    { path: '/profile', label: 'Profile', icon: faCog },
  ];

  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              isActive ? 'nav-item active' : 'nav-item'
            }
          >
            <FontAwesomeIcon icon={item.icon} className="nav-icon" />
            <span className="nav-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
