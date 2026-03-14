"""
AI Document Extraction Helper
==============================
Utility script for processing onboarding documents using the OpenAI API.
Can be run standalone or called as a module from the n8n Code node.

Usage:
    python document_extractor.py --file path/to/document.pdf

Requirements:
    pip install openai pymupdf python-dotenv
"""

import os
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
    import fitz  # PyMuPDF for PDF text extraction
except ImportError:
    print("Install dependencies: pip install openai pymupdf python-dotenv")
    exit(1)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ─── Prompts ──────────────────────────────────────────────────────────────────

DOCUMENT_EXTRACTION_PROMPT = """
You are an HR document processing assistant operating inside an enterprise onboarding system.

You will receive the text content extracted from an employee onboarding document.

Your task is to extract the following fields and return them as valid JSON:
- full_name
- date_of_birth (ISO 8601 format, or null)
- document_type (one of: government_id, offer_letter, tax_form, bank_details, nda, certificate, policy_acknowledgement, unknown)
- document_number (if applicable, or null)
- expiry_date (ISO 8601 format, or null)
- issuing_authority (if applicable, or null)
- issues_found (list of strings describing any problems, inconsistencies, or missing fields)
- requires_manual_review (boolean)

Rules:
- If a field is not present in the document, return null for that field
- Do not guess or hallucinate values
- If uncertain about any field, set requires_manual_review to true and describe the issue in issues_found
- Return only valid JSON. No explanation text, no markdown fences.
""".strip()

ONBOARDING_PLAN_PROMPT = """
You are an onboarding experience designer. Your job is to create a personalized first-week onboarding plan for a new employee joining an enterprise organization.

Generate a structured first-week onboarding plan that includes:
1. A short welcome message (2-3 sentences, warm and professional)
2. Day 1 priorities (3-5 bullet points)
3. Key contacts to meet in the first week (list with role and suggested meeting format)
4. Required resources and tools to set up
5. Recommended learning or training for their role
6. One cultural or team integration suggestion

Format the output as clean Markdown suitable for a Notion page.
Keep the tone professional but human and approachable.
""".strip()


# ─── PDF Text Extraction ───────────────────────────────────────────────────────

def extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from a PDF file using PyMuPDF."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


# ─── AI Document Extraction ───────────────────────────────────────────────────

def extract_document_fields(document_text: str) -> dict:
    """
    Send document text to GPT-4o and extract structured onboarding fields.
    Returns a dict with extracted fields and metadata.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": DOCUMENT_EXTRACTION_PROMPT},
            {"role": "user", "content": f"Extract fields from this document:\n\n{document_text[:4000]}"}
        ],
        temperature=0.1,
        max_tokens=800
    )

    raw_content = response.choices[0].message.content.strip()

    try:
        extracted = json.loads(raw_content)
    except json.JSONDecodeError:
        # Fallback: flag for manual review if AI returns non-JSON
        extracted = {
            "full_name": None,
            "date_of_birth": None,
            "document_type": "unknown",
            "document_number": None,
            "expiry_date": None,
            "issuing_authority": None,
            "issues_found": ["AI returned non-JSON response — manual review required"],
            "requires_manual_review": True
        }

    # Add processing metadata
    extracted["processed_at"] = datetime.utcnow().isoformat()
    extracted["model_used"] = "gpt-4o"
    extracted["token_usage"] = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens
    }

    return extracted


# ─── Onboarding Plan Generation ───────────────────────────────────────────────

def generate_onboarding_plan(employee_profile: dict) -> str:
    """
    Generate a personalized first-week onboarding plan for a new hire.
    Returns Markdown-formatted plan.
    """
    profile_context = f"""
Employee profile:
- Name: {employee_profile.get('full_name', 'N/A')}
- Job Title: {employee_profile.get('job_title', 'N/A')}
- Department: {employee_profile.get('department', 'N/A')}
- Work Location: {employee_profile.get('location', 'N/A')}
- Employment Type: {employee_profile.get('employment_type', 'N/A')}
- Start Date: {employee_profile.get('start_date', 'N/A')}
- Reporting Manager: {employee_profile.get('manager_name', 'N/A')}
""".strip()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": ONBOARDING_PLAN_PROMPT},
            {"role": "user", "content": profile_context}
        ],
        temperature=0.7,
        max_tokens=1200
    )

    return response.choices[0].message.content.strip()


# ─── Validation Helper ────────────────────────────────────────────────────────

def validate_onboarding_record(record: dict) -> dict:
    """
    Validate a new hire record for required fields.
    Returns validation result with list of missing fields.
    """
    required_fields = [
        "full_name", "email", "job_title", "department",
        "start_date", "manager_name", "location", "employment_type"
    ]

    missing = [f for f in required_fields if not record.get(f)]

    return {
        "is_valid": len(missing) == 0,
        "missing_fields": missing,
        "validated_at": datetime.utcnow().isoformat()
    }


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI Onboarding Document Extractor")
    parser.add_argument("--file", help="Path to PDF document to extract", required=False)
    parser.add_argument("--plan", help="Generate onboarding plan from JSON profile file", required=False)
    args = parser.parse_args()

    if args.file:
        print(f"\n📄 Extracting fields from: {args.file}")
        text = extract_text_from_pdf(args.file)
        result = extract_document_fields(text)
        print("\n✅ Extraction result:")
        print(json.dumps(result, indent=2))

        if result.get("requires_manual_review"):
            print("\n⚠️  This document requires manual HR review.")
        else:
            print("\n✅ Document passed automated review.")

    elif args.plan:
        with open(args.plan, "r") as f:
            profile = json.load(f)
        print(f"\n📋 Generating onboarding plan for: {profile.get('full_name')}")
        plan = generate_onboarding_plan(profile)
        print("\n" + plan)

    else:
        # Demo mode with mock data
        print("\n🚀 Running in demo mode with mock data...\n")

        mock_record = {
            "full_name": "Dileep Singh",
            "email": "dileep@example.com",
            "job_title": "Data Scientist",
            "department": "Analytics",
            "start_date": "2026-04-01",
            "manager_name": "Sarah Johnson",
            "location": "Remote",
            "employment_type": "Full-time"
        }

        validation = validate_onboarding_record(mock_record)
        print("📋 Validation result:")
        print(json.dumps(validation, indent=2))

        if validation["is_valid"]:
            print("\n📝 Generating onboarding plan...")
            plan = generate_onboarding_plan(mock_record)
            print("\n" + plan)


if __name__ == "__main__":
    main()
