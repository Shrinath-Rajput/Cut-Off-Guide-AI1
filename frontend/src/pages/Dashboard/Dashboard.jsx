import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import { useAuth } from '../../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const userName = currentUser?.name || 'Alex';

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
                <span className="material-symbols-outlined">auto_awesome</span>
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
            <article className="college-card">
              <div className="college-image">
                <img
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuCkEzPPEZKRYIlsvVjGHhqlBl-OvGS3qqCk_0LMpL20owyC8ATvRS0NYcYAp3O7rnVBIArdE7v4hE9IZuWVOt21_PAVeHNlEDB6MctmNS9u3uPy7s1fZer8NN7v_E0bgkM5Tl0e5MEKIj72H1MEv03tLsIygnjC5Dm8QPvIe3jmLluxpAQP4lckonowpqxrmh3ntLwATCi27dJof3K4OE6HoeS9q4uMBmY97hJPprYGMExMI77xhUp6"
                  alt="Indian Institute of Technology Madras"
                />
                <div className="college-badge">
                  <span className="material-symbols-outlined">star</span> 1
                </div>
              </div>
              <div className="college-card-body">
                <h3>Indian Institute of Technology Madras</h3>
                <p>Computer Science and Engineering</p>
                <div className="college-card-footer">
                  <div>
                    <span className="college-label">Probability</span>
                    <span className="college-value">85% - Safe</span>
                  </div>
                  <button type="button" className="details-button">
                    View Details
                  </button>
                </div>
              </div>
            </article>

            <article className="college-card">
              <div className="college-image">
                <img
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuBHhaX6UhYgf3JIoU6xSXt8tz4eiGAMbXM_cinWH3SWQnA-FUaSruU8AGobPfDMP0PAKsjlJJF93SpEExxVgsWn2hvcikGeyPYx227zL7vov_dFi0U8BYTNe8RPkh-BhUNJ2QI0U6RDo0BajqBjanLKr4HAWexE-n4-KKxO3NKF1ovHHW39plmrkPZoY172QxksacorkK1a0LaRJ0pMitCcZDrT-UlueW-vfQe8VmjdqzoS6BvAnA5t"
                  alt="Indian Institute of Technology Delhi"
                />
                <div className="college-badge">
                  <span className="material-symbols-outlined">star</span> 2
                </div>
              </div>
              <div className="college-card-body">
                <h3>Indian Institute of Technology Delhi</h3>
                <p>Electrical Engineering</p>
                <div className="college-card-footer">
                  <div>
                    <span className="college-label">Probability</span>
                    <span className="college-value college-value-warning">78% - Likely</span>
                  </div>
                  <button type="button" className="details-button details-button-outline">
                    View Details
                  </button>
                </div>
              </div>
            </article>

            <article className="college-card">
              <div className="college-image">
                <img
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuAnS83fWeqohG7gEM0XYmWqG7P4PiSNO2ICXVwR207ewtgKhekr26A0oGB4MGbRp4u6UwGipIgRMR6ediM6CEmGwhydRc_YhBneFiGaw7sq_lG2xoNL7HunMxlLISLZzBP3qncOXTNK4DtnVY0Jp-Rs8KoJ853QutYZ8v37zknQf3TQLf1nzDrcn6QXZG-LQ4HNzVtiIrKkGSesG8H2LzCZeoqgIF1nC134xf9LnJRkjfhQ1R5RKmU6"
                  alt="Indian Institute of Technology Bombay"
                />
                <div className="college-badge">
                  <span className="material-symbols-outlined">star</span> 3
                </div>
              </div>
              <div className="college-card-body">
                <h3>Indian Institute of Technology Bombay</h3>
                <p>Mechanical Engineering</p>
                <div className="college-card-footer">
                  <div>
                    <span className="college-label">Probability</span>
                    <span className="college-value">65% - Moderate</span>
                  </div>
                  <button type="button" className="details-button details-button-outline">
                    View Details
                  </button>
                </div>
              </div>
            </article>

            <article className="college-card college-card-blank">
              <div className="college-image college-image-blank">
                <span className="material-symbols-outlined">account_balance</span>
              </div>
              <div className="college-card-body">
                <h3>National Institute of Technology Trichy</h3>
                <p>Computer Science</p>
                <div className="college-card-footer">
                  <div>
                    <span className="college-label">Probability</span>
                    <span className="college-value">92% - Safe</span>
                  </div>
                  <button type="button" className="details-button details-button-outline">
                    View Details
                  </button>
                </div>
              </div>
            </article>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default Dashboard;
