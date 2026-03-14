"""
onboarding_workflow.py
AI Onboarding Automation Prototype/Code 
Author: Huzaifa Ahmed
Purpose: Demonstrates workflow logic for AI Onboarding.
"""

import json


# New Hire Data Input
new_hire_input = {
    "full_name": "John Doe",
    "personal_email": "john.doe@gmail.com",
    "job_title": "Software Engineer",
    "department": "Engineering",
    "location": "Karachi",
    "manager_name": "Jane Smith",
    "employment_type": "Full-Time",
    "start_date": "2026-04-01",
    "uploaded_documents": ["ID.pdf", "OfferLetter.pdf"]
}


# Step 1: AI Extraction & Validation 
def extract_and_validate(data):
    """
    Simulates AI extraction of structured data from new hire inputs.
    Flags missing documents or fields.
    """
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


# Step 2: Task Generation 
def generate_onboarding_tasks(profile):
    """
    Automatically generates tasks for HR, IT, and Manager.
    """
    tasks = []
    if profile["missing_fields"] or profile["missing_documents"]:
        tasks.append("HR: Review missing information or documents")

    tasks.extend([
        "IT: Setup company email and access accounts",
        "HR: Assign required training modules",
        "Manager: Schedule orientation and intro sessions"
    ])
    return tasks


# Step 3: Personalized Onboarding Plan
def generate_onboarding_plan(profile):
    """
    Creates a personalized first-week plan.
    """
    plan = {
        "welcome_note": f"Welcome {profile['structured_data']['full_name']}!",
        "first_week_priorities": [
            "Complete HR documentation",
            "Set up your workstation",
            "Meet your team and manager",
            "Start role-specific training"
        ],
        "key_contacts": [profile['structured_data']['manager_name'], "HR Coordinator"],
        "recommended_training": ["Company Policies", "Engineering Onboarding Modules"]
    }
    return plan


# Step 4: Orchestration 
def run_onboarding_workflow(new_hire_input):
    extracted_profile = extract_and_validate(new_hire_input)
    tasks = generate_onboarding_tasks(extracted_profile)
    onboarding_plan = generate_onboarding_plan(extracted_profile)
    
    output = {
        "profile": extracted_profile,
        "tasks": tasks,
        "onboarding_plan": onboarding_plan
    }
    
    # Print output as JSON 
    print(json.dumps(output, indent=4))


# Execute Workflow
run_onboarding_workflow(new_hire_input)