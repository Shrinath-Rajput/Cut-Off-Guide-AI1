import { useState } from 'react';
import { searchCutoffs } from '../../services/api';
import MainLayout from '../../components/MainLayout/MainLayout';
import SectionHeader from '../../components/SectionHeader/SectionHeader';
import Button from '../../components/Button/Button';
import { EXAM_CONFIG, validateAcademicScore } from '../../utils/validation';
import './Cutoff.css';

const Cutoff = () => {
  const [form, setForm] = useState({ exam: '', score: '', category: '', gender: '', university: '', course: '', location: '', round: '' });
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleChange = (event) => {
    const { name, value } = event.target;

    if (name === 'exam') {
      setForm((prev) => ({ ...prev, exam: value, score: '', course: '' }));
      setError(null);
      setResult(null);
    } else {
      setForm((prev) => ({ ...prev, [name]: value }));
      setResult(null);
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
    const validationError = validateAcademicScore(form.exam, form.score);
    if (validationError) {
      setError(validationError);
      return;
    }

    const requiredFields = ['exam', 'score', 'category', 'gender', 'university', 'course', 'location', 'round'];
    const missingRequiredField = requiredFields.find((field) => !String(form[field] ?? '').trim());
    if (missingRequiredField) {
      setError('Please complete all cutoff fields before predicting.');
      return;
    }

    try {
      setError(null);
      const data = await searchCutoffs(form);
      setResult(data);
    } catch (requestError) {
      console.error('Failed to search cutoffs:', requestError);
      setError(requestError?.response?.data?.detail || 'Unable to predict cutoff. Please try again.');
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
                <option>Open/General</option>
                <option>OBC</option>
                <option>SC</option>
                <option>ST</option>
                <option>EWS</option>
                <option>PWD (Persons with Disability)</option>
                <option>Defence/Ex-Servicemen</option>
                <option>Minority</option>
                <option>Kashmiri Migrant</option>
                <option>NT-B</option>
                <option>NT-C</option>
                <option>NT-D</option>
                <option>SBC</option>
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
              Home University
              <input name="university" value={form.university} onChange={handleChange} placeholder="e.g., Mumbai University" />
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
              Preferred location
              <input name="location" value={form.location} onChange={handleChange} placeholder="e.g., Pune" />
            </label>
            <label>
              CAP round
              <select name="round" value={form.round} onChange={handleChange}>
                <option value="">Select round</option>
                <option>Round 1</option>
                <option>Round 2</option>
              </select>
            </label>
          </div>
          <Button
            variant="primary"
            type="submit"
            disabled={
              !!error ||
              !form.exam ||
              !form.score ||
              !form.category ||
              !form.gender ||
              !form.university ||
              !form.course ||
              !form.location ||
              !form.round
            }
          >
            Predict
          </Button>
        </form>

        <div className="cutoff-result">
          {result ? (
            <div className="result-card">
              <h2>Prediction result</h2>
              <div className="result-grid">
                <div>
                  <strong>{result.cutoff}</strong>
                  <span>Predicted cutoff</span>
                </div>
                <div>
                  <strong>{result.rank}</strong>
                  <span>Expected rank</span>
                </div>
                <div>
                  <strong>{result.suggestion}</strong>
                  <span>Best college suggestions</span>
                </div>
              </div>
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
