import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { signInWithPopup } from 'firebase/auth';
import { loginUser, sendLoginOtp, verifyLoginOtp } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { getFirebaseAuth, getGoogleProvider } from '../../services/firebase';
import WelcomeBackground from '../../components/WelcomeBackground/WelcomeBackground';
import './Login.css';

const getErrorMessage = (error, fallback) => {
  // A thrown request with NO response means it never reached the backend
  // (server not running, wrong port, blocked preflight/CORS, network down).
  // This must NOT be reported as a credential error, otherwise a valid
  // email/password looks like it was rejected when the request simply failed.
  if (error && error.request && !error.response) {
    return 'Cannot reach the server. Please make sure the backend is running on http://127.0.0.1:5000 and try again.';
  }
  const status = error?.response?.status;
  if (status === 503) {
    return 'Service is temporarily unavailable (database not connected). Please try again in a moment.';
  }
  const detail = error?.response?.data?.detail || error?.response?.data?.message;
  if (typeof detail !== 'string') {
    if (typeof status === 'number' && status >= 500) {
      return 'The server encountered an error. Please try again shortly.';
    }
    return fallback;
  }
  if (detail === 'Phone number is not registered for this account') return 'Phone number is not registered for this account.';
  if (status === 404 || detail === 'Not Found' || detail === 'Internal Server Error') return fallback;
  return detail;
};

const OTP_LENGTH = 6;

