import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { sendOtp, verifyOtp } from '../../services/api';
import Button from '../../components/Button/Button';
import OTPinput from '../../components/OTPinput/OTPinput';
import { useAuth } from '../../context/AuthContext';
import './OTP.css';

const OTP = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [timer, setTimer] = useState(30);
  const [isVerifying, setIsVerifying] = useState(false);
  const [isResending, setIsResending] = useState(false);

  const pendingUser = sessionStorage.getItem('auth_pending_user');
  const pendingPhone = sessionStorage.getItem('auth_pending_phone');
  const pendingOtpSessionId = sessionStorage.getItem('auth_pending_otp_session_id');
  const parsedUser = pendingUser ? JSON.parse(pendingUser) : null;

  useEffect(() => {
    if (!parsedUser || !pendingPhone) {
      navigate('/login');
    }
  }, [navigate, parsedUser, pendingPhone]);

  useEffect(() => {
    if (timer <= 0) return;
    const interval = setInterval(() => setTimer((value) => value - 1), 1000);
    return () => clearInterval(interval);
  }, [timer]);

  const handleVerify = async () => {
    if (otp.length !== 6) {
      setError('Enter a valid 6-digit OTP');
      return;
    }

    setIsVerifying(true);

    try {
      const response = await verifyOtp({
        phone: pendingPhone,
        otp,
        name: parsedUser?.name || '',
        email: parsedUser?.email || '',
        sessionId: pendingOtpSessionId,
      });

      const backendUser = response?.user;
      const token = response?.token;

      if (!backendUser || !token) {
        throw new Error(response?.message || 'OTP verification failed');
      }

      login(backendUser, token);
      toast.success('Phone login successful');
      navigate('/onboarding');
    } catch (error) {
      console.error('OTP verify error', error);
      const errorMessage =
        error?.response?.data?.message || error?.message || 'Unable to verify OTP. Please try again.';
      setError(errorMessage);
      toast.error(errorMessage);
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

      if (response?.status !== 'success') {
        throw new Error(response?.message || 'Unable to resend OTP. Please try again.');
      }

      if (response?.sessionId) {
        sessionStorage.setItem('auth_pending_otp_session_id', response.sessionId);
      }
      setTimer(30);
      toast.success('OTP sent successfully');
    } catch (error) {
      console.error('OTP resend error', error);
      const errorMessage =
        error?.response?.data?.message || error?.message || 'Unable to resend OTP. Please try again.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsResending(false);
    }
  };

  const handleOtpChange = (value) => {
    setError('');
    setOtp(value);
  };

  const maskPhone = (phone) => {
    if (!phone) return '';
    const digits = phone.replace(/\D/g, '');
    if (digits.length >= 10) {
      const last4 = digits.slice(-4);
      return `+91 XXXXX ${last4}`;
    }
    return phone;
  };

  return (
    <div className="auth-shell otp-shell">
      <main className="otp-card">
        <div className="otp-brand">
          <span className="material-symbols-outlined otp-brand-icon">school</span>
          <span>Cut-Off Guide AI</span>
        </div>

        <div className="otp-copy">
          <h1>Verify your phone number</h1>
          <p>
            We've sent a 6-digit verification code to <strong>{maskPhone(pendingPhone)}</strong>
          </p>
        </div>

        <div className="otp-input-shell">
          <OTPinput value={otp} onChange={handleOtpChange} />
        </div>

        {error && <div className="otp-error">{error}</div>}

        <div className="otp-meta">
          <span>Resend in <strong>00:{timer < 10 ? `0${timer}` : timer}</strong></span>
          <button className="otp-resend" type="button" onClick={handleResend} disabled={timer > 0 || isResending}>
            {isResending ? 'Resending...' : 'Resend Code'}
          </button>
        </div>

        <div className="otp-actions">
          <Button variant="primary" fullWidth onClick={handleVerify} disabled={isVerifying}>
            {isVerifying ? 'Verifying...' : 'Verify OTP'}
          </Button>
          <Button variant="ghost" fullWidth onClick={() => navigate('/login')}>
            Change number
          </Button>
        </div>

        <p className="otp-footer">© 2024 Cut-Off Guide AI. Secure Verification.</p>
      </main>
    </div>
  );
};

export default OTP;
