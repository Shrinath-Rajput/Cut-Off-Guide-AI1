import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import './About.css';

const About = () => {
  const navigate = useNavigate();

  return (
    <div className="about-page">
      <Navbar />

      <main className="about-main">
        {/* ===== HERO SECTION ===== */}
        <section className="about-hero">
          <div className="about-hero-inner">
            <div className="about-hero-badge">
              <span className="material-symbols-outlined about-hero-badge-icon">auto_awesome</span>
              <span>Powered by Advanced AI</span>
            </div>

            <h1 className="about-hero-heading">Smarter College Decisions with AI</h1>

            <p className="about-hero-desc">
              We bridge the gap between complex admission data and student aspirations, providing crystal-clear insights to guide your academic journey.
            </p>

            <div className="about-hero-image-wrap">
              <img
                src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1600&q=80"
                alt="Students collaborating in a modern university setting"
                className="about-hero-image"
                onError={(e) => {
                  e.currentTarget.src =
                    'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=1600&q=80';
                }}
              />
            </div>
          </div>
        </section>

        {/* ===== MISSION + WHY CHOOSE US ===== */}
        <section className="about-mission">
          <div className="about-mission-inner">
            <div className="about-mission-left">
              <h2 className="about-section-heading">Our Mission</h2>
              <p className="about-mission-text">
                To democratize access to elite higher education insights. We believe every student deserves data-backed clarity when making the most critical decision of their academic career. By leveraging cutting-edge machine learning, we transform overwhelming historical cutoff data into actionable, personalized predictions.
              </p>
            </div>

            <div className="about-mission-right">
              <div className="about-why-card">
                <span className="about-why-label">WHY CHOOSE US</span>
                <ul className="about-why-list">
                  <li>
                    <span className="material-symbols-outlined about-why-check">check_circle</span>
                    <span>Industry-leading predictive accuracy models.</span>
                  </li>
                  <li>
                    <span className="material-symbols-outlined about-why-check">check_circle</span>
                    <span>Real-time data aggregation from top universities.</span>
                  </li>
                  <li>
                    <span className="material-symbols-outlined about-why-check">check_circle</span>
                    <span>Unbiased, data-driven matching algorithms.</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* ===== 3 FEATURE CARDS ===== */}
        <section className="about-features">
          <div className="about-features-inner">
            <div className="about-feature-card glass-card">
              <div className="about-feature-icon-wrap about-feature-icon-1">
                <span className="material-symbols-outlined about-feature-icon">memory</span>
              </div>
              <h3 className="about-feature-title">AI Powered</h3>
              <p className="about-feature-desc">
                Our proprietary neural networks continuously learn from admissions trends to provide unparalleled forecasting precision.
              </p>
            </div>

            <div className="about-feature-card glass-card">
              <div className="about-feature-icon-wrap about-feature-icon-2">
                <span className="material-symbols-outlined about-feature-icon">analytics</span>
              </div>
              <h3 className="about-feature-title">Data Driven</h3>
              <p className="about-feature-desc">
                Decisions backed by millions of historical data points, ensuring you never rely on guesswork for your future.
              </p>
            </div>

            <div className="about-feature-card glass-card">
              <div className="about-feature-icon-wrap about-feature-icon-3">
                <span className="material-symbols-outlined about-feature-icon">verified_user</span>
              </div>
              <h3 className="about-feature-title">Trusted &amp; Secure</h3>
              <p className="about-feature-desc">
                Enterprise-grade security protecting your academic profile, ensuring complete privacy throughout your journey.
              </p>
            </div>
          </div>
        </section>

        {/* ===== HOW IT WORKS TIMELINE ===== */}
        <section className="about-hiw">
          <div className="about-hiw-inner">
            <h2 className="about-section-heading about-hiw-heading">How It Works</h2>
            <p className="about-hiw-subtitle">
              Our streamlined process translates raw complexity into clear pathways.
            </p>

            <div className="about-hiw-timeline">
              {/* STEP 1 */}
              <div className="about-hiw-step">
                <div className="about-hiw-step-icon about-hiw-step-icon-normal">
                  <span className="material-symbols-outlined">database</span>
                </div>
                <h4 className="about-hiw-step-title">1. Data Ingestion</h4>
                <p className="about-hiw-step-desc">Aggregating historical cutoffs.</p>
                <div className="about-hiw-connector about-hiw-connector-h" />
              </div>

              {/* STEP 2 */}
              <div className="about-hiw-step">
                <div className="about-hiw-step-icon about-hiw-step-icon-normal">
                  <span className="material-symbols-outlined">query_stats</span>
                </div>
                <h4 className="about-hiw-step-title">2. Deep Analysis</h4>
                <p className="about-hiw-step-desc">Processing trends via ML.</p>
                <div className="about-hiw-connector about-hiw-connector-h" />
              </div>

              {/* STEP 3 - HIGHLIGHTED */}
              <div className="about-hiw-step">
                <div className="about-hiw-step-icon about-hiw-step-icon-primary">
                  <span className="material-symbols-outlined">lightbulb</span>
                </div>
                <h4 className="about-hiw-step-title">3. Prediction</h4>
                <p className="about-hiw-step-desc">Generating accurate forecasts.</p>
                <div className="about-hiw-connector about-hiw-connector-h" />
              </div>

              {/* STEP 4 */}
              <div className="about-hiw-step">
                <div className="about-hiw-step-icon about-hiw-step-icon-normal">
                  <span className="material-symbols-outlined">handshake</span>
                </div>
                <h4 className="about-hiw-step-title">4. Matching</h4>
                <p className="about-hiw-step-desc">Finding your ideal fit.</p>
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
