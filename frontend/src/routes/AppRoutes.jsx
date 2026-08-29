import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Splash from '../pages/Splash/Splash';
import Welcome from '../pages/Welcome/Welcome';
import Login from '../pages/Login/Login';
import Signup from '../pages/Signup/Signup';
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
import AdminLogin from '../pages/AdminLogin/AdminLogin';
import AdminPanel from '../pages/AdminPanel/AdminPanel';
import SuperAdminDashboard from '../pages/SuperAdminDashboard/SuperAdminDashboard';
import ProtectedRoute from './ProtectedRoute';
import { OnboardingProvider } from '../context/OnboardingContext';
import { useAuth } from '../context/AuthContext';

const AppRoutes = () => {
  const { currentUser } = useAuth();
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/home" element={<Home />} />
        <Route path="/welcome" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/signup"
          element={
            <OnboardingProvider currentUser={currentUser}>
              <Signup />
            </OnboardingProvider>
          }
        />
        <Route
          path="/onboarding"
          element={
            <OnboardingProvider currentUser={currentUser}>
              <Onboarding />
            </OnboardingProvider>
          }
        />
        <Route path="/otp" element={<OTP />} />
        <Route path="/about" element={<About />} />
        <Route path="/terms" element={<Terms />} />
        <Route path="/privacy" element={<Terms />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/colleges" element={<Colleges />} />
        <Route path="/college/:id" element={<CollegeDetails />} />
        <Route path="/colleges/:id" element={<CollegeDetails />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/cutoff" element={<Cutoff />} />
        <Route path="/assistant" element={<Assistant />} />
        <Route path="/saved" element={<Saved />} />
        <Route path="/history" element={<History />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/auth/google/callback" element={<GoogleCallback />} />
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="/admin/dashboard" element={<AdminRoute><AdminPanel section="dashboard" /></AdminRoute>} />
        <Route path="/admin/users" element={<AdminRoute><AdminPanel section="users" /></AdminRoute>} />
        <Route path="/admin/enquiries" element={<AdminRoute><AdminPanel section="enquiries" /></AdminRoute>} />
        <Route path="/admin/data" element={<AdminRoute><AdminPanel section="data" /></AdminRoute>} />
        <Route path="/admin/images" element={<AdminRoute><AdminPanel section="images" /></AdminRoute>} />
        <Route path="/admin/subscriptions" element={<AdminRoute><AdminPanel section="plans" /></AdminRoute>} />
        <Route path="/super-admin" element={<SuperAdminRoute><SuperAdminDashboard /></SuperAdminRoute>} />
        <Route path="/super-admin/dashboard" element={<SuperAdminRoute><SuperAdminDashboard /></SuperAdminRoute>} />
        <Route path="/super-admin/admin-panel" element={<SuperAdminRoute><AdminPanel section="dashboard" /></SuperAdminRoute>} />
        <Route path="/super-admin/users" element={<SuperAdminRoute><AdminPanel section="users" /></SuperAdminRoute>} />
        <Route path="/super-admin/data" element={<SuperAdminRoute><AdminPanel section="data" /></SuperAdminRoute>} />
        <Route path="/admin/*" element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="/super-admin/*" element={<Navigate to="/super-admin/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

const AdminRoute = ({ children }) => {
  const { adminUser, loading } = useAuth();
  if (loading) return null;
  const role = adminUser?.role || '';
  if (role === 'SUPER_ADMIN') {
    return <Navigate to="/super-admin/dashboard" replace />;
  }
  return role === 'ADMIN' ? children : <Navigate to="/login" replace />;
};

const SuperAdminRoute = ({ children }) => {
  const { adminUser, loading } = useAuth();
  if (loading) return null;
  return adminUser?.role === 'SUPER_ADMIN' ? children : <Navigate to="/login" replace />;
};

export default AppRoutes;
