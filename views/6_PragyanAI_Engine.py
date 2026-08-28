import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from src.database import (
    get_all_users_df,
    update_user_status,
    fetch_table_as_df,
    StudentModel,
    DriveModel,
    RecruiterFeedbackModel,
    TrainingSessionModel
)
from src.chat_widget import render_chat_interface

# ----------------------------------------------------
# 1. PAGE HEADER & METRICS INITIALIZATION
# ----------------------------------------------------
st.title("⚡ PragyanAI Engine — Telemetry & Governance Directorate")
st.caption("Central AI intelligence node: manage RBAC approvals, evaluate 5-axis competency radars, analyze recruiter skill gaps, and schedule interventions.")

tab_approvals, tab_radar, tab_gaps, tab_interventions, tab_copilot = st.tabs([
    "🛡️ Access & Account Approvals",
    "🎯 5-Axis Competency Radar",
    "🔍 Recruiter Gap Analysis",
    "🛠️ Curriculum Interventions",
    "💬 Governance Copilot"
])

# ----------------------------------------------------
# TAB 1: USER REGISTRATIONS & RBAC APPROVAL WORKFLOW
# ----------------------------------------------------
with tab_approvals:
    st.subheader("👥 Institutional User Registration & Role Governance")
    st.caption("Review incoming signup requests, inspect claimed credentials, and grant authenticated institutional access.")

    users_df = get_all_users_df()

    if users_df.empty:
        st.info("No user records discovered in the authorization registry.")
    else:
        pending_users = users_df[users_df["status"] == "Pending"]
        
        st.markdown(f"#### ⏳ Pending Approval Queue ({len(pending_users)} Requests)")
        
        if pending_users.empty:
            st.success("✅ All user registration requests have been vetted and approved.")
        else:
            for _, user_row in pending_users.iterrows():
                with st.expander(f"👤 {user_row['full_name']} — Requested: {user_row['role']} (@{user_row['username']})", expanded=True):
                    c1, c2, c3 = st.columns([2, 2, 2])
                    c1.write(f"**Email:** `{user_row['email']}`")
                    c1.write(f"**Organization / Branch:** `{user_row.get('organization_or_dept', 'N/A')}`")
                    c2.write(f"**Application Timestamp:** `{user_row.get('created_at', 'Recent')}`")
                    c2.write(f"**Current Gate Status:** `{user_row['status']}`")

                    admin_name = st.session_state.get("authenticated_user", {}).get("username", "PragyanAI Admin")
                    
                    btn_approve = c3.button("✅ Authorize Access", key=f"app_{user_row['id']}", type="primary", use_container_width=True)
                    btn_reject = c3.button("❌ Deny Request", key=f"rej_{user_row['id']}", use_container_width=True)

                    if btn_approve:
                        success, msg = update_user_status(user_row['id'], "Approved", approved_by_name=admin_name)
                        if success:
                            st.success(msg)
                            st.rerun()
                    if btn_reject:
                        success, msg = update_user_status(user_row['id'], "Rejected", approved_by_name=admin_name)
                        if success:
                            st.warning(msg)
                            st.rerun()

        st.markdown("---")
        st.markdown("#### 📋 Complete User Directory & Authorization Matrix")
        
        col_f1, col_f2 = st.columns([2, 1])
        search_user = col_f1.text_input("🔍 Search user by name, username, or email:")
        status_filter = col_f2.selectbox("Filter Status:", ["All", "Approved", "Pending", "Rejected"])
        
        filtered_users = users_df.copy()
        if search_user:
            filtered_users = filtered_users[
                filtered_users["full_name"].str.contains(search_user, case=False, na=False) |
                filtered_users["username"].str.contains(search_user, case=False, na=False) |
                filtered_users["email"].str.contains(search_user, case=False, na=False)
            ]
        if status_filter != "All":
            filtered_users = filtered_users[filtered_users["status"] == status_filter]

        display_cols = ["id", "username", "full_name", "email", "role", "organization_or_dept", "status", "approved_by"]
        st.dataframe(filtered_users[display_cols], use_container_width=True, hide_index=True)


