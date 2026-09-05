# MedLens — AI-Powered Clinical Information Intelligence

MedLens is a production-grade clinical intelligence platform that transforms fragmented patient information (patient-reported intake forms + uploaded laboratory reports) into a unified, source-traceable, verified patient record with an AI-generated plain-language summary.

> [!IMPORTANT]
> **Core Clinical Invariant**: MedLens is an **information-organization and provenance system**, *not* a diagnostic tool. It synthesizes health records while strictly adhering to zero data fabrication, field-level provenance, and deterministic flag computation.

---

## 🛡️ Responsible AI: What the System Will and Will Not Do

| What MedLens **WILL** Do | What MedLens **WILL NOT** Do |
| :--- | :--- |
| ✅ **Extract verbatim lab markers, units, dates, and reference ranges** directly printed on uploaded reports. | ❌ **Never guess or infer reference ranges** from general medical training. If missing from the source document, it is explicitly marked `range_unavailable`. |
| ✅ **Compute Low / Normal / High flags deterministically** solely using the reference range printed on the same laboratory report. | ❌ **Never predict or hallucinate clinical flags** via probabilistic LLM guessing. |
| ✅ **Tag every field with immutable provenance**: `user_input`, `ai_extracted`, or `ai_generated`. | ❌ **Never obscure the origin of data.** The UI visually displays distinct badges, icons, and audit tooltips for every field. |
| ✅ **Enforce Human-in-the-Loop verification** before any extracted test enters the official verified clinical record. | ❌ **Never automatically treat AI extractions as final verified truth** without clinician or patient confirmation. |
| ✅ **Summarize values strictly in relation to stated lab ranges** in accessible plain language with a hardcoded disclaimer banner. | ❌ **Never diagnose diseases, suggest clinical causes, recommend treatments, or adjust medication dosages.** |
| ✅ **Detect safety contradictions** (e.g. reported penicillin allergy conflicting with active amoxicillin prescription). | ❌ **Never replace clinical judgment.** All alerts are surfaced as prompts for physician evaluation. |

---

## 📍 Where AI Guardrails Live in the Code

MedLens enforces safety at multiple structural and programmatic layers:

1. **System Prompt Guardrails & Strict JSON Schema**:
   - Extraction contract: [`backend/app/core/prompts.py`](file:///backend/app/core/prompts.py) (`EXTRACTION_SYSTEM_PROMPT`) enforces verbatim extraction, null for unstated bounds, zero approximation, and verbatim `raw_snippet` quotes.
   - Summarization contract: [`backend/app/core/prompts.py`](file:///backend/app/core/prompts.py) (`SUMMARY_SYSTEM_PROMPT`) forbids diagnosis, forbids treatments, enforces factual comparison against ranges, and mandates physician consultation advice.
2. **Deterministic Flag Computation Engine**:
   - [`backend/app/core/flag_calculator.py`](file:///backend/app/core/flag_calculator.py) (`compute_flag`, `parse_reference_range`): Algorithmic evaluation ensuring flags (`low`, `normal`, `high`, `unavailable`) are computed from source intervals, never guessed.
3. **Field-Level Provenance & Audit Logging**:
   - Provenance enums: [`backend/app/core/provenance.py`](file:///backend/app/core/provenance.py) (`SourceProvenance.USER_INPUT`, `AI_EXTRACTED`, `AI_GENERATED`).
   - Append-only audit logger: [`backend/app/services/audit_service.py`](file:///backend/app/services/audit_service.py) logging actor, action, before/after states.
4. **Clinical Safety Contradiction Detector**:
   - Cross-check engine: [`backend/app/services/conflict_detector.py`](file:///backend/app/services/conflict_detector.py) scanning allergy lists against active medication classes.
5. **UI-Level Safety Disclaimers**:
   - Hardcoded persistent banner: [`frontend/src/components/DisclaimerBanner.tsx`](file:///frontend/src/components/DisclaimerBanner.tsx).
   - Visual provenance chips: [`frontend/src/components/ProvenanceBadge.tsx`](file:///frontend/src/components/ProvenanceBadge.tsx).
   - Multi-sensory flags (color + text + icon): [`frontend/src/components/FlagBadge.tsx`](file:///frontend/src/components/FlagBadge.tsx).

---

## 🏛️ System Architecture

```
MedLens Platform
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI routers (patients, intake, reports, extraction, summary, audit, analytics)
│   │   ├── core/            # Prompts, flag calculator, provenance enums
│   │   ├── db/              # Async SQLite engine with SQLAlchemy 2.0 (Postgres compatible)
│   │   ├── models/          # Patient, IntakeRecord, MedicalReport, ExtractedTest, Summary, AuditLog
│   │   ├── schemas/         # Pydantic v2 schemas and strict extraction contracts
│   │   └── services/        # PyMuPDF parser, AI extractor (Claude + offline parser), summarizer, conflict detector
│   ├── seed/
│   │   ├── generate_sample_pdfs.py  # ReportLab generator for realistic clinical PDFs
│   │   └── seed_data.py             # Seeds 3 demo patients (Eleanor Vance, Arthur Pendelton, Maya Rodriguez)
│   └── tests/               # Pytest suite + live API integration test
└── frontend/
    ├── src/
    │   ├── api/             # Typed API client
    │   ├── components/      # Navbar, DisclaimerBanner, ProvenanceBadge, FlagBadge, PatientListModal
    │   ├── views/           # Unified Record, Review & Verify, Intake, Upload, Side-by-Side, Trends, Conflicts, Audit
    │   ├── types/           # TypeScript contracts
    │   └── index.css        # Clinical Tailwind design system tokens
    ├── tailwind.config.js
    └── vite.config.ts
```

---

## 🚀 Quickstart & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Node.js 18+ (tested on Node.js 20)

### 1. Backend Setup
```bash
cd backend
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Run database seed script (generates sample clinical PDFs and demo patients):
$env:PYTHONPATH = "backend"
python seed/seed_data.py

# Start backend server:
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Backend API will be available at `http://127.0.0.1:8000` (Swagger docs at `/docs`).

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend application will be accessible at `http://localhost:5173`.

### 3. Automated Tests
```bash
# Run unit tests:
.\backend\venv\Scripts\pytest backend/tests

# Run live API integration test against running server:
.\backend\venv\Scripts\python backend/tests/verify_live_api.py
```

---

## 🧪 Demo Patient Walkthrough

1. **Eleanor Vance (Age 48, Female)**:
   - **Unified Record**: Synthesizes a Comprehensive Metabolic Panel (CMP) and Lipid Profile. Shows elevated Fasting Glucose (128 mg/dL [70-99]) and Total Cholesterol (228 mg/dL [< 200]).
   - **Safety Conflict Alert**: Cross-checks her reported Penicillin allergy against active Amoxicillin medication, immediately flagging a beta-lactam allergy alert!
2. **Arthur Pendelton (Age 63, Male)**:
   - **Human-in-the-Loop Review**: Newly uploaded Complete Blood Count (CBC) report awaiting verification. Navigate to the **Review & Verify** tab to inspect raw document snippets, edit values, and click **Verify All**.
3. **Maya Rodriguez (Age 34, Female)**:
   - Fresh patient profile with intake background ready for testing report uploads.
