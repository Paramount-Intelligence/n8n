"""
AI Onboarding Automation — Python Scaffold
==========================================
This script simulates the core onboarding automation workflow.
It demonstrates how data moves through each stage: intake, AI extraction,
task generation, onboarding plan creation, and communication dispatch.

Requirements:
    pip install openai requests python-dotenv

Setup:
    Create a .env file with:
        OPENAI_API_KEY=your_key_here

Usage:
    python onboarding_automation.py
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

# In production this would be: from openai import OpenAI
# For demo purposes we mock the OpenAI responses below.

load_dotenv()

# ---------------------------------------------------------------------------
# Mock Data — simulates a new hire form submission
# ---------------------------------------------------------------------------

MOCK_NEW_HIRE_SUBMISSION = {
    "full_name": "Danish kumar",
    "personal_email": "danish_kumar@gmail.com",
    "job_title": "Ai intern",
    "department": "AL/ML",
    "team": "Growth",
    "manager_name": "Alex john",
    "manager_email": "alex.johnson@company.com",
    "location": "Onsite - Pakistan",
    "employment_type": "full-time",
    "start_date": "2026-04-11",
    "documents_uploaded": ["offer_letter.pdf", "nda_signed.pdf", "id_proof.pdf"],
}

# ---------------------------------------------------------------------------
# Stage 1 — Intake Trigger
# ---------------------------------------------------------------------------

def stage_1_intake(submission: dict) -> dict:
    """Simulate receiving a new hire form submission."""
    print("\n" + "="*60)
    print("STAGE 1 — INTAKE TRIGGER")
    print("="*60)
    
    record = {
        **submission,
        "employee_id": str(uuid.uuid4()),
        "status": "INTAKE_RECEIVED",
        "created_at": datetime.utcnow().isoformat(),
    }
    
    print(f"✅ New hire record created: {record['employee_id']}")
    print(f"   Name:       {record['full_name']}")
    print(f"   Role:       {record['job_title']}")
    print(f"   Start Date: {record['start_date']}")
    print(f"   Documents:  {', '.join(record['documents_uploaded'])}")
    
    return record


# ---------------------------------------------------------------------------
# Stage 2 — AI Document Extraction (mocked)
# ---------------------------------------------------------------------------

EXTRACTION_PROMPT = """
You are an HR onboarding assistant. Given an employee submission record and list of uploaded documents, extract and validate the following fields:

- full_name
- personal_email
- job_title
- department
- start_date
- manager_name
- employment_type
- signed_documents (list)
- missing_documents (list — expected: offer_letter, nda_signed, id_proof)
- issues (list of any problems, or empty list if none)

