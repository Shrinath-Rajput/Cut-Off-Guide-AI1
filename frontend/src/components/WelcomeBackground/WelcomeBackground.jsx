import { useEffect, useState } from 'react';
import campusImage from '../../assets/images/ChatGPT Image Aug 19, 2026, 02_36_18 PM.png';
import managementImage from '../../assets/images/ChatGPT Image Aug 19, 2026, 02_37_38 PM.png';
import medicalImage from '../../assets/images/ChatGPT Image Aug 19, 2026, 02_38_19 PM.png';
import './WelcomeBackground.css';

const bgImages = [
  {
    alt: 'IIT Delhi',
    src: campusImage,
  },
  {
    alt: 'IIM Bangalore',
    src: managementImage,
  },
  {
    alt: 'Medical colleges',
    src: medicalImage,
  },
];

const WelcomeBackground = () => {
  const [bgIndex, setBgIndex] = useState(1);

  useEffect(() => {
    const interval = setInterval(() => {
      setBgIndex((prev) => (prev + 1) % bgImages.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="welcome-bg-slider" aria-hidden="true">
      {bgImages.map((img, idx) => (
        <img
          key={img.alt}
          alt={img.alt}
          className={`welcome-bg-image ${idx === bgIndex ? 'welcome-bg-image-active' : ''}`}
          src={img.src}
        />
      ))}
      <div className="welcome-bg-overlay" />
    </div>
  );
};

export default WelcomeBackground;
