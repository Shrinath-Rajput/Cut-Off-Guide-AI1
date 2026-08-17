import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const GoogleCallback = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [message, setMessage] = useState('Signing in with Google...');

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const token = params.get('token');
    const uid = params.get('uid');
    const name = params.get('name');
    const email = params.get('email');
    const photoURL = params.get('photoURL');

    if (!token || !uid) {
      setMessage('Google sign-in failed. Redirecting to login...');
      const timeout = setTimeout(() => navigate('/login', { replace: true }), 1500);
      return () => clearTimeout(timeout);
    }

    const user = {
      uid,
      name: name || 'Google User',
      email: email || '',
      provider: 'google',
      photoURL: photoURL || '',
    };

    login(user, token);
    const timeout = setTimeout(() => navigate('/onboarding', { replace: true }), 500);
    return () => clearTimeout(timeout);
  }, [location.search, login, navigate]);

  return (
    <div className="page-shell auth-callback-shell">
      <div style={{ textAlign: 'center', padding: '4rem' }}>
        <h2>{message}</h2>
      </div>
    </div>
  );
};

export default GoogleCallback;
