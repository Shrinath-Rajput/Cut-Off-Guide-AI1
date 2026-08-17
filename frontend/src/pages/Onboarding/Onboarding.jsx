import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useOnboarding } from '../../context/OnboardingContext';
import './Onboarding.css';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const Onboarding = () => {
  const navigate = useNavigate();
  const {
    activeStep,
    studentProfile,
    setPersonal,
    setAcademic,
    setPreferences,
    nextStep,
    goToStep,
  } = useOnboarding();

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
  });

  const [academic, setAcademicLocal] = useState({
    examScore: studentProfile?.academic?.examScore || '',
    preferredBranch: studentProfile?.academic?.preferredBranch || '',
  });

  const [preferences, setPreferencesLocal] = useState({
    preferredLocation: studentProfile?.preferences?.preferredLocation || '',
    budgetRange: studentProfile?.preferences?.budgetRange || '',
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    setPersonalLocal({
      fullName: studentProfile?.fullName || '',
      email: studentProfile?.email || '',
      category: studentProfile?.category || '',
    });
  }, [studentProfile?.fullName, studentProfile?.email, studentProfile?.category]);

  useEffect(() => {
    setAcademicLocal({
      examScore: studentProfile?.academic?.examScore || '',
      preferredBranch: studentProfile?.academic?.preferredBranch || '',
    });
  }, [studentProfile?.academic?.examScore, studentProfile?.academic?.preferredBranch]);

  useEffect(() => {
    setPreferencesLocal({
      preferredLocation: studentProfile?.preferences?.preferredLocation || '',
      budgetRange: studentProfile?.preferences?.budgetRange || '',
    });
  }, [
    studentProfile?.preferences?.preferredLocation,
    studentProfile?.preferences?.budgetRange,
  ]);

  const validatePersonal = () => {
    const next = {};
    if (!personal.fullName.trim()) next.fullName = 'Full Name is required';
    if (!personal.email.trim()) {
      next.email = 'Email Address is required';
    } else if (!EMAIL_REGEX.test(personal.email.trim())) {
      next.email = 'Enter a valid email address';
    }
    if (!personal.category) next.category = 'Please select a Student Category';
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const validateAcademic = () => {
    const next = {};
    if (!academic.examScore.trim()) next.examScore = 'Exam Score is required';
    if (!academic.preferredBranch.trim()) next.preferredBranch = 'Preferred Branch is required';
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const validatePreferences = () => {
    const next = {};
    if (!preferences.preferredLocation.trim()) next.preferredLocation = 'Preferred Location is required';
    if (!preferences.budgetRange.trim()) next.budgetRange = 'Budget Range is required';
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
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
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

  const handleContinue = () => {
    if (activeStep === 1) {
      if (!validatePersonal()) {
        toast.error('Please complete all required fields');
        return;
      }
      setPersonal({
        fullName: personal.fullName.trim(),
        email: personal.email.trim(),
        category: personal.category,
      });
      nextStep();
      return;
    }

    if (activeStep === 2) {
      if (!validateAcademic()) {
        toast.error('Please complete all required fields');
        return;
      }
      setAcademic({
        examScore: academic.examScore.trim(),
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
      });
      nextStep();
      return;
    }

    if (activeStep === 4) {
      toast.success('Onboarding complete! Welcome to Cutoff Guide AI.');
      navigate('/home');
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

                <div className="form-field category-field">
                  <label className="field-label">Student Category</label>
                  <div className="category-options">
                    {['General', 'OBC', 'SC', 'ST'].map((option) => (
                      <label key={option} className="category-label">
                        <input
                          type="radio"
                          name="category"
                          value={option}
                          checked={personal.category === option}
                          onChange={() => handlePersonalChange('category', option)}
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
              </>
            )}

            {activeStep === 2 && (
              <>
                <div className="form-field">
                  <label className="field-label" htmlFor="examScore">Exam Score</label>
                  <input
                    type="text"
                    id="examScore"
                    value={academic.examScore}
                    onChange={(e) => handleAcademicChange('examScore', e.target.value)}
                    placeholder="e.g., 630 / 720"
                    className={`field-input ${errors.examScore ? 'field-input-error' : ''}`}
                  />
                  {errors.examScore && <div className="field-error-text">{errors.examScore}</div>}
                </div>

                <div className="form-field">
                  <label className="field-label" htmlFor="preferredBranch">Preferred Branch</label>
                  <input
                    type="text"
                    id="preferredBranch"
                    value={academic.preferredBranch}
                    onChange={(e) => handleAcademicChange('preferredBranch', e.target.value)}
                    placeholder="e.g., Engineering, Medical"
                    className={`field-input ${errors.preferredBranch ? 'field-input-error' : ''}`}
                  />
                  {errors.preferredBranch && (
                    <div className="field-error-text">{errors.preferredBranch}</div>
                  )}
                </div>
              </>
            )}

            {activeStep === 3 && (
              <>
                <div className="form-field">
                  <label className="field-label" htmlFor="preferredLocation">Preferred Location</label>
                  <input
                    type="text"
                    id="preferredLocation"
                    value={preferences.preferredLocation}
                    onChange={(e) => handlePreferencesChange('preferredLocation', e.target.value)}
                    placeholder="e.g., Mumbai, Pune"
                    className={`field-input ${errors.preferredLocation ? 'field-input-error' : ''}`}
                  />
                  {errors.preferredLocation && (
                    <div className="field-error-text">{errors.preferredLocation}</div>
                  )}
                </div>

                <div className="form-field">
                  <label className="field-label" htmlFor="budgetRange">Budget Range</label>
                  <input
                    type="text"
                    id="budgetRange"
                    value={preferences.budgetRange}
                    onChange={(e) => handlePreferencesChange('budgetRange', e.target.value)}
                    placeholder="e.g., 5-10 LPA"
                    className={`field-input ${errors.budgetRange ? 'field-input-error' : ''}`}
                  />
                  {errors.budgetRange && <div className="field-error-text">{errors.budgetRange}</div>}
                </div>
              </>
            )}

            {activeStep === 4 && (
              <>
                <div className="form-field">
                  <p
                    style={{
                      color: '#5a4136',
                      lineHeight: '1.6',
                      margin: 0,
                      fontFamily: 'Inter, sans-serif',
                      fontSize: '16px',
                    }}
                  >
                    Ready to see your admission predictions? Click "Complete Onboarding" to view
                    personalized college matches based on your profile.
                  </p>
                </div>
              </>
            )}
          </form>
        </div>

        <div className="bottom-action">
          <button className="continue-button" onClick={handleContinue} type="button">
            {getButtonText()}
            <span className="material-symbols-outlined button-icon">arrow_forward</span>
          </button>
        </div>
      </section>
    </div>
  );
};

export default Onboarding;
