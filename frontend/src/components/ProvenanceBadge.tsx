import React from 'react';
import { User, Sparkles, ShieldCheck } from 'lucide-react';
import { ProvenanceSource } from '../types/clinical';

interface Props {
  source: ProvenanceSource | 'user_input' | 'ai_extracted' | 'ai_generated' | 'clinician_edited' | string;
  confidence?: number | null;
  pageNumber?: number | null;
  verified?: boolean;
  verifiedBy?: string | null;
  verifiedAt?: string | null;
  size?: 'xs' | 'sm' | 'md';
}

/**
 * Field-Level Provenance Badge.
 * Explicitly tracks whether clinical data originates from:
 * 1. User Intake (Patient-Reported)
 * 2. AI Extraction (with confidence % and document page)
 * 3. Clinician Verification / Human Edit (with auditor identity)
 */
export const ProvenanceBadge: React.FC<Props> = ({
  source,
  confidence,
  pageNumber,
  verified,
  verifiedBy,
  verifiedAt,
  size = 'xs'
}) => {
  const norm = (source || '').toString().toLowerCase().trim();
  const sizeClasses = size === 'xs' ? 'text-[10px] px-1.5 py-0.5' : size === 'sm' ? 'text-xs px-2 py-1' : 'text-xs px-2.5 py-1 font-semibold';

  // 1. Clinician Verified / Edited
  if (norm === 'clinician_edited' || verified) {
    const title = `Human Verified by ${verifiedBy || 'Clinician'}${verifiedAt ? ` on ${new Date(verifiedAt).toLocaleDateString()}` : ''}.`;
    return (
      <span
        title={title}
        className={`inline-flex items-center gap-1 font-semibold rounded border border-emerald-500/30 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 ${sizeClasses}`}
      >
        <ShieldCheck className="w-3 h-3 text-emerald-600 dark:text-emerald-400 stroke-[2.5]" aria-hidden="true" />
        <span>Clinician-Verified</span>
      </span>
    );
  }

  // 2. User Intake
  if (norm === 'user_intake' || norm === 'user_input') {
    return (
      <span
        title="Directly provided by patient in clinical intake."
        className={`inline-flex items-center gap-1 font-semibold rounded border border-sky-500/30 bg-sky-50 dark:bg-sky-950/40 text-sky-700 dark:text-sky-300 ${sizeClasses}`}
      >
        <User className="w-3 h-3 text-sky-600 dark:text-sky-400" aria-hidden="true" />
        <span>Patient-Reported</span>
      </span>
    );
  }

  // 3. AI Extracted
  const confPercent = confidence !== undefined && confidence !== null ? `${Math.round(confidence > 1 ? confidence : confidence * 100)}%` : null;
  const pageLabel = pageNumber ? `p.${pageNumber}` : null;
  const metaDetail = [pageLabel, confPercent].filter(Boolean).join(' • ');

  return (
    <span
      title={`AI-extracted from source document${confPercent ? ` (${confPercent} confidence)` : ''}. Pending clinician sign-off.`}
      className={`inline-flex items-center gap-1 font-semibold rounded border border-indigo-500/30 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 ${sizeClasses}`}
    >
      <Sparkles className="w-3 h-3 text-indigo-600 dark:text-indigo-400" aria-hidden="true" />
      <span>AI-Extracted{metaDetail ? ` (${metaDetail})` : ''}</span>
    </span>
  );
};
