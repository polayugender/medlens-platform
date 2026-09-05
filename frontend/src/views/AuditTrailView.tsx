import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Clock,
  User,
  Activity,
  FileText,
  ChevronDown,
  ChevronRight,
  Database
} from 'lucide-react';
import { AuditLog } from '../types';
import { api } from '../api/client';

interface Props {
  patientId: string;
}

export const AuditTrailView: React.FC<Props> = ({ patientId }) => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedLogId, setExpandedLogId] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api
      .getAuditLogs(patientId)
      .then((data) => setLogs(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [patientId]);

  const toggleExpand = (id: string) => {
    setExpandedLogId(expandedLogId === id ? null : id);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-clinical-600" />
            <h2 className="text-lg font-bold text-slate-900">Append-Only Clinical Audit Trail</h2>
            <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-700 rounded">
              Governance & Provenance
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Immutable log tracking every action, user edit, document ingestion, verification, and AI synthesis event.
          </p>
        </div>

        <div className="text-xs font-semibold text-slate-600 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
          Total Logged Events: <span className="font-mono text-clinical-700">{logs.length}</span>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading audit trail...</div>
      ) : logs.length === 0 ? (
        <div className="bg-white p-12 text-center text-xs text-slate-400 rounded-xl border border-slate-200">
          No audit logs recorded for this patient yet.
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden divide-y divide-slate-100">
          {logs.map((log) => {
            const isExpanded = expandedLogId === log.id;
            const hasPayload = log.before_state || log.after_state;

            return (
              <div key={log.id} className="p-4 hover:bg-slate-50/70 transition-colors">
                <div
                  onClick={() => hasPayload && toggleExpand(log.id)}
                  className={`flex items-start justify-between gap-4 ${
                    hasPayload ? 'cursor-pointer' : ''
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-slate-100 rounded-lg text-slate-700 mt-0.5">
                      <Activity className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-extrabold text-slate-900">
                          {log.action}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 bg-slate-100 text-slate-700 rounded font-medium">
                          {log.entity}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 mt-1 text-[11px] text-slate-500">
                        <span className="flex items-center gap-1 font-semibold text-slate-700">
                          <User className="w-3 h-3 text-slate-400" />
                          <span>Actor: {log.actor}</span>
                        </span>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3 text-slate-400" />
                          <span>{new Date(log.timestamp).toLocaleString()}</span>
                        </span>
                      </div>
                    </div>
                  </div>

                  {hasPayload && (
                    <button className="text-slate-400 hover:text-slate-600 p-1">
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4" />
                      ) : (
                        <ChevronRight className="w-4 h-4" />
                      )}
                    </button>
                  )}
                </div>

                {/* Expanded Payload Viewer */}
                {isExpanded && hasPayload && (
                  <div className="mt-3.5 pt-3 border-t border-slate-100 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                    {log.before_state && (
                      <div className="p-3 bg-rose-50/50 rounded-lg border border-rose-200/80">
                        <div className="text-[10px] uppercase font-bold text-rose-800 mb-1">
                          Before State
                        </div>
                        <pre className="text-[11px] text-rose-900 overflow-x-auto whitespace-pre-wrap">
                          {JSON.stringify(log.before_state, null, 2)}
                        </pre>
                      </div>
                    )}
                    {log.after_state && (
                      <div className="p-3 bg-emerald-50/50 rounded-lg border border-emerald-200/80">
                        <div className="text-[10px] uppercase font-bold text-emerald-800 mb-1">
                          After State
                        </div>
                        <pre className="text-[11px] text-emerald-900 overflow-x-auto whitespace-pre-wrap">
                          {JSON.stringify(log.after_state, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
