# AI-Powered Onboarding Automation — Design Solution

## Overview

This document describes a complete AI-driven onboarding automation system designed to eliminate manual coordination across HR, IT, and management. The system ingests new hire data, processes and enriches it using AI, generates personalized onboarding plans, routes tasks to the right teams, and monitors progress through to the new hire's first 30 days.

The design prioritizes practical automation over theoretical perfection — every AI step produces structured output that feeds directly into the next stage of the workflow.

---

## Step-by-Step Workflow Logic

### Stage 1 — New Hire Intake (Trigger)

**What happens:**
A new hire record is created in the system. This can be triggered by:
- HR submitting a Google Form or Typeform intake form
- A record being added to an Airtable base or Google Sheet
- A webhook fired from an HRIS system (e.g., BambooHR, Workday, Rippling)

**Data collected at intake:**
- Full name, personal email, role/job title
- Department, team, and hiring manager
- Office location or remote status
- Employment type (full-time, contractor, part-time)
- Start date
- Any uploaded documents (offer letter, ID, signed NDA, policy acknowledgements)

**Automation trigger:**
n8n listens on a webhook or polls the intake form/sheet every 15 minutes. When a new record is detected, the workflow begins.

---

### Stage 2 — Document Processing and AI Extraction

**What happens:**
Uploaded documents (PDFs, images) are sent to an AI extraction step. The AI reads each document and pulls out structured information, flagging anything missing or inconsistent.

**AI Task:** Extract fields from onboarding documents and validate completeness.

**Prompt used:**

```
You are an HR onboarding assistant. You will be given one or more employee onboarding documents.

Extract the following fields exactly as they appear:
- full_name
- date_of_birth
- national_id_or_passport_number
- personal_email
- job_title
- department
- start_date
- manager_name
- employment_type (full-time / part-time / contractor)
- signed_documents (list all documents present)
- missing_documents (list any expected documents that appear absent)
- issues (list any inconsistencies, expired documents, or items requiring HR review)

Return ONLY valid JSON. Do not include explanation or commentary.
If a field cannot be found, set its value to null.
```

**Output:** A structured JSON record attached to the onboarding profile.

**Error handling:**
- If AI confidence is low or required fields are null, the record is flagged as `NEEDS_REVIEW` and routed to an HR agent via Slack/email before continuing.
- A human review step is inserted into the workflow — no automation continues until HR marks the record as `APPROVED`.

---

### Stage 3 — Onboarding Profile Creation

**What happens:**
The cleaned AI output is merged with role/department/location metadata to build a full onboarding profile. This profile is the single source of truth for all downstream steps.

**Profile fields:**
```json
{
  "employee_id": "auto-generated UUID",
  "full_name": "john smith",
  "email": "john.smith@company.com",
  "personal_email": "john@gmail.com",
  "role": "Senior Product Designer",
  "department": "Product",
  "team": "Growth",
  "manager": "Alex johnson ",
  "location": "Remote - Pakistan",
  "employment_type": "full-time",
  "start_date": "2025-08-01",
  "status": "ONBOARDING_IN_PROGRESS",
  "documents_verified": true,
  "onboarding_track": "product_design_senior",
  "created_at": "2025-07-15T10:00:00Z"
}
```

**Where it lives:** Airtable base or Google Sheets (acts as the onboarding tracker).

---

### Stage 4 — Task Generation and Routing

**What happens:**
Based on the onboarding profile, the system automatically generates tasks for each team involved and routes them to the right place.

**AI Task:** Determine which tasks are required based on role, department, and location.

**Prompt used:**

```
You are an onboarding operations coordinator. Given the employee profile below, generate a complete onboarding task list.

Employee profile:
{employee_profile_json}

Generate tasks for the following teams:
- HR: document collection, payroll setup, benefits enrollment
- IT: laptop provisioning, software access, email setup, security training
- Hiring Manager: intro meetings, 30/60/90 day plan, team introductions
- Compliance: required training modules based on role and location

For each task include:
- task_name
- assigned_to (team or person)
- due_date (relative to start_date, e.g. "3 days before start" or "Day 1")
- priority (high / medium / low)
- depends_on (list of task_names that must complete first, or empty array)

Return ONLY a JSON array of task objects.
```

