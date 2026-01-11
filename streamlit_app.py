# streamlit_app.py
import streamlit as st
import tempfile
import os
from preprocess import derive_profile, extract_text

st.title("Resume extraction")
st.write("Upload a resume file (.pdf, .docx, .doc, .txt). The app predicts the job role based on filename and optional text analysis.")

uploaded = st.file_uploader("Upload file", type=["pdf", "docx", "doc", "txt"])

if uploaded is not None:
    # Save uploaded file to a temp path (needed for .doc/.docx)
    tmpdir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmpdir, uploaded.name)
    with open(tmp_path, "wb") as f:
        f.write(uploaded.getbuffer())

    # Extract text (optional fallback)
    extracted_text = extract_text(tmp_path)

    # Predict job role using filename + folder + extracted text
    folder_name = ""  # single file upload → no folder info
    predicted_role = derive_profile(uploaded.name, folder_name, extracted_text)

    st.success(f"Predicted Job Role: **{predicted_role}**")

    # Optional: show first 500 chars of text for reference
    if extracted_text.strip():
        st.subheader("Resume Text Preview")
        st.text_area("", extracted_text[:500] + ("..." if len(extracted_text) > 500 else ""), height=200)

    # Cleanup temp file
    try:
        os.remove(tmp_path)
        os.rmdir(tmpdir)
    except Exception:
        pass

