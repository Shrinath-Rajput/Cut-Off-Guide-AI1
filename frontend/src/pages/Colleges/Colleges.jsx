import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import './Colleges.css';

import { getColleges } from '../../services/api';

const stateOptions = ['California', 'New York', 'Massachusetts'];
const courseOptions = ['Computer Science', 'Engineering', 'Business'];
const sortOptions = [
  { value: 'relevance', label: 'Sort by: Relevance' },
  { value: 'ranking', label: 'Sort by: Ranking (High to Low)' },
  { value: 'fees', label: 'Sort by: Fees (Low to High)' },
];

const Colleges = () => {
  const navigate = useNavigate();
  const searchInputRef = useRef(null);
  const [search, setSearch] = useState('');
  const [selectedStates, setSelectedStates] = useState([]);
  const [selectedCourses, setSelectedCourses] = useState([]);
  const [selectedType, setSelectedType] = useState('');
  const [feeValue, setFeeValue] = useState(100000);
  const [sortOption, setSortOption] = useState('relevance');
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);
  const [bookmarked, setBookmarked] = useState({});
  const [compareSelected, setCompareSelected] = useState({});
  const [currentPage, setCurrentPage] = useState(1);
  const [collegeItems, setCollegeItems] = useState([]);
  const [totalCollegeCount, setTotalCollegeCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    const fetchColleges = async () => {
      try {
        const params = {
          page: currentPage,
          limit: 10,
          search: search.trim() || undefined,
          states: selectedStates.length ? selectedStates : undefined,
          courses: selectedCourses.length ? selectedCourses : undefined,
          max_fee: feeValue < 100000 ? feeValue : undefined,
          college_type: selectedType || undefined,
          sort: sortOption !== 'relevance' ? sortOption : undefined,
        };
        const data = await getColleges(params);
        setCollegeItems(data.data);
        setTotalCollegeCount(data.total);
        setTotalPages(data.total_pages);
      } catch (error) {
        console.error('Failed to fetch colleges:', error);
      }
    };
    
    const timeoutId = setTimeout(fetchColleges, 300);
    return () => clearTimeout(timeoutId);
  }, [search, selectedStates, selectedCourses, feeValue, selectedType, sortOption, currentPage]);

  useEffect(() => {
    setCurrentPage(1);
  }, [search, selectedStates, selectedCourses, feeValue, selectedType, sortOption]);

  const toggleSelection = (value, selectedValues, setSelectedValues) => {
    if (selectedValues.includes(value)) {
      setSelectedValues(selectedValues.filter((item) => item !== value));
    } else {
      setSelectedValues([...selectedValues, value]);
    }
  };

  const handleSearchFocus = () => {
    searchInputRef.current?.focus();
  };

  const displayStart = collegeItems.length ? (currentPage - 1) * 10 + 1 : 0;
  const displayEnd = collegeItems.length ? Math.min(currentPage * 10, totalCollegeCount) : 0;
  const hasResults = collegeItems.length > 0;

  const getDisplayedPages = () => {
    const pages = [];
    let start = Math.max(1, currentPage - 2);
    let end = Math.min(totalPages, start + 4);
    if (end - start < 4) {
       start = Math.max(1, end - 4);
    }
    for (let i = start; i <= end; i++) {
       pages.push(i);
    }
    return pages;
  };
  const dynamicDisplayedPages = getDisplayedPages();

  const toggleBookmark = (id) => {
    setBookmarked((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const toggleCompare = (id) => {
    setCompareSelected((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const selectedCompareCount = Object.values(compareSelected).filter(Boolean).length;

  const handleCompareNavigate = () => {
    const selectedIds = Object.keys(compareSelected).filter((id) => compareSelected[id]);
    navigate(`/compare?ids=${selectedIds.join(',')}`);
  };

  const clearAllFilters = () => {
    setSelectedStates([]);
    setSelectedCourses([]);
    setSelectedType('');
    setFeeValue(100000);
  };

  return (
    <div className="colleges-page">
      <Navbar onSearch={handleSearchFocus} />

      <main className="colleges-main">
        <header className="colleges-header">
          <div className="colleges-header-copy">
            <h1>Explore Colleges</h1>
            <p>
              Discover elite institutions, analyze historical cutoffs, and pinpoint your ideal academic destination with AI-driven insights.
            </p>
          </div>

          <div className="search-input-wrapper">
            <span className="material-symbols-outlined search-icon">search</span>
            <input
              ref={searchInputRef}
              id="colleges-search-input"
              className="search-input"
              type="text"
              placeholder="Search colleges, courses or locations..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>
        </header>

        <div className="colleges-layout">
          <aside className="filters-sidebar">
            <div className="filters-header">
              <h2>Filters</h2>
              <button type="button" className="clear-button" onClick={clearAllFilters}>
                Clear All
              </button>
            </div>

            <div className="filter-group">
              <div className="filter-group-title">
                <span>State</span>
                <span className="material-symbols-outlined">expand_more</span>
              </div>
              <div className="filter-options">
                {stateOptions.map((state) => (
                  <label key={state} className="filter-option">
                    <input
                      type="checkbox"
                      checked={selectedStates.includes(state)}
                      onChange={() => toggleSelection(state, selectedStates, setSelectedStates)}
                    />
                    <span>{state}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="divider" />

            <div className="filter-group">
              <div className="filter-group-title">
                <span>Course / Major</span>
                <span className="material-symbols-outlined">expand_more</span>
              </div>
              <div className="filter-options">
                {courseOptions.map((course) => (
                  <label key={course} className="filter-option">
                    <input
                      type="checkbox"
                      checked={selectedCourses.includes(course)}
                      onChange={() => toggleSelection(course, selectedCourses, setSelectedCourses)}
                    />
                    <span>{course}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="divider" />

            <div className="filter-group">
              <div className="filter-group-title">
                <span>Approx Fees (Annual)</span>
                <span className="material-symbols-outlined">expand_more</span>
              </div>
              <div className="fee-group">
                <input
                  className="fee-range"
                  type="range"
                  min="0"
                  max="100000"
                  step="1000"
                  value={feeValue}
                  onChange={(event) => setFeeValue(Number(event.target.value))}
                />
                <div className="fee-labels">
                  <span>$0</span>
                  <span>$100k+</span>
                </div>
              </div>
            </div>

            <div className="divider" />

            <div className="filter-group">
              <div className="filter-group-title">
                <span>College Type</span>
                <span className="material-symbols-outlined">expand_more</span>
              </div>
              <div className="type-buttons">
                {['Public', 'Private'].map((type) => (
                  <button
                    key={type}
                    type="button"
                    className={`type-button ${selectedType === type ? 'selected' : ''}`}
                    onClick={() => setSelectedType(selectedType === type ? '' : type)}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>
          </aside>

          <section className="results-column">
            <div className="results-toolbar">
              <p>
                Showing <strong>{displayStart}-{displayEnd}</strong> of <strong>{totalCollegeCount}</strong> Colleges
              </p>
              <div className="results-actions">
                <button type="button" className="mobile-filter-toggle" onClick={() => setMobileFiltersOpen(true)}>
                  <span className="material-symbols-outlined">tune</span>
                  Filters
                </button>
                <select value={sortOption} onChange={(event) => setSortOption(event.target.value)} className="sort-select">
                  {sortOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className={`cards-list ${hasResults ? '' : 'empty-state'}`}>
              {hasResults ? (
                collegeItems.map((college) => (
                  <article key={college.id} className="college-card">
                    <div className="card-image">
                      <img src={college.image} alt={college.name} />
                      <div className="card-badge">#{college.rank} National Rank</div>
                      <button
                        type="button"
                        className="bookmark-button"
                        onClick={() => toggleBookmark(college.id)}
                        aria-label={bookmarked[college.id] ? 'Remove bookmark' : 'Bookmark college'}
                      >
                        <span className="material-symbols-outlined">
                          {bookmarked[college.id] ? 'bookmark' : 'bookmark_border'}
                        </span>
                      </button>
                    </div>

                    <div className="card-content">
                      <div>
                        <div className="card-header-row">
                          <h3>{college.name}</h3>
                          <div className="card-rating">
                            <span className="material-symbols-outlined rating-icon" style={{ fontVariationSettings: "'FILL' 1" }}>
                              star
                            </span>
                            <span>{college.rating}</span>
                          </div>
                        </div>
                        <p className="card-location">
                          <span className="material-symbols-outlined">location_on</span>
                          {college.location}
                        </p>
                        <div className="card-stats">
                          <div className="stat-block">
                            <p className="stat-label">Top Courses</p>
                            <p className="stat-value">{college.courses.join(', ')}</p>
                          </div>
                          <div className="stat-block">
                            <p className="stat-label">Approx Fees</p>
                            <p className="stat-value">{college.feeLabel}</p>
                          </div>
                          <div className="stat-block stat-block-highlight">
                            <p className="stat-label">Avg. Cutoff Percentile</p>
                            <p className="stat-value stat-value-strong">{college.cutoff}</p>
                          </div>
                        </div>
                      </div>

                      <div className="card-footer-row">
                        <label className={`compare-label ${compareSelected[college.id] ? 'selected' : ''}`}>
                          <input
                            type="checkbox"
                            checked={!!compareSelected[college.id]}
                            onChange={() => toggleCompare(college.id)}
                            disabled={!compareSelected[college.id] && selectedCompareCount >= 4}
                          />
                          <span className="compare-checkbox-box">
                            <span className="material-symbols-outlined">check</span>
                          </span>
                          <span>Compare</span>
                        </label>
                        <Link to={`/college/${college.id}`} className="view-college-button">
                          View College
                        </Link>
                      </div>
                    </div>
                  </article>
                ))
              ) : (
                <div className="empty-results">
                  <div className="empty-results-icon material-symbols-outlined">search_off</div>
                  <h3>No colleges found</h3>
                  <p>Try widening your search or clearing a few filters to see more results.</p>
                </div>
              )}
            </div>

            <div className="pagination">
              <button
                type="button"
                className="pagination-button"
                onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
              >
                <span className="material-symbols-outlined">chevron_left</span>
              </button>

              {dynamicDisplayedPages.map((pageNumber) => (
                <button
                  key={pageNumber}
                  type="button"
                  className={`pagination-page ${currentPage === pageNumber ? 'active' : ''}`}
                  onClick={() => setCurrentPage(pageNumber)}
                >
                  {pageNumber}
                </button>
              ))}

              <button
                type="button"
                className="pagination-button"
                onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
                disabled={currentPage >= totalPages}
              >
                <span className="material-symbols-outlined">chevron_right</span>
              </button>
            </div>
          </section>
        </div>
      </main>

      <Footer />

      <div className={`mobile-filter-panel ${mobileFiltersOpen ? 'open' : ''}`}>
        <div className="mobile-filter-content">
          <div className="mobile-filter-header">
            <h2>Filters</h2>
            <button type="button" className="icon-button close-button" onClick={() => setMobileFiltersOpen(false)}>
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>
          <div className="filters-sidebar mobile-filter-body">
            <div className="filter-group">
              <div className="filter-group-title">
                <span>State</span>
                <span className="material-symbols-outlined">expand_more</span>
              </div>
              <div className="filter-options">
                {stateOptions.map((state) => (
                  <label key={state} className="filter-option">
                    <input
                      type="checkbox"
                      checked={selectedStates.includes(state)}
                      onChange={() => toggleSelection(state, selectedStates, setSelectedStates)}
                    />
                    <span>{state}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="divider" />

            <div className="filter-group">
              <div className="filter-group-title">
                <span>Course / Major</span>
                <span className="material-symbols-outlined">expand_more</span>
              </div>
              <div className="filter-options">
                {courseOptions.map((course) => (
                  <label key={course} className="filter-option">
                    <input
                      type="checkbox"
                      checked={selectedCourses.includes(course)}
                      onChange={() => toggleSelection(course, selectedCourses, setSelectedCourses)}
                    />
                    <span>{course}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="divider" />

            <div className="filter-group">
              <div className="filter-group-title">
                <span>Approx Fees (Annual)</span>
                <span className="material-symbols-outlined">expand_more</span>
              </div>
              <div className="fee-group">
                <input
                  className="fee-range"
                  type="range"
                  min="0"
                  max="100000"
                  step="1000"
                  value={feeValue}
                  onChange={(event) => setFeeValue(Number(event.target.value))}
                />
                <div className="fee-labels">
                  <span>$0</span>
                  <span>$100k+</span>
                </div>
              </div>
            </div>

            <div className="divider" />

            <div className="filter-group">
              <div className="filter-group-title">
                <span>College Type</span>
                <span className="material-symbols-outlined">expand_more</span>
              </div>
              <div className="type-buttons">
                {['Public', 'Private'].map((type) => (
                  <button
                    key={type}
                    type="button"
                    className={`type-button ${selectedType === type ? 'selected' : ''}`}
                    onClick={() => setSelectedType(selectedType === type ? '' : type)}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            <button type="button" className="mobile-clear-button" onClick={clearAllFilters}>
              Clear All
            </button>
          </div>
        </div>
      </div>

      {selectedCompareCount > 0 && (
        <div className="compare-banner">
          <div className="compare-banner-content">
            <p>{selectedCompareCount} {selectedCompareCount === 1 ? 'college' : 'colleges'} selected for comparison (Max 4)</p>
            <div className="compare-banner-actions">
              <button 
                type="button" 
                className="compare-banner-btn secondary"
                onClick={() => setCompareSelected({})}
              >
                Clear
              </button>
              <button 
                type="button" 
                className="compare-banner-btn primary"
                onClick={handleCompareNavigate}
                disabled={selectedCompareCount < 2}
              >
                Compare Now
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Colleges;