# ----------------------------------------------------
# TAB 2: 5-AXIS COMPETENCY RADAR TELEMETRY
# ----------------------------------------------------
with tab_radar:
    st.subheader("🎯 Multi-Department Competency Index & Radar Telemetry")
    st.caption("Synthesizes evaluated cohorts across 5 dimensions: Core Problem Solving, System Design, Applied AI/ML, Hardware/Embedded, and Enterprise Readiness.")

    students_df = st.session_state.get("students", pd.DataFrame())

    if students_df.empty:
        st.info("No student telemetry found. Ensure CSV records are loaded.")
    else:
        # Department Selection Filter
        departments = sorted(students_df["Dept"].dropna().unique().tolist())
        selected_dept = st.selectbox("Select Academic Department for Vector Diagnosis:", ["All Engineering Cohorts"] + departments)

        if selected_dept != "All Engineering Cohorts":
            target_df = students_df[students_df["Dept"] == selected_dept]
        else:
            target_df = students_df

        # Calculate synthetic 5-axis telemetry scores based on department profile
        dept_key = selected_dept if selected_dept != "All Engineering Cohorts" else "ALL"
        
        radar_categories = [
            "Problem Solving & DSA",
            "System Architecture & Cloud",
            "Generative AI & Data Eng",
            "Hardware & Embedded Systems",
            "Enterprise Readiness"
        ]

        # Department-specific competency score weights
        score_mapping = {
            "CSE": [92, 88, 82, 60, 89],
            "AIML": [88, 80, 95, 62, 85],
            "AIDS": [86, 78, 92, 55, 84],
            "ISE": [89, 86, 79, 58, 87],
            "ECE": [80, 72, 70, 94, 82],
            "EEE": [76, 68, 65, 88, 79],
            "MECH": [72, 62, 58, 80, 78],
            "ROBOTICS": [82, 75, 84, 91, 80],
            "CIVIL": [70, 58, 52, 65, 75],
            "BIOTECH": [74, 55, 78, 60, 76],
            "ALL": [85, 78, 80, 74, 83]
        }

        current_scores = score_mapping.get(dept_key, [80, 75, 75, 70, 80])

        col_radar, col_metrics = st.columns([3, 2])

        with col_radar:
            # Radar Plotly Figure
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=current_scores + [current_scores[0]],
                theta=radar_categories + [radar_categories[0]],
                fill='toself',
                fillcolor='rgba(37, 99, 235, 0.25)',
                line=dict(color='#2563EB', width=2.5),
                name=selected_dept
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], color="#64748B"),
                    angularaxis=dict(color="#0F172A", rotation=90, direction="clockwise")
                ),
                showlegend=False,
                margin=dict(l=40, r=40, t=30, b=30),
                height=380
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_metrics:
            st.markdown("##### 📊 Competency Telemetry Metrics")
            st.write(f"- **Evaluated Strength:** `{len(target_df):,}` candidates")
            st.write(f"- **Mean Cohort CGPA:** `{target_df['CGPA'].mean():.2f}`")
            placed_ct = len(target_df[target_df["Status"].isin(["Placed", "Selected"])])
            st.write(f"- **Conversion Rate:** `{(placed_ct / len(target_df) * 100) if len(target_df) > 0 else 0:.1f}%`")
            
            st.markdown("---")
            st.markdown("**🎯 Diagnostic Readout:**")
            if current_scores[2] > 85:
                st.success("High proficiency in Generative AI, RAG architectures, and model inference pipelines.")
            elif current_scores[3] > 85:
                st.success("High hardware telemetry: RTOS, bare-metal C, and digital signal processing.")
            else:
                st.info("Balanced enterprise systems and software engineering foundation.")


