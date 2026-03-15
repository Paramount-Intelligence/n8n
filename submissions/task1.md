# Task 1: AI-Powered Automation Solution Design

## Workflow Logic
The onboarding orchestrator follows a structured, intelligent path to transform raw intake data into a personalized employee journey:
1. **Intake**: New hire data is captured via an integrated n8n Form Trigger.
2. **Data Extraction**: Raw text is processed by a Groq-powered AI node (Llama 3.1) to extract structured entities like Name, Role, and Start Date.
3. **Validation Gate**: An 'If' node verifies critical information, specifically checking if a 'Personal Email' exists before proceeding.
4. **Task Initialization**: A JavaScript Code node generates a baseline set of operational tasks for IT and HR.
5. **Intelligent Personalization**: A Google Gemini node analyzes the specific role and department to generate a custom 5-day onboarding plan.
6. **Communication Dispatch**: A final LLM chain drafts a contextual welcome email, which is automatically sent to the hire via SMTP.

## Where AI Is Used
* **Classification & Extraction**: The 'Information Extractor' normalizes form inputs into clean JSON attributes.
* **Workflow Decision Logic**: The system uses role-based reasoning to determine if a hire is technical or non-technical to tailor the onboarding plan.
* **Automatic Drafting**: The LLM Chain creates ready-to-send welcome emails without manual templates.
* **Recommendations & Personalization**: Gemini generates a 5-day syllabus unique to the hire's specific job title.

## Prompt Engineering
* **Role-Based Identity**: Prompts define the AI as a "Senior HR Operations Specialist" to ensure professional output.
* **Conditional Logic**: Prompts include instructions to differentiate content for technical vs. non-technical roles.
* **Structured Constraints**: Prompts require specific formats (Markdown) and mandatory sections (Meetings, Tools, Tasks).

## Data Flow and Integrations
* **n8n**: The central automation platform orchestrating the entire flow.
* **Groq (Llama 3.1)**: Used for high-speed data extraction and email drafting.
* **Google Gemini (2.5 Flash)**: Used for complex, long-form content generation for the onboarding plan.
* **SMTP (Email)**: Dispatches the final welcome package to the new employee.

## Business Impact
* **Efficiency**: Automates the manual task of planning and drafting, reducing overhead.
* **Accuracy**: The 'If' node prevents errors by ensuring data exists before execution.
* **Personalization**: Every hire receives a plan specific to their role and Islamabad/Lahore/Peshawar location.
* **HR Time Savings**: Removes the need for manual coordination between IT and HR for initial task routing.