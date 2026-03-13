# AI-Powered Onboarding Automation — Phase 4: Prototype Scaffold

**Assessment Type:** Enterprise Onboarding Automation  
**Phase:** 4 — Prototype Scaffold (Task 2)  
**Status:** Complete  
**Deliverables:** Prototype flow description, n8n workflow spec, extraction script, sample input, sample output

---

## 1. Prototype Flow Description

The prototype isolates and demonstrates **Stage 1 (Intake) through Stage 2 (Validation)** of the full seven-stage pipeline — the two highest-value stages to prove before building the rest, since everything downstream depends on the quality of the extracted record.

### Step-by-step flow

**Step 1 — Trigger**  
An HR administrator submits a new hire intake form via Google Forms. The form submission fires a webhook that triggers the n8n `intake` workflow. For prototype purposes, the trigger is simulated by posting a JSON payload directly to an n8n webhook node.

**Step 2 — Payload assembly**  
n8n receives the raw form data and passes it to a Code node that flattens the structured JSON into a readable plain-text document string. This mimics what would happen in production when unstructured documents (offer letters, ATS exports) are concatenated into a single input.

**Step 3 — AI extraction (Claude API — Prompt 1)**  
The flattened document text is passed to the Claude API using the Phase 2 extraction system prompt. Claude reads the text, classifies all fields, normalises dates and currencies, and returns a single JSON object conforming to the extraction schema. The `extraction_status` field indicates whether extraction was `complete`, `partial`, or `failed`.

**Step 4 — Response parsing and validation**  
n8n receives the Claude response and runs it through a Function node that: (a) strips any markdown formatting, (b) parses the JSON, (c) checks all required fields are present, and (d) flags any `null` values in blocking fields. If parsing fails, the error is logged and the workflow branches to the HR alert path.

**Step 5 — Record creation in Airtable**  
The parsed extraction result is wrapped in the full `OnboardingRecord` schema (adding `record_id`, `meta`, `pipeline_status`, and empty downstream fields) and written to Airtable as a new row. The record's `pipeline_status.current_stage` is set to `"intake"` and Stage 1 is marked `"complete"`.

**Step 6 — Automatic validation trigger**  
Airtable's automation detects the new record and fires a second n8n webhook, triggering the `validation` workflow. The validation workflow fetches the onboarding record and the document manifest from Google Drive, then calls Claude again with Prompt 2.

**Step 7 — Human review routing**  
If `validation_status` is `"failed"` or `human_review_required` is `true`, n8n posts an alert to the HR Slack channel with a direct link to the record in Retool. The pipeline pauses. If validation passes, the workflow updates the Airtable record status to `"validation_complete"` and signals readiness for Stage 3.

---

## 2. n8n Workflow Description

### Workflow A: `onboarding_intake`

**Trigger:** Webhook — POST from Google Forms or manual test payload

| # | Node Name | Node Type | What It Does |
|---|---|---|---|
| 1 | `webhook_intake_trigger` | Webhook | Listens for POST requests from Google Forms / ATS. Receives raw hire payload JSON. Responds 200 immediately to avoid timeout. |
| 2 | `set_run_metadata` | Set | Attaches execution metadata: `run_id`, `triggered_at` timestamp, `source_system` from payload `_source` field. |
| 3 | `flatten_to_document_text` | Code (JS) | Iterates over the hire payload object and builds a readable plain-text document string. Handles null fields gracefully by omitting them. Returns `{ document_text: string }`. |
| 4 | `call_claude_extraction` | HTTP Request | POSTs to `https://api.anthropic.com/v1/messages` with the extraction system prompt and flattened document text as the user message. Uses `ANTHROPIC_API_KEY` from n8n credentials store. Sets `temperature: 0`, `max_tokens: 2048`. |
| 5 | `parse_extraction_response` | Code (JS) | Strips any markdown fences from the response. Parses the JSON. Validates that `extraction_status`, `employee`, and `employment` keys are present. Throws if malformed. |
| 6 | `check_extraction_status` | Switch | Routes on `extraction_status`: `complete` → node 7. `partial` → node 7 with warning flag set. `failed` → node 9 (error path). |
| 7 | `build_onboarding_record` | Code (JS) | Wraps extracted data in full `OnboardingRecord` schema. Generates `record_id` (format: `ONB-YYYY-NNNN`). Sets `pipeline_status.intake.status = "complete"`. |
| 8 | `write_to_airtable` | Airtable | Creates new row in `OnboardingRecords` table with the full record JSON. Returns `airtable_record_id` for downstream reference. |
| 9 | `log_extraction_error` | Airtable | (Error path) Writes to `ErrorLog` table: `stage: "intake"`, `error_type: "extraction_failed"`, raw Claude response, timestamp. |
| 10 | `alert_hr_slack_on_failure` | Slack | (Error path) Posts to `#hr-onboarding-ops` channel: hire name, record ID, error summary, link to Retool review queue. |

