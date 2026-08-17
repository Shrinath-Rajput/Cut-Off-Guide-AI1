import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../../components/MainLayout/MainLayout';
import './Saved.css';
import stanfordImage from '../../assets/images/clg.jpg';
import mitImage from '../../assets/images/clg1.jpg';
import cornellImage from '../../assets/images/clg2.jpg';

const initialSavedColleges = [
  {
    id: 'stanford',
    name: 'Stanford University',
    location: 'Stanford, CA',
    course: 'Computer Science (B.S.)',
    cutoff: '98.5%ile',
    savedOn: 'Oct 24, 2023',
    rank: '#12',
    rating: '4.8',
    image: stanfordImage,
  },
  {
    id: 'mit',
    name: 'MIT',
    location: 'Cambridge, MA',
    course: 'Mechanical Eng.',
    cutoff: '99.1%ile',
    savedOn: 'Nov 02, 2023',
    rank: '#3',
    rating: '4.9',
    image: mitImage,
  },
  {
    id: 'cornell',
    name: 'Cornell University',
    location: 'Ithaca, NY',
    course: 'Data Science',
    cutoff: '96.8%ile',
    savedOn: 'Nov 15, 2023',
    rank: '#21',
    rating: '4.5',
    image: cornellImage,
  },
];

const sortOptions = [
  { value: 'recent', label: 'Recently Saved' },
  { value: 'name', label: 'College Name' },
  { value: 'rating', label: 'Rating' },
  { value: 'cutoff', label: 'Predicted Cutoff' },
];

const Saved = () => {
  const [savedColleges, setSavedColleges] = useState(initialSavedColleges);
  const [sortOption, setSortOption] = useState('recent');
  const [sortOpen, setSortOpen] = useState(false);
  const navigate = useNavigate();

  const sortedColleges = useMemo(() => {
    const sorted = [...savedColleges];

    if (sortOption === 'name') {
      sorted.sort((a, b) => a.name.localeCompare(b.name));
    }

    if (sortOption === 'rating') {
      sorted.sort((a, b) => Number(b.rating) - Number(a.rating));
    }

    if (sortOption === 'cutoff') {
      sorted.sort((a, b) => Number(b.cutoff.replace('%ile', '')) - Number(a.cutoff.replace('%ile', '')));
    }

    return sorted;
  }, [savedColleges, sortOption]);

  const hasSavedColleges = sortedColleges.length > 0;

  const handleRemoveSaved = (id) => {
    setSavedColleges((prev) => prev.filter((college) => college.id !== id));
  };

  const handleViewDetails = (id) => {
    navigate(`/college/${id}`);
  };

  const handleCompare = (id) => {
    navigate('/compare');
  };

  const handleCompareAll = () => {
    navigate('/compare');
  };

  return (
    <MainLayout>
      <div className="saved-page">
        <div className="saved-header">
          <div className="saved-header-copy">
            <span className="saved-eyebrow">MY SAVED COLLEGES</span>
            <h1>My Saved Colleges</h1>
            <p>Review and compare the institutions you've bookmarked for your academic journey.</p>
          </div>

          <div className="saved-actions">
            <div className="sort-dropdown">
              <button
                type="button"
                className="sort-button"
                onClick={() => setSortOpen((prev) => !prev)}
              >
                <span className="material-symbols-outlined">sort</span>
                {sortOptions.find((option) => option.value === sortOption)?.label}
                <span className="material-symbols-outlined chevron">expand_more</span>
              </button>
              {sortOpen && (
                <div className="sort-menu">
                  {sortOptions.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      className={`sort-item ${sortOption === option.value ? 'active' : ''}`}
                      onClick={() => {
                        setSortOption(option.value);
                        setSortOpen(false);
                      }}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <button type="button" className="compare-all-button" onClick={handleCompareAll}>
              <span className="material-symbols-outlined">compare_arrows</span>
              Compare All
            </button>
          </div>
        </div>

        {hasSavedColleges ? (
          <div className="saved-grid">
            {sortedColleges.map((college) => (
              <article key={college.id} className="saved-card">
                <div className="saved-card-image-shell">
                  <img src={college.image} alt={college.name} className="saved-card-image" />
                  <button
                    type="button"
                    className="bookmark-button"
                    onClick={() => handleRemoveSaved(college.id)}
                    aria-label={`Remove ${college.name} from saved`}
                  >
                    <span className="material-symbols-outlined filled">bookmark</span>
                  </button>
                  <span className="rank-badge">Rank {college.rank}</span>
                  <span className="rating-badge">
                    <span className="material-symbols-outlined">star</span>
                    {college.rating}
                  </span>
                </div>

                <div className="saved-card-body">
                  <h2>{college.name}</h2>
                  <p className="saved-location">
                    <span className="material-symbols-outlined">location_on</span>
                    {college.location}
                  </p>

                  <div className="saved-details">
                    <div className="saved-detail-row">
                      <span className="detail-label">Target Course</span>
                      <span className="detail-value">{college.course}</span>
                    </div>
                    <div className="saved-detail-row">
                      <span className="detail-label">Predicted Cutoff</span>
                      <span className="detail-value primary">{college.cutoff}</span>
                    </div>
                    <div className="saved-detail-row">
                      <span className="detail-label">Saved On</span>
                      <span className="detail-value">{college.savedOn}</span>
                    </div>
                  </div>

                  <div className="saved-card-actions">
                    <button type="button" className="primary-button" onClick={() => handleViewDetails(college.id)}>
                      View Details
                    </button>
                    <button type="button" className="secondary-button" onClick={() => handleCompare(college.id)}>
                      Compare
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="saved-empty-state">
            <span className="material-symbols-outlined empty-icon">bookmark_border</span>
            <h2>No saved colleges yet</h2>
            <p>
              Explore our comprehensive database of institutions and save your favourites here to compare cutoffs and track your admission chances.
            </p>
            <button type="button" className="explore-button" onClick={() => navigate('/colleges')}>
              Explore Colleges
            </button>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default Saved;
