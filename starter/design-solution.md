# AI-Powered Onboarding Automation — Phase 1: Workflow Design

**Assessment Type:** Enterprise Onboarding Automation  
**Phase:** 1 of 3 — Workflow Design (Task 1, Part A)  
**Status:** Complete — Pending Phase 2 Review

---

## Overview

This document defines a seven-stage AI-powered onboarding automation workflow. Each stage is designed to minimise manual handling while surfacing human review only where judgment, compliance, or edge cases genuinely require it.

### Workflow Pipeline

```
Intake → Validation → Profile Creation → Task Routing → Onboarding Plan → Communication → Tracking
```

---

## Stage-by-Stage Breakdown

| **Stage** | **Input** | **AI Task** | **Output** | **Human Review Required** |
|---|---|---|---|---|
| **1. Intake** — *Triggered by: new hire record created in HRIS or ATS* | New hire form submission, ATS export (name, role, department, start date, location, employment type, manager ID) | **Extraction** — parse unstructured offer letter / ATS fields into a structured onboarding record; handle variable formats across departments | Standardised onboarding record (JSON/structured profile stub) |  **Yes** — if required fields are missing or role classification is ambiguous (e.g. contractor vs. FTE edge cases) |
| **2. Validation** — *Triggered by: intake record creation* | Onboarding record + document checklist (ID, right-to-work, tax forms, contracts, NDA) | **Classification** — categorise each uploaded document by type; flag missing, expired, or illegible documents; check against regulatory requirements by region | Document status report: complete / incomplete / flagged |  **Yes** — always flagged to HR/Compliance when documents are missing, expired, or jurisdiction-specific exceptions apply |
| **3. Profile Creation** — *Triggered by: validation pass (or partial pass with HR sign-off)* | Validated onboarding record, org chart data, role metadata, HR system APIs | **Generation** — auto-populate employee profile across systems (directory, SSO, Slack, ticketing); summarise role context for buddy/manager brief | Active accounts created; employee profile populated; manager briefing summary generated |  **Yes** — if system provisioning fails or role requires elevated access permissions (security review gate) |
| **4. Task Routing** — *Triggered by: profile creation complete* | Employee profile, role, department, location, employment type, manager | **Decision support + Classification** — match role attributes to onboarding task templates; assign tasks to responsible parties (IT, Facilities, Legal, Manager, HR) with deadlines | Task queue per stakeholder (IT provisioning, equipment, access, training modules, compliance tasks) |  **Conditional** — non-standard roles, senior hires, or multi-jurisdiction hires require manager/HR to approve the task set before dispatch |
| **5. Onboarding Plan** — *Triggered by: task routing confirmed* | Role, department, manager input (optional), company competency frameworks, role-specific L&D catalogue | **Generation + Summarisation** — draft a personalised 30/60/90-day onboarding plan with milestones, learning recommendations, and key stakeholder intros; summarise for manager review | 30/60/90-day plan document; manager summary; calendar invites drafted |  **Yes** — manager reviews and approves plan before it is shared with the new hire; escalated for VP+ hires |
| **6. Communication** — *Triggered by: plan approved (or auto-approved if within standard template)* | Approved plan, employee profile, manager details, company tone-of-voice guidelines | **Generation** — draft personalised welcome email, day-1 schedule, Slack welcome message, buddy introduction note, and system access instructions | Welcome email sent; day-1 pack delivered; Slack message posted; buddy notified |  **Conditional** — HR spot-checks a sample of outbound comms; all comms to executive hires reviewed before send |
| **7. Tracking & Feedback** — *Triggered by: start date reached; runs continuously for 90 days* | Task completion status, check-in survey responses, manager input, LMS completion data | **Summarisation + Decision support** — aggregate task completion rates; surface blockers and at-risk onboarding journeys; summarise pulse survey sentiment; recommend manager interventions | Weekly onboarding health dashboard; manager nudges; HR escalation alerts for stalled journeys |  **Yes** — any hire flagged as "at risk" (stalled tasks, negative sentiment) is escalated to HR for human follow-up |

---

## Human-in-the-Loop Checkpoint Summary

There are **five mandatory** and **two conditional** review gates across the workflow.

| **Checkpoint** | **Stage** | **Trigger** |
|---|---|---|
| Missing or ambiguous hire data | 1 — Intake | Required fields absent; role type unclear |
| Document compliance failure | 2 — Validation | Missing/expired docs; jurisdiction edge cases |
| Elevated access provisioning | 3 — Profile Creation | Security-sensitive system access requested |
| Non-standard task plan | 4 — Task Routing | Senior, executive, or multi-jurisdiction hires |
| Manager plan approval | 5 — Onboarding Plan | All plans; mandatory before sharing with hire |
| Executive comms review | 6 — Communication | VP+ hires; HR sample review for all others |
| At-risk hire escalation | 7 — Tracking | Low completion rate or negative pulse sentiment |

---

## AI Task Type Reference

| **AI Task Type** | **Stages Used** | **Description** |
|---|---|---|
| Extraction | 1 — Intake | Parsing unstructured data (offer letters, ATS exports) into structured records |
| Classification | 2 — Validation, 4 — Task Routing | Categorising documents; matching roles to task templates |
| Generation | 3 — Profile, 5 — Plan, 6 — Communication | Creating profiles, onboarding plans, and personalised communications |
| Summarisation | 5 — Plan, 7 — Tracking | Condensing plan details for manager review; aggregating survey and progress data |
| Decision Support | 4 — Task Routing, 7 — Tracking | Recommending task assignments and flagging at-risk journeys for human review |

---

## Key Design Principles

- **Automation-first, human-in-the-loop by exception** — AI handles all routine processing; humans intervene only at compliance, security, or quality gates.
- **Fail-safe escalation** — any stage that cannot be completed automatically raises a flag rather than proceeding with incomplete data.
- **Auditability** — every AI decision is logged with its inputs, outputs, and confidence level for compliance review.
- **Personalisation at scale** — onboarding plans and communications are generated per-hire based on role, department, location, and seniority rather than applied from a single static template.

---

*Document prepared as part of Enterprise Onboarding Automation Assessment — Phase 1.*  
*Proceed to Phase 2: Tool & Integration Architecture.*
# AI-Powered Onboarding Automation — Phase 2: Prompt Engineering

**Assessment Type:** Enterprise Onboarding Automation  
**Phase:** 2 of 3 — Prompt Engineering (Task 1, Part B)  
**Status:** Complete — Pending Phase 3 Review

---

## Overview

This document contains six production-ready prompts, one per AI task identified in Phase 1. Each prompt is structured with a role instruction, task definition, input format specification, output format, and a fallback instruction for missing or ambiguous data.

All prompts are designed to be used as **system prompts** passed to the AI model at runtime. Variable placeholders are denoted with `{{DOUBLE_CURLY_BRACES}}` and must be substituted by the orchestration layer before dispatch.

---

## Prompt Index

| # | Task | Output Format | Stage |
|---|---|---|---|
| 1 | Document field extraction | JSON | Stage 1 — Intake |
| 2 | Input validation and missing field detection | JSON | Stage 2 — Validation |
| 3 | Personalised onboarding plan generation | Markdown | Stage 5 — Onboarding Plan |
| 4 | Welcome email draft | Subject line + plain text body | Stage 6 — Communication |
| 5 | Manager summary generation | Markdown | Stage 5 — Onboarding Plan |
| 6 | Training module recommendation | Ranked list with rationale | Stage 5 — Onboarding Plan |

