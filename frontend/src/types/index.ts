export type ProvenanceSource = 'user_input' | 'ai_extracted' | 'ai_generated';

export type FlagType = 'low' | 'normal' | 'high' | 'unavailable';

export interface MedicationItem {
  name: string;
  dosage?: string;
  frequency?: string;
  route?: string;
}

export interface Patient {
  id: string;
  name: string;
  dob: string;
  sex: string;
  phone?: string;
  abha_id?: string;
  state?: string;
  city?: string;
  emergency_contact?: string;
  created_at: string;
  updated_at: string;
}

export interface IntakeRecord {
  id: string;
  patient_id: string;
  version: number;
  age: number;
  sex: string;
  symptoms: string[];
  existing_conditions: string[];
  allergies: string[];
  medications: MedicationItem[];
  source: 'user_input';
  created_at: string;
}

export interface MedicalReport {
  id: string;
  patient_id: string;
  original_filename: string;
  file_url: string;
  file_type: string;
  report_date?: string;
  report_type?: string;
  facility_name?: string;
  raw_text?: string;
  page_count: number;
  uploaded_at: string;
  test_count?: number;
}

export interface ExtractedTest {
  id: string;
  report_id: string;
  patient_id: string;
  test_name: string;
  value: string;
  value_numeric?: number | null;
  unit?: string | null;
  reference_range_raw?: string | null;
  reference_range_low?: number | null;
  reference_range_high?: number | null;
  flag: FlagType;
  source: 'ai_extracted';
  verified: boolean;
  verified_by?: string | null;
  verified_at?: string | null;
  raw_snippet?: string | null;
  confidence_score: number;
  location_meta?: {
    page?: number;
    line_number?: number;
  };
  created_at: string;
  updated_at: string;
}

export interface Summary {
  id: string;
  patient_id: string;
  version: number;
  summary_text: string;
  based_on_report_ids: string[];
  based_on_intake_version?: number | null;
  source: 'ai_generated';
  generated_at: string;
  disclaimer: string;
}

export interface AuditLog {
  id: string;
  patient_id: string;
  actor: string;
  action: string;
  entity: string;
  entity_id: string;
  before_state?: Record<string, any> | null;
  after_state?: Record<string, any> | null;
  timestamp: string;
}

export interface ClinicalConflict {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  category: string;
  title: string;
  description: string;
  source_a: string;
  source_b: string;
  action_needed: string;
}

export interface TrendPoint {
  test_id: string;
  date: string;
  value: number;
  unit?: string;
  reference_range_low?: number | null;
  reference_range_high?: number | null;
  flag: FlagType;
  verified: boolean;
  report_name: string;
}

export interface TestTrendGroup {
  test_name: string;
  points_count: number;
  unit?: string;
  points: TrendPoint[];
}
