## Candidate Information
- Full Name: Syeda Fariya Raza
- Email: sy.faraza2899@gmail.com
- LinkedIn or Portfolio: https://www.linkedin.com/in/fariyar/
- Submission Date: 2026-03-13

## Overview
I designed and scaffolded an AI-powered onboarding automation system that combines deterministic workflow orchestration with controlled AI usage for extraction, classification, personalization, and communication drafting. The submission includes a detailed architecture document, production-oriented prompt pack, a workflow JSON scaffold, and a runnable Python prototype that demonstrates core routing and task generation logic.

## Task 1: AI-Powered Automation Design

### Workflow Logic
The workflow runs in five phases:
1. Intake and pre-validation from HRIS/form submissions.
2. AI extraction and confidence-based validation from onboarding documents.
3. Policy-driven routing and task orchestration for HR, IT, Manager, and Compliance.
4. AI-generated onboarding plan and communication drafts with approval gates.
5. Milestone tracking, digest generation, and completion audit.

### Where AI Is Used
- Classification: case routing (`standard`, `manager-review`, `compliance-review`)
- Document processing: extraction from uploaded documents with confidence scoring
- Workflow decision support: recommendations combined with deterministic policy rules
- Automatic drafting: welcome email + manager brief
- Recommendations/personalization: first 14-day plan + role-specific training suggestions

### Prompt Engineering
I used schema-bound prompts with:
- strict JSON outputs
- confidence scoring
- null-on-unknown behavior
- policy-safe instructions (no unsupported inferences)
- prompt versioning fields for governance (`prompt_id`, `prompt_version`, `model`)

See full prompts in `starter/prompts/prompts.md`.

### Data Flow and Integrations
- Trigger: webhook/HRIS event
- Processing: normalization -> AI extraction -> policy gate -> classification
- Orchestration: Jira/Asana tasks for HR/IT/Manager/Compliance
- Communication: email + Slack notifications
- Tracking: Airtable/Sheet onboarding pipeline table
- Auditability: workflow decision logs with timestamps and model metadata

### Business Impact
- Faster onboarding cycle time through SLA-driven automation
- Better data quality via confidence-based extraction and human review routing
- Reduced HR coordination load and fewer manual handoffs
- More consistent and personalized new-hire experience
- Better compliance traceability with audit logs

## Task 2: Implementation Demo

### Demo Type
- n8n-style workflow scaffold JSON
- Python code scaffold prototype
- Architecture diagram (Mermaid)

### Files Included
- `starter/design-solution.md`
- `starter/prompts/prompts.md`
- `starter/workflows/onboarding-workflow.json`
- `starter/code/mock_onboarding_orchestrator.py`
- `starter/code/sample_new_hire.json` (compliance-review path)
- `starter/code/sample_standard_hire.json` (standard auto-approved path)
- `starter/diagrams/onboarding-architecture.md`
- `starter/screenshots/README.md`

### Flow of Data
1. New-hire intake payload is received.
2. Payload is normalized and docs are evaluated.
3. AI extraction returns structured fields with confidence scores.
4. Classification determines case type: `standard`, `manager-review`, or `compliance-review`.
5. Policy gates determine auto-path vs manual review.
6. Function-specific tasks are created with SLA-based due dates.
7. Personalized 5-day onboarding plan is generated.
8. Welcome email and manager briefing summary are drafted.
9. Milestone check-ins are scheduled (D-7 through Day 30).
10. Audit log captures run metadata, prompt versions, and decision path.

### Pain Points Solved
- Eliminates repetitive coordination across HR, IT, and managers.
- Reduces delays from missing documents and unclear ownership.
- Standardizes onboarding quality while preserving human control for high-risk cases.

## Assumptions
- HRIS can emit webhook events or export intake records reliably.
- A tasking system (Jira/Asana/ClickUp) is available for SLA-based execution.
- AI API access is available in the automation platform.
- PII handling policies permit controlled AI use with approved vendors.

## Setup Instructions
1. Review architecture and prompts in `starter/design-solution.md` and `starter/prompts/prompts.md`.
2. Import or map `starter/workflows/onboarding-workflow.json` into your automation platform as a scaffold.
3. Run prototype locally:
   ```
   python starter/code/mock_onboarding_orchestrator.py
   ```
4. The prototype processes both sample files automatically:
   - `sample_new_hire.json` — compliance-review path (missing doc)
   - `sample_standard_hire.json` — standard auto-approved path
5. Edit either sample or add new `sample_*.json` files to simulate additional scenarios.

## Optional Notes
The design intentionally uses hybrid decisioning (AI suggestions + deterministic policy checks) to improve trust, auditability, and enterprise safety.
