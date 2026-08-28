import os
import streamlit as st
import pandas as pd

from src.db import init_db
from src.database import authenticate_user, register_user, update_user_status, get_all_users_df

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

if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None


# ----------------------------------------------------
# 4. AUTHENTICATION & LOGIN / REGISTRATION GATEWAY
# ----------------------------------------------------
def render_auth_gateway():
    """Renders the secure Login & Self-Registration Portal."""
    if os.path.exists(BANNER_PATH):
        st.image(BANNER_PATH, use_container_width=True)

    col_l, col_center, col_r = st.columns([1, 2, 1])

    with col_center:
        st.markdown("### 🔐 PragyanAI Institutional Access Portal")
        st.caption("Sign in to your authorized account or submit a self-registration request for approval.")

        tab_login, tab_register, tab_public = st.tabs(["🔑 Sign In", "📝 Create Account", "🏆 Public Wall of Fame"])

        # --- TAB 1: LOGIN ---
        with tab_login:
            with st.form("login_form"):
                username_input = st.text_input("Username or Institutional ID")
                password_input = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("🚀 Authenticate & Enter", use_container_width=True, type="primary")

                if submit_login:
                    if not username_input or not password_input:
                        st.error("Please provide both username and password.")
                    else:
                        success, user_payload, msg = authenticate_user(username_input, password_input)
                        if success:
                            st.session_state.authenticated_user = user_payload
                            st.success(f"Welcome, {user_payload['full_name']} ({user_payload['role']})!")
                            st.rerun()
                        else:
                            st.error(f"Authentication Failed: {msg}")

            st.markdown("---")
            st.markdown("💡 **Default Demo Accounts for Instant Access:**")
            demo_df = pd.DataFrame([
                {"Role": "PragyanAI Engine / Admin", "Username": "admin", "Password": "admin123"},
                {"Role": "Placement Head", "Username": "placement_head", "Password": "head123"},
                {"Role": "Student (AIML)", "Username": "student_arjun", "Password": "student123"},
                {"Role": "Hiring Partner (NVIDIA)", "Username": "nvidia_recruiter", "Password": "nvidia123"}
            ])
            st.dataframe(demo_df, use_container_width=True, hide_index=True)

        # --- TAB 2: REGISTER ---
        with tab_register:
            st.markdown("##### 📝 Submit Registration for PragyanAI Approval")
            with st.form("register_form"):
                reg_name = st.text_input("Full Name *")
                reg_email = st.text_input("Email Address *")
                reg_user = st.text_input("Desired Username *")
                reg_pass = st.text_input("Password *", type="password")
                reg_role = st.selectbox(
                    "Select Requested Role *",
                    [
                        "Student",
                        "Placement Head",
                        "Placement Team",
                        "Hiring Partner",
                        "HOD / Principal / Management",
                        "PragyanAI Engine"
                    ]
                )
                reg_org = st.text_input("Department / Organization (e.g. 'AIML' or 'Google Inc.')")

                submit_reg = st.form_submit_button("📩 Submit for Verification", use_container_width=True)

                if submit_reg:
                    if not reg_name or not reg_email or not reg_user or not reg_pass:
                        st.error("Please fill in all mandatory fields (*).")
                    else:
                        success, reg_msg = register_user(
                            username=reg_user,
                            email=reg_email,
                            password=reg_pass,
                            full_name=reg_name,
                            role=reg_role,
                            org_or_dept=reg_org
                        )
                        if success:
                            st.success(reg_msg)
                            st.info("ℹ️ Your account has been saved with **Status: Pending**. The PragyanAI Engine / Placement Administrator can approve it from their console.")
                        else:
                            st.error(f"Registration Error: {reg_msg}")

        # --- TAB 3: PUBLIC ACCESS ---
        with tab_public:
            st.info("You can view public placement honors and achievers without signing in.")
            if st.button("🌟 Proceed to Wall of Fame (Guest Mode)", use_container_width=True):
                st.session_state.authenticated_user = {
                    "username": "guest",
                    "full_name": "Public Visitor",
                    "role": "Public / Wall of Fame",
                    "status": "Approved"
                }
                st.rerun()


# ----------------------------------------------------
# 5. CHECK AUTHENTICATION STATE
# ----------------------------------------------------
if st.session_state.authenticated_user is None:
    render_auth_gateway()
    st.stop()

# User is Authenticated
current_user = st.session_state.authenticated_user
user_role = current_user["role"]

# ----------------------------------------------------
# 6. SIDEBAR NAVIGATION & PRAGYANAI APPROVAL CONTROLLER
# ----------------------------------------------------
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=110)
    else:
        st.title("🎓 PragyanAI")

    st.markdown(f"**Logged In:** {current_user['full_name']}")
    st.caption(f"Role: `{user_role}` • Status: 🟢 `{current_user.get('status', 'Approved')}`")

    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.authenticated_user = None
        st.rerun()

    st.markdown("---")

    # Global Cohort Telemetry Widget
    if "students" in st.session_state and not st.session_state.students.empty:
        df_stu = st.session_state.students
        total_cand = len(df_stu)
        placed_cand = len(df_stu[df_stu["Status"].isin(["Placed", "Selected"])])
        p_rate = round((placed_cand / total_cand * 100), 1) if total_cand > 0 else 0.0

        st.markdown("**📊 Live Institutional Telemetry**")
        st.write(f"- **Enrolled Batch:** `{total_cand:,}`")
        st.write(f"- **Placed Scholars:** `{placed_cand:,}`")
        st.write(f"- **Placement Conversion:** `{p_rate}%`")

    st.markdown("---")
    st.caption("PragyanAI Enterprise Portal • v2.0.0 (2026)")

# ----------------------------------------------------
# 7. MULTI-PAGE DEFINITIONS & RBAC ROUTING
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
    title="PragyanAI Skill Telemetry & Approvals",
    icon="⚡",
    default=(user_role == "PragyanAI Engine")
)

wall_of_fame_page = st.Page(
    "views/7_Wall_of_Fame.py",
    title="Wall of Fame Achievers",
    icon="🏆",
    default=(user_role == "Public / Wall of Fame")
)

# RBAC Routing Based on Verified User Persona
if user_role == "Student":
    nav = st.navigation({"Candidate Workspace": [student_page, wall_of_fame_page]})
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
    nav = st.navigation({"Recruiter Terminal": [company_page, wall_of_fame_page]})
elif user_role == "HOD / Principal / Management":
    nav = st.navigation({"Strategic Governance": [exec_page, wall_of_fame_page, pragyan_page]})
elif user_role == "PragyanAI Engine":
    nav = st.navigation({"AI Telemetry, Approvals & Governance": [pragyan_page, exec_page, head_page, wall_of_fame_page]})
else:  # Public
    nav = st.navigation({"Honors & Achievers": [wall_of_fame_page]})

# ----------------------------------------------------
# 8. BANNER HEADER & VIEW EXECUTION
# ----------------------------------------------------
if os.path.exists(BANNER_PATH):
    st.image(BANNER_PATH, use_container_width=True)

nav.run()
