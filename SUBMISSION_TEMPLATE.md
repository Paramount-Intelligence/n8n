# Candidate Submission Template

## Candidate Information

- **Full Name:** Dileep Singh
- **Email:** baghirajput2326@gmail.com
- **LinkedIn or Portfolio:** https://www.linkedin.com/in/dileep-singh-6a713b263/
- **Submission Date:** 2026-03-13

---

## Overview

This submission presents a complete AI-powered onboarding automation architecture for enterprise environments. The solution covers the full new hire lifecycle — from ATS trigger through Day 1 readiness — using n8n for workflow orchestration, GPT-4o for document extraction and personalization, and Airtable as the master data layer.

The design prioritizes practical automation over theoretical complexity: every AI step has a clear input, output format, and fallback for human review. The workflow is auditable, scalable, and deployable using widely available tools.

---

## Task 1: AI-Powered Automation Design

### Workflow Logic

The onboarding workflow proceeds through 9 defined phases:

1. **Trigger** — ATS webhook fires when a candidate is marked "Hired." n8n receives the payload, assigns an `onboarding_id`, and creates an Airtable record with status `INITIATED`.

2. **Intake & Validation** — A pre-filled intake form is emailed to the new hire. On submission, AI normalizes the data, flags missing fields, and alerts HR via Slack if required information is absent.

3. **Document Collection & AI Processing** — New hire uploads documents to a secure portal. Each file is classified by document type (GPT-4o), key fields are extracted as structured JSON, and a completeness gate checks all required documents are verified before the workflow proceeds.

4. **Role-Based Task Orchestration** — A task template library (tagged by role, department, location, employment type) is matched to the new hire profile. Tasks are auto-created in Asana/Jira and assigned to HR, IT, the manager, and the new hire with calculated due dates.

5. **Personalized Onboarding Plan Generation** — GPT-4o generates a tailored first-week plan including welcome message, Day 1 priorities, key contacts, required tools, and training recommendations. Delivered as a Notion page shared with the new hire and manager.

6. **Communication Orchestration** — AI drafts all onboarding communications: welcome email, manager briefing, check-in prompts at Day 3/7/30, and milestone reminders. Sent via Gmail/Outlook on automated schedules.

7. **IT & Access Provisioning Coordination** — IT tasks are auto-created in Jira. n8n polls for completion every 6 hours and escalates to the IT lead and HR if tasks are not completed 48 hours before the start date.

8. **Progress Monitoring & Dashboard** — Airtable tracks real-time status across all active onboardings. HR receives a weekly digest. Any onboarding stuck in a phase for 72+ hours triggers an escalation alert.

9. **Day-1 Readiness Check** — 24 hours before the start date, the system runs an automated readiness checklist (docs verified, IT ready, plan shared, manager notified). Any failures generate an immediate priority Slack alert.

---

### Where AI Is Used

**Classification**
Each uploaded onboarding document is classified by GPT-4o Vision into one of: `government_id`, `offer_letter`, `tax_form`, `bank_details`, `nda`, `certificate`, `policy_acknowledgement`, or `unknown`. Unrecognized types are routed to HR.

**Document Processing**
GPT-4o extracts structured fields (name, DOB, document number, expiry, issuing authority) from each document and returns valid JSON. A `requires_manual_review` flag is set when the model is uncertain or finds inconsistencies — preventing AI errors from propagating downstream.

**Workflow Decision Logic**
AI reads the new hire's enriched profile and determines which task templates to activate. This handles edge cases like remote vs. on-site provisioning, contractor vs. full-time compliance requirements, and location-specific document rules.

**Automatic Drafting**
GPT-4o drafts: welcome emails, manager briefings, Day 1 schedule messages, and milestone check-in prompts. GPT-3.5-turbo is used for lighter, high-volume communications to control API cost.

**Recommendations and Personalization**
GPT-4o generates a role-specific onboarding plan with personalized training recommendations, suggested contacts, and first-week priorities based on the new hire's department, location, and seniority level.

---

### Prompt Engineering

Four core prompts power the AI layer. All prompts follow the same design principles:

