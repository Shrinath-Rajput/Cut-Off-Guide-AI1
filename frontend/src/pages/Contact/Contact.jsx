import { useMemo, useState } from 'react';
import MainLayout from '../../components/MainLayout/MainLayout';
import Button from '../../components/Button/Button';
import './Contact.css';

const faqItems = [
  {
    question: 'How accurate is the AI Predictor?',
    answer:
      'Our AI Predictor analyzes historical cutoff data from the past 5 years, current application trends, and demographic shifts. While highly accurate, it provides a probability score rather than a guarantee.',
  },
  {
    question: 'Can I update my profile data later?',
    answer:
      'Yes, you can update your mock test scores, desired branches, and category reservations at any time in your account settings. The predictor will immediately recalibrate based on your new data.',
  },
  {
    question: 'Do you provide counseling services?',
    answer:
      'Currently, we offer AI-driven guidance and data visualization. For personalized, 1-on-1 counseling, we recommend using our platform\'s data alongside a certified educational counselor.',
  },
];

const Contact = () => {
  const [form, setForm] = useState({ name: '', email: '', subject: 'General Inquiry', message: '' });
  const [success, setSuccess] = useState(false);
  const [openFaq, setOpenFaq] = useState(0);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setSuccess(true);
    setTimeout(() => setSuccess(false), 4500);
    setForm({ name: '', email: '', subject: 'General Inquiry', message: '' });
  };

  const faqElements = useMemo(
    () =>
      faqItems.map((item, index) => (
        <div key={item.question} className="faq-item">
          <button
            type="button"
            className={`faq-toggle ${openFaq === index ? 'open' : ''}`}
            onClick={() => setOpenFaq((prev) => (prev === index ? -1 : index))}
          >
            <span>{item.question}</span>
            <span className="material-symbols-outlined faq-icon">expand_more</span>
          </button>
          <div className={`faq-content ${openFaq === index ? 'open' : ''}`}>
            <p>{item.answer}</p>
          </div>
        </div>
      )),
    [openFaq]
  );

  return (
    <MainLayout>
      <div className="contact-page">
        <section className="contact-hero">
          <h1>Let's Talk</h1>
          <p>
            Have questions about admissions, our predictive models, or need support? Our team is here to help you navigate your academic journey.
          </p>
        </section>

        <div className="contact-grid">
          <section className="contact-panel contact-info-panel">
            <div className="panel-header">
              <h2>Contact Information</h2>
            </div>

            <div className="contact-item">
              <div className="contact-icon contact-icon-soft">
                <span className="material-symbols-outlined">mail</span>
              </div>
              <div>
                <p className="contact-item-title">Email Us</p>
                <p className="contact-item-text">support@cutoffguide.ai</p>
                <p className="contact-item-text">admissions@cutoffguide.ai</p>
              </div>
            </div>

            <div className="contact-item">
              <div className="contact-icon contact-icon-soft">
                <span className="material-symbols-outlined">call</span>
              </div>
              <div>
                <p className="contact-item-title">Call Us</p>
                <p className="contact-item-text">+1 (800) 123-4567</p>
                <p className="contact-item-subtext">Mon-Fri, 9am - 6pm EST</p>
              </div>
            </div>

            <div className="contact-item">
              <div className="contact-icon contact-icon-soft">
                <span className="material-symbols-outlined">location_on</span>
              </div>
              <div>
                <p className="contact-item-title">Headquarters</p>
                <p className="contact-item-text">123 Innovation Drive</p>
                <p className="contact-item-text">Suite 400</p>
                <p className="contact-item-text">Cambridge, MA 02142</p>
              </div>
            </div>
          </section>

          <section className="contact-panel contact-form-panel">
            <div className="panel-header">
              <h2>Send a Message</h2>
            </div>

            <form className="contact-form" onSubmit={handleSubmit}>
              <div className="contact-form-grid">
                <label>
                  Full Name
                  <input
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    placeholder="Jane Doe"
                    required
                  />
                </label>
                <label>
                  Email Address
                  <input
                    name="email"
                    type="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="jane@example.com"
                    required
                  />
                </label>
              </div>

              <label>
                Subject
                <select name="subject" value={form.subject} onChange={handleChange}>
                  <option>General Inquiry</option>
                  <option>Predictor Tool Support</option>
                  <option>Partnership Opportunities</option>
                  <option>Feedback</option>
                </select>
              </label>

              <label>
                Message
                <textarea
                  name="message"
                  value={form.message}
                  onChange={handleChange}
                  rows="5"
                  placeholder="How can we assist you today?"
                  required
                />
              </label>

              {success && <div className="contact-success">Message sent successfully!</div>}

              <Button variant="primary" type="submit">
                Send Message
                <span className="material-symbols-outlined">send</span>
              </Button>
            </form>
          </section>
        </div>

        <section className="faq-section">
          <h2>Frequently Asked Questions</h2>
          <div className="faq-list">{faqElements}</div>
        </section>
      </div>
    </MainLayout>
  );
};

export default Contact;
