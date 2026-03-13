"""
Accepts a mock new hire JSON payload, constructs the Phase 2 extraction
prompt, calls the Anthropic Claude API, and returns a structured
OnboardingRecord JSON object.

Usage
-----
    python onboarding_scaffold.py
    python onboarding_scaffold.py --input sample_input.json
    python onboarding_scaffold.py --input sample_input.json --output result.json

Dependencies
------------
    pip install anthropic

Environment variables
---------------------
    ANTHROPIC_API_KEY   — your Anthropic API key (required)
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone

import anthropic

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2048

# ---------------------------------------------------------------------------
# Phase 2 — Prompt 1: Document Field Extraction (system prompt)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an onboarding data extraction assistant for an enterprise HR operations team.
Your sole responsibility is to read raw hire documents and extract structured employee
data accurately and consistently. You do not interpret, infer, or guess. You extract
only what is explicitly stated in the source text.

TASK:
Extract all available employee onboarding fields from the raw document text provided
below. Map each piece of information to the correct field in the output schema.

INPUT FORMAT:
The input will be raw text extracted from one or more of the following document types:
- Offer letter (signed or unsigned)
- ATS (Applicant Tracking System) export
- HR intake form submission
- Employment contract cover sheet

The text may be unstructured, inconsistently formatted, or contain extraneous content
such as legal boilerplate, page numbers, or repeated headers. Extract only data
relevant to the output schema.

OUTPUT FORMAT:
Return a single valid JSON object. Do not include any explanation, commentary,
or markdown formatting outside the JSON block. The JSON must conform exactly
to the following schema:

{
  "extraction_status": "complete" | "partial" | "failed",
  "employee": {
    "full_name": string | null,
    "preferred_name": string | null,
    "personal_email": string | null,
    "phone_number": string | null
  },
  "employment": {
    "job_title": string | null,
    "department": string | null,
    "employment_type": "full_time" | "part_time" | "contractor" | "intern" | null,
    "start_date": "YYYY-MM-DD" | null,
    "end_date": "YYYY-MM-DD" | null,
    "work_location": string | null,
    "remote_status": "on_site" | "hybrid" | "remote" | null,
    "reporting_manager": string | null,
    "cost_centre": string | null,
    "salary_currency": string | null,
    "salary_amount": number | null,
    "salary_frequency": "annual" | "monthly" | "hourly" | null
  },
  "documents_present": [string],
  "extraction_notes": [string]
}

FIELD RULES:
- All dates must be normalised to ISO 8601 format (YYYY-MM-DD).
- employment_type must be classified from context if not stated verbatim
  (e.g. "fixed-term contract" -> "contractor", "graduate scheme" -> "intern").
- salary_currency must use ISO 4217 currency codes (e.g. USD, GBP, EUR).
- documents_present must list each source document type identified in the input.
- extraction_notes must log any ambiguities, conflicting values, or inferences made.

FALLBACK INSTRUCTIONS:
- If a field cannot be found or reliably inferred, set its value to null.
  Do not guess or fabricate values.
- If the document is unreadable, empty, or entirely irrelevant, set
  extraction_status to "failed" and populate extraction_notes with the reason.
- If some fields are found but others are missing, set extraction_status to "partial".
- If all required fields are populated, set extraction_status to "complete".
- Required fields for "complete" status: full_name, job_title, department,
  employment_type, start_date."""


# ---------------------------------------------------------------------------
# Step 1 — Flatten structured hire payload to readable prose
# ---------------------------------------------------------------------------

def flatten_hire_payload_to_text(payload: dict) -> str:
    """
    Convert a structured hire JSON payload into readable plain-text prose.

    This mirrors what production does when real documents (offer letters,
    ATS exports) arrive as unstructured text — meaning the same extraction
    prompt works for both structured form submissions and raw documents
    without any format-specific branching.
    """
    lines = [
        "=== HR INTAKE FORM SUBMISSION ===",
        f"Submission date: {datetime.now(timezone.utc).date().isoformat()}",
        "",
    ]

    if personal := payload.get("personal"):
        lines.append("--- Personal Details ---")
        if v := personal.get("full_name"):    lines.append(f"Full name: {v}")
        if v := personal.get("preferred_name"): lines.append(f"Preferred name: {v}")
        if v := personal.get("email"):        lines.append(f"Personal email: {v}")
        if v := personal.get("phone"):        lines.append(f"Phone: {v}")
        lines.append("")

    if role := payload.get("role"):
        lines.append("--- Role Information ---")
        if v := role.get("title"):         lines.append(f"Job title: {v}")
        if v := role.get("department"):    lines.append(f"Department: {v}")
        if v := role.get("type"):          lines.append(f"Employment type: {v}")
        if v := role.get("start_date"):    lines.append(f"Start date: {v}")
        if v := role.get("end_date"):      lines.append(f"Contract end date: {v}")
        if v := role.get("manager"):       lines.append(f"Reporting manager: {v}")
        if v := role.get("cost_centre"):   lines.append(f"Cost centre: {v}")
        if v := role.get("location"):      lines.append(f"Work location: {v}")
        if v := role.get("remote_status"): lines.append(f"Work arrangement: {v}")
        lines.append("")

    if comp := payload.get("compensation"):
        lines.append("--- Compensation ---")
        currency = comp.get("currency", "")
        amount   = comp.get("amount", "")
        freq     = comp.get("frequency", "year")
        if currency and amount:
            lines.append(f"Salary: {currency} {amount} per {freq}")
        lines.append("")

    if docs := payload.get("documents_submitted"):
        lines.append("--- Documents Submitted ---")
        for doc in docs:
            lines.append(f"- {doc}")
        lines.append("")

    if notes := payload.get("notes"):
        lines.append("--- Additional Notes ---")
        lines.append(notes)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Step 2 — Call Claude API
