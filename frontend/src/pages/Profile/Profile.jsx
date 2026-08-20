import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { getProfile, updateProfile } from '../../services/api';
import MainLayout from '../../components/MainLayout/MainLayout';
import profileImage from '../../assets/hero.png';
import './Profile.css';

const initialProfile = {
  name: '',
  email: '',
  phone: '',
  dob: '',
  exam: '',
  percentile: '',
  category: '',
  domicile: '',
};

const Profile = () => {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(initialProfile);
  const [editing, setEditing] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        if (currentUser) {
          const data = await getProfile();
          setProfile((prev) => ({
            ...prev,
            ...data,
            name: data.name || currentUser.name || prev.name,
            email: data.email || currentUser.email || prev.email,
            phone: data.phone || currentUser.phone || prev.phone,
          }));
        }
      } catch (error) {
        console.error("Failed to load profile", error);
      }
    };
    fetchProfile();
  }, [currentUser]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setProfile((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    try {
      await updateProfile(profile);
      setSaved(true);
      setEditing(false);
      window.setTimeout(() => setSaved(false), 3200);
    } catch (error) {
      console.error("Failed to save profile", error);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/home', { replace: true });
  };

  return (
    <MainLayout>
      <div className="profile-page">
        {/* Page Header */}
        <div className="profile-header">
          <h1 className="profile-title">My Profile</h1>
          <div className="profile-actions">
            <button
              type="button"
              onClick={() => setEditing((prev) => !prev)}
              className="btn btn-secondary"
            >
              {editing ? 'Cancel' : 'Edit Profile'}
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="btn btn-primary"
            >
              Save Changes
            </button>
          </div>
        </div>

        {/* Success Toast */}
        {saved && (
          <div className="profile-toast">Profile updated successfully!</div>
        )}

        {/* Main Content Grid */}
        <div className="profile-grid">
          {/* Left Column: Profile Avatar & Completeness */}
          <div className="profile-left-column">
            {/* Profile Avatar Card */}
            <div className="profile-card profile-avatar-card">
              <div className="avatar-container">
                <img
                  src={profileImage}
                  alt="Profile avatar"
                  className="profile-avatar"
                />
                <button
                  type="button"
                  className="avatar-edit-btn"
                  aria-label="Edit profile picture"
                >
                  <span className="material-symbols-outlined">edit</span>
                </button>
              </div>
              <h2 className="avatar-name">{profile.name || currentUser?.name || 'User'}</h2>
              <p className="avatar-email">{profile.email || currentUser?.email || ''}</p>
              <div className="badges-container">
                <span className="badge badge-premium">Premium Member</span>
                <span className="badge badge-engineering">Engineering</span>
              </div>
            </div>

            {/* Profile Completeness Card */}
            <div className="profile-card profile-completeness-card">
              <p className="completeness-label">PROFILE COMPLETENESS</p>
              <div className="completeness-score">85%</div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: '85%' }} />
              </div>
              <p className="completeness-note">
                Complete your academic preferences to get better AI predictions.
              </p>
            </div>
          </div>

          {/* Right Column: Information Sections */}
          <div className="profile-right-column">
            {/* Personal Information Section */}
            <section className="profile-card">
              <div className="section-header">
                <span className="material-symbols-outlined section-icon">
                  person
                </span>
                <h2 className="section-title">Personal Information</h2>
              </div>
              <div className="section-divider" />
              <div className="form-grid">
                <div className="form-field">
                  <label htmlFor="name">Full Name</label>
                  <input
                    id="name"
                    type="text"
                    name="name"
                    value={profile.name}
                    onChange={handleChange}
                    readOnly={!editing}
                    className="form-input"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="email">Email Address</label>
                  <input
                    id="email"
                    type="email"
                    name="email"
                    value={profile.email}
                    onChange={handleChange}
                    readOnly
                    className="form-input"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="phone">Phone Number</label>
                  <input
                    id="phone"
                    type="tel"
                    name="phone"
                    value={profile.phone}
                    onChange={handleChange}
                    readOnly={!editing}
                    className="form-input"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="dob">Date of Birth</label>
                  <input
                    id="dob"
                    type="date"
                    name="dob"
                    value={profile.dob}
                    onChange={handleChange}
                    readOnly={!editing}
                    className="form-input"
                  />
                </div>
              </div>
            </section>

            {/* Academic Profile Section */}
            <section className="profile-card">
              <div className="section-header">
                <span className="material-symbols-outlined section-icon">
                  workspace_premium
                </span>
                <h2 className="section-title">Academic Profile</h2>
              </div>
              <div className="section-divider" />
              <div className="form-grid">
                <div className="form-field">
                  <label htmlFor="exam">Primary Exam</label>
                  <select
                    id="exam"
                    name="exam"
                    value={profile.exam}
                    onChange={handleChange}
                    disabled={!editing}
                    className="form-input"
                  >
                    <option value="JEE Main">JEE Main</option>
                    <option value="JEE Advanced">JEE Advanced</option>
                    <option value="NEET">NEET</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="percentile">Exam Rank / Percentile</label>
                  <input
                    id="percentile"
                    type="text"
                    name="percentile"
                    value={profile.percentile}
                    onChange={handleChange}
                    readOnly={!editing}
                    className="form-input"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="category">Category</label>
                  <select
                    id="category"
                    name="category"
                    value={profile.category}
                    onChange={handleChange}
                    disabled={!editing}
                    className="form-input"
                  >
                    <option value="General">General</option>
                    <option value="OBC">OBC</option>
                    <option value="SC">SC</option>
                    <option value="ST">ST</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="domicile">State of Domicile</label>
                  <select
                    id="domicile"
                    name="domicile"
                    value={profile.domicile}
                    onChange={handleChange}
                    disabled={!editing}
                    className="form-input"
                  >
                    <option value="Maharashtra">Maharashtra</option>
                    <option value="Delhi">Delhi</option>
                    <option value="Karnataka">Karnataka</option>
                  </select>
                </div>
              </div>
            </section>

            {/* Security Section */}
            <section className="profile-card security-card">
              <h2 className="section-title security-title">Security</h2>
              <div className="security-panel">
                <div className="security-content">
                  <p className="security-heading">Log out of your account</p>
                  <p className="security-description">
                    You will need to sign in again to access your predictors.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="btn btn-danger"
                >
                  Log Out
                </button>
              </div>
            </section>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default Profile;