- **Explicit JSON output format** — no free-form responses that break automation
- **Clear role instruction** — each prompt opens with a specific persona and task
- **Null over hallucination** — prompts explicitly require `null` rather than guessed values
- **Manual review fallback** — `requires_manual_review: true` ensures uncertain outputs are held for HR approval
- **Template variable injection** — `{{variable}}` placeholders filled by n8n before each API call

**Prompt 1 – Document Field Extraction (GPT-4o, temperature: 0.1)**
Extracts: full_name, date_of_birth, document_type, document_number, expiry_date, issuing_authority, issues_found, requires_manual_review. Returns valid JSON only.

**Prompt 2 – Onboarding Plan Generation (GPT-4o, temperature: 0.7)**
Generates a Markdown first-week plan including welcome message, Day 1 priorities, key contacts, tool setup checklist, training recommendations, and one culture integration suggestion.

**Prompt 3 – Welcome Email Drafting (GPT-4o, temperature: 0.5)**
Writes a personalized welcome email (<200 words) from the HR team, referencing the new hire's name, role, start date, and manager.

**Prompt 4 – Manager Briefing Summary (GPT-3.5-turbo, temperature: 0.5)**
Generates a concise (<150 word) manager briefing with new hire introduction, pending items, suggested Day 1 actions, and risk flags.

---

### Data Flow and Integrations

**Google Workspace**
Gmail/Google Calendar for automated email communications and orientation scheduling. Google Drive for encrypted document storage (access-restricted by `onboarding_id`).

**HRIS / ATS**
Greenhouse, Lever, or Workday fire the initial webhook trigger. The architecture accepts any HRIS that supports webhooks with a field mapping config.

**Slack**
Receives HR alerts for missing fields, document review flags, IT escalations, Day-1 readiness blockers, and plan-ready confirmations.

**Email**
Gmail or Outlook send all new hire and manager communications via AI-drafted templates.

**Calendar**
Google Calendar or Outlook for scheduling orientation sessions, 1:1s, and buddy intro calls.

**Document Storage**
Google Drive with folder-per-hire structure, restricted access, and auto-archive policy for compliance.

**Automation Platform**
n8n (self-hosted) as the core orchestration engine. All workflow logic, API calls, conditional routing, and scheduling run through n8n nodes. Zapier is a viable alternative.

**Full data flow:**
ATS webhook → n8n → Airtable (record created) → Gmail (welcome email) → Form submission → AI extraction → Airtable (updated) → Document upload → AI classification/extraction → Task creation (Asana/Jira) → AI plan generation → Notion (plan delivery) → Gmail (manager briefing) → Polling for IT completion → Day-1 readiness check → Milestone check-ins

---

### Business Impact

**Efficiency**
Onboarding cycle time reduced by an estimated 60-80%. Intake that previously required 2-3 days of email back-and-forth completes same-day. Task creation that took HR 45-60 minutes per hire is automated in under 2 minutes.

**Accuracy**
AI extraction with structured JSON output and completeness gates eliminates common manual data entry errors. Every AI output with uncertainty is flagged for human review rather than passed downstream.

**Personalization**
Each new hire receives a role-specific onboarding plan, personalized communications, and a tailored task checklist — rather than a generic one-size-fits-all packet.

**HR Time Savings**
Estimated 3-5 hours of HR coordinator time saved per onboarding cycle. HR focus shifts from data entry and email coordination to exception handling and culture-building.

**New Hire Experience**
Proactive communications before Day 1 reduce first-day anxiety. Personalized plans give new hires clarity and confidence. Timely check-ins signal that the organization cares about their integration.

---

## Task 2: Implementation Demo

### Demo Type

- **n8n workflow export JSON** — fully annotated workflow with all nodes, connections, and logic
- **Python helper scripts** — document extraction CLI and onboarding plan generator
- **Architecture diagram (SVG)** — full workflow visualization across all layers
- **Task template config (JSON)** — the rule-based task assignment library

### Files Included

```
starter/
├── design-solution.md               ← Full Task 1 architecture document
├── workflows/
│   └── n8n-onboarding-workflow.json ← n8n workflow export (importable)
├── code/
│   ├── document_extractor.py        ← Python AI extraction + plan generation helper
│   └── task-templates.json          ← Task template library (17 templates)
└── diagrams/
    └── workflow-architecture.svg    ← Full system architecture diagram
```

