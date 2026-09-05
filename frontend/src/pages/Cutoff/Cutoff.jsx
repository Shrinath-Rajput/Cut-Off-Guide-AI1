import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  Award,
  TrendingUp,
  MapPin,
  CheckCircle2,
  AlertCircle,
  Bookmark,
  BookmarkCheck,
  Scale,
  DollarSign,
  Briefcase,
  Layers,
  ArrowRight,
  ShieldCheck,
  Target,
  Zap,
  ChevronDown,
  Info,
  Building2,
  AlertTriangle,
} from 'lucide-react';
import MainLayout from '../../components/MainLayout/MainLayout';
import SectionHeader from '../../components/SectionHeader/SectionHeader';
import Button from '../../components/Button/Button';
import { EXAM_CONFIG, validateAcademicScore } from '../../utils/validation';
import { predictPercentileML, predictCollegesLLM, saveCollege } from '../../services/api';
import cutoffHeroBg from '../../assets/images/cutoff-hero-bg.png';
import './Cutoff.css';

const CATEGORIES = [
  'Open/General',
  'OBC',
  'SC',
  'ST',
  'EWS',
  'TFWS (Tuition Fee Waiver)',
  'NT-A',
  'NT-B',
  'NT-C',
  'NT-D',
  'SBC',
  'Defence / Ex-Servicemen',
  'PWD (Persons with Disability)',
  'Minority',
];

const LOCATIONS = [
  'Pune',
  'Mumbai',
  'Nagpur',
  'Nashik',
  'Chhatrapati Sambhajinagar',
  'Kolhapur',
  'All Maharashtra',
  'All India',
];

const PREFERRED_BRANCHES = [
  'Computer Engineering (CSE)',
  'Information Technology (IT)',
  'Artificial Intelligence & Machine Learning',
  'Artificial Intelligence & Data Science',
  'Cyber Security',
  'Data Science',
  'Electronics & Telecommunication',
  'Electronics & Communication',
  'Electrical Engineering',
  'Mechanical Engineering',
  'Civil Engineering',
  'Chemical Engineering',
  'Robotics & Automation',
  'Mechatronics',
  'Biotechnology',
  'Aerospace Engineering',
  'Automobile Engineering',
  'Others',
];

const POPULAR_COURSES = PREFERRED_BRANCHES;

const PRESET_SCORES = {
  'MHT-CET': [85, 115, 145, 168, 185],
  'JEE Main': [100, 140, 180, 220, 260],
  'JEE Advanced': [80, 120, 165, 210, 275],
};