---

### Workflow B: `onboarding_validation`

**Trigger:** Airtable automation webhook — fires when a new `OnboardingRecord` row is created with `pipeline_status.current_stage = "intake"`

| # | Node Name | Node Type | What It Does |
|---|---|---|---|
| 1 | `webhook_validation_trigger` | Webhook | Receives Airtable record ID from automation trigger. |
| 2 | `fetch_onboarding_record` | Airtable | Reads full `OnboardingRecord` from Airtable using record ID. |
| 3 | `fetch_document_manifest` | Google Drive | Lists files in the hire's Google Drive folder (folder ID stored on the Airtable record). Returns file name, upload date, and file metadata. |
| 4 | `build_document_manifest_json` | Code (JS) | Converts Drive file list into the `document_manifest` JSON array format required by Prompt 2. Matches filenames to document type categories using a lookup table. |
| 5 | `call_claude_validation` | HTTP Request | POSTs to Claude API with the validation system prompt. Injects `onboarding_record` and `document_manifest` JSON, plus `STANDARD_REGIONS` and `ELEVATED_ACCESS_ROLES` from n8n environment variables. `temperature: 0`. |
| 6 | `parse_validation_response` | Code (JS) | Parses Claude's validation JSON response. Validates schema. Extracts `validation_status`, `missing_fields`, `document_issues`, `human_review_required`. |
| 7 | `update_airtable_validation_result` | Airtable | Writes `validation_result` object back to the `OnboardingRecord` row. Updates `pipeline_status.validation.status`. |
| 8 | `check_validation_outcome` | Switch | Routes on `validation_status`: `passed` → node 11 (proceed). `passed_with_warnings` → node 10 (warn + proceed). `failed` → node 9 (block). |
| 9 | `block_pipeline` | Airtable + Slack | Sets `pipeline_status.current_stage = "blocked"`. Creates task in Airtable `HRQueue` table. Posts Slack alert to `#hr-onboarding-ops` with issue summary and Retool link. |
| 10 | `warn_hr_advisory` | Slack | Posts advisory warning to `#hr-onboarding-ops`. Pipeline continues to Stage 3 after 30-second delay to allow HR to view the warning. |
| 11 | `signal_ready_for_profile_creation` | Airtable | Updates `pipeline_status.current_stage = "validation"`, `stages.validation.status = "complete"`. This update triggers the `onboarding_profile_creation` workflow. |

---

## 3. Extraction Helper Script

**File:** `extract_onboarding.js`  
**Runtime:** Node.js 18+  
**Dependency:** `@anthropic-ai/sdk`

### Setup

```bash
# Clone or create the scaffold directory
mkdir onboarding-scaffold && cd onboarding-scaffold

# Install dependency
npm install @anthropic-ai/sdk

# Set your API key
export ANTHROPIC_API_KEY=your_anthropic_key_here

# Run against the sample input
node extract_onboarding.js --input ./sample_input.json

# Run and save output to file
node extract_onboarding.js --input ./sample_input.json --output ./output_result.json
```

### Script overview

