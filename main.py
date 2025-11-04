# import streamlit as st
# import pandas as pd
# from PyPDF2 import PdfReader
# from openpyxl import load_workbook
# import asyncio
# from extraction_agent import call_extraction_agent
# from improvement_agent import call_improvement_agent

# st.set_page_config(page_title="Document Extraction Review", layout="wide")
# st.sidebar.title("Upload Section (Mandatory)")

# with st.sidebar.form("file_upload_form"):
#     pdf_file = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_file")
#     excel_file = st.file_uploader("Upload Excel (column schema)", type=["xlsx"], key="excel_file")
#     file_submit = st.form_submit_button("Confirm Uploads")

# if not pdf_file or not excel_file:
#     st.warning("Please upload **both** a PDF **and** an Excel file to proceed.")
#     files_uploaded = False
# else:
#     files_uploaded = True

# if "feedback_log" not in st.session_state:
#     st.session_state.feedback_log = []

# st.title("Document Extraction Feedback")

# def extract_text_from_pdf(pdf_file):
#     reader = PdfReader(pdf_file)
#     return "\n".join([page.extract_text() or "" for page in reader.pages])

# def read_excel_schema(excel_file):
#     wb = load_workbook(excel_file)
#     ws = wb.active
#     columns = [cell.value for cell in ws[1]]
#     instructions = [cell.value for cell in ws[2]]
#     return columns, instructions

# # MAIN - after file upload
# if files_uploaded:
#     st.markdown("**PDF Preview**")
#     pdf_text = extract_text_from_pdf(pdf_file)
#     st.text_area("PDF Preview", value=pdf_text[:300], height=100)

#     st.markdown("**Excel Schema & Instructions**")
#     columns, instructions = read_excel_schema(excel_file)
#     df = pd.DataFrame([instructions], columns=columns)
#     st.write(df)

#     # --- Extraction (run ONCE unless files change) ---
#     if "last_extraction" not in st.session_state or st.session_state.get("last_files", None) != (pdf_file.name, excel_file.name):
#         st.session_state.last_extraction = asyncio.run(
#             call_extraction_agent(pdf_text, columns, instructions)
#         )
#         st.session_state.last_files = (pdf_file.name, excel_file.name)

#     st.markdown("### Extracted Data (Agent Output)")
#     st.code(st.session_state.last_extraction, language="json")

#     # --- FEEDBACK ONLY ---
#     st.markdown("### Feedback or Correction")
#     feedback = st.text_area("Suggest correction/feedback regarding the extracted data:")
#     if st.button("Submit Feedback", key="feedback_button"):
#         st.session_state.feedback_log.append({
#             "extracted_data": st.session_state.last_extraction,
#             "feedback": feedback
#         })
#         st.success("Feedback logged!")
#         if st.session_state.last_extraction and feedback:
#             # (Assume you store or can re-generate previous extraction prompt)
#             previous_prompt = prompt = (
#         f"Extract the following columns from the PDF text:\n"
#         f"Columns: {', '.join(columns)}\n"
#         f"Instructions: {'; '.join(instructions)}\n"
#         f"PDF Content:\n{pdf_text[:2000]}\n"
#         "Output JSON only with column/value pairs."
#     )
#             improved_prompt = asyncio.run(
#                 call_improvement_agent(
#                     st.session_state.last_extraction,
#                     feedback,
#                     previous_prompt
#                 )
#             )
#             st.session_state.feedback_log.append({
#                 "extracted_data": st.session_state.last_extraction,
#                 "feedback": feedback,
#                 "improved_prompt": improved_prompt,
#             })
#             st.success("Feedback and improved prompt logged!")
#             st.markdown(f"#### Improved Extraction Prompt Generated:\n``````")

# if st.sidebar.checkbox("Show Feedback Log", value=True):
#     st.sidebar.markdown("### Feedback Log")
#     st.sidebar.write(st.session_state.feedback_log)

# if not files_uploaded:
#     st.info("Please upload both files and confirm to start the extraction/feedback process.")


import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from openpyxl import load_workbook
import asyncio
from extraction_agent import call_extraction_agent
from improvement_agent import call_improvement_agent

st.set_page_config(page_title="Document Extraction Feedback", layout="wide")
st.sidebar.title("Upload Section (Mandatory)")

