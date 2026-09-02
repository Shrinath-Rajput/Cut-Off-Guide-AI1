import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { registerUser, sendOtp } from '../../services/api';
import { useOnboarding } from '../../context/OnboardingContext';
import './Signup.css';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PWD_LEN = /.{8,}/;
const PWD_UPPER = /[A-Z]/;
const PWD_NUMBER = /[0-9]/;
const PWD_SPECIAL = /[!@#$%^&*()_\-+=\[\]{};:'"\\|,.<>\/?`~]/;

const normalizePhone = (raw) => {
  if (!raw) return '';
  let digits = String(raw).replace(/\D/g, '');
  if (digits.startsWith('91') && digits.length === 12) digits = digits.slice(2);
  if (digits.startsWith('0') && digits.length === 11) digits = digits.slice(1);
  return digits;
};

const PENDING_KEY = 'signup_pending_credentials';

const Signup = () => {
  const navigate = useNavigate();
  const { resetOnboarding, setPersonal, studentProfile } = useOnboarding();

  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(PENDING_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed.email) setEmail(parsed.email);
        if (parsed.phone) setPhone(parsed.phone);
        if (parsed.password) setPassword(parsed.password);
        if (parsed.confirmPassword) setConfirmPassword(parsed.confirmPassword);
      }
    } catch (e) {
      /* ignore */
    }
  }, []);

  const rules = useMemo(() => [
    { key: 'length', label: 'Minimum 8 characters', test: (v) => PWD_LEN.test(v) },
    { key: 'upper', label: 'One uppercase letter', test: (v) => PWD_UPPER.test(v) },
    { key: 'number', label: 'One number', test: (v) => PWD_NUMBER.test(v) },
    { key: 'special', label: 'One special character', test: (v) => PWD_SPECIAL.test(v) },
  ], []);

  const allRulesPass = useMemo(
    () => password.length > 0 && rules.every((r) => r.test(password)),
    [password, rules]
  );

  const validate = () => {
    const next = {};
    const trimmedEmail = email.trim().toLowerCase();
    if (!trimmedEmail) {
      next.email = 'Email is required.';
    } else if (!EMAIL_REGEX.test(trimmedEmail)) {
      next.email = 'Please enter a valid email address.';
    }

    const normalizedPhone = normalizePhone(phone);
    if (!normalizedPhone) {
      next.phone = 'Phone number is required.';
    } else if (!/^\d{10}$/.test(normalizedPhone)) {
      next.phone = 'Please enter a valid phone number.';
    }

    if (!password) {
      next.password = 'Password is required.';
    } else if (!allRulesPass) {
      next.password = 'Password does not meet the requirements.';
    }

    if (!confirmPassword) {
      next.confirmPassword = 'Please confirm your password.';
    } else if (password !== confirmPassword) {
      next.confirmPassword = 'Passwords do not match.';
    }

    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isLoading) return;
    if (!validate()) return;

    try {
      setIsLoading(true);

      const normalizedEmail = email.trim().toLowerCase();
      const normalizedPhone = normalizePhone(phone);
      const generatedName = (email.split('@')[0] || 'Student')
        .trim()
        .replace(/\s+/g, ' ')
        .replace(/(^\w|\s\w)/g, (match) => match.toUpperCase());

      resetOnboarding();

      const pendingCreds = {
        email: normalizedEmail,
        phone: normalizedPhone,
        password,
        confirmPassword,
        fullName: generatedName,
        domicile: '',
        locationZone: '',
        name: generatedName,
      };
      sessionStorage.setItem(PENDING_KEY, JSON.stringify(pendingCreds));

      setPersonal({
        fullName: generatedName,
        email: normalizedEmail,
        category: '',
        pwdCrossCategory: false,
        phone: normalizedPhone,
        domicile: '',
      });

      toast.success('Signup data saved. Please complete onboarding.', {
        icon: '✅',
      });

      navigate('/onboarding', { replace: true });
    } catch (error) {
      const detail = error?.response?.data?.detail || error?.response?.data?.message || error?.message || 'Something went wrong. Please try again.';
      toast.error(detail);
      setErrors((prev) => ({ ...prev, submit: detail }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignInClick = () => {
    try {
      sessionStorage.removeItem(PENDING_KEY);
    } catch (e) {
      /* ignore */
    }
    navigate('/login');
  };

  const handleFieldChange = (field, setter, value) => {
    setter(value);
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  return (
    <div className="cg-signup-page">
      <div className="cg-signup-left">
        <div className="cg-signup-left-art" aria-hidden="true">
          <div className="cg-signup-blob cg-signup-blob--a" />
          <div className="cg-signup-blob cg-signup-blob--b" />
          <div className="cg-signup-blob cg-signup-blob--c" />
        </div>
        <div className="cg-signup-left-overlay" aria-hidden="true" />
        <div className="cg-signup-left-content">
          <div className="cg-signup-brand-badge" aria-hidden="true">
            <span className="material-symbols-outlined">school</span>
          </div>
          <h1 className="cg-signup-left-title">Master Your Admissions Journey.</h1>
          <p className="cg-signup-left-subtitle">
            Join ambitious students making data-driven decisions with unparalleled academic clarity.
          </p>
        </div>
      </div>

      <div className="cg-signup-right">
        <div className="cg-signup-right-inner">
          <div className="cg-signup-mobile-brand" aria-hidden="true">
            <span className="material-symbols-outlined">school</span>
            <span className="cg-signup-mobile-name">Cutoff Guide AI</span>
          </div>

          <div className="cg-signup-card">
            <div className="cg-signup-card-header">
              <h1 className="cg-signup-card-title">Create Account</h1>
              <p className="cg-signup-card-subtitle">
                Enter your details to access premium admission insights.
              </p>
            </div>

            <form className="cg-signup-form" onSubmit={handleSubmit} noValidate>
              <div className="cg-signup-field">
                <label className="cg-signup-label" htmlFor="signup-email">
                  Email
                </label>
                <div className="cg-signup-input-wrap">
                  <input
                    id="signup-email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    className={`cg-signup-input ${errors.email ? 'cg-signup-input--error' : ''}`}
                    placeholder="name@example.com"
                    value={email}
                    onChange={(e) => handleFieldChange('email', setEmail, e.target.value)}
                    disabled={isLoading}
                  />
                </div>
                {errors.email && <p className="cg-signup-error" role="alert">{errors.email}</p>}
              </div>

              <div className="cg-signup-field">
                <label className="cg-signup-label" htmlFor="signup-phone">
                  Phone number
                </label>
                <div className="cg-signup-input-wrap">
                  <input
                    id="signup-phone"
                    name="phone"
                    type="tel"
                    autoComplete="tel"
                    inputMode="tel"
                    className={`cg-signup-input ${errors.phone ? 'cg-signup-input--error' : ''}`}
                    placeholder="+1 (555) 000-0000"
                    value={phone}
                    onChange={(e) => handleFieldChange('phone', setPhone, e.target.value)}
                    disabled={isLoading}
                  />
                </div>
                {errors.phone && <p className="cg-signup-error" role="alert">{errors.phone}</p>}
              </div>

              <div className="cg-signup-field">
                <label className="cg-signup-label" htmlFor="signup-password">
                  Password
                </label>
                <div className="cg-signup-input-wrap cg-signup-input-wrap--icon">
                  <input
                    id="signup-password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    className={`cg-signup-input ${errors.password ? 'cg-signup-input--error' : ''}`}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => handleFieldChange('password', setPassword, e.target.value)}
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    className="cg-signup-toggle"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    onClick={() => setShowPassword((v) => !v)}
                    tabIndex={0}
                    disabled={isLoading}
                  >
                    <span className="material-symbols-outlined">
                      {showPassword ? 'visibility_off' : 'visibility'}
                    </span>
                  </button>
                </div>
              </div>

              <div className="cg-signup-field">
                <label className="cg-signup-label" htmlFor="signup-confirm-password">
                  Confirm Password
                </label>
                <div className="cg-signup-input-wrap cg-signup-input-wrap--icon">
                  <input
                    id="signup-confirm-password"
                    name="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    className={`cg-signup-input ${errors.confirmPassword ? 'cg-signup-input--error' : ''}`}
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) =>
                      handleFieldChange('confirmPassword', setConfirmPassword, e.target.value)
                    }
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    className="cg-signup-toggle"
                    aria-label={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
                    onClick={() => setShowConfirmPassword((v) => !v)}
                    tabIndex={0}
                    disabled={isLoading}
                  >
                    <span className="material-symbols-outlined">
                      {showConfirmPassword ? 'visibility_off' : 'visibility'}
                    </span>
                  </button>
                </div>
                {(errors.password || errors.confirmPassword) && (
                  <p className="cg-signup-error" role="alert">
                    {errors.password || errors.confirmPassword}
                  </p>
                )}
              </div>

              <div className="cg-signup-requirements" aria-live="polite">
                <p className="cg-signup-req-title">Password Requirements:</p>
                <ul className="cg-signup-req-list">
                  {rules.map((rule) => {
                    const valid = password.length > 0 && rule.test(password);
                    return (
                      <li
                        key={rule.key}
                        className={`cg-signup-req-item ${valid ? 'cg-signup-req-item--valid' : ''}`}
                      >
                        <span className="cg-signup-req-icon" aria-hidden="true">
                          {valid ? '✓' : '○'}
                        </span>
                        <span>{rule.label}</span>
                      </li>
                    );
                  })}
                </ul>
              </div>

              <button
                type="submit"
                className="cg-signup-submit"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <span className="cg-signup-spinner" aria-hidden="true" />
                    <span>Creating account...</span>
                  </>
                ) : (
                  <span>Continue</span>
                )}
              </button>

              <div className="cg-divider">
                <span>or</span>
              </div>

              <a href="http://localhost:5000/api/auth/google" className="cg-google-btn">
                <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google logo" className="cg-google-icon" />
                <span>Continue with Google</span>
              </a>
            </form>
          </div>

          <div className="cg-signup-footer">
            Already have an account?
            <button
              type="button"
              className="cg-signup-link"
              onClick={handleSignInClick}
            >
              Sign In
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup;
export { PENDING_KEY as SIGNUP_PENDING_KEY };
