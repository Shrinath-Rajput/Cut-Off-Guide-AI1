import { createContext, useContext, useEffect, useState } from 'react';
import { registerUser as registerUserApi } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [adminUser, setAdminUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const storedUser = localStorage.getItem('auth_user');
    const storedToken = localStorage.getItem('auth_token');
    const storedAdminUser = localStorage.getItem('admin_user');
    const storedAdminToken = localStorage.getItem('admin_token');

    if (storedUser && storedToken) {
      setCurrentUser(JSON.parse(storedUser));
      setIsAuthenticated(true);
    } else {
      const guestUser = {
        uid: 'guest_student',
        name: 'Guest Student',
        email: 'student@cutoffguide.ai',
        phone: '9876543210',
        percentile: 95.5,
        targetBranch: 'Computer Science',
        state: 'Maharashtra',
        role: 'USER',
      };
      setCurrentUser(guestUser);
      setIsAuthenticated(true);
    }

    if (storedAdminUser && storedAdminToken) {
      const parsedAdmin = JSON.parse(storedAdminUser);
      setAdminUser(parsedAdmin);
    }

    setLoading(false);
  }, []);

  const login = (user, token) => {
    const normalizedUser = {
      uid: user.uid || 'user',
      name: user.name || 'User',
      email: user.email || '',
      phone: user.phone || '',
      provider: user.provider || 'unknown',
      photoURL: user.photoURL || '',
      ...user,
    };

    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }

    localStorage.setItem('auth_user', JSON.stringify(normalizedUser));
    setCurrentUser(normalizedUser);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    sessionStorage.removeItem('auth_pending_otp_session_id');
    sessionStorage.removeItem('auth_pending_user');
    sessionStorage.removeItem('auth_pending_phone');
    setCurrentUser(null);
    setIsAuthenticated(false);
  };

  const adminLogin = (user, token) => {
    const normalizedUser = { ...user, role: user?.role || 'ADMIN' };
    localStorage.setItem('admin_token', token);
    localStorage.setItem('admin_user', JSON.stringify(normalizedUser));
    setAdminUser(normalizedUser);
  };

  const adminLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    setAdminUser(null);
  };

  const registerAndLogin = async (userPayload) => {
    const response = await registerUserApi(userPayload);
    const backendUser = response?.user || userPayload;
    const token = response?.token || `token-${backendUser.uid}`;

    login(backendUser, token);
    return response;
  };

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        loading,
        isAuthenticated,
        adminUser,
        login,
        logout,
        adminLogin,
        adminLogout,
        registerAndLogin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
