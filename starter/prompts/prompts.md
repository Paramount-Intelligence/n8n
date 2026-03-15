# Prompts Registry: AI-Driven Onboarding Orchestration
This document outlines the prompt engineering strategy used in the automated onboarding workflow. All prompts are designed to work with LLama-3.3-70B (via Groq) and Gemini 1.5 Flash to ensure low-latency and high-accuracy extraction and generation.

## 1. Information Extraction & Normalization
Node: Information Extractor

Model: llama-3-70b-instant (Groq)

Objective: Transform unstructured form data into a validated JSON object to prevent downstream automation errors.

System Message
Plaintext
You are an HR Data Specialist. Your task is to extract structured entities from the provided raw text. 
Identify the following fields: Full Name, Personal Email, Job Title, Department, Location, Manager Name, Employment Type, and Start Date.
If any field is missing, return "Not Provided". Output the result in a clean, flattened JSON format.
User Prompt
Plaintext
New Hire Submission Details:
- Name: {{ $json["Full Name"] }}
- Email: {{ $json["Personal Email"] }}
- Role: {{ $json["Job Title"] }}
- Dept: {{ $json.Department }}
- Location: {{ $json.Location }}
- Manager: {{ $json["Manager Name"] }}
- Type: {{ $json["Employment Type"] }}
- Start Date: {{ $json["Start Date"] }}
- Systems Requested: {{ $json["Required Systems"] }}


## 2. Personalized Onboarding Plan Generation
Node: Onboarding Plan Generator

Model: gemini-1.5-flash

Objective: Contextual reasoning based on the employee's role to create a technical or operational syllabus.

System Message
Plaintext
You are a Senior HR Operations Specialist and Onboarding Designer. 
Your goal is to create a 5-day roadmap that balances technical setup with social integration.
NEVER use placeholders like [Insert Name]. Use the specific data provided.
User Prompt
Plaintext
Task: Create a detailed 5-day onboarding plan for the following new hire:

- Name: {{ $('Information Extractor').item.json.output["Full Name"] }}
- Role: {{ $('Information Extractor').item.json.output["Job Title"] }}
- Department: {{ $('Information Extractor').item.json.output.Department }}

Guidelines:
1. Personalization: If the role is technical (e.g., AI Engineer, Data Science), include deep dives into GitHub, Python environments, or Cloud Infrastructure.
2. Mandatory Sections: For each day (1-5), include:
   - Meetings: Key stakeholders to meet.
   - Tools Training: Specific software training (e.g., Slack, Jira, or MLflow).
   - First Tasks: A low-stakes "win" task.
3. Output: Clean Markdown with headers and bullet points. Keep it under 250 words.


## 3. Automated Welcome Communication
Node: Welcome Email Drafter

Model: llama-3.1-8b-instant (Groq)

Objective: Zero-shot generation of professional, ready-to-send correspondence.

System Message
Plaintext
You are an HR Automator. Write a final, ready-to-send welcome email. 
Do not include any preamble or "Here is your email" text. 
Ensure the tone is welcoming, professional, and specific to the Islamabad office branch.
User Prompt
Plaintext
Generate a welcome email for:
- Employee Name: {{ $('Information Extractor').item.json.output["Full Name"] }}
- Job Role: {{ $('Information Extractor').item.json.output["Job Title"] }}
- Manager: {{ $('Information Extractor').item.json.output["Manager Name"] }}
- Office Location: {{ $('Information Extractor').item.json.output.Location }}

Include:
- Start Date instructions for {{ $('Information Extractor').item.json.output["Start Date"] }}.
- Instructions: Mention the Islamabad office location and onboarding@company.com for support.


### Prompt Design Considerations
JSON-First Architecture: By forcing the first node to output JSON, we ensure that subsequent nodes can access data via {{ $json[...] }} without needing further AI processing.

Role-Based Logic: The onboarding plan prompt uses conditional logic instructions to differentiate between a "Software Engineer" and an "HR Admin," ensuring relevance.