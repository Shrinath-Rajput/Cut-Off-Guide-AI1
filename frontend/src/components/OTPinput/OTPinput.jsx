import { useRef, useEffect } from 'react';
import './OTPinput.css';

const OTPinput = ({ length = 6, value, onChange }) => {
  const refs = useRef([]);

  useEffect(() => {
    // Auto-focus the first box on mount
    refs.current[0]?.focus();
  }, []);

  const handleChange = (index, event) => {
    const nextValue = event.target.value.replace(/\D/g, '').slice(-1);
    const updated = value.split('');
    updated[index] = nextValue;
    onChange(updated.join(''));

    if (nextValue && index < length - 1) {
      refs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (event) => {
    const paste = (event.clipboardData || window.clipboardData).getData('text');
    const digits = paste.replace(/\D/g, '').slice(0, length);
    if (!digits) return;
    const updated = new Array(length).fill('');
    for (let i = 0; i < digits.length; i++) {
      updated[i] = digits[i];
    }
    onChange(updated.join(''));
    // focus the next empty or last
    const nextIndex = Math.min(digits.length, length - 1);
    refs.current[nextIndex]?.focus();
    event.preventDefault();
  };

  const handleKeyDown = (index, event) => {
    if (event.key === 'Backspace' && !value[index] && index > 0) {
      const updated = value.split('');
      updated[index - 1] = '';
      onChange(updated.join(''));
      refs.current[index - 1]?.focus();
    }
  };

  return (
    <div className="otp-group">
      {Array.from({ length }).map((_, index) => (
        <input
          key={index}
          ref={(element) => {
            refs.current[index] = element;
          }}
          value={value[index] || ''}
          onChange={(event) => handleChange(index, event)}
          onKeyDown={(event) => handleKeyDown(index, event)}
          onPaste={handlePaste}
          maxLength="1"
          className="otp-box"
          inputMode="numeric"
          autoComplete="one-time-code"
        />
      ))}
    </div>
  );
};

export default OTPinput;
