import React, { useState } from 'react';
import {
  Activity,
  UserPlus,
  Sparkles,
  ShieldCheck,
  FileText,
  AlertTriangle,
  History,
  TrendingUp,
  ArrowRight,
  CheckCircle2,
  FileUp,
  Search,
  Lock,
  Stethoscope,
  Info
} from 'lucide-react';
import { api } from '../api/client';

interface Props {
  onOpenNewPatientModal: () => void;
  onOpenIndianRegistration: () => void;
  onDemoLoaded: () => void;
}

export const WelcomeView: React.FC<Props> = ({
  onOpenNewPatientModal,
  onOpenIndianRegistration,
  onDemoLoaded,
}) => {
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [demoError, setDemoError] = useState<string | null>(null);

  const handleLoadDemo = async () => {
    setLoadingDemo(true);
    setDemoError(null);
    try {
      await api.seedDemoData();
      onDemoLoaded();
    } catch (err: any) {
      console.error('Failed to load demo data:', err);
      setDemoError(err.message || 'Failed to populate demo data');
    } finally {
      setLoadingDemo(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in-up">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-clinical-950 to-slate-900 border border-slate-800 p-8 sm:p-12 text-white shadow-xl">
        {/* Subtle background glow effect */}
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-clinical-500/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-12 w-80 h-80 bg-purple-500/15 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-clinical-500/10 border border-clinical-400/30 text-clinical-300 text-xs font-semibold backdrop-blur-sm">
            <Activity className="w-3.5 h-3.5 text-clinical-400 animate-pulse" />
            <span>MedLens Clinical Intelligence Platform</span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-white leading-tight">
            Unified, Source-Traceable <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 via-clinical-300 to-indigo-300">
              Patient Intelligence
            </span>
          </h1>

          <p className="text-slate-300 text-sm sm:text-base leading-relaxed max-w-2xl">
            Welcome! MedLens consolidates intake forms and diagnostic lab PDFs into a single,
            traceable clinical record. Designed with strict non-diagnostic guardrails, zero data hallucination,
            ABDM/DPDP 2023 compliance, and human-in-the-loop review.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-4">
            <button
              id="welcome-indian-reg-btn"
              onClick={onOpenIndianRegistration}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-amber-500 via-clinical-600 to-emerald-600 hover:from-amber-600 hover:to-emerald-700 text-white font-bold text-sm shadow-lg shadow-emerald-500/25 transition-all transform hover:-translate-y-0.5"
            >
              <span>🇮🇳</span>
              <span>Register Indian Patient (+91 / ABHA)</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              id="welcome-create-patient-btn"
              onClick={onOpenNewPatientModal}
              className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-white/10 hover:bg-white/20 active:bg-white/25 border border-white/20 text-white font-semibold text-sm backdrop-blur-sm transition-all"
            >
              <UserPlus className="w-4 h-4" />
              <span>Standard Intake</span>
            </button>

            <button
              id="welcome-load-demo-btn"
              onClick={handleLoadDemo}
              disabled={loadingDemo}
              className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-white/10 hover:bg-white/20 active:bg-white/25 border border-white/20 text-white font-semibold text-sm backdrop-blur-sm transition-all"
            >
              {loadingDemo ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Seeding Demo...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-amber-300" />
                  <span>Sample Sandbox</span>
                </>
              )}
            </button>
          </div>

          {demoError && (
            <div className="text-xs text-rose-300 bg-rose-950/50 border border-rose-800/60 p-2.5 rounded-lg max-w-md">
              {demoError}
            </div>
          )}
        </div>
      </div>

      {/* Three Choice Action Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Card 1: Indian Onboarding (Featured) */}
        <div className="bg-gradient-to-b from-white to-amber-50/30 rounded-2xl border-2 border-amber-300 p-6 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-amber-500 via-white to-emerald-600" />
          <div className="space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-amber-100/70 border border-amber-300 text-amber-800 flex items-center justify-center font-bold text-xl">
              🇮🇳
            </div>

            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-amber-700">Option 1 • Recommended</span>
              <h2 className="text-lg font-bold text-slate-900 mt-1">Indian Patient Onboarding</h2>
              <p className="text-xs text-slate-500 mt-2 leading-relaxed">
                3-step wizard with +91 mobile OTP verification (SMS/WhatsApp), Aadhaar legal name, ABHA ID auto-formatter, state/city directory, and real-time safety guardrails.
              </p>
            </div>

            <div className="space-y-2 pt-2 text-xs text-slate-600">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>+91 Indian telecom regex & 6-box OTP</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>ABHA ID (XX-XXXX-XXXX-XXXX) & DPDP 2023</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Real-time Penicillin vs Amoxicillin alerts</span>
              </div>
            </div>
          </div>

          <div className="pt-6">
            <button
              id="card-indian-onboarding-btn"
              onClick={onOpenIndianRegistration}
              className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 via-clinical-600 to-emerald-600 hover:from-amber-600 hover:to-emerald-700 text-white font-bold text-xs shadow-md transition-all"
            >
              <span>🇮🇳 Start Indian Onboarding</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Card 2: Standard Intake */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group">
          <div className="space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-clinical-50 border border-clinical-200 text-clinical-600 flex items-center justify-center font-bold">
              <UserPlus className="w-6 h-6" />
            </div>

            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-clinical-600">Option 2 • Standard</span>
              <h2 className="text-lg font-bold text-slate-900 mt-1">Quick Patient Intake</h2>
              <p className="text-xs text-slate-500 mt-2 leading-relaxed">
                Create a standard patient profile with name, DOB, and sex, then proceed directly to clinical intake and document ingestion.
              </p>
            </div>

            <div className="space-y-2 pt-2 text-xs text-slate-600">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Immediate profile provisioning</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Deterministic range-flagging</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Zero AI hallucination guarantee</span>
              </div>
            </div>
          </div>

          <div className="pt-6">
            <button
              onClick={onOpenNewPatientModal}
              className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs shadow-sm transition-colors"
            >
              <UserPlus className="w-4 h-4" />
              <span>Standard Intake</span>
            </button>
          </div>
        </div>

        {/* Card 3: Interactive Sample Demo */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group">
          <div className="space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-purple-50 border border-purple-200 text-purple-600 flex items-center justify-center font-bold">
              <Sparkles className="w-6 h-6" />
            </div>

            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-purple-600">Option 3 • Sandbox</span>
              <h2 className="text-lg font-bold text-slate-900 mt-1">Explore Demo Sandbox</h2>
              <p className="text-xs text-slate-500 mt-2 leading-relaxed">
                Populate synthetic clinical test cases to explore all views: Eleanor Vance (Penicillin allergy alert) and Arthur Pendelton (CBC panel).
              </p>
            </div>

            <div className="space-y-2 pt-2 text-xs text-slate-600">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-purple-600 flex-shrink-0" />
                <span>Eleanor Vance (Penicillin conflict)</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-purple-600 flex-shrink-0" />
                <span>Arthur Pendelton (CBC side-by-side)</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-purple-600 flex-shrink-0" />
                <span>Instant full feature exploration</span>
              </div>
            </div>
          </div>

          <div className="pt-6">
            <button
              id="card-explore-demo-btn"
              onClick={handleLoadDemo}
              disabled={loadingDemo}
              className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 active:bg-purple-800 text-white font-semibold text-xs shadow-sm transition-colors"
            >
              {loadingDemo ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Loading Demo...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-amber-300" />
                  <span>Load Sample Demo Data</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* How MedLens Works (4 Pillars) */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
        <div>
          <h2 className="text-base font-bold text-slate-900">How MedLens Works</h2>
          <p className="text-xs text-slate-500 mt-1">
            Engineered for high fidelity, transparency, and safety across 4 clinical intelligence stages.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-clinical-100 text-clinical-700 flex items-center justify-center font-black text-xs">
              1
            </div>
            <div className="text-xs font-bold text-slate-900">Intake Harmonization</div>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              Standardized capture of symptoms, conditions, allergies, and medications with source provenance tagging.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-sky-100 text-sky-700 flex items-center justify-center font-black text-xs">
              2
            </div>
            <div className="text-xs font-bold text-slate-900">PDF Report Extraction</div>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              High-accuracy extraction of biomarkers, values, units, and ranges directly from uploaded clinical lab PDFs.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center font-black text-xs">
              3
            </div>
            <div className="text-xs font-bold text-slate-900">Visual Verification</div>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              Human-in-the-loop review with side-by-side document previews, confidence scores, and immutable audit logging.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center font-black text-xs">
              4
            </div>
            <div className="text-xs font-bold text-slate-900">Traceable Intelligence</div>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              Automated drug-allergy conflict detection and plain-language summaries strictly bound to source data.
            </p>
          </div>
        </div>
      </div>

      {/* Core Safety & Medical Principles */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6 text-white border border-slate-700 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-400/30 text-emerald-400 flex items-center justify-center flex-shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-bold text-white">Strict Non-Diagnostic Commitment</div>
            <p className="text-xs text-slate-300 mt-1 max-w-xl">
              MedLens is an information organization and clinical intelligence tool. It does not provide medical advice,
              diagnosis, or treatment prescriptions. All AI summaries are plainly stated, source-referenced, and non-prescriptive.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          <div className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-[11px] text-slate-300">
            Zero Data Fabrication
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-[11px] text-slate-300">
            Immutable Audit Trail
          </div>
        </div>
      </div>
    </div>
  );
};