**Routing logic:**
- IT tasks → create tickets in Jira or send to #it-onboarding Slack channel
- HR tasks → update Airtable and notify HR coordinator
- Manager tasks → send email + calendar invite to hiring manager
- Compliance tasks → trigger enrollment in LMS (e.g., TalentLMS, Docebo)

---

### Stage 5 — Personalized Onboarding Plan Generation

**What happens:**
AI generates a personalized onboarding document tailored to the employee's role, seniority, and department. This is sent to the new hire before their start date.

**AI Task:** Generate a first-week onboarding plan.

**Prompt used:**

```
You are a friendly and knowledgeable onboarding guide at a modern tech company.

Write a personalized onboarding plan for a new employee with the following profile:
- Name: {full_name}
- Role: {role}
- Department: {department}
- Manager: {manager}
- Start date: {start_date}
- Location: {location}
- Employment type: {employment_type}

The onboarding plan should include:
1. A warm welcome message addressed to the employee by name
2. What to expect on Day 1 (logistics, who to meet, what to bring or prepare)
3. First week priorities (3 to 5 key goals)
4. Key contacts and who to go to for what
5. Recommended resources, tools, and documentation to review
6. Required training or compliance items to complete in the first 2 weeks
7. A note about their 30-day check-in with their manager

Keep the tone warm, clear, and encouraging. Format using headers and bullet points.
```

**Output:** A formatted markdown document sent to the new hire's personal email and stored in Notion or Google Drive.

---

### Stage 6 — Communication Dispatch

**What happens:**
The workflow sends automated but personalized communications to all stakeholders.

**Communications generated:**

**Welcome email to new hire:**
```
AI Prompt: Draft a warm welcome email to {full_name} who is joining as {role} 
in the {department} team on {start_date}. Mention their manager {manager}, 
confirm their first day logistics, and express genuine enthusiasm. 
Keep it under 200 words. Professional but human tone.
```

**Manager briefing email:**
```
AI Prompt: Write a concise briefing email to {manager_name} summarizing 
the onboarding status of their new hire {full_name} ({role}). 
Include: start date, verified documents, pending IT tasks, 
and suggested first-week priorities. Under 150 words.
```

**HR confirmation:**
Plain summary of completed intake steps, flagged items, and next actions — sent to the HR coordinator.

**IT ticket:**
Structured data payload sent to the IT ticketing system with laptop spec requirements, software list, and access permissions based on role.

---

### Stage 7 — Milestone Monitoring and Feedback

**What happens:**
The workflow schedules automated check-ins at key milestones and collects structured feedback.

**Milestone triggers:**
- Day 1: Confirm new hire has received all access and completed Day 1 checklist
- Day 7: First week check-in prompt sent to new hire and manager
- Day 30: Formal onboarding feedback survey triggered
- Day 90: Final onboarding close-out and transition to standard HR processes

**AI usage at this stage:**
- Summarize free-text feedback from surveys into structured HR reports
- Flag any negative sentiment or blockers for immediate HR review
- Generate a concise onboarding completion summary per employee

**Feedback prompt:**
```
You are an HR analyst. Summarize the following onboarding feedback from a new hire.
Identify: overall sentiment (positive / neutral / negative), top 3 positive themes,
top 3 concerns or blockers, and one recommended action for HR.
Return as structured JSON.

Feedback text: {survey_response_text}
```

---

## AI Usage Summary

| Stage | AI Task | Why AI |
|---|---|---|
| Document Processing | Field extraction from PDFs/forms | Eliminates manual data entry |
| Profile Enrichment | Input normalization and validation | Ensures data quality |
| Task Generation | Role-based task list creation | Removes coordinator guesswork |
| Onboarding Plan | Personalized plan drafting | Scales to any role or location |
| Communications | Email and message drafting | Consistent tone, zero manual writing |
| Feedback Analysis | Survey summarization and sentiment | Fast HR review at scale |

