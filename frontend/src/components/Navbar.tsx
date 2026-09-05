import React from 'react';
import {
  Activity,
  UserPlus,
  ChevronDown,
  AlertTriangle,
  FileCheck,
  ShieldCheck,
  Users
} from 'lucide-react';
import { Patient } from '../types';

interface Props {
  patients: Patient[];
  selectedPatient: Patient | null;
  onSelectPatient: (patient: Patient) => void;
  onOpenNewPatientModal: () => void;
  conflictCount: number;
  unverifiedCount: number;
}

export const Navbar: React.FC<Props> = ({
  patients,
  selectedPatient,
  onSelectPatient,
  onOpenNewPatientModal,
  conflictCount,
  unverifiedCount,
}) => {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-clinical-600 to-sky-500 flex items-center justify-center text-white shadow-md shadow-clinical-500/20">
              <Activity className="w-5 h-5 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-slate-900 via-clinical-800 to-clinical-600 bg-clip-text text-transparent">
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
                className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 bg-amber-50 border border-amber-300/80 rounded-lg text-xs font-semibold text-amber-800"
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
                  value={selectedPatient?.id || ''}
                  onChange={(e) => {
                    const found = patients.find((p) => p.id === e.target.value);
                    if (found) onSelectPatient(found);
                  }}
                  className="bg-transparent text-sm font-semibold text-slate-800 focus:outline-none cursor-pointer pr-2"
                >
                  {patients.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.sex}, DOB: {p.dob})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* New Patient Button */}
            <button
              onClick={onOpenNewPatientModal}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-clinical-600 hover:bg-clinical-700 active:bg-clinical-800 text-white text-xs font-semibold rounded-lg shadow-sm transition-all"
            >
              <UserPlus className="w-4 h-4" />
              <span className="hidden sm:inline">New Patient</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
