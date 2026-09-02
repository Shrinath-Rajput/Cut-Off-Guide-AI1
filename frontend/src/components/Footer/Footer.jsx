import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer-container">
      {/* Orange top accent */}
      <div className="footer-top-accent"></div>

      <div className="footer-content">
        {/* LEFT: BRAND & MISSION */}
        <div className="footer-brand">
          <div className="footer-brand-header">
            <h4 className="footer-brand-name">FOURISE</h4>
            <span className="footer-brand-tagline">Software Solutions Pvt. Ltd.</span>
          </div>
          <p className="footer-brand-desc">
            Empowering excellence through AI-driven college admission insights.
          </p>
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

        {/* RIGHT: PHONE & OFFICE */}
        <div className="footer-contact-right">
          <div className="contact-row">
            <span className="contact-label">Phone</span>
            <a href="tel:9527605805" className="contact-value">
              9527605805
            </a>
          </div>
          <div className="contact-row">
            <span className="contact-label">Office</span>
            <span className="contact-value">
              Office No: A-305, City Vista, Downtown Road, Ashoka Nagar, Kharadi, Pune
            </span>
          </div>
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