Return ONLY valid JSON.
"""

def call_ai_extraction(record: dict) -> dict:
    """
    In production: call OpenAI API with the prompt above.
    Here we return a realistic mocked response.
    """
    # --- PRODUCTION CODE (commented out) ---
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {"role": "system", "content": EXTRACTION_PROMPT},
    #         {"role": "user", "content": json.dumps(record)}
    #     ],
    #     response_format={"type": "json_object"}
    # )
    # return json.loads(response.choices[0].message.content)

    # --- MOCK RESPONSE ---
    return {
        "full_name": record["full_name"],
        "personal_email": record["personal_email"],
        "job_title": record["job_title"],
        "department": record["department"],
        "start_date": record["start_date"],
        "manager_name": record["manager_name"],
        "employment_type": record["employment_type"],
        "signed_documents": record["documents_uploaded"],
        "missing_documents": [],
        "issues": [],
    }


def stage_2_ai_extraction(record: dict) -> dict:
    """Run AI extraction and validate the result."""
    print("\n" + "="*60)
    print("STAGE 2 — AI DOCUMENT EXTRACTION")
    print("="*60)

    extracted = call_ai_extraction(record)

    # Validate: flag record if required fields are missing
    required_docs = {"offer_letter.pdf", "nda_signed.pdf", "id_proof.pdf"}
    uploaded_docs = set(record.get("documents_uploaded", []))
    missing = list(required_docs - uploaded_docs)

    if missing or extracted.get("issues"):
        record["status"] = "NEEDS_REVIEW"
        record["flags"] = {
            "missing_documents": missing,
            "issues": extracted.get("issues", []),
        }
        print(f"⚠️  Record flagged for HR review.")
        print(f"   Missing documents: {missing or 'None'}")
        print(f"   Issues: {extracted.get('issues') or 'None'}")
    else:
        record["status"] = "EXTRACTION_COMPLETE"
        record["extracted_data"] = extracted
        print(f"✅ Extraction complete. All documents verified.")
        print(f"   Signed docs: {', '.join(extracted['signed_documents'])}")
        print(f"   Missing:     None")
        print(f"   Issues:      None")

    return record


# ---------------------------------------------------------------------------
# Stage 3 — Onboarding Profile Creation
# ---------------------------------------------------------------------------

def stage_3_build_profile(record: dict) -> dict:
    """Merge extracted data with metadata to build the full onboarding profile."""
    print("\n" + "="*60)
    print("STAGE 3 — ONBOARDING PROFILE CREATION")
    print("="*60)

    start = datetime.strptime(record["start_date"], "%Y-%m-%d")
    
    profile = {
        "employee_id": record["employee_id"],
        "full_name": record["full_name"],
        "personal_email": record["personal_email"],
        "company_email": f"{record['full_name'].lower().replace(' ', '.')}"
                         f"@company.com",
        "role": record["job_title"],
        "department": record["department"],
        "team": record.get("team", ""),
        "manager": record["manager_name"],
        "manager_email": record.get("manager_email", ""),
        "location": record["location"],
        "employment_type": record["employment_type"],
        "start_date": record["start_date"],
        "onboarding_track": f"{record['department'].lower()}_"
                            f"{'senior' if 'Senior' in record['job_title'] else 'standard'}",
        "status": "ONBOARDING_IN_PROGRESS",
        "milestones": {
            "day_1": (start + timedelta(days=0)).strftime("%Y-%m-%d"),
            "day_7": (start + timedelta(days=7)).strftime("%Y-%m-%d"),
            "day_30": (start + timedelta(days=30)).strftime("%Y-%m-%d"),
            "day_90": (start + timedelta(days=90)).strftime("%Y-%m-%d"),
        },
        "created_at": record["created_at"],
    }

    print(f"✅ Onboarding profile built.")
    print(f"   Company email: {profile['company_email']}")
    print(f"   Track:         {profile['onboarding_track']}")
    print(f"   Milestones:    Day 1→{profile['milestones']['day_1']} | "
          f"Day 30→{profile['milestones']['day_30']}")

    return profile


# ---------------------------------------------------------------------------
# Stage 4 — Task Generation (AI-powered)
# ---------------------------------------------------------------------------

TASK_GENERATION_PROMPT = """
You are an onboarding operations coordinator. Based on the employee profile,
generate a task list covering HR, IT, manager, and compliance actions.

For each task include: task_name, assigned_to, due_offset (days relative to start_date),
priority (high/medium/low), and depends_on (list of task names or empty).

Return ONLY a JSON array.
"""

def call_ai_task_generation(profile: dict) -> list:
    """
    In production: call OpenAI API.
    Here we return a realistic mocked task list.
    """
    return [
        {
            "task_name": "Provision company laptop",
            "assigned_to": "IT",
            "due_offset": -5,
            "priority": "high",
            "depends_on": [],
        },
        {
            "task_name": "Set up company email account",
            "assigned_to": "IT",
            "due_offset": -3,
            "priority": "high",
            "depends_on": ["Provision company laptop"],
        },
        {
            "task_name": "Grant Slack, Jira, Figma access",
            "assigned_to": "IT",
            "due_offset": -2,
            "priority": "high",
            "depends_on": ["Set up company email account"],
        },
        {
            "task_name": "Complete payroll and benefits enrollment",
            "assigned_to": "HR",
            "due_offset": -3,
            "priority": "high",
            "depends_on": [],
        },
        {
            "task_name": "Assign compliance training modules",
            "assigned_to": "HR",
            "due_offset": 1,
            "priority": "medium",
            "depends_on": [],
        },
        {
            "task_name": "Schedule Day 1 welcome call",
            "assigned_to": "Manager",
            "due_offset": -2,
            "priority": "high",
            "depends_on": [],
        },
        {
            "task_name": "Send team introduction email",
            "assigned_to": "Manager",
            "due_offset": 0,
            "priority": "medium",
            "depends_on": [],
        },
        {
            "task_name": "Complete security awareness training",
            "assigned_to": "New Hire",
            "due_offset": 7,
            "priority": "high",
            "depends_on": ["Grant Slack, Jira, Figma access"],
        },
    ]


def stage_4_task_generation(profile: dict) -> list:
    """Generate and display onboarding tasks."""
    print("\n" + "="*60)
    print("STAGE 4 — TASK GENERATION AND ROUTING")
    print("="*60)

    tasks = call_ai_task_generation(profile)
    start = datetime.strptime(profile["start_date"], "%Y-%m-%d")

    print(f"✅ {len(tasks)} tasks generated:\n")
    print(f"  {'Task':<45} {'Owner':<12} {'Due Date':<12} {'Priority'}")
    print(f"  {'-'*45} {'-'*12} {'-'*12} {'-'*8}")

    for task in tasks:
        due = (start + timedelta(days=task["due_offset"])).strftime("%Y-%m-%d")
        print(f"  {task['task_name']:<45} {task['assigned_to']:<12} {due:<12} {task['priority']}")

    return tasks


# ---------------------------------------------------------------------------
# Stage 5 — Onboarding Plan Generation (AI-powered)
# ---------------------------------------------------------------------------

ONBOARDING_PLAN_PROMPT = """
You are a friendly onboarding guide. Write a personalized first-week onboarding 
plan for the new hire. Include: warm welcome, Day 1 logistics, first-week priorities,
key contacts, recommended tools to explore, and compliance items.
Keep it warm, clear, and encouraging.
"""

def call_ai_onboarding_plan(profile: dict) -> str:
    """
    In production: call OpenAI API.
    Here we return a realistic mocked plan.
    """
    return f"""
