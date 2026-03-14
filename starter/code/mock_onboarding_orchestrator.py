import json
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
from uuid import uuid4

REQUIRED_DOCS = {"government_id", "signed_offer", "policy_ack"}

TRAINING_MAP = {
    "engineering": ["Git Workflow", "CI/CD Basics", "Security Fundamentals"],
    "data science": ["Data Warehouse Orientation", "ML Platform Guide", "Data Governance"],
    "product": ["Product Lifecycle", "Analytics Dashboard", "Stakeholder Communication"],
    "design": ["Design System Walkthrough", "Figma Standards", "Accessibility Guidelines"],
    "default": ["Company Overview", "Communication Tools", "HR Policies"],
}


def mock_ai_extract(payload: dict) -> dict:
    """Simulate AI document extraction with confidence scoring."""
    emp = payload.get("employee", {})
    compliance = payload.get("compliance", {})
    received = set(compliance.get("required_docs_received", []))
    missing = sorted(REQUIRED_DOCS - received)

    name_parts = (emp.get("full_name") or "").split()
    confidence = 0.95 if len(name_parts) >= 2 and emp.get("start_date") else 0.72

    return {
        "employee": emp,
        "compliance": {
            "required_docs_received": sorted(received),
            "missing_docs": missing,
            "name_mismatch_detected": False,
            "signature_missing": "signed_offer" not in received,
        },
        "access_requirements": payload.get("access_requirements", {}),
        "confidence": {
            "employee_fields": confidence,
            "compliance_fields": 0.90 if not missing else 0.60,
            "overall": round(confidence * (0.90 if not missing else 0.60), 2),
        },
        "review_flags": (
            (["missing_required_documents"] if missing else [])
            + (["low_confidence_extraction"] if confidence < 0.85 else [])
        ),
    }


def classify_case(record: dict) -> dict:
    """Classify onboarding case for routing."""
    missing = record["compliance"].get("missing_docs", [])
    privileged = record.get("access_requirements", {}).get("privileged_access_requested", False)
    role = (record.get("employee", {}).get("job_title") or "").lower()
    senior_keywords = ["lead", "manager", "director", "head", "vp", "senior"]

    if missing:
        return {
            "case_type": "compliance-review",
            "reasons": [f"Missing documents: {', '.join(missing)}"],
            "required_human_review": True,
        }
    if privileged and any(k in role for k in senior_keywords):
        return {
            "case_type": "manager-review",
            "reasons": ["Privileged access requested for senior role"],
            "required_human_review": True,
        }
    return {
        "case_type": "standard",
        "reasons": ["All documents present, standard access"],
        "required_human_review": False,
    }


def build_tasks(record: dict, case_type: str) -> list[dict]:
    """Generate function-specific onboarding tasks with SLA dates."""
    start = date.fromisoformat(record["employee"]["start_date"])
    tasks = [
        {"team": "IT", "task": "Provision identity, SSO groups, and core tools",
         "due": str(start - timedelta(days=2)), "priority": "high"},
        {"team": "HR Ops", "task": "Validate payroll, tax profile, and benefits enrollment",
         "due": str(start - timedelta(days=3)), "priority": "high"},
        {"team": "Manager", "task": "Prepare first-week agenda, assign buddy, schedule intros",
         "due": str(start - timedelta(days=1)), "priority": "medium"},
        {"team": "Compliance", "task": "Assign mandatory training and jurisdiction attestations",
         "due": str(start + timedelta(days=3)),
         "priority": "medium" if case_type == "standard" else "high"},
    ]
    if case_type != "standard":
        tasks.append({
            "team": "HR", "task": f"Manual review required ({case_type})",
            "due": str(start - timedelta(days=4)), "priority": "critical",
        })
    return tasks


def generate_onboarding_plan(record: dict) -> dict:
    """Mock AI: generate a role-specific 5-day onboarding plan."""
    emp = record["employee"]
    dept = (emp.get("department") or "default").lower()
    training = TRAINING_MAP.get(dept, TRAINING_MAP["default"])
    name = emp.get("full_name", "New Hire").split()[0]

    return {
        "plan_title": f"Onboarding Plan for {emp['full_name']} — {emp.get('job_title', 'Role')}",
        "days": [
            {"day": "Day 1", "objectives": ["Complete HR orientation", "Set up workstation and accounts"],
             "meetings": ["Welcome call with manager", "IT setup session"],
             "tools_to_setup": (record.get("access_requirements", {}).get("systems_requested", []))[:3],
             "training": ["Company Overview"]},
            {"day": "Day 2", "objectives": ["Meet the team", "Review department goals"],
             "meetings": ["Team introduction", "Buddy sync"],
             "tools_to_setup": [], "training": [training[0]] if training else []},
            {"day": "Day 3", "objectives": ["Begin role-specific onboarding", "Access key resources"],
             "meetings": ["Manager 1:1"], "tools_to_setup": [],
             "training": [training[1]] if len(training) > 1 else []},
            {"day": "Day 4", "objectives": ["Deep-dive into current projects", "Review documentation"],
             "meetings": ["Cross-functional intro"], "tools_to_setup": [],
             "training": [training[2]] if len(training) > 2 else []},
            {"day": "Day 5", "objectives": ["Set 30-day goals with manager", "Complete week-1 feedback"],
             "meetings": ["Manager goal-setting session", "HR check-in"],
             "tools_to_setup": [], "training": []},
        ],
        "key_contacts": [emp.get("manager_name", "Manager"), "HR Business Partner", "IT Help Desk", "Assigned Buddy"],
        "success_criteria": [
            "All accounts provisioned and accessible",
            "Mandatory training modules started",
            f"{name} has met immediate team members",
            "30-day goals documented",
        ],
    }


