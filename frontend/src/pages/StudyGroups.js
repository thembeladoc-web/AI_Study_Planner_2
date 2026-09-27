import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { toast } from 'react-toastify';
import '../styles/StudyGroups.css';

const StudyGroups = () => {
  const [groups, setGroups] = useState([]);
  const [myGroups, setMyGroups] = useState([]);
  const [recommendedGroups, setRecommendedGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('recommended');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newGroup, setNewGroup] = useState({
    name: '',
    description: '',
    course_id: '',
    max_members: 5,
    privacy: 'public',
    preferred_day: '',
    preferred_time_start: '',
    preferred_time_end: '',
    venue: '',
    is_online: false
  });

  useEffect(() => {
    fetchGroupsData();
  }, []);

  const fetchGroupsData = async () => {
    try {
      const [groupsRes, myGroupsRes, recommendedRes] = await Promise.all([
        api.get('/study-groups/groups/'),
        api.get('/study-groups/my-groups/'),
        api.get('/study-groups/find/')
      ]);

      setGroups(groupsRes.data.results || groupsRes.data);
      setMyGroups(myGroupsRes.data.groups || []);
      setRecommendedGroups(recommendedRes.data.recommended_groups || []);
    } catch (error) {
      toast.error('Failed to load study groups');
    } finally {
      setLoading(false);
    }
  };

  const handleJoinGroup = async (groupId) => {
    try {
      await api.post(`/study-groups/groups/${groupId}/join/`);
      toast.success('Join request submitted!');
      fetchGroupsData();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to join group');
    }
  };

  const handleLeaveGroup = async (groupId) => {
    try {
      await api.delete(`/study-groups/groups/${groupId}/leave/`);
      toast.success('Left group successfully');
      fetchGroupsData();
    } catch (error) {
      toast.error('Failed to leave group');
    }
  };

  const handleCreateGroup = async () => {
    try {
      await api.post('/study-groups/groups/', newGroup);
      toast.success('Study group created!');
      setShowCreateForm(false);
      setNewGroup({
        name: '', description: '', course_id: '', max_members: 5,
        privacy: 'public', preferred_day: '', preferred_time_start: '',
        preferred_time_end: '', venue: '', is_online: false
      });
      fetchGroupsData();
    } catch (error) {
      toast.error('Failed to create group');
    }
  };

  const getPrivacyBadge = (privacy) => {
    const badges = {
      'public': { class: 'public', icon: '🌐' },
      'private': { class: 'private', icon: '🔒' },
      'invite_only': { class: 'invite', icon: '📩' }
    };
    return badges[privacy] || badges['public'];
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading study groups...</p>
      </div>
    );
  }

  return (
    <div className="study-groups-page">
      <header className="page-header">
        <h1>👥 Study Groups</h1>
        <p>Find study partners and collaborate with classmates</p>
      </header>

      {/* Action Bar */}
      <div className="action-bar">
        <div className="tab-buttons">
          <button 
            className={`tab-btn ${activeTab === 'recommended' ? 'active' : ''}`}
            onClick={() => setActiveTab('recommended')}
          >
            🤖 Recommended
          </button>
          <button 
            className={`tab-btn ${activeTab === 'my-groups' ? 'active' : ''}`}
            onClick={() => setActiveTab('my-groups')}
          >
            My Groups ({myGroups.length})
          </button>
          <button 
            className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => setActiveTab('all')}
          >
            All Groups
          </button>
        </div>
        <button 
          className="create-group-btn"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? 'Cancel' : '+ Create Group'}
        </button>
      </div>

      {/* Create Group Form */}
      {showCreateForm && (
        <div className="create-form">
          <h3>Create New Study Group</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Group Name</label>
              <input 
                type="text" 
                value={newGroup.name}
                onChange={(e) => setNewGroup({...newGroup, name: e.target.value})}
                placeholder="e.g., MAT201 Study Squad"
              />
            </div>
            <div className="form-group">
              <label>Course</label>
              <input 
                type="text" 
                value={newGroup.course_id}
                onChange={(e) => setNewGroup({...newGroup, course_id: e.target.value})}
                placeholder="Course ID"
              />
            </div>
            <div className="form-group">
              <label>Max Members</label>
              <input 
                type="number" 
                min="2" 
                max="20"
                value={newGroup.max_members}
                onChange={(e) => setNewGroup({...newGroup, max_members: Number(e.target.value)})}
              />
            </div>
            <div className="form-group">
              <label>Privacy</label>
              <select 
                value={newGroup.privacy}
                onChange={(e) => setNewGroup({...newGroup, privacy: e.target.value})}
              >
                <option value="public">Public</option>
                <option value="private">Private</option>
                <option value="invite_only">Invite Only</option>
              </select>
            </div>
          </div>
          <button className="submit-btn" onClick={handleCreateGroup}>
            Create Group
          </button>
        </div>
      )}

      {/* Content Based on Active Tab */}
      <div className="groups-content">
        {activeTab === 'recommended' && (
          <div className="recommended-groups">
            <h2>AI-Recommended Study Groups</h2>
            {recommendedGroups.length === 0 ? (
              <div className="empty-state">
                <p>No recommendations yet. Enroll in courses to get matched!</p>
              </div>
            ) : (
              recommendedGroups.map((item, idx) => (
                <div key={idx} className="group-card recommended">
                  <div className="compatibility-score">
                    <div className="score-circle" style={{
                      background: `conic-gradient(#4CAF50 ${item.compatibility_score}%, #e0e0e0 0)`
                    }}>
                      <span>{item.compatibility_score}%</span>
                    </div>
                    <p>Match Score</p>
                  </div>
                  <div className="group-info">
                    <h3>{item.group.name}</h3>
                    <p className="course-name">{item.group.course?.code} - {item.group.course?.name}</p>
                    <div className="group-meta">
                      <span className="members-badge">
                        👥 {item.group.current_member_count}/{item.group.max_members} members
                      </span>
                      <span className={`privacy-badge ${getPrivacyBadge(item.group.privacy).class}`}>
                        {getPrivacyBadge(item.group.privacy).icon} {item.group.privacy}
                      </span>
                    </div>
                    <div className="reasons">
                      <h4>Why this matches you:</h4>
                      <ul>
                        {item.reasons.map((reason, ridx) => (
                          <li key={ridx}>✓ {reason}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  <button 
                    className="join-btn"
                    onClick={() => handleJoinGroup(item.group.id)}
                    disabled={item.group.is_full}
                  >
                    {item.group.is_full ? 'Full' : 'Join Group'}
                  </button>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'my-groups' && (
          <div className="my-groups">
            <h2>My Study Groups</h2>
            {myGroups.length === 0 ? (
              <div className="empty-state">
                <p>You haven't joined any study groups yet.</p>
                <p>Check the "Recommended" tab to find matches!</p>
              </div>
            ) : (
              myGroups.map((item, idx) => (
                <div key={idx} className="group-card my-group">
                  <div className="group-header">
                    <h3>{item.group.name}</h3>
                    <span className={`role-badge ${item.my_role}`}>{item.my_role}</span>
                  </div>
                  <p>{item.group.course?.code}</p>
                  <div className="upcoming-meetings">
                    <h4>Upcoming Meetings:</h4>
                    {item.upcoming_meetings.length === 0 ? (
                      <p>No upcoming meetings</p>
                    ) : (
                      item.upcoming_meetings.map(meeting => (
                        <div key={meeting.id} className="meeting-item">
                          <span>📅 {meeting.date} at {meeting.start_time?.slice(0, 5)}</span>
                          <span>{meeting.title}</span>
                        </div>
                      ))
                    )}
                  </div>
                  <button 
                    className="leave-btn"
                    onClick={() => handleLeaveGroup(item.group.id)}
                  >
                    Leave Group
                  </button>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'all' && (
          <div className="all-groups">
            <h2>All Study Groups</h2>
            <div className="groups-grid">
              {groups.map(group => (
                <div key={group.id} className="group-card compact">
                  <h4>{group.name}</h4>
                  <p>{group.course?.code}</p>
                  <span className="members-badge">
                    {group.current_member_count}/{group.max_members} members
                  </span>
                  <button 
                    className="join-btn small"
                    onClick={() => handleJoinGroup(group.id)}
                    disabled={group.is_full}
                  >
                    {group.is_full ? 'Full' : 'Join'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StudyGroups;
