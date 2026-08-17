import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signInWithPopup } from 'firebase/auth';
import toast from 'react-hot-toast';
import { sendOtp, verifyOtp, googleAuth } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { auth, googleProvider } from '../../firebase';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [view, setView] = useState('phone');

  const [phone, setPhone] = useState('');
  const [phoneError, setPhoneError] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isGoogleSigning, setIsGoogleSigning] = useState(false);

  const [otpDigits, setOtpDigits] = useState(['', '', '', '', '', '']);
  const [otpError, setOtpError] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [timer, setTimer] = useState(30);
  const [isResending, setIsResending] = useState(false);

  const timerIntervalRef = useRef(null);
  const otpInputRefs = useRef([]);

  const pendingUser = sessionStorage.getItem('auth_pending_user');
  const pendingPhone = sessionStorage.getItem('auth_pending_phone');
  const pendingOtpSessionId = sessionStorage.getItem('auth_pending_otp_session_id');
  const parsedUser = pendingUser ? JSON.parse(pendingUser) : null;

  useEffect(() => {
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
  }, []);

  const startTimer = () => {
    setTimer(30);
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    timerIntervalRef.current = setInterval(() => {
      setTimer((value) => {
        if (value <= 1) {
          clearInterval(timerIntervalRef.current);
          return 0;
        }
        return value - 1;
      });
    }, 1000);
  };

  const formatPhoneDisplay = (rawPhone) => {
    const digits = (rawPhone || '').replace(/\D/g, '');
    if (digits.length >= 10) {
      return `+91 ${digits.slice(0, 5)} ${digits.slice(5)}`;
    }
    return '+91 XXXXX XXXXX';
  };

  const handlePhoneChange = (event) => {
    setPhoneError('');
    const normalized = event.target.value.replace(/\D/g, '').slice(0, 10);
    setPhone(normalized);
  };

  const validatePhone = () => {
    if (!/^[0-9]{10}$/.test(phone)) {
      setPhoneError('Enter a valid 10-digit phone number');
      return false;
    }
    return true;
  };

  const handleSendOTP = async (event) => {
    event.preventDefault();
    if (!validatePhone()) return;

    setIsSending(true);
    const phoneNumber = `+91${phone}`;

    try {
      const response = await sendOtp({
        name: `User-${phone}`,
        email: `${phone}@placeholder.local`,
        phone: phoneNumber,
      });

      if (response?.status !== 'success') {
        throw new Error(response?.message || 'Unable to send OTP. Please try again.');
      }

      sessionStorage.setItem(
        'auth_pending_user',
        JSON.stringify({
          name: `User-${phone}`,
          email: `${phone}@placeholder.local`,
        })
      );
      sessionStorage.setItem('auth_pending_phone', phoneNumber);
      if (response?.sessionId) {
        sessionStorage.setItem('auth_pending_otp_session_id', response.sessionId);
      }

      setView('otp');
      setTimeout(() => {
        if (otpInputRefs.current[0]) otpInputRefs.current[0].focus();
        startTimer();
      }, 320);

      toast.success('OTP sent successfully');
    } catch (error) {
      console.error('OTP send error', error);
      const errorMessage =
        error?.response?.data?.message || error?.message || 'Unable to send OTP. Please try again.';
      toast.error(errorMessage);
    } finally {
      setIsSending(false);
    }
  };

  const handleBackToPhone = () => {
    setView('phone');
    setOtpDigits(['', '', '', '', '', '']);
    setOtpError('');
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
  };

  const handleOtpDigitChange = (index, value, event) => {
    setOtpError('');
    const sanitized = value.replace(/[^0-9]/g, '').slice(0, 1);
    const nextDigits = [...otpDigits];
    nextDigits[index] = sanitized;
    setOtpDigits(nextDigits);

    if (sanitized && index < 5) {
      const nextInput = otpInputRefs.current[index + 1];
      if (nextInput) nextInput.focus();
    }

    if (!sanitized && event?.inputType === 'deleteContentBackward' && index > 0) {
      const prevInput = otpInputRefs.current[index - 1];
      if (prevInput) prevInput.focus();
    }
  };

  const handleOtpKeyDown = (index, event) => {
    if (event.key === 'Backspace' && !otpDigits[index] && index > 0) {
      const prevInput = otpInputRefs.current[index - 1];
      if (prevInput) prevInput.focus();
    }
  };

  const handleVerifyOTP = async (event) => {
    event.preventDefault();
    const otpValue = otpDigits.join('');
    if (otpValue.length !== 6) {
      setOtpError('Enter a valid 6-digit OTP');
      return;
    }

    setIsVerifying(true);
    const storedPhone = sessionStorage.getItem('auth_pending_phone');
    const storedUser = sessionStorage.getItem('auth_pending_user');
    const storedSessionId = sessionStorage.getItem('auth_pending_otp_session_id');
    const parsedStoredUser = storedUser ? JSON.parse(storedUser) : null;

    try {
      const response = await verifyOtp({
        phone: storedPhone || `+91${phone}`,
        otp: otpValue,
        name: parsedStoredUser?.name || `User-${phone}`,
        email: parsedStoredUser?.email || `${phone}@placeholder.local`,
        sessionId: storedSessionId,
      });

      const backendUser = response?.user;
      const token = response?.token;

      if (!backendUser || !token) {
        throw new Error(response?.message || 'OTP verification failed');
      }

      login(backendUser, token);
      toast.success('Phone login successful');
      setTimeout(() => navigate('/onboarding'), 600);
    } catch (error) {
      console.error('OTP verify error', error);
      const errorMessage =
        error?.response?.data?.message || error?.message || 'Unable to verify OTP. Please try again.';
      setOtpError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleResend = async () => {
    if (timer > 0 || isResending) return;
    setIsResending(true);
    setOtpError('');

    const storedPhone = sessionStorage.getItem('auth_pending_phone');
    const storedUser = sessionStorage.getItem('auth_pending_user');
    const parsedStoredUser = storedUser ? JSON.parse(storedUser) : null;

    try {
      const response = await sendOtp({
        name: parsedStoredUser?.name || `User-${phone}`,
        email: parsedStoredUser?.email || `${phone}@placeholder.local`,
        phone: storedPhone || `+91${phone}`,
      });

      if (response?.status !== 'success') {
        throw new Error(response?.message || 'Unable to resend OTP. Please try again.');
      }

      if (response?.sessionId) {
        sessionStorage.setItem('auth_pending_otp_session_id', response.sessionId);
      }
      startTimer();
      toast.success('OTP sent successfully');
    } catch (error) {
      console.error('OTP resend error', error);
      const errorMessage =
        error?.response?.data?.message || error?.message || 'Unable to resend OTP. Please try again.';
      setOtpError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsResending(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setIsGoogleSigning(true);

    try {
      const result = await signInWithPopup(auth, googleProvider);
      const firebaseUser = result?.user;

      if (!firebaseUser) {
        throw new Error('Google sign-in did not return a valid user.');
      }

      const idToken = await firebaseUser.getIdToken();
      const response = await googleAuth({
        idToken,
        uid: firebaseUser.uid,
        name: firebaseUser.displayName || 'Google User',
        email: firebaseUser.email || '',
        provider: 'google',
        photoURL: firebaseUser.photoURL || '',
      });

      const backendUser = response?.user;
      const token = response?.token;

      if (!backendUser || !token) {
        throw new Error(response?.message || 'Google sign-in failed. Please try again.');
      }

      login(backendUser, token);
      toast.success('Google login successful');
      setTimeout(() => navigate('/onboarding'), 600);
    } catch (error) {
      console.error('Google sign-in error', error);

      const errorMessage =
        error?.response?.data?.message ||
        error?.message ||
        'Google sign-in failed. Please try again or use phone OTP.';

      if (
        error?.code === 'auth/popup-closed-by-user' ||
        error?.code === 'auth/cancelled-popup-request'
      ) {
        toast.error('Google sign-in was cancelled.');
      } else if (error?.code === 'auth/popup-blocked') {
        toast.error('Google popup was blocked. Please allow popups and try again.');
      } else {
        toast.error(errorMessage);
      }
    } finally {
      setIsGoogleSigning(false);
    }
  };

  const currentPendingPhone = pendingPhone
    ? pendingPhone.replace('+91', '').replace(/\D/g, '')
    : phone;

  return (
    <div className="stitch-auth-page">
      <header className="stitch-auth-header">
        <div className="stitch-auth-brand">
          <span className="material-symbols-outlined stitch-auth-brand-icon" style={{ fontVariationSettings: "'FILL' 1" }}>
            school
          </span>
          <span className="stitch-auth-brand-text">Cutoff Guide AI</span>
        </div>
        <button
          type="button"
          className="stitch-auth-close-btn"
          onClick={() => navigate('/welcome')}
          aria-label="Close"
        >
          <span className="material-symbols-outlined stitch-auth-close-icon">close</span>
        </button>
      </header>

      <main className="stitch-auth-main">
        <div className="stitch-auth-card">
          <div className="stitch-auth-header-section">
            <h1 className="stitch-auth-headline">Let's get you started</h1>
            <p className="stitch-auth-subhead">
              Sign in or create an account to unlock personalized college predictions.
            </p>
          </div>

          <div className="stitch-auth-views">
            <div
              className={`stitch-auth-view stitch-view-phone ${
                view === 'phone' ? 'stitch-view-active' : 'stitch-view-hidden-left'
              }`}
            >
              <button
                type="button"
                className="stitch-google-btn"
                onClick={handleGoogleSignIn}
                disabled={isGoogleSigning}
              >
                <svg className="stitch-google-svg" viewBox="0 0 24 24">
                  <path
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    fill="#4285F4"
                  />
                  <path
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    fill="#34A853"
                  />
                  <path
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    fill="#EA4335"
                  />
                </svg>
                <span className="stitch-google-label">
                  {isGoogleSigning ? 'Redirecting...' : 'Continue with Google'}
                </span>
              </button>

              <div className="stitch-divider">
                <div className="stitch-divider-line" />
                <span className="stitch-divider-label">or</span>
                <div className="stitch-divider-line" />
              </div>

              <form className="stitch-form" onSubmit={handleSendOTP} noValidate>
                <div className="stitch-field">
                  <label className="stitch-field-label" htmlFor="stitch-phone">
                    Phone Number
                  </label>
                  <div className="stitch-phone-shell">
                    <span className="stitch-phone-prefix">+91</span>
                    <input
                      id="stitch-phone"
                      name="phone"
                      type="tel"
                      inputMode="numeric"
                      pattern="[0-9]{10}"
                      placeholder="Enter your 10-digit number"
                      value={phone}
                      onChange={handlePhoneChange}
                      className={`stitch-phone-input ${phoneError ? 'stitch-input-error' : ''}`}
                      required
                    />
                  </div>
                  {phoneError && <p className="stitch-field-error">{phoneError}</p>}
                </div>

                <button
                  type="submit"
                  className="stitch-primary-btn"
                  disabled={isSending}
                >
                  <span>{isSending ? 'Sending OTP...' : 'Send OTP'}</span>
                  <span className="material-symbols-outlined stitch-btn-arrow">arrow_forward</span>
                </button>
              </form>

              <p className="stitch-terms">
                By continuing, you agree to our{' '}
                <a
                  href="/terms"
                  onClick={(e) => {
                    e.preventDefault();
                    navigate('/terms');
                  }}
                  className="stitch-terms-link"
                >
                  Terms of Service
                </a>{' '}
                and{' '}
                <a
                  href="/privacy"
                  onClick={(e) => {
                    e.preventDefault();
                    navigate('/terms');
                  }}
                  className="stitch-terms-link"
                >
                  Privacy Policy
                </a>
                .
              </p>
            </div>

            <div
              className={`stitch-auth-view stitch-view-otp ${
                view === 'otp' ? 'stitch-view-active' : 'stitch-view-hidden-right'
              }`}
            >
              <button
                type="button"
                className="stitch-back-btn"
                onClick={handleBackToPhone}
              >
                <span className="material-symbols-outlined stitch-back-icon">arrow_back</span>
                <span>Back</span>
              </button>

              <div className="stitch-otp-info">
                <p className="stitch-otp-info-text">
                  Enter the 6-digit code sent to
                  <br />
                  <span className="stitch-otp-phone">
                    {formatPhoneDisplay(currentPendingPhone)}
                  </span>
                </p>
              </div>

              <form className="stitch-form" onSubmit={handleVerifyOTP} noValidate>
                <div className="stitch-otp-group">
                  {otpDigits.map((digit, index) => (
                    <input
                      key={index}
                      ref={(el) => (otpInputRefs.current[index] = el)}
                      type="number"
                      inputMode="numeric"
                      className={`stitch-otp-input ${otpError ? 'stitch-input-error' : ''}`}
                      maxLength={1}
                      value={digit}
                      onInput={(e) => handleOtpDigitChange(index, e.target.value, e.nativeEvent)}
                      onKeyDown={(e) => handleOtpKeyDown(index, e)}
                      autoComplete="one-time-code"
                    />
                  ))}
                </div>
                {otpError && <p className="stitch-field-error stitch-otp-error">{otpError}</p>}

                <button
                  type="submit"
                  className={`stitch-primary-btn ${
                    isVerifying === 'success' ? 'stitch-btn-success' : ''
                  }`}
                  disabled={isVerifying}
                >
                  {isVerifying ? (
                    <>
                      <span className="material-symbols-outlined stitch-btn-spin">progress_activity</span>
                      <span>Verifying...</span>
                    </>
                  ) : (
                    <span>Verify OTP</span>
                  )}
                </button>
              </form>

              <div className="stitch-resend-wrap">
                <p className="stitch-resend-question">Didn't receive the code?</p>
                {timer > 0 ? (
                  <button type="button" className="stitch-resend-btn stitch-resend-disabled" disabled>
                    Resend in 00:{timer < 10 ? `0${timer}` : timer}
                  </button>
                ) : (
                  <button
                    type="button"
                    className="stitch-resend-btn stitch-resend-active"
                    onClick={handleResend}
                    disabled={isResending}
                  >
                    {isResending ? 'Resending...' : 'Resend OTP'}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Login;
