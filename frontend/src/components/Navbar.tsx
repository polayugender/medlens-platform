import React, { useState } from 'react';
import {
  Activity,
  UserPlus,
  ChevronDown,
  AlertTriangle,
  FileCheck,
  ShieldCheck,
  Users,
  Zap,
  RotateCcw,
  Sparkles,
  Trash2
} from 'lucide-react';
import { Patient } from '../types';

interface Props {
  patients: Patient[];
  selectedPatient: Patient | null;
  onSelectPatient: (patient: Patient) => void;
  onOpenNewPatientModal: () => void;
  onOpenIndianRegistration?: () => void;
  onResetData?: () => void;
  onLoadDemo?: () => void;
  conflictCount: number;
  unverifiedCount: number;
}

export const Navbar: React.FC<Props> = ({
  patients,
  selectedPatient,
  onSelectPatient,
  onOpenNewPatientModal,
  onOpenIndianRegistration,
  onResetData,
  onLoadDemo,
  conflictCount,
  unverifiedCount,
}) => {
  const [showSettingsMenu, setShowSettingsMenu] = useState(false);

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <div className="flex items-center gap-3">
            <div className="relative w-10 h-10 rounded-xl bg-gradient-to-tr from-clinical-600 to-sky-500 flex items-center justify-center text-white shadow-md shadow-clinical-500/20 hover-lift">
              <Activity className="w-5 h-5 stroke-[2.5]" />
              {/* Live status dot */}
              <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-400 rounded-full border-2 border-white" style={{ animation: 'dotPulse 2s ease-in-out infinite' }} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-extrabold tracking-tight brand-shimmer">
                  MedLens
                </span>
                <span className="hidden sm:inline-block text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 bg-clinical-50 text-clinical-700 rounded-md border border-clinical-200/80">
                  Clinical Intelligence
                </span>
              </div>
              <p className="text-[11px] text-slate-500 hidden md:block">
                Unified Patient Provenance & Document Synthesis
              </p>
            </div>
          </div>

          {/* Patient Selector & Action Center */}
          <div className="flex items-center gap-3">
            {/* Alerts Indicators */}
            {conflictCount > 0 && (
              <div
                title={`${conflictCount} clinical cross-check alerts detected`}
                className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 bg-amber-50 border border-amber-300/80 rounded-lg text-xs font-semibold text-amber-800 animate-pulse-amber"
              >
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                <span>{conflictCount} Alert{conflictCount > 1 ? 's' : ''}</span>
              </div>
            )}

            {unverifiedCount > 0 && (
              <div
                title={`${unverifiedCount} extracted tests awaiting verification`}
                className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 bg-sky-50 border border-sky-300/80 rounded-lg text-xs font-semibold text-sky-800"
              >
                <FileCheck className="w-3.5 h-3.5 text-sky-600" />
                <span>{unverifiedCount} To Verify</span>
              </div>
            )}

            {/* Patient Switcher Dropdown */}
            <div className="relative flex items-center">
              <div className="flex items-center gap-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 px-3 py-1.5 rounded-lg transition-colors">
                <Users className="w-4 h-4 text-slate-500" />
                <select
                  id="patient-select"
                  data-testid="patient-select"
                  value={selectedPatient?.id || ''}
                  onChange={(e) => {
                    const found = patients.find((p) => p.id === e.target.value);
                    if (found) onSelectPatient(found);
                  }}
                  disabled={patients.length === 0}
                  className="bg-transparent text-sm font-semibold text-slate-800 focus:outline-none cursor-pointer pr-2 disabled:cursor-not-allowed disabled:text-slate-400"
                >
                  {patients.length === 0 ? (
                    <option value="">No patients registered</option>
                  ) : (
                    patients.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} ({p.sex}, DOB: {p.dob})
                      </option>
                    ))
                  )}
                </select>
              </div>
            </div>

            {/* Indian Onboarding Button */}
            {onOpenIndianRegistration && (
              <button
                id="nav-indian-reg-btn"
                onClick={onOpenIndianRegistration}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-amber-500 to-emerald-600 hover:from-amber-600 hover:to-emerald-700 text-white text-xs font-bold rounded-lg shadow-sm transition-all"
                title="Register Indian Patient (+91 / ABHA)"
              >
                <span>🇮🇳</span>
                <span className="hidden md:inline">Indian Profile</span>
              </button>
            )}

            {/* New Patient Button */}
            <button
              id="new-patient-btn"
              onClick={onOpenNewPatientModal}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-gradient-to-r from-clinical-600 to-clinical-700 hover:from-clinical-700 hover:to-clinical-800 active:from-clinical-800 active:to-clinical-900 text-white text-xs font-semibold rounded-lg shadow-sm shadow-clinical-500/20 transition-all hover-lift"
            >
              <UserPlus className="w-4 h-4" />
              <span className="hidden sm:inline">New Patient</span>
            </button>

            {/* System Actions Dropdown Menu */}
            {(onResetData || onLoadDemo) && (
              <div className="relative">
                <button
                  id="system-menu-btn"
                  onClick={() => setShowSettingsMenu(!showSettingsMenu)}
                  title="System Options"
                  className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  <RotateCcw className="w-4 h-4" />
                </button>

                {showSettingsMenu && (
                  <>
                    <div
                      className="fixed inset-0 z-40"
                      onClick={() => setShowSettingsMenu(false)}
                    />
                    <div className="absolute right-0 mt-2 w-52 bg-white rounded-xl shadow-xl border border-slate-200 py-1.5 z-50 text-xs animate-scale-in">
                      <div className="px-3 py-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100">
                        Data Management
                      </div>

                      {onLoadDemo && (
                        <button
                          id="menu-load-demo-btn"
                          onClick={() => {
                            setShowSettingsMenu(false);
                            onLoadDemo();
                          }}
                          className="w-full px-3 py-2 text-left flex items-center gap-2 hover:bg-slate-50 text-slate-700 font-medium"
                        >
                          <Sparkles className="w-3.5 h-3.5 text-purple-600" />
                          <span>Load Sample Demo Data</span>
                        </button>
                      )}

                      {onResetData && (
                        <button
                          id="menu-clear-data-btn"
                          onClick={() => {
                            setShowSettingsMenu(false);
                            if (window.confirm('Are you sure you want to clear all patient data? This will reset the database for new users.')) {
                              onResetData();
                            }
                          }}
                          className="w-full px-3 py-2 text-left flex items-center gap-2 hover:bg-rose-50 text-rose-600 font-medium"
                        >
                          <Trash2 className="w-3.5 h-3.5 text-rose-500" />
                          <span>Clear All Data (Purge)</span>
                        </button>
                      )}
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
