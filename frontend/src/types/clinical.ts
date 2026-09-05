import { z } from "zod";
import {
  ProvenanceSourceEnum,
  ClinicalValueSchema,
  ReferenceRangeSchema,
  LabFlagEnum,
  ObservationSchema,
  PatientIntakeSchema,
} from "../schemas/clinicalSchema";

export type ProvenanceSource = z.infer<typeof ProvenanceSourceEnum>;
export type ClinicalValue = z.infer<typeof ClinicalValueSchema>;
export type ReferenceRange = z.infer<typeof ReferenceRangeSchema>;
export type LabFlag = z.infer<typeof LabFlagEnum>;
export type Observation = z.infer<typeof ObservationSchema>;
export type PatientIntake = z.infer<typeof PatientIntakeSchema>;

export interface ClinicalProvenance {
  source: ProvenanceSource;
  pageNumber?: number;
  confidence?: number;
  editedByHuman: boolean;
  auditorId?: string;
  editedAt?: string;
}
