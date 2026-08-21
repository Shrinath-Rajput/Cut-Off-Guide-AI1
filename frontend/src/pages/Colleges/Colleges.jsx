import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import './Colleges.css';
import {
  getColleges,
  lookupCollegeAI,
  saveCollege,
  removeSavedCollege,
  getSavedColleges,
} from '../../services/api';
import { collegeImage, handleCollegeImageError } from '../../utils/collegeImage';
import toast from 'react-hot-toast';

const INDIAN_STATES = [
  'All India',
  'Maharashtra',
  'Delhi',
  'Karnataka',
  'Tamil Nadu',
  'Telangana',
  'Uttar Pradesh',
  'West Bengal',
  'Gujarat',
  'Rajasthan',
  'Kerala',
  'Andhra Pradesh',
  'Madhya Pradesh',
  'Punjab',
  'Haryana',
  'Odisha',
  'Bihar',
  'Assam',
  'Jharkhand',
  'Chhattisgarh',
  'Uttarakhand',
  'Goa',
  'Himachal Pradesh',
  'Chandigarh',
  'Jammu and Kashmir',
];

const formatCleanInsights = (rawText, collegeName = 'This institution') => {
  if (!rawText) return `${collegeName} is a recognized institution in India offering quality engineering and professional degree programs with dedicated faculty and career guidance.`;
  let cleaned = String(rawText)
    .replace(/Wikipedia\s*\[[^\]]*\]\s*:?/gi, '')
    .replace(/DuckDuckGo\s*[^:]*:/gi, '')
    .replace(/Web Snippet\s*:/gi, '')
    .replace(/\[[^\]]*\]/g, '')
    .replace(/\([^\)]*\)/g, '')
    .replace(/\s+/g, ' ')
    .replace(/\.\s*\./g, '.')
    .trim();

  const indicators = ["list of", "jurisdiction", "defence academy", "affiliated colleges", "vidyapeeth", "symbiosis", "krishi vigyan", "alumni who include"];
  const hasNoise = indicators.filter(ind => cleaned.toLowerCase().includes(ind)).length >= 2;

  if (hasNoise || cleaned.length < 25) {
    return `${collegeName} is a recognized educational institution offering undergraduate and postgraduate degree programs with modern academic infrastructure and student placement guidance.`;
  }
  return cleaned;
};

