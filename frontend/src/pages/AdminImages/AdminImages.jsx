import { useEffect, useState } from 'react';
import { getAdminColleges, uploadCollegeImage } from '../../services/api';
import { collegeImage, handleCollegeImageError } from '../../utils/collegeImage';
import './AdminImages.css';

const AdminImages = () => {
  const [colleges, setColleges] = useState([]);
  const [status, setStatus] = useState({});

  useEffect(() => {
    getAdminColleges().then((data) => setColleges(data.data || [])).catch(() => {});
  }, []);

  const handleUpload = async (collegeId, file) => {
    if (!file) return;
    setStatus((current) => ({ ...current, [collegeId]: 'Uploading...' }));
    try {
      const result = await uploadCollegeImage(collegeId, file);
      setColleges((current) => current.map((college) => (
        college.id === collegeId ? { ...college, image: result.image } : college
      )));
      setStatus((current) => ({ ...current, [collegeId]: 'Uploaded' }));
    } catch (error) {
      setStatus((current) => ({ ...current, [collegeId]: error.response?.data?.detail || 'Upload failed' }));
    }
  };

  return (
    <main className="admin-images-page">
      <header className="admin-images-header">
        <p className="admin-images-eyebrow">ADMINISTRATION</p>
        <h1>College images</h1>
        <p>Upload a current campus image for each college. Images are stored by the configured storage provider and rendered across the app.</p>
      </header>
      <section className="admin-images-grid">
        {colleges.map((college) => (
          <article className="admin-image-card" key={college.id}>
            <img src={collegeImage(college.image)} alt={college.name} onError={handleCollegeImageError} />
            <div className="admin-image-card-copy">
              <h2>{college.name}</h2>
              <p>{college.location}</p>
              <label className="admin-upload-button">
                <span className="material-symbols-outlined">upload</span>
                Choose image
                <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={(event) => handleUpload(college.id, event.target.files?.[0])} />
              </label>
              <small>{status[college.id] || 'JPG, PNG, WEBP or GIF up to 10 MB'}</small>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
};

export default AdminImages;