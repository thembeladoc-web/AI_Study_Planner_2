import React, { useState } from 'react';
import { useAuth } from '../utils/AuthContext';
import { toast } from 'react-toastify';
import '../styles/Profile.css';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    program: user?.program || '',
    study_preference: user?.study_preference || 'flexible',
    max_study_hours_per_day: user?.max_study_hours_per_day || 6,
    preferred_break_duration: user?.preferred_break_duration || 30,
    email_notifications: user?.email_notifications !== false,
    push_notifications: user?.push_notifications !== false
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await updateProfile(formData);
    if (result.success) {
      toast.success('Profile updated successfully!');
      setEditing(false);
    } else {
      toast.error(result.error);
    }
  };

  if (!user) return null;

  return (
    <div className="profile-page">
      <header className="page-header">
        <h1>👤 My Profile</h1>
        <p>Manage your account and study preferences</p>
      </header>

      <div className="profile-card">
        <div className="profile-header">
          <div className="avatar">
            {user.first_name ? user.first_name[0].toUpperCase() : user.username[0].toUpperCase()}
          </div>
          <div className="profile-info">
            <h2>{user.get_full_name || user.username}</h2>
            <p>{user.email}</p>
            <span className="student-badge">{user.student_number || 'No student number'}</span>
          </div>
          <button 
            className="edit-btn"
            onClick={() => setEditing(!editing)}
          >
            {editing ? 'Cancel' : 'Edit Profile'}
          </button>
        </div>

        {editing ? (
          <form onSubmit={handleSubmit} className="profile-form">
            <div className="form-section">
              <h3>Personal Information</h3>
              <div className="form-row">
                <div className="form-group">
                  <label>First Name</label>
                  <input type="text" name="first_name" value={formData.first_name} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label>Last Name</label>
                  <input type="text" name="last_name" value={formData.last_name} onChange={handleChange} />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Email</label>
                  <input type="email" name="email" value={formData.email} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label>Phone</label>
                  <input type="tel" name="phone" value={formData.phone} onChange={handleChange} />
                </div>
              </div>
              <div className="form-group">
                <label>Program</label>
                <input type="text" name="program" value={formData.program} onChange={handleChange} />
              </div>
            </div>

            <div className="form-section">
              <h3>Study Preferences</h3>
              <div className="form-row">
                <div className="form-group">
                  <label>Study Preference</label>
                  <select name="study_preference" value={formData.study_preference} onChange={handleChange}>
                    <option value="morning">Morning (6AM - 12PM)</option>
                    <option value="afternoon">Afternoon (12PM - 6PM)</option>
                    <option value="evening">Evening (6PM - 12AM)</option>
                    <option value="night">Night (12AM - 6AM)</option>
                    <option value="flexible">Flexible</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Max Study Hours/Day</label>
                  <input type="number" name="max_study_hours_per_day" min="1" max="12"
                    value={formData.max_study_hours_per_day} onChange={handleChange} />
                </div>
              </div>
              <div className="form-group">
                <label>Preferred Break Duration (minutes)</label>
                <input type="number" name="preferred_break_duration" min="5" max="120"
                  value={formData.preferred_break_duration} onChange={handleChange} />
              </div>
            </div>

            <div className="form-section">
              <h3>Notifications</h3>
              <div className="checkbox-group">
                <label className="checkbox-label">
                  <input type="checkbox" name="email_notifications" 
                    checked={formData.email_notifications} onChange={handleChange} />
                  Email Notifications
                </label>
                <label className="checkbox-label">
                  <input type="checkbox" name="push_notifications" 
                    checked={formData.push_notifications} onChange={handleChange} />
                  Push Notifications
                </label>
              </div>
            </div>

            <button type="submit" className="save-btn">Save Changes</button>
          </form>
        ) : (
          <div className="profile-details">
            <div className="detail-section">
              <h3>Personal Information</h3>
              <div className="detail-grid">
                <div className="detail-item">
                  <span className="label">Full Name</span>
                  <span className="value">{user.get_full_name || 'Not set'}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Email</span>
                  <span className="value">{user.email}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Phone</span>
                  <span className="value">{user.phone || 'Not set'}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Program</span>
                  <span className="value">{user.program || 'Not set'}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Year</span>
                  <span className="value">Year {user.year_of_study}</span>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h3>Study Preferences</h3>
              <div className="detail-grid">
                <div className="detail-item">
                  <span className="label">Study Preference</span>
                  <span className="value">{user.study_preference || 'Flexible'}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Max Hours/Day</span>
                  <span className="value">{user.max_study_hours_per_day || 6} hours</span>
                </div>
                <div className="detail-item">
                  <span className="label">Break Duration</span>
                  <span className="value">{user.preferred_break_duration || 30} minutes</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Profile;
