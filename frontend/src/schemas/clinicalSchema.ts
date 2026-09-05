import { z } from "zod";

export const ProvenanceSourceEnum = z.enum(["USER_INTAKE", "AI_EXTRACTED", "CLINICIAN_EDITED"]);

export const ClinicalValueSchema = z.object({
  raw: z.string(), // e.g. "<0.01", "145", "Trace", "Negative"
  numericValue: z.number().nullable(),
  operator: z.enum(["<", "<=", ">", ">=", "="]).nullable(),
  unit: z.string().nullable(),
});

export const ReferenceRangeSchema = z.object({
  low: z.number().nullable(),
  high: z.number().nullable(),
  text: z.string().nullable(), // verbatim text from source report (e.g. "0.0 - 5.0", "Negative")
  sourceProvided: z.boolean(), // TRUE only if explicit in the report. NEVER guess or infer.
});

export const LabFlagEnum = z.enum([
  "NORMAL",
  "HIGH",
  "LOW",
  "ABNORMAL_QUALITATIVE",
  "RANGE_NOT_PROVIDED"
]);

export const ObservationSchema = z.object({
  id: z.string().uuid(),
  testName: z.string().min(1),
  category: z.string().default("General"),
  date: z.string().nullable(),
  value: ClinicalValueSchema,
  referenceRange: ReferenceRangeSchema,
  flag: LabFlagEnum,
  provenance: z.object({
    source: ProvenanceSourceEnum,
    pageNumber: z.number().optional(),
    confidence: z.number().min(0).max(1).optional(),
    editedByHuman: z.boolean().default(false),
  }),
});

export const PatientIntakeSchema = z.object({
  age: z.number().int().positive().nullable(),
  sex: z.enum(["male", "female", "other", "prefer_not_to_say"]).nullable(),
  symptoms: z.array(z.string()),
  existingConditions: z.array(z.string()),
  allergies: z.array(z.string()),
  currentMedications: z.array(z.string()),
  notes: z.string().optional(),
});

/**
 * Utility parser that accurately dissects raw clinical results into
 * relational operators, numeric values, and qualitative text.
 */
export function parseClinicalValue(raw: string, unit: string | null = null): z.infer<typeof ClinicalValueSchema> {
  const trimmed = (raw || "").trim();
  if (!trimmed) {
    return { raw: "", numericValue: null, operator: null, unit };
  }

  // Check relational operator prefix: e.g. "<=0.01", "< 0.05", ">= 100", "> 1000", "= 12"
  const opMatch = trimmed.match(/^([<>]=?|=)\s*([0-9]+(?:\.[0-9]+)?)$/);
  if (opMatch) {
    const op = opMatch[1] as "<" | "<=" | ">" | ">=" | "=";
    const num = parseFloat(opMatch[2]);
    return {
      raw: trimmed,
      numericValue: isNaN(num) ? null : num,
      operator: op,
      unit: unit || null
    };
  }

  // Plain numeric
  const plainNumMatch = trimmed.match(/^([0-9]+(?:\.[0-9]+)?)$/);
  if (plainNumMatch) {
    const num = parseFloat(plainNumMatch[1]);
    return {
      raw: trimmed,
      numericValue: isNaN(num) ? null : num,
      operator: null,
      unit: unit || null
    };
  }

  // Qualitative (e.g. Trace, Negative, Positive, Reactive, Non-reactive)
  return {
    raw: trimmed,
    numericValue: null,
    operator: null,
    unit: unit || null
  };
}

/**
 * Parses verbatim reference range text into low/high bounds without guessing.
 */
export function parseReferenceRangeString(rangeText: string | null | undefined): z.infer<typeof ReferenceRangeSchema> {
  if (!rangeText || !rangeText.trim()) {
    return {
      low: null,
      high: null,
      text: null,
      sourceProvided: false
    };
  }

  const clean = rangeText.trim();
  const lower = clean.toLowerCase();

  if (["unavailable", "n/a", "none", "not provided", "range_not_provided", "unknown"].includes(lower)) {
    return {
      low: null,
      high: null,
      text: clean,
      sourceProvided: false
    };
  }

  // Upper bound only: "< 200", "<= 150"
  const ltMatch = clean.match(/^(?:<|<=)\s*([0-9]+(?:\.[0-9]+)?)$/);
  if (ltMatch) {
    return {
      low: null,
      high: parseFloat(ltMatch[1]),
      text: clean,
      sourceProvided: true
    };
  }

  // Lower bound only: "> 40", ">= 50"
  const gtMatch = clean.match(/^(?:>|>=)\s*([0-9]+(?:\.[0-9]+)?)$/);
  if (gtMatch) {
    return {
      low: parseFloat(gtMatch[1]),
      high: null,
      text: clean,
      sourceProvided: true
    };
  }

  // Dual interval: "70 - 99", "0.5 to 1.2"
  const intervalMatch = clean.match(/^([0-9]+(?:\.[0-9]+)?)\s*(?:-|–|—|to)\s*([0-9]+(?:\.[0-9]+)?)$/i);
  if (intervalMatch) {
    return {
      low: parseFloat(intervalMatch[1]),
      high: parseFloat(intervalMatch[2]),
      text: clean,
      sourceProvided: true
    };
  }

  // Qualitative text range: e.g. "Negative", "Non-reactive"
  return {
    low: null,
    high: null,
    text: clean,
    sourceProvided: true
  };
}

/**
 * Deterministically computes FHIR-aligned Lab Flag.
 * Strictly enforces RANGE_NOT_PROVIDED if source document did not specify a reference range.
 */
export function computeFHIRLabFlag(
  value: z.infer<typeof ClinicalValueSchema>,
  range: z.infer<typeof ReferenceRangeSchema>
): z.infer<typeof LabFlagEnum> {
  if (!range.sourceProvided) {
    return "RANGE_NOT_PROVIDED";
  }

  // Handle qualitative values (e.g. Trace, Positive, Reactive)
  const rawLower = value.raw.toLowerCase().trim();
  const normalQuals = ["negative", "non-reactive", "normal", "not detected", "none seen", "absent", "clear"];
  const abnormalQuals = ["positive", "reactive", "abnormal", "detected", "trace", "present", "elevated"];

  if (normalQuals.includes(rawLower)) {
    return "NORMAL";
  }
  if (abnormalQuals.includes(rawLower)) {
    return "ABNORMAL_QUALITATIVE";
  }

  // Handle numeric / relational values
  const num = value.numericValue;
  if (num !== null) {
    // If only upper bound specified (< 200)
    if (range.low === null && range.high !== null) {
      if (value.operator === ">" || value.operator === ">=" || num > range.high) {
        return "HIGH";
      }
      return "NORMAL";
    }

    // If only lower bound specified (> 40)
    if (range.low !== null && range.high === null) {
      if (value.operator === "<" || value.operator === "<=" || num < range.low) {
        return "LOW";
      }
      return "NORMAL";
    }

    // Two-sided range (70 - 99)
    if (range.low !== null && range.high !== null) {
      if (num < range.low) {
        return "LOW";
      }
      if (num > range.high) {
        return "HIGH";
      }
      return "NORMAL";
    }
  }

  // Check if range text indicates qualitative expectation (e.g. "Negative")
  if (range.text) {
    const rangeLower = range.text.toLowerCase().trim();
    if (normalQuals.includes(rangeLower)) {
      if (normalQuals.includes(rawLower)) return "NORMAL";
      if (abnormalQuals.includes(rawLower)) return "ABNORMAL_QUALITATIVE";
    }
  }

  return "RANGE_NOT_PROVIDED";
}
