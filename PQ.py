import streamlit as st
import re
from PyPDF2 import PdfReader
import requests
import pandas as pd

st.set_page_config(page_title="PQ Management System", layout="wide")

LOGO_DATA_URI = """data:image/jpeg;base64,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"""

FLOW_URL = "https://defaulte2546b9d33f94279b6ede809f62fb3.36.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/cb2c0343c20b43d19b274f4646e40e1a/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=EwGHzFJ3HEXZ2P62FqDtkYygFRkuH6W5Ei_7R3t8ERQ"

DEFAULT_USERNAME = "SEDFA"
DEFAULT_PASSWORD = "SEDFAPQ@2026"

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "submitted_questions" not in st.session_state:
    st.session_state.submitted_questions = []
if "confirm_map" not in st.session_state:
    st.session_state.confirm_map = {}
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
if "auth_error" not in st.session_state:
    st.session_state.auth_error = ""

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def extract_fields(text):
    t = text.replace("\u00a0", " ")

    house = ""
    if re.search(r"\bNATIONAL\s+ASSEMBLY\b", t, re.IGNORECASE):
        house = "National Assembly"
    elif re.search(r"\bNATIONAL\s+COUNCIL\s+OF\s+PROVINCES\b", t, re.IGNORECASE) or re.search(r"\bNCOP\b", t, re.IGNORECASE):
        house = "National Council of Provinces (NCOP)"

    qnum = re.search(r"(\d+)\.", t)
    QuestionNumber = qnum.group(1) if qnum else ""

    member = re.search(r"\d+\.\s*(.*?)\s*\(", t)
    MemberAsking = member.group(1).replace("1Mr", "Mr").strip() if member else ""

    party = re.search(r"\((.*?)\)", t)
    PoliticalParty = party.group(1).split(":")[-1].strip() if party else ""

    minister = re.search(r"to ask the\s+(.*?):", t)
    MinisterRespondent = minister.group(1).strip() if minister else ""

    minister_pos = re.search(r"to ask the\s+" + re.escape(MinisterRespondent) + r":", t)
    start_pos = minister_pos.end() if minister_pos else 0

    question_match = re.search(
        r"([\s\S]*?)(?:Reply:|REPLY:|Response:|ANSWER:|Answer:|$)",
        t[start_pos:]
    )
    Question = question_match.group(1).strip() if question_match else ""

    financial_keywords = [
        "budget", "fund", "funding", "expenditure", "cost", "costs",
        "amount", "allocation", "spending", "financial year",
        "rand", "r ", "rands", "million", "billion", "audit", "irregular",
        "fruitless", "wasteful", "procurement", "tender"
    ]

    q_lower = Question.lower()
    FinancialType = "Financial" if any(k in q_lower for k in financial_keywords) else "Non-Financial"

    return {
        "PoliticalParty": PoliticalParty,
        "HouseOfParliament": house,
        "QuestionNumber": QuestionNumber,
        "MemberAsking": MemberAsking,
        "MinisterRespondent": MinisterRespondent,
        "Question": Question,
        "Financial/Non-Financial": FinancialType
    }

def generate_response_text(fields):
    hop = fields.get("HouseOfParliament", "").strip()
    qn = fields.get("QuestionNumber", "").strip()
    member = fields.get("MemberAsking", "").strip()
    party = fields.get("PoliticalParty", "").strip()
    minister = fields.get("MinisterRespondent", "").strip()
    fin_type = fields.get("Financial/Non-Financial", "").strip()
    question = fields.get("Question", "").strip()

    financial_note = ""
    if fin_type == "Financial":
        financial_note = (
            "Where amounts are requested, the Department will provide the figures for the relevant financial year(s) "
            "and align them to the approved budget and reporting records."
        )
    else:
        financial_note = (
            "The Department will provide the requested information in line with available records and applicable policies."
        )

    return (
        f"Reply:\n\n"
        f"1. The {minister} replies:\n\n"
        f"2. The Department has noted the question posed by {member} ({party})"
        f"{' in the ' + hop if hop else ''}"
        f"{' (Question No. ' + qn + ')' if qn else ''}.\n\n"
        f"3. {financial_note}\n\n"
        f"4. The Department is verifying the relevant information and will provide a consolidated response "
        f"covering all sub-questions contained in the Parliamentary Question.\n\n"
        f"5. Additional context:\n"
        f"- Question category: {fin_type}\n\n"
        f"---\n"
        f"Question (for reference):\n{question}"
    )

def render_logo(width=170):
    st.markdown(
        f"""
        <div style="display:flex; justify-content:center; margin-top:10px; margin-bottom:10px;">
            <img src="{LOGO_DATA_URI}" style="width:{width}px; max-width:100%;"/>
        </div>
        """,
        unsafe_allow_html=True
    )

