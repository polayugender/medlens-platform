import React from 'react';

interface Props {
  message: string;
  polite?: boolean;
}

/**
 * WCAG-compliant live region for assistive technologies.
 * Announces dynamic UI updates, verification status changes, and filter results to screen readers.
 */
export const AriaLiveRegion: React.FC<Props> = ({ message, polite = true }) => {
  return (
    <div
      role="status"
      aria-live={polite ? "polite" : "assertive"}
      aria-atomic="true"
      className="sr-only"
    >
      {message}
    </div>
  );
};
