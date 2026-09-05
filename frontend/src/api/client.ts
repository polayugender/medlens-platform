import {
  Patient,
  IntakeRecord,
  MedicalReport,
  ExtractedTest,
  Summary,
  AuditLog,
  ClinicalConflict,
  TestTrendGroup
} from '../types';

const API_BASE = '/api';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = 'Request failed';
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
    } catch {
      errorDetail = `HTTP Error ${res.status}: ${res.statusText}`;
    }
    throw new Error(errorDetail);
  }
  if (res.status === 204) {
    return {} as T;
  }
  return res.json();
}

export const api = {
  // Patients
  async getPatients(): Promise<Patient[]> {
    const res = await fetch(`${API_BASE}/patients`);
    return handleResponse<Patient[]>(res);
  },

  async getPatient(id: string): Promise<Patient> {
    const res = await fetch(`${API_BASE}/patients/${id}`);
    return handleResponse<Patient>(res);
  },

  async createPatient(payload: { name: string; dob: string; sex: string }): Promise<Patient> {
    const res = await fetch(`${API_BASE}/patients`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<Patient>(res);
  },

  // Intake
  async getLatestIntake(patientId: string): Promise<IntakeRecord | null> {
    const res = await fetch(`${API_BASE}/patients/${patientId}/intake`);
    return handleResponse<IntakeRecord | null>(res);
  },

  async getIntakeHistory(patientId: string): Promise<IntakeRecord[]> {
    const res = await fetch(`${API_BASE}/patients/${patientId}/intake/history`);
    return handleResponse<IntakeRecord[]>(res);
  },

  async submitIntake(
    patientId: string,
    payload: {
      age: number;
      sex: string;
      symptoms: string[];
      existing_conditions: string[];
      allergies: string[];
      medications: { name: string; dosage?: string; frequency?: string; route?: string }[];
    }
  ): Promise<IntakeRecord> {
    const res = await fetch(`${API_BASE}/patients/${patientId}/intake`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<IntakeRecord>(res);
  },

  // Reports
  async getReports(patientId: string): Promise<MedicalReport[]> {
    const res = await fetch(`${API_BASE}/patients/${patientId}/reports`);
    return handleResponse<MedicalReport[]>(res);
  },

  async getReportDetails(reportId: string): Promise<{
    report: MedicalReport;
    tests: ExtractedTest[];
    previews: string[];
  }> {
    const res = await fetch(`${API_BASE}/reports/${reportId}`);
    return handleResponse<{
      report: MedicalReport;
      tests: ExtractedTest[];
      previews: string[];
    }>(res);
  },

  async uploadReport(patientId: string, file: File): Promise<MedicalReport> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/patients/${patientId}/reports`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<MedicalReport>(res);
  },

  async deleteReport(reportId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/reports/${reportId}`, {
      method: 'DELETE',
    });
    return handleResponse<void>(res);
  },

  // Tests & Extraction
  async getTests(
    patientId: string,
    filters?: { verified?: boolean; report_id?: string }
  ): Promise<ExtractedTest[]> {
    const params = new URLSearchParams();
    if (filters?.verified !== undefined) params.append('verified', String(filters.verified));
    if (filters?.report_id) params.append('report_id', filters.report_id);

    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/patients/${patientId}/tests${query}`);
    return handleResponse<ExtractedTest[]>(res);
  },

  async updateTest(
    testId: string,
    payload: {
      test_name?: string;
      value?: string;
      unit?: string;
      reference_range_raw?: string;
      verified?: boolean;
    },
    actor = 'User'
  ): Promise<ExtractedTest> {
    const res = await fetch(`${API_BASE}/tests/${testId}?actor=${encodeURIComponent(actor)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<ExtractedTest>(res);
  },

  async verifyBatch(
    patientId: string,
    tests: {
      id: string;
      test_name: string;
      value: string;
      value_numeric?: number | null;
      unit?: string | null;
      reference_range_raw?: string | null;
    }[],
    verifiedBy = 'Clinician Reviewer'
  ): Promise<ExtractedTest[]> {
    const res = await fetch(`${API_BASE}/patients/${patientId}/tests/verify-batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ verified_by: verifiedBy, tests }),
    });
    return handleResponse<ExtractedTest[]>(res);
  },

  async deleteTest(testId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/tests/${testId}`, {
      method: 'DELETE',
    });
    return handleResponse<void>(res);
  },

  // Summary
  async getSummary(patientId: string): Promise<Summary | null> {
    const res = await fetch(`${API_BASE}/patients/${patientId}/summary`);
    return handleResponse<Summary | null>(res);
  },

  async generateSummary(patientId: string): Promise<Summary> {
    const res = await fetch(`${API_BASE}/patients/${patientId}/summary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patient_id: patientId, regenerate: true }),
    });
    return handleResponse<Summary>(res);
  },

  // Audit Logs
  async getAuditLogs(patientId: string): Promise<AuditLog[]> {
    const res = await fetch(`${API_BASE}/patients/${patientId}/audit-logs`);
    return handleResponse<AuditLog[]>(res);
  },

  // Analytics & Conflicts
  async getConflicts(patientId: string): Promise<{ conflicts: ClinicalConflict[]; total: number }> {
    const res = await fetch(`${API_BASE}/patients/${patientId}/conflicts`);
    return handleResponse<{ conflicts: ClinicalConflict[]; total: number }>(res);
  },

  async getTrends(patientId: string): Promise<TestTrendGroup[]> {
    const res = await fetch(`${API_BASE}/patients/${patientId}/trends`);
    return handleResponse<TestTrendGroup[]>(res);
  },

  async getExportData(patientId: string, format = "json"): Promise<any> {
    const res = await fetch(`${API_BASE}/patients/${patientId}/export?format=${format}`);
    return handleResponse<any>(res);
  },

  async downloadExportPDF(patientId: string, patientName: string): Promise<void> {
    const res = await fetch(`${API_BASE}/patients/${patientId}/export?format=pdf`);
    if (!res.ok) throw new Error(`PDF export failed with status ${res.status}`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `MedLens_${patientName.replace(/\s+/g, '_')}_Clinical_Record.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },

  async downloadExportJSON(patientId: string, patientName: string): Promise<void> {
    const data = await this.getExportData(patientId, "json");
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `MedLens_${patientName.replace(/\s+/g, '_')}_Record.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },
};
