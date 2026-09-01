import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useOnboarding } from '../../context/OnboardingContext';
import { useAuth } from '../../context/AuthContext';
import { updateProfile, sendOtp, registerUser } from '../../services/api';
import { SIGNUP_PENDING_KEY } from '../Signup/Signup';
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
  'Computer Science', 'Information Technology', 'Electronics & Telecom', 'Mechanical', 'Civil', 'Electrical', 'Chemical', 'AI & ML'
];

const CAREER_OPTIONS = [
  'Engineering', 'Medical', 'Management', 'Law', 'Design', 'Architecture', 'Other'
];

const COLLEGE_TYPES = ['Government', 'Private', 'Deemed'];

const EDUCATION_LEVEL_OPTIONS = [
  'High School / Secondary',
  'Undergraduate Degree',
  'Postgraduate Degree',
  'Professional Certification',
];

const TARGET_STREAM_OPTIONS = [
  'Engineering & Technology',
  'Medicine & Health Sciences',
  'Business & Management',
  'Arts & Humanities',
  'Basic Sciences',
];

const SUBJECT_OPTIONS = ['Mathematics', 'Physics', 'Computer Science', 'Chemistry'];

const AREA_OF_INTEREST_OPTIONS = [
  'Computer Science',
  'Engineering',
  'Business Admin',
  'Mathematics',
  'Biology',
  'Economics'
];

const DEGREE_LEVEL_OPTIONS = [
  {
    value: 'undergraduate',
    label: 'Undergraduate',
    description: 'Bachelors, Associates',
    icon: 'menu_book',
  },
  {
    value: 'postgraduate',
    label: 'Postgraduate',
    description: 'Masters, PhD, Research',
    icon: 'science',
  },
];

const ROLE_OPTIONS = [
  {
    value: 'student',
    label: 'Student',
    icon: 'person',
    description: 'Looking for university admissions data and cutoffs.',
  },
  {
    value: 'parent',
    label: 'Parent / Guardian',
    icon: 'family_restroom',
    description: 'Researching options for a dependent.',
  },
  {
    value: 'counselor',
    label: 'Counselor',
    icon: 'support_agent',
    description: 'Guiding multiple students through admissions.',
  },
  {
    value: 'exploring',
    label: 'Just Exploring',
    icon: 'explore',
    description: 'Browsing academic data out of curiosity.',
  },
];

const GOAL_OPTIONS = [
  'Find Universities',
  'Compare Cutoffs',
  'Research Scholarships',
  'Analyze Trends',
];

