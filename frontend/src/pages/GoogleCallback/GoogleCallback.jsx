import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const GoogleCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login } = useAuth();
  const [message, setMessage] = useState('Completing Google sign-in...');

  const callbackUser = useMemo(() => {
    const token = searchParams.get('token') || '';
    const uid = searchParams.get('uid') || '';
    const name = searchParams.get('name') || 'Google User';
    const email = searchParams.get('email') || '';
    const photoURL = searchParams.get('photoURL') || '';

    return {
      token,
      uid,
      name,
      email,
      photoURL,
    };
  }, [searchParams]);

  useEffect(() => {
    const { token, uid, name, email, photoURL } = callbackUser;
    const error = searchParams.get('error');

    if (error) {
      setMessage('Google sign-in was cancelled or failed. Redirecting to login...');
      const timer = setTimeout(() => navigate('/login', { replace: true }), 1200);
      return () => clearTimeout(timer);
    }

    if (!token) {
      setMessage('Google sign-in failed. Redirecting to login...');
      const timer = setTimeout(() => navigate('/login', { replace: true }), 1500);
      return () => clearTimeout(timer);
    }

    const userPayload = {
      uid: uid || `google-${email || 'user'}`,
      name,
      email,
      provider: 'google',
      photoURL,
    };

    try {
      login(userPayload, token);
      setMessage('Google sign-in successful. Redirecting...');
      const timer = setTimeout(() => navigate('/home', { replace: true }), 600);
      return () => clearTimeout(timer);
    } catch (loginError) {
      console.error('Google callback login failed:', loginError);
      setMessage('Something went wrong while completing Google sign-in. Redirecting to login...');
      const timer = setTimeout(() => navigate('/login', { replace: true }), 1500);
      return () => clearTimeout(timer);
    }
  }, [callbackUser, navigate, login, searchParams]);

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #0b1020 0%, #121d33 100%)',
      color: '#f8fafc',
      fontFamily: 'Inter, system-ui, sans-serif',
      padding: '24px',
    }}>
      <div style={{
        maxWidth: '420px',
        textAlign: 'center',
        background: 'rgba(15, 23, 42, 0.72)',
        border: '1px solid rgba(148, 163, 184, 0.2)',
        borderRadius: '18px',
        padding: '32px 24px',
        boxShadow: '0 24px 60px rgba(15, 23, 42, 0.5)',
      }}>
        <div style={{ marginBottom: '12px', fontSize: '2rem' }}>🔐</div>
        <h2 style={{ margin: '0 0 10px', fontSize: '1.5rem' }}>Google Sign-In</h2>
        <p style={{ margin: 0, color: '#cbd5e1', lineHeight: 1.6 }}>{message}</p>
      </div>
    </div>
  );
};

export default GoogleCallback;
