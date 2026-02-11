
import os
import google.generativeai as genai
from utils import extract_pdf

def analyze_documents(lc_text, inv_text, bl_text, model_name):
    model = genai.GenerativeModel(model_name)
    
    # Load UCP Mandiri Reference
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ref_path = os.path.join(base_dir, 'reference_files', 'mandiri_ucp600_reference.pdf')
    
    ucp_text = ""
    if os.path.exists(ref_path):
        with open(ref_path, 'rb') as f:
            ucp_text = extract_pdf(f)

    prompt = f"""
    Act as a Trade Finance Auditor. Compare the following documents based on the provided UCP Mandiri Reference (UCP 600).
    
    REFERENCE MATERIAL (UCP Mandiri):
    {ucp_text}

    LC DATA: {lc_text}
    INVOICE DATA: {inv_text}
    BL DATA: {bl_text}

    TASK: Identify discrepancies in Applicant Name, Beneficiary Name, Dates, Ports, Weights, and Descriptions.
    
    STRICT RULES:
    1. Base your comparison on the provided REFERENCE MATERIAL.
    2. If a field/column is present in the LC DATA (Task) but NOT found in the supporting documents (Invoice/BL), you MUST still return a result entry for it. In this case, state "there is nothing to compare of" in the found_value or status explanation.
    3. For the "field" key in the JSON, use EXACTLY the field name as it appears in the Task/LC Data requirement (e.g. if the task is "Applicant Name", the field must be "Applicant Name").

    Return the result ONLY as a JSON array of objects with this structure:
    [
      {{
        "category": "Identity/Logistics/Product",
        "field": "Exact Field Name as per Task",
        "requirement": "Value in LC",
        "found_value": "Value in Docs or 'Nothing to compare of' if missing",
        "status": "MATCH, DISCREPANCY, or NOT_COMPARABLE",
        "ucp_ref": "Relevant Article from Reference Material"
      }}
    ]
    """
    
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    return response.text
