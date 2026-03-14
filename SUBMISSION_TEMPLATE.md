# Candidate Submission Template

## Candidate Information
- Full Name: Huzaifa Ahmed
- Email: huzaifafabi15@gmail.com
- LinkedIn: https://www.linkedin.com/in/huzaifa-ahmed-b15214225/
- Submission Date: March 14th, 2026.

## Overview
This submission demonstrates an AI-powered onboarding automation workflow for enterprise environments. The solution automates new hire intake, document processing, task orchestration, and personalized onboarding plan generation, using AI and no-code automation tools. The system improves operational speed, consistency, and visibility across HR, IT, and hiring manager workflows.

---

## Task 1: AI-Powered Automation Design

### Workflow Logic
1. **Intake & Data Capture**: New hire submits details via Google Form, Typeform, or HRIS. Documents such as ID and agreements are uploaded.  
2. **AI-Based Data Extraction & Validation**: AI extracts structured data, normalizes free text, and flags missing or inconsistent fields for HR review.  
3. **Employee Profile Enrichment**: Combines submitted info with role, department, location, employment type, and manager info to generate a structured onboarding profile.  
4. **Task Generation & Routing**: Automatically generates tasks for HR, IT, compliance, and managers (account setup, laptop provisioning, training assignment, orientation planning).  
5. **Personalized Onboarding Plan Creation**: AI generates role-specific onboarding plans with first-week priorities, key contacts, and training paths.  
6. **Communication Support**: AI drafts welcome emails, manager handoff notes, check-ins, and milestone reminders.  
7. **Feedback & Milestone Monitoring**: Tracks milestones, triggers check-ins, and collects feedback for continuous improvement.

### Where AI Is Used
- **Document Processing:** Extracts structured fields from uploaded documents.  
- **Input Normalization:** Standardizes responses and resolves inconsistencies.  
- **Decision Support:** Determines tasks based on role, department, location, and employment type.  
- **Personalization:** Generates onboarding plans and communication drafts.  
- **Summarization:** Converts fragmented onboarding data into concise summaries.  
- **Workflow Acceleration:** Reduces time for drafting messages and interpreting forms.

### Prompt Engineering
**Example Prompt for Data Extraction:**
```
python
def extract_and_validate(data):
    required_fields = [
        "full_name", "personal_email", "job_title",
        "department", "location", "manager_name",
        "employment_type", "start_date"
    ]
    missing_fields = [f for f in required_fields if f not in data or not data[f]]
    missing_documents = [] if "uploaded_documents" in data and data["uploaded_documents"] else ["Missing documents"]

    extracted = {
        "structured_data": {k: data.get(k, "") for k in required_fields},
        "missing_fields": missing_fields,
        "missing_documents": missing_documents
    }
    return extracted

```
### Other Prompt Use Cases:
```
* Personalized first-week onboarding plan
* Draft welcome emails
* Create hiring manager summaries
* Identify missing compliance items
* Recommend role-based training modules
```
### Data Flow and Integrations: 

```
* Intake: Google Forms, Typeform
* Records: Google Sheets, Airtable, HRIS
* AI: OpenAI API or other LLMs
* Notifications: Slack, Email
* Scheduling: Google Calendar, Outlook
* Resources: Notion, Confluence
* Task Management: Jira, Trello, ClickUp
```
### Operational Benefits:

```
* Faster onboarding cycles
* Reduced manual coordination for HR and IT
* Improved data accuracy and completeness
* Personalized onboarding experience
* Stronger operational visibility
```

### Task 2: Implementation Demo
```
Demo Type:

* n8n workflow scaffold
* Python helper script simulating AI extraction (as shown in Task 1 prompt example)
* Workflow diagram screenshot included in starter/diagrams/

Files Included:

* starter/workflows/ → n8n workflow export JSON
* starter/code/ → Python helper script (extract_and_validate.py)
* starter/diagrams/ → Onboarding workflow diagram
* starter/screenshots/ → Demo screenshot showing workflow logic

Flow of Data:

1. New hire submission triggers workflow.
2. AI node extracts and validates structured data.
3. Tasks are automatically generated and routed to HR, IT, and manager systems.
4. Personalized onboarding plan is generated.
5. Milestone tracking and feedback collection update the onboarding record.

Pain Points Solved:

* Automates repetitive onboarding tasks
* Ensures complete and accurate data capture
* Reduces manual coordination across multiple teams
* Provides a personalized and consistent onboarding experience

Assumptions:

* Mock data is used for prototype demonstration
* External integrations (HRIS, email, Slack) are simulated
* Focus is on workflow clarity, AI application, and orchestration logic

Setup Instructions:

1. Import n8n workflow JSON into your n8n workspace.
2. Place Python helper script in the workflow directory and connect to AI nodes.
3. Review workflow diagram for reference.
4. Run workflow simulation using sample data provided in starter/data/.

Optional Notes:

* AI prompts are designed for structured JSON output compatible with automation tasks
* Workflow is modular and can be extended for enterprise HRIS integration
```

**Author**: Huzaifa Ahmed
