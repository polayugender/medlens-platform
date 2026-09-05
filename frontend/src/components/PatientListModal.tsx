import React, { useState } from 'react';
import { X, UserPlus } from 'lucide-react';
import { api } from '../api/client';
import { Patient } from '../types';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onPatientCreated: (patient: Patient) => void;
}

export const PatientListModal: React.FC<Props> = ({
  isOpen,
  onClose,
  onPatientCreated,
}) => {
  const [name, setName] = useState('');
  const [dob, setDob] = useState('1985-05-12');
  const [sex, setSex] = useState('Female');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Patient name is required');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const created = await api.createPatient({ name, dob, sex });
      onPatientCreated(created);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to create patient');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-clinical-50 text-clinical-600 rounded-lg">
              <UserPlus className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Add New Patient</h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Full Legal Name
            </label>
            <input
              id="new-patient-name"
              type="text"
              required
              placeholder="e.g. Sarah Jenkins"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-clinical-500 focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Date of Birth
              </label>
              <input
                id="new-patient-dob"
                type="date"
                required
                value={dob}
                onChange={(e) => setDob(e.target.value)}
                className="w-full px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-clinical-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Biological Sex
              </label>
              <select
                id="new-patient-sex"
                value={sex}
                onChange={(e) => setSex(e.target.value)}
                className="w-full px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-clinical-500 focus:outline-none bg-white"
              >
                <option value="Female">Female</option>
                <option value="Male">Male</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              id="submit-patient-btn"
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-clinical-600 hover:bg-clinical-700 text-white text-xs font-semibold rounded-lg shadow-sm disabled:opacity-50 transition-colors"
            >
              {loading ? 'Creating...' : 'Create Patient Record'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
