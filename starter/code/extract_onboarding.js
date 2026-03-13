/*
 * Accepts a mock new hire JSON payload, constructs the Phase 2 extraction
 * prompt, calls the Claude API (Anthropic), and returns a structured
 * OnboardingRecord JSON object.
 *
 * Usage:
 *   node extract_onboarding.js
 *   node extract_onboarding.js --input ./sample_input.json
 *   node extract_onboarding.js --input ./sample_input.json --output ./result.json
 *
 * Dependencies:
 *   npm install @anthropic-ai/sdk
 *
 * Environment variables:
 *   ANTHROPIC_API_KEY   — your Anthropic API key (required)
*/

import Anthropic from "@anthropic-ai/sdk";
import { readFileSync, writeFileSync } from "fs";
import { resolve } from "path";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const MODEL = "claude-sonnet-4-20250514";
const MAX_TOKENS = 2048;
const DEFAULT_INPUT_PATH = "./sample_input.json";

// ---------------------------------------------------------------------------
// Phase 2 Extraction Prompt (Prompt 1 — Document Field Extraction)
// ---------------------------------------------------------------------------

const SYSTEM_PROMPT = `You are an onboarding data extraction assistant for an enterprise HR operations team.
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
- If some fields are found but others are missing, set extraction_status
  to "partial".
- If all required fields are populated, set extraction_status to "complete".
- Required fields for "complete" status: full_name, job_title, department,
  employment_type, start_date.`;

// ---------------------------------------------------------------------------
// Utility: flatten a mock hire JSON payload into a readable document string
// ---------------------------------------------------------------------------

function flattenHirePayloadToText(payload) {
  const lines = [];

  lines.push("=== HR INTAKE FORM SUBMISSION ===");
  lines.push(`Submission date: ${new Date().toISOString().split("T")[0]}`);
  lines.push("");

  if (payload.personal) {
    lines.push("--- Personal Details ---");
    const p = payload.personal;
    if (p.full_name) lines.push(`Full name: ${p.full_name}`);
    if (p.preferred_name) lines.push(`Preferred name: ${p.preferred_name}`);
    if (p.email) lines.push(`Personal email: ${p.email}`);
    if (p.phone) lines.push(`Phone: ${p.phone}`);
    lines.push("");
  }

  if (payload.role) {
    lines.push("--- Role Information ---");
    const r = payload.role;
    if (r.title) lines.push(`Job title: ${r.title}`);
    if (r.department) lines.push(`Department: ${r.department}`);
    if (r.type) lines.push(`Employment type: ${r.type}`);
    if (r.start_date) lines.push(`Start date: ${r.start_date}`);
    if (r.end_date) lines.push(`Contract end date: ${r.end_date}`);
    if (r.manager) lines.push(`Reporting manager: ${r.manager}`);
    if (r.cost_centre) lines.push(`Cost centre: ${r.cost_centre}`);
    if (r.location) lines.push(`Work location: ${r.location}`);
    if (r.remote_status) lines.push(`Work arrangement: ${r.remote_status}`);
    lines.push("");
  }

  if (payload.compensation) {
    lines.push("--- Compensation ---");
    const c = payload.compensation;
    if (c.currency && c.amount) {
      lines.push(`Salary: ${c.currency} ${c.amount} per ${c.frequency || "year"}`);
    }
    lines.push("");
  }

  if (payload.documents_submitted && payload.documents_submitted.length > 0) {
    lines.push("--- Documents Submitted ---");
    payload.documents_submitted.forEach((doc) => lines.push(`- ${doc}`));
    lines.push("");
  }

  if (payload.notes) {
    lines.push("--- Additional Notes ---");
    lines.push(payload.notes);
  }

  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// Core: call Claude API with the extraction prompt
// ---------------------------------------------------------------------------

async function extractOnboardingRecord(hirePayload) {
  const client = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY,
  });

  const documentText = flattenHirePayloadToText(hirePayload);

  console.log("\n📄 Flattened document text sent to Claude:\n");
  console.log("─".repeat(60));
  console.log(documentText);
  console.log("─".repeat(60));

  console.log("\n🤖 Calling Claude API for extraction...\n");

  const message = await client.messages.create({
    model: MODEL,
    max_tokens: MAX_TOKENS,
    system: SYSTEM_PROMPT,
    messages: [
      {
        role: "user",
        content: `INPUT DOCUMENT TEXT:\n${documentText}`,
      },
    ],
  });

  const rawResponse = message.content[0].text;

  console.log("✅ Claude response received. Parsing JSON...\n");

  let extractedRecord;
  try {
    const jsonMatch = rawResponse.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error("No JSON object found in Claude response");
    }
    extractedRecord = JSON.parse(jsonMatch[0]);
  } catch (parseError) {
    console.error("❌ Failed to parse Claude response as JSON:", parseError.message);
    console.error("Raw response was:", rawResponse);
    throw parseError;
  }

  return {
    record_id: `ONB-${new Date().getFullYear()}-${String(Math.floor(Math.random() * 9000) + 1000)}`,
    meta: {
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      source_system: hirePayload._source || "google_forms",
      schema_version: "1.0.0",
      assigned_hr_contact: null,
    },
    pipeline_status: {
      current_stage: extractedRecord.extraction_status === "failed" ? "blocked" : "intake",
      stages: {
        intake: {
          status: extractedRecord.extraction_status === "failed" ? "failed" : "complete",
          started_at: new Date().toISOString(),
          completed_at: new Date().toISOString(),
          error_ref: null,
        },
        validation: { status: "pending", started_at: null, completed_at: null, error_ref: null },
        profile_creation: { status: "pending", started_at: null, completed_at: null, error_ref: null },
        task_routing: { status: "pending", started_at: null, completed_at: null, error_ref: null },
        plan_generation: { status: "pending", started_at: null, completed_at: null, error_ref: null },
        communication: { status: "pending", started_at: null, completed_at: null, error_ref: null },
        tracking: { status: "pending", started_at: null, completed_at: null, error_ref: null },
      },
    },
    extracted: extractedRecord,
    validation_result: null,
    provisioning: null,
    onboarding_plan: null,
    communications: null,
    tracking: null,
    error_log: [],
  };
}

