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
    }

    if (storedAdminUser && storedAdminToken) {
      setAdminUser(JSON.parse(storedAdminUser));
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
    localStorage.clear();
    sessionStorage.clear();
    setCurrentUser(null);
    setIsAuthenticated(false);
  };

  const adminLogin = (user, token) => {
    localStorage.setItem('admin_token', token);
    localStorage.setItem('admin_user', JSON.stringify(user));
    setAdminUser(user);
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
