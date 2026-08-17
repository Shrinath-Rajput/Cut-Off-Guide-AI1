import { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiMenu, FiX } from 'react-icons/fi';
import './Navbar.css';

const navLinks = [
  { label: 'Home', to: '/home' },
  { label: 'About', to: '/about' },
  { label: 'Colleges', to: '/colleges' },
  { label: 'Compare', to: '/compare' },
  { label: 'Cutoff / Result', to: '/cutoff' },
  { label: 'AI Assistant', to: '/assistant' },
  { label: 'Saved Colleges', to: '/saved' },
  { label: 'Contact', to: '/contact' },
  { label: 'Terms & Conditions', to: '/terms' },
];

const Navbar = ({ title, backTo = '/welcome', onSearch, bookmarkTo = '/saved', profileTo = '/profile' }) => {
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  if (title) {
    return (
      <nav className="topbar auth-nav">
        <button type="button" className="nav-back" onClick={() => navigate(backTo)}>
          <FiArrowLeft />
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

        <nav className={`site-menu ${mobileOpen ? 'open' : ''}`}>
          {navLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) => (isActive ? 'active' : '')}
              onClick={() => setMobileOpen(false)}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="navbar-actions">
          <button
            className="navbar-icon"
            type="button"
            aria-label="Search"
            onClick={onSearch}
          >
            <span className="material-symbols-outlined">search</span>
          </button>
          <Link to={bookmarkTo} className="navbar-icon" aria-label="Saved Colleges">
            <span className="material-symbols-outlined">bookmark</span>
          </Link>
          <button className="navbar-icon" type="button" aria-label="Profile" onClick={() => navigate(profileTo)}>
            <span className="material-symbols-outlined">account_circle</span>
          </button>
          <button type="button" className="mobile-toggle" onClick={() => setMobileOpen((prev) => !prev)}>
            {mobileOpen ? <FiX /> : <FiMenu />}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
