import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { getProfile, updateProfile } from '../../services/api';
import MainLayout from '../../components/MainLayout/MainLayout';
import profileImage from '../../assets/hero.png';
import './Profile.css';

const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana',
  'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana',
  'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh',
  'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'
];

const EXAM_OPTIONS = [
  'JEE Main', 'JEE Advanced', 'NEET', 'MHT-CET', 'Diploma',
  'MBA CET', 'MCA CET', 'BBA CET', 'B.Pharm CET'
];

const COLLEGE_TYPES = ['Government', 'Private', 'Deemed'];

const initialProfile = {
  name: '',
  fullName: '',
  email: '',
  phone: '',
  dob: '',
  domicile: '',
  category: '',
  pwdCrossCategory: false,
  exam: '',
  examScore: '',
  careerOption: '',
  preferredBranch: '',
  preferredLocation: '',
  budgetRange: '0',
  collegeType: '',
  hostelRequired: false,
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
            fullName: data.fullName || data.name || currentUser.name || prev.name,
            name: data.name || data.fullName || currentUser.name || prev.name,
            email: data.email || currentUser.email || prev.email,
            phone: data.phone || currentUser.phone || prev.phone,
            domicile: data.domicile || data.locationZone || prev.domicile,
            exam: data.exam || data.academic?.exam || prev.exam,
            examScore: data.examScore || data.academic?.examScore || prev.examScore,
            careerOption: data.careerOption || data.academic?.careerOption || prev.careerOption,
            preferredBranch: data.preferredBranch || data.academic?.preferredBranch || prev.preferredBranch,
            preferredLocation: data.preferredLocation || data.preferences?.preferredLocation || prev.preferredLocation,
            budgetRange: data.budgetRange || data.preferences?.budgetRange || prev.budgetRange,
            collegeType: data.collegeType || data.preferences?.collegeType || prev.collegeType,
            hostelRequired: data.hostelRequired !== undefined
              ? data.hostelRequired
              : (data.preferences?.hostelRequired ?? prev.hostelRequired),
            category: data.category || prev.category,
            pwdCrossCategory: data.pwdCrossCategory !== undefined
              ? data.pwdCrossCategory
              : prev.pwdCrossCategory,
          }));
        }
      } catch (error) {
        console.error("Failed to load profile", error);
      }
    };
    fetchProfile();
  }, [currentUser]);

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setProfile((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const toggleCategory = (cat) => {
    setProfile((prev) => ({ ...prev, category: cat }));
  };

  const toggleCollegeType = (ctype) => {
    const currentTypes = profile.collegeType ? profile.collegeType.split(',').map(b => b.trim()) : [];
    let newTypes;
    if (currentTypes.includes(ctype)) {
      newTypes = currentTypes.filter(b => b !== ctype);
    } else {
      newTypes = [...currentTypes, ctype];
    }
    setProfile((prev) => ({ ...prev, collegeType: newTypes.join(', ') }));
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

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const displayValue = (val) => {
    if (val === undefined || val === null || val === '') return 'Not provided';
    if (typeof val === 'boolean') return val ? 'Yes' : 'No';
    return String(val);
  };

  return (
    <MainLayout>
      <div className="profile-page">
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

        {saved && (
          <div className="profile-toast">Profile updated successfully!</div>
        )}

        <div className="profile-grid">
          <div className="profile-left-column">
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
              <h2 className="avatar-name">{profile.fullName || profile.name || currentUser?.name || 'User'}</h2>
              <p className="avatar-email">{profile.email || currentUser?.email || ''}</p>
              <div className="badges-container">
                <span className="badge badge-premium">Premium Member</span>
                <span className="badge badge-engineering">{profile.exam || 'Academic'}</span>
              </div>
            </div>

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

          <div className="profile-right-column">
            <section className="profile-card">
              <div className="section-header">
                <span className="material-symbols-outlined section-icon">person</span>
                <h2 className="section-title">Personal Information</h2>
              </div>
              <div className="section-divider" />
              <div className="form-grid">
                <div className="form-field">
                  <label htmlFor="fullName">Full Name</label>
                  {editing ? (
                    <input
                      id="fullName"
                      type="text"
                      name="fullName"
                      value={profile.fullName || ''}
                      onChange={handleChange}
                      className="form-input"
                    />
                  ) : (
                    <div className="form-readonly">{displayValue(profile.fullName || profile.name)}</div>
                  )}
                </div>
                <div className="form-field">
                  <label htmlFor="email">Email Address</label>
                  <input
                    id="email"
                    type="email"
                    name="email"
                    value={profile.email || ''}
                    readOnly
                    className="form-input form-input--readonly"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="phone">Phone Number</label>
                  {editing ? (
                    <input
                      id="phone"
                      type="tel"
                      name="phone"
                      value={profile.phone || ''}
                      onChange={handleChange}
                      className="form-input"
                    />
                  ) : (
                    <div className="form-readonly">{displayValue(profile.phone)}</div>
                  )}
                </div>
                <div className="form-field">
                  <label htmlFor="domicile">State of Domicile</label>
                  {editing ? (
                    <select
                      id="domicile"
                      name="domicile"
                      value={profile.domicile || ''}
                      onChange={handleChange}
                      className="form-input"
                    >
                      <option value="" disabled>Select a state</option>
                      {INDIAN_STATES.map((state) => (
                        <option key={state} value={state}>{state}</option>
                      ))}
                    </select>
                  ) : (
                    <div className="form-readonly">{displayValue(profile.domicile)}</div>
                  )}
                </div>
                <div className="form-field form-field--span">
                  <label className="field-label-row">Student Category</label>
                  <div className="category-options-inline">
                    {['General', 'OBC', 'SC', 'ST', 'EWS', 'PWD', 'Defence/Ex-Servicemen', 'Minority', 'Kashmiri Migrant'].map((option) => {
                      const isSelected = (profile.category || '').includes(option);
                      if (editing) {
                        return (
                          <label key={option} className="category-label-inline">
                            <input
                              type="checkbox"
                              value={option}
                              checked={isSelected}
                              onChange={() => toggleCategory(option)}
                              className="radio-input"
                            />
                            <span>{option}</span>
                          </label>
                        );
                      }
                      return isSelected ? (
                        <span key={option} className="pill pill--category">{option}</span>
                      ) : null;
                    })}
                    {!editing && !(profile.category) && (
                      <span className="form-readonly-muted">Not provided</span>
                    )}
                  </div>
                </div>
                <div className="form-field form-field--span">
                  <label className="field-label-row">PWD (Cross-category)</label>
                  {editing ? (
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        name="pwdCrossCategory"
                        checked={profile.pwdCrossCategory || false}
                        onChange={handleChange}
                        className="radio-input"
                      />
                      <span>Applicant</span>
                    </label>
                  ) : (
                    <div className="form-readonly">{displayValue(profile.pwdCrossCategory)}</div>
                  )}
                </div>
              </div>
            </section>

            <section className="profile-card">
              <div className="section-header">
                <span className="material-symbols-outlined section-icon">workspace_premium</span>
                <h2 className="section-title">Academic Profile</h2>
              </div>
              <div className="section-divider" />
              <div className="form-grid">
                <div className="form-field">
                  <label htmlFor="exam">Primary Exam Target</label>
                  {editing ? (
                    <select
                      id="exam"
                      name="exam"
                      value={profile.exam || ''}
                      onChange={handleChange}
                      className="form-input"
                    >
                      <option value="" disabled>Select an exam</option>
                      {EXAM_OPTIONS.map((opt) => (
                        <option key={opt} value={opt}>{opt}</option>
                      ))}
                    </select>
                  ) : (
                    <div className="form-readonly">{displayValue(profile.exam)}</div>
                  )}
                </div>
                <div className="form-field">
                  <label htmlFor="examScore">Exam Score / Rank / Percentile</label>
                  {editing ? (
                    <input
                      id="examScore"
                      type="text"
                      name="examScore"
                      value={profile.examScore || ''}
                      onChange={handleChange}
                      className="form-input"
                    />
                  ) : (
                    <div className="form-readonly">{displayValue(profile.examScore)}</div>
                  )}
                </div>
                <div className="form-field">
                  <label htmlFor="careerOption">Target Field (Career)</label>
                  {editing ? (
                    <input
                      id="careerOption"
                      type="text"
                      name="careerOption"
                      value={profile.careerOption || ''}
                      onChange={handleChange}
                      className="form-input"
                    />
                  ) : (
                    <div className="form-readonly">{displayValue(profile.careerOption)}</div>
                  )}
                </div>
                <div className="form-field">
                  <label htmlFor="preferredBranch">Preferred Branch</label>
                  {editing ? (
                    <input
                      id="preferredBranch"
                      type="text"
                      name="preferredBranch"
                      value={profile.preferredBranch || ''}
                      onChange={handleChange}
                      className="form-input"
                    />
                  ) : (
                    <div className="form-readonly">{displayValue(profile.preferredBranch)}</div>
                  )}
                </div>
              </div>
            </section>

            <section className="profile-card">
              <div className="section-header">
                <span className="material-symbols-outlined section-icon">tune</span>
                <h2 className="section-title">Exam & Cutoff Preferences</h2>
              </div>
              <div className="section-divider" />
              <div className="form-grid">
                <div className="form-field">
                  <label htmlFor="preferredLocation">Preferred Location</label>
                  {editing ? (
                    <input
                      id="preferredLocation"
                      type="text"
                      name="preferredLocation"
                      value={profile.preferredLocation || ''}
                      onChange={handleChange}
                      className="form-input"
                      placeholder="e.g., Maharashtra, Pune, etc."
                    />
                  ) : (
                    <div className="form-readonly">{displayValue(profile.preferredLocation)}</div>
                  )}
                </div>
                <div className="form-field">
                  <label htmlFor="budgetRange">
                    Budget Range {editing ? `: ₹${profile.budgetRange || 0} Lakhs/year` : ''}
                  </label>
                  {editing ? (
                    <>
                      <div className="form-readonly" style={{ marginBottom: '0.25rem' }}>
                        ₹{profile.budgetRange || 0} Lakhs/year
                      </div>
                      <input
                        id="budgetRange"
                        type="range"
                        name="budgetRange"
                        min="0"
                        max="20"
                        step="1"
                        value={profile.budgetRange || '0'}
                        onChange={handleChange}
                        className="range-slider"
                      />
                    </>
                  ) : (
                    <div className="form-readonly">₹{profile.budgetRange || 0} Lakhs/year</div>
                  )}
                </div>
                <div className="form-field form-field--span">
                  <label className="field-label-row">Institutional Scope (College Type)</label>
                  <div className="category-options-inline">
                    {COLLEGE_TYPES.map((ctype) => {
                      const isSelected = (profile.collegeType || '').includes(ctype);
                      if (editing) {
                        return (
                          <button
                            type="button"
                            key={ctype}
                            className={`chip ${isSelected ? 'chip-selected' : ''}`}
                            onClick={() => toggleCollegeType(ctype)}
                          >
                            {ctype}
                          </button>
                        );
                      }
                      return isSelected ? (
                        <span key={ctype} className="pill pill--college">{ctype}</span>
                      ) : null;
                    })}
                    {!editing && !(profile.collegeType) && (
                      <span className="form-readonly-muted">Not provided</span>
                    )}
                  </div>
                </div>
                <div className="form-field form-field--span">
                  <label className="field-label-row">Hostel Required?</label>
                  {editing ? (
                    <div style={{ display: 'flex', gap: '1.5rem' }}>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                        <input
                          type="radio"
                          name="hostelRequired_yes"
                          checked={profile.hostelRequired === true}
                          onChange={() => setProfile((p) => ({ ...p, hostelRequired: true }))}
                          className="radio-input"
                        />
                        <span>Yes</span>
                      </label>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                        <input
                          type="radio"
                          name="hostelRequired_no"
                          checked={profile.hostelRequired === false}
                          onChange={() => setProfile((p) => ({ ...p, hostelRequired: false }))}
                          className="radio-input"
                        />
                        <span>No</span>
                      </label>
                    </div>
                  ) : (
                    <div className="form-readonly">{displayValue(profile.hostelRequired)}</div>
                  )}
                </div>
              </div>
            </section>

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
