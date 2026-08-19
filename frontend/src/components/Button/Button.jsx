import { motion } from 'framer-motion';
import './Button.css';

const Button = ({ children, variant = 'primary', fullWidth = false, icon, className = '', ...props }) => {
  return (
    <motion.button
      whileHover={{ y: -2, scale: 1.01 }}
      whileTap={{ scale: 0.98 }}
      className={`premium-button ${variant} ${fullWidth ? 'full-width' : ''} ${className}`.trim()}
      {...props}
    >
      {icon ? <span className="button-icon">{icon}</span> : null}
      <span>{children}</span>
    </motion.button>
  );
};

export default Button;