def login_page():
    render_logo(200)
    st.title("🔐 Login")
    st.markdown("Please sign in to access the PQ Management System.")

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", value="", placeholder="Enter username")
        password = st.text_input("Password", value="", type="password", placeholder="Enter password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
            st.session_state.is_authenticated = True
            st.session_state.auth_error = ""
            st.rerun()
        else:
            st.session_state.auth_error = "Invalid username or password."

    if st.session_state.auth_error:
        st.error(st.session_state.auth_error)

def sidebar_nav():
    st.sidebar.markdown(" ")
    render_logo(150)
    st.sidebar.title("📂 Navigation")
    page = st.sidebar.radio("Go to", ["🏠 Home", "⬆️ Upload PQs"])
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.is_authenticated = False
        st.session_state.uploaded_files = []
        st.session_state.confirm_map = {}
        st.session_state.auth_error = ""
        st.rerun()
    return page

if not st.session_state.is_authenticated:
    login_page()
    st.stop()

page = sidebar_nav()

if page == "🏠 Home":
    st.title("📄 Parliamentary Questions Management System")
    st.markdown(
        """
        ### What this system does
        - Upload Parliamentary Question PDFs
        - Automatically extract structured data
        - Generate a draft response
        - Store records securely in SharePoint
        """
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("📥 Upload", "PDF PQs")
    col2.metric("⚙️ Extract", "Key Fields")
    col3.metric("📝 Draft", "Response")
    st.info("Use the menu on the left to get started.")

elif page == "⬆️ Upload PQs":
    st.title("⬆️ Upload Parliamentary Questions")

    uploads = st.file_uploader(
        "Select one or more PQ PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        key="pq_upload_multi"
    )

    if uploads:
        st.session_state.uploaded_files = uploads

    files = st.session_state.uploaded_files

    if files:
        st.caption(f"{len(files)} file(s) selected")

        for idx, uploaded in enumerate(files):
            with st.expander(f"📄 {uploaded.name}", expanded=(idx == 0)):
                try:
                    text = extract_text_from_pdf(uploaded)
                    fields = extract_fields(text)

                    qn = fields.get("QuestionNumber", "").strip()
                    confirm_key = f"{uploaded.name}_{qn}_{idx}"
                    resp_key = f"generated_response_{confirm_key}"

                    if resp_key not in st.session_state:
                        st.session_state[resp_key] = ""

                    colA, colB = st.columns(2)
                    colA.text_input("House Of Parliament", fields["HouseOfParliament"], disabled=True, key=f"hop_{confirm_key}")
                    colB.text_input("Question Number", fields["QuestionNumber"], disabled=True, key=f"qn_{confirm_key}")

                    col1, col2 = st.columns(2)
                    col1.text_input("Political Party", fields["PoliticalParty"], disabled=True, key=f"pp_{confirm_key}")
                    col2.text_input("Member Asking", fields["MemberAsking"], disabled=True, key=f"ma_{confirm_key}")

                    col3, col4 = st.columns(2)
                    col3.text_input("Minister Respondent", fields["MinisterRespondent"], disabled=True, key=f"mr_{confirm_key}")
                    col4.text_input(
                        "Financial / Non-Financial",
                        fields["Financial/Non-Financial"],
                        disabled=True,
                        key=f"fin_{confirm_key}"
                    )

                    st.text_area("Question", fields["Question"], height=180, disabled=True, key=f"q_{confirm_key}")

                    colg1, colg2 = st.columns([1, 2])
                    with colg1:
                        if st.button("🪄 Generate Response", key=f"gen_{confirm_key}"):
                            st.session_state[resp_key] = generate_response_text(fields)
                            st.rerun()

                    st.text_area(
                        "Generated Response (editable)",
                        height=260,
                        key=resp_key
                    )

                    if qn and qn in st.session_state.submitted_questions:
                        st.warning("⚠️ This PQ has already been submitted.")
                    else:
                        if st.session_state.confirm_map.get(confirm_key) is None:
                            if st.button("📤 Submit to SharePoint", key=f"submit_{confirm_key}"):
                                st.session_state.confirm_map[confirm_key] = "pending"
                                st.rerun()

                        if st.session_state.confirm_map.get(confirm_key) == "pending":
                            st.write("Are you sure you want to upload this PQ?")
                            col_yes, col_no = st.columns(2)

                            with col_yes:
                                if st.button("✅ Yes", key=f"yes_{confirm_key}"):
                                    payload = dict(fields)
                                    payload["ResponseDetails"] = st.session_state.get(resp_key, "").strip()

                                    try:
                                        resp = requests.post(FLOW_URL, json=payload)
                                        if resp.status_code in [200, 202]:
                                            st.success("Submitted ✅")
                                            if qn:
                                                st.session_state.submitted_questions.append(qn)
                                        else:
                                            st.error(f"Submission failed: {resp.status_code}")
                                    except Exception as e:
                                        st.error(str(e))

                                    st.session_state.confirm_map[confirm_key] = None
                                    st.rerun()

                            with col_no:
                                if st.button("❌ No", key=f"no_{confirm_key}"):
                                    st.session_state.confirm_map[confirm_key] = None
                                    st.rerun()

                except Exception as e:
                    st.error(f"Could not process {uploaded.name}: {e}")

        if st.button("🧹 Clear selected files"):
            st.session_state.uploaded_files = []
            st.session_state.confirm_map = {}
            keys_to_remove = [k for k in st.session_state.keys() if k.startswith("generated_response_")]
            for k in keys_to_remove:
                del st.session_state[k]
            st.rerun()
    else:
        st.info("Upload one or more PQ PDFs to start.")
