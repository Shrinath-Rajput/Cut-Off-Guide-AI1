import { useEffect, useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { ArrowLeft, Bookmark, Bot, FileText, GitCompareArrows, GraduationCap, House, LogOut, Mail, Menu, Search, ShieldCheck, UserRound, UsersRound, X } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import './Navbar.css';

const navLinks = [
  { label: 'Home', to: '/home', icon: House },
  { label: 'About', to: '/about', icon: UsersRound },
  { label: 'Colleges', to: '/colleges', icon: GraduationCap },
  { label: 'Compare', to: '/compare', icon: GitCompareArrows },
  { label: 'Cutoff / Result', to: '/cutoff', icon: FileText },
  { label: 'AI Assistant', to: '/assistant', icon: Bot },
  { label: 'Saved Colleges', to: '/saved', icon: Bookmark },
  { label: 'Contact', to: '/contact', icon: Mail },
];

const Navbar = ({ title, backTo = '/welcome', onSearch, bookmarkTo = '/saved', profileTo = '/profile' }) => {
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profilePhoto, setProfilePhoto] = useState('');
  const { currentUser, logout } = useAuth();

  useEffect(() => {
    const avatarStorageKey = currentUser
      ? `profile-avatar-${currentUser.uid || currentUser.id || currentUser.email}`
      : null;

    const updateProfilePhoto = () => {
      setProfilePhoto(avatarStorageKey ? localStorage.getItem(avatarStorageKey) || '' : '');
    };

    updateProfilePhoto();
    const photoRefresh = window.setInterval(updateProfilePhoto, 500);
    window.addEventListener('storage', updateProfilePhoto);

    return () => {
      window.clearInterval(photoRefresh);
      window.removeEventListener('storage', updateProfilePhoto);
    };
  }, [currentUser]);

  const handleLogout = () => {
    setMobileOpen(false);
    logout();
    navigate('/login', { replace: true });
  };

  const handleSearch = () => {
    if (onSearch) {
      onSearch();
      return;
    }
    navigate('/colleges');
  };

  useEffect(() => {
    if (!mobileOpen) return undefined;

    const closeOnEscape = (event) => {
      if (event.key === 'Escape') setMobileOpen(false);
    };

    document.addEventListener('keydown', closeOnEscape);
    document.body.classList.add('drawer-open');
    return () => {
      document.removeEventListener('keydown', closeOnEscape);
      document.body.classList.remove('drawer-open');
    };
  }, [mobileOpen]);

  if (title) {
    return (
      <nav className="topbar auth-nav">
        <button type="button" className="nav-back" onClick={() => navigate(backTo)}>
          <ArrowLeft />
        </button>
        <span className="nav-title">{title}</span>
        <div className="nav-spacer" />
      </nav>
    );
  }

  return (
    <header className="site-navbar">
      <div className="navbar-inner">
        <Link to="/home" className="brand-link" onClick={() => setMobileOpen(false)}>
          Cutoff Guide AI
        </Link>

        <div className={`mobile-drawer ${mobileOpen ? 'open' : ''}`} aria-hidden={!mobileOpen}>
          <div className="drawer-header">
            <Link to="/home" className="drawer-brand" onClick={() => setMobileOpen(false)}>
              <strong>Cutoff Guide AI</strong>
              <span>AI-Powered Admission Prediction</span>
            </Link>
            <button type="button" className="drawer-close" aria-label="Close navigation menu" onClick={() => setMobileOpen(false)}>
              <X size={22} />
            </button>
          </div>

          <nav className="site-menu" aria-label="Mobile navigation">
            {navLinks.map(({ label, to, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => (isActive ? 'active' : '')}
              onClick={() => setMobileOpen(false)}
              tabIndex={mobileOpen ? 0 : -1}
            >
              <Icon size={19} strokeWidth={1.9} aria-hidden="true" />
              <span>{label}</span>
            </NavLink>
          ))}
          </nav>

          <div className="drawer-actions">
            <button type="button" onClick={() => { setMobileOpen(false); handleSearch(); }}>
              <Search size={19} strokeWidth={1.9} aria-hidden="true" />
              <span>Search</span>
            </button>
            <button type="button" onClick={() => { setMobileOpen(false); navigate(profileTo); }}>
              <UserRound size={19} strokeWidth={1.9} aria-hidden="true" />
              <span>My Profile</span>
            </button>
            {currentUser?.role === 'ADMIN' && (
              <Link to="/admin/dashboard" onClick={() => setMobileOpen(false)} tabIndex={mobileOpen ? 0 : -1}>
                <ShieldCheck size={19} strokeWidth={1.9} aria-hidden="true" />
                <span>Admin Panel</span>
              </Link>
            )}
            {currentUser && (
              <button type="button" onClick={handleLogout} tabIndex={mobileOpen ? 0 : -1}>
                <LogOut size={19} strokeWidth={1.9} aria-hidden="true" />
                <span>Logout</span>
              </button>
            )}
          </div>
        </div>

        {mobileOpen && <button type="button" className="drawer-overlay" aria-label="Close navigation menu" onClick={() => setMobileOpen(false)} />}

        <nav className="desktop-menu site-menu">
          {navLinks.map(({ label, to }) => (
            <NavLink key={to} to={to} className={({ isActive }) => (isActive ? 'active' : '')}>
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="navbar-actions">
          <button
            className="navbar-icon"
            type="button"
            aria-label="Search"
            onClick={handleSearch}
          >
            <span className="material-symbols-outlined">search</span>
          </button>
          <Link to={bookmarkTo} className="navbar-icon" aria-label="Saved Colleges">
            <span className="material-symbols-outlined">bookmark</span>
          </Link>
          <Link to="/contact" className="navbar-icon" aria-label="Contact us">
            <span className="material-symbols-outlined">mail</span>
          </Link>
          <button className="navbar-icon profile-btn" type="button" aria-label="Profile" onClick={() => navigate(profileTo)}>
            {profilePhoto ? <img src={profilePhoto} alt="" /> : <span className="material-symbols-outlined">account_circle</span>}
          </button>
          {currentUser && (
            <button
              className="navbar-icon"
              type="button"
              aria-label="Logout"
              title="Logout"
              onClick={handleLogout}
            >
              <span className="material-symbols-outlined">logout</span>
            </button>
          )}
          <button type="button" className="mobile-toggle" aria-label="Open navigation menu" aria-expanded={mobileOpen} onClick={() => setMobileOpen((prev) => !prev)}>
            {mobileOpen ? <X /> : <Menu />}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