with st.sidebar.form("file_upload_form"):
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_file")
    excel_file = st.file_uploader("Upload Excel (column schema)", type=["xlsx"], key="excel_file")
    file_submit = st.form_submit_button("Confirm Uploads")

if not pdf_file or not excel_file:
    st.warning("Please upload **both** a PDF **and** an Excel file to proceed.")
    files_uploaded = False
else:
    files_uploaded = True

if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []
if "last_extraction" not in st.session_state:
    st.session_state['last_extraction'] = None
if "last_prompt" not in st.session_state:
    st.session_state['last_prompt'] = None
if "improved_prompt" not in st.session_state:
    st.session_state['improved_prompt'] = None
if "improved_extraction" not in st.session_state:
    st.session_state['improved_extraction'] = None

st.title("Document Extraction Feedback + Prompt Refinement")

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    return "\n".join([page.extract_text() or "" for page in reader.pages])

def read_excel_schema(excel_file):
    wb = load_workbook(excel_file)
    ws = wb.active
    columns = [cell.value for cell in ws[1]]
    instructions = [cell.value for cell in ws[2]]
    return columns, instructions

if files_uploaded:
    st.markdown("**PDF Preview**")
    pdf_text = extract_text_from_pdf(pdf_file)
    st.text_area("PDF Preview", value=pdf_text[:500], height=120)

    st.markdown("**Excel Schema & Instructions**")
    columns, instructions = read_excel_schema(excel_file)
    df = pd.DataFrame([instructions], columns=columns)
    st.write(df)

    # --- Build initial extraction prompt ---
    prompt = (
        f"Extract the following columns from the PDF text:\n"
        f"Columns: {', '.join(columns)}\n"
        f"Instructions: {'; '.join(instructions)}\n"
        f"PDF Content:\n{pdf_text[:2000]}\n"
        "Return your answer as a JSON object. "
        "Do not write any commentary—output only the JSON in this format: "
        '{"column1": "extractedValue", ...}'
    )
    st.session_state['last_prompt'] = prompt

    # --- Only rerun extraction if new files uploaded ---
    if st.session_state.get("last_uploaded_files") != (pdf_file.name, excel_file.name):
        st.session_state['last_extraction'] = asyncio.run(
            call_extraction_agent(prompt, columns, instructions)
        )
        st.session_state['improved_prompt'] = None
        st.session_state['improved_extraction'] = None
        st.session_state["last_uploaded_files"] = (pdf_file.name, excel_file.name)

    # --- Show extraction ---
    st.markdown("### Extraction Agent Output (Initial)")
    st.code(st.session_state['last_extraction'], language="json")

    # --- Feedback section + RUN IMPROVEMENT AGENT ---
    st.markdown("### Feedback or Correction")
    feedback = st.text_area("Suggest correction/feedback regarding the extracted data:")
    if st.button("Submit Feedback", key="feedback_button"):
        improved_prompt = asyncio.run(
            call_improvement_agent(
                st.session_state['last_extraction'],
                feedback,
                st.session_state['last_prompt']
            )
        )
        st.session_state['improved_prompt'] = improved_prompt
        st.success("Improved prompt generated—see below.")
        st.markdown("#### Improved Extraction Prompt:")
        st.code(improved_prompt, language="markdown")

        # --- Run the extraction agent AGAIN with improved prompt ---
        improved_extraction = asyncio.run(
            call_extraction_agent(pdf_text, improved_prompt, columns)  # columns optional if now in prompt
        )
        st.session_state['improved_extraction'] = improved_extraction

        # --- Log everything ---
        st.session_state.feedback_log.append({
            "old_extraction": st.session_state['last_extraction'],
            "feedback": feedback,
            "improved_prompt": improved_prompt,
            "improved_extraction": improved_extraction
        })

    # --- Show side-by-side results (if improved available) ---
    if st.session_state['improved_extraction']:
        st.markdown("### Side-by-Side Extraction Results")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original Extraction**")
            st.code(st.session_state['last_extraction'], language="json")
        with col2:
            st.markdown("**Extraction With Improved Prompt**")
            st.code(st.session_state['improved_extraction'], language="json")

if st.sidebar.checkbox("Show Feedback Log", value=True):
    st.sidebar.markdown("### Feedback Log")
    st.sidebar.write(st.session_state.feedback_log)

if not files_uploaded:
    st.info("Please upload both files and confirm to start the extraction/feedback process.")
