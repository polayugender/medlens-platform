import React, { useState, useEffect } from 'react';
import {
  UserCheck,
  Plus,
  Trash2,
  Save,
  Clock,
  AlertTriangle,
  History,
  CheckCircle2,
  Pill,
  HeartPulse
} from 'lucide-react';
import { IntakeRecord, MedicationItem } from '../types';
import { ProvenanceBadge } from '../components/ProvenanceBadge';
import { api } from '../api/client';

interface Props {
  patientId: string;
  onIntakeUpdated: () => void;
}

export const IntakeView: React.FC<Props> = ({ patientId, onIntakeUpdated }) => {
  const [currentIntake, setCurrentIntake] = useState<IntakeRecord | null>(null);
  const [history, setHistory] = useState<IntakeRecord[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  // Form states
  const [age, setAge] = useState<number>(45);
  const [sex, setSex] = useState<string>('Female');
  const [symptomInput, setSymptomInput] = useState('');
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [conditionInput, setConditionInput] = useState('');
  const [existingConditions, setExistingConditions] = useState<string[]>([]);
  const [allergyInput, setAllergyInput] = useState('');
  const [allergies, setAllergies] = useState<string[]>([]);
  const [medications, setMedications] = useState<MedicationItem[]>([]);

  const fetchIntakeData = async () => {
    setLoading(true);
    try {
      const [latest, hist] = await Promise.all([
        api.getLatestIntake(patientId),
        api.getIntakeHistory(patientId),
      ]);
      setCurrentIntake(latest);
      setHistory(hist);
      if (latest) {
        populateForm(latest);
        setSelectedVersion(latest.version);
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const populateForm = (record: IntakeRecord) => {
    setAge(record.age);
    setSex(record.sex);
    setSymptoms(record.symptoms || []);
    setExistingConditions(record.existing_conditions || []);
    setAllergies(record.allergies || []);
    setMedications(record.medications || []);
  };

  useEffect(() => {
    fetchIntakeData();
  }, [patientId]);

  const handleSelectVersion = (vNum: number) => {
    setSelectedVersion(vNum);
    const found = history.find((h) => h.version === vNum);
    if (found) {
      populateForm(found);
    }
  };

  // Tag add helpers
  const addSymptom = () => {
    if (symptomInput.trim() && !symptoms.includes(symptomInput.trim())) {
      setSymptoms([...symptoms, symptomInput.trim()]);
      setSymptomInput('');
    }
  };

  const addCondition = () => {
    if (conditionInput.trim() && !existingConditions.includes(conditionInput.trim())) {
      setExistingConditions([...existingConditions, conditionInput.trim()]);
      setConditionInput('');
    }
  };

  const addAllergy = () => {
    if (allergyInput.trim() && !allergies.includes(allergyInput.trim())) {
      setAllergies([...allergies, allergyInput.trim()]);
      setAllergyInput('');
    }
  };

  const addMedication = () => {
    setMedications([
      ...medications,
      { name: '', dosage: '', frequency: '', route: 'Oral' },
    ]);
  };

  const updateMedication = (idx: number, field: keyof MedicationItem, val: string) => {
    const updated = [...medications];
    updated[idx] = { ...updated[idx], [field]: val };
    setMedications(updated);
  };

  const removeMedication = (idx: number) => {
    setMedications(medications.filter((_, i) => i !== idx));
  };

  const handleSaveIntake = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setStatusMsg(null);
    try {
      const validMeds = medications.filter((m) => m.name.trim().length > 0);
      const res = await api.submitIntake(patientId, {
        age: Number(age),
        sex,
        symptoms,
        existing_conditions: existingConditions,
        allergies,
        medications: validMeds,
      });
      setCurrentIntake(res);
      setSelectedVersion(res.version);
      setStatusMsg(`Intake Version ${res.version} recorded successfully!`);
      await fetchIntakeData();
      onIntakeUpdated();
      setTimeout(() => setStatusMsg(null), 4000);
    } catch (err: any) {
      alert(`Failed to save intake: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-xs text-slate-400">Loading intake record...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header & Version Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-lg font-bold text-slate-900">Clinical Patient Intake</h2>
            <ProvenanceBadge source="user_input" size="md" />
          </div>
          <p className="text-xs text-slate-500">
            Self-reported health background, symptoms, medication list, and documented allergies.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {history.length > 1 && (
            <div className="flex items-center gap-1.5 text-xs text-slate-600 bg-slate-50 px-2.5 py-1.5 rounded-lg border border-slate-200">
              <History className="w-3.5 h-3.5 text-slate-400" />
              <span>Version:</span>
              <select
                value={selectedVersion || ''}
                onChange={(e) => handleSelectVersion(Number(e.target.value))}
                className="bg-transparent font-semibold focus:outline-none"
              >
                {history.map((h) => (
                  <option key={h.id} value={h.version}>
                    v{h.version} ({new Date(h.created_at).toLocaleDateString()})
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="text-xs text-slate-400">
            Current: v{currentIntake?.version || 1}
          </div>
        </div>
      </div>

      {statusMsg && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>{statusMsg}</span>
        </div>
      )}

      <form onSubmit={handleSaveIntake} className="space-y-6">
        {/* Demographics Card */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
            <HeartPulse className="w-4 h-4 text-clinical-600" />
            <h3 className="text-sm font-bold text-slate-900">Patient Baseline Demographics</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Current Age</label>
              <input
                id="intake-age"
                type="number"
                required
                min={0}
                max={130}
                value={age}
                onChange={(e) => setAge(Number(e.target.value))}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-clinical-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Biological Sex</label>
              <select
                id="intake-sex"
                value={sex}
                onChange={(e) => setSex(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-clinical-500 focus:outline-none bg-white"
              >
                <option value="Female">Female</option>
                <option value="Male">Male</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
        </div>

        {/* Symptoms & Conditions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Symptoms */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
            <h3 className="text-sm font-bold text-slate-900">Reported Symptoms</h3>
            <div className="flex gap-2">
              <input
                id="symptom-input"
                type="text"
                placeholder="e.g. Fatigue, Dizziness"
                value={symptomInput}
                onChange={(e) => setSymptomInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSymptom())}
                className="flex-1 px-3 py-1.5 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-clinical-500 focus:outline-none"
              />
              <button
                id="add-symptom-btn"
                type="button"
                onClick={addSymptom}
                className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5 min-h-[40px] pt-1">
              {symptoms.map((s, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-2.5 py-1 bg-slate-100 text-slate-800 text-xs rounded-full font-medium"
                >
                  <span>{s}</span>
                  <button
                    type="button"
                    onClick={() => setSymptoms(symptoms.filter((_, i) => i !== idx))}
                    className="text-slate-400 hover:text-slate-600 ml-0.5"
                  >
                    ×
                  </button>
                </span>
              ))}
              {symptoms.length === 0 && (
                <span className="text-xs text-slate-400 italic">No symptoms entered</span>
              )}
            </div>
          </div>

          {/* Existing Conditions */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
            <h3 className="text-sm font-bold text-slate-900">Existing Clinical Diagnoses</h3>
            <div className="flex gap-2">
              <input
                id="condition-input"
                type="text"
                placeholder="e.g. Essential Hypertension, Type 2 Diabetes"
                value={conditionInput}
                onChange={(e) => setConditionInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCondition())}
                className="flex-1 px-3 py-1.5 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-clinical-500 focus:outline-none"
              />
              <button
                id="add-condition-btn"
                type="button"
                onClick={addCondition}
                className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5 min-h-[40px] pt-1">
              {existingConditions.map((c, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-2.5 py-1 bg-sky-50 text-sky-800 border border-sky-200 text-xs rounded-full font-medium"
                >
                  <span>{c}</span>
                  <button
                    type="button"
                    onClick={() => setExistingConditions(existingConditions.filter((_, i) => i !== idx))}
                    className="text-sky-400 hover:text-sky-600 ml-0.5"
                  >
                    ×
                  </button>
                </span>
              ))}
              {existingConditions.length === 0 && (
                <span className="text-xs text-slate-400 italic">No conditions entered</span>
              )}
            </div>
          </div>
        </div>

        {/* Known Allergies (Crucial for safety cross-check) */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <h3 className="text-sm font-bold text-slate-900">Documented Allergies & Sensitivities</h3>
            </div>
            <span className="text-[11px] text-amber-700 font-medium bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
              Cross-checked against medications
            </span>
          </div>

          <div className="flex gap-2">
            <input
              id="allergy-input"
              type="text"
              placeholder="e.g. Penicillin, Sulfa drugs, Aspirin, Latex"
              value={allergyInput}
              onChange={(e) => setAllergyInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addAllergy())}
              className="flex-1 px-3 py-1.5 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:outline-none"
            />
            <button
              id="add-allergy-btn"
              type="button"
              onClick={addAllergy}
              className="px-3 py-1.5 bg-amber-100 hover:bg-amber-200 text-amber-800 text-xs font-semibold rounded-lg transition-colors"
            >
              Add Allergy
            </button>
          </div>

          <div className="flex flex-wrap gap-1.5 min-h-[36px] pt-1">
            {allergies.map((a, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1 px-2.5 py-1 bg-amber-50 text-amber-900 border border-amber-300 text-xs rounded-full font-semibold"
              >
                <span>{a}</span>
                <button
                  type="button"
                  onClick={() => setAllergies(allergies.filter((_, i) => i !== idx))}
                  className="text-amber-500 hover:text-amber-700 ml-0.5"
                >
                  ×
                </button>
              </span>
            ))}
            {allergies.length === 0 && (
              <span className="text-xs text-slate-400 italic">No allergies recorded</span>
            )}
          </div>
        </div>

        {/* Active Medications List */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <Pill className="w-4 h-4 text-clinical-600" />
              <h3 className="text-sm font-bold text-slate-900">Current Active Medications</h3>
            </div>
            <button
              type="button"
              onClick={addMedication}
              className="inline-flex items-center gap-1 px-3 py-1 bg-clinical-50 hover:bg-clinical-100 text-clinical-700 text-xs font-semibold rounded-lg border border-clinical-200"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Medication</span>
            </button>
          </div>

          {medications.length === 0 ? (
            <div className="text-center py-6 text-xs text-slate-400">
              No active medications logged. Click "Add Medication" to include prescriptions or supplements.
            </div>
          ) : (
            <div className="space-y-2.5">
              {medications.map((med, idx) => (
                <div
                  key={idx}
                  className="grid grid-cols-1 sm:grid-cols-12 gap-2 p-3 bg-slate-50 rounded-lg border border-slate-200/80 items-center"
                >
                  <div className="sm:col-span-4">
                    <label className="block text-[10px] uppercase font-bold text-slate-500 mb-0.5">
                      Medication Name
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Lisinopril, Metformin"
                      value={med.name}
                      onChange={(e) => updateMedication(idx, 'name', e.target.value)}
                      className="w-full px-2.5 py-1.5 text-xs bg-white border border-slate-200 rounded focus:ring-1 focus:ring-clinical-500 focus:outline-none"
                    />
                  </div>
                  <div className="sm:col-span-3">
                    <label className="block text-[10px] uppercase font-bold text-slate-500 mb-0.5">
                      Dosage
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. 10mg, 500mg"
                      value={med.dosage || ''}
                      onChange={(e) => updateMedication(idx, 'dosage', e.target.value)}
                      className="w-full px-2.5 py-1.5 text-xs bg-white border border-slate-200 rounded focus:ring-1 focus:ring-clinical-500 focus:outline-none"
                    />
                  </div>
                  <div className="sm:col-span-3">
                    <label className="block text-[10px] uppercase font-bold text-slate-500 mb-0.5">
                      Frequency
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Once daily, TID"
                      value={med.frequency || ''}
                      onChange={(e) => updateMedication(idx, 'frequency', e.target.value)}
                      className="w-full px-2.5 py-1.5 text-xs bg-white border border-slate-200 rounded focus:ring-1 focus:ring-clinical-500 focus:outline-none"
                    />
                  </div>
                  <div className="sm:col-span-2 flex items-center justify-end pt-3 sm:pt-0">
                    <button
                      type="button"
                      onClick={() => removeMedication(idx)}
                      className="p-1.5 text-rose-500 hover:text-rose-700 hover:bg-rose-50 rounded"
                      title="Remove medication"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Submit Actions */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            id="save-intake-btn"
            type="submit"
            disabled={saving}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-clinical-600 hover:bg-clinical-700 active:bg-clinical-800 text-white text-xs font-bold rounded-xl shadow-sm transition-all disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving Intake Version...' : 'Save & Increment Intake Version'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
