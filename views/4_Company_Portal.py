import streamlit as st
import pandas as pd
import plotly.express as px

from src.chat_widget import render_chat_interface
from src.database import (
    db_add_company,
    fetch_table_as_df,
    CompanyModel,
    RecruiterFeedbackModel,
    RecruiterFeedbackModel as RFModel,
    get_db_session
)

st.title("🏢 Hiring Partner & Corporate Talent Acquisition Hub")
st.caption("Discover verified student talent, analyze campus cohort demographics, submit requisitions, and provide feedback on technical skill gaps.")

# ---------------------------------------------------------
# 1. DATA PREPARATION & STATE VERIFICATION
# ---------------------------------------------------------
students_df = st.session_state.get("students", pd.DataFrame())
companies_df = st.session_state.get("companies", pd.DataFrame())
drives_df = st.session_state.get("drives", pd.DataFrame())
feedback_df = st.session_state.get("recruiter_feedback", pd.DataFrame())

if students_df.empty:
    st.info("Student records database is currently initializing. Please refresh shortly.")
    st.stop()

# Talent Pool Metrics
total_talent = len(students_df)
available_talent = len(students_df[students_df["Status"].isin(["Not Placed", "In Progress", "None"])])
avg_cgpa = float(students_df["CGPA"].mean()) if not students_df.empty else 0.0
verified_passports = len(students_df[students_df["CGPA"] >= 7.5])

# Metric Banner
m1, m2, m3, m4 = st.columns(4)
m1.metric("Campus Talent Pool", f"{total_talent:,}")
m2.metric("Available Candidates", f"{available_talent:,}", delta="Ready for Hiring", delta_color="normal")
m3.metric("Cohort Mean CGPA", f"{avg_cgpa:.2f}")
m4.metric("Pragyan Verified Honors (≥7.5)", f"{verified_passports:,}")

st.markdown("---")

# ---------------------------------------------------------
# 2. RECRUITER WORKSPACE TABS
# ---------------------------------------------------------
tab_filter, tab_analytics, tab_chat, tab_feedback, tab_register = st.tabs([
    "🔍 Candidate Discovery Engine",
    "📊 Talent Pool Analytics",
    "💬 Recruiter AI Copilot",
    "📝 Post-Drive Recruiter Feedback",
    "🏢 Corporate Partner Registration"
])

# =========================================================
# TAB 1: CANDIDATE DISCOVERY & ADVANCED FILTER ENGINE
# =========================================================
with tab_filter:
    st.subheader("🔍 Targeted Candidate Discovery & Multi-Parameter Filter")
    st.caption("Filter students across academic benchmarks, verified skill frameworks, and departmental cohorts.")

    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    with f_col1:
        cgpa_cutoff = st.slider("Minimum CGPA Cutoff:", 0.0, 10.0, 7.5, 0.1)

    with f_col2:
        all_depts = sorted(students_df["Dept"].dropna().unique())
        selected_depts = st.multiselect("Academic Departments:", all_depts, default=["CSE", "AIML", "ISE"] if all(d in all_depts for d in ["CSE", "AIML", "ISE"]) else all_depts[:3])

    with f_col3:
        status_filter = st.multiselect("Placement Status:", students_df["Status"].dropna().unique(), default=["Not Placed"] if "Not Placed" in students_df["Status"].values else students_df["Status"].dropna().unique())

    with f_col4:
        grad_years = sorted(students_df["Grad_Year"].dropna().unique(), reverse=True)
        selected_years = st.multiselect("Graduation Year:", grad_years, default=grad_years)

    s_col1, s_col2 = st.columns(2)
    with s_col1:
        skill_keyword = st.text_input("Skill / Framework Keyword (e.g. Python, PyTorch, Embedded C, Docker):", "")
    with s_col2:
        role_keyword = st.text_input("Aspiration / Dream Role Match (e.g. AI Engineer, Backend, Firmware):", "")

    # Execute dynamic filtering
    matched_candidates = students_df[
        (students_df["CGPA"] >= cgpa_cutoff) &
        (students_df["Dept"].isin(selected_depts)) &
        (students_df["Status"].isin(status_filter)) &
        (students_df["Grad_Year"].isin(selected_years))
    ].copy()

    if skill_keyword.strip():
        matched_candidates = matched_candidates[
            matched_candidates["Skills"].str.contains(skill_keyword.strip(), case=False, na=False)
        ]

    if role_keyword.strip():
        matched_candidates = matched_candidates[
            matched_candidates["Dream_Roles"].str.contains(role_keyword.strip(), case=False, na=False)
        ]

    st.markdown("---")
    st.markdown(f"#### 📋 Matching Verified Candidates ({len(matched_candidates):,} Found)")

    if matched_candidates.empty:
        st.warning("No candidates match the specified filter constraints. Try broadening the CGPA cutoff or skill criteria.")
    else:
        display_talent_cols = [
            "ID", "Name", "Dept", "Grad_Year", "CGPA", "Skills",
            "Dream_Roles", "Salary_Expected_LPA", "Status", "Linkedin", "Github"
        ]
        available_display_cols = [c for c in display_talent_cols if c in matched_candidates.columns]

        st.dataframe(
            matched_candidates[available_display_cols].sort_values(by="CGPA", ascending=False),
            use_container_width=True,
            hide_index=True
        )

        csv_shortlist = matched_candidates[available_display_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Shortlisted Candidates Roster (CSV)",
            data=csv_shortlist,
            file_name="shortlisted_campus_talent.csv",
            mime="text/csv",
            type="primary"
        )

