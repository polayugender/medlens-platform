import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Calendar,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  CheckCircle2,
  Activity,
  AlertCircle
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

  // SVG Chart Calculations
  const renderSparkline = () => {
    if (!activeGroup || activeGroup.points.length === 0) return null;

    const points = activeGroup.points.map((p, idx) => ({
      ...p,
      idx,
      numVal: p.value,
    }));

    const vals = points.map((p) => p.numVal);
    const lowRef = points.find((p) => typeof p.reference_range_low === 'number')?.reference_range_low;
    const highRef = points.find((p) => typeof p.reference_range_high === 'number')?.reference_range_high;

    const allValues = [...vals];
    if (typeof lowRef === 'number') allValues.push(lowRef);
    if (typeof highRef === 'number') allValues.push(highRef);

    const min = Math.min(...allValues);
    const max = Math.max(...allValues);
    const padding = (max - min) * 0.15 || 5;
    const yMin = Math.max(0, min - padding);
    const yMax = max + padding;

    const width = 640;
    const height = 180;
    const margin = { top: 20, right: 30, bottom: 35, left: 50 };
    const chartW = width - margin.left - margin.right;
    const chartH = height - margin.top - margin.bottom;

    const getX = (idx: number) => {
      if (points.length <= 1) return margin.left + chartW / 2;
      return margin.left + (idx / (points.length - 1)) * chartW;
    };

    const getY = (val: number) => {
      if (yMax === yMin) return margin.top + chartH / 2;
      return margin.top + chartH - ((val - yMin) / (yMax - yMin)) * chartH;
    };

    const pathData = points
      .map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(p.numVal)}`)
      .join(' ');

    // Trajectory calculation
    const firstVal = points[0]?.numVal;
    const latestVal = points[points.length - 1]?.numVal;
    const delta = latestVal - firstVal;

    return (
      <div className="space-y-4">
        {/* Trend Summary Header */}
        <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-50/80 p-3.5 rounded-xl border border-slate-200">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg font-bold ${
              delta > 0 ? 'bg-rose-50 text-rose-700' : delta < 0 ? 'bg-sky-50 text-sky-700' : 'bg-slate-100 text-slate-700'
            }`}>
              {delta > 0 ? <ArrowUpRight className="w-5 h-5" /> : delta < 0 ? <ArrowDownRight className="w-5 h-5" /> : <Minus className="w-5 h-5" />}
            </div>
            <div>
              <div className="text-xs font-bold text-slate-900">
                Longitudinal Trajectory
              </div>
              <div className="text-[11px] text-slate-500">
                {points.length} sequential readings from {points[0]?.date} to {points[points.length - 1]?.date}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <div>
              <span className="text-slate-400 block text-[10px]">Net Change:</span>
              <span className={`font-mono font-bold ${delta > 0 ? 'text-rose-600' : delta < 0 ? 'text-sky-600' : 'text-slate-700'}`}>
                {delta > 0 ? `+${delta.toFixed(1)}` : delta.toFixed(1)} {activeGroup.unit || ''}
              </span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Latest Reading:</span>
              <span className="font-mono font-bold text-slate-900">
                {latestVal} {activeGroup.unit || ''}
              </span>
            </div>
          </div>
        </div>

        {/* SVG Sparkline Canvas */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-inner overflow-hidden">
          <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto">
            {/* Reference corridor fill */}
            {typeof lowRef === 'number' && typeof highRef === 'number' && (
              <rect
                x={margin.left}
                y={getY(highRef)}
                width={chartW}
                height={Math.max(0, getY(lowRef) - getY(highRef))}
                fill="rgba(16, 185, 129, 0.08)"
                stroke="rgba(16, 185, 129, 0.25)"
                strokeDasharray="4 4"
              />
            )}

            {/* Grid lines */}
            <line
              x1={margin.left}
              y1={margin.top + chartH}
              x2={margin.left + chartW}
              y2={margin.top + chartH}
              stroke="#e2e8f0"
              strokeWidth="1"
            />

            {/* Path line */}
            <path
              d={pathData}
              fill="none"
              stroke="#0284c7"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Data points */}
            {points.map((p, i) => {
              const cx = getX(i);
              const cy = getY(p.numVal);
              const isAbnormal = p.flag === 'high' || p.flag === 'low';

              return (
                <g key={i} className="cursor-pointer">
                  <circle
                    cx={cx}
                    cy={cy}
                    r="5"
                    fill={isAbnormal ? (p.flag === 'high' ? '#e11d48' : '#d97706') : '#0284c7'}
                    stroke="#ffffff"
                    strokeWidth="2"
                  />
                  <text
                    x={cx}
                    y={cy - 10}
                    textAnchor="middle"
                    className="text-[10px] font-mono font-bold"
                    fill="#1e293b"
                  >
                    {p.value}
                  </text>
                  <text
                    x={cx}
                    y={height - 10}
                    textAnchor="middle"
                    className="text-[9px] font-sans"
                    fill="#64748b"
                  >
                    {p.date}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Reference range legend */}
          <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 px-2 border-t border-slate-100">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-emerald-50 border border-emerald-300 rounded" />
              <span>Normal Reference Interval ({lowRef ?? '—'} to {highRef ?? '—'} {activeGroup.unit || ''})</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-rose-500" /> High Flag
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-amber-500" /> Low Flag
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-clinical-500" /> Normal
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  };

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

                {/* Interactive SVG Sparkline */}
                {renderSparkline()}

                {/* Sequential Report Measurements Table */}
                <div className="space-y-3">
                  <div className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Detailed Chronological History
                  </div>
                  <div className="space-y-2.5">
                    {activeGroup.points.map((pt, pIdx) => (
                      <div
                        key={pIdx}
                        className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/80 flex items-center justify-between text-xs"
                      >
                        <div className="flex items-center gap-2.5">
                          <Calendar className="w-4 h-4 text-slate-400" />
                          <span className="font-bold text-slate-800">{pt.date}</span>
                          <span className="text-slate-500">({pt.report_name})</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="font-mono text-xs font-bold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-200">
                            {pt.value} {pt.unit || ''}
                          </span>
                          <FlagBadge
                            flag={pt.flag}
                            referenceRange={
                              typeof pt.reference_range_low === 'number' && typeof pt.reference_range_high === 'number'
                                ? `${pt.reference_range_low} - ${pt.reference_range_high}`
                                : undefined
                            }
                          />
                        </div>
                      </div>
                    ))}
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
