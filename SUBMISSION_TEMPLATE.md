# Candidate Submission Template

## Candidate Information
- Full Name: [Pawan kumar]
- Email: [danishutradi243@gmail.com]
- Submission Date: [13/03/2026]

---

## Overview

This submission presents a complete AI-powered onboarding automation system designed to eliminate manual coordination across HR, IT, and management. The solution covers end-to-end workflow design (Task 1) and a working prototype scaffold (Task 2) consisting of a Python simulation, an importable n8n workflow, and an architecture diagram.

The system automates new hire intake, document validation, task generation, personalized onboarding plan creation, multi-channel communication dispatch, and milestone monitoring — using GPT-4o at every step where AI creates meaningful operational leverage.

---

## Task 1: AI-Powered Automation Design

### Workflow Logic

The onboarding workflow runs across seven stages:

1. **Intake** — New hire submits a form (Google Forms, HRIS webhook, or custom portal). The n8n workflow triggers on submission.
2. **AI Extraction and Validation** — Uploaded documents and form data are sent to GPT-4o. The model extracts structured fields, identifies missing documents, and flags issues. Records with problems are routed to HR for review before continuing.
3. **Profile Creation** — Extracted data is merged with role and department metadata to build a structured onboarding profile in Airtable.
4. **Task Generation** — GPT-4o generates a role-specific task list covering HR, IT, manager, and compliance actions, with due dates relative to the start date.
5. **Onboarding Plan** — GPT-4o produces a personalized, markdown-formatted first-week onboarding plan tailored to the employee's role, team, location, and manager.
6. **Communication Dispatch** — The workflow sends a welcome email to the new hire, a briefing email to the manager, and creates an IT provisioning ticket in Jira.
7. **Milestone Monitoring** — Scheduled triggers fire at Day 1, 7, 30, and 90 to send check-ins, collect feedback, and summarize survey responses using AI.

Full step-by-step detail is in `starter/design-solution.md`.

### Where AI Is Used

**Classification and validation:**
GPT-4o classifies document types, validates completeness, and flags records that need HR review before automation continues.

**Document processing:**
AI extracts structured fields from uploaded PDFs and forms, reducing manual data entry to zero for clean submissions.

**Workflow decision logic:**
Task generation uses AI to determine which tasks are required based on role, department, employment type, and location — avoiding the need for rigid lookup tables.

**Automatic drafting:**
AI drafts the welcome email, manager briefing, and all milestone communications. Each message is personalized to the employee's profile.

**Recommendations and personalization:**
The onboarding plan AI step generates role-specific first-week priorities, key contacts, recommended tools, and compliance requirements — all tailored to the individual.

**Feedback analysis:**
At Day 30 and Day 90, survey responses are summarized by GPT-4o into structured HR reports with sentiment scoring and recommended actions.

### Prompt Engineering

All prompts follow five principles:

1. **Role framing** — Every prompt opens with a clear role instruction ("You are an HR onboarding assistant")
2. **Explicit output format** — All extraction and classification prompts require JSON output, making results directly usable downstream
3. **Null handling** — Prompts explicitly require `null` for missing fields rather than guessed values
4. **Minimal ambiguity** — Instructions are specific about what to include, exclude, and how to format
5. **Fallback routing** — If AI output fails validation, the record is flagged and a human review step is triggered

Key prompts are documented in full in `starter/design-solution.md` under the Prompt Engineering section.

### Data Flow and Integrations

| System | Role |
|---|---|
| Google Forms / Typeform | New hire intake form |
| Google Drive | Document storage |
| n8n | Workflow orchestration |
| OpenAI API (GPT-4o) | Extraction, task generation, plan creation, summarization |
| Airtable | Onboarding tracker and source of truth |
| Jira | IT provisioning ticket management |
| Gmail / Outlook | Welcome and briefing emails |
| Slack | HR and IT notifications |
| Notion | Onboarding plan storage |
| TalentLMS | Compliance training assignment |
| Google Calendar | Orientation scheduling |

### Business Impact

**Efficiency:** Onboarding tasks that previously required 2–3 days of manual coordination begin automatically within minutes of form submission.

**Accuracy:** AI extraction and validation catches missing documents and data errors before they reach downstream systems.

