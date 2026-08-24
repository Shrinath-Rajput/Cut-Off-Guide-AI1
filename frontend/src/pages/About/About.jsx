import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import counsellingImg from '../../assets/images/about-counselling.jpg';
import premierInstitutesImg from '../../assets/images/about-premier-institutes.jpg';
import './About.css';

const About = () => {
  return (
    <div className="about-page-wrapper">
      <Navbar />

      <main className="about-main-content">
        {/* ============================================================
            HERO SECTION (FIRST IMAGE: STUDENT COUNSELLING)
            ============================================================ */}
        <section className="about-hero-section">
          {/* First Image as Background / Showcase */}
          <div className="about-hero-media-wrap">
            <img
              src={counsellingImg}
              alt="Student Counselling - Guiding Your Future"
              className="about-hero-img"
            />
            <div className="about-hero-overlay" />
          </div>

          <div className="about-hero-glass-panel glass-panel">
            <div className="about-badge">
              <span className="material-symbols-outlined text-sm">psychology</span>
              <span>AI-Driven Admissions &amp; Counseling</span>
            </div>
            <h1 className="about-hero-title">
              Smarter College Decisions with AI
            </h1>
            <p className="about-hero-subtitle">
              We bridge the gap between complex admission cutoffs and student aspirations, providing crystal-clear insights, verified cutoff predictions, and personalized counseling to guide your academic future.
            </p>

            <div className="about-hero-actions">
              <Link to="/cutoff" className="about-btn-primary">
                Predict My Cutoff
                <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </Link>
              <Link to="/colleges" className="about-btn-secondary">
                Explore Colleges
              </Link>
            </div>
          </div>
        </section>

        {/* ============================================================
            CORE VALUES SECTION
            ============================================================ */}
        <section className="about-values-section">
          <div className="about-values-grid">
            {/* Card 1: AI Powered */}
            <div className="about-value-card glass-card">
              <div className="about-card-icon-box card-icon-ai">
                <span className="material-symbols-outlined icon-3d">memory</span>
              </div>
              <h3 className="about-card-title">AI Powered</h3>
              <p className="about-card-desc">
                Our proprietary neural models analyze historical admission trends and normalized percentiles to provide unparalleled forecasting precision.
              </p>
            </div>

            {/* Card 2: Data Driven */}
            <div className="about-value-card glass-card">
              <div className="about-card-icon-box card-icon-data">
                <span className="material-symbols-outlined icon-3d">analytics</span>
              </div>
              <h3 className="about-card-title">Data Driven</h3>
              <p className="about-card-desc">
                Decisions backed by verified historical cutoff records, seat matrix trends, and official counseling datasets across all categories.
              </p>
            </div>

            {/* Card 3: Trusted & Secure */}
            <div className="about-value-card glass-card">
              <div className="about-card-icon-box card-icon-trust">
                <span className="material-symbols-outlined icon-3d">verified_user</span>
              </div>
              <h3 className="about-card-title">Trusted &amp; Secure</h3>
              <p className="about-card-desc">
                Accurate institutional profiles, fee structures, and placement metrics protecting your academic journey from misinformation.
              </p>
            </div>
          </div>
        </section>

        {/* ============================================================
            PREMIER INSTITUTES SECTION (SECOND IMAGE: PREMIER INSTITUTIONS)
            ============================================================ */}
        <section className="about-institutes-section">
          <div className="about-section-header">
            <div className="about-badge">
              <span className="material-symbols-outlined text-sm">account_balance</span>
              <span>All-India Institution Coverage</span>
            </div>
            <h2 className="about-section-title">
              Covering Premier Universities &amp; Colleges Across India
            </h2>
            <p className="about-section-subtitle">
              Comprehensive cutoff analytics and placement intelligence for IITs, NITs, IIITs, BITS, AIIMS, and top state autonomous universities.
            </p>
          </div>

          <div className="about-institutes-card glass-card">
            <img
              src={premierInstitutesImg}
              alt="Premier Institutions of India - IITs, IISc, AIIMS, IIM, BITS"
              className="about-institutes-img"
            />
          </div>
        </section>

        {/* ============================================================
            HOW IT WORKS SECTION
            ============================================================ */}
        <section className="about-hiw-section">
          <div className="about-hiw-container glass-panel">
            <div className="about-hiw-header">
              <h2 className="about-hiw-title">How It Works</h2>
              <p className="about-hiw-subtitle">
                Our streamlined process translates raw cutoff complexity into clear pathways.
              </p>
            </div>

            <div className="about-hiw-timeline-box">
              {/* Connecting Line */}
              <div className="about-timeline-line" />

              <div className="about-timeline-grid">
                {/* Step 1 */}
                <div className="about-step-card">
                  <div className="about-step-icon-wrap step-circle">
                    <span className="material-symbols-outlined icon-3d">database</span>
                  </div>
                  <h4 className="about-step-title">1. Data Ingestion</h4>
                  <p className="about-step-desc">Aggregating historical round cutoffs.</p>
                </div>

                {/* Step 2 */}
                <div className="about-step-card">
                  <div className="about-step-icon-wrap step-circle">
                    <span className="material-symbols-outlined icon-3d">troubleshoot</span>
                  </div>
                  <h4 className="about-step-title">2. Deep Analysis</h4>
                  <p className="about-step-desc">Processing trends via ML models.</p>
                </div>

                {/* Step 3 (Active) */}
                <div className="about-step-card active-step">
                  <div className="about-step-icon-wrap step-circle active">
                    <span className="material-symbols-outlined icon-3d filled-icon">lightbulb</span>
                  </div>
                  <h4 className="about-step-title">3. Prediction</h4>
                  <p className="about-step-desc">Generating accurate probabilities.</p>
                </div>

                {/* Step 4 */}
                <div className="about-step-card">
                  <div className="about-step-icon-wrap step-circle">
                    <span className="material-symbols-outlined icon-3d">handshake</span>
                  </div>
                  <h4 className="about-step-title">4. Matching</h4>
                  <p className="about-step-desc">Finding your dream college fit.</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default About;
