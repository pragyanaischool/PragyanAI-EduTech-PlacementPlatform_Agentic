import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from src.chat_widget import render_chat_interface
from src.database import (
    db_add_drive,
    db_update_company_status,
    fetch_table_as_df,
    DriveModel,
    CompanyModel,
    TrainingSessionModel,
    TrainingSessionModel as TSModel,
    get_db_session
)

st.title("👔 Placement Directorate & Leadership Console")
st.caption("Strategic corporate relations, campus drive configuration, recruiter approvals, and skill development scheduling.")

# ---------------------------------------------------------
# 1. LIVE DATA SYNC & METRICS COMPUTATION
# ---------------------------------------------------------
students_df = st.session_state.get("students", pd.DataFrame())
drives_df = st.session_state.get("drives", pd.DataFrame())
companies_df = st.session_state.get("companies", pd.DataFrame())
training_df = st.session_state.get("training_sessions", pd.DataFrame())

# Metric calculations
total_students = len(students_df)
placed_students = len(students_df[students_df["Status"].isin(["Placed", "Selected"])]) if not students_df.empty else 0
placement_rate = round((placed_students / total_students * 100), 2) if total_students > 0 else 0.0
active_drives_cnt = len(drives_df)
pending_comp_cnt = len(companies_df[companies_df["Status"] == "Pending"]) if not companies_df.empty else 0

# Metrics Banner
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Enrolled Cohort", f"{total_students:,}")
m2.metric("Total Placed", f"{placed_students:,}")
m3.metric("Placement Rate", f"{placement_rate:.1f}%")
m4.metric("Active Drives", f"{active_drives_cnt:,}")
m5.metric("Pending Approvals", f"{pending_comp_cnt:,}", delta=f"{pending_comp_cnt} To Review" if pending_comp_cnt > 0 else "All Clear", delta_color="inverse")

st.markdown("---")

# ---------------------------------------------------------
# 2. DIRECTORATE WORKSPACE TABS
# ---------------------------------------------------------
tab_chat, tab_analytics, tab_drives, tab_sessions, tab_approvals, tab_directory = st.tabs([
    "💬 Directorate Copilot",
    "📊 Strategic Analytics",
    "📢 Broadcast Campus Drive",
    "🛠️ Schedule Bootcamps & Workshops",
    "🏢 Recruiter Account Approvals",
    "👥 Directorate Directory"
])

# =========================================================
# TAB 1: CONVERSATIONAL DIRECTORATE COPILOT
# =========================================================
with tab_chat:
    render_chat_interface("Placement Head")

