import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useOnboarding } from '../../context/OnboardingContext';
import { useAuth } from '../../context/AuthContext';
import { registerUser, updateProfile } from '../../services/api';
import './Onboarding.css';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 
  'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 
  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 
  'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh', 
  'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'
];

import { EXAM_CONFIG, validateAcademicScore } from '../../utils/validation';

const STANDARD_BRANCHES = [
  'Computer Science', 'Information Technology', 'Electronics & Telecom', 'Mechanical', 'Civil', 'Electrical', 'Chemical'
];

const CAREER_OPTIONS = [
  'Engineering', 'Medical', 'Management', 'Law', 'Design', 'Architecture', 'Other'
];

const COLLEGE_TYPES = ['Government', 'Private', 'Deemed'];

const Onboarding = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const isSignup = new URLSearchParams(location.search).get('mode') === 'signup';
  const {
    activeStep,
    studentProfile,
    setPersonal,
    setAcademic,
    setPreferences,
    nextStep,
    goToStep,
  } = useOnboarding();
  const { login } = useAuth();

  const steps = useMemo(() => ['Personal', 'Academic', 'Prefs', 'Predict'], []);
  const stepIcons = useMemo(
    () => ({
      Personal: 'person',
      Academic: 'school',
      Prefs: 'tune',
      Predict: 'psychology',
    }),
    []
  );

  const [personal, setPersonalLocal] = useState({
    fullName: studentProfile?.fullName || '',
    email: studentProfile?.email || '',
    category: studentProfile?.category || '',
    pwdCrossCategory: studentProfile?.pwdCrossCategory || false,
    phone: studentProfile?.phone || '',
    domicile: studentProfile?.domicile || '',
  });

  const [academic, setAcademicLocal] = useState({
    exam: studentProfile?.academic?.exam || '',
    examScore: studentProfile?.academic?.examScore || '',
    careerOption: studentProfile?.academic?.careerOption || '',
    preferredBranch: studentProfile?.academic?.preferredBranch || '',
  });

  const [preferences, setPreferencesLocal] = useState({
    preferredLocation: studentProfile?.preferences?.preferredLocation || '',
    budgetRange: studentProfile?.preferences?.budgetRange || '0',
    collegeType: studentProfile?.preferences?.collegeType || '',
    hostelRequired: studentProfile?.preferences?.hostelRequired || false,
  });

  const [errors, setErrors] = useState({});
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setPersonalLocal({
      fullName: studentProfile?.fullName || '',
      email: studentProfile?.email || '',
      category: studentProfile?.category || '',
      pwdCrossCategory: studentProfile?.pwdCrossCategory || false,
      phone: studentProfile?.phone || '',
      domicile: studentProfile?.domicile || '',
    });
  }, [
    studentProfile?.fullName,
    studentProfile?.email,
    studentProfile?.category,
    studentProfile?.pwdCrossCategory,
    studentProfile?.phone,
    studentProfile?.domicile,
  ]);

  useEffect(() => {
    setAcademicLocal({
      exam: studentProfile?.academic?.exam || '',
      examScore: studentProfile?.academic?.examScore || '',
      careerOption: studentProfile?.academic?.careerOption || '',
      preferredBranch: studentProfile?.academic?.preferredBranch || '',
    });
  }, [
    studentProfile?.academic?.exam,
    studentProfile?.academic?.examScore,
    studentProfile?.academic?.careerOption,
    studentProfile?.academic?.preferredBranch,
  ]);

  useEffect(() => {
    setPreferencesLocal({
      preferredLocation: studentProfile?.preferences?.preferredLocation || '',
      budgetRange: studentProfile?.preferences?.budgetRange || '0',
      collegeType: studentProfile?.preferences?.collegeType || '',
      hostelRequired: studentProfile?.preferences?.hostelRequired || false,
    });
  }, [
    studentProfile?.preferences?.preferredLocation,
    studentProfile?.preferences?.budgetRange,
    studentProfile?.preferences?.collegeType,
    studentProfile?.preferences?.hostelRequired,
  ]);

  const validatePersonal = () => {
    const next = {};
    if (!personal.fullName.trim()) next.fullName = 'Full Name is required';
    if (!personal.email.trim()) {
      next.email = 'Email Address is required';
    } else if (!EMAIL_REGEX.test(personal.email.trim())) {
      next.email = 'Enter a valid email address';
    }
    if (!personal.phone.trim()) {
      next.phone = 'Phone Number is required';
    } else if (!/^\d{10}$/.test(personal.phone.replace(/\D/g, ''))) {
      next.phone = 'Enter a valid 10-digit phone number';
    }
    if (!personal.domicile) next.domicile = 'State of Domicile is required';
    if (!personal.category) next.category = 'Please select a Student Category';
    setErrors(next);
    return Object.keys(next).length === 0;
  };


  const validateAcademic = () => {
    const next = {};
    if (!academic.exam) next.exam = 'Please select an exam';
    if (!academic.examScore.trim()) {
      next.examScore = 'Exam Score is required';
    } else {
      const scoreError = validateAcademicScore(academic.exam, academic.examScore);
      if (scoreError) next.examScore = scoreError;
    }
    if (!academic.careerOption) next.careerOption = 'Please select a career option';
    if (!academic.preferredBranch) next.preferredBranch = 'Please select a branch';
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleAcademicScoreBlur = () => {
    if (academic.exam && academic.examScore) {
      const scoreError = validateAcademicScore(academic.exam, academic.examScore);
      if (scoreError) {
        setErrors((prev) => ({ ...prev, examScore: scoreError }));
      } else {
        setErrors((prev) => {
          const next = { ...prev };
          delete next.examScore;
          return next;
        });
      }
    }
  };

  const toggleCategory = (cat) => {
    const currentCategories = personal.category ? personal.category.split(',').map(b => b.trim()) : [];
    let newCategories;
    if (currentCategories.includes(cat)) {
      newCategories = currentCategories.filter(b => b !== cat);
    } else {
      newCategories = [...currentCategories, cat];
    }
    const newValue = newCategories.join(', ');
    handlePersonalChange('category', newValue);
  };

  const validatePreferences = () => {
    const next = {};
    if (!preferences.preferredLocation.trim()) next.preferredLocation = 'Preferred Location is required';
    if (!preferences.collegeType.trim()) next.collegeType = 'Please select at least one college type';
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handlePersonalChange = (field, value) => {
    setPersonalLocal((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  const handleAcademicChange = (field, value) => {
    setAcademicLocal((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      // If changing exam, re-validate score if exists
      if (field === 'exam' && academic.examScore) {
         const scoreError = validateAcademicScore(value, academic.examScore);
         setErrors((prev) => {
           const next = { ...prev };
           delete next.exam;
           if (scoreError) next.examScore = scoreError;
           else delete next.examScore;
           return next;
         });
      } else {
        setErrors((prev) => {
          const next = { ...prev };
          delete next[field];
          return next;
        });
      }
    }
  };

  const handlePreferencesChange = (field, value) => {
    setPreferencesLocal((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  const toggleCollegeType = (ctype) => {
    const currentTypes = preferences.collegeType ? preferences.collegeType.split(',').map(b => b.trim()) : [];
    let newTypes;
    if (currentTypes.includes(ctype)) {
      newTypes = currentTypes.filter(b => b !== ctype);
    } else {
      newTypes = [...currentTypes, ctype];
    }
    const newValue = newTypes.join(', ');
    handlePreferencesChange('collegeType', newValue);
  };

  const handleContinue = async () => {
    console.log('handleContinue called, activeStep:', activeStep);
    if (activeStep === 1) {
      if (!validatePersonal()) {
        toast.error('Please complete all required fields');
        return;
      }
      setPersonal({
        fullName: personal.fullName.trim(),
        email: personal.email.trim(),
        category: personal.category,
        pwdCrossCategory: personal.pwdCrossCategory,
        phone: personal.phone.trim(),
        domicile: personal.domicile,
      });
      nextStep();
      return;
    }

    if (activeStep === 2) {
      if (personal.category.trim().length === 0) {
        toast.error('Please select at least one category.');
        return;
      }
      if (!validateAcademic()) {
        toast.error('Please complete all required fields');
        return;
      }
      setAcademic({
        exam: academic.exam,
        examScore: academic.examScore.trim(),
        careerOption: academic.careerOption,
        preferredBranch: academic.preferredBranch.trim(),
      });
      nextStep();
      return;
    }

    if (activeStep === 3) {
      if (!validatePreferences()) {
        toast.error('Please complete all required fields');
        return;
      }
      setPreferences({
        preferredLocation: preferences.preferredLocation.trim(),
        budgetRange: preferences.budgetRange.trim(),
        collegeType: preferences.collegeType,
        hostelRequired: preferences.hostelRequired,
      });
      nextStep();
      return;
    }

    if (activeStep === 4) {
      if (isSignup && (!password || password.length < 8 || password !== confirmPassword)) {
        const message = !password || password.length < 8 ? 'Password must be at least 8 characters' : 'Passwords do not match';
        setErrors({ password: message });
        toast.error(message);
        return;
      }
      try {
        setIsSubmitting(true);
        const payload = {
          name: studentProfile.fullName,
          email: studentProfile.email,
          category: studentProfile.category,
          pwdCrossCategory: studentProfile.pwdCrossCategory,
          phone: studentProfile.phone,
          domicile: studentProfile.domicile,
          exam: studentProfile.academic?.exam,
          examScore: studentProfile.academic?.examScore,
          careerOption: studentProfile.academic?.careerOption,
          preferredBranch: studentProfile.academic?.preferredBranch,
          preferredLocation: studentProfile.preferences?.preferredLocation,
          budgetRange: studentProfile.preferences?.budgetRange,
          collegeType: studentProfile.preferences?.collegeType,
          hostelRequired: studentProfile.preferences?.hostelRequired,
        };
        if (isSignup) {
          await registerUser({ ...payload, password });
          localStorage.removeItem('onboarding_state');
          toast.success('Account created successfully. Please sign in.');
          navigate('/login', { replace: true });
        } else {
          const updatedUser = await updateProfile(payload);
          login(updatedUser, localStorage.getItem('auth_token'));
          toast.success('Onboarding complete! Welcome to Cutoff Guide AI.');
          navigate('/home');
        }
      } catch (error) {
        toast.error(error?.response?.data?.detail || error?.response?.data?.message || 'Failed to save profile. Please try again.');
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  const getButtonText = () => {
    if (activeStep === 1) return 'Continue to Academic Details';
    if (activeStep === 2) return 'Continue to Preferences';
    if (activeStep === 3) return 'Continue to Prediction';
    return 'Complete Onboarding';
  };

  const handleStepClick = (stepNumber) => {
    if (stepNumber >= activeStep) return;
    setErrors({});
    goToStep(stepNumber);
  };

  const renderStepIndicator = () => {
    const elements = [];
    steps.forEach((step, index) => {
      const stepNumber = index + 1;
      const isActive = stepNumber === activeStep;
      const isDone = stepNumber < activeStep;
      const clickable = isDone;

      elements.push(
        <div
          key={step}
          className="step-item"
          onClick={() => clickable && handleStepClick(stepNumber)}
          style={clickable ? { cursor: 'pointer' } : undefined}
        >
          <div className={`step-circle ${isActive ? 'active' : isDone ? 'done' : ''}`}>
            <span className="material-symbols-outlined step-icon">
              {stepIcons[step]}
            </span>
          </div>
          <span className={`step-label ${isActive ? 'active' : isDone ? 'done' : ''}`}>
            {step}
          </span>
        </div>
      );

      if (index < steps.length - 1) {
        elements.push(<div key={`divider-${index}`} className="step-divider"></div>);
      }
    });
    return elements;
  };

  const progress = (activeStep / steps.length) * 100;

  return (
    <div className="onboarding-wrapper">
      <header className="onboarding-header-section">
        <h1 className="onboarding-title">Welcome to Cutoff Guide AI</h1>
        <p className="onboarding-subtitle">Let's personalize your college prediction experience.</p>

        <div className="progress-bar-container">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
          </div>
        </div>

        <div className="step-indicator">{renderStepIndicator()}</div>
      </header>

      <section className="form-section">
        <div className="form-card">
          <h2 className="form-title">
            {activeStep === 1 && 'Personal Details'}
            {activeStep === 2 && 'Academic Details'}
            {activeStep === 3 && 'Preferences'}
            {activeStep === 4 && 'Prediction Profile'}
          </h2>

          <form className="personal-form" onSubmit={(e) => e.preventDefault()}>
            {activeStep === 1 && (
              <>
                <div className="form-field">
                  <label className="field-label" htmlFor="fullName">Full Name</label>
                  <input
                    type="text"
                    id="fullName"
                    name="fullName"
                    value={personal.fullName}
                    onChange={(e) => handlePersonalChange('fullName', e.target.value)}
                    placeholder="Enter your full name"
                    className={`field-input ${errors.fullName ? 'field-input-error' : ''}`}
                  />
                  {errors.fullName && <div className="field-error-text">{errors.fullName}</div>}
                </div>

                <div className="form-field">
                  <label className="field-label" htmlFor="email">Email Address</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={personal.email}
                    onChange={(e) => handlePersonalChange('email', e.target.value)}
                    placeholder="Enter your email"
                    className={`field-input ${errors.email ? 'field-input-error' : ''}`}
                  />
                  {errors.email && <div className="field-error-text">{errors.email}</div>}
                </div>

                <div className="form-field">
                  <label className="field-label" htmlFor="phone">Phone Number</label>
                  <input
                    type="tel"
                    id="phone"
                    name="phone"
                    value={personal.phone}
                    onChange={(e) => handlePersonalChange('phone', e.target.value)}
                    placeholder="Enter your 10-digit phone number"
                    className={`field-input ${errors.phone ? 'field-input-error' : ''}`}
                  />
                  {errors.phone && <div className="field-error-text">{errors.phone}</div>}
                </div>

                <div className="form-field">
                  <label className="field-label" htmlFor="domicile">State of Domicile</label>
                  <select
                    id="domicile"
                    name="domicile"
                    value={personal.domicile}
                    onChange={(e) => handlePersonalChange('domicile', e.target.value)}
                    className={`field-input ${errors.domicile ? 'field-input-error' : ''}`}
                  >
                    <option value="" disabled>Select your state</option>
                    {INDIAN_STATES.map((state) => (
                      <option key={state} value={state}>{state}</option>
                    ))}
                  </select>
                  {errors.domicile && <div className="field-error-text">{errors.domicile}</div>}
                </div>

                <div className="form-field category-field">
                  <label className="field-label">Student Category</label>
                  <div className="category-options">
                    {['General', 'OBC', 'SC', 'ST', 'EWS', 'PWD', 'Defence/Ex-Servicemen', 'Minority', 'Kashmiri Migrant'].map((option) => (
                      <label key={option} className="category-label">
                        <input
                          type="checkbox"
                          name="category"
                          value={option}
                          checked={personal.category.includes(option)}
                          onChange={() => toggleCategory(option)}
                          className="radio-input"
                        />
                        <span
                          className={`category-text ${errors.category ? 'category-text-error' : ''}`}
                        >
                          {option}
                        </span>
                      </label>
                    ))}
                  </div>
                  {errors.category && <div className="field-error-text">{errors.category}</div>}
                </div>
                
                <div className="form-field category-field" style={{ marginTop: '1rem' }}>
                  <label className="category-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      name="pwdCrossCategory"
                      checked={personal.pwdCrossCategory}
                      onChange={(e) => handlePersonalChange('pwdCrossCategory', e.target.checked)}
                      className="radio-input"
                    />
                    <span className="category-text">PWD (Cross-category applicant)</span>
                  </label>
                </div>
              </>
            )}

            {activeStep === 2 && (
              <>
                <div className="form-field">
                  <label className="field-label" htmlFor="exam">Exam</label>
                  <select
                    id="exam"
                    name="exam"
                    value={academic.exam}
                    onChange={(e) => handleAcademicChange('exam', e.target.value)}
                    className={`field-input ${errors.exam ? 'field-input-error' : ''}`}
                  >
                    <option value="" disabled>Select an exam</option>
                    {Object.keys(EXAM_CONFIG).map((examOption) => (
                      <option key={examOption} value={examOption}>{examOption}</option>
                    ))}
                  </select>
                  {errors.exam && <div className="field-error-text">{errors.exam}</div>}
                </div>

                <div className="form-field">
                  <label className="field-label" htmlFor="examScore">Exam Score</label>
                  <input
                    type="text"
                    id="examScore"
                    value={academic.examScore}
                    onChange={(e) => handleAcademicChange('examScore', e.target.value)}
                    onBlur={handleAcademicScoreBlur}
                    placeholder="e.g., 630"
                    className={`field-input ${errors.examScore ? 'field-input-error' : ''}`}
                  />
                  {errors.examScore && <div className="field-error-text">{errors.examScore}</div>}
                </div>

                <div className="form-field">
                  <label className="field-label" htmlFor="careerOption">Career Option</label>
                  <select
                    id="careerOption"
                    name="careerOption"
                    value={academic.careerOption}
                    onChange={(e) => handleAcademicChange('careerOption', e.target.value)}
                    className={`field-input ${errors.careerOption ? 'field-input-error' : ''}`}
                  >
                    <option value="" disabled>Select a career option</option>
                    {CAREER_OPTIONS.map((career) => (
                      <option key={career} value={career}>{career}</option>
                    ))}
                  </select>
                  {errors.careerOption && <div className="field-error-text">{errors.careerOption}</div>}
                </div>

                <div className="form-field">
                  <label className="field-label" htmlFor="preferredBranch">Preferred Branch</label>
                  <select
                    id="preferredBranch"
                    name="preferredBranch"
                    value={academic.preferredBranch}
                    onChange={(e) => handleAcademicChange('preferredBranch', e.target.value)}
                    className={`field-input ${errors.preferredBranch ? 'field-input-error' : ''}`}
                  >
                    <option value="" disabled>Select a branch</option>
                    {STANDARD_BRANCHES.map((branch) => (
                      <option key={branch} value={branch}>{branch}</option>
                    ))}
                  </select>
                  {errors.preferredBranch && (
                    <div className="field-error-text">{errors.preferredBranch}</div>
                  )}
                </div>
              </>
            )}

            {activeStep === 3 && (
              <>
                <div className="form-field">
                  <label className="field-label" htmlFor="preferredLocation">Preferred Location (State/City)</label>
                  <input
                    type="text"
                    id="preferredLocation"
                    list="locations-list"
                    value={preferences.preferredLocation}
                    onChange={(e) => handlePreferencesChange('preferredLocation', e.target.value)}
                    placeholder="Search for a state or city..."
                    className={`field-input ${errors.preferredLocation ? 'field-input-error' : ''}`}
                  />
                  <datalist id="locations-list">
                    {INDIAN_STATES.map((state) => (
                      <option key={state} value={state} />
                    ))}
                  </datalist>
                  {errors.preferredLocation && (
                    <div className="field-error-text">{errors.preferredLocation}</div>
                  )}
                </div>

                <div className="form-field">
                  <label className="field-label" htmlFor="budgetRange">
                    Budget Range: ₹{preferences.budgetRange} Lakhs/year
                  </label>
                  <input
                    type="range"
                    id="budgetRange"
                    min="0"
                    max="20"
                    step="1"
                    value={preferences.budgetRange}
                    onChange={(e) => handlePreferencesChange('budgetRange', e.target.value)}
                    className="range-slider"
                  />
                </div>

                <div className="form-field">
                  <label className="field-label">College Type</label>
                  <div className="chip-group">
                    {COLLEGE_TYPES.map(ctype => {
                      const isSelected = preferences.collegeType.includes(ctype);
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
                    })}
                  </div>
                  {errors.collegeType && (
                    <div className="field-error-text">{errors.collegeType}</div>
                  )}
                </div>

                <div className="form-field category-field" style={{ marginTop: '1rem' }}>
                  <label className="field-label">Hostel Required?</label>
                  <div className="category-options" style={{ marginTop: '0.5rem' }}>
                    <label className="category-label">
                      <input
                        type="radio"
                        name="hostelRequired"
                        value="yes"
                        checked={preferences.hostelRequired === true}
                        onChange={() => handlePreferencesChange('hostelRequired', true)}
                        className="radio-input"
                      />
                      <span className="category-text">Yes</span>
                    </label>
                    <label className="category-label">
                      <input
                        type="radio"
                        name="hostelRequired"
                        value="no"
                        checked={preferences.hostelRequired === false}
                        onChange={() => handlePreferencesChange('hostelRequired', false)}
                        className="radio-input"
                      />
                      <span className="category-text">No</span>
                    </label>
                  </div>
                </div>
              </>
            )}

            {activeStep === 4 && (
              <>
                {isSignup && (
                  <div className="summary-section">
                    <div className="form-field">
                      <label className="field-label" htmlFor="signup-password">Password</label>
                      <input id="signup-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} className="field-input" autoComplete="new-password" />
                    </div>
                    <div className="form-field">
                      <label className="field-label" htmlFor="signup-confirm-password">Confirm Password</label>
                      <input id="signup-confirm-password" type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} className="field-input" autoComplete="new-password" />
                    </div>
                    {errors.password && <div className="field-error-text">{errors.password}</div>}
                  </div>
                )}
                <div className="summary-card">
                <p className="summary-intro">Ready to see your admission predictions? Review your details below before completing.</p>
                
                <div className="summary-section">
                  <div className="summary-header">
                    <h3>Personal Details</h3>
                    <button type="button" className="edit-link" onClick={() => goToStep(1)}>Edit</button>
                  </div>
                  <div className="summary-grid">
                    <div className="summary-item"><span className="summary-label">Name:</span> {studentProfile.fullName}</div>
                    <div className="summary-item"><span className="summary-label">Email:</span> {studentProfile.email}</div>
                    <div className="summary-item"><span className="summary-label">Phone:</span> {studentProfile.phone}</div>
                    <div className="summary-item"><span className="summary-label">Domicile:</span> {studentProfile.domicile}</div>
                    <div className="summary-item"><span className="summary-label">Category:</span> {studentProfile.category} {studentProfile.pwdCrossCategory ? '(PWD)' : ''}</div>
                  </div>
                </div>

                <div className="summary-section">
                  <div className="summary-header">
                    <h3>Academic Details</h3>
                    <button type="button" className="edit-link" onClick={() => goToStep(2)}>Edit</button>
                  </div>
                  <div className="summary-grid">
                    <div className="summary-item"><span className="summary-label">Exam:</span> {studentProfile.academic?.exam}</div>
                    <div className="summary-item"><span className="summary-label">Score:</span> {studentProfile.academic?.examScore}</div>
                    <div className="summary-item"><span className="summary-label">Career Option:</span> {studentProfile.academic?.careerOption}</div>
                    <div className="summary-item"><span className="summary-label">Branch:</span> {studentProfile.academic?.preferredBranch}</div>
                  </div>
                </div>

                <div className="summary-section">
                  <div className="summary-header">
                    <h3>Preferences</h3>
                    <button type="button" className="edit-link" onClick={() => goToStep(3)}>Edit</button>
                  </div>
                  <div className="summary-grid">
                    <div className="summary-item"><span className="summary-label">Location:</span> {studentProfile.preferences?.preferredLocation}</div>
                    <div className="summary-item"><span className="summary-label">Budget:</span> ₹{studentProfile.preferences?.budgetRange} Lakhs/yr</div>
                    <div className="summary-item"><span className="summary-label">College Type:</span> {studentProfile.preferences?.collegeType}</div>
                    <div className="summary-item"><span className="summary-label">Hostel:</span> {studentProfile.preferences?.hostelRequired ? 'Yes' : 'No'}</div>
                  </div>
                </div>
                </div>
              </>
            )}
          </form>
        </div>

        <div className="bottom-action">
          <button className="continue-button" onClick={handleContinue} type="button" disabled={isSubmitting}>
            {isSubmitting ? 'Creating Account...' : isSignup && activeStep === 4 ? 'Create Account' : getButtonText()}
            <span className="material-symbols-outlined button-icon">arrow_forward</span>
          </button>
        </div>
      </section>
    </div>
  );
};

export default Onboarding;
