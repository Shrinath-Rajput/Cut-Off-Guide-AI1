import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return null;
  }

  const hasToken = !!localStorage.getItem('auth_token');
  const hasUser = !!localStorage.getItem('auth_user');
  const authed = isAuthenticated || (hasToken && hasUser);

  if (!authed) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

export default ProtectedRoute;