def draft_welcome_email(record: dict) -> dict:
    """Mock AI: draft a welcome email for the new hire."""
    emp = record["employee"]
    name = emp.get("full_name", "New Hire").split()[0]
    start = emp.get("start_date", "TBD")
    manager = emp.get("manager_name", "your manager")
    dept = emp.get("department", "the team")

    return {
        "subject": f"Welcome to the team, {name}!",
        "body": (
            f"Hi {name},\n\n"
            f"We are excited to welcome you as {emp.get('job_title', 'a new team member')} "
            f"in {dept}. Your start date is {start}.\n\n"
            f"Before your first day, please ensure your documents are submitted and review "
            f"the onboarding checklist we will share shortly.\n\n"
            f"{manager} will reach out to schedule your first-week introductions. "
            f"If you have any questions before then, reply to this email or contact HR.\n\n"
            f"Looking forward to having you on board!\n\n"
            f"Best regards,\nHR Onboarding Team"
        ),
        "tone": "professional-friendly",
    }


def draft_manager_summary(record: dict, classification: dict, tasks: list[dict]) -> dict:
    """Mock AI: create a manager briefing summary."""
    emp = record["employee"]
    return {
        "subject": f"Onboarding Brief: {emp['full_name']} starting {emp['start_date']}",
        "summary": (
            f"{emp['full_name']} is joining as {emp.get('job_title')} in {emp.get('department')} "
            f"on {emp['start_date']}. Case classified as {classification['case_type']}."
        ),
        "action_items": [t["task"] for t in tasks if t["team"] == "Manager"],
        "open_risks": classification["reasons"] if classification["required_human_review"] else [],
    }


def build_milestones(start_date_str: str) -> list[dict]:
    """Schedule milestone check-ins."""
    start = date.fromisoformat(start_date_str)
    checkpoints = [
        ("D-7 Pre-boarding reminder", -7),
        ("D-1 Final readiness check", -1),
        ("Day 1 Welcome and orientation", 0),
        ("Day 3 Early check-in", 3),
        ("Day 7 Week-1 feedback survey", 7),
        ("Day 14 Two-week pulse check", 14),
        ("Day 30 Onboarding completion review", 30),
    ]
    return [{"milestone": label, "date": str(start + timedelta(days=offset))} for label, offset in checkpoints]


def create_audit_entry(run_id: str, record: dict, classification: dict) -> dict:
    """Create an audit log entry for the workflow run."""
    return {
        "workflow_run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "employee_id": record["employee"].get("work_email", "unknown"),
        "case_type": classification["case_type"],
        "human_review_required": classification["required_human_review"],
        "prompt_versions": {
            "extraction": "v1.0",
            "classification": "v1.0",
            "onboarding_plan": "v1.0",
            "welcome_email": "v1.0",
        },
        "model": "gpt-4o (mock)",
        "decision_path": classification["reasons"],
    }


def run_pipeline(payload: dict) -> dict:
    """Execute the full onboarding automation pipeline."""
    run_id = str(uuid4())[:8]

    # Phase B: AI extraction
    extracted = mock_ai_extract(payload)

    # Phase B: Classification
    classification = classify_case(extracted)

    # Phase C: Task routing
    tasks = build_tasks(extracted, classification["case_type"])

    # Phase D: AI-generated artifacts
    plan = generate_onboarding_plan(extracted)
    welcome = draft_welcome_email(extracted)
    manager_brief = draft_manager_summary(extracted, classification, tasks)

    # Phase E: Milestones
    milestones = build_milestones(extracted["employee"]["start_date"])

    # Audit
    audit = create_audit_entry(run_id, extracted, classification)

    return {
        "run_id": run_id,
        "employee": extracted["employee"],
        "extraction_confidence": extracted["confidence"],
        "review_flags": extracted["review_flags"],
        "classification": classification,
        "tasks": tasks,
        "onboarding_plan": plan,
        "welcome_email": welcome,
        "manager_summary": manager_brief,
        "milestones": milestones,
        "audit": audit,
    }


def main() -> None:
    sample_dir = Path(__file__).parent
    samples = sorted(sample_dir.glob("sample_*.json"))

    for sample_path in samples:
        print(f"\n{'='*70}")
        print(f"Processing: {sample_path.name}")
        print(f"{'='*70}")
        data = json.loads(sample_path.read_text(encoding="utf-8-sig"))
        result = run_pipeline(data)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
