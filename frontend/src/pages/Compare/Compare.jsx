import { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import { compareCollegesAI, getColleges } from '../../services/api';
import compareHeroBg from '../../assets/images/compare-hero-student.jpg';
import './Compare.css';

const PRESET_COLLEGES = [
  'COEP Technological University Pune',
  'VJTI Mumbai',
  'PICT Pune',
  'SPIT Mumbai',
  'IIT Bombay',
  'IIT Delhi',
  'RV College of Engineering Bangalore',
  'NIT Surathkal',
  'Thapar Institute of Engineering Patiala',
  'BITS Pilani',
  'MIT-WPU Pune',
  'VIT Pune',
];

const Compare = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // Read initial params (default to empty string so search bars are clean)
  const paramC1 = searchParams.get('college1') || searchParams.get('c1') || searchParams.get('ids')?.split(',')[0] || '';
  const paramC2 = searchParams.get('college2') || searchParams.get('c2') || searchParams.get('ids')?.split(',')[1] || '';

  const [college1Input, setCollege1Input] = useState(paramC1);
  const [college2Input, setCollege2Input] = useState(paramC2);

  const [c1Suggestions, setC1Suggestions] = useState([]);
  const [c2Suggestions, setC2Suggestions] = useState([]);
  const [showC1Dropdown, setShowC1Dropdown] = useState(false);
  const [showC2Dropdown, setShowC2Dropdown] = useState(false);

  const [loading, setLoading] = useState(false);
  const [comparisonData, setComparisonData] = useState(null);
  const [error, setError] = useState(null);

  const dropdown1Ref = useRef(null);
  const dropdown2Ref = useRef(null);

  // Close dropdowns on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdown1Ref.current && !dropdown1Ref.current.contains(e.target)) {
        setShowC1Dropdown(false);
      }
      if (dropdown2Ref.current && !dropdown2Ref.current.contains(e.target)) {
        setShowC2Dropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch comparison function
  const runComparison = async (c1, c2) => {
    if (!c1 || !c2) return;
    setLoading(true);
    setError(null);
    try {
      const res = await compareCollegesAI(c1, c2);
      if (res && res.data) {
        setComparisonData(res.data);
        // update search params in URL
        setSearchParams({ college1: c1, college2: c2 });
      } else {
        throw new Error('Invalid comparison response');
      }
    } catch (err) {
      console.error('Error fetching AI comparison:', err);
      setError('Could not complete AI comparison. Please verify college names and try again.');
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    if (paramC1 && paramC2) {
      runComparison(paramC1, paramC2);
    }
  }, [paramC1, paramC2]);

  // Autocomplete fetcher
  const handleInputChange = async (val, slot) => {
    if (slot === 1) {
      setCollege1Input(val);
      if (val.trim().length > 1) {
        try {
          const res = await getColleges({ search: val.trim(), limit: 5 });
          const hits = res.data || [];
          setC1Suggestions(hits.map((h) => h.name));
          setShowC1Dropdown(true);
        } catch {
          setC1Suggestions(PRESET_COLLEGES.filter((p) => p.toLowerCase().includes(val.toLowerCase())));
          setShowC1Dropdown(true);
        }
      } else {
        setShowC1Dropdown(false);
      }
    } else {
      setCollege2Input(val);
      if (val.trim().length > 1) {
        try {
          const res = await getColleges({ search: val.trim(), limit: 5 });
          const hits = res.data || [];
          setC2Suggestions(hits.map((h) => h.name));
          setShowC2Dropdown(true);
        } catch {
          setC2Suggestions(PRESET_COLLEGES.filter((p) => p.toLowerCase().includes(val.toLowerCase())));
          setShowC2Dropdown(true);
        }
      } else {
        setShowC2Dropdown(false);
      }
    }
  };

  const handleSelectSuggestion = (collegeName, slot) => {
    if (slot === 1) {
      setCollege1Input(collegeName);
      setShowC1Dropdown(false);
      runComparison(collegeName, college2Input);
    } else {
      setCollege2Input(collegeName);
      setShowC2Dropdown(false);
      runComparison(college1Input, collegeName);
    }
  };

  const handleSwap = () => {
    const temp = college1Input;
    setCollege1Input(college2Input);
    setCollege2Input(temp);
    runComparison(college2Input, temp);
  };

  const handleManualCompare = (e) => {
    e.preventDefault();
    if (college1Input && college2Input) {
      runComparison(college1Input, college2Input);
    }
  };

  // Helper for progress bar
  const parseNum = (val) => {
    if (!val) return 0;
    const m = String(val).match(/(\d+(?:\.\d+)?)/);
    return m ? parseFloat(m[1]) : 0;
  };

  const c1 = comparisonData?.college1 || {};
  const c2 = comparisonData?.college2 || {};

  const c1Avg = parseNum(c1.placement_avg || c1.averagePackage || '7.5');
  const c2Avg = parseNum(c2.placement_avg || c2.averagePackage || '7.0');
  const maxAvg = Math.max(c1Avg, c2Avg, 1);

  const c1High = parseNum(c1.highest_package || c1.highestPackage || '42');
  const c2High = parseNum(c2.highest_package || c2.highestPackage || '38');
  const maxHigh = Math.max(c1High, c2High, 1);

  return (
    <div className="compare-page-shell">
      <Navbar />

      <main className="compare-main-container">
        {/* Hero Section with Image Background & Overlapping Glass Panel */}
        <section className="compare-hero-section">
          <div className="compare-hero-media-wrap">
            <img
              src={compareHeroBg}
              alt="Which College to Choose? Student Career and College Decision"
              className="compare-hero-img"
            />
            <div className="compare-hero-overlay" />
          </div>

          <div className="compare-hero-glass-panel compare-glass">
            <div className="compare-eyebrow">
              <span className="material-symbols-outlined text-sm">psychology</span>
              <span>AI Head-to-Head Comparison</span>
            </div>
            <h1 className="compare-title">Compare Any Two Colleges with AI</h1>
            <p className="compare-subtitle">
              Evaluate placements, cutoffs, tuition ROI, NIRF rankings, and get a definitive AI recommendation for your engineering career.
            </p>
          </div>
        </section>

        {/* Dual College Selectors Box */}
        <section className="selectors-box compare-glass">
          <form onSubmit={handleManualCompare}>
            <div className="selectors-grid">
              {/* College 1 Selector */}
              <div className="selector-column" ref={dropdown1Ref}>
                <label className="selector-label">
                  <span className="material-symbols-outlined text-sm">school</span>
                  College 1 (Primary)
                </label>
                <div className="selector-input-wrap">
                  <span className="material-symbols-outlined selector-icon">search</span>
                  <input
                    type="text"
                    className="selector-input"
                    value={college1Input}
                    onChange={(e) => handleInputChange(e.target.value, 1)}
                    onFocus={() => college1Input.length > 1 && setShowC1Dropdown(true)}
                    placeholder="Search or enter College 1 (e.g. COEP Pune)"
                  />
                  {college1Input && (
                    <button
                      type="button"
                      className="clear-btn"
                      onClick={() => setCollege1Input('')}
                      aria-label="Clear College 1"
                    >
                      <span className="material-symbols-outlined text-sm">close</span>
                    </button>
                  )}
                </div>

                {showC1Dropdown && c1Suggestions.length > 0 && (
                  <ul className="autocomplete-dropdown">
                    {c1Suggestions.map((sug, i) => (
                      <li key={i} className="autocomplete-item" onClick={() => handleSelectSuggestion(sug, 1)}>
                        <span className="autocomplete-name">{sug}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {/* VS Divider & Swap Button */}
              <div className="vs-divider">
                <div className="vs-badge">VS</div>
                <button
                  type="button"
                  className="swap-btn"
                  onClick={handleSwap}
                  title="Swap Colleges"
                  aria-label="Swap Colleges"
                >
                  <span className="material-symbols-outlined text-sm">swap_horiz</span>
                </button>
              </div>

              {/* College 2 Selector */}
              <div className="selector-column" ref={dropdown2Ref}>
                <label className="selector-label">
                  <span className="material-symbols-outlined text-sm">school</span>
                  College 2 (Comparison)
                </label>
                <div className="selector-input-wrap">
                  <span className="material-symbols-outlined selector-icon">search</span>
                  <input
                    type="text"
                    className="selector-input"
                    value={college2Input}
                    onChange={(e) => handleInputChange(e.target.value, 2)}
                    onFocus={() => college2Input.length > 1 && setShowC2Dropdown(true)}
                    placeholder="Search or enter College 2 (e.g. VJTI Mumbai)"
                  />
                  {college2Input && (
                    <button
                      type="button"
                      className="clear-btn"
                      onClick={() => setCollege2Input('')}
                      aria-label="Clear College 2"
                    >
                      <span className="material-symbols-outlined text-sm">close</span>
                    </button>
                  )}
                </div>

                {showC2Dropdown && c2Suggestions.length > 0 && (
                  <ul className="autocomplete-dropdown">
                    {c2Suggestions.map((sug, i) => (
                      <li key={i} className="autocomplete-item" onClick={() => handleSelectSuggestion(sug, 2)}>
                        <span className="autocomplete-name">{sug}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            <div className="run-compare-wrap">
              <button type="submit" className="run-compare-btn" disabled={loading || !college1Input || !college2Input}>
                <span className="material-symbols-outlined text-sm">
                  {loading ? 'hourglass_top' : 'compare_arrows'}
                </span>
                {loading ? 'AI Council Analyzing Comparison...' : 'Compare Colleges with AI'}
              </button>
            </div>
          </form>
        </section>

        {/* Error State */}
        {error && (
          <div className="bg-error-container text-on-error-container p-4 rounded-2xl mb-8 flex items-center gap-3 font-semibold text-sm border border-error">
            <span className="material-symbols-outlined">error</span>
            {error}
          </div>
        )}

        {/* Loading Skeleton */}
        {loading && (
          <div className="compare-glass rounded-3xl p-12 text-center my-8">
            <div className="inline-block animate-spin text-primary mb-3">
              <span className="material-symbols-outlined text-4xl">sync</span>
            </div>
            <h3 className="font-display font-bold text-lg text-on-surface">Evaluating Head-to-Head Metrics...</h3>
            <p className="text-on-surface-variant text-sm mt-1">
              Analyzing cutoffs, placements, NIRF data, and generating AI recommendation.
            </p>
          </div>
        )}

        {/* Comparison Results */}
        {!loading && comparisonData && (
          <>
            {/* AI Verdict Card */}
            <section className="verdict-card compare-glass">
              <div className="verdict-header">
                <div className="verdict-icon">
                  <span className="material-symbols-outlined text-xl">gavel</span>
                </div>
                <div>
                  <h3 className="verdict-title">AI Council Recommendation & Verdict</h3>
                  <span className="text-xs font-bold text-surface-tint uppercase tracking-wider">
                    Powered by Cutoff Guide AI
                  </span>
                </div>
              </div>

              <p className="verdict-text mb-0">{comparisonData.verdict}</p>
            </section>

            {/* Head-to-Head Comparison Matrix */}
            <section className="compare-matrix-section compare-glass">
              <h3 className="font-display font-extrabold text-xl text-on-surface mb-4">
                Head-to-Head Comparison Matrix
              </h3>
              <table className="matrix-table">
                <thead>
                  <tr>
                    <th style={{ width: '28%' }}>Metric</th>
                    <th style={{ width: '36%', color: '#944a00' }}>{c1.name || college1Input}</th>
                    <th style={{ width: '36%', color: '#944a00' }}>{c2.name || college2Input}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="matrix-row">
                    <td className="metric-name-cell">
                      <span className="material-symbols-outlined">military_tech</span>
                      NIRF Ranking
                    </td>
                    <td className="college-value-cell highlight">
                      #{c1.nirf_rank || c1.rank || 'N/A'}
                    </td>
                    <td className="college-value-cell highlight">
                      #{c2.nirf_rank || c2.rank || 'N/A'}
                    </td>
                  </tr>

                  <tr className="matrix-row">
                    <td className="metric-name-cell">
                      <span className="material-symbols-outlined">trending_up</span>
                      Average Placement CTC
                    </td>
                    <td className="college-value-cell highlight">
                      {c1.placement_avg || c1.averagePackage || '₹7.5 LPA'}
                    </td>
                    <td className="college-value-cell highlight">
                      {c2.placement_avg || c2.averagePackage || '₹7.0 LPA'}
                    </td>
                  </tr>

                  <tr className="matrix-row">
                    <td className="metric-name-cell">
                      <span className="material-symbols-outlined">workspace_premium</span>
                      Highest Package
                    </td>
                    <td className="college-value-cell">
                      {c1.highest_package || c1.highestPackage || '₹42.0 LPA'}
                    </td>
                    <td className="college-value-cell">
                      {c2.highest_package || c2.highestPackage || '₹38.0 LPA'}
                    </td>
                  </tr>

                  <tr className="matrix-row">
                    <td className="metric-name-cell">
                      <span className="material-symbols-outlined">currency_rupee</span>
                      Annual Tuition Fees
                    </td>
                    <td className="college-value-cell">
                      {c1.fee_display || c1.feeLabel || '₹1.4 Lakh / yr'}
                    </td>
                    <td className="college-value-cell">
                      {c2.fee_display || c2.feeLabel || '₹1.5 Lakh / yr'}
                    </td>
                  </tr>

                  <tr className="matrix-row">
                    <td className="metric-name-cell">
                      <span className="material-symbols-outlined">location_on</span>
                      Location & City
                    </td>
                    <td className="college-value-cell">{c1.location || 'India'}</td>
                    <td className="college-value-cell">{c2.location || 'India'}</td>
                  </tr>

                  <tr className="matrix-row">
                    <td className="metric-name-cell">
                      <span className="material-symbols-outlined">account_balance</span>
                      Institute Type
                    </td>
                    <td className="college-value-cell">{c1.type || 'Autonomous / Engineering'}</td>
                    <td className="college-value-cell">{c2.type || 'Autonomous / Engineering'}</td>
                  </tr>

                  <tr className="matrix-row">
                    <td className="metric-name-cell">
                      <span className="material-symbols-outlined">assignment</span>
                      Entrance Exams
                    </td>
                    <td className="college-value-cell">
                      {(c1.exams || ['MHT-CET', 'JEE Main']).join(', ')}
                    </td>
                    <td className="college-value-cell">
                      {(c2.exams || ['MHT-CET', 'JEE Main']).join(', ')}
                    </td>
                  </tr>

                  <tr className="matrix-row">
                    <td className="metric-name-cell">
                      <span className="material-symbols-outlined">corporate_fare</span>
                      Top Recruiters
                    </td>
                    <td className="college-value-cell">
                      {(c1.top_recruiters || ['TCS', 'Infosys', 'Capgemini', 'Amazon']).slice(0, 4).join(', ')}
                    </td>
                    <td className="college-value-cell">
                      {(c2.top_recruiters || ['TCS', 'Infosys', 'Capgemini', 'Wipro']).slice(0, 4).join(', ')}
                    </td>
                  </tr>
                </tbody>
              </table>
            </section>

            {/* Placement Comparison Visual Bars */}
            <section className="selectors-box compare-glass">
              <h3 className="font-display font-extrabold text-xl text-on-surface mb-6">
                Placement Package Comparison (CTC Visual)
              </h3>
              <div className="grid md:grid-cols-2 gap-6">
                {/* Average CTC Bar */}
                <div className="bg-surface p-5 rounded-2xl border border-outline-variant">
                  <p className="text-xs font-bold uppercase text-surface-tint tracking-wider mb-2">
                    Average Package (CTC)
                  </p>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-xs font-bold mb-1">
                        <span className="truncate max-w-[200px]">{c1.name || college1Input}</span>
                        <span className="text-primary">{c1.placement_avg || c1.averagePackage || '₹7.5 LPA'}</span>
                      </div>
                      <div className="w-full bg-surface-container-high rounded-full h-3 overflow-hidden">
                        <div
                          className="bg-primary h-full rounded-full transition-all duration-700"
                          style={{ width: `${(c1Avg / maxAvg) * 100}%` }}
                        />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs font-bold mb-1">
                        <span className="truncate max-w-[200px]">{c2.name || college2Input}</span>
                        <span className="text-secondary">{c2.placement_avg || c2.averagePackage || '₹7.0 LPA'}</span>
                      </div>
                      <div className="w-full bg-surface-container-high rounded-full h-3 overflow-hidden">
                        <div
                          className="bg-secondary h-full rounded-full transition-all duration-700"
                          style={{ width: `${(c2Avg / maxAvg) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Highest CTC Bar */}
                <div className="bg-surface p-5 rounded-2xl border border-outline-variant">
                  <p className="text-xs font-bold uppercase text-surface-tint tracking-wider mb-2">
                    Highest Package (CTC)
                  </p>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-xs font-bold mb-1">
                        <span className="truncate max-w-[200px]">{c1.name || college1Input}</span>
                        <span className="text-primary">{c1.highest_package || c1.highestPackage || '₹42.0 LPA'}</span>
                      </div>
                      <div className="w-full bg-surface-container-high rounded-full h-3 overflow-hidden">
                        <div
                          className="bg-primary h-full rounded-full transition-all duration-700"
                          style={{ width: `${(c1High / maxHigh) * 100}%` }}
                        />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs font-bold mb-1">
                        <span className="truncate max-w-[200px]">{c2.name || college2Input}</span>
                        <span className="text-secondary">{c2.highest_package || c2.highestPackage || '₹38.0 LPA'}</span>
                      </div>
                      <div className="w-full bg-surface-container-high rounded-full h-3 overflow-hidden">
                        <div
                          className="bg-secondary h-full rounded-full transition-all duration-700"
                          style={{ width: `${(c2High / maxHigh) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Pros Section: Why Choose College 1 vs Why Choose College 2 */}
            <div className="pros-grid">
              <div className="pros-card">
                <h4 className="pros-title">
                  <span className="material-symbols-outlined">thumb_up</span>
                  Why Choose {c1.name || college1Input}
                </h4>
                <ul className="pros-list">
                  {(comparisonData.pros_college1 || []).map((pro, idx) => (
                    <li key={idx}>
                      <span className="material-symbols-outlined">check_circle</span>
                      <span>{pro}</span>
                    </li>
                  ))}
                </ul>
                <div className="mt-6 pt-4 border-t border-outline-variant flex justify-between items-center">
                  <Link
                    to="/colleges"
                    className="text-xs font-bold text-primary hover:underline inline-flex items-center gap-1"
                  >
                    Explore Colleges
                    <span className="material-symbols-outlined text-xs">arrow_forward</span>
                  </Link>
                  <Link
                    to="/cutoff"
                    className="text-xs font-bold text-surface-tint hover:underline inline-flex items-center gap-1"
                  >
                    Predict Cutoff
                  </Link>
                </div>
              </div>

              <div className="pros-card">
                <h4 className="pros-title">
                  <span className="material-symbols-outlined">thumb_up</span>
                  Why Choose {c2.name || college2Input}
                </h4>
                <ul className="pros-list">
                  {(comparisonData.pros_college2 || []).map((pro, idx) => (
                    <li key={idx}>
                      <span className="material-symbols-outlined">check_circle</span>
                      <span>{pro}</span>
                    </li>
                  ))}
                </ul>
                <div className="mt-6 pt-4 border-t border-outline-variant flex justify-between items-center">
                  <Link
                    to="/colleges"
                    className="text-xs font-bold text-primary hover:underline inline-flex items-center gap-1"
                  >
                    Explore Colleges
                    <span className="material-symbols-outlined text-xs">arrow_forward</span>
                  </Link>
                  <Link
                    to="/cutoff"
                    className="text-xs font-bold text-surface-tint hover:underline inline-flex items-center gap-1"
                  >
                    Predict Cutoff
                  </Link>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Empty State when no colleges are compared yet */}
        {!loading && !comparisonData && !error && (
          <section className="compare-glass rounded-3xl p-10 text-center my-6">
            <div className="w-16 h-16 rounded-2xl bg-surface-container-high text-primary flex items-center justify-center mx-auto mb-4 shadow-sm">
              <span className="material-symbols-outlined text-3xl">compare_arrows</span>
            </div>
            <h3 className="font-display font-extrabold text-xl text-on-surface mb-2">
              Ready to Compare Colleges
            </h3>
            <p className="text-on-surface-variant text-sm max-w-md mx-auto mb-6">
              Search and select two colleges above, or choose a popular comparison below to view AI recommendations, NIRF rankings, fees, and placements side-by-side.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-2">
              <button
                type="button"
                className="bg-surface-container-lowest hover:bg-surface-container-high border border-outline-variant text-xs font-bold text-on-surface py-2 px-3.5 rounded-xl cursor-pointer transition-colors"
                onClick={() => {
                  setCollege1Input('COEP Technological University');
                  setCollege2Input('VJTI Mumbai');
                  runComparison('COEP Technological University', 'VJTI Mumbai');
                }}
              >
                ⚡ COEP vs VJTI
              </button>
              <button
                type="button"
                className="bg-surface-container-lowest hover:bg-surface-container-high border border-outline-variant text-xs font-bold text-on-surface py-2 px-3.5 rounded-xl cursor-pointer transition-colors"
                onClick={() => {
                  setCollege1Input('IIT Bombay');
                  setCollege2Input('IIT Delhi');
                  runComparison('IIT Bombay', 'IIT Delhi');
                }}
              >
                ⚡ IIT Bombay vs IIT Delhi
              </button>
              <button
                type="button"
                className="bg-surface-container-lowest hover:bg-surface-container-high border border-outline-variant text-xs font-bold text-on-surface py-2 px-3.5 rounded-xl cursor-pointer transition-colors"
                onClick={() => {
                  setCollege1Input('PICT Pune');
                  setCollege2Input('SPIT Mumbai');
                  runComparison('PICT Pune', 'SPIT Mumbai');
                }}
              >
                ⚡ PICT Pune vs SPIT Mumbai
              </button>
            </div>
          </section>
        )}
      </main>

      <Footer />
    </div>
  );
};

export default Compare;
