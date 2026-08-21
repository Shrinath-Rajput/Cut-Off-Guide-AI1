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
  const [showPassword, setShowPassword] = useState(false);
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
      setError(!identifier.trim() ? 'Enter your email or username.' : 'Password is required.');
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
      setError(getErrorMessage(requestError, 'Invalid username/email or password.'));
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
    <div className="cg-auth-page">
      <div className="cg-auth-bg" aria-hidden="true">
        <div className="cg-auth-blob cg-auth-blob--top" />
        <div className="cg-auth-blob cg-auth-blob--bottom" />
      </div>
      <main className="cg-auth-main">
        <div className="cg-auth-card">
          <div className="cg-auth-brand">
            <span className="material-symbols-outlined cg-auth-brand-icon fill-icon">school</span>
            <span className="cg-auth-brand-text">Cutoff Guide AI</span>
          </div>

          <div className="cg-auth-hero">
            <h1 className="cg-auth-title">
              {view === 'credentials' && 'Sign In'}
              {view === 'phone' && 'Verify Your Phone'}
              {view === 'otp' && 'Enter OTP'}
            </h1>
            <p className="cg-auth-subtitle">
              {view === 'credentials' && 'Welcome back! Please enter your details.'}
              {view === 'phone' && 'Confirm your phone number to receive a secure OTP.'}
              {view === 'otp' && `We sent a verification code to ${formatPhone(phone)}`}
            </p>
          </div>

          {view === 'credentials' && (
            <form className="cg-form" onSubmit={handleNext} noValidate>
              <div className="cg-field">
                <label className="cg-field-label" htmlFor="login-identifier">Email or Username</label>
                <input
                  id="login-identifier"
                  className={`cg-input ${error && !identifier.trim() ? 'cg-input--error' : ''}`}
                  value={identifier}
                  onChange={(event) => { setIdentifier(event.target.value); setError(''); }}
                  placeholder="Enter your email"
                  autoComplete="username"
                />
              </div>

              <div className="cg-field">
                <label className="cg-field-label" htmlFor="login-password">Password</label>
                <div className="cg-input-wrap">
                  <input
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    className={`cg-input cg-input--with-icon ${error && !password ? 'cg-input--error' : ''}`}
                    value={password}
                    onChange={(event) => { setPassword(event.target.value); setError(''); }}
                    placeholder="Enter your password"
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    className="cg-icon-btn"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    onClick={() => setShowPassword((value) => !value)}
                  >
                    <span className="material-symbols-outlined cg-icon">
                      {showPassword ? 'visibility' : 'visibility_off'}
                    </span>
                  </button>
                </div>
              </div>

              {error && <p className="cg-error-text" role="alert">{error}</p>}

              <button type="submit" className="cg-primary-btn" disabled={isLoading}>
                {isLoading ? (
                  <span className="cg-spinner" aria-hidden="true" />
                ) : null}
                <span>{isLoading ? 'Checking...' : 'Next'}</span>
              </button>

              <p className="cg-footnote">
                Don&apos;t have an account?{' '}
                <button
                  type="button"
                  className="cg-link"
                  onClick={() => {
                    localStorage.removeItem('onboarding_state');
                    try { sessionStorage.removeItem('signup_pending_credentials'); } catch (e) { /* ignore */ }
                    navigate('/signup');
                  }}
                >
                  Create Account
                </button>
              </p>
            </form>
          )}

          {view === 'phone' && (
            <form className="cg-form" onSubmit={handleSendOtp} noValidate>
              <div className="cg-field">
                <label className="cg-field-label" htmlFor="login-phone">Phone Number</label>
                <input
                  id="login-phone"
                  type="tel"
                  className={`cg-input ${phoneError ? 'cg-input--error' : ''}`}
                  value={phone}
                  onChange={(event) => { setPhone(event.target.value); setPhoneError(''); }}
                  placeholder="+91 XXXXX XXXXX"
                />
                {phoneError && <p className="cg-error-text" role="alert">{phoneError}</p>}
              </div>

              {error && <p className="cg-error-text" role="alert">{error}</p>}

              <button type="submit" className="cg-primary-btn" disabled={isLoading}>
                {isLoading ? <span className="cg-spinner" aria-hidden="true" /> : null}
                <span>{isLoading ? 'Sending OTP...' : 'Send OTP'}</span>
              </button>

              <button
                type="button"
                className="cg-back-link"
                onClick={() => { setView('credentials'); setError(''); setPhoneError(''); }}
              >
                Change credentials
              </button>
            </form>
          )}

          {view === 'otp' && (
            <form className="cg-form" onSubmit={handleVerifyOtp} noValidate>
              <div className="cg-otp-row" role="group" aria-label="One time password">
                {otpDigits.map((digit, index) => (
                  <input
                    key={index}
                    ref={(element) => { otpInputRefs.current[index] = element; }}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    className={`cg-otp-digit ${error && !digit ? 'cg-input--error' : ''}`}
                    value={digit}
                    onChange={(event) => handleOtpChange(index, event.target.value)}
                  />
                ))}
              </div>

              {error && <p className="cg-error-text cg-error-text--center" role="alert">{error}</p>}

              <button type="submit" className="cg-primary-btn" disabled={isLoading}>
                {isLoading ? <span className="cg-spinner" aria-hidden="true" /> : null}
                <span>{isLoading ? 'Verifying...' : 'Verify OTP'}</span>
              </button>

              <div className="cg-resend">
                <p className="cg-resend-text">
                  {timer > 0 ? `Resend OTP in 00:${String(timer).padStart(2, '0')}` : "Didn't receive the code?"}
                </p>
                <button
                  type="button"
                  className={`cg-link cg-resend-btn ${timer === 0 ? 'is-active' : ''}`}
                  onClick={handleResend}
                  disabled={timer > 0 || isLoading}
                >
                  Resend OTP
                </button>
              </div>

              <button
                type="button"
                className="cg-back-link"
                onClick={() => { setView('phone'); setError(''); }}
              >
                Change phone number
              </button>
            </form>
          )}
        </div>
      </main>
    </div>
  );
};

export default Login;
