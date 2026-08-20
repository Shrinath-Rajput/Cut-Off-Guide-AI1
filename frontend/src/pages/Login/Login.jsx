import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { loginUser, sendLoginOtp, verifyLoginOtp } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import './Login.css';

const getErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail || error?.response?.data?.message;
  if (typeof detail !== 'string') return fallback;
  if (detail === 'Phone number is not registered for this account') return 'Phone number is not registered for this account.';
  if (error?.response?.status === 404 || detail === 'Not Found' || detail === 'Internal Server Error') return fallback;
  return detail;
};

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [view, setView] = useState('credentials');
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [otpDigits, setOtpDigits] = useState(['', '', '', '', '', '']);
  const [error, setError] = useState('');
  const [phoneError, setPhoneError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [timer, setTimer] = useState(0);
  const [pendingLogin, setPendingLogin] = useState(null);
  const otpInputRefs = useRef([]);

  useEffect(() => {
    if (timer <= 0) return undefined;
    const interval = setInterval(() => setTimer((value) => value - 1), 1000);
    return () => clearInterval(interval);
  }, [timer]);

  const handleNext = async (event) => {
    event.preventDefault();
    if (!identifier.trim() || !password) {
      setError(!identifier.trim() ? 'Enter your username or email.' : 'Enter your password.');
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      const response = await loginUser({ username: identifier.trim(), password });
      setPendingLogin({ ...response.user, uid: response.uid || response.user.uid });
      setPhone(response.otpPhone || response.user.phone || '');
      setView('phone');
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Unable to sign in. Please check your credentials.'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendOtp = async (event) => {
    event.preventDefault();
    const normalizedPhone = phone.replace(/\D/g, '').slice(-10);
    if (!/^\d{10}$/.test(normalizedPhone)) {
      setPhoneError('Enter a valid 10-digit phone number.');
      return;
    }
    setIsLoading(true);
    setError('');
    setPhoneError('');
    try {
      const response = await sendLoginOtp({ uid: pendingLogin.uid, phone: normalizedPhone });
      sessionStorage.setItem('auth_pending_otp_session_id', response.sessionId);
      setPhone(normalizedPhone);
      setOtpDigits(['', '', '', '', '', '']);
      setTimer(30);
      setView('otp');
      toast.success('OTP sent successfully');
      setTimeout(() => otpInputRefs.current[0]?.focus(), 0);
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Unable to send OTP. Please try again.'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOtp = async (event) => {
    event.preventDefault();
    const otp = otpDigits.join('');
    if (otp.length !== 6) {
      setError('Enter the 6-digit OTP.');
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      const response = await verifyLoginOtp({
        uid: pendingLogin.uid,
        phone,
        otp,
        sessionId: sessionStorage.getItem('auth_pending_otp_session_id'),
      });
      login(response.user, response.token);
      sessionStorage.removeItem('auth_pending_otp_session_id');
      toast.success('Signed in successfully');
      navigate('/home', { replace: true });
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Invalid or expired OTP. Please try again.'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleOtpChange = (index, value) => {
    const digit = value.replace(/\D/g, '').slice(-1);
    setError('');
    setOtpDigits((current) => current.map((item, itemIndex) => (itemIndex === index ? digit : item)));
    if (digit) otpInputRefs.current[index + 1]?.focus();
  };

  const handleResend = () => {
    if (timer === 0 && !isLoading) handleSendOtp({ preventDefault: () => {} });
  };

  const formatPhone = (value) => {
    const digits = value.replace(/\D/g, '').slice(-10);
    return digits.length === 10 ? `+91 ${digits.slice(0, 5)} ${digits.slice(5)}` : '+91 XXXXX XXXXX';
  };

  return (
    <div className="stitch-auth-page">
      <header className="stitch-auth-header">
        <div className="stitch-auth-brand">
          <span className="material-symbols-outlined stitch-auth-brand-icon">school</span>
          <span className="stitch-auth-brand-text">Cutoff Guide AI</span>
        </div>
        <button type="button" className="stitch-auth-close-btn" onClick={() => navigate('/home')} aria-label="Close">
          <span className="material-symbols-outlined stitch-auth-close-icon">close</span>
        </button>
      </header>
      <main className="stitch-auth-main">
        <div className="stitch-auth-card">
          <div className="stitch-auth-header-section">
            <h1 className="stitch-auth-headline">{view === 'credentials' ? 'Sign In' : 'Verify Your Phone'}</h1>
            <p className="stitch-auth-subhead">{view === 'credentials' ? 'Sign in to continue to your personalized college guide.' : `We sent a verification code to ${formatPhone(phone)}`}</p>
          </div>
          {view === 'credentials' && (
            <form className="stitch-form" onSubmit={handleNext} noValidate>
              <div className="stitch-field"><label className="stitch-field-label" htmlFor="login-identifier">Username / Email</label><input id="login-identifier" className="stitch-phone-input" value={identifier} onChange={(event) => setIdentifier(event.target.value)} placeholder="Enter username or email" autoComplete="username" /></div>
              <div className="stitch-field"><label className="stitch-field-label" htmlFor="login-password">Password</label><input id="login-password" type="password" className="stitch-phone-input" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter password" autoComplete="current-password" /></div>
              {error && <p className="stitch-field-error">{error}</p>}
              <button type="submit" className="stitch-primary-btn" disabled={isLoading}>{isLoading ? 'Checking...' : 'Next'}</button>
              <p className="stitch-terms">Don't have an account? <button type="button" className="stitch-terms-link" onClick={() => { localStorage.removeItem('onboarding_state'); navigate('/onboarding?mode=signup'); }}>Create Account</button></p>
            </form>
          )}
          {view === 'phone' && (
            <form className="stitch-form" onSubmit={handleSendOtp} noValidate>
              <div className="stitch-field"><label className="stitch-field-label" htmlFor="login-phone">Phone Number</label><input id="login-phone" type="tel" className="stitch-phone-input" value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="+91 XXXXX XXXXX" />{phoneError && <p className="stitch-field-error">{phoneError}</p>}</div>
              {error && <p className="stitch-field-error">{error}</p>}
              <button type="submit" className="stitch-primary-btn" disabled={isLoading}>{isLoading ? 'Sending OTP...' : 'Send OTP'}</button>
              <button type="button" className="stitch-back-btn" onClick={() => { setView('credentials'); setError(''); }}>Change credentials</button>
            </form>
          )}
          {view === 'otp' && (
            <form className="stitch-form" onSubmit={handleVerifyOtp} noValidate>
              <div className="stitch-otp-group">{otpDigits.map((digit, index) => <input key={index} ref={(element) => { otpInputRefs.current[index] = element; }} type="text" inputMode="numeric" maxLength={1} className="stitch-otp-input" value={digit} onChange={(event) => handleOtpChange(index, event.target.value)} />)}</div>
              {error && <p className="stitch-field-error stitch-otp-error">{error}</p>}
              <button type="submit" className="stitch-primary-btn" disabled={isLoading}>{isLoading ? 'Verifying...' : 'Verify OTP'}</button>
              <div className="stitch-resend-wrap"><p className="stitch-resend-question">{timer > 0 ? `Resend OTP in 00:${String(timer).padStart(2, '0')}` : "Didn't receive the code?"}</p><button type="button" className="stitch-resend-btn stitch-resend-active" onClick={handleResend} disabled={timer > 0 || isLoading}>Resend OTP</button></div>
              <button type="button" className="stitch-back-btn" onClick={() => setView('phone')}>Change phone number</button>
            </form>
          )}
        </div>
      </main>
    </div>
  );
};

export default Login;