import React, { useState } from 'react';
import {
  Sparkles,
  FileText,
  UserCheck,
  RefreshCw,
  Search,
  Download,
  AlertTriangle,
  ArrowRight,
  Filter,
  CheckCircle2,
  Calendar,
  Pill,
  HeartPulse,
  Printer,
  ChevronDown
} from 'lucide-react';
import {
  Patient,
  IntakeRecord,
  MedicalReport,
  ExtractedTest,
  Summary
} from '../types';
import { DisclaimerBanner } from '../components/DisclaimerBanner';
import { ProvenanceBadge } from '../components/ProvenanceBadge';
import { FlagBadge } from '../components/FlagBadge';
import { api } from '../api/client';

interface Props {
  patient: Patient;
  intake: IntakeRecord | null;
  reports: MedicalReport[];
  tests: ExtractedTest[];
  summary: Summary | null;
  onNavigateToTab: (tab: string) => void;
  onSummaryUpdated: (newSummary: Summary) => void;
}

export const PatientRecordView: React.FC<Props> = ({
  patient,
  intake,
  reports,
  tests,
  summary,
  onNavigateToTab,
  onSummaryUpdated,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [flagFilter, setFlagFilter] = useState<string>('all');
  const [regenerating, setRegenerating] = useState(false);
  const [exportMenuOpen, setExportMenuOpen] = useState(false);
  const [exportTypeLoading, setExportTypeLoading] = useState<'pdf' | 'json' | null>(null);

  const verifiedTests = tests.filter((t) => t.verified);
  const unverifiedTests = tests.filter((t) => !t.verified);

  // Filtered verified tests
  const filteredTests = verifiedTests.filter((t) => {
    const matchesSearch =
      t.test_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (t.unit && t.unit.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesFlag =
      flagFilter === 'all' ? true : t.flag.toLowerCase() === flagFilter.toLowerCase();
    return matchesSearch && matchesFlag;
  });

  const handleRegenerateSummary = async () => {
    setRegenerating(true);
    try {
      const updated = await api.generateSummary(patient.id);
      onSummaryUpdated(updated);
    } catch (err: any) {
      alert(`Summary generation failed: ${err.message}`);
    } finally {
      setRegenerating(false);
    }
  };

  const handleDownloadPDF = async () => {
    setExportTypeLoading('pdf');
    setExportMenuOpen(false);
    try {
      await api.downloadExportPDF(patient.id, patient.name);
    } catch (err: any) {
      alert(`PDF export failed: ${err.message}`);
    } finally {
      setExportTypeLoading(null);
    }
  };

  const handleDownloadJSON = async () => {
    setExportTypeLoading('json');
    setExportMenuOpen(false);
    try {
      await api.downloadExportJSON(patient.id, patient.name);
    } catch (err: any) {
      alert(`JSON export failed: ${err.message}`);
    } finally {
      setExportTypeLoading(null);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-6">
      {/* Non-Negotiable Principle #3: Persistent Disclaimer Banner */}
      <DisclaimerBanner />

      {/* Patient Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-clinical-700 to-sky-500 text-white flex items-center justify-center font-extrabold text-xl shadow-md">
            {patient.name
              .split(' ')
              .map((n) => n[0])
              .join('')}
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-black text-slate-900">{patient.name}</h1>
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-clinical-50 text-clinical-700 rounded-full border border-clinical-200">
                Patient ID: {patient.id.slice(0, 8)}
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-4 mt-1.5 text-xs text-slate-500 font-medium">
              <span>DOB: <strong>{patient.dob}</strong></span>
              <span>•</span>
              <span>Sex: <strong>{patient.sex}</strong></span>
              <span>•</span>
              <span>Age: <strong>{intake?.age ?? '—'} yrs</strong></span>
              <span>•</span>
              <span>Verified Tests: <strong className="text-emerald-700">{verifiedTests.length}</strong></span>
              {unverifiedTests.length > 0 && (
                <>
                  <span>•</span>
                  <span className="text-amber-700 font-semibold">
                    Awaiting Review: {unverifiedTests.length}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Quick action buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrint}
            className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print Chart</span>
          </button>

          {/* Export Record Dropdown */}
          <div className="relative">
            <button
              id="export-record-dropdown-btn"
              onClick={() => setExportMenuOpen(!exportMenuOpen)}
              disabled={exportTypeLoading !== null}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-clinical-50 hover:bg-clinical-100 text-clinical-700 border border-clinical-200 text-xs font-semibold rounded-lg transition-colors shadow-sm"
            >
              {exportTypeLoading ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Download className="w-3.5 h-3.5" />
              )}
              <span>
                {exportTypeLoading === 'pdf'
                  ? 'Generating PDF...'
                  : exportTypeLoading === 'json'
                  ? 'Preparing JSON...'
                  : 'Export Record'}
              </span>
              <ChevronDown className={`w-3.5 h-3.5 transition-transform ${exportMenuOpen ? 'rotate-180' : ''}`} />
            </button>

            {exportMenuOpen && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setExportMenuOpen(false)}
                />
                <div className="absolute right-0 mt-1.5 w-60 bg-white rounded-xl shadow-lg border border-slate-200 py-1.5 z-20 animate-in fade-in slide-in-from-top-1 duration-150">
                  <div className="px-3 py-1.5 border-b border-slate-100 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Export Clinical Profile
                  </div>
                  <button
                    id="download-pdf-btn"
                    onClick={handleDownloadPDF}
                    className="w-full text-left px-3 py-2.5 hover:bg-clinical-50 text-slate-700 hover:text-clinical-800 text-xs font-medium flex items-center gap-2.5 transition-colors"
                  >
                    <FileText className="w-4 h-4 text-red-500 shrink-0" />
                    <div>
                      <div className="font-semibold text-slate-800">Download PDF</div>
                      <div className="text-[10px] text-slate-400">Formatted clinical report with disclaimer & lab tables</div>
                    </div>
                  </button>
                  <button
                    id="download-json-btn"
                    onClick={handleDownloadJSON}
                    className="w-full text-left px-3 py-2.5 hover:bg-clinical-50 text-slate-700 hover:text-clinical-800 text-xs font-medium flex items-center gap-2.5 transition-colors"
                  >
                    <Download className="w-4 h-4 text-sky-600 shrink-0" />
                    <div>
                      <div className="font-semibold text-slate-800">Download JSON</div>
                      <div className="text-[10px] text-slate-400">Complete raw profile, intake, tests & audit logs</div>
                    </div>
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Unverified Alert Callout if any */}
      {unverifiedTests.length > 0 && (
        <div className="p-4 bg-sky-50 border border-sky-200 rounded-xl flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-sky-100 text-sky-700 rounded-lg">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-sky-950">
                {unverifiedTests.length} Laboratory Results Pending Human Verification
              </div>
              <p className="text-xs text-sky-800">
                Uploaded reports extracted new values. Confirm them in the verification screen before committing.
              </p>
            </div>
          </div>
          <button
            onClick={() => onNavigateToTab('verify')}
            className="inline-flex items-center gap-1 px-3 py-1.5 bg-clinical-600 hover:bg-clinical-700 text-white text-xs font-semibold rounded-lg shadow-sm whitespace-nowrap"
          >
            <span>Review Now</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Section 1: Self-Reported Health Profile (Source: user_input) */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <HeartPulse className="w-4 h-4 text-clinical-600" />
            <h2 className="text-sm font-bold text-slate-900">Self-Reported Health Profile</h2>
            <ProvenanceBadge source="user_input" />
          </div>
          <button
            onClick={() => onNavigateToTab('intake')}
            className="text-xs text-clinical-600 hover:text-clinical-700 font-semibold"
          >
            Edit Intake (v{intake?.version || 1})
          </button>
        </div>

        {intake ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
            {/* Symptoms */}
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/60">
              <div className="font-bold text-slate-600 uppercase tracking-wider text-[10px] mb-1.5">
                Reported Symptoms
              </div>
              <div className="flex flex-wrap gap-1">
                {intake.symptoms && intake.symptoms.length > 0 ? (
                  intake.symptoms.map((s, idx) => (
                    <span key={idx} className="px-2 py-0.5 bg-white border rounded text-slate-800 font-medium">
                      {s}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-400 italic">None reported</span>
                )}
              </div>
            </div>

            {/* Conditions */}
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/60">
              <div className="font-bold text-slate-600 uppercase tracking-wider text-[10px] mb-1.5">
                Existing Conditions
              </div>
              <div className="flex flex-wrap gap-1">
                {intake.existing_conditions && intake.existing_conditions.length > 0 ? (
                  intake.existing_conditions.map((c, idx) => (
                    <span key={idx} className="px-2 py-0.5 bg-sky-50 text-sky-800 border border-sky-200 rounded font-medium">
                      {c}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-400 italic">None reported</span>
                )}
              </div>
            </div>

            {/* Allergies */}
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/60">
              <div className="font-bold text-slate-600 uppercase tracking-wider text-[10px] mb-1.5">
                Documented Allergies
              </div>
              <div className="flex flex-wrap gap-1">
                {intake.allergies && intake.allergies.length > 0 ? (
                  intake.allergies.map((a, idx) => (
                    <span key={idx} className="px-2 py-0.5 bg-amber-50 text-amber-900 border border-amber-300 rounded font-bold">
                      {a}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-400 italic">No known allergies</span>
                )}
              </div>
            </div>

            {/* Medications */}
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/60">
              <div className="font-bold text-slate-600 uppercase tracking-wider text-[10px] mb-1.5">
                Active Medications
              </div>
              <div className="space-y-1">
                {intake.medications && intake.medications.length > 0 ? (
                  intake.medications.map((m, idx) => (
                    <div key={idx} className="text-slate-800 font-medium">
                      • <strong>{m.name}</strong> {m.dosage ? `(${m.dosage})` : ''}
                    </div>
                  ))
                ) : (
                  <span className="text-slate-400 italic">No active medications</span>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-xs text-slate-400 py-3">No intake profile recorded. Click "Edit Intake" to complete.</div>
        )}
      </div>

      {/* Section 2: AI Plain-Language Clinical Summary (Source: ai_generated) */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <Sparkles className="w-5 h-5 text-purple-600" />
            <h2 className="text-sm font-bold text-slate-900">
              AI Plain-Language Clinical Information Summary
            </h2>
            <ProvenanceBadge source="ai_generated" />
          </div>

          <div className="flex items-center gap-2">
            {summary && (
              <span className="text-xs text-slate-400 font-mono">
                v{summary.version} ({new Date(summary.generated_at).toLocaleDateString()})
              </span>
            )}
            <button
              onClick={handleRegenerateSummary}
              disabled={regenerating}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 rounded-lg text-xs font-semibold transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${regenerating ? 'animate-spin' : ''}`} />
              <span>{regenerating ? 'Synthesizing...' : 'Regenerate Summary'}</span>
            </button>
          </div>
        </div>

        {summary ? (
          <div className="prose prose-sm max-w-none text-slate-700 space-y-3 leading-relaxed text-xs sm:text-sm">
            <div className="bg-slate-50/80 p-4 rounded-xl border border-slate-200/70 whitespace-pre-line">
              {summary.summary_text}
            </div>
            <div className="text-[11px] text-slate-400 italic pt-1">
              * Synthesized from verified reports: [{summary.based_on_report_ids.join(', ')}] & Intake v{summary.based_on_intake_version}
            </div>
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-slate-400">
            No summary generated yet. Click "Regenerate Summary" to synthesize patient data.
          </div>
        )}
      </div>

      {/* Section 3: Structured Diagnostic Lab Results Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-50">
          <div>
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-clinical-600" />
              <h3 className="text-sm font-bold text-slate-900">
                Verified Diagnostic Test Results ({verifiedTests.length})
              </h3>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Structured biomarker values transcribed from verified laboratory reports with deterministic flags.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            {/* Search */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search tests..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 pr-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-clinical-500 w-36 sm:w-44"
              />
            </div>

            {/* Flag Filter */}
            <select
              value={flagFilter}
              onChange={(e) => setFlagFilter(e.target.value)}
              className="text-xs px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg text-slate-700 font-medium focus:outline-none"
            >
              <option value="all">All Flags</option>
              <option value="high">High Only</option>
              <option value="low">Low Only</option>
              <option value="normal">Normal Only</option>
              <option value="unavailable">Range Unavailable</option>
            </select>
          </div>
        </div>

        {filteredTests.length === 0 ? (
          <div className="p-10 text-center text-xs text-slate-400">
            {verifiedTests.length === 0
              ? 'No verified laboratory tests yet. Upload a report and verify tests to populate this table.'
              : 'No tests match your filter criteria.'}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100/70 text-slate-500 border-b border-slate-200 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="py-3 px-4">Test Marker</th>
                  <th className="py-3 px-4">Observed Value</th>
                  <th className="py-3 px-4">Unit</th>
                  <th className="py-3 px-4">Source Reference Range</th>
                  <th className="py-3 px-4">Computed Flag</th>
                  <th className="py-3 px-4">Provenance</th>
                  <th className="py-3 px-4">Verified By</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {filteredTests.map((test) => (
                  <tr key={test.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4 font-bold text-slate-900">{test.test_name}</td>
                    <td className="py-3 px-4 font-mono font-bold text-slate-900">
                      <span className="bg-slate-100 px-2 py-0.5 rounded">{test.value}</span>
                    </td>
                    <td className="py-3 px-4 text-slate-500">{test.unit || '—'}</td>
                    <td className="py-3 px-4">
                      {test.reference_range_raw ? (
                        <span className="text-slate-700">{test.reference_range_raw}</span>
                      ) : (
                        <span className="text-slate-400 italic">range_unavailable</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <FlagBadge flag={test.flag} referenceRange={test.reference_range_raw} />
                    </td>
                    <td className="py-3 px-4">
                      <ProvenanceBadge
                        source="verified"
                        verified={test.verified}
                        verifiedBy={test.verified_by}
                      />
                    </td>
                    <td className="py-3 px-4 text-[11px] text-slate-500">
                      {test.verified_by || 'User'} ({new Date(test.verified_at || test.updated_at).toLocaleDateString()})
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