# ---------------------------------------------------------------------------

def call_claude_extraction(document_text: str, client: anthropic.Anthropic) -> dict:
    """
    Send the flattened document text to Claude using the Phase 2 extraction
    system prompt. Parse and return the JSON extraction result.
    """
    print("\n🤖  Calling Claude API for extraction...")

    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"INPUT DOCUMENT TEXT:\n{document_text}",
            }
        ],
    )

    raw_response = message.content[0].text

    # Strip markdown fences if Claude wraps output despite instructions
    clean = raw_response.strip()
    if clean.startswith("```"):
        clean = "\n".join(clean.split("\n")[1:])
    if clean.endswith("```"):
        clean = "\n".join(clean.split("\n")[:-1])

    try:
        return json.loads(clean)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Claude response was not valid JSON.\n"
            f"Raw response:\n{raw_response}"
        ) from exc


# ---------------------------------------------------------------------------
# Step 3 — Wrap extraction result in full OnboardingRecord schema
# ---------------------------------------------------------------------------

def build_onboarding_record(hire_payload: dict, extracted: dict) -> dict:
    """
    Wrap the AI extraction result in the canonical OnboardingRecord schema
    (Phase 3 JSON schema). Adds record_id, meta, and pipeline_status.
    All downstream fields are initialised to null — they will be populated
    by subsequent pipeline stages.
    """
    year = datetime.now(timezone.utc).year
    record_id = f"ONB-{year}-{random.randint(1000, 9999)}"
    now = datetime.now(timezone.utc).isoformat()

    stage_pending = {"status": "pending", "started_at": None, "completed_at": None, "error_ref": None}
    intake_status = "failed" if extracted.get("extraction_status") == "failed" else "complete"

    return {
        "record_id": record_id,
        "meta": {
            "created_at": now,
            "updated_at": now,
            "source_system": hire_payload.get("_source", "google_forms"),
            "schema_version": "1.0.0",
            "assigned_hr_contact": None,
        },
        "pipeline_status": {
            "current_stage": "blocked" if intake_status == "failed" else "intake",
            "stages": {
                "intake": {
                    "status": intake_status,
                    "started_at": now,
                    "completed_at": now,
                    "error_ref": None,
                },
                "validation":       {**stage_pending},
                "profile_creation": {**stage_pending},
                "task_routing":     {**stage_pending},
                "plan_generation":  {**stage_pending},
                "communication":    {**stage_pending},
                "tracking":         {**stage_pending},
            },
        },
        "extracted":         extracted,
        "validation_result": None,
        "provisioning":      None,
        "onboarding_plan":   None,
        "communications":    None,
        "tracking":          None,
        "error_log":         [],
    }


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Onboarding AI Extraction Helper — Phase 4 Prototype Scaffold"
    )
    parser.add_argument(
        "--input",
        default="sample_input.json",
        help="Path to the mock hire JSON payload (default: sample_input.json)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to write the enriched OnboardingRecord JSON",
    )
    args = parser.parse_args()

    # ── Validate environment ────────────────────────────────────────────────
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌  Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("    Export it with: export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    # ── Load input payload ──────────────────────────────────────────────────
    print(f"\n🚀  Onboarding AI Extraction Helper")
    print(f"    Input:  {os.path.abspath(args.input)}")
    print(f"    Model:  {MODEL}")

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            hire_payload = json.load(f)
        name = hire_payload.get("personal", {}).get("full_name", "Unknown")
        print(f"✅  Payload loaded. Hire: {name}")
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"❌  Failed to read input file '{args.input}': {exc}")
        sys.exit(1)

    # ── Flatten to document text ────────────────────────────────────────────
    document_text = flatten_hire_payload_to_text(hire_payload)
    print("\n📄  Flattened document text sent to Claude:\n")
    print("─" * 60)
    print(document_text)
    print("─" * 60)

    # ── Call Claude ─────────────────────────────────────────────────────────
    client = anthropic.Anthropic(api_key=api_key)

    try:
        extracted = call_claude_extraction(document_text, client)
        print("✅  Response received and parsed.\n")
    except (anthropic.APIError, ValueError) as exc:
        print(f"❌  Extraction failed: {exc}")
        sys.exit(1)

    # ── Build full OnboardingRecord ─────────────────────────────────────────
    record = build_onboarding_record(hire_payload, extracted)

    output_json = json.dumps(record, indent=2, ensure_ascii=False)
    print("\n🎯  Enriched OnboardingRecord:\n")
    print("─" * 60)
    print(output_json)
    print("─" * 60)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"\n💾  Output written to: {os.path.abspath(args.output)}")

    # ── Status summary ──────────────────────────────────────────────────────
    status = extracted.get("extraction_status", "unknown").upper()
    print(f"\n✅  Extraction complete. Status: {status}")

    if status == "PARTIAL":
        print("⚠️   Some fields are missing. Review extraction_notes for details.")
        for note in extracted.get("extraction_notes", []):
            print(f"     • {note}")
    elif status == "FAILED":
        print("🚨  Extraction failed. Human review required before proceeding.")


if __name__ == "__main__":
    main()
