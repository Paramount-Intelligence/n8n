# Submission Template — AI Tooling Specialist Assessment

---

## Candidate Information

| Field | Value |
|---|---|
| **Name** | Muaaz Tasawar |
| **Email** | muaaztasawar1@gmail.com |
| **Date** | 13 March 2025 |
| **Assessment** | Enterprise Onboarding Automation — Tasks 1 & 2 |

---

## Overview

This submission presents a complete, production-oriented design for an AI-powered enterprise onboarding automation system, delivered across four structured phases covering workflow logic, prompt engineering, integration architecture, and a working code prototype.

The core design principle is **automation-first, human-in-the-loop by exception**: Claude handles all repetitive processing — field extraction, document classification, plan generation, and communications drafting — while human review is reserved for compliance failures, elevated access requests, and non-standard hire scenarios.

The architecture uses **n8n** as the self-hosted orchestration layer, **Airtable** as the canonical record store, and the **Claude API** for six distinct AI tasks, each with a dedicated production-ready prompt engineered to return deterministic, schema-conformant output. The prototype scaffold demonstrates the end-to-end extraction step as runnable Python code callable from the command line.

All outputs — workflow tables, prompt library, JSON schema, integration map, and code files — are designed to be directly usable by an engineering team to begin implementation without further scoping.

---

## Task 1 — Workflow, AI Usage, Prompt Engineering, Data Flow, and Business Impact

### Workflow Logic (Phase 1)

The pipeline consists of seven sequential stages. Each stage is triggered by completion of the previous one, with human review gates controlling progression at defined checkpoints.

| Stage | Input | AI Task | Output | Human Review |
|---|---|---|---|---|
| **1. Intake** | New hire form / ATS export / HRIS webhook | Extraction — parse raw document into structured JSON | OnboardingRecord stub | ⚠️ If required fields missing or role type ambiguous |
| **2. Validation** | Onboarding record + document manifest | Classification — categorise documents, flag missing/expired, check jurisdiction compliance | Validation JSON with status + issues array | ⚠️ Always on failure or compliance gap |
| **3. Profile Creation** | Validated record + role metadata | Generation — provision accounts across Okta, Slack, Jira, Google Workspace | Active accounts; manager briefing summary | ⚠️ If elevated access or provisioning failure |
| **4. Task Routing** | Employee profile + role attributes | Decision Support — match role to task templates, assign to IT/HR/Facilities/Manager | Task queue in Jira per stakeholder | ⚠️ Senior / multi-jurisdiction hires |
| **5. Onboarding Plan** | Full record + L&D catalogue | Generation + Summarisation — 30/60/90-day plan, manager briefing, training list (3 parallel Claude calls) | Plan markdown + manager summary + training recommendations | ⚠️ Manager approval before sharing with hire |
| **6. Communication** | Approved plan + employee profile | Generation — welcome email, Slack message, day-one pack, calendar invites | All communications dispatched | ⚠️ Executive hires; HR spot-check for standard hires |
| **7. Tracking** | Task/training completion + survey responses | Summarisation + Decision Support — 90-day health monitoring, at-risk detection | Weekly dashboard + manager nudges + HR escalation alerts | ⚠️ Any hire flagged at-risk |

**Human-in-the-loop gates:** 5 mandatory (validation failure, elevated access, plan approval, executive comms, at-risk escalation) + 2 conditional (non-standard task plan, HR comms sampling).

**Design principles:**
- Automation-first, human-in-the-loop by exception
- Fail-safe escalation — any blocked stage raises a flag rather than proceeding
- Auditability — every AI decision logged with inputs, outputs, and timestamps
- Personalisation at scale — plans and comms generated per-hire, not from a single static template

---

### AI Usage (Phase 2)

Six discrete AI tasks are performed using the Claude API. Each has a dedicated system prompt with explicit role instruction, input schema, output schema, field rules, and fallback handling for missing data.

| # | Task | Output Format | Stage | Temperature |
|---|---|---|---|---|
| 1 | Document field extraction | JSON — OnboardingRecord | 1 — Intake | 0.0 |
| 2 | Input validation + missing field detection | JSON — status + issues[] | 2 — Validation | 0.0 |
| 3 | Personalised 30/60/90-day plan generation | Structured Markdown | 5 — Plan | 0.4 |
| 4 | Welcome email draft | Subject line + plain text body | 6 — Comms | 0.6 |
| 5 | Manager summary generation | Markdown briefing | 5 — Plan | 0.3 |
| 6 | Training module recommendation | Ranked list with rationale | 5 — Plan | 0.1 |

Prompts 3, 5, and 6 run in parallel via `Promise.all()` / `asyncio.gather()` once validation passes. Prompts 1 and 2 are strictly sequential.

---

### Prompt Engineering (Phase 2)

All six prompts share a consistent internal contract:

