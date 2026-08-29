import { useEffect, useMemo, useState } from 'react';
import { BarChart3, Building2, Crown, LogOut, Menu, ShieldCheck, Users, X } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../../context/AuthContext';
import { getSuperAdminDashboard } from '../../services/api';
import '../AdminPanel/AdminPanel.css';

const formatNumber = (value) => Number.isFinite(Number(value)) ? Number(value).toLocaleString() : 0;

const navItems = [
  { key: 'dashboard', label: 'Dashboard', path: '/super-admin/dashboard', icon: BarChart3 },
  { key: 'admin-panel', label: 'Admin Panel', path: '/super-admin/admin-panel', icon: ShieldCheck },
  { key: 'users', label: 'Manage Users', path: '/super-admin/users', icon: Users },
  { key: 'data', label: 'Manage Data', path: '/super-admin/data', icon: Building2 },
];

const SuperAdminDashboard = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { adminUser, adminLogout } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);

  const activeSection = location.pathname.startsWith('/super-admin/admin-panel') ? 'admin-panel' : location.pathname.startsWith('/super-admin/users') ? 'users' : location.pathname.startsWith('/super-admin/data') ? 'data' : 'dashboard';

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await getSuperAdminDashboard();
        setData(response?.data || null);
      } catch (error) {
        toast.error(error?.response?.data?.detail || 'Unable to load dashboard');
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const summary = useMemo(() => data?.summary || {}, [data]);

  const cards = [
    { label: 'Total registered users', value: summary.totalUsers },
    { label: 'Total colleges', value: summary.totalColleges },
    { label: 'College searches', value: summary.totalCollegeSearches },
    { label: 'College page visits', value: summary.totalCollegeVisits },
    { label: 'Admin users', value: summary.adminUsers },
    { label: 'Super admin users', value: summary.superAdminUsers },
  ];

  const signOut = () => {
    adminLogout();
    navigate('/login', { replace: true });
  };

  if (loading) {
    return <div className="admin-app"><main className="admin-main"><div className="admin-content"><div className="admin-loading">Loading platform metrics...</div></div></main></div>;
  }

  return (
    <div className="admin-app">
      <aside className={`admin-sidebar ${mobileOpen ? 'open' : ''}`}>
        <div className="admin-brand">
          <div className="admin-brand-shell">
            <span className="admin-brand-mark" aria-hidden="true">
              <img src="/favicon.svg" alt="FOURISE" />
            </span>
            <div className="admin-brand-copy">
              <span className="admin-brand-name">Cutoff Guide <b>Super</b></span>
              <small className="admin-brand-company">FOURISE</small>
            </div>
          </div>
          <button className="admin-close" onClick={() => setMobileOpen(false)}><X size={18} /></button>
        </div>
        <nav>
          {navItems.map(({ key, label, path, icon: Icon }) => (
            <button key={key} className={activeSection === key ? 'active' : ''} onClick={() => { navigate(path); setMobileOpen(false); }}>
              <Icon size={18} />{label}
            </button>
          ))}
        </nav>
        <button className="admin-logout" onClick={signOut}><LogOut size={18} />Logout</button>
      </aside>
      {mobileOpen && <button className="admin-overlay" aria-label="Close menu" onClick={() => setMobileOpen(false)} />}

      <main className="admin-main">
        <header className="admin-topbar">
          <button className="admin-menu" onClick={() => setMobileOpen(true)} aria-label="Open menu"><Menu size={21} /></button>
          <div>
            <p className="admin-kicker">SUPER ADMIN</p>
            <h1>{navItems.find(({ key }) => key === activeSection)?.label || 'Platform Overview'}</h1>
          </div>
          <div className="admin-user">
            <span>{adminUser?.name?.slice(0, 1) || 'S'}</span>
            <div>
              <strong>{adminUser?.name || 'Super Admin'}</strong>
              <small>{adminUser?.email || 'super-admin@cutoffguide.ai'}</small>
            </div>
          </div>
        </header>

        <div className="admin-content">
          <section className="admin-welcome">
            <div>
              <p className="admin-kicker">OVERVIEW</p>
              <h2>Monitor the full CutOff Guide platform.</h2>
              <p>Track student activity, college engagement, admin coverage, and search growth in real time.</p>
            </div>
          </section>

          <section className="stat-grid">
            {cards.map((card) => (
              <article className="stat-card" key={card.label}>
                <span>{card.label}</span>
                <strong>{formatNumber(card.value)}</strong>
                <small>Live database stats</small>
              </article>
            ))}
          </section>

          <section className="admin-two-column">
            <Panel title="Most searched colleges">
              <SimpleList items={(data?.mostSearchedColleges || []).map((item) => ({ id: item._id, name: item._id || 'Unknown college', count: item.count }))} empty="No search data yet" primary="name" secondary="count" secondaryFormatter={(value) => `${value} searches`} />
            </Panel>
            <Panel title="Most visited colleges">
              <SimpleList items={(data?.mostVisitedColleges || []).map((item) => ({ id: item._id, name: item._id || 'Unknown college', count: item.count }))} empty="No visit data yet" primary="name" secondary="count" secondaryFormatter={(value) => `${value} visits`} />
            </Panel>
          </section>

          <section className="admin-two-column">
            <Panel title="Recent searches">
              <SimpleList items={(data?.recentSearches || []).map((item) => ({ id: `${item.timestamp}-${item.eventType}`, name: item.metadata?.search || 'College search', count: item.metadata?.page || '-' }))} empty="No recent searches" primary="name" secondary="count" secondaryFormatter={(value) => `Page ${value}`} />
            </Panel>
            <Panel title="Recent college visits">
              <SimpleList items={(data?.recentCollegeVisits || []).map((item) => ({ id: `${item.timestamp}-${item.collegeId}`, name: item.collegeId || 'College visit', count: item.metadata?.college_name || '-' }))} empty="No recent visits" primary="name" secondary="count" secondaryFormatter={(value) => value} />
            </Panel>
          </section>

          <section className="admin-two-column">
            <Panel title="Recent activity">
              <SimpleList items={(data?.recentActivity || []).map((item) => ({ id: `${item.timestamp}-${item.eventType}`, name: item.eventType || 'Activity', count: item.userId || 'System' }))} empty="No recent activity" primary="name" secondary="count" secondaryFormatter={(value) => value} />
            </Panel>
            <Panel title="Recent users">
              <SimpleList items={(data?.recentUsers || []).map((item) => ({ id: item.uid || item.id, name: item.name || 'New user', count: item.email || item.phone || 'No contact' }))} empty="No recent users" primary="name" secondary="count" secondaryFormatter={(value) => value} />
            </Panel>
          </section>
        </div>
      </main>
    </div>
  );
};

const Panel = ({ title, children }) => (
  <section className="admin-panel">
    <div className="panel-heading">
      <h3>{title}</h3>
    </div>
    {children}
  </section>
);

const SimpleList = ({ items = [], empty, primary, secondary, secondaryFormatter = (value) => value }) => {
  if (!items.length) {
    return <p className="empty-state">{empty}</p>;
  }

  return (
    <div className="simple-list">
      {items.map((item) => (
        <div className="simple-row" key={item.id || `${item[primary]}-${Math.random()}`}>
          <div>
            <strong>{item[primary] || 'Untitled'}</strong>
            <small>{secondaryFormatter(item[secondary]) || '—'}</small>
          </div>
          <time>{item.timestamp ? new Date(item.timestamp).toLocaleDateString() : 'Live'}</time>
        </div>
      ))}
    </div>
  );
};

export default SuperAdminDashboard;
