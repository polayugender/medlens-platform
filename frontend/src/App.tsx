import React, { useState, useEffect } from 'react';
import {
  FileText,
  CheckCircle2,
  UploadCloud,
  TrendingUp,
  AlertTriangle,
  History,
  SplitSquareVertical,
  ClipboardList,
  HeartPulse,
  Activity,
  UserCheck
} from 'lucide-react';
import {
  Patient,
  IntakeRecord,
  MedicalReport,
  ExtractedTest,
  Summary,
  ClinicalConflict
} from './types';
import { api } from './api/client';
import { Navbar } from './components/Navbar';
import { PatientListModal } from './components/PatientListModal';
import { PatientRecordView } from './views/PatientRecordView';
import { IntakeView } from './views/IntakeView';
import { ReportsUploadView } from './views/ReportsUploadView';
import { VerificationView } from './views/VerificationView';
import { SideBySideInspectorView } from './views/SideBySideInspectorView';
import { TrendsView } from './views/TrendsView';
import { ConflictsView } from './views/ConflictsView';
import { AuditTrailView } from './views/AuditTrailView';

export function App() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [activeTab, setActiveTab] = useState<string>('record');
  const [isNewPatientModalOpen, setIsNewPatientModalOpen] = useState(false);

  // Patient detailed data
  const [intake, setIntake] = useState<IntakeRecord | null>(null);
  const [reports, setReports] = useState<MedicalReport[]>([]);
  const [tests, setTests] = useState<ExtractedTest[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [conflicts, setConflicts] = useState<ClinicalConflict[]>([]);
  const [loadingData, setLoadingData] = useState(false);

  // Load initial patients list
  const loadPatients = async () => {
    try {
      const list = await api.getPatients();
      setPatients(list);
      if (list.length > 0 && !selectedPatient) {
        setSelectedPatient(list[0]);
      }
    } catch (err) {
      console.error('Failed to load patients:', err);
    }
  };

  useEffect(() => {
    loadPatients();
  }, []);

  // Fetch active patient full record
  const loadPatientData = async (patientId: string) => {
    setLoadingData(true);
    try {
      const [intakeRes, reportsRes, testsRes, summaryRes, conflictsRes] = await Promise.all([
        api.getLatestIntake(patientId),
        api.getReports(patientId),
        api.getTests(patientId),
        api.getSummary(patientId),
        api.getConflicts(patientId),
      ]);
      setIntake(intakeRes);
      setReports(reportsRes);
      setTests(testsRes);
      setSummary(summaryRes);
      setConflicts(conflictsRes.conflicts || []);
    } catch (err) {
      console.error('Failed to load patient data:', err);
    } finally {
      setLoadingData(false);
    }
  };

  useEffect(() => {
    if (selectedPatient) {
      loadPatientData(selectedPatient.id);
    }
  }, [selectedPatient]);

  const unverifiedCount = tests.filter((t) => !t.verified).length;
  const conflictCount = conflicts.length;

  const tabs = [
    { id: 'record', label: 'Unified Record', icon: ClipboardList, badge: null },
    {
      id: 'verify',
      label: 'Review & Verify',
      icon: CheckCircle2,
      badge: unverifiedCount > 0 ? unverifiedCount : null,
      badgeColor: 'bg-amber-100 text-amber-800',
    },
    { id: 'upload', label: 'Upload & Reports', icon: UploadCloud, badge: reports.length },
    { id: 'intake', label: 'Intake Form', icon: HeartPulse, badge: null },
    { id: 'side_by_side', label: 'Side-by-Side Inspector', icon: SplitSquareVertical, badge: 'New' },
    { id: 'trends', label: 'Longitudinal Trends', icon: TrendingUp, badge: null },
    {
      id: 'conflicts',
      label: 'Safety & Conflicts',
      icon: AlertTriangle,
      badge: conflictCount > 0 ? conflictCount : null,
      badgeColor: 'bg-rose-100 text-rose-800',
    },
    { id: 'audit', label: 'Audit Trail', icon: History, badge: null },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      {/* Navbar Header */}
      <Navbar
        patients={patients}
        selectedPatient={selectedPatient}
        onSelectPatient={(p) => {
          setSelectedPatient(p);
          setActiveTab('record');
        }}
        onOpenNewPatientModal={() => setIsNewPatientModalOpen(true)}
        conflictCount={conflictCount}
        unverifiedCount={unverifiedCount}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Navigation Tabs */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-1.5 overflow-x-auto">
          <nav className="flex space-x-1 min-w-max">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-clinical-600 text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-500'}`} />
                  <span>{tab.label}</span>
                  {tab.badge !== null && (
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${
                        isActive
                          ? 'bg-white/20 text-white'
                          : tab.badgeColor || 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {tab.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        {!selectedPatient ? (
          <div className="bg-white p-12 text-center rounded-2xl border border-slate-200">
            <Activity className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <h3 className="text-base font-bold text-slate-800">No Patient Selected</h3>
            <p className="text-xs text-slate-500 mt-1">Please select or add a patient to begin.</p>
          </div>
        ) : loadingData ? (
          <div className="py-20 text-center space-y-3">
            <div className="w-10 h-10 border-4 border-clinical-600 border-t-transparent rounded-full animate-spin mx-auto" />
            <div className="text-xs font-semibold text-slate-500">Loading clinical records...</div>
          </div>
        ) : (
          <div>
            {activeTab === 'record' && (
              <PatientRecordView
                patient={selectedPatient}
                intake={intake}
                reports={reports}
                tests={tests}
                summary={summary}
                onNavigateToTab={(t) => setActiveTab(t)}
                onSummaryUpdated={(s) => setSummary(s)}
              />
            )}

            {activeTab === 'verify' && (
              <VerificationView
                patientId={selectedPatient.id}
                reports={reports}
                onVerificationComplete={() => loadPatientData(selectedPatient.id)}
              />
            )}

            {activeTab === 'upload' && (
              <ReportsUploadView
                patientId={selectedPatient.id}
                reports={reports}
                onReportUploaded={(newRep) => {
                  setReports([newRep, ...reports]);
                  loadPatientData(selectedPatient.id);
                }}
                onReportDeleted={() => loadPatientData(selectedPatient.id)}
                onNavigateToVerify={() => setActiveTab('verify')}
              />
            )}

            {activeTab === 'intake' && (
              <IntakeView
                patientId={selectedPatient.id}
                onIntakeUpdated={() => loadPatientData(selectedPatient.id)}
              />
            )}

            {activeTab === 'side_by_side' && (
              <SideBySideInspectorView
                patientId={selectedPatient.id}
                reports={reports}
              />
            )}

            {activeTab === 'trends' && <TrendsView patientId={selectedPatient.id} />}

            {activeTab === 'conflicts' && (
              <ConflictsView
                patientId={selectedPatient.id}
                onNavigateToVerify={() => setActiveTab('verify')}
                onNavigateToIntake={() => setActiveTab('intake')}
              />
            )}

            {activeTab === 'audit' && <AuditTrailView patientId={selectedPatient.id} />}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-12 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-600">MedLens</span>
            <span>— AI-Powered Clinical Information Intelligence</span>
          </div>
          <div>
            Built with strict non-diagnostic clinical guardrails & zero data fabrication principles.
          </div>
        </div>
      </footer>

      {/* New Patient Modal */}
      <PatientListModal
        isOpen={isNewPatientModalOpen}
        onClose={() => setIsNewPatientModalOpen(false)}
        onPatientCreated={(p) => {
          setPatients([p, ...patients]);
          setSelectedPatient(p);
          setActiveTab('intake');
        }}
      />
    </div>
  );
}

export default App;
