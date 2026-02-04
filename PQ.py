import streamlit as st
import re
from PyPDF2 import PdfReader
import requests
import pandas as pd

st.set_page_config(page_title="PQ Management System", layout="wide")

FLOW_URL = st.secrets["FLOW_URL"]
DEFAULT_USERNAME = st.secrets["DEFAULT_USERNAME"]
DEFAULT_PASSWORD = st.secrets["DEFAULT_PASSWORD"]

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