# ----------------------------------------------------
# TAB 3: RECRUITER GAP ANALYSIS & FEEDBACK
# ----------------------------------------------------
with tab_gaps:
    st.subheader("🔍 Recruiter Evaluator Feedback & Curriculum Gaps")
    st.caption("Aggregated post-drive evaluations submitted by corporate recruiters, indexing explicit technical deficiencies.")

    feedback_df = st.session_state.get("recruiter_feedback", pd.DataFrame())

    if feedback_df.empty:
        st.info("No recruiter feedback logs recorded yet.")
    else:
        # Summary KPI Cards
        avg_rating = feedback_df["Overall_Rating"].mean() if "Overall_Rating" in feedback_df.columns else 4.0
        kpi_c1, kpi_c2, kpi_c3 = st.columns(3)
        kpi_c1.metric("Corporate Evaluators Logged", f"{len(feedback_df)}")
        kpi_c2.metric("Mean Recruiter Rating", f"{avg_rating:.2f} / 5.0")
        kpi_c3.metric("Evaluated Sectors", f"{feedback_df['Company'].nunique()} Organizations")

        st.markdown("---")

        for _, fb in feedback_df.iterrows():
            with st.container():
                st.markdown(f"#### 🏢 {fb.get('Company', 'Partner')} — Evaluator: *{fb.get('Evaluator', 'Recruiter')}*")
                st.caption(f"Departments Audited: `{fb.get('Dept_Evaluated', 'All')}` • Rating: ⭐ **{fb.get('Overall_Rating', 4.0)}/5.0**")
                
                c_str, c_gap, c_fix = st.columns(3)
                with c_str:
                    st.success(f"**💪 Strong Areas:**\n{fb.get('Strong_Areas', 'N/A')}")
                with c_gap:
                    st.error(f"**⚠️ Observed Gaps:**\n{fb.get('Observed_Gaps', 'N/A')}")
                with c_fix:
                    st.info(f"**🛠️ Recommended Fix:**\n{fb.get('Recommended_Curriculum_Fixes', 'N/A')}")
                st.markdown("---")


# ----------------------------------------------------
# TAB 4: CURRICULUM INTERVENTIONS & BOOTCAMPS
# ----------------------------------------------------
with tab_interventions:
    st.subheader("🛠️ Skill Acceleration Bootcamps & Guest Lectures")
    st.caption("Active remedial training schedules deployed by PragyanAI to resolve identified recruiter skill gaps.")

    training_df = st.session_state.get("training_sessions", pd.DataFrame())

    if training_df.empty:
        st.info("No training sessions currently scheduled.")
    else:
        for _, tr in training_df.iterrows():
            with st.expander(f"📌 [{tr.get('Type', 'Bootcamp')}] {tr.get('Title', 'Session')} — {tr.get('Instructor', 'Lead')}", expanded=True):
                col_t1, col_t2 = st.columns(2)
                col_t1.write(f"📅 **Date & Time:** `{tr.get('Schedule_Date', 'TBD')} ({tr.get('Timing', '')})`")
                col_t1.write(f"📍 **Venue / Mode:** `{tr.get('Location', tr.get('Mode', 'Hybrid'))}`")
                col_t1.write(f"🎯 **Target Branches:** `{tr.get('Target_Depts', 'All')}`")
                
                col_t2.write(f"📖 **Curriculum Scope:**\n{tr.get('Curriculum', 'Core hands-on problem solving.')}")
                if tr.get('Meeting_Link') and tr.get('Meeting_Link') != "N/A":
                    col_t2.markdown(f"🔗 [Join Live Session]({tr.get('Meeting_Link')})")
                if tr.get('Resource_Link'):
                    col_t2.markdown(f"📚 [Curriculum Resources & Code]({tr.get('Resource_Link')})")


# ----------------------------------------------------
# TAB 5: GOVERNANCE COPILOT
# ----------------------------------------------------
with tab_copilot:
    render_chat_interface(user_role="PragyanAI Engine")
