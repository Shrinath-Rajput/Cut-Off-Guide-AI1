import { motion } from 'framer-motion';
import './Loader.css';

const Loader = () => {
  return (
    <div className="loader-shell" aria-label="Loading">
      <motion.div
        className="loader-orb"
        animate={{ rotate: 360, scale: [1, 1.06, 1] }}
        transition={{ duration: 1.3, repeat: Infinity, ease: 'linear' }}
      />
      <motion.div
        className="loader-ring"
        animate={{ rotate: -360 }}
        transition={{ duration: 1.8, repeat: Infinity, ease: 'linear' }}
      />
    </div>
  );
};

export default Loader;
