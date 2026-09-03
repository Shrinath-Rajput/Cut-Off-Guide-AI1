import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../../components/MainLayout/MainLayout';
import './Saved.css';
import { getSavedColleges, removeSavedCollege } from '../../services/api';
import { collegeImage, handleCollegeImageError } from '../../utils/collegeImage';
import toast from 'react-hot-toast';
import savedHeroImg from '../../assets/images/saved-colleges-hero.jpg';

const sortOptions = [
  { value: 'recent', label: 'Recently Saved' },
  { value: 'name', label: 'College Name' },
  { value: 'rating', label: 'Rating' },
  { value: 'cutoff', label: 'Predicted Cutoff' },
];

const Saved = () => {
  const [savedColleges, setSavedColleges] = useState([]);
  const [sortOption, setSortOption] = useState('recent');
  const [sortOpen, setSortOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    getSavedColleges()
      .then((saved) => setSavedColleges(Array.isArray(saved) ? saved : []))
      .catch(() => setSavedColleges([]));
  }, []);

  const sortedColleges = useMemo(() => {
    const sorted = [...savedColleges];

    if (sortOption === 'name') {
      sorted.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
    }

    if (sortOption === 'rating') {
      sorted.sort((a, b) => Number(b.rating || 0) - Number(a.rating || 0));
    }

    if (sortOption === 'cutoff') {
      sorted.sort((a, b) => {
        const valA = parseFloat(String(a.cutoff || '').replace(/[^0-9.]/g, '')) || 0;
        const valB = parseFloat(String(b.cutoff || '').replace(/[^0-9.]/g, '')) || 0;
        return valB - valA;
      });
    }

    return sorted;
  }, [savedColleges, sortOption]);

  const hasSavedColleges = sortedColleges.length > 0;

  const handleRemoveSaved = async (id, collegeName = 'College') => {
    try {
      await removeSavedCollege(id);
      setSavedColleges((prev) => prev.filter((college) => (college.college_id || college.collegeId || college.id) !== id));
      toast.success(`Removed ${collegeName} from saved colleges`);
    } catch (err) {
      toast.error('Could not remove college');
    }
  };

  const handleViewDetails = (id) => {
    navigate(`/colleges/${id}`);
  };

  const handleCompare = (college) => {
    const name = college.name || college.college_id || college.id;
    navigate(`/compare?college1=${encodeURIComponent(name)}`);
  };

  const handleCompareAll = () => {
    navigate('/compare');
  };

  return (
    <MainLayout>
      <div className="saved-page">
        {/* HERO BANNER WITH BACKGROUND IMAGE AND OVERLAPPING TEXT */}
        <section className="saved-hero-banner">
          <div className="saved-hero-bg-wrapper">
            <img
              src={savedHeroImg}
              alt="Different Roles, One Mission - Law, Medicine, Engineering"
              className="saved-hero-bg-img"
            />
            <div className="saved-hero-overlay" />
            <div className="saved-hero-glow" />
          </div>

          <div className="saved-hero-content">
            <div className="saved-hero-top-row">
              <div className="saved-pill-badge">
                <span className="material-symbols-outlined star-icon">auto_awesome</span>
                <span>DIFFERENT ROLES, ONE MISSION</span>
              </div>
              <div className="saved-stats-badge">
                <span className="material-symbols-outlined">bookmarks</span>
                <span>{savedColleges.length} {savedColleges.length === 1 ? 'College' : 'Colleges'} Saved</span>
              </div>
            </div>

            <div className="saved-hero-text-block">
              <h1 className="saved-hero-title">
                My Saved Colleges
              </h1>
              <p className="saved-hero-subtitle">
                Building a Better Tomorrow — Review, organize, and compare the premier engineering, medical, and professional institutions you've shortlisted for your dream career.
              </p>
            </div>

            <div className="saved-hero-bottom-bar">
              <div className="saved-tags-row">
                <span className="saved-role-tag">
                  <span className="material-symbols-outlined">gavel</span> Law
                </span>
                <span className="saved-role-tag">
                  <span className="material-symbols-outlined">medical_services</span> Medicine
                </span>
                <span className="saved-role-tag">
                  <span className="material-symbols-outlined">engineering</span> Engineering
                </span>
              </div>

              <div className="saved-actions-toolbar">
                <div className="sort-dropdown">
                  <button
                    type="button"
                    className="sort-button glass-button"
                    onClick={() => setSortOpen((prev) => !prev)}
                    aria-label="Sort saved colleges"
                  >
                    <span className="material-symbols-outlined">sort</span>
                    <span>{sortOptions.find((option) => option.value === sortOption)?.label}</span>
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
          </div>
        </section>

        {/* MAIN BODY CONTENT */}
        <div className="saved-main-container">
          {hasSavedColleges ? (
            <div className="saved-grid">
              {sortedColleges.map((college) => {
                const cid = college.college_id || college.collegeId || college.id;
                return (
                  <article key={cid} className="saved-card">
                    <div className="saved-card-image-shell">
                      <img
                        src={collegeImage(college.image)}
                        alt={college.name}
                        className="saved-card-image"
                        onError={handleCollegeImageError}
                      />
                      <button
                        type="button"
                        className="bookmark-button"
                        onClick={() => handleRemoveSaved(cid, college.name)}
                        title="Click to Unsave College"
                        aria-label={`Remove ${college.name} from saved`}
                      >
                        <span className="material-symbols-outlined filled">bookmark</span>
                      </button>
                      {college.rank && <span className="rank-badge">Rank #{college.rank}</span>}
                      <span className="rating-badge">
                        <span className="material-symbols-outlined">star</span>
                        {college.rating || '4.5'}
                      </span>
                    </div>

                    <div className="saved-card-body">
                      <h2>{college.name}</h2>
                      <p className="saved-location">
                        <span className="material-symbols-outlined">location_on</span>
                        {college.location || 'India'}
                      </p>

                      <div className="saved-details">
                        {college.course && (
                          <div className="saved-detail-row">
                            <span className="detail-label">Target Course</span>
                            <span className="detail-value">{college.course}</span>
                          </div>
                        )}
                        {college.cutoff && (
                          <div className="saved-detail-row">
                            <span className="detail-label">Predicted Cutoff</span>
                            <span className="detail-value primary">{college.cutoff}</span>
                          </div>
                        )}
                        <div className="saved-detail-row">
                          <span className="detail-label">Saved On</span>
                          <span className="detail-value">{college.savedOn || 'Recent'}</span>
                        </div>
                      </div>

                      <div className="saved-card-actions">
                        <div className="saved-card-actions-row">
                          <button type="button" className="primary-button" onClick={() => handleViewDetails(cid)}>
                            View Details
                          </button>
                          <button type="button" className="secondary-button" onClick={() => handleCompare(college)}>
                            Compare
                          </button>
                        </div>
                        <button
                          type="button"
                          className="unsave-button"
                          onClick={() => handleRemoveSaved(cid, college.name)}
                          title="Remove college from your saved list"
                        >
                          <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                            bookmark_remove
                          </span>
                          Unsave College
                        </button>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          ) : (
            <div className="saved-empty-state">
              <div className="empty-icon-wrapper">
                <span className="material-symbols-outlined empty-icon">bookmark_border</span>
              </div>
              <h2>No Saved Colleges Yet</h2>
              <p>
                Explore our comprehensive database of engineering, medical, and professional institutions to save your favorites, track cutoffs, and compare admission probabilities.
              </p>
              <div className="empty-actions">
                <button type="button" className="explore-button" onClick={() => navigate('/colleges')}>
                  <span className="material-symbols-outlined">search</span>
                  Explore Colleges
                </button>
                <button type="button" className="compare-empty-button" onClick={() => navigate('/compare')}>
                  <span className="material-symbols-outlined">compare_arrows</span>
                  Compare Tool
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
};

export default Saved;
