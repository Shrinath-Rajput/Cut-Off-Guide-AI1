import { useState } from 'react';
import { searchCutoffs } from '../../services/api';
import MainLayout from '../../components/MainLayout/MainLayout';
import SectionHeader from '../../components/SectionHeader/SectionHeader';
import Button from '../../components/Button/Button';
import './Cutoff.css';

const Cutoff = () => {
  const [form, setForm] = useState({ percentile: '', category: '', gender: '', university: '', course: '', location: '', round: '' });
  const [result, setResult] = useState(null);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const data = await searchCutoffs(form);
      setResult(data);
    } catch (error) {
      console.error('Failed to search cutoffs:', error);
    }
  };

  return (
    <MainLayout>
      <SectionHeader title="Predict your cutoff" description="Enter your profile details and receive a focused admission prediction report." />

      <div className="cutoff-layout">
        <form className="cutoff-form" onSubmit={handleSubmit}>
          <div className="cutoff-grid">
            <label>
              MHT-CET percentile
              <input name="percentile" value={form.percentile} onChange={handleChange} placeholder="95.5" />
            </label>
            <label>
              Category
              <select name="category" value={form.category} onChange={handleChange}>
                <option value="">Select category</option>
                <option>Open</option>
                <option>OBC</option>
                <option>SC/ST</option>
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
              <input name="university" value={form.university} onChange={handleChange} placeholder="Mumbai University" />
            </label>
            <label>
              Preferred course
              <input name="course" value={form.course} onChange={handleChange} placeholder="Computer Engineering" />
            </label>
            <label>
              Preferred location
              <input name="location" value={form.location} onChange={handleChange} placeholder="Pune" />
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
          <Button variant="primary" type="submit">Predict</Button>
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
