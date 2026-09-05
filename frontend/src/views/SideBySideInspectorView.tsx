import React, { useState, useEffect } from 'react';
import {
  SplitSquareVertical,
  FileText,
  Search,
  ExternalLink,
  Eye,
  CheckCircle2,
  Info
} from 'lucide-react';
import { MedicalReport, ExtractedTest } from '../types';
import { FlagBadge } from '../components/FlagBadge';
import { ProvenanceBadge } from '../components/ProvenanceBadge';
import { api } from '../api/client';

interface Props {
  patientId: string;
  reports: MedicalReport[];
}

export const SideBySideInspectorView: React.FC<Props> = ({ patientId, reports }) => {
  const [selectedReportId, setSelectedReportId] = useState<string>(
    reports[0]?.id || ''
  );
  const [reportDetails, setReportDetails] = useState<{
    report: MedicalReport;
    tests: ExtractedTest[];
    previews: string[];
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [hoveredTestId, setHoveredTestId] = useState<string | null>(null);
  const [activeSnippet, setActiveSnippet] = useState<string | null>(null);

  useEffect(() => {
    if (reports.length > 0 && !selectedReportId) {
      setSelectedReportId(reports[0].id);
    }
  }, [reports]);

  useEffect(() => {
    if (!selectedReportId) return;
    setLoading(true);
    api
      .getReportDetails(selectedReportId)
      .then((data) => {
        setReportDetails(data);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [selectedReportId]);

  const activeReport = reportDetails?.report;
  const tests = reportDetails?.tests || [];
  const previews = reportDetails?.previews || [];

  return (
    <div className="space-y-4">
      {/* Header & Report Picker */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <SplitSquareVertical className="w-5 h-5 text-clinical-600" />
            <h2 className="text-base font-bold text-slate-900">Side-by-Side Source Inspector</h2>
            <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-purple-100 text-purple-800 rounded">
              Differentiator
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Hover over any extracted test on the right to trace its verbatim citation snippet directly in the original laboratory report.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-600">Select Report:</span>
          <select
            value={selectedReportId}
            onChange={(e) => setSelectedReportId(e.target.value)}
            className="text-xs px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 font-semibold focus:outline-none focus:ring-2 focus:ring-clinical-500"
          >
            {reports.map((r) => (
              <option key={r.id} value={r.id}>
                {r.original_filename} ({r.report_date || 'No Date'})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading side-by-side document views...</div>
      ) : !activeReport ? (
        <div className="p-12 text-center text-xs text-slate-400">Please select a report to inspect.</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
          {/* Left Pane: Document Viewer / Preview */}
          <div className="lg:col-span-6 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col h-[740px]">
            <div className="p-3 bg-slate-100 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-slate-600" />
                <span className="text-xs font-bold text-slate-800 truncate max-w-[240px]">
                  {activeReport.original_filename}
                </span>
                <span className="text-[10px] px-1.5 py-0.5 bg-slate-200 text-slate-700 rounded font-mono">
                  {activeReport.page_count} pg
                </span>
              </div>
              <a
                href={activeReport.file_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-[11px] font-semibold text-clinical-600 hover:text-clinical-700"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                <span>Open Full PDF</span>
              </a>
            </div>

            {/* Active Highlight Snippet Callout */}
            {activeSnippet ? (
              <div className="px-4 py-2.5 bg-amber-100 border-b border-amber-300 text-amber-950 text-xs flex items-start gap-2 animate-fadeIn">
                <Search className="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="text-[10px] uppercase font-extrabold tracking-wider text-amber-800">
                    Source Document Highlight:
                  </div>
                  <div className="font-mono font-semibold text-xs mt-0.5">"{activeSnippet}"</div>
                </div>
              </div>
            ) : (
              <div className="px-4 py-2 bg-slate-50 border-b border-slate-200 text-slate-500 text-[11px] flex items-center gap-2">
                <Info className="w-3.5 h-3.5" />
                <span>Hover over any test marker on the right to inspect its exact source citation</span>
              </div>
            )}

            {/* Document Content View */}
            <div className="flex-1 overflow-y-auto p-4 bg-slate-200/50 flex flex-col items-center gap-4">
              {previews.length > 0 ? (
                previews.map((prevUrl, pIdx) => (
                  <div
                    key={pIdx}
                    className="relative bg-white shadow-md border border-slate-300 rounded max-w-full overflow-hidden"
                  >
                    <img
                      src={prevUrl}
                      alt={`Page ${pIdx + 1}`}
                      className="w-full object-contain pointer-events-none"
                    />
                    <div className="absolute bottom-2 right-2 px-2 py-0.5 bg-slate-900/70 text-white text-[10px] rounded backdrop-blur-sm">
                      Page {pIdx + 1}
                    </div>
                  </div>
                ))
              ) : (
                <div className="w-full h-full bg-white p-6 rounded-lg font-mono text-xs text-slate-700 overflow-auto whitespace-pre-wrap leading-relaxed shadow-sm">
                  {activeReport.raw_text}
                </div>
              )}
            </div>
          </div>

          {/* Right Pane: Structured Extraction Table */}
          <div className="lg:col-span-6 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col h-[740px]">
            <div className="p-3 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Extracted Structured Markers ({tests.length})
                </h3>
              </div>
              <span className="text-[11px] text-slate-500 font-medium">
                Linked by snippet quote
              </span>
            </div>

            <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
              {tests.map((t) => {
                const isHovered = hoveredTestId === t.id;

                return (
                  <div
                    key={t.id}
                    onMouseEnter={() => {
                      setHoveredTestId(t.id);
                      setActiveSnippet(t.raw_snippet || `${t.test_name}: ${t.value}`);
                    }}
                    onMouseLeave={() => {
                      setHoveredTestId(null);
                      setActiveSnippet(null);
                    }}
                    className={`p-3.5 transition-all cursor-pointer ${
                      isHovered
                        ? 'bg-amber-50/90 border-l-4 border-l-amber-500 pl-4 shadow-sm'
                        : 'hover:bg-slate-50 border-l-4 border-l-transparent'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold text-slate-900">{t.test_name}</span>
                          <FlagBadge flag={t.flag} referenceRange={t.reference_range_raw} />
                        </div>
                        <div className="flex items-center gap-3 mt-1 text-xs text-slate-600">
                          <span>
                            Value:{' '}
                            <strong className="font-mono text-slate-900 bg-slate-100 px-1.5 py-0.5 rounded">
                              {t.value} {t.unit || ''}
                            </strong>
                          </span>
                          <span>
                            Range:{' '}
                            <span className="text-slate-700 font-medium">
                              {t.reference_range_raw || 'unavailable'}
                            </span>
                          </span>
                        </div>
                      </div>

                      <div className="flex flex-col items-end gap-1">
                        <ProvenanceBadge
                          source="verified"
                          verified={t.verified}
                          verifiedBy={t.verified_by}
                        />
                        <span className="text-[10px] text-slate-400 font-mono">
                          Conf: {Math.round(t.confidence_score * 100)}%
                        </span>
                      </div>
                    </div>

                    {/* Verbatim quote snippet */}
                    <div
                      className={`mt-2.5 p-2 rounded text-[11px] font-mono leading-relaxed border transition-colors ${
                        isHovered
                          ? 'bg-amber-100/90 text-amber-950 border-amber-300 font-semibold'
                          : 'bg-slate-50 text-slate-500 border-slate-200/80'
                      }`}
                    >
                      <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">
                        Exact Document Snippet:
                      </span>
                      "{t.raw_snippet || `${t.test_name} ${t.value} ${t.unit || ''}`}"
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