// ---------------------------------------------------------------------------
// Main entrypoint
// ---------------------------------------------------------------------------

async function main() {
  const args = process.argv.slice(2);
  const inputFlag = args.indexOf("--input");
  const outputFlag = args.indexOf("--output");

  const inputPath = inputFlag !== -1 ? args[inputFlag + 1] : DEFAULT_INPUT_PATH;
  const outputPath = outputFlag !== -1 ? args[outputFlag + 1] : null;

  if (!process.env.ANTHROPIC_API_KEY) {
    console.error("❌ Error: ANTHROPIC_API_KEY environment variable is not set.");
    console.error("   Export it with: export ANTHROPIC_API_KEY=your_key_here");
    process.exit(1);
  }

  console.log(`\n🚀 Onboarding AI Extraction Helper`);
  console.log(`   Input:  ${resolve(inputPath)}`);
  console.log(`   Model:  ${MODEL}`);

  let hirePayload;
  try {
    const raw = readFileSync(resolve(inputPath), "utf8");
    hirePayload = JSON.parse(raw);
    console.log(`✅ Input payload loaded. Hire: ${hirePayload?.personal?.full_name || "Unknown"}`);
  } catch (err) {
    console.error(`❌ Failed to read or parse input file at ${inputPath}:`, err.message);
    process.exit(1);
  }

  try {
    const onboardingRecord = await extractOnboardingRecord(hirePayload);

    console.log("\n🎯 Enriched OnboardingRecord:\n");
    console.log("─".repeat(60));
    const output = JSON.stringify(onboardingRecord, null, 2);
    console.log(output);
    console.log("─".repeat(60));

    if (outputPath) {
      writeFileSync(resolve(outputPath), output, "utf8");
      console.log(`\n💾 Output written to: ${resolve(outputPath)}`);
    }

    const status = onboardingRecord.extracted?.extraction_status;
    console.log(`\n✅ Extraction complete. Status: ${status?.toUpperCase()}`);

    if (status === "partial") {
      console.log("⚠️  Some fields are missing. Review extraction_notes for details.");
    } else if (status === "failed") {
      console.log("🚨 Extraction failed. Human review required before proceeding.");
    }

  } catch (err) {
    console.error("\n❌ Extraction failed:", err.message);
    process.exit(1);
  }
}

main();
