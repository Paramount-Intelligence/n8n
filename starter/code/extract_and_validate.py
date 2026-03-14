"""
Helper script to simulate AI extraction and validation of new hire data.
This can be called from n8n or any automation platform.
"""

def extract_and_validate(data):
    """
    Extract structured data and flag missing documents or fields.
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


# Example data
mock_data = {
        "full_name": "John Doe",
        "personal_email": "john@example.com",
        "job_title": "Software Engineer",
        "department": "IT",
        "location": "Karachi",
        "manager_name": "Ali Khan",
        "employment_type": "Full-time",
        "start_date": "2026-04-01",
        "uploaded_documents": ["ID.pdf", "Agreement.pdf"]
    }

result = extract_and_validate(mock_data)
print("Extracted Data:", result)