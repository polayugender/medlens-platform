import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  HeartPulse,
  User,
  Calendar,
  MapPin,
  Phone,
  Plus,
  Trash2,
  UploadCloud,
  ClipboardList,
  Building2,
  Lock,
  Info,
  Check,
  RefreshCw,
  X
} from 'lucide-react';
import { api } from '../api/client';
import { Patient, IntakeRecord } from '../types';
import { AuthView } from '../components/AuthView';

interface Props {
  onComplete: (patient: Patient, intake: IntakeRecord | null, targetTab: 'upload' | 'record') => void;
  onCancel: () => void;
}

const INDIAN_STATES_CITIES: Record<string, string[]> = {
  'Telangana': ['Hyderabad', 'Warangal', 'Nizamabad', 'Karimnagar', 'Khammam', 'Ramagundam'],
  'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Thane', 'Aurangabad', 'Solapur'],
  'Karnataka': ['Bengaluru', 'Mysuru', 'Hubballi', 'Mangaluru', 'Belagavi', 'Davangere'],
  'Delhi / NCR': ['New Delhi', 'North Delhi', 'South Delhi', 'Noida', 'Gurugram', 'Faridabad'],
  'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Tirunelveli'],
  'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar', 'Jamnagar'],
  'West Bengal': ['Kolkata', 'Howrah', 'Durgapur', 'Siliguri', 'Asansol'],
  'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Varanasi', 'Agra', 'Prayagraj', 'Noida', 'Ghaziabad'],
  'Kerala': ['Thiruvananthapuram', 'Kochi', 'Kozhikode', 'Thrissur', 'Kollam'],
  'Andhra Pradesh': ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Tirupati', 'Kurnool'],
  'Rajasthan': ['Jaipur', 'Jodhpur', 'Udaipur', 'Kota', 'Bikaner', 'Ajmer'],
  'Punjab': ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda'],
  'Madhya Pradesh': ['Bhopal', 'Indore', 'Gwalior', 'Jabalpur', 'Ujjain']
};

const COMMON_CONDITIONS = [
  'Type 2 Diabetes',
  'Hypertension',
  'Hypothyroidism',
  'Asthma',
  'Coronary Artery Disease (CAD)',
  'Chronic Kidney Disease (CKD)',
  'Dyslipidemia',
  'GERD / Acid Peptic Disease',
  'Fatty Liver (NAFLD)',
  'Tuberculosis (History)'
];

const COMMON_ALLERGIES = [
  'Penicillins',
  'Sulfa drugs',
  'NSAIDs',
  'Cephalosporins',
  'Fluoroquinolones',
  'Macrolides',
  'Paracetamol'
];

interface MedRow {
  name: string;
  dosage: string;
  frequency: string;
  route: string;
}

