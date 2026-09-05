import React from 'react';
import { ArrowDown, ArrowUp, Check, MinusCircle } from 'lucide-react';
import { FlagType } from '../types';

interface Props {
  flag: FlagType | string;
  referenceRange?: string | null;
  size?: 'sm' | 'md';
}

export const FlagBadge: React.FC<Props> = ({ flag, referenceRange, size = 'sm' }) => {
  const normalized = (flag || 'unavailable').toLowerCase();
  const sizeClasses = size === 'sm' ? 'text-[11px] py-0.5 px-2' : 'text-xs py-1 px-2.5';

  if (normalized === 'low') {
    return (
      <span
        title={referenceRange ? `Below source reference range: ${referenceRange}` : 'Below laboratory range'}
        className={`clinical-badge flag-low ${sizeClasses}`}
      >
        <ArrowDown className="w-3 h-3 text-amber-700 stroke-[2.5]" />
        <span>Low</span>
      </span>
    );
  }

  if (normalized === 'high') {
    return (
      <span
        title={referenceRange ? `Above source reference range: ${referenceRange}` : 'Above laboratory range'}
        className={`clinical-badge flag-high ${sizeClasses}`}
      >
        <ArrowUp className="w-3 h-3 text-rose-700 stroke-[2.5]" />
        <span>High</span>
      </span>
    );
  }

  if (normalized === 'normal') {
    return (
      <span
        title={referenceRange ? `Within source reference range: ${referenceRange}` : 'Within reference interval'}
        className={`clinical-badge flag-normal ${sizeClasses}`}
      >
        <Check className="w-3 h-3 text-emerald-700 stroke-[2.5]" />
        <span>Normal</span>
      </span>
    );
  }

  return (
    <span
      title="No reference range provided in the source report. Per safety rules, range is marked unavailable."
      className={`clinical-badge flag-unavail ${sizeClasses}`}
    >
      <MinusCircle className="w-3 h-3 text-slate-500" />
      <span>Range Unavailable</span>
    </span>
  );
};
