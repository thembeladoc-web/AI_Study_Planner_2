import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { toast } from 'react-toastify';
import '../styles/Timetable.css';

const Timetable = () => {
  const [schedules, setSchedules] = useState([]);
  const [courses, setCourses] = useState([]);
  const [myCourses, setMyCourses] = useState([]);
  const [conflicts, setConflicts] = useState(null);
  const [loading, setLoading] = useState(true);
  // Convert JavaScript's Sunday-first index to the Monday-first list below.
  const [selectedDay, setSelectedDay] = useState((new Date().getDay() + 6) % 7);

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const timeSlots = Array.from({ length: 18 }, (_, i) => i + 6); // 6 AM to 11 PM

  useEffect(() => {
    fetchTimetableData();
  }, []);

  const fetchTimetableData = async () => {
    try {
      const [schedulesRes, coursesRes, myCoursesRes, conflictsRes] = await Promise.all([
        api.get('/timetable/schedules/'),
        api.get('/timetable/courses/'),
        api.get('/timetable/my-courses/'),
        api.get('/timetable/conflicts/')
      ]);

      // Django REST Framework returns paginated list data as { results: [] }.
      // Keep the page safe if pagination is disabled in another environment.
      const toList = (data) => (Array.isArray(data) ? data : data?.results || []);
      setSchedules(toList(schedulesRes.data));
      setCourses(toList(coursesRes.data));
      setMyCourses(toList(myCoursesRes.data));
      setConflicts(conflictsRes.data);
    } catch (error) {
      toast.error('Failed to load timetable data');
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async (courseId) => {
    try {
      await api.post('/timetable/enroll/', { course_id: courseId });
      toast.success('Successfully enrolled!');
      fetchTimetableData();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Enrollment failed');
    }
  };

  const getClassesForDay = (dayIndex) => {
    return schedules.filter(s => s.day_of_week === dayIndex);
  };

  const getClassPosition = (startTime) => {
    const [hours, minutes] = startTime.split(':').map(Number);
    return (hours - 6) * 60 + minutes; // Position in minutes from 6 AM
  };

  const getClassHeight = (startTime, endTime) => {
    const [startH, startM] = startTime.split(':').map(Number);
    const [endH, endM] = endTime.split(':').map(Number);
    return ((endH - startH) * 60 + (endM - startM));
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading timetable...</p>
      </div>
    );
  }

  return (
    <div className="timetable-page">
      <header className="page-header">
        <h1>📅 My Timetable</h1>
        <p>Manage your classes and detect conflicts</p>
      </header>

      {/* Conflicts Alert */}
      {conflicts && conflicts.total_conflicts > 0 && (
        <div className="conflicts-panel">
          <h3>⚠️ Schedule Conflicts ({conflicts.total_conflicts})</h3>
          {conflicts.overlapping_classes.length > 0 && (
            <div className="conflict-section">
              <h4>Overlapping Classes</h4>
              {conflicts.overlapping_classes.map((conflict, idx) => (
                <div key={idx} className="conflict-item">
                  <span className="conflict-badge critical">OVERLAP</span>
                  <p>
                    {conflict.class_1.course?.code} ({conflict.class_1.start_time}-{conflict.class_1.end_time}) 
                    overlaps with 
                    {conflict.class_2.course?.code} ({conflict.class_2.start_time}-{conflict.class_2.end_time})
                  </p>
                </div>
              ))}
            </div>
          )}
          {conflicts.back_to_back_exams.length > 0 && (
            <div className="conflict-section">
              <h4>Back-to-Back Exams</h4>
              {conflicts.back_to_back_exams.map((conflict, idx) => (
                <div key={idx} className="conflict-item">
                  <span className="conflict-badge warning">BACK-TO-BACK</span>
                  <p>
                    {conflict.exam_1.course?.code} and {conflict.exam_2.course?.code} 
                    on {conflict.exam_1.date} with only {conflict.gap_hours} hours gap
                  </p>
                </div>
              ))}
            </div>
          )}
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

      {/* Timetable Grid */}
      <div className="timetable-grid">
        <div className="time-column">
          {timeSlots.map(hour => (
            <div key={hour} className="time-slot">
              {hour}:00
            </div>
          ))}
        </div>
        <div className="classes-column">
          {getClassesForDay(selectedDay).map(schedule => (
            <div
              key={schedule.id}
              className={`class-card ${schedule.session_type}`}
              style={{
                top: `${getClassPosition(schedule.start_time)}px`,
                height: `${getClassHeight(schedule.start_time, schedule.end_time)}px`
              }}
            >
              <h4>{schedule.course?.code}</h4>
              <p>{schedule.session_type}</p>
              <p>{schedule.venue}</p>
              <span className="time-badge">
                {schedule.start_time?.slice(0, 5)} - {schedule.end_time?.slice(0, 5)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* My Courses */}
      <div className="my-courses-section">
        <h2>My Enrolled Courses</h2>
        {myCourses.length === 0 ? (
          <div className="empty-state">
            <p>You haven't enrolled in any courses yet.</p>
            <p>Browse available courses below and enroll.</p>
          </div>
        ) : (
          <div className="courses-grid">
            {myCourses.map(enrollment => (
              <div key={enrollment.id} className="course-card">
                <h4>{enrollment.course?.code}</h4>
                <p>{enrollment.course?.name}</p>
                <span className="credit-badge">{enrollment.course?.credits} credits</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Available Courses */}
      <div className="available-courses">
        <h2>Available Courses</h2>
        <div className="courses-grid">
          {courses.map(course => {
            const isEnrolled = myCourses.some(e => e.course?.id === course.id);
            return (
              <div key={course.id} className={`course-card ${isEnrolled ? 'enrolled' : ''}`}>
                <h4>{course.code}</h4>
                <p>{course.name}</p>
                <div className="course-meta">
                  <span className="credit-badge">{course.credits} credits</span>
                  <span className="difficulty-badge">Difficulty: {course.difficulty_rating}/5</span>
                </div>
                {!isEnrolled && (
                  <button 
                    className="enroll-btn"
                    onClick={() => handleEnroll(course.id)}
                  >
                    Enroll
                  </button>
                )}
                {isEnrolled && <span className="enrolled-badge">✓ Enrolled</span>}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Timetable;
