import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import MainLayout from '../../components/MainLayout/MainLayout';
import './Home.css';

const heroImage =
  'https://lh3.googleusercontent.com/aida-public/AB6AXuBQPJpMbLY2KKYymwKyfKT82PmRmV5_H9Sc0e9sSDIAsrvgR55keQtfd8PorDhJX-nJ5faZhm_LW0qTuATNB0RwvXT_joyPvJj8jj1AxVDgSJ-NyzujXJiq4vY1Hx-fsVLqb6TqhmL0SFxA37CpBK5tLIrPFWuM0g62u4nG_hdRtYlJhmknKEl2K53jev_pDVA9_gE9HwZ45BlBGgMd--mzB1gwbiuCuL4vxFhl4LclXKp8gf94_QFd';

const featureCards = [
  {
    title: 'AI Cutoff Predictor',
    text: 'Input your scores and let our machine learning models analyze historical data to provide real-time admission probabilities across top institutions.',
    icon: 'model_training',
    large: true,
  },
  {
    title: 'College Discovery',
    text: 'Explore hidden gems and premier universities tailored precisely to your academic profile and career aspirations.',
    icon: 'travel_explore',
  },
  {
    title: 'Smart Comparison',
    text: 'Evaluate institutions side-by-side on metrics that matter: placements, faculty, infrastructure, and fee structures.',
    icon: 'compare_arrows',
  },
  {
    title: 'Career Assistant',
    text: 'Consult with our generative AI for personalized advice on course selection and long-term career trajectories.',
    icon: 'support_agent',
  },
  {
    title: 'Saved Colleges',
    text: 'Organize your shortlists.',
    icon: 'bookmarks',
  },
  {
    title: 'Prediction History',
    text: 'Review past analyses.',
    icon: 'history',
  },
];

const navLinks = [
  { label: 'Home', to: '/home' },
  { label: 'Colleges', to: '/colleges' },
  { label: 'Predictor', to: '/cutoff' },
  { label: 'Compare', to: '/compare' },
  { label: 'AI Assistant', to: '/assistant' },
  { label: 'About', to: '/about' },
];

export default function Home() {
  useEffect(() => {
    document.body.classList.add('home-page');
    return () => {
      document.body.classList.remove('home-page');
    };
  }, []);

  return (
    <MainLayout>
      <div className="home-page-shell">
        <main className="home-main">
          <section className="home-hero">
            <div className="hero-copy">
              <span className="hero-pill">
                <span className="material-symbols-outlined">psychology</span>
                AI Powered Admission Prediction
              </span>
              <h1 className="hero-title">
                Your Future.
                <br />
                Your College.
                <br />
                <span>Your Choice.</span>
              </h1>
              <p className="hero-description">
                Leverage advanced artificial intelligence to accurately predict college cutoffs, compare premier institutions,
                and architect your academic destiny with precision.
              </p>
              <div className="hero-buttons">
                <Link to="/cutoff" className="button-primary">
                  Start Your Journey
                  <span className="material-symbols-outlined">arrow_forward</span>
                </Link>
                <Link to="/colleges" className="button-secondary">
                  Explore Colleges
                </Link>
              </div>
            </div>
            <div className="hero-image-panel">
              <div className="hero-image-bg" />
              <img className="hero-image" src={heroImage} alt="College Campus" />
              <div className="floating-card">
                <div className="floating-icon">
                  <span className="material-symbols-outlined">query_stats</span>
                </div>
                <div>
                  <p className="floating-title">Admission 2026</p>
                  <p className="floating-text">Predict your chances instantly with 95% accuracy.</p>
                </div>
              </div>
            </div>
          </section>

          <section className="home-stats">
            <div className="stat-item">
              <p className="stat-value">500+</p>
              <p className="stat-label">Colleges Tracked</p>
            </div>
            <div className="stat-item">
              <p className="stat-value">50K+</p>
              <p className="stat-label">Students Guided</p>
            </div>
            <div className="stat-item">
              <p className="stat-value">95%+</p>
              <p className="stat-label">Prediction Accuracy</p>
            </div>
            <div className="stat-item">
              <p className="stat-value">1000+</p>
              <p className="stat-label">Courses Analyzed</p>
            </div>
          </section>

          <section className="home-features">
            <div className="features-intro">
              <h2>Everything You Need for Your College Journey</h2>
              <p>A comprehensive suite of intelligent tools designed to transform uncertainty into strategic academic decisions.</p>
            </div>
            <div className="features-grid">
              {featureCards.map((card) => (
                <article key={card.title} className={`feature-card ${card.large ? 'feature-card-large' : ''}`}>
                  <span className="material-symbols-outlined feature-icon">{card.icon}</span>
                  <h3>{card.title}</h3>
                  <p>{card.text}</p>
                </article>
              ))}
            </div>
          </section>

          <section className="home-cta-section">
            <div className="cta-panel">
              <h2>Ready to find your perfect college?</h2>
              <p>Join thousands of students who have successfully navigated their admissions using our predictive intelligence.</p>
              <Link to="/cutoff" className="button-primary cta-button">
                Start Prediction
                <span className="material-symbols-outlined">magic_button</span>
              </Link>
            </div>
          </section>

          <footer className="home-footer">
            <div className="footer-top">
              <div className="footer-brand">Cutoff Guide AI</div>
              <div className="footer-columns">
                <div>
                  <p className="footer-section-title">Product</p>
                  <Link to="/colleges">Colleges</Link>
                  <Link to="/cutoff">Predictor</Link>
                  <Link to="/assistant">AI Assistant</Link>
                </div>
                <div>
                  <p className="footer-section-title">Company</p>
                  <Link to="/about">About Us</Link>
                  <a href="#">Careers</a>
                </div>
                <div>
                  <p className="footer-section-title">Support</p>
                  <a href="#">Help Center</a>
                  <Link to="/contact">Contact</Link>
                </div>
              </div>
            </div>
            <p className="footer-copy">© 2024 Cutoff Guide AI. Empowering academic excellence.</p>
          </footer>
        </main>
      </div>
    </MainLayout>
  );
}
