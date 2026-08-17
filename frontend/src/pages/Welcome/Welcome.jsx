import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Welcome.css';

const bgImages = [
  {
    alt: 'IIT Delhi',
    src: 'https://lh3.googleusercontent.com/aida/AP1WRLt_SfeGuNAGsex-1IUq9gDMIyzNF5yrMlV2tLe2Kkj8vqptBqHwmiFZsHLn2X8I48NlnnyS67P_F2X8RHdGin_OA_2z2udNnglHvAonRF3O4pPktH7N1A5MpFo2EqbuNLQQ4MQDwBOKx4J28HBHQRd2NGLozu-5H-uK4Y7PYAK6vyiW9FDy1hvC5Ip7RN2nyq7tZbQ9ydFc0dEL2yyEZtxcCqHQG6An6e9ngMZ9LCN3DiQ5q7Gl8MtYbVs',
  },
  {
    alt: 'IIT Bombay',
    src: 'https://lh3.googleusercontent.com/aida/AP1WRLthpBNX06PKmB9Hr7048okr6IY6sqM53bQYhCk6lb862nUHM8yw_nLd6xyX0RWMXR8tVp-nFUGFHaocwE-aYR984A9Ol493J3-0b_-9qMf_MdGLa2M_kRFvvQeis5mFppXKhe4vNzbObY2SlhBFqnmvFeDOZ-fSoipgguRH6sp6DilGz993DbXiMHHM5M0HvfaozGpSrt4NnrSvMQIgduIDuxfyDRQpxYXH5Gl5t1ryPvHCWRlXOqWPiFnc',
  },
  {
    alt: 'IISc Bangalore',
    src: 'https://lh3.googleusercontent.com/aida/AP1WRLtyM_wIGUvM8yepWSQmC3S3OQiTOQThxAs94VINQwqq1Wv-goQCi-aHfEFRqBUQvWszo-6nUAP7xhkLWDhll-fGm5x_x5mX8dGoxq-ufwY9cO01hpxq1Gu2PJ4qmGsgEIT2oC5Jr30Wnd174WAvtsMp3N5O5TfoX2DCZRuEwmSfpnXkVGUEVGe3Gsh0UmFbEKebTsUtZYOkNGb7XWlRm5qhHcBuoTb7zwFnB1mQNWTw1ufU9V60GnCFsz5D',
  },
];

const Welcome = () => {
  const navigate = useNavigate();
  const [bgIndex, setBgIndex] = useState(1);
  const mainContainerRef = useRef(null);
  const heroMainRef = useRef(null);
  const heroContentRef = useRef(null);
  const headerLogoRef = useRef(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setBgIndex((prev) => (prev + 1) % bgImages.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const tiltContainer = heroMainRef.current;
    const tiltContent = heroContentRef.current;
    if (!tiltContainer || !tiltContent) return undefined;

    const handleMove = (e) => {
      const rect = tiltContainer.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = ((y - centerY) / centerY) * -3;
      const rotateY = ((x - centerX) / centerX) * 3;
      tiltContent.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(20px)`;
    };

    const handleLeave = () => {
      tiltContent.style.transform = 'rotateX(0deg) rotateY(0deg) translateZ(0px)';
    };

    tiltContainer.addEventListener('mousemove', handleMove);
    tiltContainer.addEventListener('mouseleave', handleLeave);
    return () => {
      tiltContainer.removeEventListener('mousemove', handleMove);
      tiltContainer.removeEventListener('mouseleave', handleLeave);
    };
  }, []);

  useEffect(() => {
    const mainContainer = mainContainerRef.current;
    const headerLogo = headerLogoRef.current;
    if (!mainContainer || !headerLogo) return undefined;

    const handleMove = (e) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 15;
      const y = (e.clientY / window.innerHeight - 0.5) * 15;
      headerLogo.style.transform = `translate(${x}px, ${y}px)`;
    };

    const handleLeave = () => {
      headerLogo.style.transform = 'translate(0px, 0px)';
    };

    mainContainer.addEventListener('mousemove', handleMove);
    mainContainer.addEventListener('mouseleave', handleLeave);
    return () => {
      mainContainer.removeEventListener('mousemove', handleMove);
      mainContainer.removeEventListener('mouseleave', handleLeave);
    };
  }, []);

  return (
    <div className="welcome-body">
      <div className="welcome-bg-slider">
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

      <div className="welcome-container" ref={mainContainerRef}>
        <header className="welcome-header">
          <div className="welcome-logo" ref={headerLogoRef}>
            <img
              alt="CutoffGuide Logo"
              className="welcome-logo-img"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuBmJ8FfY3-DdAVKDZSXstVx8X6kxtsWOnhI7PR5iZuTUqz8ouifw73JOOm4s1u3RwlEQIswn4sRegRkSkOecYfrazfg8Xdfa_bmAYrOICASuoaEpDfNkjyabV6rR8oyJS5x8VblV3lWOWB3PT0bNVvAasmELwx_f05PbjJ32-CeA6yRDtLTqXEesQF-ZKJZn7Jl51RBujvjFj1riAcGT64anBZGC6xRKPQUhze-dEa5q0WpVpHcju2cjg"
            />
            <span className="welcome-logo-text">CutoffGuide</span>
          </div>
        </header>

        <main className="welcome-hero" ref={heroMainRef}>
          <div className="welcome-hero-content" ref={heroContentRef}>
            <h1 className="welcome-hero-title welcome-fade-up welcome-fade-up-1">
              Navigate Your Future with
            </h1>
            <p className="welcome-hero-desc welcome-fade-up welcome-fade-up-2">
              AI-Powered Competitive Exam &amp; College Guidance Platform designed for the next generation of scholars. Get personalized predictions, compare institutions, and chart your optimal academic path.
            </p>
            <div className="welcome-hero-actions welcome-fade-up welcome-fade-up-3">
              <button
                type="button"
                className="welcome-hero-btn"
                onClick={() => navigate('/login')}
              >
                <div className="welcome-hero-btn-shine" />
                <span className="welcome-hero-btn-text">Start Your Journey</span>
                <span className="material-symbols-outlined welcome-hero-btn-icon">
                  arrow_forward
                </span>
              </button>
            </div>
          </div>
        </main>

        <footer className="welcome-footer">
          <p className="welcome-footer-copy">
            © 2024 CutoffGuide. Developed by Fourise Software Solutions Pvt. Ltd.
          </p>
          <div className="welcome-footer-links">
            <button
              type="button"
              className="welcome-footer-link welcome-footer-link-btn"
              onClick={() => navigate('/about')}
            >
              Developer Credits
            </button>
            <button
              type="button"
              className="welcome-footer-link welcome-footer-link-btn"
              onClick={() => navigate('/privacy')}
            >
              Privacy Policy
            </button>
            <button
              type="button"
              className="welcome-footer-link welcome-footer-link-btn"
              onClick={() => navigate('/terms')}
            >
              Terms of Service
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Welcome;