# Welcome to the Team, {profile['full_name']}! 🎉

We're thrilled to have you joining us as **{profile['role']}** in the **{profile['department']}** team.
Your start date is **{profile['start_date']}** and your manager will be **{profile['manager']}**.

---

## Day 1 — What to Expect

- Your company laptop will be ready and shipped/available before you start.
- You'll receive login credentials for your company email ({profile['company_email']}) on Day 1.
- Your manager {profile['manager']} will reach out to schedule a welcome call — look out for that!
- Join the **#team-{profile['department'].lower()}** and **#general** Slack channels to say hello.

---

## First Week Priorities

1. **Get set up** — Confirm access to all tools: Slack, Jira, Figma, Google Workspace.
2. **Meet the team** — Attend your team intro meeting arranged by {profile['manager']}.
3. **Review resources** — Read through the team wiki, product docs, and design guidelines.
4. **Complete compliance training** — Security awareness and data privacy modules (due Day 7).
5. **1:1 with your manager** — Discuss your 30/60/90 day goals and immediate priorities.

---

## Key Contacts

| Name | Role | How to Reach |
|---|---|---|
| {profile['manager']} | Your Manager | Slack / Email |
| HR Team | Payroll, Benefits, Policies | hr@company.com |
| IT Helpdesk | Access, Laptop, Tools | it-help@company.com |

---

## Recommended Tools to Explore This Week

- **Notion** — Team documentation and onboarding resources
- **Figma** — Design collaboration (your primary tool)
- **Jira** — Project and sprint tracking
- **Slack** — Team communication

---

## Required Compliance Items (Complete by Day 14)

- [ ] Security Awareness Training (assigned in TalentLMS)
- [ ] Data Privacy Policy Acknowledgement
- [ ] Code of Conduct sign-off

---

## Your 30-Day Check-In

At the end of your first month, you'll have a formal check-in with {profile['manager']}
to review your onboarding experience, discuss initial projects, and align on priorities
for your next 60 days. You'll also receive a short feedback survey from HR — your input
helps us keep improving the onboarding experience for everyone.

We're so glad you're here. Don't hesitate to ask questions — no question is too small!

