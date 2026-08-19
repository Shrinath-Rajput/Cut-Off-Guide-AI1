import MainLayout from '../../components/MainLayout/MainLayout';
import './Terms.css';

const tableOfContents = [
  { id: 'intro', label: '1. Introduction' },
  { id: 'agreement', label: '2. Acceptance of Agreement' },
  { id: 'services', label: '3. Description of Services' },
  { id: 'responsibilities', label: '4. User Responsibilities' },
  { id: 'ai', label: '5. AI Prediction Disclaimer' },
  { id: 'account', label: '6. Account & Registration' },
  { id: 'privacy', label: '7. Privacy & Data Usage' },
  { id: 'ip', label: '8. Intellectual Property' },
  { id: 'liability', label: '9. Limitation of Liability' },
  { id: 'termination', label: '10. Termination' },
  { id: 'changes', label: '11. Changes to Terms' },
  { id: 'contact', label: '12. Contact Information' },
];

const Terms = () => {
  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <MainLayout>
      <main className="terms-page">
        <section className="terms-hero">
          <div className="terms-hero-inner">
            <div className="terms-hero-badge">
              <span className="material-symbols-outlined terms-hero-badge-icon">description</span>
              <span>LEGAL DOCUMENT</span>
            </div>
            <h1 className="terms-hero-title">Terms &amp; Conditions</h1>
            <p className="terms-hero-date">Last updated: August 13, 2026</p>
            <p className="terms-hero-desc">
              Please read these terms carefully before using CutoffGuide AI. By accessing or using our platform,
              you acknowledge that you have read, understood, and agree to be bound by the following terms.
            </p>
          </div>
        </section>

        <div className="terms-body-layout">
          <aside className="terms-toc-card">
            <div className="terms-toc-header">
              <span className="material-symbols-outlined terms-toc-icon">list_alt</span>
              <h2 className="terms-toc-title">Contents</h2>
            </div>
            <ul className="terms-toc-list">
              {tableOfContents.map((item) => (
                <li key={item.id}>
                  <button
                    type="button"
                    className="terms-toc-link"
                    onClick={() => scrollToSection(item.id)}
                  >
                    {item.label}
                  </button>
                </li>
              ))}
            </ul>
          </aside>

          <article className="terms-article">
            <section id="intro" className="terms-section">
              <div className="terms-section-head">
                <div className="terms-section-index">01</div>
                <h2 className="terms-section-title">1. Introduction</h2>
              </div>
              <p className="terms-text">
                Welcome to <strong>CutoffGuide AI</strong> (&quot;the Platform&quot;), an AI-powered educational guidance
                service operated by Fourise Software Solutions Pvt. Ltd. These Terms &amp; Conditions
                (&quot;Terms&quot;) govern your access to and use of our website, mobile applications, predictive
                tools, datasets, and all related services (collectively, the &quot;Services&quot;).
              </p>
              <p className="terms-text">
                By creating an account, logging in, or otherwise using the Services, you confirm that you are at
                least 13 years of age and possess the legal authority to enter into this agreement. If you are
                using the Services on behalf of an institution or organization, you represent that you have full
                authority to bind that entity to these Terms.
              </p>
            </section>

            <section id="agreement" className="terms-section">
              <div className="terms-section-head">
                <div className="terms-section-index">02</div>
                <h2 className="terms-section-title">2. Acceptance of Agreement</h2>
              </div>
              <p className="terms-text">
                Your continued use of the Services constitutes acceptance of these Terms and our Privacy Policy,
                as may be amended from time to time. If you object to any provision, your sole remedy is to
                discontinue use of the Platform immediately.
              </p>
              <div className="terms-callout terms-callout-info">
                <div className="terms-callout-icon-wrap">
                  <span className="material-symbols-outlined terms-callout-icon">info</span>
                </div>
                <div>
                  <p className="terms-callout-title">Policy Updates</p>
                  <p className="terms-callout-text">
                    We will notify you of material changes via the email associated with your account or through
                    an in-platform notification at least 15 days prior to the effective date.
                  </p>
                </div>
              </div>
            </section>

            <section id="services" className="terms-section">
              <div className="terms-section-head">
                <div className="terms-section-index">03</div>
                <h2 className="terms-section-title">3. Description of Services</h2>
              </div>
              <p className="terms-text">
                CutoffGuide AI provides users with educational guidance tools, including but not limited to:
              </p>
              <ul className="terms-list">
                <li>AI-driven cutoff and rank predictions based on historical admission datasets.</li>
                <li>College and university search, filtering, and discovery engine.</li>
                <li>Side-by-side comparison of institutions across 50+ metrics.</li>
                <li>Conversational AI assistant for personalized academic counseling.</li>
                <li>Saved colleges, bookmarked predictions, and analysis history.</li>
              </ul>
              <p className="terms-text">
                All Services are provided on an &quot;as available&quot; basis. We strive for 99.9% uptime but do not
                warrant uninterrupted or error-free access.
              </p>
            </section>

            <section id="responsibilities" className="terms-section">
              <div className="terms-section-head">
                <div className="terms-section-index">04</div>
                <h2 className="terms-section-title">4. User Responsibilities</h2>
              </div>
              <p className="terms-text">
                As a user of CutoffGuide AI, you agree to all of the following:
              </p>
              <div className="terms-responsibility-grid">
                <div className="terms-responsibility-card">
                  <div className="terms-resp-icon terms-resp-icon-1">
                    <span className="material-symbols-outlined">check_circle</span>
                  </div>
                  <h4 className="terms-resp-title">Accurate Inputs</h4>
                  <p className="terms-resp-text">
                    Provide truthful and accurate information when using prediction tools and profile setup.
                  </p>
                </div>
                <div className="terms-responsibility-card">
                  <div className="terms-resp-icon terms-resp-icon-2">
                    <span className="material-symbols-outlined">lock</span>
                  </div>
                  <h4 className="terms-resp-title">Account Security</h4>
                  <p className="terms-resp-text">
                    Maintain the confidentiality of your credentials and notify us immediately of unauthorized use.
                  </p>
                </div>
                <div className="terms-responsibility-card">
                  <div className="terms-resp-icon terms-resp-icon-3">
                    <span className="material-symbols-outlined">block</span>
                  </div>
                  <h4 className="terms-resp-title">Lawful Use</h4>
                  <p className="terms-resp-text">
                    Use the Services only for lawful, non-commercial purposes. No scraping, crawling, or reverse engineering.
                  </p>
                </div>
                <div className="terms-responsibility-card">
                  <div className="terms-resp-icon terms-resp-icon-4">
                    <span className="material-symbols-outlined">shield</span>
                  </div>
                  <h4 className="terms-resp-title">Fair Usage</h4>
                  <p className="terms-resp-text">
                    Do not overload or attempt to disrupt the integrity of our APIs, datasets, or infrastructure.
                  </p>
                </div>
              </div>
            </section>

            <section id="ai" className="terms-section">
              <div className="terms-section-head">
                <div className="terms-section-index">05</div>
                <h2 className="terms-section-title">5. AI Prediction Disclaimer</h2>
              </div>
              <div className="terms-disclaimer-card">
                <div className="terms-disclaimer-head">
                  <span className="material-symbols-outlined terms-disclaimer-icon">warning</span>
                  <h4 className="terms-disclaimer-title">IMPORTANT — PLEASE READ</h4>
                </div>
                <p className="terms-disclaimer-text">
                  The predictions, probability scores, and recommendations generated by CutoffGuide AI are produced
                  by machine-learning models trained on historical admission data. They are statistical estimates
                  only and do <strong>not</strong> constitute a guarantee of admission, scholarship, or any outcome.
                </p>
                <p className="terms-disclaimer-text">
                  Actual admission decisions are made exclusively by the respective colleges, universities, and
                  regulatory bodies based on their own criteria, seat availability, reservation policies, and
                  additional factors not captured by our models. Users are strongly advised to cross-verify with
                  official sources and consult certified educational counselors before making final decisions.
                </p>
              </div>
            </section>

            <section id="account" className="terms-section">
              <div className="terms-section-head">
                <div className="terms-section-index">06</div>
                <h2 className="terms-section-title">6. Account &amp; Registration</h2>
              </div>
              <p className="terms-text">
                Access to certain features requires creating an account via OTP-based phone authentication or
                Google SSO. You are responsible for all activity occurring under your account.
              </p>
              <ul className="terms-list">
                <li>We reserve the right to suspend or terminate accounts that violate these Terms.</li>
                <li>You may request permanent account deletion via your Profile settings at any time.</li>
                <li>Deactivated accounts are fully anonymized within 30 days of deletion request.</li>
              </ul>
            </section>

            <section id="privacy" className="terms-section">
              <div className="terms-section-head">
                <div className="terms-section-index">07</div>
                <h2 className="terms-section-title">7. Privacy &amp; Data Usage</h2>
              </div>
              <p className="terms-text">
                Your use of the Services is also governed by our <a href="#privacy-policy">Privacy Policy</a>,
                which describes how we collect, store, process, and safeguard your personal information. We
                commit to:
              </p>
              <ul className="terms-list">
                <li>Never selling your academic or personal data to third parties.</li>
                <li>Encrypting data in transit (TLS 1.3) and at rest (AES-256).</li>
                <li>Allowing you to export or erase all of your data at any time.</li>
                <li>Using anonymized data only for improving model accuracy and platform quality.</li>
              </ul>
            </section>

            <section id="ip" className="terms-section">
              <div className="terms-section-head">
                <div className="terms-section-index">08</div>
                <h2 className="terms-section-title">8. Intellectual Property</h2>
              </div>
              <p className="terms-text">
                All content, trademarks, logos, training datasets, model weights, software, and documentation
                published on or through the Platform are the exclusive property of Fourise Software Solutions Pvt. Ltd.
                or its licensors. You may not reproduce, distribute, modify, or create derivative works without
                prior written authorization.
              </p>
            </section>

            <section id="liability" className="terms-section">
              <div className="terms-section-head">
                <div className="terms-section-index">09</div>
                <h2 className="terms-section-title">9. Limitation of Liability</h2>
              </div>
              <p className="terms-text">
                To the maximum extent permitted by law, CutoffGuide AI and its directors, employees, and partners
                shall not be liable for any indirect, incidental, special, consequential, or punitive damages
                arising from your use or inability to use the Services, including but not limited to missed
                admission deadlines, incorrect college selection, or loss of opportunity.
              </p>
            </section>

            <section id="termination" className="terms-section">
              <div className="terms-section-head">
                <div className="terms-section-index">10</div>
                <h2 className="terms-section-title">10. Termination</h2>
              </div>
              <p className="terms-text">
                Either party may terminate this agreement at any time. Upon termination:
              </p>
              <ul className="terms-list">
                <li>Your right to use the Services ceases immediately.</li>
                <li>Provisions regarding IP, disclaimer, and liability survive termination indefinitely.</li>
                <li>Your data is retained for a minimum of 30 days to allow export before deletion.</li>
              </ul>
            </section>

            <section id="changes" className="terms-section">
              <div className="terms-section-head">
                <div className="terms-section-index">11</div>
                <h2 className="terms-section-title">11. Changes to Terms</h2>
              </div>
              <p className="terms-text">
                We may update these Terms periodically. The &quot;Last updated&quot; date at the top of this page
                reflects the most recent revision. Continued use of the Platform after such changes confirms your
                acceptance of the revised Terms.
              </p>
            </section>

            <section id="contact" className="terms-section terms-section-last">
              <div className="terms-section-head">
                <div className="terms-section-index">12</div>
                <h2 className="terms-section-title">12. Contact Information</h2>
              </div>
              <p className="terms-text">
                For questions about these Terms or any aspect of our Services, please reach out through the
                following channels:
              </p>
              <div className="terms-contact-grid">
                <div className="terms-contact-card">
                  <span className="material-symbols-outlined terms-contact-icon">mail</span>
                  <h4>Email Support</h4>
                  <p>legal@cutoffguide.ai</p>
                </div>
                <div className="terms-contact-card">
                  <span className="material-symbols-outlined terms-contact-icon">chat</span>
                  <h4>Help Center</h4>
                  <p>Visit /contact in-platform</p>
                </div>
                <div className="terms-contact-card">
                  <span className="material-symbols-outlined terms-contact-icon">apartment</span>
                  <h4>Registered Office</h4>
                  <p>Fourise Software Solutions Pvt. Ltd., India</p>
                </div>
              </div>
            </section>
          </article>
        </div>
      </main>
    </MainLayout>
  );
};

export default Terms;