The script has three responsibilities:

1. **`flattenHirePayloadToText(payload)`** — converts the structured mock hire JSON into a readable plain-text document string that mimics what Claude would receive from a real offer letter or ATS export.

2. **`extractOnboardingRecord(hirePayload)`** — calls the Claude API with the Phase 2 Prompt 1 system prompt, parses the JSON response, and wraps the result in the full `OnboardingRecord` schema with a generated `record_id`, `meta`, and `pipeline_status` block.

3. **`main()`** — CLI entrypoint. Reads input from `--input` path (defaults to `./sample_input.json`), runs extraction, prints the result, and optionally writes it to `--output` path.

**Key design decisions:**
- Temperature is not set (defaults to 1 for the SDK); in production, set `temperature: 0` for deterministic extraction.
- The JSON parser strips markdown fences from the response before parsing, as Claude occasionally wraps JSON in triple backticks even when instructed not to.
- All errors are thrown with descriptive messages rather than silently returning null, so n8n can catch them in its error branch.

---

## 4. Sample Input Payload

**File:** `sample_input.json`

```json
{
  "_source": "google_forms",
  "_submitted_at": "2025-03-13T09:14:00Z",
  "_form_version": "intake-v3",

  "personal": {
    "full_name": "Priya Anand",
    "preferred_name": "Pri",
    "email": "priya.anand@gmail.com",
    "phone": "+44 7712 334 891"
  },

  "role": {
    "title": "Senior Product Designer",
    "department": "Product",
    "type": "Full-time permanent",
    "start_date": "2025-04-14",
    "end_date": null,
    "manager": "James Okonkwo",
    "cost_centre": "CC-PROD-007",
    "location": "London, UK",
    "remote_status": "hybrid"
  },

  "compensation": {
    "currency": "GBP",
    "amount": 78000,
    "frequency": "annual"
  },

  "documents_submitted": [
    "Signed offer letter",
    "Passport (UK)",
    "Right to work declaration",
    "NDA (signed)",
    "P45 from previous employer"
  ],

  "notes": "Priya is relocating from Bristol. She has requested a standing desk and dual monitors. She mentioned she uses Figma extensively and has asked about access to the full Adobe Creative Suite. Her onboarding buddy has not yet been assigned."
}
```

### What this tests

- Date normalisation (`"2025-04-14"` is already ISO 8601 — extraction should pass it through cleanly)
- Employment type inference (`"Full-time permanent"` → `"full_time"`)
- Currency classification (`"GBP"` → ISO 4217 correct)
- Notes field handling — rich free-text that contains useful operational data (equipment requests, buddy status) but should not pollute extracted fields
- Document type recognition — includes a P45, which is a UK-specific tax document the model should identify correctly
- Partial information handling — no tax declaration form (Starter Checklist / P46), which should surface as a note

---

## 5. Sample Output Payload

**File:** `sample_output.json`

