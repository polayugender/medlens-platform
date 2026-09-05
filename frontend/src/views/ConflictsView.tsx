import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  ShieldAlert,
  HelpCircle,
  CheckCircle2,
  ArrowRight,
  Info,
  RefreshCw
} from 'lucide-react';
import { ClinicalConflict } from '../types';
import { api } from '../api/client';

interface Props {
  patientId: string;
  onNavigateToVerify: () => void;
  onNavigateToIntake: () => void;
}

export const ConflictsView: React.FC<Props> = ({
  patientId,
  onNavigateToVerify,
  onNavigateToIntake,
}) => {
  const [conflicts, setConflicts] = useState<ClinicalConflict[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchConflicts = async () => {
    setLoading(true);
    try {
      const res = await api.getConflicts(patientId);
      setConflicts(res.conflicts || []);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConflicts();
  }, [patientId]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <h2 className="text-lg font-bold text-slate-900">
              Cross-Source Inconsistency & Safety Checks
            </h2>
            <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-purple-100 text-purple-800 rounded">
              Differentiator
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Automated cross-checking comparing patient-reported intake (allergies, symptoms, medications) with uploaded diagnostic lab reports.
          </p>
        </div>

        <button
          onClick={fetchConflicts}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Re-scan Records</span>
        </button>
      </div>

      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Scanning records for clinical contradictions...</div>
      ) : conflicts.length === 0 ? (
        <div className="bg-white p-12 text-center rounded-xl border border-slate-200 shadow-sm space-y-2">
          <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto" />
          <h3 className="text-sm font-bold text-slate-800">No Clinical Contradictions Found</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Reported medications do not conflict with documented allergies, and all active laboratory values have valid source references.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {conflicts.map((c) => {
            const isCritical = c.severity === 'critical';
            const isWarning = c.severity === 'warning';

            return (
              <div
                key={c.id}
                className={`p-5 rounded-xl border transition-all ${
                  isCritical
                    ? 'bg-rose-50/70 border-rose-300 text-rose-950'
                    : isWarning
                    ? 'bg-amber-50/70 border-amber-300 text-amber-950'
                    : 'bg-sky-50/70 border-sky-300 text-sky-950'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <div
                      className={`p-2 rounded-lg mt-0.5 ${
                        isCritical
                          ? 'bg-rose-100 text-rose-700'
                          : isWarning
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-sky-100 text-sky-700'
                      }`}
                    >
                      {isCritical ? (
                        <ShieldAlert className="w-5 h-5" />
                      ) : isWarning ? (
                        <AlertTriangle className="w-5 h-5" />
                      ) : (
                        <Info className="w-5 h-5" />
                      )}
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] uppercase font-extrabold tracking-wider px-2 py-0.5 rounded bg-white/80 border">
                          {c.category}
                        </span>
                        <h3 className="text-sm font-bold">{c.title}</h3>
                      </div>
                      <p className="text-xs leading-relaxed opacity-90">{c.description}</p>

                      <div className="flex flex-wrap items-center gap-4 pt-2 text-[11px] font-medium opacity-80">
                        <span>
                          Source A: <strong>{c.source_a}</strong>
                        </span>
                        <span>•</span>
                        <span>
                          Source B: <strong>{c.source_b}</strong>
                        </span>
                      </div>

                      <div className="mt-3 p-2.5 bg-white/90 rounded-lg border border-slate-200/80 text-xs text-slate-800">
                        <strong className="text-slate-900">Recommended Action:</strong> {c.action_needed}
                      </div>
                    </div>
                  </div>

                  {/* Context button */}
                  <div className="self-end sm:self-center">
                    {c.category === 'Allergy Contradiction' ? (
                      <button
                        onClick={onNavigateToIntake}
                        className="inline-flex items-center gap-1 px-3 py-1.5 bg-white hover:bg-slate-100 text-slate-800 text-xs font-semibold rounded-lg shadow-sm border border-slate-200 transition-colors"
                      >
                        <span>Review Intake</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    ) : (
                      <button
                        onClick={onNavigateToVerify}
                        className="inline-flex items-center gap-1 px-3 py-1.5 bg-white hover:bg-slate-100 text-slate-800 text-xs font-semibold rounded-lg shadow-sm border border-slate-200 transition-colors"
                      >
                        <span>Open Verification</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