export const IndianProfileRegistration: React.FC<Props> = ({ onComplete, onCancel }) => {
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);

  // Step 1: Authentication & Patient State
  const [phone, setPhone] = useState('');

  // Step 2: Demographics State
  const [name, setName] = useState('');
  const [dob, setDob] = useState('');
  const [calculatedAge, setCalculatedAge] = useState<number | null>(null);
  const [sex, setSex] = useState<'Male' | 'Female' | 'Other'>('Male');
  const [abhaId, setAbhaId] = useState('');
  const [state, setState] = useState('Telangana');
  const [city, setCity] = useState('Hyderabad');
  const [emergencyName, setEmergencyName] = useState('');
  const [emergencyRelation, setEmergencyRelation] = useState('Spouse');
  const [emergencyPhone, setEmergencyPhone] = useState('');
  const [step2Error, setStep2Error] = useState<string | null>(null);

  // Step 3: Clinical Intake State
  const [selectedConditions, setSelectedConditions] = useState<string[]>([]);
  const [customCondition, setCustomCondition] = useState('');
  const [selectedAllergies, setSelectedAllergies] = useState<string[]>([]);
  const [customAllergy, setCustomAllergy] = useState('');
  const [medications, setMedications] = useState<MedRow[]>([]);
  const [dpdpConsent, setDpdpConsent] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Step 4: Health Card Result / Created Patient
  const [createdPatient, setCreatedPatient] = useState<Patient | null>(null);
  const [createdIntake, setCreatedIntake] = useState<IntakeRecord | null>(null);

  // Auto-calculate age when DOB changes
  useEffect(() => {
    if (dob) {
      const birthDate = new Date(dob);
      const today = new Date();
      let age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
      }
      setCalculatedAge(age >= 0 ? age : 0);
    } else {
      setCalculatedAge(null);
    }
  }, [dob]);

  // Update city list default when state changes
  useEffect(() => {
    const cities = INDIAN_STATES_CITIES[state] || [];
    if (cities.length > 0 && !cities.includes(city)) {
      setCity(cities[0]);
    }
  }, [state]);

  // ABHA ID auto-formatter (XX-XXXX-XXXX-XXXX)
  const handleAbhaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/\D/g, '').slice(0, 14);
    const parts = [];
    if (raw.length > 0) parts.push(raw.slice(0, 2));
    if (raw.length > 2) parts.push(raw.slice(2, 6));
    if (raw.length > 6) parts.push(raw.slice(6, 10));
    if (raw.length > 10) parts.push(raw.slice(10, 14));
    setAbhaId(parts.join('-'));
  };

  // Step 2 Validation & Next
  const handleStep2Submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setStep2Error('Legal name is required');
      return;
    }
    if (!dob) {
      setStep2Error('Date of birth is required');
      return;
    }
    if (!state || !city) {
      setStep2Error('State and city are required');
      return;
    }
    setStep2Error(null);
    setStep(3);
  };

  // Step 3 Clinical Tag helpers
  const toggleCondition = (cond: string) => {
    setSelectedConditions((prev) =>
      prev.includes(cond) ? prev.filter((c) => c !== cond) : [...prev, cond]
    );
  };

  const addCustomCondition = () => {
    if (customCondition.trim() && !selectedConditions.includes(customCondition.trim())) {
      setSelectedConditions((prev) => [...prev, customCondition.trim()]);
      setCustomCondition('');
    }
  };

  const toggleAllergy = (allergy: string) => {
    setSelectedAllergies((prev) =>
      prev.includes(allergy) ? prev.filter((a) => a !== allergy) : [...prev, allergy]
    );
  };

  const addCustomAllergy = () => {
    if (customAllergy.trim() && !selectedAllergies.includes(customAllergy.trim())) {
      setSelectedAllergies((prev) => [...prev, customAllergy.trim()]);
      setCustomAllergy('');
    }
  };

  // Medications Table Helpers
  const addMedication = (
    preset?: { name: string; dosage: string; frequency: string; route: string }
  ) => {
    if (preset) {
      setMedications((prev) => [...prev, preset]);
    } else {
      setMedications((prev) => [
        ...prev,
        { name: '', dosage: '', frequency: 'OD', route: 'Oral' }
      ]);
    }
  };

  const updateMedication = (index: number, field: keyof MedRow, value: string) => {
    setMedications((prev) => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  };

  const removeMedication = (index: number) => {
    setMedications((prev) => prev.filter((_, i) => i !== index));
  };

  // Real-Time Conflict Detection Logic
  const hasPenicillinAllergy = selectedAllergies.some((a) =>
    a.toLowerCase().includes('penicillin')
  );

  const penicillinMedConflict = medications.find((m) => {
    const n = m.name.toLowerCase();
    return (
      n.includes('amoxicillin') ||
      n.includes('augmentin') ||
      n.includes('ampicillin') ||
      n.includes('amoxil') ||
      n.includes('penicillin')
    );
  });

  const hasNsaidAllergy = selectedAllergies.some((a) =>
    a.toLowerCase().includes('nsaid')
  );

  const nsaidMedConflict = medications.find((m) => {
    const n = m.name.toLowerCase();
    return (
      n.includes('aspirin') ||
      n.includes('ibuprofen') ||
      n.includes('diclofenac') ||
      n.includes('naproxen') ||
      n.includes('ecosprin') ||
      n.includes('combiflam')
    );
  });

  // Final Registration Submission
  const handleFinalSubmit = async () => {
    if (!dpdpConsent) {
      setSubmitError('You must agree to the DPDP Act 2023 data processing consent to proceed.');
      return;
    }

    setSubmitting(true);
    setSubmitError(null);

    try {
      // 1. Create or update Patient with Indian Demographics
      const emergencyContactString = emergencyName
        ? `${emergencyName} (${emergencyRelation})${emergencyPhone ? ` - ${emergencyPhone}` : ''}`
        : undefined;

      let patientRecord: Patient;
      if (createdPatient?.id) {
        patientRecord = await api.updatePatient(
          createdPatient.id,
          {
            name: name.trim(),
            dob,
            sex,
            phone: phone ? (phone.startsWith('+91') ? phone : `+91 ${phone}`) : undefined,
            abha_id: abhaId.trim() || undefined,
            state,
            city,
            emergency_contact: emergencyContactString,
          },
          'patient_self_service'
        );
      } else {
        patientRecord = await api.createPatient(
          {
            name: name.trim(),
            dob,
            sex,
            phone: phone ? (phone.startsWith('+91') ? phone : `+91 ${phone}`) : undefined,
            abha_id: abhaId.trim() || undefined,
            state,
            city,
            emergency_contact: emergencyContactString,
          },
          'patient_self_service'
        );
      }

      // 2. Submit Baseline Clinical Intake Record
      const validMeds = medications
        .filter((m) => m.name.trim().length > 0)
        .map((m) => ({
          name: m.name.trim(),
          dosage: m.dosage.trim() || 'Standard',
          frequency: m.frequency,
          route: m.route,
        }));

      const newIntake = await api.submitIntake(
        patientRecord.id,
        {
          age: calculatedAge ?? 30,
          sex,
          symptoms: [],
          existing_conditions: selectedConditions,
          allergies: selectedAllergies,
          medications: validMeds,
        },
        'patient_self_service'
      );

      setCreatedPatient(patientRecord);
      setCreatedIntake(newIntake);
      setStep(4);
    } catch (err: any) {
      console.error('Registration failed:', err);
      setSubmitError(err.message || 'Failed to complete registration');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6 space-y-6 animate-fade-in-up">
      {/* Header Bar */}
      <div className="flex items-center justify-between bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-white to-emerald-600 p-0.5 shadow-sm">
            <div className="w-full h-full bg-slate-900 rounded-[10px] flex items-center justify-center">
              <span className="text-base">🇮🇳</span>
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-slate-900">
                Indian Patient Clinical Onboarding
              </h2>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300">
                ABDM & DPDP Compliant
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Structured registration, mobile verification, and safety-checked clinical baseline
            </p>
          </div>
        </div>

        <button
          onClick={onCancel}
          className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
          title="Cancel Registration"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Stepper Progress Navigation */}
      {step < 4 && (
        <div className="grid grid-cols-3 gap-2 sm:gap-4">
          <div
            className={`p-3 rounded-xl border transition-all ${
              step === 1
                ? 'bg-clinical-50 border-clinical-300 shadow-sm'
                : step > 1
                ? 'bg-emerald-50/60 border-emerald-200 text-emerald-800'
                : 'bg-white border-slate-200 text-slate-400'
            }`}
          >
            <div className="flex items-center gap-2">
              <div
                className={`w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center ${
                  step === 1
                    ? 'bg-clinical-600 text-white'
                    : step > 1
                    ? 'bg-emerald-600 text-white'
                    : 'bg-slate-200 text-slate-600'
                }`}
              >
                {step > 1 ? <Check className="w-3.5 h-3.5" /> : '1'}
              </div>
              <div>
                <div className="text-xs font-bold">Authentication</div>
                <div className="text-[10px] hidden sm:block text-slate-500">
                  Account & Security
                </div>
              </div>
            </div>
          </div>

          <div
            className={`p-3 rounded-xl border transition-all ${
              step === 2
                ? 'bg-clinical-50 border-clinical-300 shadow-sm'
                : step > 2
                ? 'bg-emerald-50/60 border-emerald-200 text-emerald-800'
                : 'bg-white border-slate-200 text-slate-400'
            }`}
          >
            <div className="flex items-center gap-2">
              <div
                className={`w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center ${
                  step === 2
                    ? 'bg-clinical-600 text-white'
                    : step > 2
                    ? 'bg-emerald-600 text-white'
                    : 'bg-slate-200 text-slate-600'
                }`}
              >
                {step > 2 ? <Check className="w-3.5 h-3.5" /> : '2'}
              </div>
              <div>
                <div className="text-xs font-bold">Demographics & ABHA</div>
                <div className="text-[10px] hidden sm:block text-slate-500">
                  Aadhaar & State Info
                </div>
              </div>
            </div>
          </div>

          <div
            className={`p-3 rounded-xl border transition-all ${
              step === 3
                ? 'bg-clinical-50 border-clinical-300 shadow-sm'
                : 'bg-white border-slate-200 text-slate-400'
            }`}
          >
            <div className="flex items-center gap-2">
              <div
                className={`w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center ${
                  step === 3
                    ? 'bg-clinical-600 text-white'
                    : 'bg-slate-200 text-slate-600'
                }`}
              >
                3
              </div>
              <div>
                <div className="text-xs font-bold">Clinical Baseline</div>
                <div className="text-[10px] hidden sm:block text-slate-500">
                  Allergies & Safety Check
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Persistent Non-Diagnostic Disclaimer */}
      <div className="p-3 bg-amber-50 border border-amber-200/80 rounded-xl text-amber-900 text-xs flex items-start gap-2.5">
        <Info className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
        <div>
          <span className="font-bold">MedLens Non-Diagnostic Advisory:</span> This platform
          structures medical history and diagnostic lab data for clinical decision support. It
          does not provide autonomous diagnosis or prescriptive care.
        </div>
      </div>

      {/* ──────────────────────────────────────────────
          STEP 1: SECURE AUTHENTICATION (SIGN IN / REGISTER)
         ────────────────────────────────────────────── */}
      {step === 1 && (
        <AuthView
          onRegisterSuccess={(registeredPatient) => {
            setCreatedPatient(registeredPatient);
            if (registeredPatient.name) setName(registeredPatient.name);
            if (registeredPatient.phone) {
              setPhone(registeredPatient.phone.replace('+91 ', '').trim());
            }
            setStep(2);
          }}
          onLoginSuccess={(loggedInPatient) => {
            onComplete(loggedInPatient, null, 'record');
          }}
        />
      )}

      {/* ──────────────────────────────────────────────
          STEP 2: DEMOGRAPHICS & NATIONAL HEALTH ID (ABHA)
         ────────────────────────────────────────────── */}
      {step === 2 && (
        <form
          onSubmit={handleStep2Submit}
          className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6 animate-fade-in-up"
        >
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-900">
                Step 2: Demographics & National Health ID
              </h3>
              <span className="px-2 py-0.5 bg-sky-100 text-sky-800 text-[10px] font-semibold rounded-full">
                [User Input] Provenance
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Provide government identification details to anchor your patient clinical records.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Legal Name */}
            <div className="sm:col-span-2 space-y-1.5">
              <label className="block text-xs font-bold text-slate-700">
                Legal Full Name (as per Aadhaar / Government ID) <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  id="indian-name-input"
                  type="text"
                  required
                  placeholder="e.g. Rajesh Kumar"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 text-xs font-semibold rounded-xl border border-slate-300 focus:ring-2 focus:ring-clinical-500 focus:outline-none"
                />
              </div>
            </div>

            {/* Date of Birth & Live Age */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="block text-xs font-bold text-slate-700">
                  Date of Birth <span className="text-rose-500">*</span>
                </label>
                {calculatedAge !== null && (
                  <span className="text-[11px] font-bold text-clinical-700 bg-clinical-50 px-2 py-0.5 rounded-md border border-clinical-200">
                    Age: {calculatedAge} years
                  </span>
                )}
              </div>
              <div className="relative">
                <Calendar className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  id="indian-dob-input"
                  type="date"
                  required
                  value={dob}
                  max={new Date().toISOString().split('T')[0]}
                  onChange={(e) => setDob(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 text-xs font-semibold rounded-xl border border-slate-300 focus:ring-2 focus:ring-clinical-500 focus:outline-none"
                />
              </div>
            </div>

            {/* Biological Sex */}
            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-slate-700">
                Biological Sex (for reference range baseline) <span className="text-rose-500">*</span>
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(['Male', 'Female', 'Other'] as const).map((s) => (
                  <button
                    key={s}
                    id={`sex-btn-${s.toLowerCase()}`}
                    type="button"
                    onClick={() => setSex(s)}
                    className={`py-2 px-3 text-xs font-bold rounded-xl border transition-all ${
                      sex === s
                        ? 'bg-clinical-600 text-white border-clinical-600 shadow-sm'
                        : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            {/* ABHA ID (Ayushman Bharat Health Account) */}
            <div className="sm:col-span-2 space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="block text-xs font-bold text-slate-700">
                  Ayushman Bharat Health Account (ABHA ID / Number)
                </label>
                <span className="text-[10px] text-slate-500 font-medium">Optional • ABDM</span>
              </div>
              <div className="relative">
                <Building2 className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  id="indian-abha-input"
                  type="text"
                  placeholder="91-4820-9182-3841"
                  maxLength={17}
                  value={abhaId}
                  onChange={handleAbhaChange}
                  className="w-full pl-10 pr-4 py-2 text-xs font-mono font-semibold tracking-wider rounded-xl border border-slate-300 focus:ring-2 focus:ring-clinical-500 focus:outline-none"
                />
              </div>
              <p className="text-[10px] text-slate-500">
                Format: 14 digits with hyphens (e.g. 91-4820-9182-3841). Facilitates ABDM unified health record exchange.
              </p>
            </div>

            {/* State Selection */}
            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-slate-700">
                State / Union Territory <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <select
                  id="indian-state-select"
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 text-xs font-semibold rounded-xl border border-slate-300 focus:ring-2 focus:ring-clinical-500 focus:outline-none bg-white"
                >
                  {Object.keys(INDIAN_STATES_CITIES).map((st) => (
                    <option key={st} value={st}>
                      {st}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* City Selection */}
            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-slate-700">
                City / District <span className="text-rose-500">*</span>
              </label>
              <select
                id="indian-city-select"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full px-4 py-2 text-xs font-semibold rounded-xl border border-slate-300 focus:ring-2 focus:ring-clinical-500 focus:outline-none bg-white"
              >
                {(INDIAN_STATES_CITIES[state] || []).map((ct) => (
                  <option key={ct} value={ct}>
                    {ct}
                  </option>
                ))}
              </select>
            </div>

            {/* Emergency Contact */}
            <div className="sm:col-span-2 pt-2 border-t border-slate-100 space-y-2">
              <span className="text-xs font-bold text-slate-800">
                Emergency Contact (Next of Kin)
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <input
                  id="emergency-name-input"
                  type="text"
                  placeholder="Contact Name (e.g. Priya Kumar)"
                  value={emergencyName}
                  onChange={(e) => setEmergencyName(e.target.value)}
                  className="px-3 py-2 text-xs font-medium rounded-xl border border-slate-300 focus:outline-none"
                />

                <select
                  id="emergency-relation-select"
                  value={emergencyRelation}
                  onChange={(e) => setEmergencyRelation(e.target.value)}
                  className="px-3 py-2 text-xs font-medium rounded-xl border border-slate-300 focus:outline-none bg-white"
                >
                  <option value="Spouse">Spouse</option>
                  <option value="Parent">Parent</option>
                  <option value="Child">Child</option>
                  <option value="Sibling">Sibling</option>
                  <option value="Guardian">Guardian</option>
                  <option value="Other">Other</option>
                </select>

                <input
                  id="emergency-phone-input"
                  type="tel"
                  maxLength={10}
                  placeholder="Emergency Phone (10 digits)"
                  value={emergencyPhone}
                  onChange={(e) => setEmergencyPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                  className="px-3 py-2 text-xs font-medium rounded-xl border border-slate-300 focus:outline-none"
                />
              </div>
            </div>
          </div>

          {step2Error && (
            <div className="p-2.5 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs font-medium flex items-center gap-2">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-600 flex-shrink-0" />
              <span>{step2Error}</span>
            </div>
          )}

          {/* Navigation buttons */}
          <div className="flex items-center justify-between pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setStep(1)}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Step 1</span>
            </button>

            <button
              id="step2-next-btn"
              type="submit"
              className="inline-flex items-center gap-1.5 px-6 py-2.5 rounded-xl bg-clinical-600 hover:bg-clinical-700 text-white font-bold text-xs shadow-md shadow-clinical-600/20 transition-all"
            >
              <span>Continue to Clinical Baseline</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>
      )}

      {/* ──────────────────────────────────────────────
          STEP 3: BASELINE CLINICAL INTAKE & SAFETY GUARDRAILS
         ────────────────────────────────────────────── */}
      {step === 3 && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6 animate-fade-in-up">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-900">
                Step 3: Baseline Clinical Intake & Safety Guardrails
              </h3>
              <span className="px-2 py-0.5 bg-sky-100 text-sky-800 text-[10px] font-semibold rounded-full">
                [User Input] Provenance
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Declare existing medical conditions, drug hypersensitivities, and active medications. Real-time contraindication engine is active.
            </p>
          </div>

          {/* Real-time Penicillin vs Amoxicillin Alert Banner */}
          {hasPenicillinAllergy && penicillinMedConflict && (
            <div
              id="critical-conflict-banner"
              className="p-4 bg-rose-50 border-2 border-rose-500 rounded-2xl text-rose-900 shadow-sm animate-fade-in-up space-y-2"
            >
              <div className="flex items-center gap-2 text-xs font-black text-rose-700 uppercase tracking-wide">
                <AlertTriangle className="w-4 h-4 text-rose-600 animate-bounce" />
                <span>CRITICAL CLINICAL CONFLICT DETECTED</span>
              </div>
              <p className="text-xs leading-relaxed text-rose-900 font-medium">
                Patient has a documented <strong className="underline">Penicillin Allergy</strong>, but the active medication list contains{' '}
                <strong className="underline">{penicillinMedConflict.name || 'a penicillin-class medication'}</strong>.
                Administering this medication carries an acute risk of severe hypersensitivity, acute rash, or life-threatening anaphylaxis.
              </p>
              <div className="text-[11px] font-semibold text-rose-800 bg-rose-100/80 px-2.5 py-1 rounded-lg inline-block">
                Provenance Tag: Alert generated from [User Input Allergy: Penicillins] vs [User Input Medication: {penicillinMedConflict.name}]
              </div>
            </div>
          )}

          {/* Real-time NSAID Conflict Alert */}
          {hasNsaidAllergy && nsaidMedConflict && (
            <div className="p-4 bg-amber-50 border-2 border-amber-500 rounded-2xl text-amber-900 shadow-sm animate-fade-in-up space-y-2">
              <div className="flex items-center gap-2 text-xs font-black text-amber-700 uppercase tracking-wide">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span>CLINICAL WARNING: NSAID HYPERSENSITIVITY</span>
              </div>
              <p className="text-xs leading-relaxed text-amber-900 font-medium">
                Documented <strong className="underline">NSAID Allergy</strong> matches medication{' '}
                <strong className="underline">{nsaidMedConflict.name}</strong>. Risk of acute bronchospasm, urticaria, or cross-reactivity.
              </p>
            </div>
          )}

          {/* Pre-existing Conditions */}
          <div className="space-y-2.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-slate-800 flex items-center gap-2">
                <span>Pre-existing Conditions</span>
                <span className="text-[10px] font-semibold text-slate-400">[User Input]</span>
              </label>
              <span className="text-[11px] text-slate-500 font-medium">
                {selectedConditions.length} selected
              </span>
            </div>

            <div className="flex flex-wrap gap-2">
              {COMMON_CONDITIONS.map((cond) => {
                const isSelected = selectedConditions.includes(cond);
                return (
                  <button
                    key={cond}
                    id={`cond-chip-${cond.toLowerCase().replace(/[^a-z0-9]/g, '-')}`}
                    type="button"
                    onClick={() => toggleCondition(cond)}
                    className={`text-xs px-3 py-1.5 rounded-xl border font-semibold transition-all ${
                      isSelected
                        ? 'bg-clinical-600 text-white border-clinical-600 shadow-sm'
                        : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {cond}
                  </button>
                );
              })}
            </div>

            {/* Custom Condition Input */}
            <div className="flex gap-2 max-w-md pt-1">
              <input
                id="custom-condition-input"
                type="text"
                placeholder="Add other diagnosed condition..."
                value={customCondition}
                onChange={(e) => setCustomCondition(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addCustomCondition();
                  }
                }}
                className="flex-1 px-3 py-1.5 text-xs rounded-xl border border-slate-300 focus:outline-none focus:ring-1 focus:ring-clinical-500"
              />
              <button
                type="button"
                onClick={addCustomCondition}
                className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl border border-slate-300"
              >
                Add
              </button>
            </div>
          </div>

          {/* Drug Allergies */}
          <div className="space-y-2.5 pt-2 border-t border-slate-100">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-slate-800 flex items-center gap-2">
                <span>Known Drug Allergies & Hypersensitivities</span>
                <span className="text-[10px] font-semibold text-rose-600 bg-rose-50 px-1.5 py-0.5 rounded border border-rose-200">
                  Critical Safety
                </span>
              </label>
              <span className="text-[11px] text-slate-500 font-medium">
                {selectedAllergies.length} selected
              </span>
            </div>

            <div className="flex flex-wrap gap-2">
              {COMMON_ALLERGIES.map((allergy) => {
                const isSelected = selectedAllergies.includes(allergy);
                return (
                  <button
                    key={allergy}
                    id={`allergy-chip-${allergy.toLowerCase().replace(/[^a-z0-9]/g, '-')}`}
                    type="button"
                    onClick={() => toggleAllergy(allergy)}
                    className={`text-xs px-3 py-1.5 rounded-xl border font-bold transition-all ${
                      isSelected
                        ? 'bg-rose-600 text-white border-rose-600 shadow-sm'
                        : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {allergy}
                  </button>
                );
              })}
            </div>

            {/* Custom Allergy Input */}
            <div className="flex gap-2 max-w-md pt-1">
              <input
                id="custom-allergy-input"
                type="text"
                placeholder="Add other drug allergy..."
                value={customAllergy}
                onChange={(e) => setCustomAllergy(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addCustomAllergy();
                  }
                }}
                className="flex-1 px-3 py-1.5 text-xs rounded-xl border border-slate-300 focus:outline-none focus:ring-1 focus:ring-clinical-500"
              />
              <button
                type="button"
                onClick={addCustomAllergy}
                className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl border border-slate-300"
              >
                Add
              </button>
            </div>
          </div>

          {/* Current Medications Table */}
          <div className="space-y-3 pt-2 border-t border-slate-100">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <label className="text-xs font-bold text-slate-800 flex items-center gap-2">
                  <span>Current Prescribed Medications</span>
                  <span className="text-[10px] font-semibold text-sky-700 bg-sky-50 px-1.5 py-0.5 rounded">
                    [User Input]
                  </span>
                </label>
                <p className="text-[11px] text-slate-500">
                  Standard Indian prescription frequencies: OD (once/day), BD (twice/day), TDS (thrice/day), SOS (as needed).
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  id="add-medication-btn"
                  type="button"
                  onClick={() => addMedication()}
                  className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-clinical-50 text-clinical-700 border border-clinical-200 text-xs font-bold hover:bg-clinical-100 transition-colors"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Medication Row</span>
                </button>
              </div>
            </div>

            {/* Quick Preset Buttons */}
            <div className="flex flex-wrap items-center gap-1.5 pt-1">
              <span className="text-[10px] font-semibold text-slate-400">Quick Regimens:</span>
              <button
                type="button"
                onClick={() =>
                  addMedication({
                    name: 'Metformin',
                    dosage: '500mg',
                    frequency: 'BD',
                    route: 'Oral',
                  })
                }
                className="text-[10px] px-2 py-0.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-md border border-slate-200"
              >
                + Metformin 500mg BD
              </button>
              <button
                type="button"
                onClick={() =>
                  addMedication({
                    name: 'Telmisartan',
                    dosage: '40mg',
                    frequency: 'OD',
                    route: 'Oral',
                  })
                }
                className="text-[10px] px-2 py-0.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-md border border-slate-200"
              >
                + Telmisartan 40mg OD
              </button>
              <button
                id="preset-amox-btn"
                type="button"
                onClick={() =>
                  addMedication({
                    name: 'Amoxicillin-Clavulanate',
                    dosage: '625mg',
                    frequency: 'TDS',
                    route: 'Oral',
                  })
                }
                className="text-[10px] px-2 py-0.5 bg-amber-50 hover:bg-amber-100 text-amber-800 rounded-md border border-amber-300 font-semibold"
              >
                + Amoxicillin-Clav 625mg TDS (Safety Test)
              </button>
            </div>

            {/* Medications Rows */}
            {medications.length === 0 ? (
              <div className="py-6 text-center border-2 border-dashed border-slate-200 rounded-xl bg-slate-50/50 text-xs text-slate-500">
                No active medications entered. Click <strong>"Add Medication Row"</strong> or select a quick regimen above.
              </div>
            ) : (
              <div className="space-y-2">
                {medications.map((m, idx) => (
                  <div
                    key={idx}
                    className="grid grid-cols-12 gap-2 p-2.5 rounded-xl border border-slate-200 bg-slate-50/60 items-center"
                  >
                    <div className="col-span-12 sm:col-span-4">
                      <input
                        id={`med-name-${idx}`}
                        type="text"
                        placeholder="Drug name (e.g. Amoxicillin)"
                        value={m.name}
                        onChange={(e) => updateMedication(idx, 'name', e.target.value)}
                        className="w-full px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-300 focus:outline-none focus:ring-1 focus:ring-clinical-500 bg-white"
                      />
                    </div>

                    <div className="col-span-4 sm:col-span-3">
                      <input
                        id={`med-dosage-${idx}`}
                        type="text"
                        placeholder="Strength (e.g. 500mg)"
                        value={m.dosage}
                        onChange={(e) => updateMedication(idx, 'dosage', e.target.value)}
                        className="w-full px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-300 focus:outline-none focus:ring-1 focus:ring-clinical-500 bg-white"
                      />
                    </div>

                    <div className="col-span-4 sm:col-span-2">
                      <select
                        id={`med-frequency-${idx}`}
                        value={m.frequency}
                        onChange={(e) => updateMedication(idx, 'frequency', e.target.value)}
                        className="w-full px-2 py-1.5 text-xs font-semibold rounded-lg border border-slate-300 focus:outline-none bg-white"
                      >
                        <option value="OD">OD (Once/day)</option>
                        <option value="BD">BD (Twice/day)</option>
                        <option value="TDS">TDS (Thrice/day)</option>
                        <option value="QID">QID (4x/day)</option>
                        <option value="SOS">SOS (As needed)</option>
                        <option value="HS">HS (Bedtime)</option>
                      </select>
                    </div>

                    <div className="col-span-3 sm:col-span-2">
                      <select
                        id={`med-route-${idx}`}
                        value={m.route}
                        onChange={(e) => updateMedication(idx, 'route', e.target.value)}
                        className="w-full px-2 py-1.5 text-xs font-medium rounded-lg border border-slate-300 focus:outline-none bg-white"
                      >
                        <option value="Oral">Oral</option>
                        <option value="Inhalation">Inhalation</option>
                        <option value="Subcutaneous">Subcutaneous</option>
                        <option value="Topical">Topical</option>
                        <option value="Intravenous">Intravenous</option>
                      </select>
                    </div>

                    <div className="col-span-1 text-right">
                      <button
                        type="button"
                        onClick={() => removeMedication(idx)}
                        className="p-1 text-slate-400 hover:text-rose-600 rounded-md transition-colors"
                        title="Remove row"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* DPDP Act 2023 Consent Checkbox */}
          <div className="pt-4 border-t border-slate-100">
            <label className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 border border-slate-200 cursor-pointer select-none">
              <input
                id="dpdp-consent-checkbox"
                type="checkbox"
                checked={dpdpConsent}
                onChange={(e) => setDpdpConsent(e.target.checked)}
                className="mt-0.5 w-4 h-4 rounded text-clinical-600 focus:ring-clinical-500 border-slate-300 cursor-pointer"
              />
              <div className="space-y-1">
                <span className="text-xs font-bold text-slate-900 block">
                  DPDP Act 2023 Consent & Clinical Information Processing Agreement <span className="text-rose-500">*</span>
                </span>
                <p className="text-[11px] text-slate-600 leading-relaxed">
                  I hereby consent to the collection, extraction, and synthesis of my health data by MedLens in compliance with the
                  <strong> Digital Personal Data Protection (DPDP) Act 2023</strong> and ABDM health data principles. I acknowledge that all
                  clinical interpretations require licensed medical practitioner verification.
                </p>
              </div>
            </label>
          </div>

          {submitError && (
            <div className="p-2.5 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs font-medium flex items-center gap-2">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-600 flex-shrink-0" />
              <span>{submitError}</span>
            </div>
          )}

          {/* Navigation and Final Submit */}
          <div className="flex items-center justify-between pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setStep(2)}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Demographics</span>
            </button>

            <button
              id="complete-onboarding-btn"
              type="button"
              onClick={handleFinalSubmit}
              disabled={submitting}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-clinical-600 hover:from-emerald-700 hover:to-clinical-700 text-white font-bold text-xs shadow-lg shadow-emerald-600/20 transition-all"
            >
              {submitting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Provisioning Clinical Profile...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Complete Registration & Issue Health Card</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* ──────────────────────────────────────────────
          STEP 4: DIGITAL MEDLENS HEALTH CARD (SUCCESS)
         ────────────────────────────────────────────── */}
      {step === 4 && createdPatient && createdIntake && (
        <div className="space-y-6 animate-fade-in-up">
          {/* Digital Health Card */}
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-6 sm:p-8 shadow-2xl border border-slate-700">
            {/* Top Indian Tricolor Ribbon */}
            <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-amber-500 via-white to-emerald-600" />

            {/* Card Background Glow */}
            <div className="absolute top-0 right-0 -mt-10 -mr-10 w-72 h-72 bg-emerald-500/15 rounded-full blur-3xl pointer-events-none" />

            <div className="relative z-10 space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-white/10 border border-white/20 flex items-center justify-center font-black text-emerald-400">
                    ML
                  </div>
                  <div>
                    <h3 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
                      <span>MedLens Digital Health Card</span>
                      <span className="text-[10px] px-2 py-0.2 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                        ABDM Verified
                      </span>
                    </h3>
                    <p className="text-[11px] text-slate-400 font-mono">
                      ID: {createdPatient.id.slice(0, 18)}...
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-xs font-bold text-amber-300">Republic of India</span>
                  <div className="text-[10px] text-slate-400">DPDP 2023 Consented</div>
                </div>
              </div>

              {/* Patient Core Info Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div>
                  <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold block">
                    Patient Name
                  </span>
                  <span id="card-patient-name" className="text-sm sm:text-base font-bold text-white">
                    {createdPatient.name}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold block">
                    Age / Sex
                  </span>
                  <span className="text-sm sm:text-base font-bold text-white">
                    {createdIntake.age} Yrs • {createdPatient.sex}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold block">
                    Mobile (+91)
                  </span>
                  <span className="text-sm sm:text-base font-mono font-bold text-white">
                    {createdPatient.phone || `+91 ${phone}`}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold block">
                    ABHA ID
                  </span>
                  <span className="text-sm sm:text-base font-mono font-bold text-emerald-400">
                    {createdPatient.abha_id || 'Not Linked'}
                  </span>
                </div>
              </div>

              {/* Location & Emergency Contact */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-white/10 text-xs">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">
                    Jurisdiction & Location
                  </span>
                  <span className="text-slate-200 font-semibold">
                    {createdPatient.city || city}, {createdPatient.state || state}, India
                  </span>
                </div>

                {createdPatient.emergency_contact && (
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">
                      Emergency Contact
                    </span>
                    <span className="text-slate-200 font-semibold">
                      {createdPatient.emergency_contact}
                    </span>
                  </div>
                )}
              </div>

              {/* Clinical Profile Chips */}
              <div className="pt-2 border-t border-white/10 space-y-2">
                <div className="flex flex-wrap items-center gap-1.5">
                  <span className="text-[10px] uppercase font-bold text-slate-400 mr-2">
                    Conditions:
                  </span>
                  {createdIntake.existing_conditions.length > 0 ? (
                    createdIntake.existing_conditions.map((c, i) => (
                      <span
                        key={i}
                        className="text-[11px] px-2 py-0.5 rounded-md bg-white/10 text-white font-medium"
                      >
                        {c}
                      </span>
                    ))
                  ) : (
                    <span className="text-[11px] text-slate-400 italic">None reported</span>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-1.5">
                  <span className="text-[10px] uppercase font-bold text-slate-400 mr-2">
                    Allergies:
                  </span>
                  {createdIntake.allergies.length > 0 ? (
                    createdIntake.allergies.map((a, i) => (
                      <span
                        key={i}
                        className="text-[11px] px-2 py-0.5 rounded-md bg-rose-500/20 text-rose-300 font-bold border border-rose-500/30"
                      >
                        {a}
                      </span>
                    ))
                  ) : (
                    <span className="text-[11px] text-slate-400 italic">None reported</span>
                  )}
                </div>
              </div>

              {/* Provenance Badge */}
              <div className="flex items-center justify-between pt-2 border-t border-white/10 text-[10px] text-slate-400">
                <span>Field Provenance: Verified Self-Registration [User Input]</span>
                <span>Audit Trail: INTAKE_CREATED by patient_self_service</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <button
              id="card-upload-pdf-btn"
              onClick={() => onComplete(createdPatient, createdIntake, 'upload')}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-clinical-600 to-sky-600 hover:from-clinical-700 hover:to-sky-700 text-white font-bold text-xs shadow-lg shadow-clinical-600/25 transition-all"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Upload Diagnostic Lab Report (PDF)</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>

            <button
              id="card-view-record-btn"
              onClick={() => onComplete(createdPatient, createdIntake, 'record')}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-white hover:bg-slate-50 text-slate-800 border border-slate-200 font-bold text-xs shadow-sm transition-all"
            >
              <ClipboardList className="w-4 h-4 text-clinical-600" />
              <span>View Unified Patient Record</span>
            </button>

            <button
              onClick={() => {
                setStep(1);
                setPhone('');
                setName('');
                setDob('');
                setAbhaId('');
                setSelectedConditions([]);
                setSelectedAllergies([]);
                setMedications([]);
                setDpdpConsent(false);
                setCreatedPatient(null);
                setCreatedIntake(null);
              }}
              className="w-full sm:w-auto text-xs text-slate-500 hover:text-slate-800 font-semibold px-4 py-2"
            >
              Register Another Patient
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
