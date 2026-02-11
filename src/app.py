import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import os
from dotenv import load_dotenv

# Local imports
try:
    from config import MODELS, PAGE_CONFIG
    from utils import extract_pdf
    from services import analyze_documents
except ImportError:
    # Fallback for when running from root as module (unlikely with streamlit run)
    from src.config import MODELS, PAGE_CONFIG
    from src.utils import extract_pdf
    from src.services import analyze_documents

load_dotenv()

# --- UI Config ---
st.set_page_config(**PAGE_CONFIG)
st.title("🏦 Comprehensive Trade Audit (UCP 600)")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

with st.sidebar:
    st.header("Settings")
    selected_model = st.selectbox("Select Model", MODELS, index=0)

# --- Document Uploads ---
cols = st.columns(3)
lc = cols[0].file_uploader("Letter of Credit (MT700)", type="pdf")
inv = cols[1].file_uploader("Invoice", type="pdf")
bl = cols[2].file_uploader("Bill of Lading", type="pdf")

if st.button("🚀 Run Comprehensive Audit"):
    if not (lc and inv and bl):
        st.warning("Please provide all 3 documents.")
    else:
        with st.spinner("Analyzing documents..."):
            lc_text = extract_pdf(lc)
            inv_text = extract_pdf(inv)
            bl_text = extract_pdf(bl)

            try:
                # Use the service function
                raw_response = analyze_documents(lc_text, inv_text, bl_text, selected_model)

                # print log
                st.text_area("Raw Response Log", raw_response, height=200)

                data = json.loads(raw_response)
                df = pd.DataFrame(data)

                # Add visual status indicators
                if 'status' in df.columns:
                    df['status'] = df['status'].apply(lambda x: f"🚩 {x}" if "DISCREPANCY" in str(x).upper() else f"✅ {x}")

                st.subheader("Audit Report")
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Metric Dashboard
                if not df.empty and 'status' in df.columns:
                    m1, m2 = st.columns(2)
                    m1.metric("Total Checks", len(df))
                    
                    # Safe counting of discrepancies
                    discrepancy_count = len(df[df['status'].astype(str).str.contains("DISCREPANCY", case=False, na=False)])
                    m2.metric("Discrepancies", discrepancy_count)

            except Exception as e:
                st.error(f"Error: {e}")
                # st.code(raw_response) # raw_response might not be defined if error happens before
