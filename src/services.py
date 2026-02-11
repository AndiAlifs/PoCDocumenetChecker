
import google.generativeai as genai

def analyze_documents(lc_text, inv_text, bl_text, model_name):
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    Act as a Trade Finance Auditor. Compare the following documents based on UCP 600.
    
    LC DATA: {lc_text}
    INVOICE DATA: {inv_text}
    BL DATA: {bl_text}

    TASK: Identify discrepancies in Applicant Name, Beneficiary Name, Dates, Ports, Weights, and Descriptions.
    
    Return the result ONLY as a JSON array of objects with this structure:
    [
      {{
        "category": "Identity/Logistics/Product",
        "field": "Field Name",
        "requirement": "Value in LC",
        "found_value": "Value in Docs",
        "status": "MATCH or DISCREPANCY",
        "ucp_ref": "UCP 600 Article"
      }}
    ]
    """
    
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    return response.text
