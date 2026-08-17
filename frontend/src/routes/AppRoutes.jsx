import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Splash from '../pages/Splash/Splash';
import Welcome from '../pages/Welcome/Welcome';
import Login from '../pages/Login/Login';
import OTP from '../pages/OTP/OTP';
import Dashboard from '../pages/Dashboard/Dashboard';
import Home from '../pages/Home/Home';
import Profile from '../pages/Profile/Profile';
import Onboarding from '../pages/Onboarding/Onboarding';
import About from '../pages/About/About';
import Terms from '../pages/Terms/Terms';
import Contact from '../pages/Contact/Contact';
import Colleges from '../pages/Colleges/Colleges';
import CollegeDetails from '../pages/CollegeDetails/CollegeDetails';
import Compare from '../pages/Compare/Compare';
import Cutoff from '../pages/Cutoff/Cutoff';
import Assistant from '../pages/Assistant/Assistant';
import Saved from '../pages/Saved/Saved';
import History from '../pages/History/History';
import GoogleCallback from '../pages/GoogleCallback/GoogleCallback';
import ProtectedRoute from './ProtectedRoute';
import { OnboardingProvider } from '../context/OnboardingContext';
import { useAuth } from '../context/AuthContext';

const AppRoutes = () => {
  const { currentUser } = useAuth();
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Splash />} />
        <Route path="/welcome" element={<Welcome />} />
        <Route path="/login" element={<Login />} />
        <Route path="/otp" element={<OTP />} />
        <Route path="/about" element={<About />} />
        <Route path="/terms" element={<Terms />} />
        <Route path="/privacy" element={<Terms />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/colleges" element={<Colleges />} />
        <Route path="/college/:id" element={<CollegeDetails />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/cutoff" element={<Cutoff />} />
        <Route path="/assistant" element={<Assistant />} />
        <Route path="/saved" element={<Saved />} />
        <Route path="/history" element={<History />} />
        <Route
          path="/home"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/onboarding"
          element={
            <ProtectedRoute>
              <OnboardingProvider currentUser={currentUser}>
                <Onboarding />
              </OnboardingProvider>
            </ProtectedRoute>
          }
        />
        <Route path="/auth/google/callback" element={<GoogleCallback />} />
        <Route path="*" element={<Navigate to="/welcome" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRoutes;
