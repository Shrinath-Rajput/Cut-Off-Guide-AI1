import React from 'react';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import './About.css';

const About = () => {
  return (
    <div className="about-page-wrapper">
      <Navbar />

      <main className="about-main-content">
        {/* ============================================================
            HERO SECTION
            ============================================================ */}
        <section className="about-hero-section">
          <div className="about-hero-bg-img" />

          <div className="about-hero-glass-panel glass-panel">
            <h1 className="about-hero-title">
              Smarter College Decisions with AI
            </h1>
            <p className="about-hero-subtitle">
              We bridge the gap between complex admission data and student aspirations, providing crystal-clear insights to guide your academic journey.
            </p>
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
                Our proprietary neural networks continuously learn from admissions trends to provide unparalleled forecasting precision.
              </p>
            </div>

            {/* Card 2: Data Driven */}
            <div className="about-value-card glass-card">
              <div className="about-card-icon-box card-icon-data">
                <span className="material-symbols-outlined icon-3d">analytics</span>
              </div>
              <h3 className="about-card-title">Data Driven</h3>
              <p className="about-card-desc">
                Decisions backed by millions of historical data points, ensuring you never rely on guesswork for your future.
              </p>
            </div>

            {/* Card 3: Trusted & Secure */}
            <div className="about-value-card glass-card">
              <div className="about-card-icon-box card-icon-trust">
                <span className="material-symbols-outlined icon-3d">verified_user</span>
              </div>
              <h3 className="about-card-title">Trusted &amp; Secure</h3>
              <p className="about-card-desc">
                Enterprise-grade security protecting your academic profile, ensuring complete privacy throughout your journey.
              </p>
            </div>
          </div>
        </section>

        {/* ============================================================
            HOW IT WORKS SECTION
            ============================================================ */}
        <section className="about-hiw-section">
          <div className="about-hiw-bg-img" />

          <div className="about-hiw-container glass-panel">
            <div className="about-hiw-header">
              <h2 className="about-hiw-title">How It Works</h2>
              <p className="about-hiw-subtitle">
                Our streamlined process translates raw complexity into clear pathways.
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
                  <p className="about-step-desc">Aggregating historical cutoffs.</p>
                </div>

                {/* Step 2 */}
                <div className="about-step-card">
                  <div className="about-step-icon-wrap step-circle">
                    <span className="material-symbols-outlined icon-3d">troubleshoot</span>
                  </div>
                  <h4 className="about-step-title">2. Deep Analysis</h4>
                  <p className="about-step-desc">Processing trends via ML.</p>
                </div>

                {/* Step 3 (Active) */}
                <div className="about-step-card active-step">
                  <div className="about-step-icon-wrap step-circle active">
                    <span className="material-symbols-outlined icon-3d filled-icon">lightbulb</span>
                  </div>
                  <h4 className="about-step-title">3. Prediction</h4>
                  <p className="about-step-desc">Generating accurate forecasts.</p>
                </div>

                {/* Step 4 */}
                <div className="about-step-card">
                  <div className="about-step-icon-wrap step-circle">
                    <span className="material-symbols-outlined icon-3d">handshake</span>
                  </div>
                  <h4 className="about-step-title">4. Matching</h4>
                  <p className="about-step-desc">Finding your ideal fit.</p>
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
