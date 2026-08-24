import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { sendOtp, verifyOtp } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import './OTP.css';

const getErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail || error?.response?.data?.message || error?.message;
  if (typeof detail === 'string' && detail && detail !== 'Internal Server Error' && detail !== 'Not Found') return detail;
  return fallback;
};

const INITIAL_COUNTDOWN = 60;
const OTP_LENGTH = 6;

const OTP = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [error, setError] = useState('');
  const [timer, setTimer] = useState(INITIAL_COUNTDOWN);
  const [isVerifying, setIsVerifying] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const inputRefs = useRef([]);

  const focusInput = (index) => {
    if (index < 0 || index >= OTP_LENGTH) return;
    requestAnimationFrame(() => {
      inputRefs.current[index]?.focus();
    });
  };

  const pendingUser = sessionStorage.getItem('auth_pending_user');
  const pendingPhone = sessionStorage.getItem('auth_pending_phone');
  const pendingOtpSessionId = sessionStorage.getItem('auth_pending_otp_session_id');
  const parsedUser = pendingUser ? JSON.parse(pendingUser) : null;

  useEffect(() => {
    if (!parsedUser || !pendingPhone) {
      navigate('/login', { replace: true });
      return;
    }
    requestAnimationFrame(() => inputRefs.current[0]?.focus());
  }, [navigate, pendingPhone, pendingUser]);

  useEffect(() => {
    if (timer <= 0) return undefined;
    const interval = setInterval(() => setTimer((value) => value - 1), 1000);
    return () => clearInterval(interval);
  }, [timer]);

  const maskPhone = (phone) => {
    if (!phone) return '';
    const digits = String(phone).replace(/\D/g, '').slice(-10);
    if (digits.length !== 10) return phone;
    return `*** *** ${digits.slice(-4)}`;
  };

  const handleDigitChange = (index, rawValue) => {
    const digit = String(rawValue || '').replace(/\D/g, '').slice(-1);
    setError('');
    setOtp((current) => {
      const next = [...current];
      next[index] = digit;
      return next;
    });

    if (digit && index < OTP_LENGTH - 1) {
      requestAnimationFrame(() => inputRefs.current[index + 1]?.focus());
    }
  };

  const handleKeyDown = (event, index) => {
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
        focusInput(index - 1);
      }
      return;
    }

    if (event.key === 'ArrowLeft' && index > 0) {
      event.preventDefault();
      focusInput(index - 1);
      return;
    }

    if (event.key === 'ArrowRight' && index < OTP_LENGTH - 1) {
      event.preventDefault();
      focusInput(index + 1);
    }
  };

  const handlePaste = (event, index) => {
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
    requestAnimationFrame(() => inputRefs.current[Math.min(index + pasted.length - 1, OTP_LENGTH - 1)]?.focus());
  };

  const handleVerify = async (event) => {
    event.preventDefault();
    const otpValue = otp.join('');
    if (otpValue.length !== 6) {
      setError('Please enter all 6 digits.');
      return;
    }
    setIsVerifying(true);
    setError('');
    try {
      const isSignupFlow = sessionStorage.getItem('signup_from_onboarding') === 'true';
      const completePayloadRaw = sessionStorage.getItem('signup_complete_payload');
      const completePayload = completePayloadRaw ? JSON.parse(completePayloadRaw) : null;

      const verifyPayload = {
        phone: pendingPhone,
        otp: otpValue,
        name: parsedUser?.name || '',
        email: parsedUser?.email || '',
        sessionId: pendingOtpSessionId,
      };

      if (isSignupFlow && completePayload) {
        verifyPayload.registerPayload = completePayload;
      }

      const response = await verifyOtp(verifyPayload);
      const backendUser = response?.user;
      const token = response?.token;
      if (!backendUser || !token) throw new Error(response?.message || 'OTP verification failed');
      login(backendUser, token);

      sessionStorage.removeItem('auth_pending_otp_session_id');
      sessionStorage.removeItem('auth_pending_user');
      sessionStorage.removeItem('auth_pending_phone');
      sessionStorage.removeItem('signup_from_onboarding');
      sessionStorage.removeItem('signup_complete_payload');
      sessionStorage.removeItem('signup_pending_credentials');
      localStorage.removeItem('onboarding_state');

      if (response?.newAccount) {
        toast.success('Account created successfully! Welcome to Cutoff Guide AI.', { icon: '🎉' });
      } else {
        toast.success('Signed in successfully');
      }
      navigate('/home', { replace: true });
    } catch (requestError) {
      const message = getErrorMessage(requestError, 'Invalid code. Please try again.');
      setError(message);
      toast.error(message);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleResend = async () => {
    if (timer > 0 || isResending || !pendingPhone) return;
    setIsResending(true);
    setError('');
    try {
      const response = await sendOtp({
        name: parsedUser?.name || '',
        email: parsedUser?.email || '',
        phone: pendingPhone,
      });
      if (response?.sessionId) {
        sessionStorage.setItem('auth_pending_otp_session_id', response.sessionId);
      }
      setOtp(['', '', '', '', '', '']);
      setTimer(INITIAL_COUNTDOWN);
      toast.success('OTP sent successfully.');
      focusInput(0);
    } catch (requestError) {
      const message = getErrorMessage(requestError, 'Unable to resend OTP. Please try again.');
      setError(message);
      toast.error(message);
    } finally {
      setIsResending(false);
    }
  };

  const handleChangePhone = () => {
    sessionStorage.removeItem('auth_pending_otp_session_id');
    navigate('/login', { replace: true });
  };

  const countdownLabel =
    timer > 0 ? `Available in 00:${String(timer).padStart(2, '0')}` : 'Ready to resend';
  const resendDisabled = timer > 0 || isResending;

  return (
    <div className="cg-otp-page">
      <div className="cg-otp-bg" aria-hidden="true">
        <div className="cg-otp-blob cg-otp-blob--top" />
        <div className="cg-otp-blob cg-otp-blob--bottom" />
      </div>

      <main className="cg-otp-shell">
        <div className="cg-otp-brand">
          <div className="cg-otp-badge">
            <span className="material-symbols-outlined cg-otp-badge-icon fill-icon">school</span>
          </div>
          <h1 className="cg-otp-brand-text">Cutoff Guide AI</h1>
        </div>

        <div className="cg-otp-card">
          <span className="cg-otp-card-accent" aria-hidden="true" />

          <div className="cg-otp-copy">
            <h2 className="cg-otp-title">Verify Your Phone</h2>
            <p className="cg-otp-subtitle">
              We&apos;ve sent a 6-digit verification code to
            </p>
            <p className="cg-otp-phone" aria-label={`Masked phone number ending with ${maskPhone(pendingPhone).slice(-4)}`}>
              {maskPhone(pendingPhone)}
            </p>
          </div>

          <form className="cg-otp-form" onSubmit={handleVerify} noValidate>
            <div className="cg-otp-row" role="group" aria-label="One-time password">
              {otp.map((digit, index) => (
                <input
                  key={index}
                  ref={(element) => { inputRefs.current[index] = element; }}
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  autoComplete="one-time-code"
                  maxLength={1}
                  className={`cg-otp-digit ${error && !digit ? 'cg-otp-digit--error' : ''}`}
                  value={digit}
                  aria-label={`OTP digit ${index + 1}`}
                  onChange={(event) => handleDigitChange(index, event.target.value)}
                  onKeyDown={(event) => handleKeyDown(event, index)}
                  onPaste={(event) => handlePaste(event, index)}
                />
              ))}
            </div>

            {error && <p className="cg-otp-error" role="alert">{error}</p>}

            <button type="submit" className="cg-otp-verify" disabled={isVerifying}>
              {isVerifying ? (
                <>
                  <span className="cg-otp-spinner" aria-hidden="true" />
                  <span>Verifying...</span>
                </>
              ) : (
                <>
                  <span>Verify OTP</span>
                  <span className="material-symbols-outlined cg-otp-arrow">arrow_forward</span>
                </>
              )}
            </button>

            <div className="cg-otp-resend">
              <p className="cg-otp-resend-copy">
                Didn&apos;t receive the code?{' '}
                <button
                  type="button"
                  className={`cg-otp-resend-link ${resendDisabled ? 'is-disabled' : ''}`}
                  onClick={handleResend}
                  disabled={resendDisabled}
                >
                  {isResending ? 'Resending...' : 'Resend OTP'}
                </button>
              </p>
              <p className={`cg-otp-countdown ${timer === 0 ? 'is-ready' : ''}`}>
                {countdownLabel}
              </p>
            </div>

            <button
              type="button"
              className="cg-otp-back"
              onClick={handleChangePhone}
            >
              <span className="material-symbols-outlined cg-otp-back-icon">edit</span>
              <span>Change phone number</span>
            </button>
          </form>
        </div>
      </main>
    </div>
  );
};

export default OTP;
