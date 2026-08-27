import { useState } from 'react';
import MainLayout from '../../components/MainLayout/MainLayout';
import SectionHeader from '../../components/SectionHeader/SectionHeader';
import Button from '../../components/Button/Button';
import { EXAM_CONFIG, validateAcademicScore } from '../../utils/validation';
import './Cutoff.css';

// Local prediction fetcher
const predictCutoffs = async (data) => {
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
  const response = await fetch(`${API_URL}/prediction`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Prediction request failed');
  }
  return response.json();
};

const Cutoff = () => {
  const [form, setForm] = useState({ exam: '', score: '', category: '', gender: '', university: '', course: '', location: '', round: '', target_year: 2027 });
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleChange = (event) => {
    const { name, value } = event.target;
    
    if (name === 'exam') {
      setForm((prev) => ({ ...prev, exam: value, score: '', course: '' }));
      setError(null);
    } else {
      setForm((prev) => ({ ...prev, [name]: name === 'target_year' ? parseInt(value, 10) : value }));
      if (name === 'score') {
        setError(null);
      }
    }
  };

  const handleScoreBlur = () => {
    if (form.exam && form.score) {
      const validationError = validateAcademicScore(form.exam, form.score);
      setError(validationError);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (error) return;
    
    try {
      // Use college name as university for prediction req
      const req = {
          college: form.university || "VJTI",
          course: form.course || "Computer Engineering",
          category: form.category,
          gender: form.gender,
          target_year: form.target_year
      };
      const data = await predictCutoffs(req);
      setResult(data);
    } catch (error) {
      console.error('Failed to search cutoffs:', error);
    }
  };

  const selectedExamConfig = EXAM_CONFIG[form.exam];

  return (
    <MainLayout>
      <SectionHeader title="Predict your cutoff" description="Enter your profile details and receive a focused admission prediction report." />

      <div className="cutoff-layout">
        <form className="cutoff-form" onSubmit={handleSubmit}>
          <div className="cutoff-grid">
            <label>
              Select Exam
              <select name="exam" value={form.exam} onChange={handleChange}>
                <option value="" disabled>Select an exam</option>
                {Object.keys(EXAM_CONFIG).map((examOption) => (
                  <option key={examOption} value={examOption}>{examOption}</option>
                ))}
              </select>
            </label>
            
            <label>
              {selectedExamConfig ? selectedExamConfig.label : 'Score / Percentile'}
              <input 
                name="score" 
                value={form.score} 
                onChange={handleChange} 
                onBlur={handleScoreBlur}
                placeholder={selectedExamConfig ? `e.g. ${selectedExamConfig.type === 'percentile' ? '95.5' : '150'}` : 'Select an exam first'} 
                disabled={!form.exam}
                className={error ? 'input-error' : ''}
              />
              {error && <span className="field-error">{error}</span>}
            </label>

            <label>
              Category
              <select name="category" value={form.category} onChange={handleChange}>
                <option value="">Select category</option>
                <option>Open</option>
                <option>OBC</option>
                <option>SC</option>
                <option>ST</option>
              </select>
            </label>
            <label>
              Gender
              <select name="gender" value={form.gender} onChange={handleChange}>
                <option value="">Select gender</option>
                <option>Male</option>
                <option>Female</option>
                <option>Other</option>
              </select>
            </label>
            <label>
              College / University Search
              <input name="university" value={form.university} onChange={handleChange} placeholder="e.g., VJTI Mumbai" />
            </label>
            <label>
              Preferred course
              <select 
                name="course" 
                value={form.course} 
                onChange={handleChange}
                disabled={!form.exam}
              >
                <option value="" disabled>{form.exam ? 'Select a course' : 'Select an exam first'}</option>
                {selectedExamConfig?.courses?.map((courseOption) => (
                  <option key={courseOption} value={courseOption}>{courseOption}</option>
                ))}
              </select>
            </label>
            <label>
              Target Year
              <select name="target_year" value={form.target_year} onChange={handleChange}>
                <option value={2026}>2026</option>
                <option value={2027}>2027</option>
                <option value={2028}>2028</option>
              </select>
            </label>
          </div>
          <Button variant="primary" type="submit" disabled={!!error || !form.exam || !form.score}>Predict</Button>
        </form>

        <div className="cutoff-result">
          {result ? (
            <div className="result-card">
              {result.message ? (
                 <div className="result-empty">{result.message}</div>
              ) : (
                 <>
                   <h2>{result.target_year} Predicted Cutoff</h2>
                   <div className="result-grid">
                     <div>
                       <strong>{result.predicted_cutoff}</strong>
                       <span>Expected/Predicted Value</span>
                     </div>
                     <div>
                       <strong>{result.lower_bound} - {result.upper_bound}</strong>
                       <span>Prediction Range</span>
                     </div>
                     <div>
                       <strong>{result.confidence}</strong>
                       <span>Confidence</span>
                     </div>
                     <div>
                       <strong>{result.latest_actual_year}</strong>
                       <span>Latest Actual Data</span>
                     </div>
                     <div>
                       <strong>{result.data_status.replace(/_/g, " ")}</strong>
                       <span>Data Status</span>
                     </div>
                   </div>
                 </>
              )}
            </div>
          ) : (
            <div className="result-empty">Enter your details to view a tailored prediction.</div>
          )}
        </div>
      </div>
    </MainLayout>
  );
};

export default Cutoff;