---

---

## Prompt 1 — Document Field Extraction

**Stage:** 1 — Intake  
**AI Task Type:** Extraction  
**Output Format:** JSON

```
SYSTEM PROMPT:

You are an onboarding data extraction assistant for an enterprise HR operations team.
Your sole responsibility is to read raw hire documents and extract structured employee
data accurately and consistently. You do not interpret, infer, or guess. You extract
only what is explicitly stated in the source text.

TASK:
Extract all available employee onboarding fields from the raw document text provided
below. Map each piece of information to the correct field in the output schema.

INPUT FORMAT:
The input will be raw text extracted from one or more of the following document types:
- Offer letter (signed or unsigned)
- ATS (Applicant Tracking System) export
- HR intake form submission
- Employment contract cover sheet

The text may be unstructured, inconsistently formatted, or contain extraneous content
such as legal boilerplate, page numbers, or repeated headers. Extract only data
relevant to the output schema.

OUTPUT FORMAT:
Return a single valid JSON object. Do not include any explanation, commentary,
or markdown formatting outside the JSON block. The JSON must conform exactly
to the following schema:

{
  "extraction_status": "complete" | "partial" | "failed",
  "employee": {
    "full_name": string | null,
    "preferred_name": string | null,
    "personal_email": string | null,
    "phone_number": string | null
  },
  "employment": {
    "job_title": string | null,
    "department": string | null,
    "employment_type": "full_time" | "part_time" | "contractor" | "intern" | null,
    "start_date": "YYYY-MM-DD" | null,
    "end_date": "YYYY-MM-DD" | null,
    "work_location": string | null,
    "remote_status": "on_site" | "hybrid" | "remote" | null,
    "reporting_manager": string | null,
    "cost_centre": string | null,
    "salary_currency": string | null,
    "salary_amount": number | null,
    "salary_frequency": "annual" | "monthly" | "hourly" | null
  },
  "documents_present": [string],
  "extraction_notes": [string]
}

FIELD RULES:
- All dates must be normalised to ISO 8601 format (YYYY-MM-DD).
- employment_type must be classified from context if not stated verbatim
  (e.g. "fixed-term contract" → "contractor", "graduate scheme" → "intern").
- salary_currency must use ISO 4217 currency codes (e.g. USD, GBP, EUR).
- documents_present must list each source document type identified in the input.
- extraction_notes must log any ambiguities, conflicting values, or inferences made.

FALLBACK INSTRUCTIONS:
- If a field cannot be found or reliably inferred, set its value to null.
  Do not guess or fabricate values.
- If the document is unreadable, empty, or entirely irrelevant, set
  extraction_status to "failed" and populate extraction_notes with the reason.
- If some fields are found but others are missing, set extraction_status
  to "partial".
- If all required fields are populated, set extraction_status to "complete".
- Required fields for "complete" status: full_name, job_title, department,
  employment_type, start_date.

INPUT DOCUMENT TEXT:
{{RAW_DOCUMENT_TEXT}}
```

---

---

## Prompt 2 — Input Validation and Missing Field Detection

**Stage:** 2 — Validation  
**AI Task Type:** Classification  
**Output Format:** JSON with status and issues array

```
SYSTEM PROMPT:

You are an onboarding compliance validation assistant for an enterprise HR operations team.
Your role is to review a structured employee onboarding record and a set of uploaded
document metadata, then determine whether the record is complete, compliant, and ready
to proceed to profile creation.

You apply validation rules consistently and without exception. You do not approve
records that fail mandatory checks, regardless of context.

TASK:
Validate the onboarding record provided against the required field checklist and
document requirements for the employee's jurisdiction and employment type.
Identify all missing fields, invalid values, expired documents, and compliance gaps.

INPUT FORMAT:
You will receive two JSON objects:

1. onboarding_record — the structured employee record produced by the extraction step.
2. document_manifest — a list of uploaded documents with their metadata.

Example structure:

onboarding_record: { ...fields as per extraction schema... }

document_manifest: [
  {
    "document_type": string,
    "upload_date": "YYYY-MM-DD",
    "expiry_date": "YYYY-MM-DD" | null,
    "status": "uploaded" | "missing" | "illegible"
  }
]

OUTPUT FORMAT:
Return a single valid JSON object. Do not include any explanation, commentary,
or markdown outside the JSON block.

{
  "validation_status": "passed" | "passed_with_warnings" | "failed",
  "record_id": string,
  "validated_at": "ISO 8601 timestamp",
  "missing_fields": [
    {
      "field": string,
      "severity": "blocking" | "advisory",
      "reason": string
    }
  ],
  "document_issues": [
    {
      "document_type": string,
      "issue": "missing" | "expired" | "illegible" | "wrong_type",
      "severity": "blocking" | "advisory",
      "details": string
    }
  ],
  "compliance_flags": [
    {
      "flag": string,
      "jurisdiction": string,
      "details": string
    }
  ],
  "recommended_action": string,
  "human_review_required": boolean,
  "human_review_reason": string | null
}

VALIDATION RULES:

Blocking missing fields (must be present to proceed):
- full_name, job_title, department, employment_type, start_date, work_location,
  reporting_manager, personal_email

Advisory missing fields (warn but do not block):
- preferred_name, phone_number, cost_centre, salary details

Required documents (blocking if missing):
- Government-issued photo ID
- Right-to-work or work authorisation document
- Signed employment contract or offer letter
- Tax declaration form (jurisdiction-specific)
- NDA (if role is in Engineering, Product, Legal, or Finance)

Document expiry: flag any document with an expiry_date in the past or within
30 days of the employee's start_date as a blocking issue.

employment_type validation:
- "contractor" records must include an end_date. Flag as blocking if absent.
- "intern" records must include a cost_centre. Flag as advisory if absent.

human_review_required must be set to true if:
- Any blocking issue exists, OR
- The jurisdiction is outside the organisation's standard operating regions
  ({{STANDARD_REGIONS}}), OR
- The employee's role is flagged as requiring elevated system access
  ({{ELEVATED_ACCESS_ROLES}})

FALLBACK INSTRUCTIONS:
- If the onboarding_record input is null, empty, or unparseable, return
  validation_status "failed" with a single blocking missing_field entry:
  { "field": "onboarding_record", "severity": "blocking",
    "reason": "No valid onboarding record provided." }
- If document_manifest is empty, treat all required documents as missing.
- If jurisdiction cannot be determined from work_location, set a compliance_flag
  with flag "jurisdiction_unknown" and set human_review_required to true.
- Do not infer or assume document presence. Only validate what is explicitly
  listed in the document_manifest.

INPUT DATA:
onboarding_record: {{ONBOARDING_RECORD_JSON}}
document_manifest: {{DOCUMENT_MANIFEST_JSON}}
standard_regions: {{STANDARD_REGIONS}}
elevated_access_roles: {{ELEVATED_ACCESS_ROLES}}
```

---

---

## Prompt 3 — Personalised Onboarding Plan Generation