# =========================================================
# TAB 2: TALENT POOL DEMOGRAPHICS & ANALYTICS
# =========================================================
with tab_analytics:
    st.subheader("📊 Campus Cohort Demographics & Academic Distribution")

    col_ta1, col_ta2 = st.columns(2)

    with col_ta1:
        fig_dept_box = px.box(
            students_df,
            x="Dept",
            y="CGPA",
            color="Dept",
            title="CGPA Performance Spread across Academic Departments",
            points="outliers",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_dept_box, use_container_width=True)

    with col_ta2:
        status_counts = students_df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_avail_pie = px.pie(
            status_counts,
            names="Status",
            values="Count",
            title="Current Talent Availability & Placement Ratio",
            hole=0.4,
            color_discrete_sequence=["#10B981", "#3B82F6", "#EF4444", "#F59E0B"]
        )
        st.plotly_chart(fig_avail_pie, use_container_width=True)

    col_ta3, col_ta4 = st.columns(2)

    with col_ta3:
        if "Package_LPA" in students_df.columns:
            placed_subset = students_df[students_df["Status"].isin(["Placed", "Selected"])]
            if not placed_subset.empty:
                fig_comp_bar = px.histogram(
                    placed_subset,
                    x="Package_LPA",
                    nbins=12,
                    title="Compensation Distribution of Placed Cohort (LPA)",
                    color_discrete_sequence=["#6366F1"]
                )
                st.plotly_chart(fig_comp_bar, use_container_width=True)
            else:
                st.info("No salary telemetry available for compensation histogram.")

    with col_ta4:
        dept_counts = students_df["Dept"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Enrollment"]
        fig_dept_dist = px.bar(
            dept_counts,
            x="Enrollment",
            y="Department",
            orientation="h",
            title="Student Headcount Distribution by Department",
            text="Enrollment",
            color="Enrollment",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_dept_dist, use_container_width=True)

# =========================================================
# TAB 3: RECRUITER AI COPILOT
# =========================================================
with tab_chat:
    render_chat_interface("Hiring Partner")

# =========================================================
# TAB 4: POST-DRIVE RECRUITER FEEDBACK & GAP ASSESSMENT
# =========================================================
with tab_feedback:
    st.subheader("📝 Post-Drive Recruiter Assessment & Curriculum Feedback")
    st.caption("Submit your evaluation of candidate preparedness to help the Placement Directorate and academic boards refine coursework and bootcamps.")

    approved_comp_names = sorted(companies_df["Company"].dropna().unique().tolist()) if not companies_df.empty else ["Google", "Qualcomm", "NVIDIA", "Microsoft", "Other"]

    with st.form("recruiter_feedback_submission_form"):
        col_fb1, col_fb2 = st.columns(2)

        with col_fb1:
            fb_company = col_fb1.selectbox("Recruiting Organization:", approved_comp_names)
            fb_evaluator = col_fb1.text_input("Evaluator Name / Designation:", "Lead Technical Hiring Manager")
            fb_drive_id = col_fb1.text_input("Associated Drive ID (Optional):", "DRV-001")

        with col_fb2:
            fb_depts = col_fb2.multiselect(
                "Departments Evaluated during Drive:",
                ["CSE", "AIML", "AIDS", "ISE", "ECE", "EEE", "MECH", "ROBOTICS", "CIVIL", "BIOTECH"],
                default=["CSE", "AIML"]
            )
            fb_rating = col_fb2.slider("Overall Cohort Preparedness Score (1.0 to 5.0):", 1.0, 5.0, 4.2, 0.1)

        fb_strengths = st.text_area(
            "Observed Candidate Strengths:",
            "Strong core computer science fundamentals, clean syntax in Python/C++, and effective communication during initial problem decomposition."
        )

        fb_gaps = st.text_area(
            "Identified Technical Gaps & Deficiencies:",
            "Candidates struggled with low-level concurrency locks, asynchronous thread safety, distributed cache invalidation (Redis), and dry-running boundary invariants on paper."
        )

        fb_fixes = st.text_area(
            "Actionable Recommendations for Academic Curriculum / Bootcamps:",
            "Conduct hands-on weekend bootcamps on Multi-threaded System Design, Docker containerized microservices, and live whiteboard debugging sessions."
        )

        if st.form_submit_button("🚀 Submit Evaluator Report to Placement Directorate", type="primary"):
            if not fb_depts:
                st.error("Please select at least one evaluated department.")
            else:
                feedback_payload = {
                    "company": fb_company,
                    "drive_id": fb_drive_id,
                    "evaluator": fb_evaluator,
                    "dept_evaluated": ", ".join(fb_depts),
                    "overall_rating": float(fb_rating),
                    "strong_areas": fb_strengths,
                    "observed_gaps": fb_gaps,
                    "recommended_curriculum_fixes": fb_fixes
                }

                try:
                    db_session = get_db_session()
                    fb_obj = RFModel(**feedback_payload)
                    db_session.add(fb_obj)
                    db_session.commit()
                    db_session.close()

                    st.session_state.recruiter_feedback = fetch_table_as_df(RecruiterFeedbackModel).rename(columns={
                        "company": "Company", "drive_id": "Drive_ID", "evaluator": "Evaluator",
                        "dept_evaluated": "Dept_Evaluated", "overall_rating": "Overall_Rating",
                        "strong_areas": "Strong_Areas", "observed_gaps": "Observed_Gaps",
                        "recommended_curriculum_fixes": "Recommended_Curriculum_Fixes"
                    })

                    st.success(f"Evaluator report for **{fb_company}** has been committed to the database. The AI Remediation Engine has indexed your feedback.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to submit feedback: {e}")

    st.markdown("---")
    st.subheader("📑 Previously Submitted Recruiter Assessments")
    if not feedback_df.empty:
        st.dataframe(feedback_df, use_container_width=True, hide_index=True)
    else:
        st.info("No prior recruiter feedback records found.")

# =========================================================
# TAB 5: CORPORATE PARTNER REGISTRATION
# =========================================================
with tab_register:
    st.subheader("🏢 Register New Hiring Partner Organization")
    st.caption("Submit your company details for Placement Directorate authorization to publish drives and access unredacted student portfolios.")

    with st.form("company_signup_form"):
        col_reg1, col_reg2 = st.columns(2)

        with col_reg1:
            new_comp_name = col_reg1.text_input("Organization Name (Legal Entity):", "")
            new_comp_domain = col_reg1.selectbox(
                "Industry Sector / Domain:",
                [
                    "Tier-1 Tech & Cloud Infrastructure",
                    "AI, Generative Systems & Big Data",
                    "Semiconductors, VLSI & Embedded",
                    "Automotive, EV & Robotics",
                    "FinTech, Banking & Quant",
                    "Enterprise IT, Consulting & Systems",
                    "Aerospace, Energy & Industrial",
                    "HealthTech, BioTech & Consumer Tech"
                ]
            )

        with col_reg2:
            new_comp_email = col_reg2.text_input("Corporate HR / Campus Recruiter Email:", "")
            new_comp_openings = col_reg2.number_input("Anticipated Campus Hiring Openings:", 1, 500, 10)

        if st.form_submit_button("Submit Registration for Placement Head Authorization", type="primary"):
            if not new_comp_name.strip() or not new_comp_email.strip():
                st.error("Please enter a valid company name and recruiter email.")
            else:
                company_payload = {
                    "company": new_comp_name.strip(),
                    "domain": new_comp_domain,
                    "email": new_comp_email.strip(),
                    "status": "Pending",
                    "openings": int(new_comp_openings)
                }

                try:
                    db_add_company(company_payload)

                    st.session_state.companies = fetch_table_as_df(CompanyModel).rename(columns={
                        "company": "Company", "domain": "Domain", "email": "Email",
                        "status": "Status", "openings": "Openings"
                    })

                    st.success(f"Registration for **{new_comp_name}** has been submitted! The Placement Directorate will review and activate your account.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to submit company registration: {e}")
                    
