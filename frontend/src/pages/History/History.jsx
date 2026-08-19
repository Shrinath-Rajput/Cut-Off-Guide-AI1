import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../../components/MainLayout/MainLayout';
import Button from '../../components/Button/Button';
import './History.css';

const records = [
  {
    date: 'Oct 12, 2023',
    exam: 'JEE Advanced 2023',
    target: 'Target: IIT Bombay, IIT Delhi',
    percentile: '99.2',
    rank: '4,520',
    category: 'General',
    summary: 'High chance for top 5 NITs',
    status: 'green',
  },
  {
    date: 'Sep 28, 2023',
    exam: 'BITSAT 2023',
    target: 'Target: BITS Pilani (CS)',
    percentile: '-',
    rank: '-',
    category: 'General',
    summary: 'Borderline for CS, safe for ECE',
    status: 'amber',
  },
  {
    date: 'Aug 15, 2023',
    exam: 'JEE Main 2023 (Session 2)',
    target: 'Target: NIT Trichy, NIT Surathkal',
    percentile: '98.5',
    rank: '15,300',
    category: 'OBC-NCL',
    summary: 'Confirmed seat in Top 3 NITs',
    status: 'green',
  },
];

const chartBars = [
  { label: 'Jan', value: 18 },
  { label: 'Feb', value: 42 },
  { label: 'Mar', value: 78, highlight: true },
  { label: 'Apr', value: 30 },
  { label: 'May', value: 60 },
  { label: 'Jun', value: 26 },
];

const History = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [range, setRange] = useState('Last 6 Months');

  const filteredRecords = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) return records;

    return records.filter((record) => {
      return [record.date, record.exam, record.target, record.category, record.summary]
        .some((field) => field.toLowerCase().includes(query));
    });
  }, [searchQuery]);

  return (
    <MainLayout>
      <div className="history-page">
        <div className="history-hero">
          <div className="history-hero-copy">
            <h1>Prediction History</h1>
            <p>Review your previous college admission predictions and AI assessments.</p>
          </div>

          <div className="history-hero-actions">
            <button type="button" className="history-filter-button">
              <span className="material-symbols-outlined">filter_list</span>
              Filter
            </button>
            <Button type="button" variant="primary" onClick={() => navigate('/cutoff')}>
              <span className="material-symbols-outlined">add</span>
              New Prediction
            </Button>
          </div>
        </div>

        <div className="history-summary-grid">
          <section className="history-card activity-card">
            <div className="section-header">
              <div>
                <p className="section-label">Prediction Activity</p>
              </div>
              <select className="history-range-select" value={range} onChange={(event) => setRange(event.target.value)}>
                <option>Last 6 Months</option>
                <option>This Year</option>
                <option>All Time</option>
              </select>
            </div>

            <div className="activity-chart">
              {chartBars.map((bar) => (
                <div key={bar.label} className="activity-bar-item">
                  <div className={`activity-bar${bar.highlight ? ' highlight' : ''}`} style={{ height: `${bar.value}%` }} />
                  <span>{bar.label}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="history-card stats-card">
            <div className="section-header">
              <div>
                <p className="section-label">Summary Stats</p>
              </div>
            </div>

            <div className="stats-list">
              <div className="stat-row">
                <div>
                  <span className="stat-title">Total Predictions</span>
                  <p className="stat-value">24</p>
                </div>
              </div>
              <div className="stat-row">
                <div>
                  <span className="stat-title">Saved Colleges</span>
                  <p className="stat-value">12</p>
                </div>
              </div>
              <div className="stat-row">
                <div>
                  <span className="stat-title">Avg. Probability</span>
                  <p className="stat-value">68%</p>
                </div>
              </div>
            </div>
          </section>
        </div>

        <section className="history-card records-card">
          <div className="records-header">
            <div>
              <p className="section-label">Recent Records</p>
            </div>
            <div className="records-search">
              <span className="material-symbols-outlined">search</span>
              <input
                type="search"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="Search exams or colleges..."
                aria-label="Search exams or colleges"
              />
            </div>
          </div>

          <div className="records-table-wrapper">
            <table className="records-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Exam / Target</th>
                  <th>Percentile</th>
                  <th>Rank</th>
                  <th>Category</th>
                  <th>Result Summary</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecords.map((record) => (
                  <tr key={record.date + record.exam} className="records-row">
                    <td>{record.date}</td>
                    <td>
                      <div className="record-exam-name">{record.exam}</div>
                      <div className="record-exam-target">{record.target}</div>
                    </td>
                    <td>{record.percentile}</td>
                    <td>{record.rank}</td>
                    <td>
                      <span className={`record-category ${record.status}`}>{record.category}</span>
                    </td>
                    <td>
                      <div className="record-summary">
                        <span className={`record-status-dot ${record.status}`} />
                        {record.summary}
                      </div>
                    </td>
                    <td className="record-actions">
                      <button type="button" className="record-action-button" aria-label="View Result">
                        <span className="material-symbols-outlined">visibility</span>
                      </button>
                      <button type="button" className="record-action-button" aria-label="Compare Again">
                        <span className="material-symbols-outlined">compare_arrows</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="records-footer">
            <span>Showing 1 to {filteredRecords.length} of 24 entries</span>
            <div className="pagination-controls">
              <button type="button" className="pagination-button" disabled>
                Prev
              </button>
              <button type="button" className="pagination-button">Next</button>
            </div>
          </div>
        </section>
      </div>
    </MainLayout>
  );
};

export default History;