**Stage:** 5 — Onboarding Plan  
**AI Task Type:** Generation + Summarisation  
**Output Format:** Structured Markdown

```
SYSTEM PROMPT:

You are a senior onboarding programme designer for an enterprise organisation.
Your role is to create personalised, practical, and motivating 30/60/90-day
onboarding plans for new hires. You write clearly, concisely, and in a
professional but welcoming tone. You never use filler content or generic
boilerplate.

Plans must reflect the employee's specific role, seniority, department,
and work arrangement. Every milestone must be actionable and measurable.

TASK:
Using the employee profile, role metadata, and organisational context provided,
generate a complete personalised 30/60/90-day onboarding plan. The plan must
include milestones, learning objectives, key relationships to build, and
success criteria for each phase.

INPUT FORMAT:
You will receive the following fields as a JSON object:

{
  "employee": {
    "full_name": string,
    "preferred_name": string | null,
    "job_title": string,
    "department": string,
    "seniority_level": "junior" | "mid" | "senior" | "lead" | "director" | "vp",
    "employment_type": string,
    "remote_status": string,
    "reporting_manager": string,
    "start_date": string
  },
  "team_context": {
    "team_size": number,
    "key_stakeholders": [string],
    "current_team_priorities": [string]
  },
  "role_context": {
    "primary_responsibilities": [string],
    "tools_and_systems": [string],
    "required_compliance_training": [string]
  },
  "company_context": {
    "company_values": [string],
    "onboarding_buddy": string | null,
    "probation_period_days": number | null
  }
}

OUTPUT FORMAT:
Return structured markdown only. Do not include any JSON, code blocks,
or commentary outside the markdown. Use the exact section structure below.
Do not add, remove, or rename sections.

---

# Onboarding Plan — {{preferred_name or full_name}}, {{job_title}}

**Start Date:** {{start_date}}  
**Department:** {{department}}  
**Manager:** {{reporting_manager}}  
**Plan Period:** 90 days

---

## Phase 1 — First 30 Days: Learn

**Theme:** Orientation, relationships, and foundational understanding.

### Goals
- [3–5 specific, measurable goals for this phase]

### Key Activities
- [Bulleted list of concrete activities, meetings, and tasks]

### Relationships to Build
- [Named stakeholders or roles, with context on why each matters]

### Compliance & Admin Checklist
- [Required compliance training and administrative tasks to complete]

### Success Criteria
- [How will the employee and manager know Phase 1 has been completed successfully?]

---

## Phase 2 — Days 31–60: Contribute

**Theme:** Building confidence, delivering early wins, deepening context.

### Goals
### Key Activities
### Relationships to Build
### Success Criteria

---

## Phase 3 — Days 61–90: Lead

**Theme:** Independence, impact, and future planning.

### Goals
### Key Activities
### Relationships to Build
### Success Criteria

---

## Probation Milestone
[If probation_period_days is provided, include a brief note on what a
successful probation review looks like. If null, omit this section.]

---

## Notes for Manager
[2–4 sentences of practical guidance for the manager on how to support
this specific employee through onboarding, based on their seniority and role.]

---

WRITING GUIDELINES:
- Address the employee by their preferred_name where available, otherwise full_name.
- Adjust depth and independence of milestones to match seniority_level.
  Junior hires need more structured guidance; senior/lead hires need more
  strategic framing and autonomy.
- remote_status should influence activity design (e.g. remote hires need
  explicit virtual coffee introductions; on-site hires can reference in-person sessions).
- Incorporate current_team_priorities naturally into Phase 2 and Phase 3 activities.
- Keep language clear and direct. Avoid corporate jargon.

FALLBACK INSTRUCTIONS:
- If seniority_level is null, default to "mid" and note the assumption
  in the Notes for Manager section.
- If team_context or role_context fields are null or empty, generate
  the plan using the available data and add a note at the top:
  "⚠️ This plan was generated with limited role context. Manager review
  is recommended before sharing with the new hire."
- If start_date is null, use "TBD" and flag for HR to confirm.
- Never fabricate specific tool names, stakeholder names, or team priorities
  that are not present in the input. Use placeholder language instead,
  e.g. "[primary project management tool]".

INPUT DATA:
{{ONBOARDING_PLAN_INPUT_JSON}}
```

---

---

## Prompt 4 — Welcome Email Draft

**Stage:** 6 — Communication  
**AI Task Type:** Generation  
**Output Format:** Subject line + plain text body

```
SYSTEM PROMPT:

You are an internal communications writer for an enterprise organisation.
Your role is to draft warm, professional, and personalised welcome emails
for new employees joining the company. Your writing is clear, human, and
concise. You do not use clichés, excessive enthusiasm, or corporate jargon.

Every email must feel personally written, not templated — even though it
is generated at scale. The tone should match the company's voice guidelines
provided in the input.

TASK:
Draft a welcome email to be sent to a new employee before their first day.
The email must cover: a warm welcome, what to expect on day one, how to
prepare, who their first point of contact will be, and where to go for help.

INPUT FORMAT:
You will receive the following fields as a JSON object:

{
  "employee": {
    "preferred_name": string | null,
    "full_name": string,
    "job_title": string,
    "department": string,
    "start_date": string,
    "work_location": string,
    "remote_status": "on_site" | "hybrid" | "remote"
  },
  "manager": {
    "full_name": string,
    "job_title": string,
    "email": string
  },
  "buddy": {
    "full_name": string | null,
    "job_title": string | null,
    "email": string | null
  },
  "day_one": {
    "start_time": string,
    "location_or_link": string,
    "first_activity": string,
    "it_setup_instructions": string | null
  },
  "company": {
    "name": string,
    "tone_of_voice": "formal" | "professional" | "friendly" | "casual",
    "support_email": string,
    "hr_contact_name": string
  }
}

OUTPUT FORMAT:
Return plain text only, structured exactly as follows.
Do not use markdown formatting, HTML, or JSON in the output.

SUBJECT: [Single line — the email subject line]

BODY:
[Email body — plain text, naturally paragraphed]

RULES:
- Maximum 350 words for the body.
- Use the employee's preferred_name if available, otherwise first name from full_name.
- Adapt tone to match company.tone_of_voice:
    formal     → professional salutations, no contractions, third-person references to the company
    professional → warm but structured, light use of contractions acceptable
    friendly   → conversational, first-name basis, inclusive language
    casual     → relaxed and direct, short sentences, minimal formality
- remote_status must influence day-one instructions:
    on_site  → include physical address and arrival instructions
    hybrid   → include both the office address and the video call link
    remote   → include only the video call link; omit all office references
- If a buddy is assigned, introduce them by name and role in the email.
- End the email with the manager's name and a note that they are the
  primary contact for questions before day one.
- Do not fabricate details not present in the input (e.g. do not invent
  a team lunch if first_activity does not mention one).

FALLBACK INSTRUCTIONS:
- If start_date is null, write "your upcoming start date" instead of
  a specific date, and add a note at the very end of your output:
  [NOTE: start_date was not provided — HR should confirm before sending.]
- If day_one.it_setup_instructions is null, omit the IT setup paragraph.
- If buddy is null, omit all buddy references.
- If company.tone_of_voice is null, default to "professional".
- If location_or_link is null, replace with "[Location to be confirmed]"
  and flag for HR review.

INPUT DATA:
{{WELCOME_EMAIL_INPUT_JSON}}
```

