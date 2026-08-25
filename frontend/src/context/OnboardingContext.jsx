import { createContext, useContext, useEffect, useState } from 'react';

const OnboardingContext = createContext(null);

const STORAGE_KEY = 'onboarding_state';

const normalizeStoredProfile = (profile = {}) => {
  const domicile = profile.domicile ?? profile.stateOfDomicile ?? profile.locationZone ?? '';
  const category = profile.category ?? profile.studentCategory ?? '';
  return {
    ...profile,
    domicile,
    category,
    locationZone: profile.locationZone ?? domicile,
  };
};

const buildInitialProfile = (currentUser) => ({
  name: currentUser?.name || '',
  fullName: currentUser?.name || '',
  email: currentUser?.email || '',
  userType: 'student',
  goals: [],
  category: '',
  pwdCrossCategory: false,
  phone: '',
  domicile: '',
  locationZone: '',
  academic: {
    exam: '',
    examTarget: '',
    examScore: '',
    careerOption: '',
    preferredBranch: '',
    educationLevel: '',
    targetStream: '',
    subjects: [],
    areasOfInterest: [],
    targetDegreeLevel: '',
    expectedEntranceScore: '',
  },
  preferences: {
    preferredLocation: '',
    budgetRange: '0-10',
    collegeType: '',
    hostelRequired: false,
  },
});

const buildPendingSignupProfile = (currentUser) => {
  try {
    const raw = sessionStorage.getItem('signup_pending_credentials');
    if (!raw) return buildInitialProfile(currentUser);

    const parsed = JSON.parse(raw);
    const fullName = parsed.fullName || parsed.name || currentUser?.name || '';
    const domicile = parsed.domicile ?? parsed.stateOfDomicile ?? parsed.locationZone ?? '';
    const category = parsed.category ?? parsed.studentCategory ?? '';

    return normalizeStoredProfile({
      ...buildInitialProfile(currentUser),
      name: fullName,
      fullName,
      email: parsed.email || currentUser?.email || '',
      phone: parsed.phone || '',
      domicile,
      category,
      locationZone: domicile,
    });
  } catch (e) {
    console.warn('Pending signup restore failed', e);
    return buildInitialProfile(currentUser);
  }
};

const resolveInitialProfile = (currentUser) => {
  const base = buildInitialProfile(currentUser);

  try {
    const savedRaw = localStorage.getItem(STORAGE_KEY);
    if (savedRaw) {
      const savedProfile = normalizeStoredProfile(JSON.parse(savedRaw));
      const merged = { ...base, ...savedProfile };
      if (savedProfile.academic) merged.academic = { ...base.academic, ...savedProfile.academic };
      if (savedProfile.preferences) merged.preferences = { ...base.preferences, ...savedProfile.preferences };
      return normalizeStoredProfile(merged);
    }
  } catch (e) {
    console.warn('Onboarding storage restore failed', e);
  }

  const pendingProfile = buildPendingSignupProfile(currentUser);
  const hasPendingValues = !!(pendingProfile?.email || pendingProfile?.phone || pendingProfile?.fullName || pendingProfile?.domicile);
  return hasPendingValues ? pendingProfile : base;
};

export const OnboardingProvider = ({ children, currentUser }) => {
  const [activeStep, setActiveStep] = useState(1);
  const [studentProfile, setStudentProfile] = useState(() => {
    const pendingProfile = buildPendingSignupProfile(currentUser);
    const hasPendingValues = !!(pendingProfile?.email || pendingProfile?.phone || pendingProfile?.fullName || pendingProfile?.domicile);

    if (hasPendingValues) {
      return pendingProfile;
    }

    return resolveInitialProfile(currentUser);
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(studentProfile));
    } catch (e) {
      console.warn('Onboarding storage save failed', e);
    }
  }, [studentProfile]);

  const setPersonal = (payload) => {
    setStudentProfile((prev) => {
      const nextFullName = payload.fullName ?? payload.name ?? prev.fullName ?? prev.name ?? '';
      const nextDomicile = payload.domicile ?? payload.stateOfDomicile ?? payload.locationZone ?? prev.domicile ?? prev.stateOfDomicile ?? prev.locationZone ?? '';
      const nextCategory = payload.category ?? payload.studentCategory ?? prev.category ?? prev.studentCategory ?? '';

      return normalizeStoredProfile({
        ...prev,
        name: payload.name ?? nextFullName,
        fullName: nextFullName,
        email: payload.email ?? prev.email,
        userType: payload.userType ?? prev.userType ?? 'student',
        goals: payload.goals ?? prev.goals ?? [],
        category: nextCategory,
        pwdCrossCategory: payload.pwdCrossCategory ?? prev.pwdCrossCategory,
        phone: payload.phone ?? prev.phone,
        domicile: nextDomicile,
        locationZone: nextDomicile,
      });
    });
  };

  const setAcademic = (payload) => {
    setStudentProfile((prev) => {
      const nextExam = payload.exam ?? payload.examTarget ?? prev.academic?.exam ?? '';
      return {
        ...prev,
        academic: {
          ...prev.academic,
          ...payload,
          exam: nextExam,
          examTarget: nextExam,
        },
      };
    });
  };

  const setPreferences = (payload) => {
    setStudentProfile((prev) => {
      const nextPreferredLocation = payload.preferredLocation ?? payload.locationZone ?? prev.preferences?.preferredLocation ?? prev.locationZone ?? '';
      return {
        ...prev,
        locationZone: payload.locationZone ?? nextPreferredLocation,
        preferences: {
          ...prev.preferences,
          ...payload,
          preferredLocation: nextPreferredLocation,
        },
      };
    });
  };

  const nextStep = () => {
    setActiveStep((prev) => (prev < 4 ? prev + 1 : prev));
  };

  const prevStep = () => {
    setActiveStep((prev) => (prev > 1 ? prev - 1 : prev));
  };

  const goToStep = (step) => {
    if (step >= 1 && step <= 4) {
      setActiveStep(step);
    }
  };

  const resetOnboarding = () => {
    setActiveStep(1);
    setStudentProfile(buildInitialProfile(currentUser));
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (e) {
      /* ignore */
    }
  };

  return (
    <OnboardingContext.Provider
      value={{
        activeStep,
        studentProfile,
        setPersonal,
        setAcademic,
        setPreferences,
        nextStep,
        prevStep,
        goToStep,
        resetOnboarding,
      }}
    >
      {children}
    </OnboardingContext.Provider>
  );
};

export const useOnboarding = () => {
  const ctx = useContext(OnboardingContext);
  if (!ctx) {
    throw new Error('useOnboarding must be used within OnboardingProvider');
  }
  return ctx;
};

export default OnboardingContext;
