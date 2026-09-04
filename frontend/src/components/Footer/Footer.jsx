import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer-container">
      {/* Orange top accent */}
      <div className="footer-top-accent"></div>

      <div className="footer-content">
        {/* BRAND & MISSION */}
        <div className="footer-brand">
          <div className="footer-brand-header">
            <h4 className="footer-brand-name">FOURISE</h4>
            <span className="footer-brand-tagline">Software Solutions Pvt. Ltd.</span>
          </div>
          <p className="footer-brand-desc">
            Empowering excellence through AI-driven college admission insights.
          </p>
        </div>

        {/* WEBSITE & EMAIL LINKS */}
        <div className="footer-brand-links">
          <a href="https://www.fouriseindia.com" target="_blank" rel="noopener noreferrer" className="brand-sublink">
            www.fouriseindia.com
          </a>
          <span className="link-separator">•</span>
          <a href="mailto:hr@fouriseindia.com" className="brand-sublink">
            hr@fouriseindia.com
          </a>
        </div>
      </div>

      {/* Copyright section */}
      <div className="footer-divider"></div>
      <div className="footer-copyright">
        <p className="copyright-text">
          &copy; {new Date().getFullYear()} FOURISE Software Solutions Pvt. Ltd. All rights reserved.
        </p>
        <p className="copyright-disclaimer">
          Cutoff Guide AI is a product of FOURISE Software Solutions Pvt. Ltd.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