---

---

## Prompt 5 — Manager Summary Generation

**Stage:** 5 — Onboarding Plan  
**AI Task Type:** Summarisation  
**Output Format:** Brief structured Markdown

```
SYSTEM PROMPT:

You are an HR operations assistant specialising in new hire briefings.
Your role is to prepare concise, practical manager briefing summaries
before a new employee joins their team. Your writing is direct, informative,
and free of HR jargon. You respect managers' time — briefings must be
scannable in under two minutes.

TASK:
Using the new hire's profile, onboarding plan, and any relevant notes,
generate a manager briefing summary. This summary will be sent to the
hiring manager before the employee's first day to help them prepare
for an effective onboarding experience.

INPUT FORMAT:
You will receive the following fields as a JSON object:

{
  "employee": {
    "full_name": string,
    "preferred_name": string | null,
    "job_title": string,
    "department": string,
    "seniority_level": string,
    "start_date": string,
    "employment_type": string,
    "remote_status": string
  },
  "onboarding_plan_summary": {
    "phase_1_goals": [string],
    "key_stakeholders": [string],
    "compliance_training_required": [string],
    "probation_period_days": number | null
  },
  "validation_flags": [
    {
      "field": string,
      "severity": string,
      "reason": string
    }
  ],
  "buddy_assigned": string | null,
  "hr_contact": string
}

OUTPUT FORMAT:
Return structured markdown only. Use the exact section structure below.
Keep the total length under 400 words. Do not add or remove sections.

---

## New Hire Briefing — {{full_name}}, {{job_title}}

**Start Date:** {{start_date}} | **Works:** {{remote_status}} | **Type:** {{employment_type}}

---

### Who They Are
[2–3 sentences covering name/preferred name, role, seniority, and any notable
context the manager should know going in.]

### What You Need to Do Before Day One
[Bulleted checklist of 3–6 concrete actions the manager must take before
the employee starts. Examples: confirm equipment, schedule 1:1, add to team channels.]

### Day-One Priorities
[Bulleted list of 3–5 specific activities or conversations to prioritise on day one.]

### 30-Day Goals
[Brief list of the Phase 1 goals from the onboarding plan — formatted as
short, manager-facing action items.]

### Compliance & Training
[List any mandatory compliance training the employee must complete and the
deadline or window for completion.]

### Flags for Your Attention
[List any outstanding validation flags from the onboarding record that the
manager should be aware of. Use plain language — no HR codes or system references.
If there are no flags, write: "No open issues at this time."]

### Your Support Contacts
**Onboarding Buddy:** {{buddy_assigned or "Not yet assigned"}}  
**HR Contact:** {{hr_contact}}

---

WRITING GUIDELINES:
- Write for a busy manager, not an HR audience.
- Use plain, direct language. Avoid acronyms unless defined.
- Adjust the "What You Need to Do Before Day One" section based on
  remote_status (e.g. remote managers need to arrange equipment shipping;
  on-site managers need to prepare a physical workspace).
- Do not repeat the same information across sections.

FALLBACK INSTRUCTIONS:
- If onboarding_plan_summary is null or empty, note at the top of the document:
  "⚠️ Onboarding plan not yet finalised. This summary reflects available
  profile data only. A full plan will follow."
- If validation_flags is empty, write "No open issues at this time." in
  the Flags section. Do not omit the section.
- If probation_period_days is provided, add a one-line note in the
  30-Day Goals section: "Note: Probation review due at day {{n}}."
- If any field in employee is null, omit it from the summary gracefully
  rather than printing null.

INPUT DATA:
{{MANAGER_SUMMARY_INPUT_JSON}}
```

---

---

## Prompt 6 — Training Module Recommendation

**Stage:** 5 — Onboarding Plan  
**AI Task Type:** Decision Support  
**Output Format:** Ranked list with rationale

```
SYSTEM PROMPT:

You are a learning and development advisor for an enterprise organisation.
Your role is to recommend the most relevant training modules for a new
employee based on their role, skill level, department, and compliance
requirements. You are objective and evidence-based. You rank recommendations
by priority and always explain your reasoning clearly.

You recommend only from the catalogue provided. You do not invent or
suggest external resources unless explicitly instructed.

TASK:
Review the employee's profile, their role requirements, and the available
training module catalogue. Select and rank the most appropriate training
modules for this employee's first 90 days. Separate mandatory compliance
training from recommended development training.

INPUT FORMAT:
You will receive the following fields as a JSON object:

{
  "employee": {
    "full_name": string,
    "job_title": string,
    "department": string,
    "seniority_level": "junior" | "mid" | "senior" | "lead" | "director" | "vp",
    "employment_type": string,
    "tools_and_systems": [string],
    "skills_gaps_identified": [string] | null,
    "prior_relevant_experience": string | null
  },
  "compliance_requirements": [string],
  "training_catalogue": [
    {
      "module_id": string,
      "title": string,
      "category": "compliance" | "technical" | "soft_skills" | "leadership" | "product",
      "duration_hours": number,
      "suitable_for_levels": [string],
      "tags": [string],
      "mandatory_for_roles": [string] | null,
      "mandatory_for_departments": [string] | null
    }
  ],
  "max_training_hours_first_30_days": number | null
}

OUTPUT FORMAT:
Return structured markdown only. Do not include JSON, code blocks,
or commentary outside the markdown. Use the exact section structure below.

---

## Training Recommendations — {{full_name}}, {{job_title}}

---

### Mandatory Compliance Training
*Must be completed within the first 30 days.*

| Priority | Module | Duration | Reason |
|---|---|---|---|
| [1, 2, 3...] | [Module title] | [X hrs] | [One-sentence reason why this is required] |

---

### Recommended Development Training — First 30 Days
*Prioritised based on role requirements and identified skill gaps.*

| Priority | Module | Duration | Rationale |
|---|---|---|---|

---

### Recommended Development Training — Days 31–90
*Deeper skill-building for medium-term growth.*

| Priority | Module | Duration | Rationale |
|---|---|---|---|

---

### Not Recommended at This Time
[Brief list of any catalogue modules explicitly excluded and a one-line reason
for each exclusion (e.g. "too advanced for current seniority level",
"not relevant to this department", "covered by prior experience").]

---

### Total Estimated Training Hours
- Mandatory (first 30 days): X hrs
- Recommended (first 30 days): X hrs
- Recommended (days 31–90): X hrs
- **Total (90 days): X hrs**

[If max_training_hours_first_30_days is provided and mandatory + recommended
hours exceed it, add a warning: "⚠️ Recommended hours exceed the allocated
training capacity for the first 30 days. The development training list above
has been prioritised accordingly — lower-ranked modules may need to be deferred."]

---

RANKING CRITERIA (apply in order):
1. Compliance and regulatory requirement — always ranked first regardless of other factors.
2. Role-specific mandatory modules (mandatory_for_roles matches job_title).
3. Department-specific mandatory modules (mandatory_for_departments matches department).
4. Modules directly addressing identified skills_gaps_identified.
5. Modules matching tools_and_systems listed in the employee profile.
6. Modules appropriate for the employee's seniority_level.
7. General development modules suitable for the department.

FALLBACK INSTRUCTIONS:
- If training_catalogue is empty or null, return only the following in
  the Mandatory section: "No catalogue provided. HR must supply the training
  module list before recommendations can be generated." Omit all other sections.
- If skills_gaps_identified is null, base development recommendations
  solely on role, department, seniority, and tools.
- If max_training_hours_first_30_days is null, do not include a capacity
  warning and do not limit recommendations by hours.
- If no modules match a section's criteria (e.g. no relevant development
  modules for days 31–90), write "No additional modules recommended for
  this phase." in that section. Do not omit the section.
- Only recommend modules where the employee's seniority_level appears in
  suitable_for_levels. Do not recommend modules above or below the
  employee's level unless no suitable alternatives exist — if so, note
  the mismatch in the Rationale column.

INPUT DATA:
{{TRAINING_RECOMMENDATION_INPUT_JSON}}
```

