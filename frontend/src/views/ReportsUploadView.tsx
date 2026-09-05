import React, { useState } from 'react';
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  Trash2,
  ExternalLink,
  Calendar,
  Building,
  AlertCircle,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { MedicalReport } from '../types';
import { api } from '../api/client';

interface Props {
  patientId: string;
  reports: MedicalReport[];
  onReportUploaded: (newReport: MedicalReport) => void;
  onReportDeleted: (reportId: string) => void;
  onNavigateToVerify: () => void;
}

export const ReportsUploadView: React.FC<Props> = ({
  patientId,
  reports,
  onReportUploaded,
  onReportDeleted,
  onNavigateToVerify,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgressMsg, setUploadProgressMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleFileUpload = async (file: File) => {
    setError(null);
    setUploading(true);
    setUploadProgressMsg('Ingesting document and extracting page structures...');

    try {
      setTimeout(() => {
        setUploadProgressMsg('Running AI laboratory marker extraction with strict JSON contract...');
      }, 1000);

      setTimeout(() => {
        setUploadProgressMsg('Computing deterministic Low/Normal/High flags against source ranges...');
      }, 2000);

      const created = await api.uploadReport(patientId, file);
      onReportUploaded(created);
      setUploadProgressMsg('Extraction complete! Redirecting to verification...');
      setTimeout(() => {
        setUploading(false);
        setUploadProgressMsg(null);
        onNavigateToVerify();
      }, 1200);
    } catch (err: any) {
      setError(err.message || 'Upload and extraction failed');
      setUploading(false);
      setUploadProgressMsg(null);
    }
  };

  const handleDelete = async (reportId: string, filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}" and all its extracted tests?`)) {
      return;
    }
    try {
      await api.deleteReport(reportId);
      onReportDeleted(reportId);
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Box */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="mb-4">
          <h2 className="text-lg font-bold text-slate-900">Upload Diagnostic Medical Report</h2>
          <p className="text-xs text-slate-500">
            Upload patient laboratory reports (PDF or images). MedLens extracts structured values, citations, and computes clinical reference flags without hallucination.
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all ${
            dragActive
              ? 'border-clinical-500 bg-clinical-50/50 scale-[1.005]'
              : 'border-slate-300 hover:border-slate-400 bg-slate-50/40'
          }`}
        >
          {uploading ? (
            <div className="py-6 space-y-5 max-w-lg mx-auto">
              <div className="w-12 h-12 border-4 border-clinical-600 border-t-transparent rounded-full animate-spin mx-auto" />
              <div className="text-sm font-bold text-slate-800">
                {uploadProgressMsg}
              </div>
              {/* Multi-step progress track */}
              <div className="grid grid-cols-4 gap-2 pt-2">
                {[
                  { title: 'Ingestion', done: true },
                  { title: 'Extraction', done: uploadProgressMsg?.includes('Extraction') || uploadProgressMsg?.includes('Computing') || uploadProgressMsg?.includes('complete') },
                  { title: 'Flagging', done: uploadProgressMsg?.includes('Computing') || uploadProgressMsg?.includes('complete') },
                  { title: 'Ready', done: uploadProgressMsg?.includes('complete') },
                ].map((step, idx) => (
                  <div key={idx} className="flex flex-col items-center">
                    <div
                      className={`w-full h-1.5 rounded-full transition-all duration-300 ${
                        step.done ? 'bg-clinical-600' : 'bg-slate-200'
                      }`}
                    />
                    <span
                      className={`text-[10px] mt-1 font-semibold ${
                        step.done ? 'text-clinical-700' : 'text-slate-400'
                      }`}
                    >
                      {step.title}
                    </span>
                  </div>
                ))}
              </div>
              <p className="text-xs text-slate-400">
                Adhering to zero-hallucination extraction schema & source range verification
              </p>
            </div>
          ) : (
            <div className="py-4 space-y-3">
              <div className="w-14 h-14 bg-clinical-50 text-clinical-600 rounded-2xl flex items-center justify-center mx-auto shadow-sm">
                <UploadCloud className="w-8 h-8 stroke-[1.8]" />
              </div>
              <div>
                <label className="text-sm font-bold text-clinical-700 hover:text-clinical-800 cursor-pointer underline">
                  Click to select a report
                  <input
                    type="file"
                    accept=".pdf,image/png,image/jpeg"
                    onChange={handleFileInput}
                    className="hidden"
                  />
                </label>
                <span className="text-sm text-slate-500"> or drag and drop files here</span>
              </div>
              <p className="text-xs text-slate-400">
                Supported formats: PDF, PNG, JPG (Laboratory reports, CMP, CBC, Lipid Panels)
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Uploaded Reports List */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-slate-600" />
            <h3 className="text-sm font-bold text-slate-900">
              Uploaded Source Documents ({reports.length})
            </h3>
          </div>
          <button
            onClick={onNavigateToVerify}
            className="text-xs font-semibold text-clinical-700 hover:text-clinical-800 inline-flex items-center gap-1"
          >
            <span>Review Extracted Tests</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {reports.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-400">
            No medical reports uploaded yet. Upload a PDF or test with the sample reports.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {reports.map((r) => (
              <div
                key={r.id}
                className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/70 transition-colors"
              >
                <div className="flex items-start gap-3.5">
                  <div className="p-2.5 bg-clinical-50 text-clinical-700 rounded-xl border border-clinical-200/60 mt-0.5">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">{r.original_filename}</h4>
                    <div className="flex flex-wrap items-center gap-3 mt-1 text-xs text-slate-500">
                      <span className="font-semibold text-clinical-800 bg-clinical-50 px-2 py-0.5 rounded">
                        {r.report_type || 'Laboratory Panel'}
                      </span>
                      {r.report_date && (
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3.5 h-3.5 text-slate-400" />
                          <span>Report Date: {r.report_date}</span>
                        </span>
                      )}
                      {r.facility_name && (
                        <span className="flex items-center gap-1">
                          <Building className="w-3.5 h-3.5 text-slate-400" />
                          <span>{r.facility_name}</span>
                        </span>
                      )}
                      <span className="font-medium text-slate-600">
                        {r.test_count ?? 0} extracted tests
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-center">
                  <a
                    href={r.file_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>View PDF</span>
                  </a>
                  <button
                    onClick={() => handleDelete(r.id, r.original_filename)}
                    className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                    title="Delete report"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
