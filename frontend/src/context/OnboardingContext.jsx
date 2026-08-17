import { createContext, useContext, useEffect, useState } from 'react';

const OnboardingContext = createContext(null);

const STORAGE_KEY = 'onboarding_state';

const buildInitialProfile = (currentUser) => ({
  fullName: currentUser?.name || '',
  email: currentUser?.email || '',
  category: '',
  academic: {
    examScore: '',
    preferredBranch: '',
  },
  preferences: {
    preferredLocation: '',
    budgetRange: '',
  },
});

export const OnboardingProvider = ({ children, currentUser }) => {
  const [activeStep, setActiveStep] = useState(1);
  const [studentProfile, setStudentProfile] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        return {
          ...buildInitialProfile(currentUser),
          ...parsed,
        };
      }
    } catch (e) {
      console.warn('Onboarding storage restore failed', e);
    }
    return buildInitialProfile(currentUser);
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(studentProfile));
    } catch (e) {
      console.warn('Onboarding storage save failed', e);
    }
  }, [studentProfile]);

  const setPersonal = (payload) => {
    setStudentProfile((prev) => ({
      ...prev,
      fullName: payload.fullName ?? prev.fullName,
      email: payload.email ?? prev.email,
      category: payload.category ?? prev.category,
    }));
  };

  const setAcademic = (payload) => {
    setStudentProfile((prev) => ({
      ...prev,
      academic: {
        ...prev.academic,
        ...payload,
      },
    }));
  };

  const setPreferences = (payload) => {
    setStudentProfile((prev) => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        ...payload,
      },
    }));
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
