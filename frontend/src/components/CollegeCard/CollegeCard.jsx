import Button from '../Button/Button';
import './CollegeCard.css';

const CollegeCard = ({ college, onView, onCompare, onSave }) => {
  return (
    <article className="college-card">
      <div className="college-banner" aria-hidden="true">
        <div className="college-hero-overlay" />
        <div className="college-badge">{college.category}</div>
      </div>
      <div className="college-card-body">
        <h3>{college.name}</h3>
        <p className="college-location">{college.location}</p>
        <div className="college-meta">
          <span>{college.courses.join(', ')}</span>
          <span>{college.fees}</span>
        </div>
        <div className="college-stats">
          <div>
            <strong>{college.cutoff}</strong>
            <span>Cutoff</span>
          </div>
          <div>
            <strong>{college.rating}</strong>
            <span>Rating</span>
          </div>
        </div>
      </div>
      <div className="college-card-actions">
        <Button variant="secondary" onClick={() => onView(college.id)}>
          View details
        </Button>
        <div className="college-card-tools">
          <button className="link-button" type="button" onClick={() => onCompare(college.id)}>
            Compare
          </button>
          <button className="link-button" type="button" onClick={() => onSave(college.id)}>
            Save
          </button>
        </div>
      </div>
    </article>
  );
};

export default CollegeCard;
