import { Link } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import coepHeritageImg from '../../assets/images/coep-heritage.jpg';
import graduatesCtaImg from '../../assets/images/graduates-cta.png';
import './Home.css';

const Home = () => {
  return (
    <div className="bg-background text-on-background antialiased font-body-md overflow-x-hidden min-h-screen flex flex-col">
      <Navbar />

      <main className="pt-24 md:pt-32 pb-stack-lg home-bg-texture min-h-screen flex-grow">
        {/* Hero Section */}
        <section className="relative max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop flex items-center min-h-[80vh] overflow-hidden rounded-3xl">
          {/* Heritage Building Backdrop Image */}
          <div className="absolute inset-0 z-0 overflow-hidden rounded-3xl">
            <img
              alt="College of Engineering Pune heritage building"
              className="w-full h-full object-cover object-center transform scale-105 transition-transform duration-1000"
              src={coepHeritageImg}
            />
            {/* Subtle Gradient Overlays */}
            <div className="absolute inset-0 bg-gradient-to-r from-surface/90 via-surface/60 to-transparent" />
            <div className="absolute inset-0 bg-gradient-to-t from-surface/80 via-transparent to-transparent" />
          </div>

          {/* Floating Hero Glass Card */}
          <div className="space-y-stack-md relative z-10 max-w-2xl home-glass-panel p-8 md:p-10 rounded-3xl animate-float-hero my-8">
            <h1 className="font-display text-headline-lg-mobile md:text-display text-on-background font-extrabold leading-tight">
              <span className="block animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
                Your Future.
              </span>
              <span className="block animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
                Your College.
              </span>
              <span
                className="text-primary-container italic font-extrabold block animate-fade-in-up"
                style={{ animationDelay: '0.5s' }}
              >
                Your Choice.
              </span>
            </h1>

            <p
              className="font-body-lg text-body-lg text-on-surface-variant max-w-lg mt-stack-sm animate-fade-in-up leading-relaxed"
              style={{ animationDelay: '0.7s' }}
            >
              Leverage advanced artificial intelligence to accurately predict college cutoffs, compare premier institutions, and architect your academic destiny with precision.
            </p>

            <div
              className="flex flex-wrap gap-stack-sm pt-stack-sm animate-fade-in-up items-center"
              style={{ animationDelay: '0.9s' }}
            >
              <Link
                to="/cutoff"
                className="bg-primary shimmer-btn text-on-primary font-label-md text-label-md px-7 py-3.5 rounded-xl flex items-center gap-2 hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-primary/50 text-white font-bold no-underline"
              >
                Start Your Journey
                <span className="material-symbols-outlined text-sm transition-transform group-hover:translate-x-1">
                  arrow_forward
                </span>
              </Link>
              <Link
                to="/colleges"
                className="bg-surface text-on-surface border border-outline font-label-md text-label-md px-7 py-3.5 rounded-xl hover:bg-surface-container-low hover:scale-105 transition-all duration-300 hover:shadow-md font-bold no-underline"
              >
                Explore Colleges
              </Link>
            </div>
          </div>
        </section>

        {/* Statistics Bar */}
        <section className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop mt-stack-lg relative z-20 -mt-10">
          <div className="home-glass-panel bg-surface/90 rounded-2xl border border-outline-variant/40 shadow-md py-stack-md px-stack-lg flex flex-wrap justify-around items-center gap-stack-md text-center">
            <div className="flex-1 min-w-[120px] animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              <h3 className="font-display text-headline-md text-on-surface hover:text-primary transition-colors font-extrabold text-2xl md:text-3xl">
                500+
              </h3>
              <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mt-1 font-semibold text-xs">
                Colleges Tracked
              </p>
            </div>
            <div className="hidden md:block w-px h-12 bg-outline-variant/40" />
            <div className="flex-1 min-w-[120px] animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
              <h3 className="font-display text-headline-md text-on-surface hover:text-primary transition-colors font-extrabold text-2xl md:text-3xl">
                50K+
              </h3>
              <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mt-1 font-semibold text-xs">
                Students Guided
              </p>
            </div>
            <div className="hidden md:block w-px h-12 bg-outline-variant/40" />
            <div className="flex-1 min-w-[120px] animate-fade-in-up" style={{ animationDelay: '0.6s' }}>
              <h3 className="font-display text-headline-md text-on-surface hover:text-primary transition-colors font-extrabold text-2xl md:text-3xl">
                95%+
              </h3>
              <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mt-1 font-semibold text-xs">
                Prediction Accuracy
              </p>
            </div>
            <div className="hidden md:block w-px h-12 bg-outline-variant/40" />
            <div className="flex-1 min-w-[120px] animate-fade-in-up" style={{ animationDelay: '0.8s' }}>
              <h3 className="font-display text-headline-md text-on-surface hover:text-primary transition-colors font-extrabold text-2xl md:text-3xl">
                1000+
              </h3>
              <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mt-1 font-semibold text-xs">
                Courses Analyzed
              </p>
            </div>
          </div>
        </section>

        {/* Feature Grid Section */}
        <section className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg mt-stack-lg">
          <div className="text-center max-w-2xl mx-auto mb-stack-lg animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
            <h2 className="font-display text-headline-lg-mobile md:text-headline-lg text-on-background mb-stack-sm font-extrabold text-2xl md:text-4xl">
              Everything You Need for Your College Journey
            </h2>
            <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed">
              A comprehensive suite of intelligent tools designed to transform uncertainty into strategic academic decisions.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-gutter">
            {/* Feature Card 1 */}
            <Link
              to="/cutoff"
              className="bg-surface rounded-2xl p-6 border border-outline-variant/30 shadow-sm hover:-translate-y-2 hover:shadow-xl hover:shadow-primary/10 transition-all duration-300 group animate-fade-in-up no-underline block"
              style={{ animationDelay: '0.4s' }}
            >
              <div className="bg-surface-container-low w-12 h-12 rounded-xl flex items-center justify-center text-primary mb-4 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300 shadow-sm">
                <span className="material-symbols-outlined text-primary">my_location</span>
              </div>
              <h3 className="font-headline-md text-label-md text-on-surface mb-2 group-hover:text-primary transition-colors font-bold text-lg">
                AI Cutoff Predictor
              </h3>
              <p className="font-body-md text-label-sm text-on-surface-variant leading-relaxed">
                Input your scores and let our machine learning models analyze historical data to provide real-time admission probabilities across top institutions.
              </p>
            </Link>

            {/* Feature Card 2 */}
            <Link
              to="/colleges"
              className="bg-surface rounded-2xl p-6 border border-outline-variant/30 shadow-sm hover:-translate-y-2 hover:shadow-xl hover:shadow-primary/10 transition-all duration-300 group animate-fade-in-up no-underline block"
              style={{ animationDelay: '0.5s' }}
            >
              <div className="bg-surface-container-low w-12 h-12 rounded-xl flex items-center justify-center text-primary mb-4 group-hover:scale-110 group-hover:-rotate-3 transition-transform duration-300 shadow-sm">
                <span className="material-symbols-outlined text-primary">travel_explore</span>
              </div>
              <h3 className="font-headline-md text-label-md text-on-surface mb-2 group-hover:text-primary transition-colors font-bold text-lg">
                College Discovery
              </h3>
              <p className="font-body-md text-label-sm text-on-surface-variant leading-relaxed">
                Explore hidden gems and premier universities tailored precisely to your academic profile and career aspirations.
              </p>
            </Link>

            {/* Feature Card 3 */}
            <Link
              to="/compare"
              className="bg-surface rounded-2xl p-6 border border-outline-variant/30 shadow-sm hover:-translate-y-2 hover:shadow-xl hover:shadow-primary/10 transition-all duration-300 group animate-fade-in-up no-underline block"
              style={{ animationDelay: '0.6s' }}
            >
              <div className="bg-surface-container-low w-12 h-12 rounded-xl flex items-center justify-center text-primary mb-4 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300 shadow-sm">
                <span className="material-symbols-outlined text-primary">compare_arrows</span>
              </div>
              <h3 className="font-headline-md text-label-md text-on-surface mb-2 group-hover:text-primary transition-colors font-bold text-lg">
                Smart Comparison
              </h3>
              <p className="font-body-md text-label-sm text-on-surface-variant leading-relaxed">
                Evaluate institutions side-by-side on metrics that matter: placements, faculty, infrastructure, and fee structures.
              </p>
            </Link>

            {/* Feature Card 4 */}
            <Link
              to="/assistant"
              className="bg-surface rounded-2xl p-6 border border-outline-variant/30 shadow-sm hover:-translate-y-2 hover:shadow-xl hover:shadow-primary/10 transition-all duration-300 group animate-fade-in-up no-underline block"
              style={{ animationDelay: '0.7s' }}
            >
              <div className="bg-surface-container-low w-12 h-12 rounded-xl flex items-center justify-center text-primary mb-4 group-hover:scale-110 group-hover:-rotate-3 transition-transform duration-300 shadow-sm">
                <span className="material-symbols-outlined text-primary">forum</span>
              </div>
              <h3 className="font-headline-md text-label-md text-on-surface mb-2 group-hover:text-primary transition-colors font-bold text-lg">
                AI Council
              </h3>
              <p className="font-body-md text-label-sm text-on-surface-variant leading-relaxed">
                Consult with our generative AI for personalized advice on course selection and long-term career trajectories.
              </p>
            </Link>

            {/* Feature Card 5 */}
            <Link
              to="/saved"
              className="bg-surface rounded-2xl p-6 border border-outline-variant/30 shadow-sm hover:-translate-y-2 hover:shadow-xl hover:shadow-primary/10 transition-all duration-300 group animate-fade-in-up no-underline block"
              style={{ animationDelay: '0.8s' }}
            >
              <div className="bg-surface-container-low w-12 h-12 rounded-xl flex items-center justify-center text-primary mb-4 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300 shadow-sm">
                <span className="material-symbols-outlined text-primary">bookmark</span>
              </div>
              <h3 className="font-headline-md text-label-md text-on-surface mb-2 group-hover:text-primary transition-colors font-bold text-lg">
                Saved Colleges
              </h3>
              <p className="font-body-md text-label-sm text-on-surface-variant leading-relaxed">
                Organize your shortlists. Keep track of application deadlines, required documents, and important updates for your preferred colleges.
              </p>
            </Link>

            {/* Feature Card 6 */}
            <Link
              to="/history"
              className="bg-surface rounded-2xl p-6 border border-outline-variant/30 shadow-sm hover:-translate-y-2 hover:shadow-xl hover:shadow-primary/10 transition-all duration-300 group animate-fade-in-up no-underline block"
              style={{ animationDelay: '0.9s' }}
            >
              <div className="bg-surface-container-low w-12 h-12 rounded-xl flex items-center justify-center text-primary mb-4 group-hover:scale-110 group-hover:-rotate-3 transition-transform duration-300 shadow-sm">
                <span className="material-symbols-outlined text-primary">history</span>
              </div>
              <h3 className="font-headline-md text-label-md text-on-surface mb-2 group-hover:text-primary transition-colors font-bold text-lg">
                Prediction History
              </h3>
              <p className="font-body-md text-label-sm text-on-surface-variant leading-relaxed">
                Review past analyses. Compare how your chances evolve as you update your scores or as cutoff trends shift over time.
              </p>
            </Link>
          </div>
        </section>

        {/* CTA Section (Above Footer with Crisp Graduates Backdrop) */}
        <section className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg animate-fade-in-up mb-12" style={{ animationDelay: '0.5s' }}>
          <div className="relative rounded-3xl overflow-hidden shadow-xl border border-outline-variant/40 min-h-[440px] md:min-h-[500px] flex items-end md:items-center">
            {/* Crisp High-Res Graduates Background Image (No blur) */}
            <div className="absolute inset-0 z-0">
              <img
                src={graduatesCtaImg}
                alt="Graduates celebrating success"
                className="w-full h-full object-cover object-top md:object-center"
              />
              {/* Subtle gradient vignette to ensure high text contrast while keeping image neat & crisp */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/40 to-transparent md:bg-gradient-to-r md:from-black/80 md:via-black/40 md:to-transparent" />
            </div>

            {/* Content Overlapping on the Image */}
            <div className="relative z-10 p-8 md:p-14 max-w-2xl flex flex-col items-start gap-4">
              <div className="inline-flex items-center gap-2 bg-primary/90 text-white text-xs font-bold px-3.5 py-1.5 rounded-full shadow-sm backdrop-blur-sm">
                <span className="material-symbols-outlined text-sm">school</span>
                <span>Admissions 2026</span>
              </div>

              <h2 className="font-display text-2xl sm:text-3xl md:text-4xl text-white font-extrabold leading-tight tracking-tight drop-shadow-md">
                Ready to find your perfect college?
              </h2>

              <p className="font-body-md text-white/90 text-sm md:text-base leading-relaxed drop-shadow-sm max-w-lg">
                Join thousands of students who have successfully navigated their admissions using our predictive intelligence.
              </p>

              <div className="flex flex-wrap gap-3 mt-2">
                <Link
                  to="/cutoff"
                  className="bg-primary shimmer-btn text-white font-label-md text-sm px-8 py-3.5 rounded-xl flex items-center gap-2 transition-all hover:scale-105 shadow-[0_0_20px_rgba(230,126,34,0.4)] hover:shadow-[0_0_40px_rgba(230,126,34,0.7)] duration-300 font-bold no-underline cursor-pointer"
                >
                  Start Prediction
                  <span className="material-symbols-outlined text-sm transition-transform group-hover:rotate-12">
                    auto_awesome
                  </span>
                </Link>

                <Link
                  to="/colleges"
                  className="bg-white/20 hover:bg-white/30 text-white border border-white/40 backdrop-blur-md font-label-md text-sm px-6 py-3.5 rounded-xl transition-all duration-300 font-bold no-underline cursor-pointer"
                >
                  Explore Colleges
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default Home;