*— The People & Operations Team*
"""


def stage_5_onboarding_plan(profile: dict) -> str:
    """Generate and display the personalized onboarding plan."""
    print("\n" + "="*60)
    print("STAGE 5 — PERSONALIZED ONBOARDING PLAN")
    print("="*60)

    plan = call_ai_onboarding_plan(profile)
    print(plan)
    return plan


# ---------------------------------------------------------------------------
# Stage 6 — Communication Dispatch
# ---------------------------------------------------------------------------

def stage_6_communications(profile: dict) -> dict:
    """Generate and simulate sending all onboarding communications."""
    print("\n" + "="*60)
    print("STAGE 6 — COMMUNICATION DISPATCH")
    print("="*60)

    communications = {
        "welcome_email": {
            "to": profile["personal_email"],
            "subject": f"Welcome to the team, {profile['full_name'].split()[0]}! 🎉",
            "body": (
                f"Hi {profile['full_name'].split()[0]},\n\n"
                f"We're so excited to have you join us as {profile['role']} "
                f"in the {profile['department']} team on {profile['start_date']}.\n\n"
                f"Your manager {profile['manager']} will be in touch soon to welcome you "
                f"and share everything you need for Day 1. Your full onboarding plan "
                f"is attached to this email.\n\n"
                f"See you soon!\n— The People Team"
            ),
            "status": "SENT",
        },
        "manager_briefing": {
            "to": profile["manager_email"],
            "subject": f"New hire starting {profile['start_date']}: {profile['full_name']}",
            "body": (
                f"Hi {profile['manager']},\n\n"
                f"{profile['full_name']} is joining your team as {profile['role']} "
                f"on {profile['start_date']}. All documents have been verified.\n\n"
                f"Pending IT tasks: laptop provisioning, email setup, tool access.\n"
                f"Action needed from you: please schedule a Day 1 welcome call "
                f"and a team introduction by the end of their first week.\n\n"
                f"— HR Operations"
            ),
            "status": "SENT",
        },
        "it_ticket": {
            "system": "Jira",
            "project": "IT-ONBOARDING",
            "summary": f"Onboard new hire: {profile['full_name']} ({profile['role']})",
            "description": (
                f"New hire starting {profile['start_date']}.\n"
                f"Required: MacBook Pro, Slack, Jira, Figma, Google Workspace.\n"
                f"Laptop must be ready 3 business days before start date."
            ),
            "priority": "High",
            "status": "CREATED",
        },
    }

    for key, comm in communications.items():
        if key == "it_ticket":
            print(f"✅ IT ticket created in {comm['system']}: {comm['summary']}")
        else:
            print(f"✅ Email sent to {comm['to']}: {comm['subject']}")

    return communications


# ---------------------------------------------------------------------------
# Stage 7 — Milestone Scheduling
# ---------------------------------------------------------------------------

def stage_7_milestone_scheduling(profile: dict) -> None:
    """Schedule milestone check-ins and feedback triggers."""
    print("\n" + "="*60)
    print("STAGE 7 — MILESTONE SCHEDULING")
    print("="*60)

    milestones = profile["milestones"]
    print("✅ Scheduled milestone triggers:\n")
    print(f"  Day 1  ({milestones['day_1']})  → Access confirmation check + Slack welcome")
    print(f"  Day 7  ({milestones['day_7']})  → First week check-in email to new hire + manager")
    print(f"  Day 30 ({milestones['day_30']}) → Onboarding feedback survey (Typeform)")
    print(f"  Day 90 ({milestones['day_90']}) → Final onboarding close-out + HR review")
    print()
    print("  (In production: each trigger is a scheduled n8n node or cron job)")


# ---------------------------------------------------------------------------
# Main — Run the full workflow
# ---------------------------------------------------------------------------

def run_onboarding_workflow(submission: dict) -> None:
    """Execute the complete onboarding automation workflow end to end."""
    print("\n" + "█"*60)
    print("  AI ONBOARDING AUTOMATION — WORKFLOW EXECUTION")
    print("█"*60)

    # Run each stage in sequence
    record = stage_1_intake(submission)
    record = stage_2_ai_extraction(record)

    # Stop if record needs human review
    if record.get("status") == "NEEDS_REVIEW":
        print("\n⛔ Workflow paused — record requires HR review before continuing.")
        print(f"   Flags: {record.get('flags')}")
        return

    profile = stage_3_build_profile(record)
    tasks   = stage_4_task_generation(profile)
    plan    = stage_5_onboarding_plan(profile)
    comms   = stage_6_communications(profile)
    stage_7_milestone_scheduling(profile)

    print("\n" + "="*60)
    print("WORKFLOW COMPLETE")
    print("="*60)
    print(f"✅ {profile['full_name']} onboarding initiated successfully.")
    print(f"   Employee ID:   {profile['employee_id']}")
    print(f"   Status:        {profile['status']}")
    print(f"   Tasks created: {len(tasks)}")
    print(f"   Emails sent:   2 (new hire + manager)")
    print(f"   IT tickets:    1")
    print(f"   Plan stored:   Notion / Google Drive")
    print()


if __name__ == "__main__":
    run_onboarding_workflow(MOCK_NEW_HIRE_SUBMISSION)
