# Task 2: Implementation Demo

## Demo Type
* **n8n Workflow**: A live, multi-node automation scaffold.
* **AI Model Integration**: Combines Groq and Google Gemini APIs for specialized tasks.

## Files Included
* `Employee-onboarding.json`: The complete n8n workflow export file.
* `prompts.md`: A registry of all system and user prompts used in the models.

## Flow of Data
1. **Source**: Data enters via the `On form submission` node.
2. **Parsing**: The `Information Extractor` (Llama 3.1) structures the raw text.
3. **Filtering**: The `If` node ensures a `Personal Email` is present; otherwise, it triggers a `Stop and Error` node.
4. **Augmentation**: The `Code in JavaScript` node attaches a standard task list to the workflow.
5. **Generation**: `Message a model` (Gemini) creates the plan, and `Basic LLM Chain` drafts the email.
6. **Execution**: The `Send an Email` node delivers the final output to the user's Gmail.

## Pain Points Solved
* **Manual Drafting**: Solves the need for HR to manually write individualized welcome letters.
* **Fragmented Processes**: Unites the intake, task routing, and planning into a single visual flow.
* **Lack of Personalization**: Moves away from generic templates to role-specific technical roadmaps.

## Assumptions
* **API Access**: Assumes valid credentials for Groq and Google Gemini are provided.
* **SMTP Config**: Assumes a Gmail App Password is used for the SMTP connection.

## Setup Instructions
1.  Open **n8n** and select **Import from File** to upload the `Employee-onboarding.json`.
2.  Add your **Groq API Key** to the `Groq account` credential.
3.  Add your **Google Gemini API Key** to the `Google Gemini Api account`.
4.  Configure the **SMTP node** with your Gmail address and App Password.
5.  Execute the workflow to generate the form URL and submit a test hire.