---

---

## Implementation Notes

### Variable Substitution
All `{{PLACEHOLDER}}` values must be resolved by the orchestration layer before the prompt is sent to the model. No placeholder should reach the model unresolved.

### Temperature Settings
| Prompt | Recommended Temperature | Reason |
|---|---|---|
| 1 — Extraction | 0.0 | Deterministic extraction; no creativity required |
| 2 — Validation | 0.0 | Rule-based logic; must be consistent across runs |
| 3 — Onboarding Plan | 0.4 | Structured generation with moderate personalisation |
| 4 — Welcome Email | 0.6 | Needs natural language variation while staying on-brief |
| 5 — Manager Summary | 0.3 | Professional summarisation; low variance preferred |
| 6 — Training Recommendations | 0.1 | Ranking logic should be near-deterministic |

### Chaining Order
These prompts are designed to chain sequentially. The output of each prompt feeds the input of the next:

```
Prompt 1 (Extraction) → Prompt 2 (Validation) → Prompt 3 (Plan) + Prompt 5 (Manager Summary) + Prompt 6 (Training)
                                                → Prompt 4 (Welcome Email)
```

Prompts 3, 5, and 6 can run in parallel once validation is complete.

### Human Review Gates
Any prompt that returns a `human_review_required: true` field (Prompt 2) or a `⚠️` warning flag (Prompts 3, 5, 6) must be routed to an HR reviewer before the output is acted upon or sent downstream.

---

*Document prepared as part of Enterprise Onboarding Automation Assessment — Phase 2.*  
*Proceed to Phase 3: Integration Architecture & System Design.*
# AI-Powered Onboarding Automation — Phase 3: Integration Architecture

**Assessment Type:** Enterprise Onboarding Automation  
**Phase:** 3 of 3 — Integration Architecture (Task 1, Part C)  
**Status:** Complete

---

## 1. Systems Inventory

All systems involved in the onboarding automation pipeline, grouped by architectural layer.

### Layer 1 — Intake (Data Sources & Triggers)

| System | Role | Integration Type | Trigger / Direction |
|---|---|---|---|
| Google Forms | New hire intake form — primary data entry point for HR-submitted records | Webhook → n8n | Inbound trigger on form submit |
| ATS (Greenhouse / Lever) | Exports accepted candidate record on offer acceptance | REST API → n8n | Inbound trigger on status change |
| HRIS (Workday) | Source of truth for employee identity and employment data | REST API → n8n | Inbound trigger on new hire record creation |
| Google Drive | Receives uploaded onboarding documents (ID, contract, NDA, tax forms) | Google Drive API → n8n | Inbound; polled or webhook on file upload |

### Layer 2 — Orchestration & Storage

| System | Role | Integration Type | Trigger / Direction |
|---|---|---|---|
| n8n | Central workflow orchestrator — sequences all stages, manages retries, routes errors, calls AI and downstream APIs | Self-hosted or n8n Cloud | Coordinates all flow |
| Airtable | Canonical onboarding record store — single source of truth for each hire's onboarding state throughout the 90-day window | REST API (read/write) | Read and write at every stage |
| Airtable (Error Log table) | Dedicated error and exception log — captures failed steps, retry counts, and HR escalation status | REST API (write) | Write on any caught error |
| Retool | Internal HR dashboard — displays onboarding health, pending reviews, and at-risk flags in real time | Airtable + REST API read | Read; HR-facing UI |

### Layer 3 — AI Processing

| System | Role | Integration Type | Trigger / Direction |
|---|---|---|---|
| Claude API (Anthropic) | Executes all six AI tasks via structured prompts: extraction, validation, plan generation, email drafting, manager summary, training recommendations | REST API (POST /v1/messages) | Called by n8n at each AI task stage |
| Prompt template store (n8n variables / Airtable) | Stores versioned prompt templates with variable placeholders; resolved by n8n before each API call | Internal to n8n | Read at runtime |
| Response parser (n8n Function node) | Validates and parses JSON / markdown returned by Claude; catches malformed responses before downstream use | Internal to n8n | Runs after every Claude API call |
| L&D training catalogue (Airtable) | Stores available training modules with metadata (category, duration, seniority suitability, mandatory flags) | REST API (read) | Read during training recommendation stage |

### Layer 4 — Delivery (Downstream Systems)

| System | Role | Integration Type | Trigger / Direction |
|---|---|---|---|
| Gmail (Google Workspace) | Sends welcome email and day-one pack to the new hire | Gmail API via n8n | Outbound; triggered at Stage 6 |
| Slack | Posts welcome message to team channel; sends buddy introduction; delivers manager nudges | Slack API via n8n | Outbound; triggered at Stages 6 and 7 |
| Okta | Provisions SSO identity and application access for the new hire | Okta API via n8n | Outbound; triggered at Stage 3 |
| Jira (or Asana) | Creates onboarding task queue for IT, Facilities, HR, and manager; tracks completion | Jira REST API via n8n | Outbound; triggered at Stage 4 |
| LMS (e.g. Learnupon / TalentLMS) | Enrols employee in mandatory and recommended training modules | LMS REST API via n8n | Outbound; triggered at Stage 5 |
| Google Calendar | Creates day-one schedule; books 30/60/90-day check-in meetings | Google Calendar API via n8n | Outbound; triggered at Stage 5 |

---

## 2. Data Flow Sequence

What moves between which systems at each stage.

### Stage 1 — Intake

```
Google Forms / ATS / HRIS
    → [webhook or API poll]
    → n8n (intake workflow triggered)
    → Claude API (Prompt 1: field extraction)
        Input:  raw document text
        Output: structured JSON (onboarding record stub)
    → Airtable (record created with status = "intake_complete")
```

**Data moved:** Raw hire submission → structured `OnboardingRecord` JSON written to Airtable.

---

### Stage 2 — Validation

```
Airtable (onboarding record)
    → n8n (validation workflow triggered on record creation)
    → Google Drive API (fetch document manifest for this hire)
    → Claude API (Prompt 2: validation + missing field detection)
        Input:  onboarding_record JSON + document_manifest JSON
        Output: validation JSON (status, missing_fields[], document_issues[], compliance_flags[])
    → Airtable (record updated: validation_status, issues array)
    → [if human_review_required = true]
        → Airtable (HR queue table: new review task created)
        → Slack (HR channel: alert posted)
    → [if passed] continue to Stage 3
```

