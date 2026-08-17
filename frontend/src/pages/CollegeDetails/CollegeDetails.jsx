import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import MainLayout from '../../components/MainLayout/MainLayout';
import './CollegeDetails.css';
import heroImage from '../../assets/images/clg.jpg';

const collegeDetails = {
  mit: {
    name: 'Massachusetts Institute of Technology',
    location: 'Cambridge, MA, United States',
    rating: '4.9/5',
    reviews: '2,450 Reviews',
    ranking: '#1 QS World Ranking',
    badges: ['Top 10 Global', 'Accredited'],
    heroImage: heroImage,
  },
  stanford: {
    name: 'Stanford University',
    location: 'Stanford, CA, United States',
    rating: '4.8/5',
    reviews: '2,120 Reviews',
    ranking: '#2 QS World Ranking',
    badges: ['Top 10 Global', 'Accredited'],
    heroImage: heroImage,
  },
};

const stats = [
  {
    label: 'Average Package',
    value: '$142,000',
    detail: '+8.5% YoY',
    icon: 'payments',
  },
  {
    label: 'Highest Package',
    value: '$450,000',
    detail: 'International',
    icon: 'military_tech',
  },
  {
    label: 'Total Courses',
    value: '120+',
    detail: 'UG, PG & Ph.D',
    icon: 'auto_stories',
  },
  {
    label: 'Admission Rate',
    value: '4.8%',
    detail: 'Highly Competitive',
    icon: 'groups',
  },
];

const courseCards = [
  {
    title: 'B.Tech Computer Science and Engineering',
    duration: '4 Years',
    fee: '$55,000 / yr',
    eligibility: 'SAT/ACT',
    difficulty: '98th Percentile',
    progress: 98,
    accent: 'primary',
  },
  {
    title: 'M.Tech Artificial Intelligence',
    duration: '2 Years',
    fee: '$62,000 / yr',
    eligibility: 'GRE',
    difficulty: '95th Percentile',
    progress: 95,
    accent: 'secondary',
  },
  {
    title: 'B.Sc Data Science and Analytics',
    duration: '3 Years',
    fee: '$48,000 / yr',
    eligibility: 'High School Math',
    difficulty: '88th Percentile',
    progress: 88,
    accent: 'neutral',
  },
];

const chartYears = [
  { year: '2020', stanford: 85, mit: 65 },
  { year: '2021', stanford: 88, mit: 70 },
  { year: '2022', stanford: 92, mit: 75 },
  { year: '2023', stanford: 95, mit: 78 },
  { year: '2024 (Est)', stanford: 98, mit: 82, projected: true },
];

const CollegeDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('Overview');
  const college = collegeDetails[id] || collegeDetails.mit;

  return (
    <MainLayout>
      <main className="college-details-page">
        <section className="college-hero" style={{ backgroundImage: `url(${college.heroImage})` }}>
          <div className="hero-overlay" />
        </section>

        <section className="college-profile-shell">
          <div className="college-profile-card">
            <div>
              <div className="college-badges">
                {college.badges.map((badge) => (
                  <span key={badge} className="college-badge">{badge}</span>
                ))}
              </div>
              <h1>{college.name}</h1>
              <div className="college-meta-row">
                <div className="college-meta-item">
                  <span className="material-symbols-outlined">location_on</span>
                  <span>{college.location}</span>
                </div>
                <div className="college-meta-item">
                  <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>star</span>
                  <span>{college.rating} ({college.reviews})</span>
                </div>
                <div className="college-meta-item">
                  <span className="material-symbols-outlined">workspace_premium</span>
                  <span>{college.ranking}</span>
                </div>
              </div>
            </div>

            <div className="college-profile-actions">
              <button type="button" className="college-action-btn outline" onClick={() => navigate('/saved')}>
                <span className="material-symbols-outlined">bookmark_add</span>
                Save
              </button>
              <button type="button" className="college-action-btn outline" onClick={() => navigate('/compare')}>
                <span className="material-symbols-outlined">compare_arrows</span>
                Compare
              </button>
              <button type="button" className="college-action-btn primary" onClick={() => navigate('/contact')}>
                <span className="material-symbols-outlined">school</span>
                Apply Now
              </button>
            </div>
          </div>

          <div className="college-tabs-shell">
            <div className="college-tabs">
              {['Overview', 'Courses', 'Cutoffs', 'Fees', 'Placements', 'Facilities', 'Reviews'].map((tab) => (
                <button
                  key={tab}
                  type="button"
                  className={`college-tab ${activeTab === tab ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab)}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>
        </section>

        <section className="college-stats-grid">
          {stats.map((item) => (
            <article key={item.label} className="stat-card">
              <div className="stat-icon-background">
                <span className="material-symbols-outlined">{item.icon}</span>
              </div>
              <div className="stat-copy">
                <span className="stat-label">{item.label}</span>
                <span className="stat-value">{item.value}</span>
                <span className="stat-detail">{item.detail}</span>
              </div>
            </article>
          ))}
        </section>

        <div className="college-main-layout">
          <div className="college-main-column">
            <section className="cutoff-trends-card">
              <div className="section-heading-row">
                <div>
                  <h2>Previous Year Cutoff Trends</h2>
                  <p>AI-driven analysis of Computer Science engineering cutoffs.</p>
                </div>
                <button type="button" className="text-link" onClick={() => navigate('/assistant')}>
                  View Detailed Analytics
                </button>
              </div>
              <div className="cutoff-chart-card">
                <div className="chart-toolbar">
                  <div className="chart-toggle-group">
                    <button className="toggle-pill active" type="button">B.Tech CS</button>
                    <button className="toggle-pill" type="button">M.Tech AI</button>
                  </div>
                  <div className="chart-legend">
                    <span><span className="legend-dot general" /> General</span>
                    <span><span className="legend-dot reserved" /> Reserved</span>
                  </div>
                </div>
                <div className="cutoff-chart-visual">
                  {chartYears.map((item) => (
                    <div key={item.year} className="chart-column">
                      <div className={`chart-bars ${item.projected ? 'projected' : ''}`}>
                        <div className="chart-bar primary" style={{ height: `${item.stanford}%` }} />
                        <div className="chart-bar secondary" style={{ height: `${item.mit}%` }} />
                      </div>
                      <span className="chart-label">{item.year}</span>
                      {item.projected && <span className="projected-label">AI Prediction</span>}
                    </div>
                  ))}
                </div>
              </div>
            </section>

            <section className="courses-section">
              <div className="section-header-row">
                <h2>Top Courses Offered</h2>
              </div>
              <div className="courses-list">
                {courseCards.map((course) => (
                  <article key={course.title} className="course-card">
                    <div className={`course-accent course-accent--${course.accent}`} />
                    <div className="course-card-body">
                      <div>
                        <h3>{course.title}</h3>
                        <div className="course-tags">
                          <span>{course.duration}</span>
                          <span>{course.fee}</span>
                          <span>Eligibility: {course.eligibility}</span>
                        </div>
                        <div className="difficulty-row">
                          <div className="difficulty-label">Expected Admission Difficulty</div>
                          <div className="difficulty-value">{course.difficulty}</div>
                        </div>
                        <div className="difficulty-bar">
                          <div className="difficulty-fill" style={{ width: `${course.progress}%` }} />
                        </div>
                      </div>
                      <div className="course-actions">
                        <button type="button" className="course-action outline">Syllabus</button>
                        <button type="button" className="course-action primary">View Details</button>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
              <button type="button" className="view-all-courses" onClick={() => navigate('/courses')}>
                View All 120+ Courses
                <span className="material-symbols-outlined">arrow_forward</span>
              </button>
            </section>
          </div>

          <aside className="college-sidebar">
            <div className="sidebar-card ai-insight-card">
              <div className="sidebar-card-header">
                <span className="material-symbols-outlined">auto_awesome</span>
                <h3>AI Insight</h3>
              </div>
              <p>Based on current trajectory, cutoffs for CS programs are expected to rise by 1.2% this year due to increased international applications.</p>
              <button type="button" className="sidebar-button" onClick={() => navigate('/assistant')}>
                Run Custom Prediction
                <span className="material-symbols-outlined">trending_flat</span>
              </button>
            </div>

            <div className="sidebar-card dates-card">
              <h3>Important Dates</h3>
              <ul>
                <li>
                  <div>
                    <span>Fall Application Deadline</span>
                    <small>Regular Decision</small>
                  </div>
                  <strong>Jan 15</strong>
                </li>
                <li>
                  <div>
                    <span>Financial Aid Priority</span>
                    <small>FAFSA/CSS Profile</small>
                  </div>
                  <strong>Feb 15</strong>
                </li>
                <li>
                  <div>
                    <span>Decision Notification</span>
                    <small>Mid-March</small>
                  </div>
                </li>
              </ul>
            </div>

            <div className="sidebar-card tour-card">
              <div className="tour-icon-wrap">
                <span className="material-symbols-outlined">tour</span>
              </div>
              <h3>Campus Virtual Tour</h3>
              <p>Experience the campus from anywhere in the world.</p>
              <button type="button" className="sidebar-button outline" onClick={() => navigate('/colleges')}>
                Start Tour
              </button>
            </div>
          </aside>
        </div>
      </main>
    </MainLayout>
  );
};

export default CollegeDetails;
