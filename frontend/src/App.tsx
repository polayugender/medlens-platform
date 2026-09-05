import React, { useState, useEffect, useCallback } from 'react';
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
  UserCheck,
  Zap,
  Shield,
  Github,
  Globe,
  PlusCircle,
  ArrowRight,
  Info
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
import { WelcomeView } from './views/WelcomeView';
import { IndianProfileRegistration } from './views/IndianProfileRegistration';

export function App() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [currentUser, setCurrentUser] = useState<Patient | null>(null);
  const [activeTab, setActiveTab] = useState<string>('record');
  const [isNewPatientModalOpen, setIsNewPatientModalOpen] = useState(false);
  const [isIndianRegOpen, setIsIndianRegOpen] = useState(false);
  const [tabTransitionKey, setTabTransitionKey] = useState(0);
  const [systemNotice, setSystemNotice] = useState<string | null>(null);

  // Patient detailed data
  const [intake, setIntake] = useState<IntakeRecord | null>(null);
  const [reports, setReports] = useState<MedicalReport[]>([]);
  const [tests, setTests] = useState<ExtractedTest[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [conflicts, setConflicts] = useState<ClinicalConflict[]>([]);
  const [loadingData, setLoadingData] = useState(false);

  // Load initial patients list
  const loadPatients = async (preferredPatientId?: string) => {
    try {
      const list = await api.getPatients();
      setPatients(list);
      if (list.length > 0) {
        if (preferredPatientId) {
          const matched = list.find((p) => p.id === preferredPatientId);
          setSelectedPatient(matched || list[0]);
        } else if (!selectedPatient || !list.some((p) => p.id === selectedPatient.id)) {
          setSelectedPatient(list[0]);
        }
      } else {
        setSelectedPatient(null);
      }
    } catch (err) {
      console.error('Failed to load patients:', err);
    }
  };

  useEffect(() => {
    const initAuthAndData = async () => {
      try {
        const user = await api.getCurrentUser();
        if (user) {
          setCurrentUser(user);
          await loadPatients(user.id);
        } else {
          await loadPatients();
        }
      } catch {
        await loadPatients();
      }
    };
    initAuthAndData();
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
    } else {
      setIntake(null);
      setReports([]);
      setTests([]);
      setSummary(null);
      setConflicts([]);
    }
  }, [selectedPatient]);

  // System management handlers
  const handleResetData = async () => {
    try {
      await api.resetSystem();
      setPatients([]);
      setSelectedPatient(null);
      setIntake(null);
      setReports([]);
      setTests([]);
      setSummary(null);
      setConflicts([]);
      setSystemNotice('All clinical records and storage files have been purged. MedLens is clean for new users.');
      setTimeout(() => setSystemNotice(null), 5000);
    } catch (err: any) {
      alert(`Reset failed: ${err.message}`);
    }
  };

  const handleLoadDemo = async () => {
    try {
      await api.seedDemoData();
      const list = await api.getPatients();
      setPatients(list);
      const preferred = list.find((p) => p.name.includes('Eleanor')) || list[0];
      setSelectedPatient(preferred);
      setActiveTab('record');
      setSystemNotice('Sample clinical demo records loaded successfully.');
      setTimeout(() => setSystemNotice(null), 5000);
    } catch (err: any) {
      alert(`Failed to load demo data: ${err.message}`);
    }
  };

  const unverifiedCount = tests.filter((t) => !t.verified).length;
  const conflictCount = conflicts.length;

  const tabs = [
    { id: 'record', label: 'Unified Record', icon: ClipboardList, badge: null, shortcut: '1' },
    {
      id: 'verify',
      label: 'Review & Verify',
      icon: CheckCircle2,
      badge: unverifiedCount > 0 ? unverifiedCount : null,
      badgeColor: 'bg-amber-100 text-amber-800',
      shortcut: '2',
    },
    { id: 'upload', label: 'Upload & Reports', icon: UploadCloud, badge: reports.length, shortcut: '3' },
    { id: 'intake', label: 'Intake Form', icon: HeartPulse, badge: null, shortcut: '4' },
    { id: 'side_by_side', label: 'Side-by-Side', icon: SplitSquareVertical, badge: null, shortcut: '5' },
    { id: 'trends', label: 'Trends', icon: TrendingUp, badge: null, shortcut: '6' },
    {
      id: 'conflicts',
      label: 'Safety & Conflicts',
      icon: AlertTriangle,
      badge: conflictCount > 0 ? conflictCount : null,
      badgeColor: 'bg-rose-100 text-rose-800',
      shortcut: '7',
    },
    { id: 'audit', label: 'Audit Trail', icon: History, badge: null, shortcut: '8' },
  ];

  // Handle tab switch with animation trigger
  const switchTab = useCallback((tabId: string) => {
    setActiveTab(tabId);
    setTabTransitionKey((k) => k + 1);
  }, []);

  // Keyboard shortcuts (Ctrl+1 through Ctrl+8)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && !e.shiftKey && !e.altKey) {
        const num = parseInt(e.key);
        if (num >= 1 && num <= 8) {
          e.preventDefault();
          switchTab(tabs[num - 1].id);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [switchTab, tabs]);

  // Is this a brand-new patient with no data yet?
  const isFreshPatient = selectedPatient && !intake && reports.length === 0 && tests.length === 0;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      {/* Navbar Header */}
      <Navbar
        patients={patients}
        selectedPatient={selectedPatient}
        currentUser={currentUser}
        onSelectPatient={(p) => {
          setSelectedPatient(p);
          setIsIndianRegOpen(false);
          switchTab('record');
        }}
        onOpenNewPatientModal={() => setIsNewPatientModalOpen(true)}
        onOpenIndianRegistration={() => setIsIndianRegOpen(true)}
        onLogout={() => {
          api.logout();
          setCurrentUser(null);
          setSystemNotice('Successfully signed out of MedLens.');
          setTimeout(() => setSystemNotice(null), 4000);
          loadPatients();
        }}
        onResetData={handleResetData}
        onLoadDemo={handleLoadDemo}
        conflictCount={conflictCount}
        unverifiedCount={unverifiedCount}
      />

      {/* System Toast Notification */}
      {systemNotice && (
        <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 pt-4">
          <div className="flex items-center justify-between gap-3 p-3 bg-clinical-50 border border-clinical-200 text-clinical-900 rounded-xl text-xs font-semibold shadow-sm animate-fade-in-up">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-clinical-600 flex-shrink-0" />
              <span>{systemNotice}</span>
            </div>
            <button
              onClick={() => setSystemNotice(null)}
              className="text-slate-400 hover:text-slate-600 text-xs px-2 py-0.5 rounded"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {isIndianRegOpen ? (
          <IndianProfileRegistration
            onComplete={(newPatient, newIntake, targetTab) => {
              setIsIndianRegOpen(false);
              setCurrentUser(newPatient);
              setPatients((prev) => [newPatient, ...prev.filter((p) => p.id !== newPatient.id)]);
              setSelectedPatient(newPatient);
              if (newIntake) setIntake(newIntake);
              setActiveTab(targetTab);
              setSystemNotice(`Clinical profile active for ${newPatient.name} (ABHA: ${newPatient.abha_id || 'Not Linked'}).`);
              setTimeout(() => setSystemNotice(null), 6000);
            }}
            onCancel={() => setIsIndianRegOpen(false)}
          />
        ) : !selectedPatient ? (
          /* Welcome Portal for New Users */
          <WelcomeView
            onOpenNewPatientModal={() => setIsNewPatientModalOpen(true)}
            onOpenIndianRegistration={() => setIsIndianRegOpen(true)}
            onDemoLoaded={handleLoadDemo}
          />
        ) : (
          <>
            {/* New Patient Guided Setup Stepper Banner */}
            {isFreshPatient && (
              <div className="bg-gradient-to-r from-clinical-50 via-sky-50 to-indigo-50 border border-clinical-200/80 rounded-2xl p-4 shadow-sm animate-fade-in-up">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-clinical-600 text-white flex items-center justify-center font-bold text-xs flex-shrink-0">
                      NEW
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-900">
                        Patient Profile Created: {selectedPatient.name}
                      </h4>
                      <p className="text-[11px] text-slate-600">
                        Follow the clinical pipeline: 1) Fill Intake Form → 2) Upload Lab Report PDFs → 3) Review & Verify.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => switchTab('intake')}
                      className={`text-xs px-3 py-1.5 rounded-lg font-semibold transition-all ${
                        activeTab === 'intake'
                          ? 'bg-clinical-600 text-white shadow-sm'
                          : 'bg-white text-clinical-700 border border-clinical-200 hover:bg-clinical-50'
                      }`}
                    >
                      Step 1: Fill Intake
                    </button>
                    <button
                      onClick={() => switchTab('upload')}
                      className={`text-xs px-3 py-1.5 rounded-lg font-semibold transition-all ${
                        activeTab === 'upload'
                          ? 'bg-clinical-600 text-white shadow-sm'
                          : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50'
                      }`}
                    >
                      Step 2: Upload Reports
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Navigation Tabs */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-1.5 overflow-x-auto animate-fade-in-up">
              <nav className="flex items-center justify-start xl:justify-between gap-1 w-full min-w-max xl:min-w-0">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;

                  return (
                    <button
                      key={tab.id}
                      id={`nav-tab-${tab.id}`}
                      onClick={() => switchTab(tab.id)}
                      title={`${tab.label} (Ctrl+${tab.shortcut})`}
                      className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all duration-200 ${
                        isActive
                          ? 'bg-gradient-to-r from-clinical-600 to-clinical-700 text-white shadow-sm shadow-clinical-500/20'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                      }`}
                    >
                      <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-slate-500'}`} />
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
            {loadingData ? (
              <div className="py-20 text-center space-y-3 animate-fade-in-up">
                <div className="w-10 h-10 border-4 border-clinical-600 border-t-transparent rounded-full animate-spin mx-auto" />
                <div className="text-xs font-semibold text-slate-500">Loading clinical records...</div>
              </div>
            ) : (
              <div key={tabTransitionKey} className="tab-content-enter">
                {activeTab === 'record' && (
                  <PatientRecordView
                    patient={selectedPatient}
                    intake={intake}
                    reports={reports}
                    tests={tests}
                    summary={summary}
                    onNavigateToTab={(t) => switchTab(t)}
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
                    onNavigateToVerify={() => switchTab('verify')}
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
                    onNavigateToVerify={() => switchTab('verify')}
                    onNavigateToIntake={() => switchTab('intake')}
                  />
                )}

                {activeTab === 'audit' && <AuditTrailView patientId={selectedPatient.id} />}
              </div>
            )}
          </>
        )}
      </main>

      {/* Premium Footer */}
      <footer className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 mt-12 py-6 border-t border-slate-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-clinical-500 to-sky-400 flex items-center justify-center text-white shadow-sm">
                <Activity className="w-4 h-4 stroke-[2.5]" />
              </div>
              <div>
                <span className="text-sm font-bold text-white">MedLens</span>
                <span className="text-xs text-slate-400 ml-2">v1.0.0</span>
              </div>
            </div>

            <div className="flex items-center gap-6 text-xs text-slate-400">
              <div className="flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-emerald-400" />
                <span>Non-Diagnostic Guardrails Active</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                <span>Zero Data Fabrication</span>
              </div>
            </div>

            <div className="text-[11px] text-slate-500">
              Built for AI-powered clinical information intelligence
            </div>
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
          switchTab('intake');
        }}
      />
    </div>
  );
}

export default App;