**Personalization:** Every new hire receives a role-specific onboarding plan with no manual effort from HR or the hiring manager.

**HR time savings:** Estimated 4–6 hours saved per hire. At 10 hires per month, that is 40–60 hours of recovered HR capacity monthly.

**New hire experience:** Consistent, professional, and personalized onboarding from Day 1 — regardless of which coordinator is on duty.

---

## Task 2: Implementation Demo

### Demo Type

- Python scaffold (runnable simulation of the full workflow)
- n8n workflow export (importable JSON with all nodes and connections)
- Mermaid architecture diagram (visual of the complete data flow)

### Files Included

```
starter/
├── design-solution.md                          ← Task 1: Full workflow design
├── code/
│   └── onboarding_automation.py               ← Python scaffold (runnable demo)
├── workflows/
│   └── n8n_onboarding_workflow.json           ← n8n export (importable)
└── diagrams/
    └── onboarding_workflow_diagram.png   ← Architecture diagram
```

### Flow of Data

1. Mock new hire record enters via `MOCK_NEW_HIRE_SUBMISSION` dict (simulates form input)
2. Stage 1 creates a record with a UUID and timestamp
3. Stage 2 sends data to AI extraction (mocked response in demo, real API call in production)
4. Stage 3 builds the enriched onboarding profile
5. Stage 4 generates a task list and prints it with owner and due dates
6. Stage 5 generates and prints the personalized onboarding plan
7. Stage 6 simulates sending emails and creating an IT ticket
8. Stage 7 logs the milestone schedule for Days 1, 7, 30, and 90

The n8n JSON mirrors this same flow with real integration nodes for Airtable, OpenAI, Jira, Gmail, Slack, and Notion.

### Pain Points Solved

**Manual document review:** AI extraction eliminates the need for HR to manually read every uploaded document and transfer fields into a tracker.

**Task coordination delays:** Automatic task generation and routing removes the multi-day lag between a new hire record being created and IT/HR/manager tasks being assigned.

**Inconsistent communications:** AI-drafted, template-free communications ensure every new hire and manager receives a professional, personalized message on the same day as submission.

**No visibility:** Airtable as a central tracker with status fields gives HR real-time visibility into every active onboarding case.

---

## Assumptions

- The company uses Google Workspace (Gmail, Google Drive, Calendar) as its primary collaboration stack
- Jira is used for IT task management
- Notion is used for internal documentation and onboarding plans
- The HRIS system can fire a webhook or export to a Google Sheet when a new hire is confirmed
- OpenAI API access is available with the organization API key
- Mock data is used in the Python scaffold; production would replace mock responses with real API calls
- The n8n workflow requires credential configuration (Airtable base ID, Notion database ID, Jira project, Gmail OAuth) before running

---

## Setup Instructions

### Python Scaffold

```bash
# Install dependencies
pip install openai python-dotenv requests

# Create a .env file
echo "OPENAI_API_KEY=your_key_here" > .env

# Run the simulation
python starter/code/onboarding_automation.py
```

The script runs in demo mode by default using mock AI responses. To enable real OpenAI calls, uncomment the production code blocks in each `call_ai_*` function.

### n8n Workflow

1. Open your n8n instance
2. Go to **Workflows → Import from File**
3. Upload `starter/workflows/n8n_onboarding_workflow.json`
4. Configure credentials: Airtable, OpenAI, Gmail, Slack, Jira, Notion
5. Replace placeholder IDs (YOUR_AIRTABLE_BASE_ID, YOUR_NOTION_DATABASE_ID)
6. Activate the workflow

### Architecture Diagram

Open `starter/diagrams/onboarding_workflow_diagram

---

## Optional Notes

- The system is designed to be modular — any integration node can be swapped for an alternative (e.g., Notion → Confluence, Airtable → Google Sheets, Jira → ClickUp)
- Human review pause points are intentionally built into both the Python scaffold and n8n workflow — automation does not continue past document validation failures without HR action
- The prompt designs use temperature 0 for extraction tasks (deterministic) and 0.3–0.7 for generative tasks (more natural output)
- The workflow is stateless — each run is independent, making it safe to retry without side effects
- Audit logging is built into the Airtable record (status, timestamps, linked URLs) to support HR compliance requirements
