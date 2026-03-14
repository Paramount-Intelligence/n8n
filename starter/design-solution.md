# AI Onboarding Automation – Design Solution

**Author:** Dileep Singh  
**Role Applied For:** Data Scientist  
**Organization:** Paramount Intelligence  

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Step-by-Step Workflow Logic](#step-by-step-workflow-logic)
3. [AI Usage Across the Onboarding Flow](#ai-usage-across-the-onboarding-flow)
4. [Prompt Engineering Details](#prompt-engineering-details)
5. [Integrations and Data Flow](#integrations-and-data-flow)
6. [Operational Benefits and Expected Impact](#operational-benefits-and-expected-impact)
7. [Security, Compliance, and Auditability](#security-compliance-and-auditability)
8. [Error Handling and Edge Cases](#error-handling-and-edge-cases)
9. [Scalability Considerations](#scalability-considerations)

---

## Executive Summary

Enterprise onboarding today is slow, fragmented, and inconsistent. HR teams coordinate across spreadsheets, email threads, and disconnected tools — while new hires wait days for access, guidance, and a sense of belonging.

This solution proposes an **AI-powered onboarding automation system** that transforms the new hire journey from reactive and manual into proactive, intelligent, and scalable. The system covers the full onboarding lifecycle: intake, document processing, task orchestration, personalized communication, IT provisioning coordination, and milestone tracking.

**Core design principles:**
- AI is applied where it creates the most operational leverage — not everywhere
- The workflow is observable and auditable at every step
- Human review is preserved for high-stakes decisions
- The system is designed to run on widely available tools (n8n, OpenAI API, Airtable, Google Workspace)

---

## Step-by-Step Workflow Logic

### Phase 1 — Trigger: New Hire Record Created

**Source:** ATS (Greenhouse, Lever, or Workday) fires a webhook when a candidate is marked "Hired."

**Data captured:**
- Full name, personal email, phone
- Job title, department, reporting manager
- Start date, work location (remote / on-site / hybrid)
- Employment type (full-time, part-time, contractor)

**Automation actions:**
1. n8n webhook node receives the payload
2. A new employee record is created in Airtable with status `INITIATED`
3. A unique `onboarding_id` is generated and logged
4. A pre-onboarding welcome email is sent to the new hire with a secure intake form link

---

### Phase 2 — Intake & Data Validation

**Goal:** Collect all required new hire information before documents and tasks are triggered.

**Actions:**
1. New hire submits intake form (Typeform or Google Forms) — pre-filled with known ATS data
2. On submission, an n8n HTTP node sends the form payload to the AI extraction node
3. AI normalizes free-text responses, corrects formatting inconsistencies, and flags missing required fields
4. If any required field is missing, a Slack alert is sent to the HR coordinator with the specific gap
5. Airtable record is updated with validated, normalized data
6. Status moves to `INTAKE_COMPLETE`

---

### Phase 3 — Document Collection & AI Processing

**Goal:** Collect, classify, validate, and extract structured data from onboarding documents.

**Documents handled:**
| Document | Required For |
|---|---|
| Government-issued ID | All employees |
| Signed offer letter | All employees |
| Tax form (W-4 or local equivalent) | All employees |
| Bank/payroll details | All employees |
| NDA / IP agreement | Full-time and contractors |
| Professional certificates | Role-dependent |
| Policy acknowledgements | All employees |

**Sub-steps:**

**3a. Document Upload**
- New hire uploads documents through a secure portal (DocuSign or a custom Google Forms file upload)
- Files are stored in a restricted Google Drive folder named by `onboarding_id`

**3b. AI Document Classification**
- Each uploaded file is passed to the LLM with a classification prompt
- AI returns: document type, confidence score, and any flags
- Unrecognized documents are routed to HR for manual review

**3c. AI Data Extraction**
- ID documents: extract full name, date of birth, ID number, expiry
- Offer letter: extract role, salary band, start date, manager
- Tax forms: extract filing status and tax code
- Extracted fields are matched against the Airtable record for consistency

**3d. Completeness Gate**
- System checks all required documents are received and verified
- Missing document reminder emails are triggered every 48 hours
- If documents are still missing 72 hours before start date, HR receives a priority Slack alert
- Status moves to `DOCS_VERIFIED` only when all required documents pass

---

### Phase 4 — Role-Based Task Orchestration

**Goal:** Generate and assign a personalized onboarding task checklist based on the new hire's profile.

**How it works:**
1. The system queries a task template library (JSON config file stored in the repo)
2. Templates are tagged by: `department`, `role_level`, `location_type`, `employment_type`
3. The AI reads the new hire's enriched profile and selects the matching task set
4. Tasks are created in Asana (or Jira/Notion) and assigned to responsible owners with due dates

**Task categories:**
| Category | Owner | Examples |
|---|---|---|
| HR Admin | HR Coordinator | Sign NDA, submit tax forms, I-9 verification |
| IT Setup | IT Team | Laptop provisioning, email account creation, software licenses |
| Access & Permissions | IT + Manager | VPN setup, system access requests, badge issue |
| Training | L&D / New Hire | Compliance training, product walkthroughs, tool tutorials |
| Culture & Integration | Manager + Buddy | Team introductions, 1:1 scheduling, culture reading |
| New Hire Actions | New Hire | Complete profile, join Slack channels, review handbook |

---

### Phase 5 — Personalized Onboarding Plan Generation

**Goal:** Create a role-specific onboarding plan for the new hire before Day 1.

**How it works:**
1. AI receives the enriched employee profile (role, department, location, manager, employment type)
2. AI generates a structured first-week plan covering: welcome guidance, key contacts, required resources, first-week priorities, and recommended training paths
3. The plan is formatted as a Notion page or Google Doc and shared with the new hire and their manager
4. Manager receives a parallel summary with suggested talking points for the Day 1 conversation

---

### Phase 6 — Communication Orchestration

**Goal:** Ensure timely, personalized, and consistent communication throughout onboarding.

**Automated communications:**
| Trigger | Recipient | Content |
|---|---|---|
| Record created | New hire | Welcome email + intake form link |
| Docs verified | New hire | Confirmation + what to expect next |
| 5 days before start | Manager | Manager prep guide + new hire summary |
| Day 1 | New hire | Day 1 schedule, access links, buddy intro |
| Day 3 | New hire | Check-in prompt + FAQ |
| Day 7 | New hire | Week 1 reflection form |
| Day 30 | New hire + HR | 30-day milestone survey |

All email drafts are AI-generated from templates with personalized fields injected.

---

### Phase 7 — IT & Access Provisioning Coordination

**Goal:** Ensure all system access and equipment is ready before Day 1.

**Actions:**
1. IT task ticket is auto-created in Jira with the full access requirements checklist
2. IT team confirms completion in the ticket
3. n8n polls for ticket status every 6 hours
4. If IT tasks are not completed 48 hours before start date, Slack alert is sent to IT lead and HR
5. Status moves to `IT_READY` once confirmed

---

### Phase 8 — Progress Monitoring & HR Dashboard

**Goal:** Give HR and managers real-time visibility into each new hire's onboarding progress.

**How it works:**
1. All status changes update the Airtable record in real time
2. An Airtable dashboard (or connected Google Sheets view) shows: status per new hire, pending documents, overdue tasks, upcoming start dates
3. Weekly digest email is sent to HR summarizing all active onboardings
4. Any onboarding stuck in a phase for more than 72 hours triggers an automatic escalation alert

---

### Phase 9 — Day 1 Readiness Check

**Goal:** Confirm everything is in place before the new hire's first day.

**Automated checklist run 24 hours before start date:**
- ✅ All documents received and verified
- ✅ All IT tasks completed
- ✅ Onboarding plan shared with new hire
- ✅ Manager notified
- ✅ Day 1 calendar invites sent

If any item fails the check, HR receives a targeted alert with the specific blocker.

---

## AI Usage Across the Onboarding Flow

| Workflow Step | AI Task | Model Used | Output Format |
|---|---|---|---|
| Intake form processing | Field extraction + normalization | GPT-4o | JSON |
| Document classification | Identify document type + flag issues | GPT-4o Vision | JSON |
| Document data extraction | Extract key fields from ID, offer letter, tax forms | GPT-4o | JSON |
| Task generation | Match task templates to employee profile | GPT-4o | JSON array |
| Onboarding plan creation | Generate personalized first-week plan | GPT-4o | Markdown / Notion block |
| Welcome email drafting | Personalized email generation | GPT-4o | Plain text / HTML |
| Manager summary | Summarize new hire profile for manager | GPT-4o | Markdown |
| Check-in prompts | Generate contextual check-in messages | GPT-3.5-turbo | Plain text |
| Feedback summarization | Summarize survey responses for HR review | GPT-4o | Bullet summary |

**Design principle:** GPT-4o is used for complex extraction, generation, and classification. GPT-3.5-turbo is used for lighter, high-volume tasks (check-ins, reminders) to control cost.

---

## Prompt Engineering Details

### Prompt 1 — Document Data Extraction

**Objective:** Extract structured fields from uploaded onboarding documents.

**Prompt:**
```
You are an HR document processing assistant operating inside an enterprise onboarding system.

You will receive the text content extracted from an employee onboarding document.

Your task is to extract the following fields and return them as valid JSON:
- full_name
- date_of_birth (ISO 8601 format)
- document_type (one of: government_id, offer_letter, tax_form, bank_details, nda, certificate, policy_acknowledgement, unknown)
- document_number (if applicable)
- expiry_date (ISO 8601 format, if applicable)
- issuing_authority (if applicable)
- issues_found (list of strings describing any problems, inconsistencies, or missing fields)
- requires_manual_review (boolean)

If a field is not present in the document, return null for that field.
Do not guess or hallucinate values. If you are uncertain, set requires_manual_review to true and describe the issue in issues_found.

Return only valid JSON. No explanation text.
```

---

### Prompt 2 — Personalized Onboarding Plan Generation

**Objective:** Generate a tailored first-week onboarding plan for the new hire.

**Prompt:**
```
You are an onboarding experience designer. Your job is to create a personalized first-week onboarding plan for a new employee joining an enterprise organization.

Here is the employee profile:
- Name: {{full_name}}
- Job Title: {{job_title}}
- Department: {{department}}
- Work Location: {{work_location}}
- Employment Type: {{employment_type}}
- Start Date: {{start_date}}
- Reporting Manager: {{manager_name}}

Generate a structured first-week onboarding plan that includes:
1. A short welcome message (2-3 sentences, warm and professional)
2. Day 1 priorities (3-5 bullet points)
3. Key contacts to meet in the first week (list with role and suggested meeting format)
4. Required resources and tools to set up
5. Recommended learning or training for their role
6. One cultural or team integration suggestion

Format the output as clean Markdown suitable for a Notion page.
Keep the tone professional but human and approachable.
```

---

### Prompt 3 — Welcome Email Drafting

**Objective:** Generate a personalized welcome email from the HR team to the new hire.

**Prompt:**
```
You are an HR communications assistant. Write a warm, professional welcome email to a new employee joining the company.

Employee details:
- Name: {{full_name}}
- Job Title: {{job_title}}
- Department: {{department}}
- Start Date: {{start_date}}
- Manager: {{manager_name}}

The email should:
- Be addressed personally to the employee by first name
- Congratulate them and express genuine enthusiasm for them joining
- Briefly outline what they can expect in their first week
- Tell them their onboarding plan will be shared separately
- Include a note that their manager has been notified and will reach out
- Close warmly with the HR team's name as the sender

Keep the email concise (under 200 words). Plain text format. No subject line needed.
```

---

### Prompt 4 — Manager Briefing Summary

**Objective:** Generate a concise summary for the hiring manager ahead of their new hire's start date.

**Prompt:**
```
You are an HR operations assistant. Create a brief manager briefing for an upcoming new hire.

New hire profile:
{{employee_profile_json}}

Pending onboarding items:
{{pending_tasks_json}}

Write a short summary (under 150 words) that:
- Introduces the new hire and their start date
- Highlights any pending items that the manager should be aware of
- Suggests 2-3 actions the manager should take in the first week
- Flags any risks or blockers if present

Tone: professional, direct, helpful. Plain text format.
```

---

### Prompt Design Principles Applied

1. **Explicit output format:** Every prompt specifies JSON or Markdown — no free-form responses that break automation
2. **Strict role instruction:** Each prompt opens with a clear persona and task context
3. **No hallucination tolerance:** Prompts explicitly instruct the model to return `null` rather than guess
4. **Fallback built in:** `requires_manual_review` flag ensures uncertain outputs are escalated to humans
5. **Minimal ambiguity:** Field names, formats (ISO 8601), and enumerated options are all specified
6. **Context injection via templates:** `{{variable}}` placeholders are filled by the automation layer before the API call

---

## Integrations and Data Flow

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    TRIGGER LAYER                        │
│  ATS (Greenhouse/Lever) → Webhook → n8n                 │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   PROCESSING LAYER                      │
│  n8n Workflow Engine                                    │
│  ├── HTTP nodes (API calls)                             │
│  ├── Function nodes (JS logic)                          │
│  ├── Conditional/Switch nodes (routing)                 │
│  └── Error handling nodes                               │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                     AI LAYER                            │
│  OpenAI API (GPT-4o)                                    │
│  ├── Document extraction                                │
│  ├── Classification                                     │
│  ├── Plan generation                                    │
│  └── Communication drafting                             │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    DATA LAYER                           │
│  Airtable (master onboarding records)                   │
│  Google Drive (document storage)                        │
│  Google Sheets (reporting/export)                       │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│               DOWNSTREAM INTEGRATIONS                   │
│  Gmail / Outlook     → Automated emails                 │
│  Slack               → HR + IT alerts                   │
│  Asana / Jira        → Task management                  │
│  Google Calendar     → Scheduling                       │
│  Notion / Confluence → Onboarding plan delivery         │
│  DocuSign            → Document signing                 │
└─────────────────────────────────────────────────────────┘
```

### Data Flow Sequence

```
1. ATS webhook fires → n8n receives payload
2. n8n creates Airtable record (status: INITIATED)
3. Welcome email sent → new hire submits intake form
4. Form submission → n8n triggers AI extraction node
5. AI returns normalized JSON → Airtable record updated (status: INTAKE_COMPLETE)
6. Document upload link sent → new hire uploads files to Google Drive
7. n8n detects new files → sends each to AI classification + extraction
8. Extracted data validated → Airtable updated (status: DOCS_VERIFIED)
9. Task template engine runs → tasks created in Asana
10. AI generates onboarding plan → posted to Notion, shared via email
11. Manager briefing email sent
12. IT ticket created in Jira → n8n polls for completion
13. Day-1 readiness check runs → status: READY or BLOCKED (with alert)
14. Day 1 communications sent
15. Milestone check-ins triggered at Day 3, Day 7, Day 30
16. Feedback responses summarized by AI → HR dashboard updated
```

---

## Operational Benefits and Expected Impact

### Efficiency Gains

| Metric | Before Automation | After Automation | Improvement |
|---|---|---|---|
| Time to complete intake | 2–3 days (email back-and-forth) | Same day (automated form + validation) | ~80% faster |
| Document verification | 1–2 days (manual HR review) | Hours (AI extraction + flagging) | ~90% faster |
| Task creation per new hire | 45–60 min (HR manually assigns) | ~2 min (automated template matching) | ~95% faster |
| Onboarding plan creation | 30–60 min per hire | Auto-generated in seconds | ~99% faster |
| HR coordination emails | 15–20 per hire | 2–3 (exceptions only) | ~85% reduction |

### Accuracy and Consistency

- Structured AI extraction reduces manual data entry errors
- Completeness checks ensure no required documents are missed
- Standardized task templates ensure every new hire gets the same quality of onboarding regardless of which HR coordinator handles it

### New Hire Experience

- Personalized Day 1 plan makes new hires feel seen and prepared
- Timely, proactive communications reduce first-day anxiety
- Buddy assignment and manager prep ensure human connection is prioritized alongside automation

### HR Time Savings

- Estimated 3–5 hours of HR time saved per onboarding cycle
- HR focus shifts from data entry and coordination to exception handling and culture-building

---

## Security, Compliance, and Auditability

### Data Security
- All documents stored in Google Drive with role-based access control (RBAC)
- Airtable records are access-restricted by team
- OpenAI API calls use data that is not stored for training (via API, not ChatGPT interface)
- PII is not logged in n8n execution logs — only `onboarding_id` references are used in logs

### Compliance
- Document retention policies enforced via Google Drive auto-archive rules
- I-9 / local employment verification handled with appropriate manual review checkpoints
- All AI outputs flagged with `requires_manual_review: true` are held for HR approval before action

### Auditability
- Every workflow execution in n8n is logged with timestamp, node, input, and output
- Every Airtable status change is timestamped and attributed to the triggering workflow
- AI prompts and responses are logged to a separate audit table for review
- A full audit trail per `onboarding_id` is available for HR compliance review

---

## Error Handling and Edge Cases

| Scenario | System Response |
|---|---|
| ATS webhook fails | n8n retry with exponential backoff (3 attempts); Slack alert if all fail |
| Intake form not submitted within 48 hrs | Automated reminder email sent; HR notified at 72 hrs |
| AI extraction returns low-confidence result | `requires_manual_review: true` flag → HR review queue |
| Unrecognized document type uploaded | Classified as `unknown` → routed to HR with original file |
| Missing required document 72 hrs before start | Priority Slack alert to HR coordinator |
| IT tasks not completed 48 hrs before start | Escalation alert to IT lead + HR |
| Onboarding plan generation API failure | Fallback to standard template; HR notified to personalize manually |
| New hire start date changes | Workflow recalculates all downstream due dates automatically |
| New hire withdraws before start | HR manually triggers `CANCELLED` status; all pending tasks closed |

---

## Scalability Considerations

- **Horizontal scale:** n8n supports parallel workflow executions — multiple new hires can be processed simultaneously without queue bottlenecks
- **Template library:** Task templates are maintained in a JSON config file — HR can add new templates without touching workflow code
- **Multi-location support:** Location field drives country-specific document and task requirements — adding a new country requires only a new template entry
- **Cost control:** AI calls are routed by complexity — GPT-3.5-turbo for lightweight tasks, GPT-4o for extraction and generation
- **HRIS integration ready:** The architecture is designed to accept webhooks from any HRIS (Workday, BambooHR, HiBob) with a simple field mapping config
- **Monitoring:** n8n execution logs + Airtable dashboards provide ops visibility without additional infrastructure
