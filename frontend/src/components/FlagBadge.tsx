import React from 'react';
import { ArrowDown, ArrowUp, Check, AlertTriangle, HelpCircle } from 'lucide-react';
import { FlagType } from '../types';
import { LabFlag } from '../types/clinical';

interface Props {
  flag: FlagType | LabFlag | string;
  referenceRange?: string | null;
  testName?: string;
  value?: string | number | null;
  size?: 'sm' | 'md';
}

/**
 * WCAG 1.4.1 Compliant Clinical Flag Badge.
 * NEVER relies on color alone to convey clinical status:
 * - Employs distinct geometric glyphs: ▲ (High), ▼ (Low), ● (Normal), ◆ (Abnormal), ⭘ (Range Not Provided)
 * - Employs distinct SVG vector icons
 * - Employs explicit bold uppercase text labels
 * - Includes ARIA role="status" and hidden screen-reader descriptive strings
 */
export const FlagBadge: React.FC<Props> = ({
  flag,
  referenceRange,
  testName,
  value,
  size = 'sm',
}) => {
  const normalized = (flag || 'RANGE_NOT_PROVIDED').toString().toLowerCase().trim();
  const sizeClasses = size === 'sm' ? 'text-[11px] py-0.5 px-2' : 'text-xs py-1 px-2.5';
  const valContext = value !== undefined && value !== null ? ` (Value: ${value})` : '';

  // HIGH
  if (normalized === 'high') {
    const srDescription = `High flag${testName ? ` for ${testName}` : ''}${valContext}. Result exceeds laboratory reference interval${referenceRange ? `: ${referenceRange}` : ''}.`;
    return (
      <span
        role="status"
        aria-label={srDescription}
        title={referenceRange ? `Above reference range: ${referenceRange}` : 'Above laboratory reference interval'}
        className={`clinical-badge flag-high ${sizeClasses} inline-flex items-center gap-1.5 font-bold rounded-md border border-rose-500/40 bg-rose-50 dark:bg-rose-950/40 text-rose-800 dark:text-rose-200 transition-all hover:scale-105`}
      >
        <span aria-hidden="true" className="text-[10px] leading-none font-black text-rose-700 dark:text-rose-400">▲</span>
        <ArrowUp className="w-3 h-3 text-rose-700 dark:text-rose-400 stroke-[2.5]" aria-hidden="true" />
        <span>HIGH</span>
        <span className="sr-only">{srDescription}</span>
      </span>
    );
  }

  // LOW
  if (normalized === 'low') {
    const srDescription = `Low flag${testName ? ` for ${testName}` : ''}${valContext}. Result below laboratory reference interval${referenceRange ? `: ${referenceRange}` : ''}.`;
    return (
      <span
        role="status"
        aria-label={srDescription}
        title={referenceRange ? `Below reference range: ${referenceRange}` : 'Below laboratory reference interval'}
        className={`clinical-badge flag-low ${sizeClasses} inline-flex items-center gap-1.5 font-bold rounded-md border border-amber-500/40 bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-200 transition-all hover:scale-105`}
      >
        <span aria-hidden="true" className="text-[10px] leading-none font-black text-amber-700 dark:text-amber-400">▼</span>
        <ArrowDown className="w-3 h-3 text-amber-700 dark:text-amber-400 stroke-[2.5]" aria-hidden="true" />
        <span>LOW</span>
        <span className="sr-only">{srDescription}</span>
      </span>
    );
  }

  // NORMAL
  if (normalized === 'normal') {
    const srDescription = `Normal result${testName ? ` for ${testName}` : ''}${valContext}. Within laboratory reference interval${referenceRange ? `: ${referenceRange}` : ''}.`;
    return (
      <span
        role="status"
        aria-label={srDescription}
        title={referenceRange ? `Within reference range: ${referenceRange}` : 'Within reference interval'}
        className={`clinical-badge flag-normal ${sizeClasses} inline-flex items-center gap-1.5 font-bold rounded-md border border-emerald-500/40 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-200 transition-all hover:scale-105`}
      >
        <span aria-hidden="true" className="text-[10px] leading-none font-black text-emerald-700 dark:text-emerald-400">●</span>
        <Check className="w-3 h-3 text-emerald-700 dark:text-emerald-400 stroke-[2.5]" aria-hidden="true" />
        <span>NORMAL</span>
        <span className="sr-only">{srDescription}</span>
      </span>
    );
  }

  // ABNORMAL QUALITATIVE (e.g. Trace, Reactive, Positive)
  if (normalized === 'abnormal_qualitative' || normalized === 'abnormal') {
    const srDescription = `Abnormal qualitative result${testName ? ` for ${testName}` : ''}${valContext}. Requires clinical review.`;
    return (
      <span
        role="status"
        aria-label={srDescription}
        title="Abnormal qualitative finding (e.g., Trace, Positive, Reactive)"
        className={`clinical-badge flag-abnormal ${sizeClasses} inline-flex items-center gap-1.5 font-bold rounded-md border border-purple-500/40 bg-purple-50 dark:bg-purple-950/40 text-purple-800 dark:text-purple-200 transition-all hover:scale-105`}
      >
        <span aria-hidden="true" className="text-[10px] leading-none font-black text-purple-700 dark:text-purple-400">◆</span>
        <AlertTriangle className="w-3 h-3 text-purple-700 dark:text-purple-400 stroke-[2.5]" aria-hidden="true" />
        <span>ABNORMAL</span>
        <span className="sr-only">{srDescription}</span>
      </span>
    );
  }

  // RANGE NOT PROVIDED (or unavailable)
  const unavailDescription = `Range not provided by testing facility${testName ? ` for ${testName}` : ''}${valContext}. Reference interval was not printed in the source document.`;
  return (
    <span
      role="status"
      aria-label={unavailDescription}
      title="No reference range was specified in the source laboratory report. Range was not inferred to prevent AI hallucination."
      className={`clinical-badge flag-unavail ${sizeClasses} inline-flex items-center gap-1.5 font-bold rounded-md border border-slate-400/40 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 transition-all hover:scale-105`}
    >
      <span aria-hidden="true" className="text-[10px] leading-none font-black text-slate-500">⭘</span>
      <HelpCircle className="w-3 h-3 text-slate-500 stroke-[2.2]" aria-hidden="true" />
      <span>RANGE NOT PROVIDED</span>
      <span className="sr-only">{unavailDescription}</span>
    </span>
  );
};
