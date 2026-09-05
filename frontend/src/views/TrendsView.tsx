import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Calendar,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  CheckCircle2
} from 'lucide-react';
import { TestTrendGroup } from '../types';
import { FlagBadge } from '../components/FlagBadge';
import { api } from '../api/client';

interface Props {
  patientId: string;
}

export const TrendsView: React.FC<Props> = ({ patientId }) => {
  const [trends, setTrends] = useState<TestTrendGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedMarker, setSelectedMarker] = useState<string>('');

  useEffect(() => {
    setLoading(true);
    api
      .getTrends(patientId)
      .then((data) => {
        setTrends(data);
        if (data.length > 0) {
          setSelectedMarker(data[0].test_name);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [patientId]);

  const activeGroup = trends.find((t) => t.test_name === selectedMarker) || trends[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-clinical-600" />
            <h2 className="text-lg font-bold text-slate-900">Biomarker Longitudinal Trends</h2>
            <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-purple-100 text-purple-800 rounded">
              Differentiator
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Track test values over multiple chronological reports to evaluate patterns relative to reference intervals.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading trend trajectories...</div>
      ) : trends.length === 0 ? (
        <div className="bg-white p-12 text-center text-xs text-slate-400 rounded-xl border border-slate-200">
          No numeric biomarkers found across reports for trend plotting.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left: Test Selector List */}
          <div className="lg:col-span-4 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-3.5 bg-slate-50 border-b border-slate-200 text-xs font-bold text-slate-700 uppercase tracking-wider">
              Available Biomarkers ({trends.length})
            </div>
            <div className="divide-y divide-slate-100 max-h-[600px] overflow-y-auto">
              {trends.map((group) => {
                const isSelected = group.test_name === selectedMarker;
                const latestPoint = group.points[group.points.length - 1];

                return (
                  <button
                    key={group.test_name}
                    onClick={() => setSelectedMarker(group.test_name)}
                    className={`w-full text-left p-3.5 transition-colors flex items-center justify-between ${
                      isSelected
                        ? 'bg-clinical-50 border-l-4 border-l-clinical-600 pl-4'
                        : 'hover:bg-slate-50 border-l-4 border-l-transparent'
                    }`}
                  >
                    <div>
                      <div className="text-xs font-bold text-slate-900">{group.test_name}</div>
                      <div className="text-[11px] text-slate-500 mt-0.5">
                        Latest: <span className="font-mono font-semibold">{latestPoint.value} {group.unit || ''}</span>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <span className="text-[10px] px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded font-semibold">
                        {group.points_count} reading{group.points_count > 1 ? 's' : ''}
                      </span>
                      <FlagBadge flag={latestPoint.flag} size="sm" />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right: Trend Visualization & Table */}
          <div className="lg:col-span-8 space-y-6">
            {activeGroup && (
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-6">
                <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                  <div>
                    <h3 className="text-base font-extrabold text-slate-900">{activeGroup.test_name}</h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Measurement Unit: <span className="font-semibold text-slate-700">{activeGroup.unit || 'Standard'}</span>
                    </p>
                  </div>
                  <div className="text-xs text-slate-500">
                    Chronological Trajectory ({activeGroup.points.length} data points)
                  </div>
                </div>

                {/* Visual Corridor Bar Chart */}
                <div className="space-y-4">
                  <div className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Sequential Report Measurements
                  </div>
                  <div className="space-y-3">
                    {activeGroup.points.map((pt, pIdx) => {
                      const low = pt.reference_range_low ?? 0;
                      const high = pt.reference_range_high ?? 100;
                      const val = pt.value;

                      return (
                        <div
                          key={pIdx}
                          className="p-4 bg-slate-50 rounded-xl border border-slate-200/80 space-y-2"
                        >
                          <div className="flex items-center justify-between text-xs">
                            <div className="flex items-center gap-2">
                              <Calendar className="w-3.5 h-3.5 text-slate-400" />
                              <span className="font-semibold text-slate-800">{pt.date}</span>
                              <span className="text-slate-400">({pt.report_name})</span>
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="font-mono text-sm font-bold text-slate-900">
                                {pt.value} {pt.unit || ''}
                              </span>
                              <FlagBadge flag={pt.flag} />
                            </div>
                          </div>

                          {/* Reference interval bar preview */}
                          <div className="relative pt-2">
                            <div className="h-2 w-full bg-slate-200 rounded-full overflow-hidden relative">
                              {/* Reference Corridor Bar (middle 50%) */}
                              <div className="absolute left-[20%] right-[30%] top-0 bottom-0 bg-emerald-200/80" />
                            </div>
                            <div className="flex justify-between text-[10px] text-slate-400 mt-1 font-mono">
                              <span>Low bound: {pt.reference_range_low ?? '—'}</span>
                              <span className="text-emerald-700 font-medium">Standard Reference Range Interval</span>
                              <span>High bound: {pt.reference_range_high ?? '—'}</span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
