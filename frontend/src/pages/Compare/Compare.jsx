import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import MainLayout from '../../components/MainLayout/MainLayout';
import './Compare.css';
import { getCollegeById } from '../../services/api';

const Compare = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [collegeCards, setCollegeCards] = useState([null, null, null, null]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchColleges = async () => {
      setLoading(true);
      const idsParam = searchParams.get('ids');
      if (!idsParam) {
        setCollegeCards([null, null, null, null]);
        setLoading(false);
        return;
      }
      
      const ids = idsParam.split(',').slice(0, 4);
      try {
        const fetchedColleges = await Promise.all(
          ids.map(id => getCollegeById(id))
        );
        
        const newCards = [null, null, null, null];
        fetchedColleges.forEach((college, index) => {
          newCards[index] = college;
        });
        setCollegeCards(newCards);
      } catch (error) {
        console.error("Error fetching colleges:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchColleges();
  }, [searchParams]);

  const removeCollege = (index) => {
    const newCards = [...collegeCards];
    newCards[index] = null;
    
    // update URL
    const activeIds = newCards.filter(Boolean).map(c => c.id);
    if (activeIds.length > 0) {
      setSearchParams({ ids: activeIds.join(',') });
    } else {
      setSearchParams({});
    }
  };

  const handleAddCollege = () => {
    navigate('/colleges');
  };

  const handleAskAI = () => {
    navigate('/assistant');
  };

  // build comparisonRows dynamically
  const comparisonRows = [
    { metric: 'Ranking', icon: 'trophy', key: 'rank', format: val => `#${val} Global` },
    { metric: 'Rating', icon: 'star', key: 'rating', format: val => `${val} / 5.0` },
    { metric: 'Tuition Fees (Yr)', icon: 'payments', key: 'feeLabel', format: val => val },
    { metric: 'Acceptance Rate', icon: 'trending_up', key: 'acceptanceRate', format: val => val || 'N/A' },
  ].map(rowDef => {
    const row = { metric: rowDef.metric, icon: rowDef.icon };
    
    let bestIndex = -1;
    if (rowDef.key === 'rank') {
      const ranks = collegeCards.map(c => c ? c.rank : Infinity);
      const minRank = Math.min(...ranks);
      if (minRank !== Infinity) bestIndex = ranks.indexOf(minRank);
    } else if (rowDef.key === 'rating') {
      const ratings = collegeCards.map(c => c ? parseFloat(c.rating) : -1);
      const maxRating = Math.max(...ratings);
      if (maxRating !== -1) bestIndex = ratings.indexOf(maxRating);
    } else if (rowDef.key === 'feeLabel') {
      const fees = collegeCards.map(c => c ? c.feeValue : Infinity);
      const minFee = Math.min(...fees);
      if (minFee !== Infinity) bestIndex = fees.indexOf(minFee);
    } else if (rowDef.key === 'acceptanceRate') {
      const rates = collegeCards.map(c => c && c.acceptanceRate ? parseFloat(c.acceptanceRate.replace('%','')) : -1);
      const maxRate = Math.max(...rates);
      if (maxRate !== -1) bestIndex = rates.indexOf(maxRate);
    }

    collegeCards.forEach((card, i) => {
      row[`col${i}`] = card ? rowDef.format(card[rowDef.key]) : '-';
      if (i === bestIndex) row.highlight = `col${i}`;
    });
    return row;
  });

  // build placementCards dynamically
  const parseCurrency = (val) => val ? parseFloat(val.replace(/[^0-9.]/g, '')) : 0;
  
  const activeColleges = collegeCards.filter(Boolean);
  
  const avgPackages = activeColleges.map(c => parseCurrency(c.averagePackage));
  const maxAvgPackage = Math.max(...avgPackages, 1);
  const avgPackageBars = activeColleges.map((c, i) => ({
    label: c.name,
    value: (parseCurrency(c.averagePackage) / maxAvgPackage) * 100,
    color: i % 2 === 0 ? 'primary' : 'secondary',
    displayValue: c.averagePackage || 'N/A'
  }));

  const highPackages = activeColleges.map(c => parseCurrency(c.highestPackage));
  const maxHighPackage = Math.max(...highPackages, 1);
  const highPackageBars = activeColleges.map((c, i) => ({
    label: c.name,
    value: (parseCurrency(c.highestPackage) / maxHighPackage) * 100,
    color: i % 2 === 0 ? 'primary' : 'secondary',
    displayValue: c.highestPackage || 'N/A'
  }));

  const placementCards = [];
  if (activeColleges.length > 0) {
    placementCards.push({
      title: 'Average Package',
      value: activeColleges[0].averagePackage || 'N/A',
      comparison: activeColleges[1] ? activeColleges[1].averagePackage || 'N/A' : '-',
      bars: avgPackageBars,
    });
    placementCards.push({
      title: 'Highest Package',
      value: activeColleges[0].highestPackage || 'N/A',
      comparison: activeColleges[1] ? activeColleges[1].highestPackage || 'N/A' : '-',
      bars: highPackageBars,
    });
  }

  return (
    <MainLayout>
      <section className="compare-page">
        <div className="compare-hero">
          <div className="compare-copy">
            <div className="compare-eyebrow">Compare Colleges</div>
            <h1>Compare Colleges</h1>
            <p>
              Select up to 4 institutions to compare their academic rigor, placement records, and infrastructure side-by-side.
            </p>
          </div>
          <button className="compare-hero-action" type="button" onClick={handleAskAI}>
            <span className="material-symbols-outlined compare-action-icon">smart_toy</span>
            Ask AI Which College Is Better?
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>Loading comparison data...</div>
        ) : (
          <>
            <section className="compare-selection-card">
              <div className="selection-grid">
                {collegeCards.map((card, index) => (
                  <div key={index} className={card ? 'college-card selected-card' : 'college-card empty-card'}>
                    {card ? (
                      <>
                        <div className="college-card-meta">
                          <img src={card.image} alt={card.name} className="college-card-image" />
                          <div>
                            <p className="college-card-name">{card.name}</p>
                            <p className="college-card-location">{card.location}</p>
                          </div>
                        </div>
                        <button
                          type="button"
                          className="college-card-close"
                          aria-label={`Remove ${card.name}`}
                          onClick={() => removeCollege(index)}
                        >
                          <span className="material-symbols-outlined">close</span>
                        </button>
                      </>
                    ) : (
                      <button type="button" className="empty-card-button" onClick={handleAddCollege}>
                        <span className="material-symbols-outlined">add_circle</span>
                        <span>Add College</span>
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </section>

            <section className="compare-table-wrapper">
              <div className="compare-table">
                <div className="table-row table-header">
                  <div className="table-cell metric-cell" />
                  {collegeCards.map((card, index) => (
                    <div key={index} className={card ? 'table-cell college-header' : 'table-cell empty-header'}>
                      {card ? (
                        <>
                          <img src={card.image} alt={card.name} />
                          <span>{card.name}</span>
                        </>
                      ) : (
                        <>
                          <span className="material-symbols-outlined">domain_add</span>
                          <span>Empty</span>
                        </>
                      )}
                    </div>
                  ))}
                </div>
                {comparisonRows.map((row) => (
                  <div key={row.metric} className="table-row">
                    <div className="table-cell metric-cell">
                      <span className="material-symbols-outlined metric-icon">{row.icon}</span>
                      <span>{row.metric}</span>
                    </div>
                    {collegeCards.map((card, index) => (
                      <div key={index} className={`table-cell ${row.highlight === `col${index}` ? 'highlight-cell' : ''} ${!card ? 'empty-value' : ''}`}>
                        {row[`col${index}`]}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </section>

            {placementCards.length > 0 && (
              <section className="placement-section">
                <div className="placement-header">
                  <h2>Placement Packages Comparison</h2>
                </div>

                <div className="placement-grid">
                  {placementCards.map((card) => (
                    <article key={card.title} className="placement-card">
                      <div className="placement-card-header">
                        <p className="placement-card-label">{card.title}</p>
                        <div className="placement-card-values">
                          <span className="placement-value-primary">{card.value}</span>
                          {activeColleges.length > 1 && (
                            <span className="placement-value-secondary">vs {card.comparison}</span>
                          )}
                        </div>
                      </div>

                      <div className="placement-bars">
                        {card.bars.map((bar) => (
                          <div key={bar.label} className="placement-bar-row">
                            <span className="placement-bar-label">{bar.label}</span>
                            <div className="placement-bar-track">
                              <div className={`placement-bar ${bar.color}`} style={{ width: `${bar.value}%` }} />
                            </div>
                            <span className="placement-bar-value" style={{ marginLeft: '12px', fontSize: '12px', color: '#5a4136' }}>{bar.displayValue}</span>
                          </div>
                        ))}
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </section>
    </MainLayout>
  );
};

export default Compare;