---

## Prompt Engineering Principles

All prompts in this system follow these design rules:

**1. Role framing first**
Every prompt begins by telling the model what role it plays ("You are an HR onboarding assistant"). This anchors the tone and expertise.

**2. Explicit output format**
Every extraction or classification prompt specifies the output format (JSON, array, markdown). This makes the output directly usable by the next automation step without parsing guesswork.

**3. Null handling**
Prompts explicitly instruct the model to return `null` for missing fields rather than hallucinating values.

**4. Minimal ambiguity**
Prompts avoid open-ended questions. Every instruction is specific about what to include, what to exclude, and what length or structure to use.

**5. Fallback routing**
If AI output fails validation (missing required fields, malformed JSON), the record is flagged and a human review step is triggered before continuing.

---

## Data Flow and Integrations

```
[Google Form / HRIS / Webhook]
        ↓
[n8n Workflow Trigger]
        ↓
[Document Storage: Google Drive]
        ↓
[OpenAI API — Extraction + Validation]
        ↓
[Airtable — Onboarding Record Created]
        ↓
        ├──→ [Jira — IT Ticket Created]
        ├──→ [Slack — HR + Manager Notifications]
        ├──→ [LMS — Training Assigned]
        └──→ [Gmail — Welcome Email + Manager Brief]
        ↓
[OpenAI API — Onboarding Plan Generation]
        ↓
[Notion / Google Drive — Plan Stored]
        ↓
[Scheduled Milestone Triggers — Day 1 / 7 / 30 / 90]
        ↓
[Typeform — Feedback Survey]
        ↓
[OpenAI API — Feedback Summarization]
        ↓
[Airtable — Status Updated, HR Report Generated]
```

**Integration map:**

| System | Role |
|---|---|
| Google Forms / Typeform | New hire intake |
| Google Drive | Document storage |
| Airtable | Onboarding tracker and source of truth |
| OpenAI API (GPT-4o) | Extraction, generation, summarization |
| n8n | Workflow orchestration |
| Gmail / Outlook | Email communications |
| Slack | Team notifications and alerts |
| Jira | IT provisioning tickets |
| Google Calendar | Orientation and intro scheduling |
| TalentLMS / Docebo | Training and compliance assignment |
| Notion | Onboarding plan storage |

---

## Operational Benefits and Expected Impact

**Speed**
Onboarding tasks that previously took 2–3 days of manual coordination begin automatically within minutes of a new hire record being submitted.

**Consistency**
Every new hire receives the same structured process regardless of which HR coordinator is on duty or how busy the team is.

**Data quality**
AI extraction and validation catches missing documents and inconsistent data before it reaches downstream systems.

**Personalization at scale**
Each new hire receives a role-specific, name-personalized onboarding plan without any manual effort from HR or the hiring manager.

**Visibility**
All onboarding records, task statuses, and milestone completions are tracked in a single Airtable base, giving HR a real-time view across all active onboarding cases.

**HR time savings**
Estimated reduction of 4–6 hours of manual coordination per new hire. At 10 hires per month, this saves roughly 40–60 hours of HR and coordinator time monthly.

---

## Edge Cases and Human Review Points

The following scenarios always trigger a human review pause before automation continues:

- Required documents are missing or expired
- AI extraction returns null for more than 2 required fields
- Start date is less than 5 business days away (expedited onboarding lane)
- Employment type is contractor or part-time (different compliance requirements)
- Location is flagged as a new country or region with unknown legal requirements
- Negative sentiment detected in Day 7 or Day 30 feedback

---

## Security and Compliance Considerations

- Documents are stored in Google Drive with restricted access (HR only)
- PII is never logged in plaintext in automation workflow logs
- OpenAI API calls use the organization's API key with no training data opt-in
- All onboarding records include an audit trail of status changes with timestamps
- Document retention follows the company's data retention policy (configurable)
- Access to the Airtable onboarding base is role-restricted to HR and IT leads