**Data moved:** Onboarding record + document manifest → validation result written back to Airtable; HR alerted if blocked.

---

### Stage 3 — Profile Creation

```
Airtable (validated onboarding record)
    → n8n (profile creation workflow triggered on validation_status = "passed")
    → Okta API (create identity, assign app access groups)
    → Slack API (create user account, add to team channels)
    → Jira API (create user account)
    → Google Workspace Admin API (create email address, add to groups)
    → Airtable (record updated: provisioning_status per system)
    → [on any provisioning failure]
        → Airtable Error Log (failure recorded)
        → Slack (HR/IT channel: provisioning failure alert)
```

**Data moved:** Employee identity fields → account creation events in Okta, Slack, Jira, Google Workspace. Provisioning status written back to Airtable.

---

### Stage 4 — Task Routing

```
Airtable (profile + role metadata)
    → n8n (task routing workflow triggered on provisioning_status = "complete")
    → [role-based template lookup in Airtable task template table]
    → Jira API (create task queue: IT provisioning, equipment, training, compliance tasks)
        Assigned to: IT, Facilities, HR, Manager — based on role/department/location
    → Airtable (task list written to record; status = "tasks_routed")
    → [if senior / multi-jurisdiction hire]
        → Airtable HR queue (manager approval required before tasks are dispatched)
```

**Data moved:** Role attributes → task set created in Jira; Airtable updated with task references.

---

### Stage 5 — Onboarding Plan Generation

```
Airtable (full onboarding record + task list)
    → n8n (plan generation workflow; runs three Claude calls in parallel)

    → Claude API (Prompt 3: 30/60/90-day plan)
        Input:  employee profile + team context + role context + company context
        Output: structured markdown plan
    → Airtable (plan stored as markdown field)

    → Claude API (Prompt 5: manager summary)
        Input:  employee profile + plan summary + validation flags
        Output: markdown manager briefing
    → Airtable (manager_summary stored)

    → Claude API (Prompt 6: training module recommendations)
        Input:  employee profile + compliance requirements + L&D catalogue
        Output: ranked markdown list
    → LMS API (enrol employee in mandatory modules)
    → Airtable (training_recommendations stored)

    → Google Calendar API (create day-one schedule + 30/60/90 check-in events)
    → Airtable (status = "plan_ready"; manager_review_required = true)
    → [await manager approval in Retool dashboard before Stage 6]
```

**Data moved:** Employee and role context → three AI-generated documents stored in Airtable; LMS enrolment triggered; calendar events created.

---

### Stage 6 — Communication

```
Airtable (plan_approved = true; triggered by manager action in Retool)
    → n8n (communication workflow triggered)
    → Claude API (Prompt 4: welcome email draft)
        Input:  employee profile + day-one details + manager + buddy
        Output: subject line + plain text body
    → Gmail API (welcome email sent to employee personal_email)
    → Slack API (welcome message posted to team channel; buddy DM sent)
    → Google Calendar API (day-one invite sent to employee)
    → Airtable (status = "comms_sent"; sent_at timestamp recorded)
    → [on delivery failure: Gmail bounce / Slack API error]
        → Airtable Error Log (failure recorded with retry_count)
        → n8n (retry up to 3 times with 10-minute backoff)
        → [after 3 failures] → Airtable HR queue (manual send required)
```

**Data moved:** Approved plan and employee profile → personalised email, Slack message, calendar invite delivered. Delivery status written back to Airtable.

---

### Stage 7 — Tracking & Feedback

```
Airtable (active onboarding records where start_date <= today <= day 90)
    → n8n (scheduled workflow; runs daily)
    → Jira API (pull task completion status per hire)
    → LMS API (pull training completion rates per hire)
    → [weekly at day 7, 30, 60, 90] → Google Forms (send pulse survey link via Gmail)
    → [survey responses collected] → Google Forms API → n8n → Airtable
    → Claude API (summarisation + decision support)
        Input:  task completion data + survey responses + LMS data
        Output: health summary + at-risk flag + recommended actions
    → Airtable (onboarding_health_score updated; at_risk flag set)
    → Retool dashboard (live view updated)
    → [if at_risk = true]
        → Slack (manager DM: nudge with specific recommended action)
        → Airtable HR queue (HR escalation task created)
```

**Data moved:** Task, training, and survey completion data → AI-generated health summary → dashboard updated; manager and HR alerted if at-risk.

---

## 3. Orchestration Platform

**Selected platform: n8n (self-hosted)**

### Why n8n

n8n is selected as the orchestration layer for the following reasons:

- **Native AI node support** — n8n 1.x includes a built-in HTTP Request node and LangChain-compatible AI Agent node, enabling direct Claude API calls with structured input/output handling without custom code.
- **Visual workflow editor** — non-engineering HR operations teams can inspect, modify, and debug workflows without touching code.
- **Webhook and polling support** — handles both push triggers (Google Forms, ATS webhooks) and pull triggers (Jira, LMS polling) natively.
- **Error handling primitives** — built-in retry logic, error branches, and workflow execution logs reduce the need for custom error infrastructure.
- **Self-hosted deployment** — keeps all PII and onboarding data within the organisation's own infrastructure; no data passes through third-party SaaS orchestration servers.
- **Cost model** — self-hosted n8n is open source; no per-execution pricing at scale.

### n8n Workflow Structure

| Workflow | Trigger | Nodes used |
|---|---|---|
| `intake` | Webhook (Forms/ATS) or Schedule (HRIS poll) | HTTP Request (Claude), Airtable Write |
| `validation` | Airtable trigger (new record) | Google Drive, HTTP Request (Claude), Airtable Write, Slack (alert) |
| `profile_creation` | Airtable trigger (validation passed) | HTTP Request (Okta/Slack/Jira/Google), Airtable Write, Error branch |
| `task_routing` | Airtable trigger (provisioning complete) | Airtable Read (templates), Jira Create, Airtable Write |
| `plan_generation` | Airtable trigger (tasks routed) | HTTP Request ×3 (Claude), LMS API, Google Calendar, Airtable Write |
| `communication` | Airtable trigger (plan approved) | HTTP Request (Claude), Gmail, Slack, Google Calendar, Airtable Write |
| `tracking` | Schedule (daily cron) | Jira Read, LMS Read, HTTP Request (Claude), Airtable Write, Slack, Retool |

---

## 4. Central Onboarding Record — JSON Schema