const Onboarding = () => {
  const navigate = useNavigate();
  const {
    activeStep,
    studentProfile,
    setPersonal,
    setAcademic,
    setPreferences,
    nextStep,
    prevStep,
    goToStep,
  } = useOnboarding();
  const { login, isAuthenticated } = useAuth();

  useEffect(() => {
    const hasPending = !!sessionStorage.getItem(SIGNUP_PENDING_KEY);
    if (!isAuthenticated && !hasPending) {
      navigate('/signup', { replace: true });
    }
  }, [isAuthenticated, navigate]);

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
    educationLevel: studentProfile?.academic?.educationLevel || '',
    targetStream: studentProfile?.academic?.targetStream || '',
    subjects: Array.isArray(studentProfile?.academic?.subjects) ? studentProfile.academic.subjects : [],
    areasOfInterest: Array.isArray(studentProfile?.academic?.areasOfInterest) ? studentProfile.academic.areasOfInterest : [],
    targetDegreeLevel: studentProfile?.academic?.targetDegreeLevel || '',
    expectedEntranceScore: studentProfile?.academic?.expectedEntranceScore || '',
    scoreType: studentProfile?.academic?.scoreType || 'Percentage',
  });

  const [preferences, setPreferencesLocal] = useState({
    preferredLocation: studentProfile?.preferences?.preferredLocation || '',
    budgetRange: studentProfile?.preferences?.budgetRange || '0',
    collegeType: studentProfile?.preferences?.collegeType || '',
    hostelRequired: studentProfile?.preferences?.hostelRequired || false,
  });

  const [errors, setErrors] = useState({});
  const [selectedRole, setSelectedRole] = useState(studentProfile?.userType || 'student');
  const [selectedGoals, setSelectedGoals] = useState(Array.isArray(studentProfile?.goals) ? studentProfile.goals : []);

  useEffect(() => {
    setPersonalLocal({
      fullName: studentProfile?.fullName || '',
      email: studentProfile?.email || '',
      category: studentProfile?.category || '',
      pwdCrossCategory: studentProfile?.pwdCrossCategory || false,
      phone: studentProfile?.phone || '',
      domicile: studentProfile?.domicile || '',
    });
    setSelectedRole(studentProfile?.userType || 'student');
    setSelectedGoals(Array.isArray(studentProfile?.goals) ? studentProfile.goals : []);
  }, [
    studentProfile?.fullName,
    studentProfile?.email,
    studentProfile?.category,
    studentProfile?.pwdCrossCategory,
    studentProfile?.phone,
    studentProfile?.domicile,
    studentProfile?.userType,
    studentProfile?.goals,
  ]);

  useEffect(() => {
    setAcademicLocal({
      exam: studentProfile?.academic?.exam || '',
      examScore: studentProfile?.academic?.examScore || '',
      careerOption: studentProfile?.academic?.careerOption || '',
      preferredBranch: studentProfile?.academic?.preferredBranch || '',
      educationLevel: studentProfile?.academic?.educationLevel || '',
      targetStream: studentProfile?.academic?.targetStream || '',
      subjects: Array.isArray(studentProfile?.academic?.subjects) ? studentProfile.academic.subjects : [],
      areasOfInterest: Array.isArray(studentProfile?.academic?.areasOfInterest) ? studentProfile.academic.areasOfInterest : [],
      targetDegreeLevel: studentProfile?.academic?.targetDegreeLevel || '',
      expectedEntranceScore: studentProfile?.academic?.expectedEntranceScore || '',
      scoreType: studentProfile?.academic?.scoreType || 'Percentage',
    });
  }, [
    studentProfile?.academic?.exam,
    studentProfile?.academic?.examScore,
    studentProfile?.academic?.careerOption,
    studentProfile?.academic?.preferredBranch,
    studentProfile?.academic?.educationLevel,
    studentProfile?.academic?.targetStream,
    studentProfile?.academic?.subjects,
    studentProfile?.academic?.areasOfInterest,
    studentProfile?.academic?.targetDegreeLevel,
    studentProfile?.academic?.expectedEntranceScore,
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
      next.examScore = 'Academic score is required';
    } else {
      const num = parseFloat(academic.examScore);
      if (isNaN(num) || num < 0) {
        next.examScore = 'Please enter a valid positive number';
      } else if (academic.scoreType === 'Percentage' && num > 100) {
        next.examScore = 'Percentage cannot exceed 100';
      } else if (academic.scoreType === 'CGPA' && num > 10) {
        next.examScore = 'CGPA cannot exceed 10';
      }
    }
    if (!academic.careerOption) next.careerOption = 'Please select a career option';
    if (!academic.preferredBranch) next.preferredBranch = 'Please select a branch';
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleAcademicScoreBlur = () => {
    if (academic.examScore) {
      let scoreError = null;
      const num = parseFloat(academic.examScore);
      if (isNaN(num) || num < 0) {
        scoreError = 'Please enter a valid positive number';
      } else if (academic.scoreType === 'Percentage' && num > 100) {
        scoreError = 'Percentage cannot exceed 100';
      } else if (academic.scoreType === 'CGPA' && num > 10) {
        scoreError = 'CGPA cannot exceed 10';
      }
      
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
    handlePersonalChange('category', cat);
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
    setAcademicLocal((prev) => {
      const next = { ...prev, [field]: value };
      if (field === 'exam') {
        next.careerOption = '';
        next.preferredBranch = '';
      }
      return next;
    });
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

  const toggleAcademicSubject = (subject) => {
    setAcademicLocal((prev) => {
      const current = Array.isArray(prev.subjects) ? prev.subjects : [];
      const next = current.includes(subject) ? [] : [subject];
      return { ...prev, subjects: next };
    });

    if (errors.subjects) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next.subjects;
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

  const validateFinalReview = () => {
    const missing = [];
    const domicileValue = studentProfile?.domicile || studentProfile?.stateOfDomicile || personal.domicile || '';
    const categoryValue = studentProfile?.category || studentProfile?.studentCategory || personal.category || '';

    if (!studentProfile.fullName) missing.push('Full Name');
    if (!studentProfile.email) missing.push('Email');
    if (!studentProfile.phone) missing.push('Phone');
    if (!domicileValue) missing.push('State of Domicile');
    if (!categoryValue) missing.push('Student Category');
    if (!studentProfile.academic?.exam) missing.push('Primary Exam');
    if (!studentProfile.academic?.examScore) missing.push('Exam Score');
    if (!studentProfile.academic?.careerOption) missing.push('Career Option');
    if (!studentProfile.academic?.preferredBranch) missing.push('Preferred Branch');
    if (!studentProfile.academic?.targetDegreeLevel) missing.push('Target Degree Level');
    return missing;
  };

  const toggleGoal = (goal) => {
    setSelectedGoals((prev) => {
      const next = prev.includes(goal) ? prev.filter((item) => item !== goal) : [...prev, goal];
      return next;
    });
  };

  const toggleAreasOfInterest = (area) => {
    setAcademicLocal((prev) => {
      const current = Array.isArray(prev.areasOfInterest) ? prev.areasOfInterest : [];
      const next = current.includes(area) ? [] : [area];
      return { ...prev, areasOfInterest: next };
    });
    if (errors.areasOfInterest) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next.areasOfInterest;
        return next;
      });
    }
  };

  const validateStepOne = () => {
    const next = {};
    if (!selectedRole) next.role = 'Please select an option';
    if (!selectedGoals.length) next.goals = 'Please select at least one goal';
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const getDomicileValue = () => studentProfile?.domicile || studentProfile?.stateOfDomicile || personal.domicile || '';
  const getCategoryValue = () => studentProfile?.category || studentProfile?.studentCategory || personal.category || '';

  const handleContinue = async () => {
    if (activeStep === 1) {
      if (!validateStepOne()) {
        toast.error(selectedGoals.length ? 'Please select your role.' : 'Please select at least one goal.');
        return;
      }
      setPersonal({
        fullName: personal.fullName.trim(),
        email: personal.email.trim(),
        category: personal.category,
        pwdCrossCategory: personal.pwdCrossCategory,
        phone: personal.phone.trim(),
        domicile: personal.domicile,
        userType: selectedRole,
        goals: selectedGoals,
      });
      nextStep();
      return;
    }

    if (activeStep === 2) {
      const next = {};
      if (!academic.educationLevel) next.educationLevel = 'Please select your current education level';
      if (!academic.targetStream) next.targetStream = 'Please select your target stream';
      
      if (!academic.examScore.trim()) {
        next.examScore = 'Academic score is required';
      } else {
        const num = parseFloat(academic.examScore);
        if (isNaN(num) || num < 0) {
          next.examScore = 'Please enter a valid positive number';
        } else if (academic.scoreType === 'Percentage' && num > 100) {
          next.examScore = 'Percentage cannot exceed 100';
        } else if (academic.scoreType === 'CGPA' && num > 10) {
          next.examScore = 'CGPA cannot exceed 10';
        }
      }

      if (!academic.subjects || academic.subjects.length === 0) next.subjects = 'Please select at least one subject';
      if (!personal.domicile) next.domicile = 'State of Domicile is required';
      if (!personal.category) next.category = 'Please select a Student Category';
      setErrors(next);

      if (Object.keys(next).length > 0) {
        toast.error(Object.values(next)[0]);
        return;
      }

      const derivedExam = academic.exam || academic.educationLevel || 'Academic Background';
      const derivedCareerOption = academic.careerOption || (academic.targetStream ? 'General' : '');
      const derivedBranch = academic.preferredBranch || academic.targetStream || '';

      setPersonal({
        fullName: personal.fullName.trim(),
        email: personal.email.trim(),
        category: personal.category,
        pwdCrossCategory: personal.pwdCrossCategory,
        phone: personal.phone.trim(),
        domicile: personal.domicile,
        userType: selectedRole,
        goals: selectedGoals,
      });

      setAcademic({
        exam: derivedExam,
        examScore: academic.examScore.trim(),
        careerOption: derivedCareerOption,
        preferredBranch: derivedBranch.trim(),
        educationLevel: academic.educationLevel,
        targetStream: academic.targetStream,
        subjects: academic.subjects,
        scoreType: academic.scoreType,
      });
      nextStep();
      return;
    }

    if (activeStep === 3) {
      const step3Errors = {};
      if (!academic.targetDegreeLevel) {
        step3Errors.targetDegreeLevel = 'Please select your target degree level';
      }
      
      if (academic.expectedEntranceScore.trim()) {
        const num = parseFloat(academic.expectedEntranceScore);
        if (isNaN(num) || num < 0 || num > 100) {
          step3Errors.expectedEntranceScore = 'Please enter a valid percentage/percentile between 0 and 100';
        }
      }

      setErrors(step3Errors);
      if (Object.keys(step3Errors).length > 0) {
        toast.error(Object.values(step3Errors)[0] || 'Please fix the errors to continue');
        return;
      }

      const derivedExam = academic.exam || academic.educationLevel || 'Academic Background';
      const derivedCareerOption = academic.careerOption || (academic.targetStream ? 'General' : '');
      const derivedBranch = academic.preferredBranch || academic.targetStream || '';

      setAcademic({
        exam: derivedExam,
        examScore: academic.examScore.trim(),
        careerOption: derivedCareerOption,
        preferredBranch: derivedBranch.trim(),
        educationLevel: academic.educationLevel,
        targetStream: academic.targetStream,
        subjects: academic.subjects,
        areasOfInterest: academic.areasOfInterest,
        targetDegreeLevel: academic.targetDegreeLevel,
        expectedEntranceScore: academic.expectedEntranceScore.trim(),
        scoreType: academic.scoreType,
      });

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
      const missingFields = validateFinalReview();
      if (missingFields.length > 0) {
        toast.error(`Please complete: ${missingFields.join(', ')}`);
        setErrors((prev) => ({ ...prev, finalReview: missingFields }));
        return;
      }

      try {
        const pendingRaw = sessionStorage.getItem(SIGNUP_PENDING_KEY);
        const pendingCreds = pendingRaw ? JSON.parse(pendingRaw) : {};

        const domicileValue = getDomicileValue();
        const categoryValue = getCategoryValue();

        const completePayload = {
          name: studentProfile.fullName,
          fullName: studentProfile.fullName,
          email: studentProfile.email,
          phone: studentProfile.phone,
          password: pendingCreds.password,
          userType: 'student',
          category: categoryValue,
          studentCategory: categoryValue,
          pwdCrossCategory: studentProfile.pwdCrossCategory,
          domicile: domicileValue,
          stateOfDomicile: domicileValue,
          locationZone: domicileValue,
          exam: studentProfile.academic?.exam,
          examScore: studentProfile.academic?.examScore,
          scoreType: studentProfile.academic?.scoreType,
          careerOption: studentProfile.academic?.careerOption,
          preferredBranch: studentProfile.academic?.preferredBranch,
          preferredLocation: studentProfile.preferences?.preferredLocation,
          budgetRange: studentProfile.preferences?.budgetRange,
          collegeType: studentProfile.preferences?.collegeType,
          hostelRequired: studentProfile.preferences?.hostelRequired,
        };

        sessionStorage.setItem('signup_complete_payload', JSON.stringify(completePayload));
        sessionStorage.setItem('auth_pending_user', JSON.stringify({
          name: completePayload.name,
          email: completePayload.email,
          phone: completePayload.phone,
        }));
        sessionStorage.setItem('auth_pending_phone', completePayload.phone);
        sessionStorage.setItem('signup_from_onboarding', 'true');

        const otpResponse = await sendOtp({
          name: completePayload.name,
          email: completePayload.email,
          phone: completePayload.phone,
        });

        if (otpResponse?.sessionId) {
          sessionStorage.setItem('auth_pending_otp_session_id', otpResponse.sessionId);
        }

        if (otpResponse?.dev_otp) {
          toast.success(`OTP sent. Dev OTP: ${otpResponse.dev_otp}`);
        } else {
          toast.success('OTP sent to your phone number.');
        }

        navigate('/otp', { replace: true });
      } catch (error) {
        const detail = error?.response?.data?.detail || error?.response?.data?.message || error?.message || 'Failed to send OTP. Please try again.';
        toast.error(detail);
      }
    }
  };

  const getButtonText = () => {
    if (activeStep === 1) return 'Continue';
    if (activeStep === 2) return 'Continue';
    if (activeStep === 3) return 'Continue';
    return 'Create Account & Analyze';
  };

  const handleBack = () => {
    setErrors({});
    prevStep();
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

  const renderStepOneProgress = () => (
    <div className="onboarding-progress-wrap onboarding-progress-wrap-step-one">
      <div className="onboarding-step-label">Step 1 of 4</div>
      <div className="onboarding-progress onboarding-progress-simple" aria-label="Progress 1 of 4">
        {steps.map((_, index) => {
          const stepNumber = index + 1;
          const isActive = stepNumber === 1;
          return (
            <span
              key={`step-one-${stepNumber}`}
              className={`progress-segment ${isActive ? 'active' : ''}`}
              aria-hidden="true"
            />
          );
        })}
      </div>
    </div>
  );

  const renderStepTwoProgress = () => (
    <div className="onboarding-progress-wrap onboarding-progress-wrap-step-two" aria-label="Progress 2 of 4">
      <div className="step-two-dots-progress">
        <div className="step-two-dot step-two-dot-done" aria-hidden="true"></div>
        <div className="step-two-line step-two-line-done" aria-hidden="true"></div>
        <div className="step-two-dot step-two-dot-active" aria-hidden="true"></div>
        <div className="step-two-line step-two-line-inactive" aria-hidden="true"></div>
        <div className="step-two-dot step-two-dot-inactive" aria-hidden="true"></div>
        <div className="step-two-line step-two-line-inactive" aria-hidden="true"></div>
        <div className="step-two-dot step-two-dot-inactive" aria-hidden="true"></div>
      </div>
    </div>
  );

  const filteredCareerOptions = useMemo(() => {
    if (!academic.exam) return CAREER_OPTIONS;
    if (['JEE Main', 'JEE Advanced', 'MHT-CET', 'Diploma'].includes(academic.exam)) return ['Engineering', 'Architecture', 'Other'];
    if (academic.exam === 'NEET') return ['Medical', 'Other'];
    if (academic.exam.includes('Pharm')) return ['Pharmacy', 'Medical', 'Other'];
    return CAREER_OPTIONS;
  }, [academic.exam]);

  const filteredBranches = useMemo(() => {
    if (!academic.exam || !EXAM_CONFIG[academic.exam]) return STANDARD_BRANCHES;
    return EXAM_CONFIG[academic.exam].courses;
  }, [academic.exam]);

  const progress = (activeStep / steps.length) * 100;

  return (
    <div className={`onboarding-wrapper ${activeStep === 4 ? 'onboarding-wrapper-step-four' : ''}`}>
      {activeStep !== 4 && (
        <header className={`onboarding-brand-header ${activeStep === 4 ? 'onboarding-brand-header-summary' : ''}`}>
          <div className={`onboarding-brand-center ${activeStep === 4 ? 'onboarding-brand-center-summary' : ''}`}>
            <span className="material-symbols-outlined onboarding-brand-icon">school</span>
            {activeStep !== 4 && <span className="onboarding-brand-name">Cutoff Guide AI</span>}
          </div>
        </header>
      )}

      <section className={`onboarding-main-shell ${activeStep === 4 ? 'onboarding-main-shell-step-four' : ''}`}>
        {activeStep === 4 ? null : activeStep === 1 ? (
          renderStepOneProgress()
        ) : activeStep === 2 ? (
          renderStepTwoProgress()
        ) : activeStep === 3 ? null : (
          <div className="onboarding-progress-wrap">
            <div className="onboarding-step-label">STEP {activeStep} OF {steps.length}</div>
            <div className="onboarding-progress" aria-label={`Progress ${activeStep} of ${steps.length}`}>
              {renderStepIndicator()}
            </div>
          </div>
        )}

        {activeStep !== 4 && (
          <div className="form-card onboarding-step-card">
            <form className="personal-form" onSubmit={(e) => e.preventDefault()}>
            {activeStep === 1 && (
              <>
                <div className="onboarding-intro onboarding-step-one-intro">
                  <h1 className="onboarding-page-heading">Let's personalize your journey</h1>
                  <p className="onboarding-page-subheading">
                    Tell us a bit about yourself so we can tailor the academic data to your specific needs.
                  </p>
                </div>

                <div className="onboarding-question-block">
                  <h2 className="onboarding-question-label">I am a...</h2>
                  <div className="user-type-grid">
                    {ROLE_OPTIONS.map((option) => {
                      const isSelected = selectedRole === option.value;
                      return (
                        <label key={option.value} className={`user-type-option ${isSelected ? 'selected' : ''}`}>
                          <input
                            type="radio"
                            name="user-role"
                            value={option.value}
                            checked={isSelected}
                            onChange={() => setSelectedRole(option.value)}
                            className="sr-only-radio"
                          />
                          <div className="user-type-card" aria-pressed={isSelected}>
                            <div className="user-type-icon-wrap">
                              <span className="material-symbols-outlined user-type-icon">{option.icon}</span>
                            </div>
                            <div className="user-type-copy">
                              <span className="user-type-title">{option.label}</span>
                              <span className="user-type-description">{option.description}</span>
                            </div>
                          </div>
                        </label>
                      );
                    })}
                  </div>
                </div>

                <div className="onboarding-goal-block">
                  <div className="onboarding-goal-header">
                    <h2 className="onboarding-question-label">What is your primary goal?</h2>
                    <div className="onboarding-goal-subtext">Select all that apply.</div>
                  </div>
                  <div className="goal-chip-group">
                    {GOAL_OPTIONS.map((goal) => {
                      const isSelected = selectedGoals.includes(goal);
                      return (
                        <button
                          type="button"
                          key={goal}
                          className={`goal-chip ${isSelected ? 'selected' : ''}`}
                          onClick={() => toggleGoal(goal)}
                          aria-pressed={isSelected}
                        >
                          {goal}
                        </button>
                      );
                    })}
                  </div>
                  {errors.goals && <div className="field-error-text onboarding-error">{errors.goals}</div>}
                </div>
              </>
            )}

            {activeStep === 2 && (
              <>
                <div className="step-two-hero">
                  <h1 className="step-two-heading">Academic Background</h1>
                  <p className="step-two-subheading">
                    Help us tailor your cutoff predictions by detailing your educational history.
                  </p>
                </div>

                <div className="step-two-form">
                  <div className="step-two-grid">
                    <div className="step-two-form-field">
                      <label className="step-two-label" htmlFor="educationLevel">Current Education Level</label>
                      <div className="step-two-select-wrap">
                        <select
                          id="educationLevel"
                          name="educationLevel"
                          value={academic.educationLevel}
                          onChange={(e) => handleAcademicChange('educationLevel', e.target.value)}
                          className={`step-two-select ${errors.educationLevel ? 'step-two-field-error' : ''}`}
                        >
                          <option value="" disabled>Select level</option>
                          {EDUCATION_LEVEL_OPTIONS.map((level) => (
                            <option key={level} value={level}>{level}</option>
                          ))}
                        </select>
                        <span className="material-symbols-outlined step-two-select-caret">expand_more</span>
                      </div>
                      {errors.educationLevel && <div className="field-error-text">{errors.educationLevel}</div>}
                    </div>

                    <div className="step-two-form-field">
                      <label className="step-two-label" htmlFor="targetStream">Target Stream</label>
                      <div className="step-two-select-wrap">
                        <select
                          id="targetStream"
                          name="targetStream"
                          value={academic.targetStream}
                          onChange={(e) => handleAcademicChange('targetStream', e.target.value)}
                          className={`step-two-select ${errors.targetStream ? 'step-two-field-error' : ''}`}
                        >
                          <option value="" disabled>Select stream</option>
                          {TARGET_STREAM_OPTIONS.map((stream) => (
                            <option key={stream} value={stream}>{stream}</option>
                          ))}
                        </select>
                        <span className="material-symbols-outlined step-two-select-caret">expand_more</span>
                      </div>
                      {errors.targetStream && <div className="field-error-text">{errors.targetStream}</div>}
                    </div>
                  </div>

                  <div className="step-two-form-field step-two-full">
                    <label className="step-two-label" htmlFor="examScore">Most Recent Academic Score</label>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                      <div className="step-two-select-wrap" style={{ width: '140px' }}>
                        <select
                          value={academic.scoreType}
                          onChange={(e) => handleAcademicChange('scoreType', e.target.value)}
                          className="step-two-select"
                        >
                          <option value="Percentage">Percentage</option>
                          <option value="CGPA">CGPA</option>
                        </select>
                        <span className="material-symbols-outlined step-two-select-caret">expand_more</span>
                      </div>
                      <input
                        type="text"
                        id="examScore"
                        value={academic.examScore}
                        onChange={(e) => handleAcademicChange('examScore', e.target.value)}
                        onBlur={handleAcademicScoreBlur}
                        placeholder={academic.scoreType === 'CGPA' ? "e.g., 8.5" : "e.g., 92"}
                        className={`step-two-input ${errors.examScore ? 'step-two-field-error' : ''}`}
                        style={{ flex: 1 }}
                      />
                    </div>
                    <p className="step-two-hint">This helps us gauge baseline eligibility.</p>
                    {errors.examScore && <div className="field-error-text">{errors.examScore}</div>}
                  </div>

                  <div className="step-two-form-field step-two-full">
                    <label className="step-two-label" htmlFor="domicile">State of Domicile</label>
                    <div className="step-two-select-wrap">
                      <select
                        id="domicile"
                        name="domicile"
                        value={personal.domicile}
                        onChange={(e) => handlePersonalChange('domicile', e.target.value)}
                        className={`step-two-select ${errors.domicile ? 'step-two-field-error' : ''}`}
                      >
                        <option value="" disabled>Select your state</option>
                        {INDIAN_STATES.map((state) => (
                          <option key={state} value={state}>{state}</option>
                        ))}
                      </select>
                      <span className="material-symbols-outlined step-two-select-caret">expand_more</span>
                    </div>
                    {errors.domicile && <div className="field-error-text">{errors.domicile}</div>}
                  </div>

                  <div className="step-two-form-field step-two-full">
                    <label className="step-two-label">Student Category</label>
                    <div className="step-two-chips">
                      {['General', 'OBC', 'SC', 'ST', 'EWS', 'PWD', 'Defence/Ex-Servicemen', 'Minority', 'Kashmiri Migrant'].map((option) => {
                        const selected = (personal.category || '').trim() === option;
                        return (
                          <button
                            key={option}
                            type="button"
                            className={`step-two-chip ${selected ? 'selected' : ''}`}
                            onClick={() => toggleCategory(option)}
                            aria-pressed={selected}
                          >
                            {option}
                            <span className="material-symbols-outlined step-two-chip-icon">
                              {selected ? 'close' : 'add'}
                            </span>
                          </button>
                        );
                      })}
                    </div>
                    {errors.category && <div className="field-error-text">{errors.category}</div>}
                  </div>

                  <div className="step-two-form-field step-two-full">
                    <label className="step-two-label">Key Subjects / Strengths</label>
                    <div className="step-two-chips">
                      {SUBJECT_OPTIONS.map((subject) => {
                        const selected = academic.subjects.includes(subject);
                        return (
                          <button
                            key={subject}
                            type="button"
                            className={`step-two-chip ${selected ? 'selected' : ''}`}
                            onClick={() => toggleAcademicSubject(subject)}
                            aria-pressed={selected}
                          >
                            {subject}
                            <span className="material-symbols-outlined step-two-chip-icon">
                              {selected ? 'close' : 'add'}
                            </span>
                          </button>
                        );
                      })}
                      <button type="button" className="step-two-chip step-two-chip-custom" onClick={() => {}}>
                        <span className="material-symbols-outlined step-two-chip-icon">search</span>
                        Add Custom Subject
                      </button>
                    </div>
                    {errors.subjects && <div className="field-error-text">{errors.subjects}</div>}
                  </div>
                </div>

                <div className="step-two-divider" aria-hidden="true"></div>

                <div className="step-two-cta">
                  <button className="step-two-back-btn" type="button" onClick={handleBack}>
                    <span className="material-symbols-outlined button-icon">arrow_back</span>
                    Back
                  </button>
                  <button className="step-two-continue-btn" onClick={handleContinue} type="button">
                    Continue
                    <span className="material-symbols-outlined button-icon">arrow_forward</span>
                  </button>
                </div>
              </>
            )}

            {activeStep === 3 && (
              <div className="step-three-shell">
                <div className="step-three-progress-header">
                  <div className="step-three-progress-row">
                    <span className="material-symbols-outlined step-three-progress-icon fill">school</span>
                    <span className="step-three-step-kicker">STEP 3 OF 4</span>
                  </div>
                  <div className="step-three-progress-bar" aria-label="Progress 3 of 4">
                    <span className="step-three-progress-fill" />
                  </div>
                </div>

                <div className="step-three-main-content">
                  <header className="step-three-hero">
                    <h1 className="step-three-title">Refine Your Focus</h1>
                    <p className="step-three-subtitle">
                      Select the academic disciplines and degree levels you are targeting. This helps us filter relevant cutoff data.
                    </p>
                  </header>

                  <div className="step-three-form-stack">
                    <section className="step-three-section">
                      <h2 className="step-three-section-heading">
                        <span className="material-symbols-outlined step-three-section-icon">category</span>
                        Areas of Interest
                      </h2>
                      <div className="step-three-chips">
                        {AREA_OF_INTEREST_OPTIONS.map((area) => {
                          const isSelected = academic.areasOfInterest.includes(area);
                          return (
                            <button
                              type="button"
                              key={area}
                              className={`step-three-chip ${isSelected ? 'selected' : ''}`}
                              onClick={() => toggleAreasOfInterest(area)}
                              aria-pressed={isSelected}
                            >
                              {area}
                            </button>
                          );
                        })}
                      </div>
                    </section>

                    <div className="step-three-divider" aria-hidden="true"></div>

                    <section className="step-three-section">
                      <h2 className="step-three-section-heading">
                        <span className="material-symbols-outlined step-three-section-icon">workspace_premium</span>
                        Target Degree Level
                      </h2>
                      <div className="step-three-degree-grid">
                        {DEGREE_LEVEL_OPTIONS.map((option) => {
                          const isSelected = academic.targetDegreeLevel === option.value;
                          return (
                            <button
                              type="button"
                              key={option.value}
                              className={`step-three-degree-card ${isSelected ? 'selected' : ''}`}
                              onClick={() => handleAcademicChange('targetDegreeLevel', option.value)}
                              aria-pressed={isSelected}
                            >
                              <span className="material-symbols-outlined step-three-degree-icon">
                                {option.icon}
                              </span>
                              <div className="step-three-degree-copy">
                                <span className="step-three-degree-title">{option.label}</span>
                                <span className="step-three-degree-description">{option.description}</span>
                              </div>
                            </button>
                          );
                        })}
                      </div>
                      {errors.targetDegreeLevel && (
                        <div className="field-error-text">{errors.targetDegreeLevel}</div>
                      )}
                    </section>

                    <section className="step-three-section step-three-input-section">
                      <h2 className="step-three-section-heading">
                        <span className="material-symbols-outlined step-three-section-icon">analytics</span>
                        Expected Entrance Score (Optional)
                      </h2>
                      <input
                        type="text"
                        className={`step-three-input ${errors.expectedEntranceScore ? 'step-two-field-error' : ''}`}
                        placeholder="e.g., 95.5 percentile"
                        value={academic.expectedEntranceScore}
                        onChange={(e) => handleAcademicChange('expectedEntranceScore', e.target.value)}
                      />
                      {errors.expectedEntranceScore && (
                        <div className="field-error-text" style={{marginTop: '0.5rem'}}>{errors.expectedEntranceScore}</div>
                      )}
                    </section>
                  </div>
                </div>

                <div className="step-three-action-footer">
                  <button
                    type="button"
                    className="step-three-back-btn"
                    onClick={handleBack}
                  >
                    Back
                  </button>
                  <button
                    type="button"
                    className="step-three-continue-btn"
                    onClick={handleContinue}
                  >
                    Continue
                    <span className="material-symbols-outlined button-icon">arrow_forward</span>
                  </button>
                </div>
              </div>
            )}

            {activeStep === 4 && null}
          </form>
        </div>
        )}

        {activeStep === 1 ? (
          <>
            <div className="bottom-action onboarding-step-one-cta">
              <button className="continue-button" onClick={handleContinue} type="button">
                Continue
                <span className="material-symbols-outlined button-icon">arrow_forward</span>
              </button>
            </div>
            <div className="onboarding-login-link">
              Already have an account? <button type="button" className="onboarding-login-button" onClick={() => navigate('/login')}>Log in</button>
            </div>
          </>
        ) : activeStep === 3 ? null : activeStep === 2 ? null : null}
      </section>

      {activeStep === 4 && (
        <div className="step-four-shell">
          <div className="step-four-ambient step-four-ambient-1" aria-hidden="true"></div>
          <div className="step-four-ambient step-four-ambient-2" aria-hidden="true"></div>

          <header className="step-four-header">
            <button
              type="button"
              className="step-four-back-btn"
              onClick={handleBack}
              aria-label="Go back to Step 3"
            >
              <span className="material-symbols-outlined step-four-back-icon">arrow_back</span>
            </button>
            <div className="step-four-brand">
              <span className="material-symbols-outlined step-four-brand-icon fill">school</span>
              <span className="step-four-brand-name">Cutoff Guide AI</span>
            </div>
            <div className="step-four-header-spacer" aria-hidden="true"></div>
          </header>

          <div className="step-four-progress-wrap" aria-label="Progress 4 of 4">
            <div className="step-four-progress-row">
              <span className="step-four-progress-label">STEP 4 OF 4</span>
              <span className="step-four-progress-label step-four-progress-label-right">FINAL REVIEW</span>
            </div>
            <div className="step-four-progress-bar" aria-hidden="true">
              {[0, 1, 2, 3].map((seg) => (
                <span
                  key={`step-four-seg-${seg}`}
                  className={`step-four-progress-segment ${seg === 3 ? 'step-four-progress-segment-last' : ''}`}
                />
              ))}
            </div>
          </div>

          <header className="step-four-hero">
            <h1 className="step-four-hero-title">Ready to optimize your future?</h1>
            <p className="step-four-hero-subtitle">
              Please review your academic profile. Ensuring this data is accurate helps our AI model calculate your most viable cutoff strategies.
            </p>
          </header>

          <div className="step-four-summary-grid">
            <article className="step-four-card step-four-card-identity">
              <div className="step-four-card-header">
                <div className="step-four-card-title-wrap">
                  <span className="material-symbols-outlined step-four-card-icon">person</span>
                  <h2 className="step-four-card-title">Identity</h2>
                </div>
                <button
                  type="button"
                  className="step-four-card-edit"
                  onClick={() => goToStep(1)}
                  aria-label="Edit Identity"
                >
                  <span className="material-symbols-outlined">edit</span>
                </button>
              </div>

              <div className="step-four-card-divider" aria-hidden="true"></div>

              <div className="step-four-value-group">
                <div className="step-four-value-block">
                  <span className="step-four-value-label">FULL NAME</span>
                  <span className="step-four-value-text">{studentProfile.fullName || 'Not provided'}</span>
                </div>
                <div className="step-four-value-block">
                  <span className="step-four-value-label">CONTACT</span>
                  <span className="step-four-value-text">{studentProfile.email || studentProfile.phone || 'Not provided'}</span>
                </div>
                <div className="step-four-value-block">
                  <span className="step-four-value-label">LOCATION ZONE</span>
                  <span className="step-four-value-text">{studentProfile.domicile || 'Not provided'}</span>
                </div>
              </div>
            </article>

            <article className="step-four-card step-four-card-academic">
              <div className="step-four-card-header">
                <div className="step-four-card-title-wrap">
                  <span className="material-symbols-outlined step-four-card-icon">menu_book</span>
                  <h2 className="step-four-card-title">Academic Baseline</h2>
                </div>
                <button
                  type="button"
                  className="step-four-card-edit"
                  onClick={() => goToStep(2)}
                  aria-label="Edit Academic Baseline"
                >
                  <span className="material-symbols-outlined">edit</span>
                </button>
              </div>

              <div className="step-four-card-divider" aria-hidden="true"></div>

              <div className="step-four-value-group">
                <div className="step-four-value-block">
                  <span className="step-four-value-label">CURRENT LEVEL</span>
                  <span className="step-four-value-text">
                    {studentProfile.academic?.educationLevel ||
                      studentProfile.academic?.preferredBranch ||
                      studentProfile.academic?.careerOption ||
                      'Not provided'}
                  </span>
                </div>
                <div className="step-four-value-block">
                  <span className="step-four-value-label">CURRENT GPA (EST.)</span>
                  <span className="step-four-value-text">{studentProfile.academic?.examScore || 'Not provided'}</span>
                </div>
                <div className="step-four-value-block">
                  <span className="step-four-value-label">TARGET FIELD</span>
                  <div className="step-four-pill-row">
                    {Array.isArray(studentProfile.academic?.areasOfInterest) &&
                    studentProfile.academic.areasOfInterest.length > 0 ? (
                      studentProfile.academic.areasOfInterest.map((field, i) => (
                        <span
                          key={`${field}-${i}`}
                          className={`step-four-pill ${i === 0 ? 'step-four-pill-primary' : ''}`}
                        >
                          {field}
                        </span>
                      ))
                    ) : studentProfile.academic?.careerOption ||
                      studentProfile.academic?.preferredBranch ||
                      studentProfile.academic?.targetStream ? (
                      <>
                        {studentProfile.academic?.careerOption && (
                          <span className="step-four-pill step-four-pill-primary">
                            {studentProfile.academic.careerOption}
                          </span>
                        )}
                        {studentProfile.academic?.preferredBranch &&
                        studentProfile.academic.preferredBranch !== studentProfile.academic?.careerOption && (
                          <span className="step-four-pill">
                            {studentProfile.academic.preferredBranch}
                          </span>
                        )}
                        {studentProfile.academic?.targetStream &&
                        studentProfile.academic.targetStream !== studentProfile.academic?.careerOption &&
                        studentProfile.academic.targetStream !== studentProfile.academic?.preferredBranch && (
                          <span className="step-four-pill">
                            {studentProfile.academic.targetStream}
                          </span>
                        )}
                      </>
                    ) : (
                      <span className="step-four-value-text">Not provided</span>
                    )}
                  </div>
                </div>
              </div>
            </article>

            <article className="step-four-card step-four-card-parameters">
              <div className="step-four-card-header">
                <div className="step-four-card-title-wrap">
                  <span className="material-symbols-outlined step-four-card-icon">flag</span>
                  <h2 className="step-four-card-title">Cutoff Parameters</h2>
                </div>
                <button
                  type="button"
                  className="step-four-card-edit"
                  onClick={() => goToStep(3)}
                  aria-label="Edit Cutoff Parameters"
                >
                  <span className="material-symbols-outlined">edit</span>
                </button>
              </div>

              <div className="step-four-card-divider" aria-hidden="true"></div>

              <div className="step-four-params-grid">
                <div className="step-four-value-block">
                  <span className="step-four-value-label">PRIMARY EXAM TARGET</span>
                  <span className="step-four-value-text">
                    {studentProfile.academic?.exam ||
                      studentProfile.academic?.targetStream ||
                      studentProfile.academic?.educationLevel ||
                      'Not provided'}
                  </span>
                </div>

                <div className="step-four-value-block">
                  <span className="step-four-value-label">CONFIDENCE INTERVAL</span>
                  <div className="step-four-confidence-line">
                    <span className="step-four-confidence-label">
                      {studentProfile.academic?.examScore ? 'High' : 'Not provided'}
                    </span>
                    {studentProfile.academic?.examScore && (
                      <div className="step-four-confidence-bars" aria-hidden="true">
                        {[0, 1, 2].map((bar) => (
                          <span key={`conf-${bar}`} className="step-four-confidence-bar" />
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div className="step-four-value-block">
                  <span className="step-four-value-label">INSTITUTIONAL SCOPE</span>
                  <span className="step-four-value-text">
                    {studentProfile.preferences?.preferredLocation ||
                      studentProfile.preferences?.collegeType ||
                      studentProfile.domicile ||
                      'Not provided'}
                  </span>
                </div>
              </div>
            </article>
          </div>

          <div className="step-four-cta">
            <button
              type="button"
              className="step-four-create-btn"
              onClick={handleContinue}
            >
              <span className="material-symbols-outlined step-four-create-icon fill">arrow_forward</span>
              {getButtonText()}
            </button>
            <p className="step-four-terms">
              By creating an account, you agree to our{' '}
              <button
                type="button"
                className="step-four-terms-link"
                onClick={() => navigate('/terms')}
              >
                Terms of Service
              </button>{' '}
              and{' '}
              <button
                type="button"
                className="step-four-terms-link"
                onClick={() => navigate('/privacy')}
              >
                Privacy Policy
              </button>
              .
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Onboarding;
