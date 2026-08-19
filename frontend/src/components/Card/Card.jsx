import { motion } from 'framer-motion';
import './Card.css';

const Card = ({ children, className = '', glow = false, ...props }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
      className={`premium-card ${glow ? 'glow' : ''} ${className}`.trim()}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export default Card;