This is the canonical data schema for a single hire's onboarding record as stored in Airtable. All systems read from and write to this structure via n8n.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "onboarding-record-v1",
  "title": "OnboardingRecord",
  "description": "Canonical data record for a single hire's onboarding journey.",
  "type": "object",
  "required": [
    "record_id",
    "meta",
    "employee",
    "employment",
    "pipeline_status"
  ],
  "properties": {

    "record_id": {
      "type": "string",
      "description": "Unique identifier for this onboarding record. Format: ONB-YYYY-NNNN",
      "pattern": "^ONB-\\d{4}-\\d{4}$",
      "example": "ONB-2025-0142"
    },

    "meta": {
      "type": "object",
      "description": "Record lifecycle metadata.",
      "required": ["created_at", "updated_at", "source_system", "schema_version"],
      "properties": {
        "created_at": { "type": "string", "format": "date-time" },
        "updated_at": { "type": "string", "format": "date-time" },
        "source_system": {
          "type": "string",
          "enum": ["google_forms", "ats_greenhouse", "ats_lever", "hris_workday", "manual"],
          "description": "System that originated this record."
        },
        "schema_version": { "type": "string", "example": "1.0.0" },
        "assigned_hr_contact": { "type": ["string", "null"] }
      }
    },

    "employee": {
      "type": "object",
      "description": "Personal identity fields.",
      "required": ["full_name", "personal_email"],
      "properties": {
        "full_name":       { "type": "string" },
        "preferred_name":  { "type": ["string", "null"] },
        "personal_email":  { "type": "string", "format": "email" },
        "work_email":      { "type": ["string", "null"], "format": "email",
                             "description": "Populated by n8n after Google Workspace provisioning." },
        "phone_number":    { "type": ["string", "null"] }
      }
    },

    "employment": {
      "type": "object",
      "description": "Role and contract details.",
      "required": ["job_title", "department", "employment_type", "start_date"],
      "properties": {
        "job_title":         { "type": "string" },
        "department":        { "type": "string" },
        "seniority_level": {
          "type": ["string", "null"],
          "enum": ["junior", "mid", "senior", "lead", "director", "vp", null]
        },
        "employment_type": {
          "type": "string",
          "enum": ["full_time", "part_time", "contractor", "intern"]
        },
        "start_date":        { "type": "string", "format": "date" },
        "end_date":          { "type": ["string", "null"], "format": "date",
                               "description": "Required for contractors." },
        "work_location":     { "type": ["string", "null"] },
        "remote_status": {
          "type": ["string", "null"],
          "enum": ["on_site", "hybrid", "remote", null]
        },
        "reporting_manager": { "type": ["string", "null"] },
        "cost_centre":       { "type": ["string", "null"] },
        "probation_period_days": { "type": ["integer", "null"] },
        "compensation": {
          "type": ["object", "null"],
          "properties": {
            "currency":  { "type": "string", "description": "ISO 4217 code, e.g. USD, GBP" },
            "amount":    { "type": "number" },
            "frequency": { "type": "string", "enum": ["annual", "monthly", "hourly"] }
          }
        }
      }
    },

    "documents": {
      "type": "object",
      "description": "Document validation state.",
      "properties": {
        "manifest": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["document_type", "status"],
            "properties": {
              "document_type": { "type": "string" },
              "upload_date":   { "type": ["string", "null"], "format": "date" },
              "expiry_date":   { "type": ["string", "null"], "format": "date" },
              "status": {
                "type": "string",
                "enum": ["uploaded", "missing", "expired", "illegible", "approved"]
              },
              "drive_file_id": { "type": ["string", "null"] }
            }
          }
        }
      }
    },

    "pipeline_status": {
      "type": "object",
      "description": "Current state of each workflow stage.",
      "required": ["current_stage", "stages"],
      "properties": {
        "current_stage": {
          "type": "string",
          "enum": [
            "intake",
            "validation",
            "profile_creation",
            "task_routing",
            "plan_generation",
            "communication",
            "tracking",
            "completed",
            "blocked"
          ]
        },
        "stages": {
          "type": "object",
          "description": "Per-stage completion state.",
          "properties": {
            "intake":           { "$ref": "#/$defs/stage_result" },
            "validation":       { "$ref": "#/$defs/stage_result" },
            "profile_creation": { "$ref": "#/$defs/stage_result" },
            "task_routing":     { "$ref": "#/$defs/stage_result" },
            "plan_generation":  { "$ref": "#/$defs/stage_result" },
            "communication":    { "$ref": "#/$defs/stage_result" },
            "tracking":         { "$ref": "#/$defs/stage_result" }
          }
        }
      }
    },

    "validation_result": {
      "type": ["object", "null"],
      "description": "Output of Prompt 2. Null until validation runs.",
      "properties": {
        "validation_status": {
          "type": "string",
          "enum": ["passed", "passed_with_warnings", "failed"]
        },
        "missing_fields":    { "type": "array", "items": { "type": "object" } },
        "document_issues":   { "type": "array", "items": { "type": "object" } },
        "compliance_flags":  { "type": "array", "items": { "type": "object" } },
        "human_review_required": { "type": "boolean" },
        "human_review_reason":   { "type": ["string", "null"] },
        "reviewed_by":           { "type": ["string", "null"] },
        "reviewed_at":           { "type": ["string", "null"], "format": "date-time" }
      }
    },

    "provisioning": {
      "type": ["object", "null"],
      "description": "Account provisioning status per system.",
      "properties": {
        "okta":             { "$ref": "#/$defs/provisioning_result" },
        "google_workspace": { "$ref": "#/$defs/provisioning_result" },
        "slack":            { "$ref": "#/$defs/provisioning_result" },
        "jira":             { "$ref": "#/$defs/provisioning_result" }
      }
    },

    "onboarding_plan": {
      "type": ["object", "null"],
      "description": "AI-generated plan outputs. Null until Stage 5 runs.",
      "properties": {
        "plan_markdown":          { "type": ["string", "null"],
                                    "description": "Full 30/60/90-day plan (Prompt 3 output)." },
        "manager_summary_markdown": { "type": ["string", "null"],
                                    "description": "Manager briefing (Prompt 5 output)." },
        "training_recommendations": { "type": ["string", "null"],
                                    "description": "Ranked training list (Prompt 6 output)." },
        "plan_approved":          { "type": "boolean", "default": false },
        "plan_approved_by":       { "type": ["string", "null"] },
        "plan_approved_at":       { "type": ["string", "null"], "format": "date-time" }
      }
    },

    "communications": {
      "type": ["object", "null"],
      "description": "Delivery status for all outbound communications.",
      "properties": {
        "welcome_email": {
          "type": "object",
          "properties": {
            "status":    { "type": "string", "enum": ["pending", "sent", "failed", "retry"] },
            "sent_at":   { "type": ["string", "null"], "format": "date-time" },
            "retry_count": { "type": "integer", "default": 0 }
          }
        },
        "slack_welcome": {
          "type": "object",
          "properties": {
            "status":    { "type": "string", "enum": ["pending", "sent", "failed"] },
            "sent_at":   { "type": ["string", "null"], "format": "date-time" }
          }
        },
        "calendar_invite": {
          "type": "object",
          "properties": {
            "status":    { "type": "string", "enum": ["pending", "sent", "failed"] },
            "event_id":  { "type": ["string", "null"] }
          }
        }
      }
    },

    "tracking": {
      "type": ["object", "null"],
      "description": "Ongoing 90-day tracking data.",
      "properties": {
        "task_completion_rate":     { "type": ["number", "null"],
                                      "minimum": 0, "maximum": 100,
                                      "description": "Percentage of Jira tasks marked complete." },
        "training_completion_rate": { "type": ["number", "null"],
                                      "minimum": 0, "maximum": 100 },
        "pulse_survey_responses":   { "type": "array", "items": { "type": "object" } },
        "onboarding_health_score":  { "type": ["number", "null"],
                                      "minimum": 0, "maximum": 100,
                                      "description": "AI-computed composite score." },
        "at_risk":                  { "type": "boolean", "default": false },
        "at_risk_reason":           { "type": ["string", "null"] },
        "last_evaluated_at":        { "type": ["string", "null"], "format": "date-time" }
      }
    },

    "error_log": {
      "type": "array",
      "description": "All caught errors for this record.",
      "items": { "$ref": "#/$defs/error_entry" }
    }

  },

  "$defs": {

    "stage_result": {
      "type": "object",
      "properties": {
        "status": {
          "type": "string",
          "enum": ["pending", "running", "complete", "failed", "blocked", "skipped"]
        },
        "started_at":   { "type": ["string", "null"], "format": "date-time" },
        "completed_at": { "type": ["string", "null"], "format": "date-time" },
        "error_ref":    { "type": ["string", "null"],
                          "description": "Reference to error_log entry if stage failed." }
      }
    },

    "provisioning_result": {
      "type": "object",
      "properties": {
        "status":         { "type": "string", "enum": ["pending", "provisioned", "failed"] },
        "external_id":    { "type": ["string", "null"],
                            "description": "User ID in the target system." },
        "provisioned_at": { "type": ["string", "null"], "format": "date-time" },
        "error_message":  { "type": ["string", "null"] }
      }
    },

    "error_entry": {
      "type": "object",
      "required": ["error_id", "stage", "error_type", "occurred_at"],
      "properties": {
        "error_id":       { "type": "string" },
        "stage":          { "type": "string" },
        "error_type": {
          "type": "string",
          "enum": [
            "extraction_failed",
            "validation_blocked",
            "provisioning_failed",
            "ai_response_invalid",
            "api_timeout",
            "delivery_failed",
            "human_review_required",
            "schema_violation",
            "unknown"
          ]
        },
        "message":        { "type": "string" },
        "payload":        { "type": ["object", "null"],
                            "description": "Sanitised request/response snapshot for debugging." },
        "occurred_at":    { "type": "string", "format": "date-time" },
        "retry_count":    { "type": "integer", "default": 0 },
        "resolved":       { "type": "boolean", "default": false },
        "resolved_by":    { "type": ["string", "null"] },
        "resolved_at":    { "type": ["string", "null"], "format": "date-time" }
      }
    }

  }
}
```

---

## 5. Error Handling Architecture

Errors are caught at four distinct levels. Each level has a defined response: automatic retry, human escalation, or hard stop with logging.

### Level 1 — AI Response Errors (Claude API)

**Where caught:** n8n Response Parser node, immediately after each Claude API call.

**Conditions:**
- HTTP 4xx / 5xx from the Claude API
- Response body does not parse as valid JSON (for extraction and validation prompts)
- Response body is empty or below minimum length threshold
- Required output fields are missing from the parsed response
- `extraction_status = "failed"` returned by Prompt 1

**Response:**

| Condition | Action |
|---|---|
| HTTP 429 (rate limit) | Automatic retry with exponential backoff: 30s → 2m → 5m. After 3 attempts, log and escalate. |
| HTTP 5xx (server error) | Retry twice with 60-second delay. After 2 failures, log and pause workflow. |
| Invalid JSON response | Log raw response to error_log; set stage status = "failed"; create HR queue task. |
| Missing required fields | Flag as `ai_response_invalid`; route to human review queue with raw output attached. |

---

### Level 2 — Validation Blocks (Business Logic Errors)

**Where caught:** After Prompt 2 (validation) returns its result; evaluated by n8n Switch node.

**Conditions:**
- `validation_status = "failed"` (blocking missing fields or documents)
- `human_review_required = true`
- Jurisdiction identified as outside standard operating regions
- Employment type is `contractor` with no `end_date`

**Response:**

| Condition | Action |
|---|---|
| Blocking validation failure | Pipeline halted at Stage 2. Airtable record status → "blocked". HR queue task created with issue list. Slack alert to HR channel. |
| Human review required | Pipeline paused. Manager / HR notified via Slack and Airtable HR queue. Pipeline resumes only when `reviewed_by` and `reviewed_at` are populated. |
| Advisory warnings only | Pipeline continues. Warnings recorded in `validation_result.document_issues`. HR dashboard flagged. |

---

### Level 3 — Provisioning Failures (External API Errors)

**Where caught:** n8n Error branch on each provisioning API call (Okta, Slack, Jira, Google Workspace).

**Conditions:**
- API returns 4xx (auth failure, duplicate account, permission denied)
- API returns 5xx (system outage)
- API timeout (> 30 seconds)
- Account already exists in target system (duplicate hire scenario)

**Response:**

| Condition | Action |
|---|---|
| Auth / permission error (4xx) | Log to `error_log` with error_type `provisioning_failed`. Create IT queue task in Jira. Do not retry automatically — requires credential review. |
| System outage (5xx) | Retry 3× with 5-minute backoff. After 3 failures, log and create IT queue task. Set that system's `provisioning.status = "failed"`. |
| Duplicate account | Log as warning. Fetch existing account ID, write to `provisioning.external_id`. Continue pipeline. Flag for HR review. |
| Partial provisioning (some systems failed) | Continue pipeline with successfully provisioned systems. Failed systems logged and queued for manual action. Employee notified of partial access on day one. |

---

### Level 4 — Communication Delivery Failures

**Where caught:** n8n Error branch after Gmail, Slack, and Google Calendar API calls (Stage 6).

**Conditions:**
- Gmail bounce / invalid email address
- Slack API error (workspace not found, user not yet in system)
- Calendar API conflict or permission error

**Response:**

| Condition | Action |
|---|---|
| Gmail delivery failure | Retry 3× with 10-minute backoff. After 3 failures, set `communications.welcome_email.status = "failed"`. HR queue task created: "Send welcome email manually." |
| Slack API error | Log error. Retry once after 5 minutes. If still failing, set status = "failed". HR notified to send welcome message manually. |
| Calendar conflict | Log and skip. HR queue task created: "Rebook day-one calendar invite manually." |

---

### Global Error Escalation Rules

All errors, regardless of level, are written to the `error_log` array on the `OnboardingRecord` in Airtable and are visible in the Retool HR dashboard.

| Condition | Escalation |
|---|---|
| Any error with `retry_count >= 3` | Automatically escalated to HR queue as unresolved; flagged in Retool dashboard. |
| Any error blocking pipeline progression for > 24 hours | Slack alert sent to HR manager and IT lead. |
| `at_risk = true` during tracking | Slack DM to hiring manager with recommended action; Airtable HR queue task created. |
| Any error involving PII in the payload | Payload sanitised before logging (PII fields replaced with `[REDACTED]`). Security team notified if data exfiltration is suspected. |

---

## Architecture Summary

```
[Intake sources] → n8n (orchestrator) → Claude API (6 AI tasks)
                                       ↓
                              Airtable (canonical record)
                                       ↓
                    [Delivery systems: Gmail, Slack, Okta, Jira, LMS, Calendar]
                                       ↓
                         Retool dashboard (HR visibility + review gates)

Error handling: 4 levels → retry → HR queue → Retool escalation
```

---

*Document prepared as part of Enterprise Onboarding Automation Assessment — Phase 3.*  
*All three phases complete. Ready for implementation planning or stakeholder review.*