const Colleges = () => {
  const navigate = useNavigate();
  const searchInputRef = useRef(null);

  // Search & Filters
  const [search, setSearch] = useState('');
  const [selectedState, setSelectedState] = useState('Maharashtra');
  const [sortOption, setSortOption] = useState('Top Rated (Stars)');
  const [currentPage, setCurrentPage] = useState(1);
  const [collegeItems, setCollegeItems] = useState([]);
  const [totalCollegeCount, setTotalCollegeCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Saved / Bookmarks
  const [bookmarked, setBookmarked] = useState({});

  // AI & Web Search Modal / Live Lookup State
  const [aiLookupQuery, setAiLookupQuery] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null);
  const [showAiModal, setShowAiModal] = useState(false);

  // Load user bookmarks on mount
  useEffect(() => {
    const loadBookmarks = async () => {
      try {
        const saved = await getSavedColleges();
        if (Array.isArray(saved)) {
          const map = {};
          saved.forEach((c) => {
            const cid = c.collegeId || c.id || c._id;
            if (cid) map[cid] = true;
          });
          setBookmarked(map);
        }
      } catch (err) {
        // user offline or not logged in
      }
    };
    loadBookmarks();
  }, []);

  // Fetch catalog colleges with state filter & search
  useEffect(() => {
    const fetchColleges = async () => {
      setLoading(true);
      try {
        let sortParam = 'rating';
        if (sortOption === 'Lowest Cutoff' || sortOption === 'NIRF Ranking') {
          sortParam = 'ranking';
        } else if (sortOption === 'Highest Placement' || sortOption === 'Fees') {
          sortParam = 'fees';
        }

        const isAllIndia =
          selectedState === 'All India' ||
          selectedState === 'All Over India' ||
          selectedState === 'IN All India';

        const params = {
          page: currentPage,
          limit: 12,
          search: search.trim() || undefined,
          state: isAllIndia ? undefined : selectedState,
          states: isAllIndia ? undefined : [selectedState],
          sort: sortParam,
        };
        const data = await getColleges(params);
        setCollegeItems(data.data || []);
        setTotalCollegeCount(data.total || 0);
        setTotalPages(data.total_pages || 1);
      } catch (error) {
        console.error('Failed to fetch colleges:', error);
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(fetchColleges, 250);
    return () => clearTimeout(timeoutId);
  }, [search, selectedState, sortOption, currentPage]);

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [search, selectedState, sortOption]);

  const toggleBookmark = async (college) => {
    const cid = college.id || college._id;
    const isBookmarked = !!bookmarked[cid];
    setBookmarked((prev) => ({ ...prev, [cid]: !isBookmarked }));

    try {
      if (isBookmarked) {
        await removeSavedCollege(cid);
        toast.success('Removed from saved colleges');
      } else {
        await saveCollege({
          collegeId: cid,
          name: college.name,
          location: college.location || `${college.city || ''}, ${college.state || ''}`,
          rating: college.rating || 4.5,
          image: college.image,
        });
        toast.success('Saved to your colleges list');
      }
    } catch (err) {
      toast.error(isBookmarked ? 'Failed to remove' : 'Please login to save colleges');
    }
  };

  // Trigger Live AI + Web Search
  const handleAiLookup = async (customQuery) => {
    const q = (customQuery || search || aiLookupQuery).trim();
    if (!q) {
      toast.error('Please enter a college name to search with AI');
      return;
    }

    setAiLookupQuery(q);
    setAiLoading(true);
    setShowAiModal(true);
    setAiResult(null);

    try {
      const res = await lookupCollegeAI(q);
      if (res?.status === 'success' && res?.data) {
        setAiResult(res.data);
      } else {
        throw new Error('AI could not find details for this college');
      }
    } catch (error) {
      console.error('AI College lookup error:', error);
      toast.error('Unable to fetch live AI insights. Please try again.');
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className="bg-surface text-on-surface font-body-md min-h-screen flex flex-col">
      <Navbar />

      {/* Main Content */}
      <main className="flex-grow pt-32 pb-24 px-margin-mobile md:px-margin-desktop max-w-[1280px] mx-auto w-full flex flex-col gap-stack-lg">
        {/* Hero Section */}
        <section className="flex flex-col items-center text-center gap-stack-md max-w-3xl mx-auto mb-8">
          <h1 className="font-headline-lg-mobile md:font-display text-headline-lg-mobile md:text-display text-on-surface font-extrabold tracking-tight">
            Find Your Dream College in India
          </h1>

          <div className="w-full mt-stack-md relative">
            <div className="flex items-center bg-surface-container-lowest border border-outline-variant rounded-full px-6 py-4 shadow-sm focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20 transition-all w-full relative">
              <span className="material-symbols-outlined text-outline mr-3">search</span>
              <input
                ref={searchInputRef}
                className="bg-transparent border-none outline-none flex-grow font-body-md text-on-surface placeholder:text-outline-variant focus:ring-0 w-full"
                placeholder="Search for colleges..."
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleAiLookup(search);
                }}
              />
              {search && (
                <button
                  type="button"
                  className="text-outline hover:text-on-surface transition-colors mx-2 cursor-pointer"
                  onClick={() => setSearch('')}
                  title="Clear search"
                >
                  <span className="material-symbols-outlined text-lg">close</span>
                </button>
              )}
              <button
                type="button"
                className="bg-primary-container text-white px-6 py-2.5 rounded-full font-label-md text-label-md flex items-center gap-2 hover:bg-primary transition-colors shadow-md ml-2 absolute right-2 top-2 bottom-2 my-auto h-auto cursor-pointer"
                onClick={() => handleAiLookup(search)}
              >
                <span className="material-symbols-outlined text-sm">magic_button</span> AI Search
              </button>
            </div>
          </div>
        </section>

        {/* Filters & Sorting */}
        <section className="border-y border-outline-variant py-4 flex flex-col gap-stack-md">
          {/* Region/State Dropdown & Pills */}
          <div className="flex flex-col md:flex-row items-start md:items-center gap-4 w-full">
            <div className="flex items-center gap-3 w-full md:w-auto shrink-0">
              <span className="material-symbols-outlined text-outline">location_on</span>
              <div className="flex flex-col">
                <span className="font-label-sm text-label-sm text-outline">Select Region /</span>
                <span className="font-label-sm text-label-sm text-outline">State:</span>
              </div>
              <select
                value={selectedState}
                onChange={(e) => setSelectedState(e.target.value)}
                className="ml-2 bg-surface-container-lowest border border-outline-variant text-on-surface font-body-md rounded-xl px-4 py-2 focus:ring-primary focus:border-primary min-w-[200px] shadow-sm cursor-pointer appearance-none shadow-md"
              >
                {INDIAN_STATES.map((st) => (
                  <option key={st} value={st}>
                    {st === 'All India' ? 'All India (All States)' : st}
                  </option>
                ))}
              </select>
            </div>

            {/* Horizontal scrolling pills */}
            <div className="flex-grow overflow-x-auto pb-2 md:pb-0 hide-scrollbar flex items-center gap-2">
              {['All India', 'Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Telangana', 'Uttar Pradesh'].map(
                (st) => {
                  const isActive =
                    selectedState === st ||
                    (st === 'All India' &&
                      (selectedState === 'All Over India' || selectedState === 'IN All India'));
                  return (
                    <button
                      key={st}
                      type="button"
                      onClick={() => setSelectedState(st)}
                      className={`shrink-0 px-4 py-1.5 rounded-full font-label-sm text-label-sm transition-colors whitespace-nowrap cursor-pointer ${
                        isActive
                          ? 'bg-surface-tint text-white shadow-sm'
                          : 'border border-outline-variant text-on-surface-variant hover:bg-surface-variant bg-surface-container-lowest'
                      }`}
                    >
                      {st === 'All India' ? 'IN All India' : st}
                    </button>
                  );
                }
              )}
            </div>
          </div>

          {/* Sort Row */}
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-outline">sort</span>
            <span className="font-label-md text-label-md text-on-surface-variant">Sort:</span>
            <select
              value={sortOption}
              onChange={(e) => setSortOption(e.target.value)}
              className="bg-surface-container-lowest border border-outline-variant text-on-surface font-body-md rounded-xl px-4 py-1.5 focus:ring-primary focus:border-primary shadow-sm cursor-pointer appearance-none text-sm shadow-md"
            >
              <option value="Top Rated (Stars)">Top Rated (Stars)</option>
              <option value="Lowest Cutoff">Lowest Cutoff</option>
              <option value="Highest Placement">Highest Placement</option>
            </select>
          </div>
        </section>

        {/* Content Area */}
        <section className="flex flex-col gap-stack-lg">
          {/* Status Text */}
          <div className="font-headline-md text-headline-md text-on-surface">
            Showing <span className="text-primary-container font-bold">{totalCollegeCount}</span> Colleges{' '}
            {selectedState !== 'All India' && selectedState !== 'All Over India' && selectedState !== 'IN All India'
              ? `in ${selectedState}`
              : 'Across All India'}
          </div>

          {/* Loading / Cards Grid / Empty State */}
          {loading ? (
            <div className="flex flex-col items-center justify-center py-16 text-center gap-4">
              <div className="spinner-large" />
              <p className="font-body-md text-on-surface-variant">Fetching colleges...</p>
            </div>
          ) : collegeItems.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center gap-4">
              <div className="relative w-24 h-24 mb-4 opacity-50 flex items-center justify-center">
                <span className="material-symbols-outlined text-[80px] text-outline absolute inset-0 m-auto">search_off</span>
              </div>
              <h2 className="font-headline-md text-headline-md text-on-surface">
                No colleges found in catalog for "{search || selectedState}"
              </h2>
              <p className="font-body-md text-body-md text-on-surface-variant mb-6">
                Try searching with our AI &amp; Web Search model for live information on any college!
              </p>
              <button
                type="button"
                className="bg-primary-container hover:bg-primary text-white font-label-md text-label-md px-8 py-4 rounded-xl flex items-center gap-2 transition-colors shadow-lg hover:-translate-y-1 active:translate-y-0 transform cursor-pointer"
                onClick={() => handleAiLookup(search || selectedState)}
              >
                <span className="material-symbols-outlined">magic_button</span> Search "{search || selectedState}" with Live AI
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {collegeItems.map((college) => {
                const cid = college.id || college._id;
                const isSaved = !!bookmarked[cid];
                const locationText = college.location || `${college.city || ''}, ${college.state || ''}`;

                return (
                  <div
                    key={cid}
                    className="bg-surface-container-lowest border border-outline-variant rounded-2xl overflow-hidden flex flex-col shadow-sm hover:shadow-md transition-all duration-200 hover:-translate-y-1"
                  >
                    {/* Image Banner */}
                    <div className="relative h-44 w-full overflow-hidden bg-surface-container">
                      <img
                        src={collegeImage(college.image, 'banner', college.name)}
                        alt={college.name}
                        className="w-full h-full object-cover"
                        onError={handleCollegeImageError}
                      />
                      <button
                        type="button"
                        className={`absolute top-3 right-3 w-9 h-9 rounded-full bg-white/90 backdrop-blur-sm border-none flex items-center justify-center text-outline hover:text-primary transition-colors cursor-pointer shadow-sm ${
                          isSaved ? 'text-primary' : ''
                        }`}
                        onClick={() => toggleBookmark(college)}
                        title={isSaved ? 'Remove from Saved' : 'Save College'}
                      >
                        <span className="material-symbols-outlined text-[20px]">
                          {isSaved ? 'bookmark_added' : 'bookmark_border'}
                        </span>
                      </button>

                      {college.type && (
                        <span className="absolute bottom-3 left-3 bg-inverse-surface/85 backdrop-blur-sm text-white font-label-sm text-[12px] px-2.5 py-1 rounded-md">
                          {college.type}
                        </span>
                      )}
                    </div>

                    {/* Body */}
                    <div className="p-5 flex flex-col flex-grow">
                      {/* Meta badges */}
                      <div className="flex items-center gap-2 mb-2 flex-wrap">
                        <div className="inline-flex items-center gap-1 bg-[#fff9e6] border border-[#ffe082] rounded-md px-2 py-0.5 text-[12px] font-bold text-[#b78103]">
                          <span className="material-symbols-outlined text-[14px] text-amber-500 fill">star</span>
                          <span>{college.rating || 4.5}</span>
                          <span className="text-[10px] text-[#8c7247]">/5</span>
                        </div>
                        {college.nirf_rank && (
                          <div className="bg-[#e8f5e9] border border-[#c8e6c9] rounded-md px-2 py-0.5 text-[12px] font-bold text-[#2e7d32]">
                            NIRF #{college.nirf_rank}
                          </div>
                        )}
                        {college.state && (
                          <div className="bg-surface-container-low rounded-md px-2 py-0.5 text-[12px] font-medium text-on-surface-variant">
                            {college.state}
                          </div>
                        )}
                      </div>

                      {/* Name & Location */}
                      <h3 className="font-headline-md text-[17px] font-bold text-on-surface mb-1 line-clamp-2 leading-snug">
                        {college.name}
                      </h3>
                      <p className="font-body-md text-[13px] text-on-surface-variant flex items-center gap-1 mb-3">
                        <span className="material-symbols-outlined text-[15px]">location_on</span>
                        {locationText}
                      </p>

                      {/* Highlights */}
                      {college.highlights && (
                        <p className="font-body-md text-[13px] text-on-surface-variant line-clamp-2 mb-4 leading-relaxed">
                          {college.highlights}
                        </p>
                      )}

                      {/* Stats */}
                      <div className="mt-auto pt-3 border-t border-outline-variant/40 flex flex-wrap gap-4 text-[12px]">
                        {college.placement_avg && (
                          <div>
                            <span className="text-outline">Avg CTC: </span>
                            <span className="text-green-700 font-bold">{college.placement_avg}</span>
                          </div>
                        )}
                        {college.fee_display && (
                          <div>
                            <span className="text-outline">Fees: </span>
                            <span className="text-on-surface font-semibold">{college.fee_display}</span>
                          </div>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2 mt-4">
                        <Link
                          to={`/colleges/${cid}`}
                          className="flex-grow bg-surface-container-low hover:bg-primary hover:text-white border border-outline-variant text-on-surface font-label-md text-[13px] py-2 px-3 rounded-xl flex items-center justify-center gap-1 transition-colors font-semibold text-center"
                        >
                          View Details
                          <span className="material-symbols-outlined text-[15px]">arrow_forward</span>
                        </Link>
                        <button
                          type="button"
                          className="bg-primary-fixed hover:bg-primary-container text-on-primary-fixed border border-primary-fixed font-label-md text-[13px] py-2 px-3 rounded-xl flex items-center gap-1 transition-colors font-semibold cursor-pointer shrink-0"
                          onClick={() => handleAiLookup(college.name)}
                          title="Ask AI Council about this college"
                        >
                          <span className="material-symbols-outlined text-[16px]">psychology</span>
                          AI Info
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button
                type="button"
                className="bg-surface-container-lowest border border-outline-variant rounded-xl px-4 py-2 text-sm font-semibold text-on-surface flex items-center gap-1 disabled:opacity-40 cursor-pointer"
                disabled={currentPage <= 1}
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              >
                <span className="material-symbols-outlined text-sm">chevron_left</span>
                Prev
              </button>
              <div className="flex gap-1.5">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                  <button
                    key={p}
                    type="button"
                    className={`w-9 h-9 rounded-xl border text-sm font-semibold flex items-center justify-center cursor-pointer transition-colors ${
                      currentPage === p
                        ? 'bg-surface-tint text-white border-surface-tint shadow-sm'
                        : 'bg-surface-container-lowest border-outline-variant text-on-surface hover:border-primary'
                    }`}
                    onClick={() => setCurrentPage(p)}
                  >
                    {p}
                  </button>
                ))}
              </div>
              <button
                type="button"
                className="bg-surface-container-lowest border border-outline-variant rounded-xl px-4 py-2 text-sm font-semibold text-on-surface flex items-center gap-1 disabled:opacity-40 cursor-pointer"
                disabled={currentPage >= totalPages}
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              >
                Next
                <span className="material-symbols-outlined text-sm">chevron_right</span>
              </button>
            </div>
          )}
        </section>

        {/* ============================================================
            AI & WEB SEARCH MODAL
            ============================================================ */}
        {showAiModal && (
          <div
            className="fixed inset-0 bg-inverse-surface/60 backdrop-blur-sm flex items-center justify-center p-4 z-50"
            onClick={() => setShowAiModal(false)}
          >
            <div
              className="bg-surface-container-lowest rounded-3xl max-w-2xl w-full max-h-[85vh] overflow-y-auto shadow-2xl border border-outline-variant"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6 border-b border-outline-variant flex items-center justify-between bg-surface-container-low rounded-t-3xl">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-surface-tint text-white flex items-center justify-center shadow-sm">
                    <span className="material-symbols-outlined text-[22px]">auto_awesome</span>
                  </div>
                  <div>
                    <h3 className="font-headline-md text-headline-md text-on-surface">Live AI &amp; Web Search Results</h3>
                    <p className="font-body-md text-xs text-on-surface-variant">
                      Powered by Llama-3.1 &amp; DuckDuckGo Search
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  className="text-outline hover:text-on-surface p-1.5 rounded-lg cursor-pointer transition-colors"
                  onClick={() => setShowAiModal(false)}
                >
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>

              <div className="p-6">
                {aiLoading ? (
                  <div className="text-center py-12 flex flex-col items-center">
                    <div className="spinner-large mb-4" />
                    <h4 className="font-headline-md text-lg font-bold text-on-surface mb-1">
                      Searching web &amp; synthesizing insights for "{aiLookupQuery}"...
                    </h4>
                    <p className="font-body-md text-sm text-on-surface-variant">
                      Fetching location, NIRF rankings, cutoffs, and placements
                    </p>
                  </div>
                ) : aiResult ? (
                  <div className="flex flex-col gap-5">
                    <div>
                      <h2 className="font-headline-lg-mobile text-2xl font-extrabold text-on-surface mb-2">
                        {aiResult.name}
                      </h2>
                      <div className="flex flex-wrap gap-2">
                        {aiResult.rating && (
                          <span className="bg-[#fff9e6] border border-[#ffe082] text-[#b78103] px-3 py-1 rounded-full text-xs font-bold">
                            ⭐ {aiResult.rating} / 5
                          </span>
                        )}
                        {aiResult.nirf_rank && (
                          <span className="bg-[#e8f5e9] border border-[#c8e6c9] text-[#2e7d32] px-3 py-1 rounded-full text-xs font-bold">
                            NIRF #{aiResult.nirf_rank}
                          </span>
                        )}
                        {aiResult.type && (
                          <span className="bg-surface-container-low border border-outline-variant text-on-surface-variant px-3 py-1 rounded-full text-xs font-medium">
                            {aiResult.type}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div className="bg-surface-container-low border border-outline-variant rounded-xl p-3.5 flex items-start gap-3">
                        <span className="material-symbols-outlined text-surface-tint text-[20px] mt-0.5">
                          location_on
                        </span>
                        <div>
                          <label className="block text-[11px] font-bold text-outline uppercase tracking-wider">
                            Location &amp; State
                          </label>
                          <p className="text-sm font-semibold text-on-surface">
                            {aiResult.location || `${aiResult.city || ''}, ${aiResult.state || 'India'}`}
                          </p>
                        </div>
                      </div>

                      <div className="bg-surface-container-low border border-outline-variant rounded-xl p-3.5 flex items-start gap-3">
                        <span className="material-symbols-outlined text-surface-tint text-[20px] mt-0.5">
                          payments
                        </span>
                        <div>
                          <label className="block text-[11px] font-bold text-outline uppercase tracking-wider">
                            Estimated Fees
                          </label>
                          <p className="text-sm font-semibold text-on-surface">
                            {aiResult.fee_display || '₹1.0 - ₹2.5 Lakh / year'}
                          </p>
                        </div>
                      </div>

                      <div className="bg-surface-container-low border border-outline-variant rounded-xl p-3.5 flex items-start gap-3">
                        <span className="material-symbols-outlined text-surface-tint text-[20px] mt-0.5">
                          trending_up
                        </span>
                        <div>
                          <label className="block text-[11px] font-bold text-outline uppercase tracking-wider">
                            Average Package
                          </label>
                          <p className="text-sm font-semibold text-green-700">
                            {aiResult.placement_avg || '₹8.5 - ₹14.0 LPA'}
                          </p>
                        </div>
                      </div>

                      <div className="bg-surface-container-low border border-outline-variant rounded-xl p-3.5 flex items-start gap-3">
                        <span className="material-symbols-outlined text-surface-tint text-[20px] mt-0.5">
                          verified
                        </span>
                        <div>
                          <label className="block text-[11px] font-bold text-outline uppercase tracking-wider">
                            Accepted Exams
                          </label>
                          <p className="text-sm font-semibold text-on-surface">
                            {Array.isArray(aiResult.exams) ? aiResult.exams.join(', ') : 'JEE Main / State CET'}
                          </p>
                        </div>
                      </div>
                    </div>

                    {aiResult.highlights && (
                      <div className="bg-surface-container-low border border-outline-variant rounded-2xl p-4">
                        <h4 className="text-xs font-bold text-surface-tint flex items-center gap-1.5 mb-1.5 uppercase tracking-wider">
                          <span className="material-symbols-outlined text-sm">lightbulb</span>
                          AI Key Insights
                        </h4>
                        <p className="text-sm text-on-surface-variant leading-relaxed">
                          {formatCleanInsights(aiResult.highlights, aiResult.name)}
                        </p>
                      </div>
                    )}

                    {aiResult.courses && aiResult.courses.length > 0 && (
                      <div className="bg-surface-container-low border border-outline-variant rounded-2xl p-4">
                        <h4 className="text-xs font-bold text-surface-tint flex items-center gap-1.5 mb-2 uppercase tracking-wider">
                          <span className="material-symbols-outlined text-sm">menu_book</span>
                          Top Courses &amp; Branches
                        </h4>
                        <div className="flex flex-wrap gap-1.5">
                          {aiResult.courses.map((course, idx) => (
                            <span
                              key={idx}
                              className="bg-surface-container-lowest border border-outline-variant text-on-surface text-xs font-semibold px-2.5 py-1 rounded-md"
                            >
                              {course}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="mt-2">
                      <button
                        type="button"
                        className="w-full bg-surface-tint hover:bg-primary text-white font-label-md py-3.5 px-6 rounded-2xl flex items-center justify-center gap-2 transition-colors shadow-md font-bold cursor-pointer"
                        onClick={() => navigate('/assistant')}
                      >
                        <span className="material-symbols-outlined">chat</span>
                        Ask AI Council More About This College
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-on-surface-variant text-sm">
                      No results found. Please check the college name and try again.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
};

export default Colleges;
