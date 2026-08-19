import { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();
  const fromAdminLogout = sessionStorage.getItem('admin_logout_redirect') === 'true';

  useEffect(() => {
    if (fromAdminLogout && location.pathname === '/home') {
      sessionStorage.removeItem('admin_logout_redirect');
    }
  }, [fromAdminLogout, location.pathname]);

  if (loading) {
    return null;
  }

  if (!isAuthenticated && fromAdminLogout && location.pathname === '/home') {
    return children;
  }

  if (!isAuthenticated && fromAdminLogout && location.pathname.startsWith('/admin')) {
    return <Navigate to="/home" replace state={{ fromAdminLogout: true }} />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/welcome" state={{ from: location }} replace />;
  }

  return children;
};

export default ProtectedRoute;
