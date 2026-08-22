import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useOnboarding } from '../../context/OnboardingContext';
import { useAuth } from '../../context/AuthContext';
import { registerUser, sendOtp, updateProfile } from '../../services/api';
import './Onboarding.css';

const SIGNUP_PENDING_KEY = 'signup_pending_credentials';

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
    prevStep,
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
    userType: studentProfile?.userType || 'student',
    goals: studentProfile?.goals || [],
    category: studentProfile?.category || '',
    pwdCrossCategory: studentProfile?.pwdCrossCategory || false,
    phone: studentProfile?.phone || '',
    domicile: studentProfile?.domicile || '',
  });

  const defaultAcademicSubjects = ['Mathematics', 'Physics', 'Computer Science', 'Chemistry'];
  const step3AreasOfInterest = ['Computer Science', 'Engineering', 'Business Admin', 'Data Science', 'Mathematics', 'Biology', 'Economics'];

  const [academic, setAcademicLocal] = useState({
    exam: studentProfile?.academic?.exam || '',
    examScore: studentProfile?.academic?.examScore || '',
    careerOption: studentProfile?.academic?.careerOption || '',
    preferredBranch: studentProfile?.academic?.preferredBranch || '',
    educationLevel: studentProfile?.academic?.educationLevel || '',
    targetStream: studentProfile?.academic?.targetStream || '',
    subjects: Array.isArray(studentProfile?.academic?.subjects)
      ? studentProfile.academic.subjects
      : defaultAcademicSubjects.filter(() => false),
    areasOfInterest: Array.isArray(studentProfile?.academic?.areasOfInterest)
      ? studentProfile.academic.areasOfInterest
      : [],
    targetDegreeLevel: studentProfile?.academic?.targetDegreeLevel || '',
    expectedEntranceScore: studentProfile?.academic?.expectedEntranceScore || '',
  });

  const [customSubjectInput, setCustomSubjectInput] = useState('');
  const [showCustomSubjectInput, setShowCustomSubjectInput] = useState(false);

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
    if (!isSignup) return;
    try {
      const raw = sessionStorage.getItem(SIGNUP_PENDING_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed.password) setPassword(parsed.password);
        if (parsed.confirmPassword) setConfirmPassword(parsed.confirmPassword);
        if (parsed.email || parsed.phone || parsed.fullName || parsed.domicile || parsed.name || parsed.locationZone) {
          setPersonalLocal((prev) => ({
            ...prev,
            fullName: parsed.fullName || parsed.name || prev.fullName || '',
            email: parsed.email || prev.email || '',
            phone: parsed.phone || prev.phone || '',
            domicile: parsed.domicile || parsed.locationZone || prev.domicile || '',
          }));
        }
      }
    } catch (e) {
      /* ignore */
    }
  }, [isSignup]);

  useEffect(() => {
    setPersonalLocal({
      fullName: studentProfile?.fullName || '',
      email: studentProfile?.email || '',
      userType: studentProfile?.userType || 'student',
      goals: studentProfile?.goals || [],
      category: studentProfile?.category || '',
      pwdCrossCategory: studentProfile?.pwdCrossCategory || false,
      phone: studentProfile?.phone || '',
      domicile: studentProfile?.domicile || '',
    });
  }, [
    studentProfile?.fullName,
    studentProfile?.email,
    studentProfile?.userType,
    studentProfile?.goals,
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
      educationLevel: studentProfile?.academic?.educationLevel || '',
      targetStream: studentProfile?.academic?.targetStream || '',
      subjects: Array.isArray(studentProfile?.academic?.subjects)
        ? studentProfile.academic.subjects
        : [],
      areasOfInterest: Array.isArray(studentProfile?.academic?.areasOfInterest)
        ? studentProfile.academic.areasOfInterest
        : [],
      targetDegreeLevel: studentProfile?.academic?.targetDegreeLevel || '',
      expectedEntranceScore: studentProfile?.academic?.expectedEntranceScore || '',
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
    if (!personal.userType) next.userType = 'Please select an option';
    const trimmedFullName = String(personal.fullName || '').trim();
    if (!trimmedFullName) next.fullName = 'Please enter your full name';

    const trimmedEmail = String(personal.email || '').trim().toLowerCase();
    if (!trimmedEmail) {
      next.email = 'Please enter your email';
    } else if (!EMAIL_REGEX.test(trimmedEmail)) {
      next.email = 'Please enter a valid email address';
    }

    const normalizedPhone = String(personal.phone || '').replace(/\D/g, '');
    if (!normalizedPhone) {
      next.phone = 'Please enter your phone number';
    } else if (!/^\d{10}$/.test(normalizedPhone)) {
      next.phone = 'Please enter a valid 10-digit phone number';
    }

    if (!String(personal.domicile || '').trim()) {
      next.domicile = 'Please enter your location zone';
    }

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

  const validateAcademicBackground = () => {
    const next = {};
    if (!academic.educationLevel) next.educationLevel = 'Please select your current education level';
    if (!academic.targetStream) next.targetStream = 'Please select a target stream';
    if (!academic.exam) next.exam = 'Please select your primary exam target';

    const scoreValue = academic.examScore.trim();
    if (!scoreValue) {
      next.examScore = 'Academic score is required';
    } else {
      const numericScore = Number(scoreValue.replace(/%/g, ''));
      const isValidNumeric = !Number.isNaN(numericScore) && numericScore >= 0;
      const isValidPercent = scoreValue.includes('%') ? numericScore <= 100 : numericScore <= 10 || numericScore <= 100;
      if (!isValidNumeric || !isValidPercent) {
        next.examScore = 'Enter a valid score such as 8.5 or 92%';
      }
    }

    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const validateAcademicFocus = () => {
    const next = {};
    if (!academic.targetDegreeLevel) {
      next.targetDegreeLevel = 'Please select a target degree level';
    }
    if (academic.expectedEntranceScore) {
      const value = academic.expectedEntranceScore.trim();
      const matched = value.match(/^\d+(?:\.\d+)?\s*(?:percentile|%|score)?$/i);
      if (!matched) {
        next.expectedEntranceScore = 'Enter a valid score like 95.5 percentile';
      }
    }
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

  const toggleAcademicSubject = (subject) => {
    setAcademicLocal((prev) => ({
      ...prev,
      subjects: prev.subjects.includes(subject)
        ? prev.subjects.filter((item) => item !== subject)
        : [...prev.subjects, subject],
    }));
    if (errors.subjects) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next.subjects;
        return next;
      });
    }
  };

  const toggleAreaOfInterest = (area) => {
    setAcademicLocal((prev) => ({
      ...prev,
      areasOfInterest: prev.areasOfInterest.includes(area)
        ? prev.areasOfInterest.filter((item) => item !== area)
        : [...prev.areasOfInterest, area],
    }));
    if (errors.areasOfInterest) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next.areasOfInterest;
        return next;
      });
    }
  };

  const addCustomSubject = () => {
    const trimmed = customSubjectInput.trim();
    if (!trimmed) {
      setShowCustomSubjectInput(true);
      return;
    }

    const subject = trimmed.replace(/\s+/g, ' ');
    setAcademicLocal((prev) => {
      const alreadyExists = prev.subjects.includes(subject);
      return {
        ...prev,
        subjects: alreadyExists ? prev.subjects : [...prev.subjects, subject],
      };
    });
    setCustomSubjectInput('');
    setShowCustomSubjectInput(false);
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

  const handleUserTypeChange = (value) => {
    setPersonalLocal((prev) => ({ ...prev, userType: value }));
    if (errors.userType) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next.userType;
        return next;
      });
    }
  };

  const toggleGoal = (goalValue) => {
    const currentGoals = personal.goals || [];
    const nextGoals = currentGoals.includes(goalValue)
      ? currentGoals.filter((goal) => goal !== goalValue)
      : [...currentGoals, goalValue];

    setPersonalLocal((prev) => ({ ...prev, goals: nextGoals }));
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

  const resolveLatestProfile = () => {
    const personalState = {
      ...studentProfile,
      ...personal,
      name: String(personal.fullName || studentProfile?.fullName || studentProfile?.name || '').trim(),
      fullName: String(personal.fullName || studentProfile?.fullName || studentProfile?.name || '').trim(),
      email: String(personal.email || studentProfile?.email || '').trim().toLowerCase(),
      phone: String(personal.phone || studentProfile?.phone || '').replace(/\D/g, ''),
      domicile: String(personal.domicile || studentProfile?.domicile || studentProfile?.locationZone || '').trim(),
      locationZone: String(personal.domicile || studentProfile?.domicile || studentProfile?.locationZone || '').trim(),
    };

    const academicState = {
      ...(studentProfile?.academic || {}),
      ...academic,
      exam: String(academic.exam || studentProfile?.academic?.exam || studentProfile?.academic?.examTarget || '').trim(),
      examTarget: String(academic.exam || studentProfile?.academic?.exam || studentProfile?.academic?.examTarget || '').trim(),
      examScore: String(academic.examScore || studentProfile?.academic?.examScore || '').trim(),
      preferredBranch: String(academic.preferredBranch || studentProfile?.academic?.preferredBranch || '').trim(),
      targetDegreeLevel: String(academic.targetDegreeLevel || studentProfile?.academic?.targetDegreeLevel || '').trim(),
      expectedEntranceScore: String(academic.expectedEntranceScore || studentProfile?.academic?.expectedEntranceScore || '').trim(),
    };

    const preferencesState = {
      ...(studentProfile?.preferences || {}),
      ...preferences,
      preferredLocation: String(preferences.preferredLocation || studentProfile?.preferences?.preferredLocation || studentProfile?.locationZone || '').trim(),
      collegeType: String(preferences.collegeType || studentProfile?.preferences?.collegeType || '').trim(),
      budgetRange: String(preferences.budgetRange || studentProfile?.preferences?.budgetRange || '').trim(),
    };

    return {
      ...studentProfile,
      ...personalState,
      academic: academicState,
      preferences: preferencesState,
    };
  };

  const handleContinue = async () => {
    if (isSubmitting) return;

    if (activeStep === 1) {
      if (!validatePersonal()) {
        toast.error('Please select your profile type to continue.');
        return;
      }
      const nextProfile = resolveLatestProfile();
      setPersonal({
        ...nextProfile,
        fullName: String(nextProfile.fullName || '').trim(),
        email: String(nextProfile.email || '').trim(),
        userType: nextProfile.userType,
        goals: nextProfile.goals,
        category: nextProfile.category,
        pwdCrossCategory: nextProfile.pwdCrossCategory,
        phone: String(nextProfile.phone || '').trim(),
        domicile: String(nextProfile.domicile || '').trim(),
      });
      nextStep();
      return;
    }

    if (activeStep === 2) {
      if (!validateAcademicBackground()) {
        toast.error('Please complete all required fields');
        return;
      }
      const nextProfile = resolveLatestProfile();
      setAcademic({
        ...nextProfile.academic,
        exam: nextProfile.academic?.exam || '',
        examScore: String(nextProfile.academic?.examScore || '').trim(),
        careerOption: nextProfile.academic?.careerOption || '',
        preferredBranch: String(nextProfile.academic?.preferredBranch || '').trim(),
        educationLevel: nextProfile.academic?.educationLevel,
        targetStream: nextProfile.academic?.targetStream,
        subjects: nextProfile.academic?.subjects || [],
      });
      nextStep();
      return;
    }

    if (activeStep === 3) {
      if (!validateAcademicFocus()) {
        toast.error('Please complete all required fields');
        return;
      }
      const nextProfile = resolveLatestProfile();
      setAcademic({
        ...nextProfile.academic,
        exam: nextProfile.academic?.exam || '',
        examScore: String(nextProfile.academic?.examScore || '').trim(),
        careerOption: nextProfile.academic?.careerOption || '',
        preferredBranch: String(nextProfile.academic?.preferredBranch || '').trim(),
        educationLevel: nextProfile.academic?.educationLevel,
        targetStream: nextProfile.academic?.targetStream,
        subjects: nextProfile.academic?.subjects || [],
        areasOfInterest: nextProfile.academic?.areasOfInterest || [],
        targetDegreeLevel: nextProfile.academic?.targetDegreeLevel,
        expectedEntranceScore: String(nextProfile.academic?.expectedEntranceScore || '').trim(),
      });
      nextStep();
      return;
    }

    if (activeStep === 4) {
      const resolvedProfile = resolveLatestProfile();
      const requiredName = String(resolvedProfile?.fullName || resolvedProfile?.name || '').trim();
      const requiredEmail = String(resolvedProfile?.email || '').trim().toLowerCase();
      const requiredPhone = String(resolvedProfile?.phone || '').replace(/\D/g, '');
      const requiredDomicile = String(resolvedProfile?.domicile || resolvedProfile?.locationZone || '').trim();
      const requiredExam = String(resolvedProfile?.academic?.exam || resolvedProfile?.academic?.examTarget || '').trim();
      const requiredExamScore = String(resolvedProfile?.academic?.examScore || '').trim();
      const requiredPreferredLocation = String(resolvedProfile?.preferences?.preferredLocation || resolvedProfile?.locationZone || '').trim();

      if (isSignup) {
        if (!requiredName) {
          toast.error('Please enter your full name.');
          setErrors({ submit: 'Please enter your full name.' });
          return;
        }
        if (!requiredEmail) {
          toast.error('Please enter your email.');
          setErrors({ submit: 'Please enter your email.' });
          return;
        }
        if (!requiredPhone) {
          toast.error('Please enter your phone number.');
          setErrors({ submit: 'Please enter your phone number.' });
          return;
        }
        if (!requiredDomicile) {
          toast.error('Please enter your location zone.');
          setErrors({ submit: 'Please enter your location zone.' });
          return;
        }
        if (!requiredExam) {
          toast.error('Please select your primary exam target.');
          setErrors({ submit: 'Please select your primary exam target.' });
          return;
        }
        if (!requiredExamScore) {
          toast.error('Please enter your exam score.');
          setErrors({ submit: 'Please enter your exam score.' });
          return;
        }
        if (!requiredPreferredLocation) {
          toast.error('Please enter your preferred location.');
          setErrors({ submit: 'Please enter your preferred location.' });
          return;
        }
        if (!password || password.length < 8) {
          toast.error('Password must be at least 8 characters.');
          setErrors({ submit: 'Password must be at least 8 characters.' });
          return;
        }
        if (password !== confirmPassword) {
          toast.error('Passwords do not match.');
          setErrors({ submit: 'Passwords do not match.' });
          return;
        }
      }

      try {
        setIsSubmitting(true);
        setErrors((prev) => ({ ...prev, submit: '' }));

        if (isSignup) {
          const normalizedPhone = String(resolvedProfile?.phone || '').replace(/\D/g, '');
          const payload = {
            name: String(resolvedProfile?.fullName || resolvedProfile?.name || '').trim(),
            email: String(resolvedProfile?.email || '').trim().toLowerCase(),
            phone: normalizedPhone,
            password,
            userType: String(resolvedProfile?.userType || '').trim() || undefined,
            goals: Array.isArray(resolvedProfile?.goals) && resolvedProfile.goals.length
              ? resolvedProfile.goals
              : undefined,
            category: String(resolvedProfile?.category || '').trim() || undefined,
            pwdCrossCategory: typeof resolvedProfile?.pwdCrossCategory === 'boolean'
              ? resolvedProfile.pwdCrossCategory
              : undefined,
            domicile: String(resolvedProfile?.domicile || resolvedProfile?.locationZone || '').trim() || undefined,
            locationZone: String(resolvedProfile?.locationZone || resolvedProfile?.domicile || '').trim() || undefined,
            exam: String(resolvedProfile?.academic?.exam || resolvedProfile?.academic?.examTarget || '').trim() || undefined,
            examScore: String(resolvedProfile?.academic?.examScore || '').trim() || undefined,
            careerOption: String(resolvedProfile?.academic?.careerOption || '').trim() || undefined,
            preferredBranch: String(resolvedProfile?.academic?.preferredBranch || '').trim() || undefined,
            educationLevel: String(resolvedProfile?.academic?.educationLevel || '').trim() || undefined,
            targetStream: String(resolvedProfile?.academic?.targetStream || '').trim() || undefined,
            subjects: Array.isArray(resolvedProfile?.academic?.subjects) && resolvedProfile.academic.subjects.length
              ? resolvedProfile.academic.subjects
              : undefined,
            areasOfInterest: Array.isArray(resolvedProfile?.academic?.areasOfInterest) && resolvedProfile.academic.areasOfInterest.length
              ? resolvedProfile.academic.areasOfInterest
              : undefined,
            targetDegreeLevel: String(resolvedProfile?.academic?.targetDegreeLevel || '').trim() || undefined,
            expectedEntranceScore: String(resolvedProfile?.academic?.expectedEntranceScore || '').trim() || undefined,
            preferredLocation: String(resolvedProfile?.preferences?.preferredLocation || resolvedProfile?.locationZone || '').trim() || undefined,
            budgetRange: String(resolvedProfile?.preferences?.budgetRange || '').trim() || undefined,
            collegeType: String(resolvedProfile?.preferences?.collegeType || '').trim() || undefined,
            hostelRequired: typeof resolvedProfile?.preferences?.hostelRequired === 'boolean'
              ? resolvedProfile.preferences.hostelRequired
              : undefined,
          };

          const registrationPayload = Object.fromEntries(
            Object.entries(payload).filter(([, value]) => value !== undefined && value !== null && value !== '')
          );

          console.log('FINAL REGISTER PAYLOAD:', registrationPayload);

          try {
            const registrationResponse = await registerUser(registrationPayload);
            const pendingUser = {
              name: registrationPayload.name,
              email: registrationPayload.email,
              phone: registrationPayload.phone,
            };

            sessionStorage.setItem('auth_pending_user', JSON.stringify(pendingUser));
            sessionStorage.setItem('auth_pending_phone', registrationPayload.phone);

            if (registrationResponse?.sessionId) {
              sessionStorage.setItem('auth_pending_otp_session_id', registrationResponse.sessionId);
            } else {
              const otpResponse = await sendOtp({
                name: registrationPayload.name,
                email: registrationPayload.email,
                phone: registrationPayload.phone,
              });
              if (otpResponse?.sessionId) {
                sessionStorage.setItem('auth_pending_otp_session_id', otpResponse.sessionId);
              }
            }

            localStorage.removeItem('onboarding_state');
            try { sessionStorage.removeItem(SIGNUP_PENDING_KEY); } catch (e) { /* ignore */ }

            toast.success('Account created successfully!');
            navigate('/otp', { replace: true });
            return;
          } catch (registerError) {
            const detail = registerError?.response?.data?.detail || registerError?.response?.data?.message || registerError?.message;
            const message = typeof detail === 'string' && detail ? detail : 'Something went wrong while creating your account. Please try again.';

            if (registerError?.response?.status === 422) {
              toast.error(message);
              setErrors((prev) => ({ ...prev, submit: message }));
              return;
            }

            if (registerError?.response?.status === 409) {
              toast.error('Email already registered');
              setErrors((prev) => ({ ...prev, submit: 'Email already registered' }));
              return;
            }

            if (registerError?.response?.status === 401) {
              toast.error(message || 'Authentication failed. Please try again.');
              setErrors((prev) => ({ ...prev, submit: message || 'Authentication failed. Please try again.' }));
              return;
            }

            if (registerError?.response?.status === 500) {
              toast.error('Something went wrong while creating your account. Please try again.');
              setErrors((prev) => ({ ...prev, submit: 'Something went wrong while creating your account. Please try again.' }));
              return;
            }

            if (!registerError?.response) {
              toast.error('Unable to connect to the server.');
              setErrors((prev) => ({ ...prev, submit: 'Unable to connect to the server.' }));
              return;
            }

            toast.error(message);
            setErrors((prev) => ({ ...prev, submit: message }));
            return;
          }
        }

        const updatedUser = await updateProfile({
          name: String(resolvedProfile?.fullName || resolvedProfile?.name || '').trim(),
          email: String(resolvedProfile?.email || '').trim().toLowerCase(),
          phone: String(resolvedProfile?.phone || '').replace(/\D/g, ''),
          category: String(resolvedProfile?.category || '').trim() || undefined,
          pwdCrossCategory: typeof resolvedProfile?.pwdCrossCategory === 'boolean' ? resolvedProfile.pwdCrossCategory : undefined,
          domicile: String(resolvedProfile?.domicile || resolvedProfile?.locationZone || '').trim() || undefined,
          exam: String(resolvedProfile?.academic?.exam || resolvedProfile?.academic?.examTarget || '').trim() || undefined,
          examScore: String(resolvedProfile?.academic?.examScore || '').trim() || undefined,
          careerOption: String(resolvedProfile?.academic?.careerOption || '').trim() || undefined,
          preferredBranch: String(resolvedProfile?.academic?.preferredBranch || '').trim() || undefined,
          preferredLocation: String(resolvedProfile?.preferences?.preferredLocation || resolvedProfile?.locationZone || '').trim() || undefined,
          budgetRange: String(resolvedProfile?.preferences?.budgetRange || '').trim() || undefined,
          collegeType: String(resolvedProfile?.preferences?.collegeType || '').trim() || undefined,
          hostelRequired: typeof resolvedProfile?.preferences?.hostelRequired === 'boolean' ? resolvedProfile.preferences.hostelRequired : undefined,
        });
        login(updatedUser, localStorage.getItem('auth_token'));
        toast.success('Onboarding complete! Welcome to Cutoff Guide AI.');
        navigate('/home');
      } catch (error) {
        const detail = error?.response?.data?.detail || error?.response?.data?.message || error?.message;
        const message = typeof detail === 'string' && detail ? detail : 'Failed to save profile. Please try again.';
        setErrors((prev) => ({ ...prev, submit: message }));
        toast.error(message);
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  const getButtonText = () => {
    if (activeStep === 1) return 'Continue';
    if (activeStep === 2) return 'Continue';
    if (activeStep === 3) return 'Continue';
    return 'Complete Onboarding';
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

    for (let stepNumber = 1; stepNumber <= 4; stepNumber += 1) {
      const isComplete = stepNumber < activeStep;
      const isActive = stepNumber === activeStep;

      elements.push(
        <span
          key={`circle-${stepNumber}`}
          className={`progress-circle ${isComplete ? 'complete' : ''} ${isActive ? 'active' : ''}`}
        />
      );

      if (stepNumber < 4) {
        elements.push(
          <span
            key={`line-${stepNumber}`}
            className={`progress-line ${isComplete ? 'complete' : ''} ${isActive ? 'active' : ''}`}
          />
        );
      }
    }

    return elements;
  };

  const progress = (activeStep / steps.length) * 100;

  return (
    <div className="onboarding-wrapper">
      <header className={`onboarding-brand-header ${activeStep === 4 ? 'onboarding-brand-header-summary' : ''}`}>
        <div className={`onboarding-brand-center ${activeStep === 4 ? 'onboarding-brand-center-summary' : ''}`}>
          <span className="material-symbols-outlined onboarding-brand-icon">school</span>
          {activeStep !== 4 && <span className="onboarding-brand-name">Cutoff Guide AI</span>}
        </div>
      </header>

      <section className="onboarding-main-shell">
        {activeStep === 4 ? (
          <div className="onboarding-progress-wrap onboarding-progress-wrap-summary">
            <div className="onboarding-progress-summary-row">
              <span className="onboarding-step-label onboarding-step-label-summary">STEP 4 OF 4</span>
              <span className="onboarding-step-label onboarding-step-label-summary onboarding-step-label-right">FINAL REVIEW</span>
            </div>
            <div className="onboarding-progress-summary-bar" aria-label="Progress 4 of 4">
              <span className="onboarding-progress-summary-fill" />
            </div>
          </div>
        ) : (
          <div className="onboarding-progress-wrap">
            <div className="onboarding-step-label">STEP {activeStep} OF {steps.length}</div>
            <div className="onboarding-progress" aria-label={`Progress ${activeStep} of ${steps.length}`}>
              {renderStepIndicator()}
            </div>
          </div>
        )}

        <div className="form-card onboarding-step-card">
          <form className="personal-form" onSubmit={(e) => e.preventDefault()}>
            {activeStep === 1 && (
              <>
                <div className="onboarding-intro">
                  <h1 className="onboarding-page-heading">Let's personalize your journey</h1>
                  <p className="onboarding-page-subheading">Tell us a bit about yourself so we can tailor the academic data to your specific needs.</p>
                </div>

                <div className="onboarding-question-block">
                  <label className="onboarding-question-label">I am a...</label>
                  <div className="user-type-grid">
                    {[
                      {
                        value: 'student',
                        label: 'Student',
                        description: 'Looking for university admissions data and cutoffs.',
                        icon: 'person',
                      },
                      {
                        value: 'parent',
                        label: 'Parent / Guardian',
                        description: 'Researching options for a dependent.',
                        icon: 'family_restroom',
                      },
                      {
                        value: 'counselor',
                        label: 'Counselor',
                        description: 'Guiding multiple students through admissions.',
                        icon: 'support_agent',
                      },
                      {
                        value: 'exploring',
                        label: 'Just Exploring',
                        description: 'Browsing academic data out of curiosity.',
                        icon: 'explore',
                      },
                    ].map((option) => {
                      const isSelected = personal.userType === option.value;

                      return (
                        <label key={option.value} className={`user-type-option ${isSelected ? 'selected' : ''}`}>
                          <input
                            type="radio"
                            name="userType"
                            value={option.value}
                            checked={isSelected}
                            onChange={() => handleUserTypeChange(option.value)}
                            className="sr-only-radio"
                          />
                          <div className="user-type-card">
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
                  {errors.userType && <div className="field-error-text onboarding-error">{errors.userType}</div>}
                </div>

                <div className="step2-field-grid">
                  <div className="step2-field">
                    <label className="step2-label" htmlFor="fullName">Full Name</label>
                    <input
                      id="fullName"
                      type="text"
                      value={personal.fullName}
                      onChange={(e) => handlePersonalChange('fullName', e.target.value)}
                      placeholder="Enter your full name"
                      className={`step2-input ${errors.fullName ? 'field-input-error' : ''}`}
                    />
                    {errors.fullName && <div className="field-error-text">{errors.fullName}</div>}
                  </div>

                  <div className="step2-field">
                    <label className="step2-label" htmlFor="email">Email Address</label>
                    <input
                      id="email"
                      type="email"
                      value={personal.email}
                      onChange={(e) => handlePersonalChange('email', e.target.value)}
                      placeholder="name@example.com"
                      className={`step2-input ${errors.email ? 'field-input-error' : ''}`}
                    />
                    {errors.email && <div className="field-error-text">{errors.email}</div>}
                  </div>
                </div>

                <div className="step2-field-grid">
                  <div className="step2-field">
                    <label className="step2-label" htmlFor="phone">Phone Number</label>
                    <input
                      id="phone"
                      type="tel"
                      value={personal.phone}
                      onChange={(e) => handlePersonalChange('phone', e.target.value)}
                      placeholder="Enter your phone number"
                      className={`step2-input ${errors.phone ? 'field-input-error' : ''}`}
                    />
                    {errors.phone && <div className="field-error-text">{errors.phone}</div>}
                  </div>

                  <div className="step2-field">
                    <label className="step2-label" htmlFor="domicile">Location Zone</label>
                    <input
                      id="domicile"
                      type="text"
                      value={personal.domicile}
                      onChange={(e) => handlePersonalChange('domicile', e.target.value)}
                      placeholder="e.g., Maharashtra"
                      className={`step2-input ${errors.domicile ? 'field-input-error' : ''}`}
                    />
                    {errors.domicile && <div className="field-error-text">{errors.domicile}</div>}
                  </div>
                </div>

                <div className="onboarding-goal-block">
                  <div className="onboarding-goal-header">
                    <label className="onboarding-question-label">What is your primary goal?</label>
                    <p className="onboarding-goal-subtext">Select all that apply.</p>
                  </div>

                  <div className="goal-chip-group">
                    {['Find Universities', 'Compare Cutoffs', 'Research Scholarships', 'Analyze Trends'].map((goal) => {
                      const selected = (personal.goals || []).includes(goal);
                      return (
                        <button
                          key={goal}
                          type="button"
                          className={`goal-chip ${selected ? 'selected' : ''}`}
                          onClick={() => toggleGoal(goal)}
                          aria-pressed={selected}
                        >
                          {goal}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </>
            )}

            {activeStep === 2 && (
              <>
                <div className="academic-step-header">
                  <h1 className="academic-step-title">Academic Background</h1>
                  <p className="academic-step-subtitle">Help us tailor your cutoff predictions by detailing your educational history.</p>
                </div>

                <div className="step2-field-grid">
                  <div className="step2-field">
                    <label className="step2-label" htmlFor="educationLevel">Current Education Level</label>
                    <div className="custom-select-wrap">
                      <select
                        id="educationLevel"
                        name="educationLevel"
                        value={academic.educationLevel}
                        onChange={(e) => handleAcademicChange('educationLevel', e.target.value)}
                        className={`custom-select ${errors.educationLevel ? 'field-input-error' : ''}`}
                      >
                        <option value="" disabled>Select level</option>
                        <option value="High School / Secondary">High School / Secondary</option>
                        <option value="Undergraduate Degree">Undergraduate Degree</option>
                        <option value="Postgraduate Degree">Postgraduate Degree</option>
                        <option value="Professional Certification">Professional Certification</option>
                      </select>
                      <span className="material-symbols-outlined custom-select-icon">expand_more</span>
                    </div>
                    {errors.educationLevel && <div className="field-error-text">{errors.educationLevel}</div>}
                  </div>

                  <div className="step2-field">
                    <label className="step2-label" htmlFor="targetStream">Target Stream</label>
                    <div className="custom-select-wrap">
                      <select
                        id="targetStream"
                        name="targetStream"
                        value={academic.targetStream}
                        onChange={(e) => handleAcademicChange('targetStream', e.target.value)}
                        className={`custom-select ${errors.targetStream ? 'field-input-error' : ''}`}
                      >
                        <option value="" disabled>Select stream</option>
                        <option value="Engineering & Technology">Engineering &amp; Technology</option>
                        <option value="Medicine & Health Sciences">Medicine &amp; Health Sciences</option>
                        <option value="Business & Management">Business &amp; Management</option>
                        <option value="Arts & Humanities">Arts &amp; Humanities</option>
                        <option value="Basic Sciences">Basic Sciences</option>
                      </select>
                      <span className="material-symbols-outlined custom-select-icon">expand_more</span>
                    </div>
                    {errors.targetStream && <div className="field-error-text">{errors.targetStream}</div>}
                  </div>
                </div>

                <div className="step2-field-grid">
                  <div className="step2-field">
                    <label className="step2-label" htmlFor="exam">Primary Exam Target</label>
                    <div className="custom-select-wrap">
                      <select
                        id="exam"
                        name="exam"
                        value={academic.exam}
                        onChange={(e) => handleAcademicChange('exam', e.target.value)}
                        className={`custom-select ${errors.exam ? 'field-input-error' : ''}`}
                      >
                        <option value="" disabled>Select exam</option>
                        {Object.keys(EXAM_CONFIG).map((examOption) => (
                          <option key={examOption} value={examOption}>{examOption}</option>
                        ))}
                      </select>
                      <span className="material-symbols-outlined custom-select-icon">expand_more</span>
                    </div>
                    {errors.exam && <div className="field-error-text">{errors.exam}</div>}
                  </div>

                  <div className="step2-field step2-score-field">
                    <label className="step2-label" htmlFor="examScore">Most Recent Academic Score (CGPA / %)</label>
                    <input
                      type="text"
                      id="examScore"
                      value={academic.examScore}
                      onChange={(e) => handleAcademicChange('examScore', e.target.value)}
                      onBlur={handleAcademicScoreBlur}
                      placeholder="e.g., 8.5 or 92%"
                      className={`step2-input ${errors.examScore ? 'field-input-error' : ''}`}
                    />
                    <small className="step2-caption">This helps us gauge baseline eligibility.</small>
                    {errors.examScore && <div className="field-error-text">{errors.examScore}</div>}
                  </div>
                </div>


                <div className="step2-subject-block">
                  <label className="step2-label">Key Subjects / Strengths</label>

                  <div className="subject-chip-list">
                    {defaultAcademicSubjects.map((subject) => {
                      const selected = academic.subjects.includes(subject);
                      return (
                        <button
                          key={subject}
                          type="button"
                          className={`subject-chip ${selected ? 'selected' : ''}`}
                          aria-pressed={selected}
                          onClick={() => toggleAcademicSubject(subject)}
                        >
                          <span>{subject}</span>
                          <span className="material-symbols-outlined subject-icon">{selected ? 'close' : 'add'}</span>
                        </button>
                      );
                    })}

                    {academic.subjects
                      .filter((subject) => !defaultAcademicSubjects.includes(subject))
                      .map((subject) => (
                        <button
                          key={subject}
                          type="button"
                          className="subject-chip selected"
                          aria-pressed="true"
                          onClick={() => toggleAcademicSubject(subject)}
                        >
                          <span>{subject}</span>
                          <span className="material-symbols-outlined subject-icon">close</span>
                        </button>
                      ))}

                    <button
                      type="button"
                      className="subject-chip add-custom"
                      onClick={() => {
                        setShowCustomSubjectInput((prev) => !prev);
                        if (!showCustomSubjectInput) setCustomSubjectInput('');
                      }}
                    >
                      <span className="material-symbols-outlined subject-icon">search</span>
                      <span>Add Custom Subject</span>
                    </button>
                  </div>

                  {showCustomSubjectInput && (
                    <div className="custom-subject-row">
                      <input
                        type="text"
                        value={customSubjectInput}
                        onChange={(e) => setCustomSubjectInput(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            addCustomSubject();
                          }
                          if (e.key === 'Escape') {
                            setShowCustomSubjectInput(false);
                            setCustomSubjectInput('');
                          }
                        }}
                        className="custom-subject-input"
                        placeholder="Enter subject"
                        autoFocus
                      />
                      <button type="button" className="custom-subject-add" onClick={addCustomSubject}>Add</button>
                    </div>
                  )}
                </div>
              </>
            )}

            {activeStep === 3 && (
              <>
                <div className="step3-header">
                  <div className="step3-progress-row">
                    <span className="material-symbols-outlined step3-brand-icon">school</span>
                    <span className="step3-step-kicker">STEP 3 OF 4</span>
                  </div>
                  <div className="step3-progress-bar" aria-label="Step 3 of 4">
                    <span className="step3-progress-fill" />
                  </div>
                </div>

                <div className="step3-content">
                  <h1 className="step3-title">Refine Your Focus</h1>
                  <p className="step3-subtitle">Select the academic disciplines and degree levels you are targeting. This helps us filter relevant cutoff data.</p>

                  <div className="step3-section">
                    <h2 className="step3-section-title">
                      <span className="material-symbols-outlined step3-section-icon">category</span>
                      Areas of Interest
                    </h2>

                    <div className="step3-chips">
                      {step3AreasOfInterest.map((area) => {
                        const selected = academic.areasOfInterest.includes(area);
                        return (
                          <button
                            key={area}
                            type="button"
                            className={`step3-chip ${selected ? 'selected' : ''}`}
                            onClick={() => toggleAreaOfInterest(area)}
                            aria-pressed={selected}
                          >
                            {area}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  <div className="step3-divider" />

                  <div className="step3-section">
                    <h2 className="step3-section-title">
                      <span className="material-symbols-outlined step3-section-icon">workspace_premium</span>
                      Target Degree Level
                    </h2>

                    <div className="step3-degree-grid">
                      {[
                        { value: 'Undergraduate', label: 'Undergraduate', description: 'Bachelors, Associates', icon: 'menu_book' },
                        { value: 'Postgraduate', label: 'Postgraduate', description: 'Masters, PhD, Research', icon: 'science' },
                      ].map((degree) => {
                        const selected = academic.targetDegreeLevel === degree.value;
                        return (
                          <label key={degree.value} className={`step3-degree-card ${selected ? 'selected' : ''}`}>
                            <input
                              type="radio"
                              name="targetDegreeLevel"
                              value={degree.value}
                              checked={selected}
                              onChange={() => handleAcademicChange('targetDegreeLevel', degree.value)}
                              className="step3-degree-input"
                            />
                            <span className="material-symbols-outlined step3-degree-icon">{degree.icon}</span>
                            <span className="step3-degree-copy">
                              <span className="step3-degree-title">{degree.label}</span>
                              <span className="step3-degree-description">{degree.description}</span>
                            </span>
                          </label>
                        );
                      })}
                    </div>
                    {errors.targetDegreeLevel && <div className="field-error-text">{errors.targetDegreeLevel}</div>}
                  </div>

                  <div className="step3-section step3-input-section">
                    <label className="step3-section-title step3-inline-title" htmlFor="expectedEntranceScore">
                      <span className="material-symbols-outlined step3-section-icon">analytics</span>
                      Expected Entrance Score (Optional)
                    </label>
                    <input
                      type="text"
                      id="expectedEntranceScore"
                      value={academic.expectedEntranceScore}
                      onChange={(e) => handleAcademicChange('expectedEntranceScore', e.target.value)}
                      placeholder="e.g., 95.5 percentile"
                      className={`step3-input ${errors.expectedEntranceScore ? 'field-input-error' : ''}`}
                    />
                    {errors.expectedEntranceScore && <div className="field-error-text">{errors.expectedEntranceScore}</div>}
                  </div>
                </div>
              </>
            )}

            {activeStep === 4 && (
              <>
                <div className="summary-grid-layout">
                  <div className="summary-card summary-card-identity">
                    <div className="summary-card-header">
                      <div className="summary-card-title-wrap">
                        <span className="material-symbols-outlined summary-card-icon">person</span>
                        <h2>Identity</h2>
                      </div>
                      <button type="button" className="summary-edit-button" onClick={() => goToStep(1)} aria-label="Edit personal identity">
                        <span className="material-symbols-outlined">edit</span>
                      </button>
                    </div>

                    <div className="summary-value-block">
                      <span className="summary-label">Full Name</span>
                      <span className="summary-value">{studentProfile.fullName || 'Not provided'}</span>
                    </div>
                    <div className="summary-value-block">
                      <span className="summary-label">Contact</span>
                      <span className="summary-value">{studentProfile.email || 'Not provided'}</span>
                    </div>
                    <div className="summary-value-block">
                      <span className="summary-label">Location Zone</span>
                      <span className="summary-value">{studentProfile.domicile || 'Not provided'}</span>
                    </div>
                  </div>

                  <div className="summary-card summary-card-academic">
                    <div className="summary-card-header">
                      <div className="summary-card-title-wrap">
                        <span className="material-symbols-outlined summary-card-icon">menu_book</span>
                        <h2>Academic Baseline</h2>
                      </div>
                      <button type="button" className="summary-edit-button" onClick={() => goToStep(2)} aria-label="Edit academic baseline">
                        <span className="material-symbols-outlined">edit</span>
                      </button>
                    </div>

                    <div className="summary-value-block">
                      <span className="summary-label">Current Level</span>
                      <span className="summary-value">{studentProfile.academic?.educationLevel || 'Not provided'}</span>
                    </div>
                    <div className="summary-value-block">
                      <span className="summary-label">Current GPA (Est.)</span>
                      <span className="summary-value">{studentProfile.academic?.examScore || 'Not provided'}</span>
                    </div>
                    <div className="summary-value-block">
                      <span className="summary-label">Target Field</span>
                      <div className="summary-pill-row">
                        {(studentProfile.academic?.areasOfInterest?.length ? studentProfile.academic.areasOfInterest : ['Not provided']).map((item) => (
                          <span key={item} className="summary-pill">{item}</span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="summary-card summary-card-parameters">
                    <div className="summary-card-header">
                      <div className="summary-card-title-wrap">
                        <span className="material-symbols-outlined summary-card-icon">flag</span>
                        <h2>Cutoff Parameters</h2>
                      </div>
                      <button type="button" className="summary-edit-button" onClick={() => goToStep(3)} aria-label="Edit cutoff parameters">
                        <span className="material-symbols-outlined">edit</span>
                      </button>
                    </div>

                    <div className="summary-value-block">
                      <span className="summary-label">Primary Exam Target</span>
                      <span className="summary-value">{studentProfile.academic?.exam || 'Not provided'}</span>
                    </div>
                    <div className="summary-value-block">
                      <span className="summary-label">Confidence Interval</span>
                      <div className="summary-confidence-line">
                        <span className="summary-confidence-label">{studentProfile.academic?.expectedEntranceScore ? 'High' : 'No score set'}</span>
                        <div className="summary-confidence-bars" aria-hidden="true">
                          {[0, 1, 2].map((bar) => (
                            <span key={bar} className={`summary-confidence-bar ${studentProfile.academic?.expectedEntranceScore ? 'active' : ''}`} />
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="summary-value-block">
                      <span className="summary-label">Institutional Scope</span>
                      <span className="summary-value">{studentProfile.preferences?.preferredLocation || 'Not provided'}</span>
                    </div>
                  </div>
                </div>

              </>
            )}
          </form>
        </div>

        {activeStep === 2 || activeStep === 3 ? (
          <div className="step2-actions">
            <button className="step2-back-button" type="button" onClick={handleBack}>
              <span className="material-symbols-outlined button-icon">arrow_back</span>
              Back
            </button>
            <button className="continue-button" onClick={handleContinue} type="button" disabled={isSubmitting}>
              {isSubmitting ? 'Creating Account...' : isSignup && activeStep === 4 ? 'Create Account' : getButtonText()}
              <span className="material-symbols-outlined button-icon">arrow_forward</span>
            </button>
          </div>
        ) : (
          <div className="bottom-action">
            <button className="continue-button" onClick={handleContinue} type="button" disabled={isSubmitting}>
              {isSubmitting ? 'Creating Account...' : isSignup && activeStep === 4 ? 'Create Account' : getButtonText()}
              <span className="material-symbols-outlined button-icon">arrow_forward</span>
            </button>
          </div>
        )}
      </section>
    </div>
  );
};

export default Onboarding;
