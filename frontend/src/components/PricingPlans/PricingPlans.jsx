import { useState } from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';

const plans = [
  {
    name: 'Starter',
    monthlyPrice: '$19',
    yearlyPrice: '$15',
    description: 'Perfect for students and solo builders who want a polished edge.',
    features: ['AI college shortlist', 'Daily cutoff insights', 'Saved college workspace'],
    cta: 'Get started',
    featured: false,
  },
  {
    name: 'Professional',
    monthlyPrice: '$54',
    yearlyPrice: '$45',
    description: 'For ambitious applicants who want deeper strategy and smart guidance.',
    features: ['Advanced admission analytics', 'Priority recommendations', 'Unlimited shortlist exports'],
    cta: 'Choose Professional',
    featured: false,
  },
  {
    name: 'Company',
    monthlyPrice: '$89',
    yearlyPrice: '$74',
    description: 'Made for teams, institutes, and high-volume counsellor workflows.',
    features: ['Team collaboration', 'Shared dashboards', 'Dedicated success manager'],
    cta: 'Book a demo',
    featured: true,
  },
];

const PricingCard = ({ plan, billingMode }) => {
  const isFeatured = plan.featured;
  const displayPrice = billingMode === 'monthly' ? plan.monthlyPrice : plan.yearlyPrice;

  return (
    <motion.article
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -8, scale: 1.01, transition: { duration: 0.2 } }}
      className={`relative overflow-hidden rounded-[24px] border p-7 sm:p-8 shadow-[0_18px_60px_rgba(91,33,182,0.10)] backdrop-blur-xl transition-all duration-300 ${
        isFeatured
          ? 'border-white/10 bg-[linear-gradient(135deg,_#1d103f_0%,_#2d1563_55%,_#4a1e8a_100%)] text-white shadow-[0_30px_90px_rgba(102,36,217,0.34)] lg:scale-[1.03]'
          : 'border-violet-100/80 bg-white/80 text-slate-800'
      }`}
    >
      {isFeatured && (
        <div className="absolute inset-x-0 top-0 flex justify-center">
          <span className="rounded-b-full bg-gradient-to-r from-violet-400 to-fuchsia-400 px-4 py-1.5 text-[10px] font-semibold uppercase tracking-[0.35em] text-white shadow-lg shadow-fuchsia-400/30">
            MOST POPULAR
          </span>
        </div>
      )}

      <div className={`absolute -right-8 -top-8 h-28 w-28 rounded-full blur-3xl ${isFeatured ? 'bg-fuchsia-400/25' : 'bg-violet-200/40'}`} />
      <div className={`absolute -bottom-8 -left-8 h-24 w-24 rounded-full blur-3xl ${isFeatured ? 'bg-violet-500/20' : 'bg-fuchsia-200/30'}`} />

      <div className="relative">
        <div className="mb-6 flex items-center justify-between">
          <h3 className={`text-xl font-semibold ${isFeatured ? 'text-white' : 'text-slate-900'}`}>{plan.name}</h3>
          {isFeatured ? (
            <span className="rounded-full border border-white/20 bg-white/10 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] text-violet-100">
              Premium
            </span>
          ) : (
            <span className="rounded-full bg-violet-100 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] text-violet-700">
              Growth
            </span>
          )}
        </div>

        <p className={`mb-8 text-sm leading-6 ${isFeatured ? 'text-violet-100/90' : 'text-slate-600'}`}>
          {plan.description}
        </p>

        <div className="mb-8 flex items-end gap-1">
          <span className={`text-5xl font-semibold tracking-tight ${isFeatured ? 'text-white' : 'text-slate-900'}`}>
            {displayPrice}
          </span>
          <span className={`pb-1 text-sm font-medium ${isFeatured ? 'text-violet-100' : 'text-slate-500'}`}>
            /month
          </span>
        </div>

        <motion.button
          whileHover={{ scale: 1.03, boxShadow: '0 0 0 6px rgba(139,92,246,0.16)' }}
          whileTap={{ scale: 0.98 }}
          className={`mb-8 w-full rounded-full px-5 py-3 text-sm font-semibold transition-all duration-300 ${
            isFeatured
              ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow-[0_12px_35px_rgba(168,85,247,0.28)] hover:brightness-110'
              : 'bg-gradient-to-r from-violet-600 to-fuchsia-500 text-white shadow-[0_12px_30px_rgba(124,58,237,0.2)]'
          }`}
        >
          {plan.cta}
        </motion.button>

        <ul className="space-y-3">
          {plan.features.map((feature) => (
            <li key={feature} className="flex items-start gap-3 text-sm">
              <span className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${isFeatured ? 'bg-white/15 text-white' : 'bg-violet-100 text-violet-700'}`}>
                <Check size={14} />
              </span>
              <span className={isFeatured ? 'text-violet-100' : 'text-slate-600'}>{feature}</span>
            </li>
          ))}
        </ul>
      </div>
    </motion.article>
  );
};

const PricingPlans = () => {
  const [billingMode, setBillingMode] = useState('monthly');

  return (
    <section className="relative overflow-hidden rounded-[32px] border border-violet-100/70 bg-[radial-gradient(circle_at_top_left,_rgba(255,255,255,0.95),_rgba(244,236,255,0.98))] px-4 py-14 sm:px-6 lg:px-8 lg:py-16">
      <div className="absolute inset-0 bg-[linear-gradient(135deg,_rgba(247,244,255,0.95)_0%,_rgba(245,238,252,0.92)_100%)]" />
      <div className="relative mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-10 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between"
        >
          <div className="max-w-2xl">
            <p className="mb-3 inline-flex rounded-full border border-violet-200 bg-white/70 px-4 py-1.5 text-sm font-semibold uppercase tracking-[0.3em] text-violet-700 shadow-sm">
              Premium plans
            </p>
            <h2 className="text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl">
              Plans & Pricing
            </h2>
            <p className="mt-3 text-lg leading-8 text-slate-600">
              Upgrade your admissions journey with an elegant, high-conviction experience built for momentum.
            </p>
          </div>

          <div className="inline-flex rounded-full border border-violet-200 bg-white/70 p-1.5 shadow-[0_10px_30px_rgba(139,92,246,0.12)] backdrop-blur">
            <button
              type="button"
              onClick={() => setBillingMode('monthly')}
              className={`rounded-full px-4 py-2 text-sm font-semibold transition-all duration-300 ${
                billingMode === 'monthly' ? 'bg-violet-600 text-white shadow-lg shadow-violet-200' : 'text-slate-600'
              }`}
            >
              Monthly
            </button>
            <button
              type="button"
              onClick={() => setBillingMode('yearly')}
              className={`rounded-full px-4 py-2 text-sm font-semibold transition-all duration-300 ${
                billingMode === 'yearly' ? 'bg-violet-600 text-white shadow-lg shadow-violet-200' : 'text-slate-600'
              }`}
            >
              Yearly
            </button>
          </div>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {plans.map((plan) => (
            <PricingCard key={plan.name} plan={plan} billingMode={billingMode} />
          ))}
        </div>
      </div>
    </section>
  );
};

export default PricingPlans;
