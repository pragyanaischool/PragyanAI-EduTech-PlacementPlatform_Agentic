import os
import streamlit as st
import pandas as pd

from src.db import init_db

# ----------------------------------------------------
# 1. PAGE CONFIGURATION & METADATA
# ----------------------------------------------------
st.set_page_config(
    page_title="PragyanAI Enterprise Placement Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 2. ASSETS INJECTION (CSS STYLES & BRANDING)
# ----------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(PROJECT_ROOT, "assets", "css", "custom.css")
LOGO_PATH = os.path.join(PROJECT_ROOT, "assets", "images", "pragyan_logo.png")
BANNER_PATH = os.path.join(PROJECT_ROOT, "assets", "images", "hero_banner.png")

if os.path.exists(CSS_PATH):
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. DATABASE SYNCHRONIZATION & INITIALIZATION
# ----------------------------------------------------
if "students" not in st.session_state:
    with st.spinner("Initializing SQLite database & loading CSV seed records..."):
        init_db()

# ----------------------------------------------------
# 4. SIDEBAR NAVIGATION & RBAC CONTROLLER
# ----------------------------------------------------
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=120)
    else:
        st.title("🎓 PragyanAI")

    st.markdown("### 🏛️ Institutional Portal")
    st.caption("AI-Powered Campus Recruitment & Skill Telemetry Suite")
    st.markdown("---")

    # Role-Based Access Selector
    user_role = st.selectbox(
        "Select Active RBAC Persona:",
        [
            "Student",
            "Placement Head",
            "Placement Team",
            "Hiring Partner",
            "HOD / Principal / Management",
            "PragyanAI Engine",
            "Public / Wall of Fame"
        ],
        index=0
    )

    st.markdown("---")

    # Global Cohort Telemetry Widget in Sidebar
    if "students" in st.session_state and not st.session_state.students.empty:
        df_stu = st.session_state.students
        total_cand = len(df_stu)
        placed_cand = len(df_stu[df_stu["Status"].isin(["Placed", "Selected"])])
        p_rate = round((placed_cand / total_cand * 100), 1) if total_cand > 0 else 0.0

        st.markdown("**📊 Institutional Snapshot**")
        st.write(f"- **Enrolled Batch:** `{total_cand:,}`")
        st.write(f"- **Placed Scholars:** `{placed_cand:,}`")
        st.write(f"- **Placement Conversion:** `{p_rate}%`")

    st.markdown("---")
    st.caption("PragyanAI Placement Suite • v2.0.0 (2026)")

# ----------------------------------------------------
# 5. MULTI-PAGE PAGE DEFINITIONS & RBAC ROUTING
# ----------------------------------------------------
student_page = st.Page(
    "views/1_Student_Hub.py",
    title="Student Career Hub & RAG",
    icon="👩‍🎓",
    default=(user_role == "Student")
)

head_page = st.Page(
    "views/2_Placement_Head.py",
    title="Placement Directorate",
    icon="👔",
    default=(user_role == "Placement Head")
)

team_page = st.Page(
    "views/3_Placement_Team.py",
    title="Operations & Pipeline Ledger",
    icon="📋",
    default=(user_role == "Placement Team")
)

company_page = st.Page(
    "views/4_Company_Portal.py",
    title="Hiring Partner Hub",
    icon="🏢",
    default=(user_role == "Hiring Partner")
)

exec_page = st.Page(
    "views/5_Executive_Board.py",
    title="Executive Board & NIRF Audit",
    icon="🏛️",
    default=(user_role == "HOD / Principal / Management")
)

pragyan_page = st.Page(
    "views/6_PragyanAI_Engine.py",
    title="PragyanAI Skill Telemetry",
    icon="⚡",
    default=(user_role == "PragyanAI Engine")
)

wall_of_fame_page = st.Page(
    "views/7_Wall_of_Fame.py",
    title="Wall of Fame Achievers",
    icon="🏆",
    default=(user_role == "Public / Wall of Fame")
)

# Enforce Navigation Routing based on Selected Persona
if user_role == "Student":
    nav = st.navigation({
        "Candidate Workspace": [student_page, wall_of_fame_page]
    })
elif user_role == "Placement Head":
    nav = st.navigation({
        "Directorate Control": [head_page, team_page, exec_page],
        "Platform & Telemetry": [pragyan_page, wall_of_fame_page]
    })
elif user_role == "Placement Team":
    nav = st.navigation({
        "Operations": [team_page, student_page],
        "Institutional Ledger": [wall_of_fame_page, exec_page]
    })
elif user_role == "Hiring Partner":
    nav = st.navigation({
        "Recruiter Terminal": [company_page, wall_of_fame_page]
    })
elif user_role == "HOD / Principal / Management":
    nav = st.navigation({
        "Strategic Governance": [exec_page, wall_of_fame_page, pragyan_page]
    })
elif user_role == "PragyanAI Engine":
    nav = st.navigation({
        "AI Telemetry & Diagnostics": [pragyan_page, exec_page, wall_of_fame_page]
    })
else:  # Public / Wall of Fame
    nav = st.navigation({
        "Honors & Achievers": [wall_of_fame_page, exec_page]
    })

# ----------------------------------------------------
# 6. BANNER HEADER & PAGE EXECUTION
# ----------------------------------------------------
if os.path.exists(BANNER_PATH):
    st.image(BANNER_PATH, use_container_width=True)

nav.run()