1. **Role instruction** — establishes the model's identity and authority boundary before it sees any data
2. **Task definition** — specifies exactly what the model must do, not how it should think about doing it
3. **Input format specification** — describes the structure and source of the incoming data
4. **Output format** — embeds the full output schema directly in the system prompt for single-call conformant output
5. **Field rules** — normalisation rules (ISO 8601 dates, ISO 4217 currencies, enum classification)
6. **Fallback instructions** — first-class logic for null fields, empty inputs, and unresolvable ambiguity

**Key decisions:**
- Temperature 0.0 for extraction and validation (deterministic, rule-based); up to 0.6 for email drafting (natural language variation needed)
- `null` is always the fallback for missing fields — the model is explicitly instructed never to fabricate plausible values
- The `extraction_notes` array surfaces ambiguities (e.g. P45 present but Starter Checklist missing) without polluting structured fields — this is the most compelling output to show non-technical stakeholders

Full prompt text for all six prompts is in `starter/design-solution.md` — Phase 2 section.

---

### Data Flow (Phase 3)

**Orchestration platform: n8n (self-hosted)**

Selected for: native webhook/polling support, built-in retry and error branch primitives, self-hosted deployment (PII stays within org infrastructure), visual editor for HR ops teams, open-source (no per-execution cost at scale).

**Systems involved:**

| Layer | System | Role |
|---|---|---|
| Intake | Google Forms | New hire intake trigger |
| Intake | ATS (Greenhouse / Lever) | Candidate record export on offer acceptance |
| Intake | HRIS (Workday) | Source of truth for employment data |
| Intake | Google Drive | Document upload store |
| Orchestration | n8n | Central workflow orchestrator |
| Orchestration | Airtable | Canonical OnboardingRecord store |
| Orchestration | Retool | HR dashboard — live pipeline status + review queue |
| AI | Claude API | All six AI tasks |
| Delivery | Gmail | Welcome email + day-one pack |
| Delivery | Slack | Team welcome, buddy intro, manager nudges |
| Delivery | Okta | SSO identity + application access provisioning |
| Delivery | Jira | Onboarding task queue |
| Delivery | LMS | Training module enrolment |
| Delivery | Google Calendar | Day-one schedule + 30/60/90 check-ins |

**Data flow principle:** All inter-stage data moves through Airtable. Nothing passes directly between systems. This makes the pipeline restartable from any point without data loss.

**Error handling — four levels:**

| Level | Where caught | Response |
|---|---|---|
| AI Response | n8n Response Parser | Retry ×3 with backoff; log + HR queue after threshold |
| Validation | n8n Switch node | Pipeline halt; Airtable HR queue; Slack alert |
| Provisioning | n8n Error branch per API | Retry ×3; IT queue; partial provisioning continues |
| Delivery | n8n Error branch Stage 6 | Retry ×3 (10-min backoff); HR queue if unresolved |

Global: any error unresolved after 3 retries or 24 hours → Slack escalation to HR manager + IT lead.

Full JSON schema for the canonical OnboardingRecord is in `starter/design-solution.md` — Phase 3 section.

---

### Business Impact

- **Time-to-productivity:** Eliminates 4–8 hours of manual HR and IT coordinator data re-entry per hire
- **Compliance risk reduction:** Automated document classification catches missing right-to-work docs and jurisdiction gaps before day one
- **Personalisation at scale:** Every hire receives a role- and seniority-specific plan and training list generated in seconds rather than assembled manually
- **At-risk detection:** Surfaces stalled onboarding journeys within the 90-day window where attrition risk is highest
- **Auditability:** Full audit trail on every OnboardingRecord — inputs, outputs, stage timestamps, error log — for compliance review

---

## Task 2 — Prototype Scaffold

### Demo type

Code scaffold + annotated data flow diagram. The prototype demonstrates **Stages 1–2** (Intake and Validation) end-to-end as runnable Python code — the two stages that all downstream processing depends on, and the hardest to get right.

---

### Files included

| File | Description |
|---|---|
| `starter/design-solution.md` | Full Phases 1–3: workflow table, all six prompts, systems inventory, JSON schema, error handling spec |
| `starter/code/onboarding_scaffold.py` | Python extraction helper — calls Claude API, returns enriched OnboardingRecord JSON |
| `starter/diagrams/workflow-overview.md` | Mermaid pipeline diagram, system integration map, AI task map, HITL gate table |
| `SUBMISSION_TEMPLATE.md` | This document |

**Also available (generated during assessment):**
- `sample_input.json` — mock new hire payload (Priya Anand, Senior Product Designer)
- `sample_output.json` — expected enriched OnboardingRecord after AI extraction

---

### Flow of data

