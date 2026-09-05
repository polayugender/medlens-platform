import React from 'react';
import { ShieldAlert } from 'lucide-react';

interface Props {
  compact?: boolean;
}

export const DisclaimerBanner: React.FC<Props> = ({ compact = false }) => {
  if (compact) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-50/90 border border-amber-300/80 rounded-lg text-xs text-amber-900">
        <ShieldAlert className="w-4 h-4 text-amber-600 flex-shrink-0" />
        <span>
          <strong>Clinical Intelligence Advisory:</strong> Organizational information tool only. Not a medical diagnosis or prescription. Consult a licensed physician.
        </span>
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden bg-gradient-to-r from-amber-50 via-amber-50/90 to-orange-50 border border-amber-300/90 rounded-xl p-4 shadow-sm mb-6">
      <div className="flex items-start gap-3.5">
        <div className="p-2 bg-amber-100/80 rounded-lg text-amber-700 flex-shrink-0 mt-0.5">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div className="text-sm leading-relaxed text-amber-950">
          <div className="flex items-center gap-2 font-semibold text-amber-900 mb-0.5">
            <span>Clinical Information Intelligence & Provenance System</span>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 bg-amber-200/80 text-amber-800 rounded">
              Non-Diagnostic Guardrail
            </span>
          </div>
          <p className="text-amber-900/90 text-xs sm:text-sm">
            MedLens synthesizes fragmented patient data and verifies source references into a unified timeline.
            <strong> It does not formulate medical diagnoses, clinical prognoses, or treatment recommendations.</strong> All reference ranges are transcribed directly from laboratory documents; never inferred or estimated. Always review with a licensed healthcare practitioner.
          </p>
        </div>
      </div>
    </div>
  );
};
