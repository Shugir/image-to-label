import streamlit as st
import os
from engine.ai_processor import extract_product_data
import tempfile

# Page initialization
st.set_page_config(page_title="Image-to-Label", layout="centered")

# Session state initialization
if "current_page" not in st.session_state:
    st.session_state.current_page = "Upload"
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# Page 1: Upload
def show_upload_page():
    st.title("📦 Product Data Extraction")
    st.subheader("Upload an image to extract product details")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Save image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:
            with st.spinner("Analyzing image with AI..."):
                data = extract_product_data(tmp_path)
                
            if "error" in data:
                st.error(f"AI Extraction failed: {data['error']}")
            else:
                st.session_state.extracted_data = data
                st.success("Data successfully extracted!")
                st.json(data)
                
                if st.button("Proceed to Edit"):
                    navigate_to("Edit")
        finally:
            # Cleanup temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

# Page 2: Edit
def show_edit_page():
    st.title("✍️ Edit Product Data")
    if st.session_state.extracted_data is None:
        st.warning("No data found. Please upload an image first.")
        if st.button("Go back to Upload"):
            navigate_to("Upload")
        return

    st.write("Review and modify the extracted information below.")
    # Edit logic will be implemented in Task 6
    st.json(st.session_state.extracted_data)
    
    if st.button("Back to Upload"):
        st.session_state.extracted_data = None
        navigate_to("Upload")
    
    if st.button("Proceed to Label Generation"):
        navigate_to("Label")

# Page 3: Label
def show_label_page():
    st.title("🏷️ Label Generation")
    if st.session_state.extracted_data is None:
        st.warning("No data found. Please upload an image first.")
        if st.button("Go back to Upload"):
            navigate_to("Upload")
        return

    st.write("Generate and preview your product label.")
    # Label logic will be implemented in Task 7
    st.json(st.session_state.extracted_data)
    
    if st.button("Back to Edit"):
        navigate_to("Edit")

# Router
if st.session_state.current_page == "Upload":
    show_upload_page()
elif st.session_state.current_page == "Edit":
    show_edit_page()
elif st.session_state.current_page == "Label":
    show_label_page()