1. HR submits a new hire intake form. The payload is represented by `sample_input.json` — structured JSON containing personal details, role, compensation, documents submitted, and free-text notes.
2. `onboarding_scaffold.py` reads the payload and calls `flatten_hire_payload_to_text()`, converting structured JSON into readable plain-text prose — mirroring what production does with real offer letters and ATS exports.
3. The flattened text is sent to the Claude API with the Phase 2 Prompt 1 system prompt at `temperature=0`. Claude extracts all fields, normalises dates and currencies, classifies employment type, and returns a JSON object with an `extraction_notes` array surfacing ambiguities.
4. The response parser strips any markdown formatting and validates the JSON structure.
5. The extraction result is wrapped in the full `OnboardingRecord` schema — adding `record_id`, `meta`, `pipeline_status` (intake complete, all other stages pending), and null placeholders for downstream fields.
6. The enriched record is printed to stdout and optionally written to a JSON file. In production this step is an Airtable API write, which triggers the validation workflow automatically.

---

### Pain points solved

- **Proves extraction before integration work begins.** The hardest part of the pipeline to get right is field extraction from variable-format documents. This prototype validates Claude handles it correctly — including employment type inference and UK-specific document recognition (P45 vs P46 / Starter Checklist).
- **Format-agnostic from day one.** The flatten-then-extract pattern means the same prompt handles Google Forms JSON, raw offer letter text, and ATS exports without format-specific branching.
- **Surfaces compliance observations without explicit rules.** The `extraction_notes` array (e.g. missing Starter Checklist flagged automatically) is the single best demo moment for non-technical stakeholders — it shows the qualitative difference between rules-based and LLM-powered automation.
- **Production-ready schema from step one.** The OnboardingRecord wrapper means the script output flows directly into Airtable without transformation.

---

## Assumptions

1. The organisation uses **Google Workspace** (Gmail, Drive, Calendar) as its productivity suite. Microsoft 365 equivalents (Outlook, OneDrive, Teams) are drop-in substitutes requiring only node-level changes in n8n.
2. **Airtable** is available and accessible via API within the organisation's security perimeter. PostgreSQL or Notion could serve the same role with minor schema adaptation.
3. **n8n is self-hosted** to keep all PII within the organisation's infrastructure. n8n Cloud is a valid alternative if data residency requirements permit.
4. The **Claude API (Anthropic)** is used for all AI tasks. The prompt library is transferable to other OpenAI-compatible endpoints with minimal changes; temperature and max_tokens may need tuning per model.
5. HR administrators submit new hire data via a **structured intake form** (Google Forms or equivalent). The extraction prompt handles unstructured input, but form-based submission reduces ambiguity and improves accuracy.
6. **Buddy assignment and manager plan approval** are performed through the Retool HR dashboard by humans — not automated. These are deliberate HITL gates; automating them would reduce compliance oversight.

---

## Setup Instructions

### Prerequisites
- Python 3.9 or later
- An Anthropic API key — obtain from [console.anthropic.com](https://console.anthropic.com)

### Installation

```bash
cd starter/code
pip install anthropic
```

### Configuration

```bash
# macOS / Linux
export ANTHROPIC_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY = "your_api_key_here"
```

### Run the prototype

```bash
# Print result to stdout
python onboarding_scaffold.py --input sample_input.json

# Save enriched record to file
python onboarding_scaffold.py --input sample_input.json --output result.json
```

### Expected output

The script prints three sections:
1. The flattened document text sent to Claude
2. Confirmation that the API responded and JSON was parsed
3. The full enriched `OnboardingRecord` JSON

**Extraction status will be one of:**
- `COMPLETE` — all required fields found; pipeline may proceed to validation
- `PARTIAL` — some fields missing; check `extraction_notes`
- `FAILED` — document unreadable; human review required

---

## Optional Notes

**On Claude vs GPT-4:** Claude's instruction-following on structured output tasks — particularly the discipline to return `null` for missing fields rather than plausible-sounding fabrications — makes it a strong fit for HR data extraction, where hallucinated values (a wrong start date, an invented cost centre) have real operational consequences. The fallback instruction pattern used in all six prompts exploits this deliberately.

**On the flatten-then-extract pattern:** Converting structured JSON to prose before sending it to Claude may seem redundant. The reason is forward compatibility: in production, most documents arrive as PDFs, scanned images, or copy-pasted email text. Building extraction around unstructured prose input means the same prompt works for all source formats without branching logic.

**On the `extraction_notes` array:** This is the most compelling output to show non-technical stakeholders. In the sample run, the model surfaces that a UK Starter Checklist (P46) is absent despite a P45 being present — a real HMRC compliance gap no static form validation would catch. It also flags the unassigned buddy and the Bristol relocation. None of these required explicit rules.

**On the JSON schema `null` pattern:** All unpopulated downstream fields (`validation_result`, `onboarding_plan`, `communications`, `tracking`) are explicitly `null` rather than absent. This means consumers always check for `null` rather than key absence — reducing defensive coding in n8n function nodes and future API clients.