const Cutoff = () => {
  const navigate = useNavigate();
  const step2Ref = useRef(null);
  const resultsRef = useRef(null);

  // Phase 1 States
  const [selectedExam, setSelectedExam] = useState('MHT-CET');
  const [marks, setMarks] = useState('');
  const [marksError, setMarksError] = useState(null);
  const [isPredictingML, setIsPredictingML] = useState(false);
  const [percentileResult, setPercentileResult] = useState(null);

  // Phase 2 States
  const [category, setCategory] = useState('Open/General');
  const [location, setLocation] = useState('Pune');
  const [capRound, setCapRound] = useState('Round 1');
  const [selectedCourses, setSelectedCourses] = useState([
    'Computer Engineering (CSE)',
    'Information Technology (IT)',
  ]);
  const [manualPercentile, setManualPercentile] = useState('');

  // Phase 3 States
  const [isPredictingLLM, setIsPredictingLLM] = useState(false);
  const [collegeResponse, setCollegeResponse] = useState(null);
  const [filterTab, setFilterTab] = useState('all');
  const [branchFilter, setBranchFilter] = useState('all');
  const [isFetchingBranch, setIsFetchingBranch] = useState(null);
  const [savedIds, setSavedIds] = useState(new Set());

  const examConfig = EXAM_CONFIG[selectedExam] || EXAM_CONFIG['MHT-CET'];

  // Handle Exam Selection Change
  const handleExamChange = (newExam) => {
    setSelectedExam(newExam);
    setMarks('');
    setMarksError(null);
    setPercentileResult(null);
    setManualPercentile('');
    setCollegeResponse(null);
    setBranchFilter('all');
  };

  // Handle Marks Input with Clamping & Validation
  const handleMarksChange = (e) => {
    const rawVal = e.target.value;
    if (rawVal === '') {
      setMarks('');
      setMarksError(null);
      return;
    }

    const numVal = parseFloat(rawVal);
    if (isNaN(numVal)) {
      setMarks(rawVal);
      setMarksError('Marks must be a valid number.');
      return;
    }

    if (numVal > examConfig.max) {
      setMarks(String(examConfig.max));
      setMarksError(`Clamped to maximum marks of ${examConfig.max} for ${selectedExam}.`);
      toast.error(`Maximum marks for ${selectedExam} is ${examConfig.max}!`);
      return;
    }

    if (numVal < 0) {
      setMarks('0');
      setMarksError('Marks cannot be negative.');
      return;
    }

    setMarks(rawVal);
    setMarksError(null);
  };

  // Predict Percentile via ML API
  const handlePredictPercentile = async (e) => {
    if (e) e.preventDefault();
    const valErr = validateAcademicScore(selectedExam, marks);
    if (valErr) {
      setMarksError(valErr);
      toast.error(valErr);
      return;
    }

    setIsPredictingML(true);
    setMarksError(null);

    try {
      const data = await predictPercentileML({
        exam: selectedExam,
        marks: parseFloat(marks),
      });

      setPercentileResult(data);
      setManualPercentile(String(data.predicted_percentile));
      if (data.predicted_percentile < 30) {
        toast('Percentile is below 30% — too low for government cutoffs. Search for private colleges.', {
          icon: '⚠️',
          duration: 6000,
        });
      } else {
        toast.success(`Predicted: ${data.predicted_percentile}%ile (${data.estimated_rank})`);
      }

      // Smooth scroll to Step 2
      setTimeout(() => {
        if (step2Ref.current) {
          step2Ref.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 300);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to predict percentile. Please try again.';
      setMarksError(msg);
      toast.error(msg);
    } finally {
      setIsPredictingML(false);
    }
  };

  // Toggle Course in preferences
  const handleToggleCourse = (course) => {
    setSelectedCourses((prev) => {
      if (prev.includes(course)) {
        if (prev.length === 1) {
          toast.error('Select at least one course preference.');
          return prev;
        }
        return prev.filter((c) => c !== course);
      } else {
        return [...prev, course];
      }
    });
  };

  // Predict Eligible Colleges via LLM API
  const handlePredictColleges = async () => {
    const effectivePct = parseFloat(manualPercentile || percentileResult?.predicted_percentile);
    if (isNaN(effectivePct) || effectivePct <= 0 || effectivePct > 100) {
      toast.error('Please predict or enter a valid percentile (0 - 100).');
      return;
    }

    setIsPredictingLLM(true);

    try {
      const payload = {
        exam: selectedExam,
        marks: parseFloat(marks) || null,
        percentile: effectivePct,
        category: category,
        location: location,
        round: capRound,
        preferred_courses: selectedCourses,
      };

      const response = await predictCollegesLLM(payload);
      setCollegeResponse(response);
      setBranchFilter('all');
      if (effectivePct < 30) {
        toast('Notice: Percentile is below 30%. Showing private college guidance & management quota options.', {
          icon: '⚠️',
          duration: 6000,
        });
      } else {
        toast.success(`Found ${response.colleges?.length || 0} tailored college matches!`);
      }

      // Smooth scroll to Results
      setTimeout(() => {
        if (resultsRef.current) {
          resultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 300);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to retrieve college recommendations.';
      toast.error(msg);
    } finally {
      setIsPredictingLLM(false);
    }
  };

  // Branch matching helper for precise & alias-aware filtering
  const isBranchMatch = (collegeBranch, targetBranch) => {
    if (!collegeBranch || !targetBranch) return false;
    if (targetBranch === 'all') return true;

    const cb = collegeBranch.toLowerCase().trim();
    const tb = targetBranch.toLowerCase().trim();

    if (cb === tb) return true;
    if (cb.includes(tb) || tb.includes(cb)) return true;

    if (tb.includes('cse') || tb.includes('computer')) {
      return cb.includes('cse') || cb.includes('computer') || cb.includes('software');
    }
    if (tb.includes('it') || tb.includes('information technology')) {
      return cb.includes('information technology') || /\bit\b/.test(cb);
    }
    if (tb.includes('machine learning') || tb.includes('ai & ml') || tb.includes('aiml')) {
      return cb.includes('machine learning') || cb.includes('ai & ml') || cb.includes('aiml');
    }
    if (tb.includes('data science') || tb.includes('ai & ds')) {
      return cb.includes('data science') || cb.includes('ds');
    }
    if (tb.includes('cyber')) return cb.includes('cyber');
    if (tb.includes('telecommunication') || tb.includes('e&tc') || tb.includes('entc')) {
      return cb.includes('telecommunication') || cb.includes('e&tc') || cb.includes('entc');
    }
    if (tb.includes('communication') || tb.includes('ece')) {
      return cb.includes('communication') || cb.includes('ece');
    }
    if (tb.includes('electrical')) return cb.includes('electrical');
    if (tb.includes('mechanical')) return cb.includes('mechanical');
    if (tb.includes('civil')) return cb.includes('civil');
    if (tb.includes('chemical')) return cb.includes('chemical');
    if (tb.includes('robotics')) return cb.includes('robotics');
    if (tb.includes('mechatronics')) return cb.includes('mechatronics');
    if (tb.includes('biotechnology') || tb.includes('biotech')) return cb.includes('biotech');
    if (tb.includes('aerospace')) return cb.includes('aerospace') || cb.includes('aeronautic');
    if (tb.includes('automobile')) return cb.includes('automobile') || cb.includes('automotive');
    if (tb === 'others') return cb.includes('other') || cb.includes('instrumentation') || cb.includes('production');

    return false;
  };

  // Handle clicking a branch pill on the Result Page
  const handleResultBranchClick = async (branch) => {
    if (isFetchingBranch) return;

    if (branchFilter === branch) {
      setBranchFilter('all');
      return;
    }

    const matchingColleges = rawColleges.filter((c) => isBranchMatch(c.branch, branch));
    if (matchingColleges.length > 0) {
      setBranchFilter(branch);
      toast.success(`Showing ${matchingColleges.length} colleges for ${branch}`);
      return;
    }

    // Branch not yet in current result list: fetch recommendations tailored for this branch
    const effectivePct = parseFloat(manualPercentile || percentileResult?.predicted_percentile);
    if (isNaN(effectivePct) || effectivePct <= 0 || effectivePct > 100) {
      setBranchFilter(branch);
      return;
    }

    setIsFetchingBranch(branch);
    const toastId = toast.loading(`Loading recommendations for ${branch}...`);

    try {
      const payload = {
        exam: selectedExam,
        marks: parseFloat(marks) || null,
        percentile: effectivePct,
        category: category,
        location: location,
        round: capRound,
        preferred_courses: [branch],
      };

      const response = await predictCollegesLLM(payload);
      const newColleges = response.colleges || [];

      if (newColleges.length > 0) {
        setCollegeResponse((prev) => {
          const prevColleges = prev?.colleges || [];
          const existingKeys = new Set(prevColleges.map((c) => `${c.college_id}_${c.branch}`));
          const uniqueNew = newColleges.filter((c) => !existingKeys.has(`${c.college_id}_${c.branch}`));

          return {
            ...prev,
            colleges: [...prevColleges, ...uniqueNew],
            summary: {
              ...(prev?.summary || response.summary),
              total_recommendations: prevColleges.length + uniqueNew.length,
            },
          };
        });
        setBranchFilter(branch);
        toast.success(`Loaded ${newColleges.length} colleges for ${branch}!`, { id: toastId });
      } else {
        setBranchFilter(branch);
        toast('No specific colleges found for this branch in selected criteria.', { id: toastId });
      }
    } catch (err) {
      toast.error(`Could not load colleges for ${branch}.`, { id: toastId });
    } finally {
      setIsFetchingBranch(null);
    }
  };

  // Handle Save to Wishlist
  const handleSaveCollege = async (item) => {
    const cid = item.college_id;
    try {
      await saveCollege({
        id: cid,
        name: item.college_name,
        location: item.location,
        rating: 4.5,
      });
      setSavedIds((prev) => new Set([...prev, cid]));
      toast.success(`Saved ${item.college_name} to wishlist!`);
    } catch (err) {
      toast.error('Could not save college.');
    }
  };

  // Filter recommendations by both Branch and Chance Tier
  const rawColleges = collegeResponse?.colleges || [];
  const branchFilteredColleges =
    branchFilter === 'all'
      ? rawColleges
      : rawColleges.filter((c) => isBranchMatch(c.branch, branchFilter));

  const filteredColleges =
    filterTab === 'all'
      ? branchFilteredColleges
      : branchFilteredColleges.filter((c) => c.chance_tier === filterTab);

  const safeCount = branchFilteredColleges.filter((c) => c.chance_tier === 'Safe').length;
  const targetCount = branchFilteredColleges.filter((c) => c.chance_tier === 'Target').length;
  const ambitiousCount = branchFilteredColleges.filter((c) => c.chance_tier === 'Ambitious').length;

  return (
    <MainLayout>
      <div className="cutoff-page-container">
        {/* Hero Header Banner with Illustration Background & Overlapping Text */}
        <section className="cutoff-hero-banner">
          <div className="cutoff-hero-bg-wrapper">
            <img
              src={cutoffHeroBg}
              alt="Percentile & College Predictor"
              className="cutoff-hero-bg-img"
            />
            <div className="cutoff-hero-overlay" />
            <div className="cutoff-hero-glow" />
          </div>

          <div className="cutoff-hero-content">
            <h1 className="cutoff-hero-title">Percentile &amp; College Predictor</h1>

            {/* Stepper Pill Indicator Overlapping on Hero */}
            <div className="cutoff-steps-indicator">
              <div className={`step-item ${marks ? 'completed' : 'active'}`}>
                <span className="step-num">1</span>
                <span>Percentile Predictor</span>
              </div>
              <div className="step-connector" />
              <div className={`step-item ${percentileResult ? (collegeResponse ? 'completed' : 'active') : ''}`}>
                <span className="step-num">2</span>
                <span>Candidate Criteria</span>
              </div>
              <div className="step-connector" />
              <div className={`step-item ${collegeResponse ? 'active' : ''}`}>
                <span className="step-num">3</span>
                <span>Eligible College Results</span>
              </div>
            </div>
          </div>
        </section>

        {/* ========================================================================= */}
        {/* PHASE 1: ML PERCENTILE PREDICTION */}
        {/* ========================================================================= */}
        <div className="phase-card phase-1-card">
          <div className="phase-header">
            <div className="phase-icon-badge">
              <Zap size={22} />
            </div>
            <div>
              <h2>Step 1: Percentile Prediction</h2>
              <p>Select your entrance exam and input your raw marks bounded by exam limits.</p>
            </div>
          </div>

          {/* Exam Selector Cards */}
          <div className="exam-cards-grid">
            {['MHT-CET', 'JEE Main', 'JEE Advanced'].map((examKey) => {
              const cfg = EXAM_CONFIG[examKey];
              const isSelected = selectedExam === examKey;
              return (
                <div
                  key={examKey}
                  className={`exam-card-button ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleExamChange(examKey)}
                  role="button"
                  tabIndex={0}
                >
                  <div className="exam-card-top">
                    <span className="exam-name">{examKey}</span>
                    <span className="max-marks-pill">Max {cfg.max}</span>
                  </div>
                  <span className="exam-desc">{cfg.description}</span>
                </div>
              );
            })}
          </div>

          {/* Marks Input Form */}
          <form className="marks-form" onSubmit={handlePredictPercentile}>
            <div className="marks-input-wrapper">
              <label htmlFor="marks-input">
                Enter Expected Marks in {selectedExam}
                <span className="max-indicator"> (Allowed: 0 to {examConfig.max})</span>
              </label>

              <div className="input-with-action">
                <input
                  id="marks-input"
                  type="number"
                  step="any"
                  min="0"
                  max={examConfig.max}
                  value={marks}
                  onChange={handleMarksChange}
                  placeholder={`e.g. ${Math.round(examConfig.max * 0.75)}`}
                  className={marksError ? 'has-error' : ''}
                />
                <Button
                  variant="primary"
                  type="submit"
                  disabled={isPredictingML || !marks}
                  className="predict-percentile-btn"
                >
                  {isPredictingML ? (
                    <>
                      <span className="spinner-dots" /> Calculating Percentile...
                    </>
                  ) : (
                    <>
                      <TrendingUp size={18} /> Predict Percentile
                    </>
                  )}
                </Button>
              </div>

              {marksError && <div className="error-banner">{marksError}</div>}

              {/* Quick Preset Marks Chips */}
              <div className="preset-chips">
                <span className="preset-label">Quick test marks:</span>
                {PRESET_SCORES[selectedExam]?.map((scoreVal) => (
                  <button
                    key={scoreVal}
                    type="button"
                    className="preset-chip"
                    onClick={() => {
                      setMarks(String(scoreVal));
                      setMarksError(null);
                    }}
                  >
                    {scoreVal} / {examConfig.max}
                  </button>
                ))}
              </div>
            </div>
          </form>

          {/* Percentile Result Showcase */}
          {percentileResult && (
            <div className="percentile-result-card animate-fade-in">
              <div className="result-main-grid">
                <div className="percentile-display-col">
                  <span className="res-label">Predicted Percentile</span>
                  <div className="percentile-hero-number">
                    {percentileResult.predicted_percentile}
                    <span className="pct-symbol">%ile</span>
                  </div>
                  <span className="confidence-pill">
                    Confidence Range: {percentileResult.percentile_range}
                  </span>
                </div>

                <div className="result-stats-col">
                  <div className="stat-box">
                    <Award className="stat-icon" size={24} />
                    <div>
                      <span className="stat-title">Estimated Rank</span>
                      <strong className="stat-value">{percentileResult.estimated_rank}</strong>
                    </div>
                  </div>

                  <div className="stat-box">
                    <TrendingUp className="stat-icon" size={24} />
                    <div>
                      <span className="stat-title">Performance Tier</span>
                      <strong className="stat-value">{percentileResult.performance_tier}</strong>
                    </div>
                  </div>
                </div>
              </div>

              {/* Low Percentile Advisory Banner */}
              {(percentileResult.predicted_percentile < 30 || percentileResult.advisory_message) && (
                <div className="low-percentile-advisory-card">
                  <div className="advisory-card-header">
                    <div className="advisory-badge-pill">
                      <AlertTriangle size={15} />
                      <span>Advisory: Score Below 30%ile</span>
                    </div>
                    <span className="advisory-subtext">Too low percentile to apply for government seats</span>
                  </div>
                  <h4 className="advisory-card-title">
                    Too Low Percentile to Apply — Search for Private Colleges
                  </h4>
                  <p className="advisory-card-message">
                    {percentileResult.advisory_message ||
                      'Your predicted score is below 30 percentile, which is too low to apply for merit-based seats in government or top autonomous colleges through CAP rounds. Please search for private colleges, deemed universities, and institute-level / management quota seats to apply.'}
                  </p>
                  <div className="advisory-card-actions">
                    <button
                      type="button"
                      className="advisory-search-private-btn"
                      onClick={() => navigate('/colleges?search=private')}
                    >
                      <Building2 size={16} /> Search Private Colleges
                    </button>
                    <button
                      type="button"
                      className="advisory-proceed-btn"
                      onClick={() => {
                        step2Ref.current?.scrollIntoView({ behavior: 'smooth' });
                      }}
                    >
                      Configure College Criteria <ArrowRight size={15} />
                    </button>
                  </div>
                </div>
              )}

              <div className="percentile-result-footer">
                <div className="info-tag">
                  <CheckCircle2 size={16} color="#16a34a" />
                  <span>
                    Calibrated on historical {selectedExam} normalization curves. Monotonically bound.
                  </span>
                </div>
                <button
                  type="button"
                  className="jump-step2-btn"
                  onClick={() => {
                    step2Ref.current?.scrollIntoView({ behavior: 'smooth' });
                  }}
                >
                  Configure College Criteria <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* ========================================================================= */}
        {/* PHASE 2: CANDIDATE PROFILE & CRITERIA */}
        {/* ========================================================================= */}
        <div className="phase-card phase-2-card" ref={step2Ref}>
          <div className="phase-header">
            <div className="phase-icon-badge secondary">
              <Layers size={22} />
            </div>
            <div>
              <h2>Step 2: Candidate Profile & Preferences</h2>
              <p>Customize your category quota, target location, round, and preferred engineering branches.</p>
            </div>
          </div>

          <div className="criteria-grid">
            {/* Percentile Field */}
            <div className="criteria-field">
              <label>
                Percentile
                <span className="field-hint"> (Auto-filled or override)</span>
              </label>
              <input
                type="number"
                step="any"
                min="0"
                max="100"
                value={manualPercentile}
                onChange={(e) => setManualPercentile(e.target.value)}
                placeholder="e.g. 98.50"
              />
            </div>

            {/* Category Field */}
            <div className="criteria-field">
              <label>Candidate Category / Quota</label>
              <select value={category} onChange={(e) => setCategory(e.target.value)}>
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>

            {/* Preferred Location */}
            <div className="criteria-field">
              <label>Preferred Location</label>
              <select value={location} onChange={(e) => setLocation(e.target.value)}>
                {LOCATIONS.map((loc) => (
                  <option key={loc} value={loc}>
                    {loc}
                  </option>
                ))}
              </select>
            </div>

            {/* CAP Round */}
            <div className="criteria-field">
              <label>CAP Admission Round</label>
              <select value={capRound} onChange={(e) => setCapRound(e.target.value)}>
                <option value="Round 1">Round 1 (Initial Benchmarks)</option>
                <option value="Round 2">Round 2 (Betterment / Shift)</option>
                <option value="Round 3">Round 3 (Mop-up / Final State)</option>
              </select>
            </div>
          </div>

          {/* Real-time Notice if entered percentile is < 30 */}
          {parseFloat(manualPercentile) > 0 && parseFloat(manualPercentile) < 30 && (
            <div className="criteria-low-percentile-alert">
              <div className="criteria-alert-header">
                <AlertTriangle size={18} className="criteria-alert-icon" />
                <span className="criteria-alert-badge">Score Below 30%ile Notice</span>
              </div>
              <div className="criteria-alert-body">
                <h5 className="criteria-alert-title">
                  Too low percentile to apply for government cutoffs ({parseFloat(manualPercentile)}%ile)
                </h5>
                <p className="criteria-alert-desc">
                  Scores below 30 percentile do not meet regular CAP merit cutoffs for government institutions.
                  Please search for private colleges, deemed universities, or explore direct institute-level / management quota seats to apply.
                </p>
              </div>
              <button
                type="button"
                className="btn-criteria-search-private"
                onClick={() => navigate('/colleges?search=private')}
              >
                <Building2 size={15} /> Search Private Colleges
              </button>
            </div>
          )}

          {/* Preferred Branches Multi-Select */}
          <div className="courses-selector-section">
            <label className="courses-label">
              Preferred Branches:
              <span className="field-hint"> (Select one or more preferred branches)</span>
            </label>
            <div className="course-chips-grid">
              {PREFERRED_BRANCHES.map((course) => {
                const isChecked = selectedCourses.includes(course);
                return (
                  <button
                    key={course}
                    type="button"
                    className={`course-chip ${isChecked ? 'active' : ''}`}
                    onClick={() => handleToggleCourse(course)}
                  >
                    {isChecked ? <CheckCircle2 size={16} /> : <span className="chip-plus">+</span>}
                    <span>{course}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Predict Colleges CTA */}
          <div className="predict-colleges-cta-row">
            <Button
              variant="primary"
              className="predict-colleges-btn"
              onClick={handlePredictColleges}
              disabled={isPredictingLLM || (!manualPercentile && !percentileResult)}
            >
              {isPredictingLLM ? (
                <>
                  <span className="spinner-dots" /> Consulting LLM Admissions Engine...
                </>
              ) : (
                <>
                  <Building2 size={20} /> Predict Eligible Colleges
                </>
              )}
            </Button>
            <span className="cta-note">
              Analyzes college closing trends, category relaxations, and round shift dynamics.
            </span>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* PHASE 3: INTERACTIVE COLLEGE RECOMMENDATIONS */}
        {/* ========================================================================= */}
        {collegeResponse && (
          <div className="phase-card phase-3-card animate-fade-in" ref={resultsRef}>
            <div className="phase-header">
              <div className="phase-icon-badge success">
                <Target size={22} />
              </div>
              <div>
                <h2>Step 3: College Recommendations</h2>
                <p>
                  Curated institutional options categorized into Safe, Target, and Ambitious tiers for{' '}
                  <strong>{collegeResponse.summary?.candidate_percentile}%ile</strong> under{' '}
                  <strong>{collegeResponse.summary?.category}</strong> in{' '}
                  <strong>{collegeResponse.summary?.round}</strong>.
                </p>
              </div>
            </div>

            {/* Low Percentile Advisory Banner */}
            {(collegeResponse.summary?.candidate_percentile < 30 || collegeResponse.summary?.is_low_percentile) && (
              <div className="results-low-percentile-banner">
                <div className="banner-left-content">
                  <div className="banner-badge-row">
                    <AlertTriangle size={18} className="banner-alert-icon" />
                    <span className="banner-badge-text">Advisory Notice</span>
                  </div>
                  <h3 className="banner-title">
                    Too Low Percentile to Apply for Government CAP Merit Cutoffs ({collegeResponse.summary?.candidate_percentile}%ile)
                  </h3>
                  <p className="banner-desc">
                    {collegeResponse.summary?.advisory_message ||
                      'Your percentile is below 30%, which is too low to apply for merit-based seats in government or top autonomous engineering colleges through regular CAP rounds. Please search for private colleges, deemed universities, and management quota seats.'}
                  </p>
                </div>
                <button
                  type="button"
                  className="banner-search-private-btn"
                  onClick={() => navigate('/colleges?search=private')}
                >
                  <Building2 size={18} /> Search Private Colleges
                </button>
              </div>
            )}

            {/* Strategic Summary Banner */}
            <div className="strategy-summary-banner">
              <div className="summary-stats-bar">
                <div className="summary-stat-pill all">
                  <span>Total Matches</span>
                  <strong>{collegeResponse.summary?.total_recommendations || rawColleges.length}</strong>
                </div>
                <div className="summary-stat-pill safe">
                  <span>Safe (High Chance)</span>
                  <strong>{safeCount}</strong>
                </div>
                <div className="summary-stat-pill target">
                  <span>Target (Competitive)</span>
                  <strong>{targetCount}</strong>
                </div>
                <div className="summary-stat-pill ambitious">
                  <span>Ambitious (Dream)</span>
                  <strong>{ambitiousCount}</strong>
                </div>
              </div>

              {collegeResponse.summary?.counselor_advice && (
                <div className="counselor-advice-box">
                  <Info size={20} className="advice-icon" />
                  <p>{collegeResponse.summary.counselor_advice}</p>
                </div>
              )}
            </div>

            {/* Preferred Branches Filter Section on Cutoff Result Page */}
            <div className="result-preferred-branches-section">
              <div className="result-branches-head-row">
                <div className="result-branches-title-group">
                  <div className="result-branches-icon-badge">
                    <Layers size={18} />
                  </div>
                  <div>
                    <h4 className="result-branches-title">Preferred Branches</h4>
                    <p className="result-branches-subtitle">
                      Filter college matches or switch engineering disciplines to view cutoffs
                    </p>
                  </div>
                </div>

                {branchFilter !== 'all' && (
                  <button
                    type="button"
                    className="btn-clear-branch-filter"
                    onClick={() => setBranchFilter('all')}
                  >
                    View All Branches ({rawColleges.length})
                  </button>
                )}
              </div>

              <div className="result-branches-chips-grid">
                <button
                  type="button"
                  className={`result-branch-pill ${branchFilter === 'all' ? 'active' : ''}`}
                  onClick={() => setBranchFilter('all')}
                >
                  <span className="pill-title">All Branches</span>
                  <span className="pill-badge pill-badge-total">{rawColleges.length}</span>
                </button>

                {PREFERRED_BRANCHES.map((branch) => {
                  const isSelected = branchFilter === branch;
                  const count = rawColleges.filter((c) => isBranchMatch(c.branch, branch)).length;
                  const isLoadingThis = isFetchingBranch === branch;

                  return (
                    <button
                      key={branch}
                      type="button"
                      className={`result-branch-pill ${isSelected ? 'active' : ''} ${
                        count > 0 ? 'has-matches' : 'no-matches'
                      }`}
                      onClick={() => handleResultBranchClick(branch)}
                      disabled={isFetchingBranch !== null && isFetchingBranch !== branch}
                      title={
                        count > 0
                          ? `Show ${count} colleges for ${branch}`
                          : `Load recommendations for ${branch}`
                      }
                    >
                      {isSelected && <CheckCircle2 size={13} className="pill-active-icon" />}
                      <span className="pill-title">{branch}</span>
                      {isLoadingThis ? (
                        <span className="pill-loading-indicator">...</span>
                      ) : count > 0 ? (
                        <span className="pill-badge">{count}</span>
                      ) : (
                        <span className="pill-fetch-label">+ Fetch</span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Filter Tabs */}
            <div className="filter-tabs-row">
              <button
                type="button"
                className={`tab-btn ${filterTab === 'all' ? 'active' : ''}`}
                onClick={() => setFilterTab('all')}
              >
                All Colleges ({branchFilteredColleges.length})
              </button>
              <button
                type="button"
                className={`tab-btn tab-safe ${filterTab === 'Safe' ? 'active' : ''}`}
                onClick={() => setFilterTab('Safe')}
              >
                <ShieldCheck size={16} /> Safe / High Chance ({safeCount})
              </button>
              <button
                type="button"
                className={`tab-btn tab-target ${filterTab === 'Target' ? 'active' : ''}`}
                onClick={() => setFilterTab('Target')}
              >
                <Target size={16} /> Target / Competitive ({targetCount})
              </button>
              <button
                type="button"
                className={`tab-btn tab-ambitious ${filterTab === 'Ambitious' ? 'active' : ''}`}
                onClick={() => setFilterTab('Ambitious')}
              >
                <Award size={16} /> Ambitious / Dream ({ambitiousCount})
              </button>
            </div>

            {/* Recommendations Grid */}
            {filteredColleges.length === 0 ? (
              <div className="empty-results-private-guidance">
                <Building2 size={48} className="empty-guidance-icon" />
                {branchFilter !== 'all' || filterTab !== 'all' ? (
                  <>
                    <h3>No Matches for Selected Filters</h3>
                    <p>
                      No colleges currently match {branchFilter !== 'all' ? <strong>{branchFilter}</strong> : 'all branches'} in the {filterTab !== 'all' ? <strong>{filterTab} tier</strong> : 'selected tier'}.
                      You can reset branch or tier filters below to view all options.
                    </p>
                    <div className="empty-guidance-actions">
                      {branchFilter !== 'all' && (
                        <button
                          type="button"
                          className="btn-search-private-primary"
                          onClick={() => setBranchFilter('all')}
                        >
                          Show All Branches
                        </button>
                      )}
                      {filterTab !== 'all' && (
                        <button
                          type="button"
                          className="btn-reset-filters"
                          onClick={() => setFilterTab('all')}
                        >
                          Show All Tiers
                        </button>
                      )}
                      {(collegeResponse.summary?.candidate_percentile < 30 || collegeResponse.summary?.is_low_percentile) && (
                        <button
                          type="button"
                          className="btn-search-private-primary"
                          onClick={() => navigate('/colleges?search=private')}
                        >
                          <Building2 size={18} /> Search Private Colleges
                        </button>
                      )}
                    </div>
                  </>
                ) : (
                  <>
                    <h3>No Regular Government Cutoffs for Below 30%ile</h3>
                    <p>
                      Merit cutoffs for state and national government institutions close significantly higher.
                      Since your score is too low to apply for open merit CAP rounds, we strongly recommend exploring
                      private colleges, deemed universities, and direct institute-level / management quota seats.
                    </p>
                    <div className="empty-guidance-actions">
                      <button
                        type="button"
                        className="btn-search-private-primary"
                        onClick={() => navigate('/colleges?search=private')}
                      >
                        <Building2 size={18} /> Search Private Colleges Now
                      </button>
                      <button
                        type="button"
                        className="btn-reset-filters"
                        onClick={() => {
                          setFilterTab('all');
                          setBranchFilter('all');
                        }}
                      >
                        View All College Options
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="colleges-results-grid">
                {filteredColleges.map((item, idx) => {
                const isSaved = savedIds.has(item.college_id);
                const candidatePct = collegeResponse.summary?.candidate_percentile || 0;
                const cutoffDelta = (candidatePct - item.cutoff_percentile).toFixed(2);
                const isPositive = candidatePct >= item.cutoff_percentile;

                return (
                  <div key={`${item.college_id}_${item.branch}_${idx}`} className="college-result-card">
                    {/* Card Top Header */}
                    <div className="card-top-row">
                      <div className="college-title-block">
                        <span className="college-city-tag">
                          <MapPin size={12} /> {item.city} • {item.round}
                        </span>
                        <h3 className="college-name">{item.college_name}</h3>
                        <span className="college-branch-pill">{item.branch}</span>
                      </div>

                      <div className={`tier-badge tier-${item.chance_tier.toLowerCase()}`}>
                        {item.chance_tier === 'Safe' && <ShieldCheck size={16} />}
                        {item.chance_tier === 'Target' && <Target size={16} />}
                        {item.chance_tier === 'Ambitious' && <Award size={16} />}
                        <span>{item.chance_tier}</span>
                      </div>
                    </div>

                    {/* Cutoff vs Percentile Visual Comparison Bar */}
                    <div className="cutoff-comparison-section">
                      <div className="comparison-metric-row">
                        <div>
                          <span className="metric-label">Projected Cutoff ({item.category})</span>
                          <strong className="metric-value">{item.cutoff_percentile}%ile</strong>
                        </div>
                        <div className="chance-score-box">
                          <span className="metric-label">Admission Chance</span>
                          <strong className="chance-num">{item.chance_percentage}%</strong>
                        </div>
                      </div>

                      <div className="progress-bar-track">
                        <div
                          className={`progress-bar-fill fill-${item.chance_tier.toLowerCase()}`}
                          style={{ width: `${Math.min(100, item.chance_percentage)}%` }}
                        />
                      </div>

                      <div className="delta-caption">
                        {isPositive ? (
                          <span className="delta-positive">
                            +{cutoffDelta}%ile above closing cutoff
                          </span>
                        ) : (
                          <span className="delta-reach">
                            {cutoffDelta}%ile gap from closing cutoff
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Key Stats: Placements & Fees */}
                    <div className="card-metrics-grid">
                      <div className="metric-cell">
                        <Briefcase size={16} className="metric-cell-icon" />
                        <div>
                          <span className="cell-label">Average CTC</span>
                          <strong className="cell-val">{item.placement_avg}</strong>
                        </div>
                      </div>

                      <div className="metric-cell">
                        <TrendingUp size={16} className="metric-cell-icon" />
                        <div>
                          <span className="cell-label">Highest CTC</span>
                          <strong className="cell-val">{item.highest_package}</strong>
                        </div>
                      </div>

                      <div className="metric-cell">
                        <DollarSign size={16} className="metric-cell-icon" />
                        <div>
                          <span className="cell-label">Annual Fees</span>
                          <strong className="cell-val">{item.fee_display}</strong>
                        </div>
                      </div>
                    </div>

                    {/* AI Reasoning Box */}
                    <div className="ai-reasoning-card">
                      <div className="ai-reasoning-head">
                        <Info size={14} color="#ea580c" />
                        <span>Admissions Counselor Insight</span>
                      </div>
                      <p className="ai-reasoning-text">{item.ai_reasoning}</p>
                    </div>

                    {/* Action Buttons */}
                    <div className="card-actions-row">
                      <button
                        type="button"
                        className={`action-btn-save ${isSaved ? 'saved' : ''}`}
                        onClick={() => handleSaveCollege(item)}
                      >
                        {isSaved ? (
                          <>
                            <BookmarkCheck size={16} color="#16a34a" /> Wishlisted
                          </>
                        ) : (
                          <>
                            <Bookmark size={16} /> Save to Wishlist
                          </>
                        )}
                      </button>

                      <button
                        type="button"
                        className="action-btn-compare"
                        onClick={() => navigate(`/compare?college1=${encodeURIComponent(item.college_id)}`)}
                      >
                        <Scale size={16} /> Compare
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
      </div>
    </MainLayout>
  );
};

export default Cutoff;