### Flow of Data

1. ATS webhook payload enters n8n via the Webhook node
2. Function node validates required fields and assigns `onboarding_id`
3. Airtable node creates the master record with status `INITIATED`
4. IF node routes: missing fields → Slack alert; complete record → welcome email
5. Gmail node sends welcome email with intake form link
6. Form submission triggers document upload flow
7. n8n detects uploaded files in Google Drive and sends each to the OpenAI HTTP node
8. AI returns structured JSON → Function node parses and sets `requires_manual_review` flag
9. AI generates onboarding plan (Markdown) → posted to Notion
10. AI generates manager summary → sent via Gmail
11. Airtable updated with `PLAN_GENERATED` status and Notion URL
12. Schedule trigger runs readiness check every 6 hours → Slack alert if any checklist item fails
13. Milestone check-ins fired at Day 3, 7, 30 via Schedule nodes

### Pain Points Solved

**Pain point:** HR spends hours manually reviewing documents and chasing missing information.
**Solution:** AI document classification and extraction with completeness gating automates this entirely, only surfacing genuine exceptions for human review.

**Pain point:** Every new hire gets the same generic onboarding experience regardless of role or location.
**Solution:** Role-based task templates + AI-generated personalized plans ensure every hire gets a contextually relevant onboarding experience.

**Pain point:** IT provisioning often isn't ready by Day 1, creating a poor first impression.
**Solution:** IT tasks are auto-created 7 days before start date, and automated escalation alerts fire at 48-hour and 24-hour checkpoints if tasks remain incomplete.

**Pain point:** HR has no real-time visibility into where each onboarding stands.
**Solution:** Airtable dashboard with status fields updated at every workflow step gives HR a live view of all active onboardings and blockers.

---

## Assumptions

1. The company uses a modern ATS (Greenhouse, Lever, or Workday) that supports outbound webhooks.
2. An OpenAI API key is available for LLM calls. Model can be swapped to any compatible provider.
3. Airtable is used as the data layer. Google Sheets is a viable alternative with minor node changes.
4. n8n is self-hosted or running on n8n Cloud. Zapier can replicate most of the flow with equivalent zaps.
5. Document uploads are handled via a secure Google Form or DocuSign. The document text is extracted as plain text before being passed to the AI.
6. The onboarding plan is delivered via Notion. This can be replaced with Confluence, Google Docs, or email attachment with minor changes.
7. Mock/placeholder values are used for API keys, base IDs, and URLs in the workflow JSON. These must be replaced with real credentials before running.
8. The task template library covers common cases. Role-specific templates should be reviewed and extended by HR before production deployment.

---

## Setup Instructions

### To import and run the n8n workflow:
1. Install n8n: `npm install -g n8n` or use n8n Cloud
2. Open n8n → Import workflow → select `starter/workflows/n8n-onboarding-workflow.json`
3. Set credentials: OpenAI API key, Airtable API key + Base ID, Gmail/Google OAuth
4. Replace all `{{PLACEHOLDER}}` values in node parameters with real values
5. Activate the workflow — the webhook URL will be displayed in the Webhook node

### To run the Python helper:
```bash
pip install openai pymupdf python-dotenv
cp .env.example .env   # Add your OPENAI_API_KEY
python starter/code/document_extractor.py          # Demo mode
python starter/code/document_extractor.py --file path/to/doc.pdf   # Extract from PDF
python starter/code/document_extractor.py --plan path/to/profile.json  # Generate plan
```

---

## Optional Notes

- The workflow is designed to be modular — each phase can be activated independently. Teams can start with just the intake automation and add document processing and AI plan generation incrementally.
- The `requires_manual_review` flag throughout the AI layer is intentional. This system is designed to augment HR judgment, not replace it. Every AI output that is uncertain surfaces a human review checkpoint.
- For production deployment, I would recommend adding a secrets manager (AWS Secrets Manager or HashiCorp Vault) for API key management, and structured logging to a centralized observability platform (Datadog or CloudWatch) rather than relying solely on n8n execution logs.
- The architecture is HRIS-agnostic by design. Any system that emits a webhook or can be polled via REST API can serve as the trigger layer.