```json
{
  "record_id": "ONB-2025-0142",
  "meta": {
    "created_at": "2025-03-13T09:14:22.000Z",
    "updated_at": "2025-03-13T09:14:28.000Z",
    "source_system": "google_forms",
    "schema_version": "1.0.0",
    "assigned_hr_contact": null
  },
  "pipeline_status": {
    "current_stage": "intake",
    "stages": {
      "intake": {
        "status": "complete",
        "started_at": "2025-03-13T09:14:22.000Z",
        "completed_at": "2025-03-13T09:14:28.000Z",
        "error_ref": null
      },
      "validation":       { "status": "pending", "started_at": null, "completed_at": null, "error_ref": null },
      "profile_creation": { "status": "pending", "started_at": null, "completed_at": null, "error_ref": null },
      "task_routing":     { "status": "pending", "started_at": null, "completed_at": null, "error_ref": null },
      "plan_generation":  { "status": "pending", "started_at": null, "completed_at": null, "error_ref": null },
      "communication":    { "status": "pending", "started_at": null, "completed_at": null, "error_ref": null },
      "tracking":         { "status": "pending", "started_at": null, "completed_at": null, "error_ref": null }
    }
  },
  "extracted": {
    "extraction_status": "complete",
    "employee": {
      "full_name": "Priya Anand",
      "preferred_name": "Pri",
      "personal_email": "priya.anand@gmail.com",
      "phone_number": "+44 7712 334 891"
    },
    "employment": {
      "job_title": "Senior Product Designer",
      "department": "Product",
      "employment_type": "full_time",
      "start_date": "2025-04-14",
      "end_date": null,
      "work_location": "London, UK",
      "remote_status": "hybrid",
      "reporting_manager": "James Okonkwo",
      "cost_centre": "CC-PROD-007",
      "salary_currency": "GBP",
      "salary_amount": 78000,
      "salary_frequency": "annual"
    },
    "documents_present": [
      "Signed offer letter",
      "Passport (UK)",
      "Right to work declaration",
      "NDA (signed)",
      "P45 from previous employer"
    ],
    "extraction_notes": [
      "employment_type inferred as 'full_time' from stated 'Full-time permanent'.",
      "No tax declaration form (P46/Starter Checklist) identified — P45 present instead. Validation stage should confirm whether this satisfies HMRC requirements.",
      "Notes field contains equipment preferences (standing desk, dual monitors) and software access requests (Figma, Adobe Creative Suite) — these are not mapped to schema fields but should be routed to IT task queue in Stage 4.",
      "Onboarding buddy not yet assigned — flagged for HR to assign before Stage 6 communication.",
      "Employee is relocating from Bristol — HR may wish to confirm London office address for payroll and right-to-work records."
    ]
  },
  "validation_result": null,
  "provisioning": null,
  "onboarding_plan": null,
  "communications": null,
  "tracking": null,
  "error_log": []
}
```

### Reading the output

| Field | Value | What it means |
|---|---|---|
| `extraction_status` | `"complete"` | All five required fields present: `full_name`, `job_title`, `department`, `employment_type`, `start_date`. Pipeline may proceed to validation. |
| `employment_type` | `"full_time"` | Correctly inferred from `"Full-time permanent"` — not stated verbatim in the input. |
| `end_date` | `null` | Not applicable for a permanent hire. Correctly left null rather than fabricated. |
| `extraction_notes[1]` | P46/P45 note | Model correctly identified that a P45 is present but a Starter Checklist is missing — a real compliance consideration for UK PAYE. |
| `extraction_notes[2]` | Equipment and software note | Unstructured data from the `notes` field has been surfaced as a note rather than incorrectly mapped to a schema field. |
| `pipeline_status.stages.*` | All `"pending"` except `intake: "complete"` | Record is ready for Stage 2. No other stages have been triggered yet. |
| `validation_result` | `null` | Validation has not run yet — will be populated by Workflow B. |
| `error_log` | `[]` | No errors during extraction. |

---

## File Structure

```
onboarding-scaffold/
├── extract_onboarding.js   # Main extraction script (Node.js / Claude API)
├── sample_input.json       # Mock new hire intake payload
├── sample_output.json      # Expected enriched OnboardingRecord output
├── package.json            # Project config and npm scripts
└── PHASE4.md               # This document
```

---

## Next Steps for Full Implementation

To extend this prototype into the full seven-stage pipeline:

1. **Add `validate_onboarding.js`** — implements Workflow B. Calls Prompt 2, parses the validation result, routes to HR queue or proceeds.
2. **Add n8n workflow JSON exports** — the node configurations described in Section 2 can be exported as n8n workflow JSON and imported directly into a running n8n instance.
3. **Connect Airtable** — replace the `sample_output.json` write in the script with an Airtable REST API call using the schema from Phase 3.
4. **Parallelise plan generation** — Stage 5 calls three Claude prompts (plan, manager summary, training). Implement with `Promise.all()` in Node.js or n8n's parallel branch pattern.
5. **Add retry middleware** — wrap all Claude API calls in an exponential backoff utility function before moving to production.

---