const Login = () => {
  const navigate = useNavigate();
  const { login, adminLogin } = useAuth();
  const [view, setView] = useState('credentials');
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [error, setError] = useState('');
  const [phoneError, setPhoneError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [timer, setTimer] = useState(0);
  const [pendingLogin, setPendingLogin] = useState(null);
  const otpInputRefs = useRef([]);

  const focusOtpInput = (index) => {
    if (index < 0 || index >= OTP_LENGTH) return;
    requestAnimationFrame(() => {
      otpInputRefs.current[index]?.focus();
    });
  };

  useEffect(() => {
    if (timer <= 0) return undefined;
    const interval = setInterval(() => setTimer((value) => value - 1), 1000);
    return () => clearInterval(interval);
  }, [timer]);

  const handleGoogleLogin = async () => {
    setIsGoogleLoading(true);
    setError('');
    try {
      const auth = getFirebaseAuth();
      const provider = getGoogleProvider();
      const result = await signInWithPopup(auth, provider);
      const user = result.user;
      const token = await user.getIdToken();
      const userPayload = {
        uid: user.uid,
        name: user.displayName || user.email?.split('@')[0] || 'User',
        email: user.email || '',
        phone: user.phoneNumber || '',
        photoURL: user.photoURL || '',
        provider: 'google',
        role: 'USER',
      };

      login(userPayload, token);
      toast.success('Signed in successfully');
      navigate('/home', { replace: true });
    } catch (googleError) {
      if (
        googleError?.code === 'auth/popup-closed-by-user' ||
        googleError?.code === 'auth/cancelled-popup-request' ||
        googleError?.code === 'auth/user-cancelled'
      ) {
        setError('Sign-in cancelled. Please try again.');
      } else if (googleError?.code === 'auth/popup-blocked') {
        setError('Popup was blocked by your browser. Please allow popups and try again.');
      } else if (googleError?.code === 'auth/network-request-failed') {
        setError('Network error during Google sign-in. Please check your connection.');
      } else if (googleError?.code === 'auth/unauthorized-domain') {
        setError('This domain is not authorized in Firebase Console. Please add localhost to Authorized Domains in Firebase.');
      } else if (googleError?.code === 'auth/operation-not-allowed') {
        setError('Google sign-in provider is not enabled in Firebase Console.');
      } else if (
        googleError?.code === 'auth/invalid-api-key' ||
        googleError?.code === 'auth/configuration-not-found' ||
        googleError?.code === 'auth/missing-api-key' ||
        googleError?.code === 'app/no-options'
      ) {
        setError('Firebase authentication configuration error. Please check your setup.');
      } else {
        const errorMsg = googleError?.message;
        setError(typeof errorMsg === 'string' && !errorMsg.includes('Firebase:') ? errorMsg : 'Failed to sign in with Google. Please try again.');
      }
    } finally {
      setIsGoogleLoading(false);
    }
  };

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
      if (response.user?.role === 'ADMIN' || response.user?.role === 'SUPER_ADMIN') {
        adminLogin(response.user, response.token);
        navigate(response.user?.role === 'SUPER_ADMIN' ? '/super-admin/dashboard' : '/admin/dashboard', { replace: true });
        return;
      }
      if (response.requiresOtp || response.status === 'pending_otp') {
        setPendingLogin({
          uid: response.uid || response.user?.uid,
          name: response.user?.name || '',
          email: response.user?.email || '',
        });
        setPhone('');
        setView('phone');
        return;
      }
      // Safety fallback: if somehow a token was returned for a non-admin, enforce phone step
      if (response.user?.role === 'USER') {
        setPendingLogin({
          uid: response.uid || response.user?.uid,
          name: response.user?.name || '',
          email: response.user?.email || '',
        });
        setPhone('');
        setView('phone');
        return;
      }
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Invalid username/email or password.'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendOtp = async (event) => {
    if (event?.preventDefault) event.preventDefault();
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
      setOtp(['', '', '', '', '', '']);
      setTimer(30);
      setView('otp');
      toast.success('OTP sent successfully');
      setTimeout(() => otpInputRefs.current[0]?.focus(), 50);
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Unable to send OTP. Please try again.'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOtp = async (event) => {
    if (event?.preventDefault) event.preventDefault();
    const otpValue = otp.join('');
    if (otpValue.length !== 6) {
      setError('Enter the 6-digit OTP.');
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      const response = await verifyLoginOtp({
        uid: pendingLogin.uid,
        phone,
        otp: otpValue,
        sessionId: sessionStorage.getItem('auth_pending_otp_session_id') || '',
      });
      if (response.token && response.user) {
        login(response.user, response.token);
        sessionStorage.removeItem('auth_pending_otp_session_id');
        toast.success('Signed in successfully');
        navigate('/home', { replace: true });
      } else {
        setError('Verification failed. Please try again.');
      }
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Invalid or expired OTP. Please try again.'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleOtpChange = (index, rawValue) => {
    const digit = String(rawValue || '').replace(/\D/g, '').slice(-1);
    setError('');
    setOtp((current) => {
      const next = [...current];
      next[index] = digit;
      return next;
    });

    if (digit && index < OTP_LENGTH - 1) {
      requestAnimationFrame(() => otpInputRefs.current[index + 1]?.focus());
    }
  };

  const handleOtpKeyDown = (event, index) => {
    if (event.key === 'Backspace') {
      setError('');
      if (otp[index]) {
        event.preventDefault();
        setOtp((current) => {
          const next = [...current];
          next[index] = '';
          return next;
        });
        return;
      }

      if (index > 0) {
        event.preventDefault();
        setOtp((current) => {
          const next = [...current];
          next[index - 1] = '';
          return next;
        });
        focusOtpInput(index - 1);
      }
      return;
    }

    if (event.key === 'ArrowLeft' && index > 0) {
      event.preventDefault();
      focusOtpInput(index - 1);
      return;
    }

    if (event.key === 'ArrowRight' && index < OTP_LENGTH - 1) {
      event.preventDefault();
      focusOtpInput(index + 1);
    }
  };

  const handleOtpPaste = (event, index) => {
    event.preventDefault();
    const pasted = event.clipboardData.getData('text').replace(/\D/g, '').slice(0, OTP_LENGTH);
    if (!pasted) return;
    setError('');
    setOtp((current) => {
      const next = [...current];
      pasted.split('').forEach((digit, offset) => {
        if (index + offset < OTP_LENGTH) next[index + offset] = digit;
      });
      return next;
    });
    requestAnimationFrame(() => otpInputRefs.current[Math.min(index + pasted.length - 1, OTP_LENGTH - 1)]?.focus());
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
      <WelcomeBackground />
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

              <div className="cg-divider">
                <span>or</span>
              </div>

              <button
                type="button"
                className="cg-google-btn"
                onClick={handleGoogleLogin}
                disabled={isLoading || isGoogleLoading}
              >
                <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google logo" className="cg-google-icon" />
                <span>{isGoogleLoading ? 'Connecting...' : 'Continue with Google'}</span>
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
                  className={`cg-input ${phoneError || error ? 'cg-input--error' : ''}`}
                  value={phone}
                  onChange={(event) => { setPhone(event.target.value); setPhoneError(''); setError(''); }}
                  placeholder="Enter 10-digit mobile number"
                  maxLength={10}
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
                {otp.map((digit, index) => (
                  <input
                    key={index}
                    ref={(element) => { otpInputRefs.current[index] = element; }}
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={1}
                    autoComplete="one-time-code"
                    className={`cg-otp-digit ${error && !digit ? 'cg-input--error' : ''}`}
                    value={digit}
                    onChange={(event) => handleOtpChange(index, event.target.value)}
                    onKeyDown={(event) => handleOtpKeyDown(event, index)}
                    onPaste={(event) => handleOtpPaste(event, index)}
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
