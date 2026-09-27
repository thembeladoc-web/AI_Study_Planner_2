import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import { toast } from 'react-toastify';
import '../styles/Auth.css';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    student_number: '',
    program: '',
    year_of_study: '1',
    study_preference: 'flexible'
  });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.password_confirm) {
      toast.error('Passwords do not match');
      return;
    }

    setLoading(true);
    const result = await register(formData);

    if (result.success) {
      toast.success('Registration successful!');
      navigate('/');
    } else {
      const errorMsg = typeof result.error === 'object' 
        ? Object.values(result.error).flat().join(', ')
        : result.error;
      toast.error(errorMsg);
    }

    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-card register-card">
        <img src="/pace-logo.jpeg" alt="Pace AI Study Planner" className="auth-logo" />
        <h2>Create Account</h2>
        <p>Join Pace AI Study Planner</p>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-row">
            <div className="form-group">
              <label>First Name</label>
              <input type="text" name="first_name" value={formData.first_name} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>Last Name</label>
              <input type="text" name="last_name" value={formData.last_name} onChange={handleChange} required />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Username</label>
              <input type="text" name="username" value={formData.username} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input type="email" name="email" value={formData.email} onChange={handleChange} required />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Student Number</label>
              <input type="text" name="student_number" value={formData.student_number} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Program</label>
              <input type="text" name="program" value={formData.program} onChange={handleChange} placeholder="e.g., BSc IT" />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Year of Study</label>
              <select name="year_of_study" value={formData.year_of_study} onChange={handleChange}>
                <option value="1">First Year</option>
                <option value="2">Second Year</option>
                <option value="3">Third Year</option>
                <option value="4">Fourth Year</option>
              </select>
            </div>
            <div className="form-group">
              <label>Study Preference</label>
              <select name="study_preference" value={formData.study_preference} onChange={handleChange}>
                <option value="morning">Morning</option>
                <option value="afternoon">Afternoon</option>
                <option value="evening">Evening</option>
                <option value="night">Night</option>
                <option value="flexible">Flexible</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Password</label>
              <input type="password" name="password" value={formData.password} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>Confirm Password</label>
              <input type="password" name="password_confirm" value={formData.password_confirm} onChange={handleChange} required />
            </div>
          </div>

          <button type="submit" className="auth-btn" disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
