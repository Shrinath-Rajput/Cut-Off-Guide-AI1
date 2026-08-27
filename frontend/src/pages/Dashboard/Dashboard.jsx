import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import { useAuth } from '../../context/AuthContext';
import { getColleges } from '../../services/api';
import { collegeImage, handleCollegeImageError } from '../../utils/collegeImage';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const userName = currentUser?.name || 'Alex';
  const [recommendedColleges, setRecommendedColleges] = useState([]);

  useEffect(() => {
    getColleges({ page: 1, limit: 4 })
      .then((response) => setRecommendedColleges(response.data || []))
      .catch(() => setRecommendedColleges([]));
  }, []);

  return (
    <div className="dashboard-page">
      <Navbar />
      <main className="dashboard-main">
        <section className="dashboard-welcome">
          <h1>
            Welcome back, {userName} <span className="wave-emoji">👋</span>
          </h1>
          <p>
            Your AI-powered admission journey is looking promising. Based on recent mock tests,
            your predicted standings have updated.
          </p>
        </section>

        <section className="summary-grid">
          <article className="summary-card summary-card-rank">
            <div className="summary-card-top">
              <div className="summary-card-label">
                <span className="material-symbols-outlined">emoji_events</span>
                <span>Predicted Rank</span>
              </div>
              <span className="summary-pill">+120 improvement</span>
            </div>
            <div className="summary-card-value">4,250</div>
            <p className="summary-card-meta">Based on JEE Main Mock 4</p>
          </article>

          <article className="summary-card summary-card-percentile">
            <div className="summary-card-top">
              <div className="summary-card-label">
                <span className="material-symbols-outlined">analytics</span>
                <span>Target Percentile</span>
              </div>
            </div>
            <div className="summary-card-value">98.5%</div>
            <div className="progress-container">
              <div className="progress-track">
                <div className="progress-fill" style={{ width: '98.5%' }} />
              </div>
            </div>
            <p className="summary-card-meta">Top 1.5% of applicants</p>
          </article>

          <article className="summary-card summary-card-probability">
            <div className="summary-card-top">
              <div className="summary-card-label summary-card-label-light">
                <span className="material-symbols-outlined">trending_up</span>
                <span>Top Choice Probability</span>
              </div>
            </div>
            <p className="probability-description">IIT Bombay - Computer Science</p>
            <div className="probability-score-row">
              <span className="probability-score">72%</span>
              <span className="probability-tag">High Chance</span>
            </div>
            <div className="percentile-track">
              <div className="percentile-fill" style={{ width: '72%' }} />
            </div>
          </article>
        </section>

        <div className="dashboard-grid">
          <section className="quick-actions-panel">
            <div className="panel-title">
              <h2>Quick Actions</h2>
            </div>
            <div className="quick-actions-grid">
              <button className="action-card" type="button" onClick={() => navigate('/cutoff')}>
                <span className="action-icon action-icon-primary material-symbols-outlined">troubleshoot</span>
                <span>Predict Cutoff</span>
              </button>
              <button className="action-card" type="button" onClick={() => navigate('/colleges')}>
                <span className="action-icon action-icon-secondary material-symbols-outlined">account_balance</span>
                <span>Explore Colleges</span>
              </button>
              <button className="action-card" type="button" onClick={() => navigate('/compare')}>
                <span className="action-icon action-icon-tertiary material-symbols-outlined">compare_arrows</span>
                <span>Compare Colleges</span>
              </button>
              <button className="action-card" type="button" onClick={() => navigate('/assistant')}>
                <span className="action-icon action-icon-accent material-symbols-outlined">smart_toy</span>
                <span>Ask AI Guide</span>
              </button>
            </div>
          </section>

          <section className="trend-panel">
            <div className="trend-header">
              <h2>Your Admission Chances Trend</h2>
              <select className="trend-select" aria-label="Time range">
                <option>Last 6 Mock Tests</option>
                <option>Last 3 Months</option>
              </select>
            </div>
            <div className="chart-card">
              <div className="chart-bars">
                <div className="chart-bar-group" tabIndex="0">
                  <span className="chart-tooltip">Test 1: 45%</span>
                  <div className="chart-bar" style={{ height: '45%' }} />
                </div>
                <div className="chart-bar-group" tabIndex="0">
                  <span className="chart-tooltip">Test 2: 52%</span>
                  <div className="chart-bar" style={{ height: '52%' }} />
                </div>
                <div className="chart-bar-group" tabIndex="0">
                  <span className="chart-tooltip">Test 3: 58%</span>
                  <div className="chart-bar" style={{ height: '58%' }} />
                </div>
                <div className="chart-bar-group" tabIndex="0">
                  <span className="chart-tooltip">Test 4: 55%</span>
                  <div className="chart-bar" style={{ height: '55%' }} />
                </div>
                <div className="chart-bar-group" tabIndex="0">
                  <span className="chart-tooltip">Test 5: 68%</span>
                  <div className="chart-bar" style={{ height: '68%' }} />
                </div>
                <div className="chart-bar-group chart-bar-current" tabIndex="0">
                  <span className="chart-tooltip">Test 6: 72%</span>
                  <div className="chart-bar current" style={{ height: '72%' }} />
                </div>
              </div>
              <div className="chart-labels">
                <span>Mock 1</span>
                <span>Mock 2</span>
                <span>Mock 3</span>
                <span>Mock 4</span>
                <span>Mock 5</span>
                <span className="current-label">Current</span>
              </div>
            </div>
          </section>
        </div>

        <section className="recommendations-section">
          <div className="recommendations-header">
            <h2>Recommended Based on Your Profile</h2>
            <button className="view-all-button" type="button">
              View All <span className="material-symbols-outlined">arrow_forward</span>
            </button>
          </div>
          <div className="recommendations-scroll">
            {recommendedColleges.map((college, index) => (
              <article className="college-card" key={college.id}>
                <div className="college-image">
                  <img src={collegeImage(college.image)} alt={college.name} onError={handleCollegeImageError} />
                  <div className="college-badge"><span className="material-symbols-outlined">star</span> {index + 1}</div>
                </div>
                <div className="college-card-body">
                  <h3>{college.name}</h3>
                  <p>{college.courses?.[0] || 'Courses available'}</p>
                  <div className="college-card-footer">
                    <div><span className="college-label">Rating</span><span className="college-value">{college.rating || 'N/A'}</span></div>
                    <button type="button" className="details-button" onClick={() => navigate(`/college/${college.id}`)}>View Details</button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default Dashboard;