# =========================================================
# TAB 2: STRATEGIC RECRUITMENT & SECTOR ANALYTICS
# =========================================================
with tab_analytics:
    st.subheader("📊 Institutional Recruitment Analytics & Conversion Trends")

    col_a1, col_a2 = st.columns(2)

    with col_a1:
        if not drives_df.empty:
            # Group by company drive counts
            drive_dist = drives_df.groupby("Company")["Drive_ID"].count().reset_index()
            drive_dist.columns = ["Company", "Open Drives"]
            fig_pie = px.pie(
                drive_dist.head(10),
                names="Company",
                values="Open Drives",
                title="Active Drive Distribution across Top Recruiting Partners",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No active drives posted to display drive distribution.")

    with col_a2:
        if not students_df.empty:
            placed_df = students_df[students_df["Status"].isin(["Placed", "Selected"])]
            if not placed_df.empty:
                top_hiring = placed_df.groupby("Company")["ID"].count().reset_index()
                top_hiring.columns = ["Company", "Hires Extended"]
                top_hiring = top_hiring[top_hiring["Company"] != "None"].sort_values(by="Hires Extended", ascending=True).tail(8)

                fig_bar = px.bar(
                    top_hiring,
                    x="Hires Extended",
                    y="Company",
                    orientation="h",
                    title="Top Recruiting Organizations by Final Hires Extended",
                    text="Hires Extended",
                    color="Hires Extended",
                    color_continuous_scale="Viridis"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No student placement conversion telemetry available yet.")
        else:
            st.info("Student records unavailable.")

    # Department-wise Placement Breakdown
    if not students_df.empty:
        st.markdown("#### 🏢 Department-wise Placement Conversion Ratio")
        dept_summary = students_df.groupby(["Dept", "Status"])["ID"].count().reset_index()
        dept_summary.columns = ["Department", "Placement Status", "Student Count"]
        fig_dept_bar = px.bar(
            dept_summary,
            x="Department",
            y="Student Count",
            color="Placement Status",
            barmode="group",
            title="Departmental Placement Spread (Placed vs. Unplaced)",
            color_discrete_map={"Placed": "#10B981", "Selected": "#10B981", "Not Placed": "#EF4444"}
        )
        st.plotly_chart(fig_dept_bar, use_container_width=True)

# =========================================================
# TAB 3: CONFIGURE & BROADCAST CAMPUS DRIVES
# =========================================================
with tab_drives:
    st.subheader("📢 Configure & Broadcast Campus Recruitment Drive")
    st.caption("Publish verified placement drives with CTC boundaries, eligibility parameters, and registration links.")

    # Select from approved companies or add manual
    approved_comps = []
    if not companies_df.empty:
        approved_comps = companies_df[companies_df["Status"] == "Approved"]["Company"].tolist()
    if not approved_comps:
        approved_comps = ["Google", "Microsoft", "Qualcomm", "NVIDIA", "Amazon", "Tata Motors", "Bosch"]

    with st.form("head_broadcast_drive_form"):
        col_d1, col_d2 = st.columns(2)

        with col_d1:
            d_company = col_d1.selectbox("Hiring Organization", approved_comps)
            d_role = col_d1.text_input("Job Profile / Designation", "Associate Software Engineer (Cloud & AI)")
            d_min_cgpa = col_d1.number_input("Minimum CGPA Eligibility Cutoff", 0.0, 10.0, 7.5, 0.1)
            d_depts = col_d1.multiselect(
                "Eligible Academic Departments",
                ["CSE", "AIML", "AIDS", "ISE", "ECE", "EEE", "MECH", "ROBOTICS", "CIVIL", "BIOTECH"],
                default=["CSE", "AIML", "ISE"]
            )
            d_skills = col_d1.text_input("Mandatory Skills (Comma separated)", "Python, FastAPI, Docker, SQL, Data Structures")

        with col_d2:
            d_pkg = col_d2.number_input("Annual Compensation / CTC (LPA)", 1.0, 150.0, 14.5, 0.5)
            d_date = col_d2.date_input("Drive / Pre-Placement Session Date")
            d_app_link = col_d2.text_input("Official Application Portal Link", "https://careers.company.com/apply")
            d_sem_link = col_d2.text_input("Pre-Placement Seminar Link (Google Meet / MS Teams)", "https://meet.google.com/xyz-drive")
            d_ppt_link = col_d2.text_input("Company Orientation Deck URL (PPT/PDF)", "https://pragyan.edu/resources/company_deck.pdf")

        d_desc = st.text_area(
            "Comprehensive Job Description & Evaluation Criteria",
            "Round 1: Online Assessment (Algorithms & Core CS). Round 2: Technical Architecture & System Invariants. Round 3: Leadership/HR Interview."
        )

        if st.form_submit_button("🚀 Publish & Broadcast Placement Drive", type="primary"):
            if not d_depts:
                st.error("Please select at least one eligible academic department.")
            else:
                new_drive_id = f"DRV-{len(drives_df) + 1:03d}"
                drive_payload = {
                    "drive_id": new_drive_id,
                    "company": d_company,
                    "role": d_role,
                    "min_cgpa": float(d_min_cgpa),
                    "eligible_depts": ", ".join(d_depts),
                    "required_skills": d_skills,
                    "description": d_desc,
                    "package_lpa": float(d_pkg),
                    "session_date": str(d_date),
                    "app_link": d_app_link,
                    "seminar_link": d_sem_link,
                    "ppt_link": d_ppt_link
                }

                try:
                    db_add_drive(drive_payload, jd_text=d_desc)

                    # Reload session state from DB
                    st.session_state.drives = fetch_table_as_df(DriveModel).rename(columns={
                        "drive_id": "Drive_ID", "company": "Company", "role": "Role",
                        "min_cgpa": "Min_CGPA", "eligible_depts": "Eligible_Depts",
                        "required_skills": "Required_Skills", "description": "Description",
                        "package_lpa": "Package_LPA", "session_date": "Session_Date",
                        "app_link": "App_Link", "seminar_link": "Seminar_Link", "ppt_link": "PPT_Link"
                    })
                    st.success(f"Campus Placement Drive **{new_drive_id}** for **{d_company}** has been broadcasted successfully to all student portals!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to publish drive: {e}")

    st.markdown("---")
    st.subheader("📋 Active Campus Recruitment Drives Registry")
    if not drives_df.empty:
        display_drive_cols = ["Drive_ID", "Company", "Role", "Min_CGPA", "Package_LPA", "Eligible_Depts", "Session_Date"]
        st.dataframe(drives_df[display_drive_cols], use_container_width=True, hide_index=True)

# =========================================================
# TAB 4: SCHEDULE WORKSHOPS, BOOTCAMPS & GUEST LECTURES
# =========================================================
with tab_sessions:
    st.subheader("🛠️ Schedule Skill Bootcamps & Guest Lectures")
    st.caption("Organize technical training sessions, hands-on hackathons, and guest seminars to bridge identified skill gaps.")

    with st.form("new_training_session_form"):
        col_w1, col_w2 = st.columns(2)

        with col_w1:
            s_type = col_w1.selectbox("Event Modality", ["Bootcamp", "Workshop", "Guest Lecture", "Masterclass", "Hackathon"])
            s_title = col_w1.text_input("Session Title", "Scalable Agentic AI & RAG Deployment Masterclass")
            s_instructor = col_w1.text_input("Lead Instructor / Corporate Speaker", "Dr. Sateesh Ambesange (PragyanAI)")
            s_target_depts = col_w1.multiselect(
                "Target Academic Cohorts",
                ["CSE", "AIML", "AIDS", "ISE", "ECE", "EEE", "MECH", "ROBOTICS", "CIVIL", "BIOTECH"],
                default=["CSE", "AIML", "AIDS", "ISE"]
            )

        with col_w2:
            s_date = col_w2.date_input("Event Date")
            s_timing = col_w2.text_input("Timing / Schedule Duration", "10:00 AM - 04:00 PM")
            s_mode = col_w2.selectbox("Delivery Format", ["Hybrid", "Offline", "Online"])
            s_location = col_w2.text_input("Venue / Room Specification", "Pragyan DeepTech AI Lab, 3rd Floor")

        s_curriculum = st.text_area(
            "Curriculum Blueprint & Modular Topics Covered",
            "1. Multi-Agent Swarms with LangGraph\n2. Vector Database Chunking & Hybrid Retrieval\n3. High-Throughput Inference Engine Setup\n4. Capstone Architecture Review"
        )

        col_l1, col_l2 = st.columns(2)
        s_meet_link = col_l1.text_input("Online Video Stream Link", "https://zoom.us/j/pragyan-bootcamp")
        s_res_link = col_l2.text_input("Lecture Deck / GitHub Repository URL", "https://github.com/pragyan-ai/agentic-curriculum-2026")

        if st.form_submit_button("📅 Publish Session to Student Schedules", type="primary"):
            new_session_id = f"TRN-{len(training_df) + 101}"
            session_payload = {
                "session_id": new_session_id,
                "type": s_type,
                "title": s_title,
                "target_depts": ", ".join(s_target_depts),
                "instructor": s_instructor,
                "schedule_date": str(s_date),
                "timing": s_timing,
                "mode": s_mode,
                "location": s_location,
                "curriculum": s_curriculum,
                "meeting_link": s_meet_link,
                "resource_link": s_res_link
            }

            try:
                db_session = get_db_session()
                session_obj = TSModel(**session_payload)
                db_session.add(session_obj)
                db_session.commit()
                db_session.close()

                # Refresh state
                st.session_state.training_sessions = fetch_table_as_df(TrainingSessionModel).rename(columns={
                    "session_id": "Session_ID", "type": "Type", "title": "Title",
                    "target_depts": "Target_Depts", "instructor": "Instructor",
                    "schedule_date": "Schedule_Date", "timing": "Timing", "mode": "Mode",
                    "location": "Location", "curriculum": "Curriculum",
                    "meeting_link": "Meeting_Link", "resource_link": "Resource_Link"
                })
                st.success(f"{s_type} **'{s_title}'** has been published to student calendars!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to record training session: {e}")

    st.markdown("---")
    st.subheader("📚 Scheduled Training & Upskilling Sessions")
    if not training_df.empty:
        st.dataframe(training_df[["Session_ID", "Type", "Title", "Instructor", "Schedule_Date", "Mode", "Location"]], use_container_width=True, hide_index=True)

# =========================================================
# TAB 5: RECRUITER REGISTRATION & ACCESS APPROVALS
# =========================================================
with tab_approvals:
    st.subheader("🏢 Corporate Recruiting Partner Account Authorizations")
    st.caption("Review corporate registration requests, authorize credentials, or flag pending employer verifications.")

    if companies_df.empty:
        st.info("No corporate partner accounts registered in the database.")
    else:
        pending_companies = companies_df[companies_df["Status"] == "Pending"]

        if pending_companies.empty:
            st.success("✅ All registered corporate partner accounts are reviewed and authorized.")
        else:
            st.markdown(f"**Pending Authorizations ({len(pending_companies)}):**")
            for idx, comp_row in pending_companies.iterrows():
                with st.container(border=True):
                    c_col1, c_col2, c_col3, c_col4 = st.columns([3, 2, 2, 2])
                    c_col1.markdown(f"🏢 **{comp_row.get('Company', 'Company')}**")
                    c_col1.caption(f"Email: `{comp_row.get('Email', 'N/A')}`")

                    c_col2.markdown(f"**Domain:** {comp_row.get('Domain', 'General')}")
                    c_col3.markdown(f"**Projected Openings:** {comp_row.get('Openings', 5)}")

                    btn_app, btn_rej = c_col4.columns(2)
                    if btn_app.button("Approve", key=f"btn_app_{idx}", type="primary"):
                        db_update_company_status(comp_row["Company"], "Approved")
                        st.session_state.companies = fetch_table_as_df(CompanyModel).rename(columns={
                            "company": "Company", "domain": "Domain", "email": "Email",
                            "status": "Status", "openings": "Openings"
                        })
                        st.success(f"Approved {comp_row['Company']}!")
                        st.rerun()

                    if btn_rej.button("Reject", key=f"btn_rej_{idx}"):
                        db_update_company_status(comp_row["Company"], "Rejected")
                        st.session_state.companies = fetch_table_as_df(CompanyModel).rename(columns={
                            "company": "Company", "domain": "Domain", "email": "Email",
                            "status": "Status", "openings": "Openings"
                        })
                        st.warning(f"Rejected {comp_row['Company']}.")
                        st.rerun()

        st.markdown("---")
        st.subheader("📑 Master Corporate Partners Roster")
        st.dataframe(companies_df, use_container_width=True, hide_index=True)

# =========================================================
# TAB 6: DIRECTORATE TEAM & ESCALATION DIRECTORY
# =========================================================
with tab_directory:
    st.subheader("👥 Placement Cell Directorate & Escalation Hierarchy")
    st.markdown("""
    The Training and Placement Directorate operates under a centralized executive governance structure:
    """)

    col_dir1, col_dir2 = st.columns(2)

    with col_dir1:
        with st.container(border=True):
            st.markdown("### 👔 Directorate Leadership")
            st.markdown("""
            * **Head - Training & Placement:** Dr. S. Ramanujan
              - 📧 `placement.head@pragyan.edu` | 📞 +91-98765-43210
            * **Lead - Corporate Relations & Marquee Drives:** Ms. Meera Kulkarni
              - 📧 `corporate.relations@pragyan.edu` | 📞 +91-98765-43211
            * **Coordinator - Industry Partnerships & MOUs:** Prof. Rajesh Nair
              - 📧 `partnerships@pragyan.edu` | 📞 +91-98765-43212
            """)

    with col_dir2:
        with st.container(border=True):
            st.markdown("### 🎓 Department Faculty Placement Coordinators")
            st.markdown("""
            * **Computing & AI (CSE / AIML / AIDS / ISE):** Prof. Anitha Rao (`tpo.cse@pragyan.edu`)
            * **Circuit Branches (ECE / EEE):** Prof. Harish Bhat (`tpo.ece@pragyan.edu`)
            * **Mechanical, EV & Robotics:** Prof. Suresh Hegde (`tpo.mech@pragyan.edu`)
            * **Infrastructure & BioTech:** Prof. Lakshmi Varma (`tpo.civil@pragyan.edu`)
            """)
