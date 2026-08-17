import './Input.css';

const Input = ({ label, type = 'text', icon, name, value, onChange, error, ...props }) => {
  return (
    <div className="field-group">
      <label className="field-label" htmlFor={name}>{label}</label>
      <div className={`input-shell ${error ? 'has-error' : ''}`}>
        {icon ? <span className="input-icon">{icon}</span> : null}
        <input
          id={name}
          name={name}
          type={type}
          value={value}
          onChange={onChange}
          className="premium-input"
          {...props}
        />
      </div>
      {error ? <p className="field-error">{error}</p> : null}
    </div>
  );
};

export default Input;
