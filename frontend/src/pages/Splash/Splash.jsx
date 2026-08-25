import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiZap } from 'react-icons/fi';
import Loader from '../../components/Loader/Loader';
import { useAuth } from '../../context/AuthContext';
import './Splash.css';

const Splash = () => {
  const navigate = useNavigate();
  const { isAuthenticated, loading } = useAuth();

  useEffect(() => {
    if (loading) return undefined;
    const timer = setTimeout(() => {
      navigate(isAuthenticated ? '/home' : '/login', { replace: true });
    }, 1500);
    return () => clearTimeout(timer);
  }, [navigate, isAuthenticated, loading]);

  return (
    <div className="page-shell splash-shell">
      <motion.div
        initial={{ opacity: 0, scale: 0.94 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
        className="glass-panel splash-card"
      >
        <motion.div
          animate={{ y: [0, -10, 0], rotate: [0, 4, -4, 0] }}
          transition={{ duration: 2.3, repeat: Infinity, ease: 'easeInOut' }}
          className="splash-logo"
        >
          <FiZap />
        </motion.div>
        <h1>CutOff Guide AI</h1>
        <p>Crafting your next admission move with clarity and precision.</p>
        <Loader />
      </motion.div>
    </div>
  );
};

export default Splash;
