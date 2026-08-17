import { Link } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer-container">
      {/* Orange top accent */}
      <div className="footer-top-accent"></div>

      <div className="footer-content">
        {/* COLUMN 1: BRAND */}
        <div className="footer-column footer-brand">
          <h4 className="footer-brand-name">FOURISE</h4>
          <p className="footer-brand-tagline">Software Solutions Pvt. Ltd.</p>
          <p className="footer-brand-desc">
            Empowering excellence through AI-driven college admission insights.
          </p>
        </div>

        {/* COLUMN 2: CONTACT */}
        <div className="footer-column">
          <h5 className="footer-heading">Contact Information</h5>
          <div className="footer-contact-list">
            <div className="contact-row">
              <span className="contact-label">Website</span>
              <a href="https://www.fouriseindia.com" target="_blank" rel="noopener noreferrer" className="contact-value">
                www.fouriseindia.com
              </a>
            </div>
            <div className="contact-row">
              <span className="contact-label">Email</span>
              <a href="mailto:hr@fouriseindia.com" className="contact-value">
                hr@fouriseindia.com
              </a>
            </div>
            <div className="contact-row">
              <span className="contact-label">Phone</span>
              <a href="tel:9527605805" className="contact-value">
                9527605805 / 7020759254
              </a>
            </div>
            <div className="contact-row">
              <span className="contact-label">Office</span>
              <span className="contact-value">
                A-305, City Vista, Downtown Road, Ashoka Nagar, Kharadi, Pune 411014
              </span>
            </div>
          </div>
        </div>

        {/* COLUMN 3: CORPORATE */}
        <div className="footer-column">
          <h5 className="footer-heading">Corporate Information</h5>
          <div className="footer-corporate-list">
            <div className="corporate-row">
              <span className="corporate-label">GST</span>
              <span className="corporate-value">27AAFCF4062R1Z3</span>
            </div>
            <div className="corporate-row">
              <span className="corporate-label">CIN</span>
              <span className="corporate-value">U62099PN2023PTC218917</span>
            </div>
          </div>
        </div>

        {/* COLUMN 4: LINKS */}
        <div className="footer-column">
          <h5 className="footer-heading">Quick Links</h5>
          <div className="footer-links-list">
            <Link to="/about" className="footer-link">About Us</Link>
            <Link to="/contact" className="footer-link">Contact</Link>
            <Link to="/terms" className="footer-link">Terms &amp; Conditions</Link>
            <Link to="/privacy" className="footer-link">Privacy Policy</Link>
          </div>
        </div>
      </div>

      {/* Copyright section */}
      <div className="footer-divider"></div>
      <div className="footer-copyright">
        <p className="copyright-text">
          &copy; 2024 FOURISE Software Solutions Pvt. Ltd. All rights reserved.
        </p>
        <p className="copyright-disclaimer">
          Cutoff Guide AI is a product of FOURISE Software Solutions Pvt. Ltd.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
