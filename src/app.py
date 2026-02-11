import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import os
from dotenv import load_dotenv
import extra_streamlit_components as stx
import time

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

cookie_manager = stx.CookieManager()
cookie_manager.get_all()

api_key = cookie_manager.get(cookie="gemini_api_key")

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    with st.sidebar:
        with st.form("api_key_form"):
            st.markdown("### Enter Gemini API Key")
            key_input = st.text_input("API Key", type="password")
            submitted = st.form_submit_button("Save Key")
            if submitted and key_input:
                cookie_manager.set("gemini_api_key", key_input, key="set_key")
                st.rerun()

    st.warning("Please enter your Gemini API Key in the sidebar to proceed.")
    st.stop()

genai.configure(api_key=api_key)

with st.sidebar:
    st.markdown("### ℹ️ Tentang Aplikasi")
    st.markdown("""
    **Deskripsi & Kapabilitas:**
    
    Aplikasi ini menggunakan AI untuk menganalisis dokumen perdagangan (LC, Invoice, BL) dan memverifikasi kesesuaiannya dengan aturan UCP 600.
    
    **Fitur Utama:**
    *   ✅ Pengecekan konsistensi dokumen otomatis.
    *   ✅ Identifikasi discrepancy.
    *   ✅ Referensi pasal UCP 600.
    """)
    
    st.markdown("### ⚠️ Disclaimer")
    st.warning("""
    **Perhatian**: Hasil analisis AI ini hanya untuk tujuan referensi dan tidak menggantikan pemeriksaan profesional resmi. Selalu verifikasi dokumen asli secara manual.
    """)

    st.markdown("---")
    with st.expander("📂 UCP Reference Files"):
        # Determine path to reference_files (assuming app.py is in src/)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ref_path = os.path.join(base_dir, "reference_files")
        
        if os.path.exists(ref_path):
            files = os.listdir(ref_path)
            for f in files:
                if f.endswith(".pdf"):
                    file_path = os.path.join(ref_path, f)
                    with open(file_path, "rb") as pdf_file:
                        st.download_button(
                            label=f"📄 {f}",
                            data=pdf_file,
                            file_name=f,
                            mime="application/pdf"
                        )
        else:
            st.info("Reference files directory not found.")

    st.markdown("---")

    st.header("Settings")
    selected_model = st.selectbox("Select Model", MODELS, index=0)

# --- Document Uploads ---
cols = st.columns(3)
lc = cols[0].file_uploader("Letter of Credit (MT700)", type="pdf")
inv = cols[1].file_uploader("Invoice", type="pdf")
bl = cols[2].file_uploader("Bill of Lading", type="pdf")


col1, col2 = st.columns([1, 2])
with col1:
    run_audit = st.button("🚀 Run Comprehensive Audit")
with col2:
    use_ref = st.button("📂 Auto-Load Reference Files")

if run_audit or use_ref:
    if use_ref:
        try:
            # Determine path to reference_files (assuming app.py is in src/)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ref_path = os.path.join(base_dir, "reference_files")
            
            lc = open(os.path.join(ref_path, "lc_document.pdf"), "rb")
            inv = open(os.path.join(ref_path, "invoice_document.pdf"), "rb")
            bl = open(os.path.join(ref_path, "bill_of_lading_document.pdf"), "rb")
            st.info("Using reference documents from `reference_files/`")
        except FileNotFoundError:
            st.error("Reference files not found. Please ensure `reference_files/` folder exists with lc_document.pdf, invoice_document.pdf, and bill_of_lading_document.pdf")
            st.stop()

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

                # print log to console
                print("Raw Response:", raw_response)

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
