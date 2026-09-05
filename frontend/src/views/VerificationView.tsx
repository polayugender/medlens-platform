import React, { useState, useEffect } from 'react';
import {
  CheckCircle2,
  AlertCircle,
  FileSearch,
  Check,
  Edit2,
  Trash2,
  ShieldCheck,
  Sparkles,
  Info
} from 'lucide-react';
import { ExtractedTest, MedicalReport } from '../types';
import { FlagBadge } from '../components/FlagBadge';
import { ProvenanceBadge } from '../components/ProvenanceBadge';
import { AriaLiveRegion } from '../components/AriaLiveRegion';
import { api } from '../api/client';

interface Props {
  patientId: string;
  reports: MedicalReport[];
  onVerificationComplete: () => void;
}

export const VerificationView: React.FC<Props> = ({
  patientId,
  reports,
  onVerificationComplete,
}) => {
  const [tests, setTests] = useState<ExtractedTest[]>([]);
  const [selectedReportId, setSelectedReportId] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<Partial<ExtractedTest>>({});
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const fetchTests = async () => {
    setLoading(true);
    try {
      const filterReport = selectedReportId !== 'all' ? selectedReportId : undefined;
      const allTests = await api.getTests(patientId, { report_id: filterReport });
      setTests(allTests);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTests();
  }, [patientId, selectedReportId]);

  const unverifiedTests = tests.filter((t) => !t.verified);
  const verifiedTests = tests.filter((t) => t.verified);

  const startEditing = (test: ExtractedTest) => {
    setEditingId(test.id);
    setEditForm({
      test_name: test.test_name,
      value: test.value,
      unit: test.unit || '',
      reference_range_raw: test.reference_range_raw || '',
    });
  };

  const saveEdit = async (testId: string) => {
    try {
      const updated = await api.updateTest(testId, {
        test_name: editForm.test_name,
        value: editForm.value,
        unit: editForm.unit || undefined,
        reference_range_raw: editForm.reference_range_raw || undefined,
      });
      setTests((prev) => prev.map((t) => (t.id === testId ? updated : t)));
      setEditingId(null);
      setStatusMessage('Test details updated successfully.');
      setTimeout(() => setStatusMessage(null), 3000);
    } catch (err: any) {
      alert(`Update failed: ${err.message}`);
    }
  };

  const verifySingle = async (test: ExtractedTest) => {
    try {
      const res = await api.verifyBatch(patientId, [
        {
          id: test.id,
          test_name: test.test_name,
          value: test.value,
          unit: test.unit,
          reference_range_raw: test.reference_range_raw,
        },
      ]);
      setTests((prev) =>
        prev.map((t) => (t.id === test.id ? res[0] || { ...t, verified: true } : t))
      );
      onVerificationComplete();
    } catch (err: any) {
      alert(`Verification failed: ${err.message}`);
    }
  };

  const verifyAllPending = async () => {
    if (unverifiedTests.length === 0) return;
    setVerifying(true);
    try {
      const payload = unverifiedTests.map((t) => ({
        id: t.id,
        test_name: t.test_name,
        value: t.value,
        value_numeric: t.value_numeric,
        unit: t.unit,
        reference_range_raw: t.reference_range_raw,
      }));
      await api.verifyBatch(patientId, payload);
      await fetchTests();
      onVerificationComplete();
      setStatusMessage(`Successfully verified and committed ${payload.length} test records!`);
      setTimeout(() => setStatusMessage(null), 4000);
    } catch (err: any) {
      alert(`Batch verification failed: ${err.message}`);
    } finally {
      setVerifying(false);
    }
  };

  const deleteTestItem = async (testId: string) => {
    if (!confirm('Are you sure you want to remove this extracted test entry?')) return;
    try {
      await api.deleteTest(testId);
      setTests((prev) => prev.filter((t) => t.id !== testId));
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-lg font-bold text-slate-900">Human-in-the-Loop Verification</h2>
            <span className="px-2 py-0.5 text-xs font-semibold bg-sky-100 text-sky-800 rounded-full">
              Phase 1 Core
            </span>
          </div>
          <p className="text-xs text-slate-500">
            Per Clinical Safety Principle #4, every AI-extracted laboratory marker must be verified by a human before entering the official clinical record.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Report Filter */}
          <select
            value={selectedReportId}
            onChange={(e) => setSelectedReportId(e.target.value)}
            className="text-xs px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-clinical-500"
          >
            <option value="all">All Uploaded Reports</option>
            {reports.map((r) => (
              <option key={r.id} value={r.id}>
                {r.original_filename} ({r.report_date || 'No Date'})
              </option>
            ))}
          </select>

          {/* Batch Verify Button */}
          {unverifiedTests.length > 0 && (
            <button
              id="verify-all-btn"
              data-testid="verify-all-btn"
              onClick={verifyAllPending}
              disabled={verifying}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white text-xs font-semibold rounded-lg shadow-sm transition-all disabled:opacity-50"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>{verifying ? 'Verifying...' : `Verify All Pending (${unverifiedTests.length})`}</span>
            </button>
          )}
        </div>
      </div>

      <AriaLiveRegion message={statusMessage || (unverifiedTests.length > 0 ? `${unverifiedTests.length} laboratory tests pending verification.` : 'All laboratory tests are verified.')} />

      {statusMessage && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>{statusMessage}</span>
        </div>
      )}

      {/* Unverified Queue */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-200 bg-amber-50/50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse" />
            <h3 className="text-sm font-bold text-slate-900">
              Pending Review & Verification ({unverifiedTests.length})
            </h3>
          </div>
          <span className="text-xs text-amber-800 font-medium">
            Review values against source raw snippets below
          </span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading extracted records...</div>
        ) : unverifiedTests.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500 bg-slate-50/50">
            <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2 opacity-80" />
            <p className="font-semibold text-slate-700">All extracted tests have been verified!</p>
            <p className="text-slate-400 mt-1">No unverified records are pending for this filter.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="py-3 px-4">Test Marker</th>
                  <th className="py-3 px-4">Observed Value</th>
                  <th className="py-3 px-4">Unit</th>
                  <th className="py-3 px-4">Source Reference Range</th>
                  <th className="py-3 px-4">Computed Flag</th>
                  <th className="py-3 px-4">AI Confidence</th>
                  <th className="py-3 px-4">Source Snippet (Audit Quote)</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {unverifiedTests.map((t) => {
                  const isEditing = editingId === t.id;

                  return (
                    <tr key={t.id} className="hover:bg-slate-50/80 transition-colors">
                      {/* Name */}
                      <td className="py-3 px-4">
                        {isEditing ? (
                          <input
                            type="text"
                            value={editForm.test_name}
                            onChange={(e) => setEditForm({ ...editForm, test_name: e.target.value })}
                            className="w-full px-2 py-1 border border-slate-300 rounded text-xs"
                          />
                        ) : (
                          <span className="font-semibold text-slate-900">{t.test_name}</span>
                        )}
                      </td>

                      {/* Value */}
                      <td className="py-3 px-4">
                        {isEditing ? (
                          <input
                            id={`edit-value-input-${t.id}`}
                            type="text"
                            value={editForm.value}
                            onChange={(e) => setEditForm({ ...editForm, value: e.target.value })}
                            className="w-20 px-2 py-1 border border-slate-300 rounded text-xs font-mono"
                          />
                        ) : (
                          <span className="font-mono font-semibold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">
                            {t.value}
                          </span>
                        )}
                      </td>

                      {/* Unit */}
                      <td className="py-3 px-4 text-slate-500">
                        {isEditing ? (
                          <input
                            type="text"
                            value={editForm.unit || ''}
                            onChange={(e) => setEditForm({ ...editForm, unit: e.target.value })}
                            className="w-16 px-2 py-1 border border-slate-300 rounded text-xs"
                          />
                        ) : (
                          t.unit || '—'
                        )}
                      </td>

                      {/* Reference Range */}
                      <td className="py-3 px-4">
                        {isEditing ? (
                          <input
                            type="text"
                            value={editForm.reference_range_raw || ''}
                            placeholder="e.g. 70 - 99 or < 200"
                            onChange={(e) =>
                              setEditForm({ ...editForm, reference_range_raw: e.target.value })
                            }
                            className="w-28 px-2 py-1 border border-slate-300 rounded text-xs"
                          />
                        ) : (
                          <span className="text-slate-600">
                            {t.reference_range_raw || (
                              <span className="text-slate-400 italic">range_unavailable</span>
                            )}
                          </span>
                        )}
                      </td>

                      {/* Computed Flag */}
                      <td className="py-3 px-4">
                        <FlagBadge flag={t.flag} referenceRange={t.reference_range_raw} />
                      </td>

                      {/* AI Confidence Score */}
                      <td className="py-3 px-4">
                        <span
                          title={`Deterministic LLM JSON schema confidence: ${Math.round((t.confidence_score ?? 1) * 100)}%`}
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            (t.confidence_score ?? 1) >= 0.9
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : (t.confidence_score ?? 1) >= 0.75
                              ? 'bg-sky-50 text-sky-700 border border-sky-200'
                              : 'bg-amber-50 text-amber-700 border border-amber-200'
                          }`}
                        >
                          <Sparkles className="w-2.5 h-2.5" />
                          {Math.round((t.confidence_score ?? 1) * 100)}%
                        </span>
                      </td>

                      {/* Raw Snippet Audit Citation */}
                      <td className="py-3 px-4 max-w-xs">
                        <div
                          title={t.raw_snippet || ''}
                          className="font-mono text-[11px] text-slate-500 truncate bg-slate-50 p-1 rounded border border-slate-200/60"
                        >
                          "{t.raw_snippet || 'Snippet not logged'}"
                        </div>
                      </td>

                      {/* Action buttons */}
                      <td className="py-3 px-4 text-right whitespace-nowrap">
                        {isEditing ? (
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              id={`save-test-${t.id}`}
                              data-testid="save-test-btn"
                              onClick={() => saveEdit(t.id)}
                              className="p-1 text-emerald-700 bg-emerald-100 hover:bg-emerald-200 rounded"
                              title="Save Changes"
                            >
                              <Check className="w-3.5 h-3.5" />
                            </button>
                            <button
                              id={`cancel-test-${t.id}`}
                              onClick={() => setEditingId(null)}
                              className="px-2 py-1 text-slate-500 hover:bg-slate-100 rounded text-[11px]"
                            >
                              Cancel
                            </button>
                          </div>
                        ) : (
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              id={`verify-test-${t.id}`}
                              data-testid="verify-single-btn"
                              onClick={() => verifySingle(t)}
                              className="inline-flex items-center gap-1 px-2.5 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-300 rounded-md font-semibold text-[11px] transition-colors"
                              title="Confirm and verify this test"
                            >
                              <Check className="w-3 h-3" />
                              <span>Verify</span>
                            </button>
                            <button
                              id={`edit-test-${t.id}`}
                              data-testid="edit-test-btn"
                              onClick={() => startEditing(t)}
                              className="p-1 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded"
                              title="Edit test values"
                            >
                              <Edit2 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              id={`delete-test-${t.id}`}
                              onClick={() => deleteTestItem(t.id)}
                              className="p-1 text-rose-500 hover:text-rose-700 hover:bg-rose-50 rounded"
                              title="Delete row"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Verified Records Section */}
      <div id="verified-records-section" className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-5 py-3 border-b border-slate-200 bg-slate-50/70 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <h3 className="text-sm font-bold text-slate-800">
              Verified Records in Patient Chart ({verifiedTests.length})
            </h3>
          </div>
          <span className="text-xs text-slate-500">
            Immutable clinical records with logged verification timestamp
          </span>
        </div>

        {verifiedTests.length === 0 ? (
          <div className="p-6 text-center text-xs text-slate-400">
            No verified tests yet. Complete verification above to commit records.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/50 text-slate-400 border-b border-slate-100 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-2.5 px-4">Test Marker</th>
                  <th className="py-2.5 px-4">Result</th>
                  <th className="py-2.5 px-4">Unit</th>
                  <th className="py-2.5 px-4">Reference Range</th>
                  <th className="py-2.5 px-4">Flag</th>
                  <th className="py-2.5 px-4">Provenance</th>
                  <th className="py-2.5 px-4">Verified By</th>
                  <th className="py-2.5 px-4 text-right">Edit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {verifiedTests.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-50/50">
                    <td className="py-2.5 px-4 font-semibold text-slate-900">{t.test_name}</td>
                    <td className="py-2.5 px-4 font-mono font-bold text-slate-900">{t.value}</td>
                    <td className="py-2.5 px-4 text-slate-500">{t.unit || '—'}</td>
                    <td className="py-2.5 px-4 text-slate-600">{t.reference_range_raw || 'range_unavailable'}</td>
                    <td className="py-2.5 px-4">
                      <FlagBadge flag={t.flag} referenceRange={t.reference_range_raw} />
                    </td>
                    <td className="py-2.5 px-4">
                      <ProvenanceBadge source="verified" verified={true} verifiedBy={t.verified_by} />
                    </td>
                    <td className="py-2.5 px-4 text-[11px] text-slate-500">
                      {t.verified_by || 'User'} ({new Date(t.verified_at || t.updated_at).toLocaleDateString()})
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      <button
                        onClick={() => startEditing(t)}
                        className="text-slate-400 hover:text-slate-700 p-1"
                        title="Edit verified record (recomputes flag and logs audit)"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
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
