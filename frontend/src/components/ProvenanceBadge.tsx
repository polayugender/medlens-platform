import React from 'react';
import { UserCheck, Sparkles, CheckCircle2, Clock, Bot } from 'lucide-react';
import { ProvenanceSource } from '../types';

interface Props {
  source: ProvenanceSource | 'verified';
  verified?: boolean;
  verifiedBy?: string | null;
  size?: 'sm' | 'md';
}

export const ProvenanceBadge: React.FC<Props> = ({
  source,
  verified = false,
  verifiedBy,
  size = 'sm',
}) => {
  const sizeClasses = size === 'sm' ? 'text-[11px] py-0.5 px-2' : 'text-xs py-1 px-2.5';

  if (source === 'user_input') {
    return (
      <span
        title="Source: Patient or User Input (Direct intake entry)"
        className={`clinical-badge badge-user-input ${sizeClasses}`}
      >
        <UserCheck className="w-3 h-3 text-sky-600" />
        <span>User Input</span>
      </span>
    );
  }

  if (source === 'ai_generated') {
    return (
      <span
        title="Source: AI Plain-Language Summarizer (Constrained by Non-Diagnostic Prompts)"
        className={`clinical-badge badge-ai-generated ${sizeClasses}`}
      >
        <Sparkles className="w-3 h-3 text-purple-600" />
        <span>AI Generated</span>
      </span>
    );
  }

  if (verified || source === 'verified') {
    return (
      <span
        title={`Verified by: ${verifiedBy || 'User / Clinician'}`}
        className={`clinical-badge badge-verified ${sizeClasses}`}
      >
        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
        <span>Verified</span>
      </span>
    );
  }

  // AI Extracted but not yet verified
  return (
    <span
      title="Source: AI Extracted from uploaded document — Awaiting user review"
      className={`clinical-badge badge-ai-extracted ${sizeClasses}`}
    >
      <Clock className="w-3 h-3 text-amber-600" />
      <span>AI Extracted (Unverified)</span>
    </span>
  );
};
