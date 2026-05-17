import streamlit as st
import streamlit.components.v1 as components
import os
import html as html_mod
import pandas as pd
from engine.ai_processor import extract_product_data
from engine import formatter
from engine import printer
from database import db_manager
import tempfile

# Page initialization
st.set_page_config(page_title="Image-to-Label", layout="centered")

# Session state initialization
if "current_page" not in st.session_state:
    st.session_state.current_page = "Upload"
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None
if "processed_file_id" not in st.session_state:
    st.session_state.processed_file_id = None

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# Page 1: Upload
def show_upload_page():
    st.title("📦 Product Data Extraction")
    st.subheader("Upload an image to extract product details")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"

        # Only run AI once per unique file — not on every Streamlit rerun/button click
        if st.session_state.processed_file_id != file_id:
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
                    st.session_state.processed_file_id = file_id
                    st.success("Data extracted successfully!")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        else:
            st.success("Data extracted successfully!")

        if st.session_state.extracted_data is not None and st.session_state.processed_file_id == file_id:
            if st.button("Proceed to Edit"):
                navigate_to("Edit")

# Page 2: Edit
def show_edit_page():
    st.title("✍️ Edit Product Data")
    if st.session_state.extracted_data is None:
        st.warning("No data found. Please upload an image first.")
        if st.button("Go back to Upload"):
            navigate_to("Upload")
        return

    st.write("Review and modify the extracted information below.")
    
    # Use columns for Editor and Live Canvas
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Editor")
        
        # Product Info Section
        st.markdown("### 📦 Product Info")
        st.session_state.extracted_data["product_title"] = st.text_input(
            "Product Title", value=st.session_state.extracted_data.get("product_title", "")
        )
        st.session_state.extracted_data["footer"] = st.text_input(
            "Footer", value=st.session_state.extracted_data.get("footer", "")
        )

        # Nutrition Section
        st.markdown("### 🥗 Nutrition")
        nutrition = st.session_state.extracted_data.get("nutrition", {})

        # Build rows from extracted data; always show editor (empty row if none)
        nutrition_rows = []
        for prop, values in nutrition.items():
            if prop == "serving_note":
                continue
            if isinstance(values, list):
                for entry in values:
                    nutrition_rows.append({"Property": prop, "100g": entry.get("100g", ""), "Serving": entry.get("serving", "")})
            elif isinstance(values, dict):
                nutrition_rows.append({"Property": prop, "100g": values.get("100g", ""), "Serving": values.get("serving", "")})
            else:
                nutrition_rows.append({"Property": prop, "100g": str(values), "Serving": ""})

        if not nutrition_rows:
            nutrition_rows = [{"Property": "", "100g": "", "Serving": ""}]

        edited_nutrition = st.data_editor(
            st.session_state.extracted_data.get("nutrition_df", pd.DataFrame(nutrition_rows)),
            num_rows="dynamic",
            key="nutrition_editor"
        )

        # Map DataFrame back to nutrition dict for formatter
        new_nutrition = {}
        for _, row in edited_nutrition.iterrows():
            prop = str(row["Property"]).strip()
            if not prop:
                continue
            if prop not in new_nutrition:
                new_nutrition[prop] = []
            new_nutrition[prop].append({"100g": str(row["100g"]), "serving": str(row["Serving"])})

        serving_note_val = nutrition.get("serving_note", "")
        new_nutrition["serving_note"] = serving_note_val
        st.session_state.extracted_data["nutrition"] = new_nutrition
        st.session_state.extracted_data["nutrition_df"] = edited_nutrition

        st.session_state.extracted_data["nutrition"]["serving_note"] = st.text_input(
            "Serving Note (e.g. *Per 25g serving)", value=serving_note_val
        )

        # Ingredients Section
        st.markdown("### 🌿 Ingredients")
        st.session_state.extracted_data["ingredients"] = st.text_area(
            "Ingredients List", value=st.session_state.extracted_data.get("ingredients", ""), height=100
        )
        st.session_state.extracted_data["allergy_advice"] = st.text_input(
            "Allergy Advice", value=st.session_state.extracted_data.get("allergy_advice", "")
        )

        # Storage Section
        st.markdown("### ❄️ Storage")
        st.session_state.extracted_data["storage"] = st.text_area(
            "Storage Instructions", value=st.session_state.extracted_data.get("storage", ""), height=80
        )

    with col2:
        st.subheader("Live Canvas")
        
        # Generate the formatted text
        label_text = formatter.generate_label_text(st.session_state.extracted_data)
        
        # 55-char lines at 10px Courier New ≈ 330px; canvas 350px content = fits without wrapping
        canvas_html = f"""
        <style>
            body {{ margin: 0; padding: 6px; background: #e8e8e8; }}
            .label-canvas {{
                width: 370px;
                min-height: 150px;
                background-color: white;
                color: black;
                padding: 8px 10px;
                font-family: 'Courier New', Courier, monospace;
                white-space: pre;
                overflow-x: hidden;
                box-shadow: 0 3px 8px rgba(0,0,0,0.25);
                border: 1px solid #ccc;
                font-size: 10px;
                line-height: 1.35;
                display: block;
                box-sizing: border-box;
            }}
        </style>
        <div class="label-canvas">{html_mod.escape(label_text)}</div>
        """
        components.html(canvas_html, height=520, scrolling=True)


    st.divider()
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⬅️ Back to Upload"):
            st.session_state.extracted_data = None
            st.session_state.processed_file_id = None
            navigate_to("Upload")
    with c2:
        if st.button("💾 Save Label", use_container_width=True):
            # We assume image_path is stored or passed. For now, use "N/A" as we don't have it in session_state.
            db_manager.save_label("N/A", st.session_state.extracted_data, label_text)
            st.success("Label saved to database!")
    with c3:
        if st.button("Proceed to Print ➡️", use_container_width=True):
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
    
    # Generate the formatted text again for the print page
    label_text = formatter.generate_label_text(st.session_state.extracted_data)
    
    # Preview
    preview_html = f"""
    <style>
        body {{ margin: 0; padding: 6px; background: #e8e8e8; }}
        .label-canvas-small {{
            width: 370px;
            min-height: 80px;
            background-color: white;
            color: black;
            padding: 8px 10px;
            font-family: 'Courier New', Courier, monospace;
            white-space: pre;
            overflow-x: hidden;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            border: 1px solid #ccc;
            font-size: 10px;
            line-height: 1.35;
            display: block;
            box-sizing: border-box;
        }}
    </style>
    <div class="label-canvas-small">{html_mod.escape(label_text)}</div>
    """
    components.html(preview_html, height=320, scrolling=True)



    st.divider()

    # Print Settings
    copies = st.number_input("Number of copies", min_value=1, value=1, step=1)

    conn_type = st.radio("Connection", ["Network (IP)", "USB (Auto-detect)"], horizontal=True)

    printer_identifier = None
    if conn_type == "Network (IP)":
        ip = st.text_input("Brother QL-810W IP Address", placeholder="192.168.1.x")
        if ip:
            printer_identifier = f"tcp://{ip}"
    else:
        with st.spinner("Scanning for USB printers..."):
            devices = printer.discover_printers()
        if devices:
            labels = [d[0] for d in devices]
            identifiers = [d[1] for d in devices]
            idx = st.selectbox("Select USB Printer", range(len(labels)), format_func=lambda i: labels[i])
            printer_identifier = identifiers[idx]
        else:
            st.warning("No USB Brother printers detected. Use Network (IP) instead.")

    if st.button("Print Now", use_container_width=True):
        if not printer_identifier:
            st.error("Enter printer IP or connect via USB first.")
        else:
            with st.spinner("Rendering and sending to printer..."):
                success = printer.print_label(label_text, printer_identifier, copies)
                if success:
                    st.toast("Label sent to printer!", icon="✅")
                    st.success("Printed successfully!")
                else:
                    st.toast("Printing failed!", icon="❌")
                    st.error("Print failed. Check IP/USB connection and that brother_ql is installed.")

    if st.button("Back to Edit"):
        navigate_to("Edit")

# Router
if st.session_state.current_page == "Upload":
    show_upload_page()
elif st.session_state.current_page == "Edit":
    show_edit_page()
elif st.session_state.current_page == "Label":
    show_label_page()
