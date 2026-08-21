import { useState } from 'react';
import { ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { adminLogin as adminLoginApi } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import './AdminLogin.css';

const AdminLogin = () => {
  const navigate = useNavigate();
  const { adminLogin: saveAdminSession } = useAuth();
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await adminLoginApi(credentials);
      saveAdminSession(response.user, response.token);
      navigate('/admin/dashboard', { replace: true });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Unable to sign in');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="admin-login-shell">
      <section className="admin-login-card">
        <div className="admin-mark"><ShieldCheck size={28} /></div>
        <p className="admin-kicker">CUTOFF GUIDE AI</p>
        <h1>Admin Login</h1>
        <p className="admin-login-copy">Sign in with an authorized administrator account to manage the guide.</p>
        <form onSubmit={submit} className="admin-form">
          <label>Email<input type="email" required value={credentials.email} onChange={(event) => setCredentials({ ...credentials, email: event.target.value })} /></label>
          <label>Password<input type="password" required value={credentials.password} onChange={(event) => setCredentials({ ...credentials, password: event.target.value })} /></label>
          <button className="admin-primary-button" disabled={loading}>{loading ? 'Checking access...' : 'Login'}</button>
        </form>
        <button className="admin-back-link" onClick={() => navigate('/login')}>Return to Cutoff Guide</button>
      </section>
    </main>
  );
};

export default AdminLogin;
