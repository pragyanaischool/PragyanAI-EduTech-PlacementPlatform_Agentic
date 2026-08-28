import streamlit as st
import pandas as pd
import struct
import plotly.express as px
from datetime import datetime

from src.db import init_db
from src.chat_widget import render_chat_interface
from src.database import (
    db_update_candidate_stage,
    db_add_or_update_student,
    fetch_table_as_df,
    CandidateStageModel,
    DriveSelectionModel,
    StudentModel,
    get_db_session
)

# ---------------------------------------------------------
# 1. LIVE DATA SYNC & STATE VERIFICATION
# ---------------------------------------------------------
if "students" not in st.session_state or st.session_state.students.empty:
    init_db()

st.title("📋 Placement Team Operations & Candidate Pipeline Ledger")
st.caption("Manage drive-level attendance reconciliation, selection offer commitments, stage-by-stage pipeline progressions, and live candidate tracking.")

# Helper function to unpack raw byte years if encountered from SQLite
def clean_year_val(val):
    if isinstance(val, (bytes, bytearray)):
        try:
            if len(val) == 8:
                return struct.unpack("<q", val)[0]
            elif len(val) == 4:
                return struct.unpack("<i", val)[0]
        except Exception:
            return 2026
    try:
        return int(pd.to_numeric(val, errors="coerce"))
    except Exception:
        return 2026

# Retrieve dataframes from session state
students_df = st.session_state.get("students", pd.DataFrame()).copy()
drives_df = st.session_state.get("drives", pd.DataFrame()).copy()
stages_df = st.session_state.get("candidate_stages", pd.DataFrame()).copy()
selections_df = st.session_state.get("drive_selections", pd.DataFrame()).copy()

if students_df.empty or drives_df.empty:
    st.info("System database is initializing or core data is unavailable. Please check the database initialization.")
    st.stop()

# Clean and normalize students dataframe
students_df.rename(columns={c: c.strip() for c in students_df.columns}, inplace=True)
students_df["Grad_Year"] = students_df["Grad_Year"].apply(clean_year_val).fillna(2026).astype(int)
students_df["CGPA"] = pd.to_numeric(students_df["CGPA"], errors="coerce").fillna(0.0)
students_df["Package_LPA"] = pd.to_numeric(students_df["Package_LPA"], errors="coerce").fillna(0.0)
students_df["Status"] = students_df["Status"].astype(str).str.strip()

# Operational KPI computation
total_candidates = len(students_df)
active_pipeline_cnt = len(stages_df)
offers_extended_cnt = len(students_df[students_df["Status"].isin(["Placed", "Selected"])])
interviewing_cnt = (
    len(stages_df[~stages_df["Current_Round"].str.contains("Selected|Offer", case=False, na=False)])
    if not stages_df.empty and "Current_Round" in stages_df.columns
    else 0
)

# Metrics Banner
m1, m2, m3, m4 = st.columns(4)
m1.metric("Enrolled Batch Roster", f"{total_candidates:,}")
m2.metric("Active Candidates in Pipeline", f"{active_pipeline_cnt:,}")
m3.metric("Live Interview Stages", f"{interviewing_cnt:,}")
m4.metric("Total Offers Committed", f"{offers_extended_cnt:,}", delta="Verified Offers", delta_color="normal")

st.markdown("---")

# ---------------------------------------------------------
# 2. OPERATIONAL WORKSPACE TABS
# ---------------------------------------------------------
tab_postdrive, tab_stages, tab_chat, tab_analytics, tab_roster = st.tabs([
    "🎯 Post-Drive Selection & Attendance",
    "📍 Candidate Stage Progression",
    "💬 Operations AI Copilot",
    "📊 Funnel & Pipeline Analytics",
    "📑 Master Student Ledger"
])

# =========================================================
# TAB 1: POST-DRIVE RECONCILIATION & OFFER ENTRY
# =========================================================
with tab_postdrive:
    st.subheader("🎯 Post-Drive Attendance & Final Offer Reconciliation")
    st.caption("Select a completed campus drive, audit student participation, and commit verified selection offers directly to the master database.")

    drive_options = drives_df["Drive_ID"] + " - " + drives_df["Company"] + " (" + drives_df["Role"] + ")"
    selected_drive_str = st.selectbox("Select Target Completed Drive:", drive_options)
    selected_drive_id = selected_drive_str.split(" - ")[0].strip()

    target_drive = drives_df[drives_df["Drive_ID"] == selected_drive_id].iloc[0]
    comp_name = str(target_drive.get("Company", "Corporate Partner"))
    role_name = str(target_drive.get("Role", "Software Engineer"))
    base_ctc = float(target_drive.get("Package_LPA", 0.0))

    st.info(f"Drive Profile: **{comp_name}** | Role: **{role_name}** | Benchmark CTC: **₹{base_ctc:.2f} LPA** | Eligible Branches: `{target_drive.get('Eligible_Depts', 'All')}`")

    # Filter eligible department candidates or provide complete list
    eligible_depts = [d.strip() for d in str(target_drive.get("Eligible_Depts", "")).split(",") if d.strip()]
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        all_depts = sorted(students_df["Dept"].dropna().unique().tolist())
        default_depts = [d for d in eligible_depts if d in all_depts] or all_depts
        filter_dept_cohort = st.multiselect("Filter Candidate Pool by Department:", all_depts, default=default_depts)
    with col_f2:
        cgpa_filter = st.slider("Filter by Minimum CGPA Cutoff:", 0.0, 10.0, float(target_drive.get("Min_CGPA", 6.0)), 0.1)

    candidate_pool = students_df[
        (students_df["Dept"].isin(filter_dept_cohort)) &
        (students_df["CGPA"] >= cgpa_filter)
    ].copy()

    st.markdown("#### Candidate Verification & Outcome Grid")
    st.caption("Mark check-boxes for attendance and verified selection. Adjust individual package allocations if custom CTC bonuses apply.")

    # Prepare reconciliation matrix data
    edit_rows = []
    for _, s in candidate_pool.iterrows():
        s_id = str(s["ID"])
        # Check existing drive selection record
        existing_sel = selections_df[
            (selections_df["Drive_ID"] == selected_drive_id) &
            (selections_df["Student_ID"] == s_id)
        ] if not selections_df.empty else pd.DataFrame()

        if not existing_sel.empty:
            is_att = bool(existing_sel.iloc[0].get("Attended", False))
            is_sel = existing_sel.iloc[0].get("Selection_Status") in ["Selected", "Placed"]
            offered_pkg = float(existing_sel.iloc[0].get("Offered_CTC_LPA", base_ctc))
        else:
            is_att = False
            is_sel = (str(s.get("Company", "")) == comp_name and s.get("Status") in ["Placed", "Selected"])
            offered_pkg = float(s.get("Package_LPA", base_ctc)) if is_sel else base_ctc

        edit_rows.append({
            "Student_ID": s_id,
            "Name": str(s["Name"]),
            "Dept": str(s["Dept"]),
            "CGPA": float(s["CGPA"]),
            "Attended_Drive": is_att,
            "Offer_Extended": is_sel,
            "Offered_CTC_LPA": offered_pkg,
            "Designation": role_name
        })

    reconcile_df = pd.DataFrame(edit_rows)

    with st.form("post_drive_reconcile_form"):
        edited_table = st.data_editor(
            reconcile_df,
            column_config={
                "Student_ID": st.column_config.TextColumn("USN / Roll No", disabled=True),
                "Name": st.column_config.TextColumn("Student Name", disabled=True),
                "Dept": st.column_config.TextColumn("Dept", disabled=True),
                "CGPA": st.column_config.NumberColumn("CGPA", format="%.2f", disabled=True),
                "Attended_Drive": st.column_config.CheckboxColumn("Attended Session", default=False),
                "Offer_Extended": st.column_config.CheckboxColumn("Offer Extended ✅", default=False),
                "Offered_CTC_LPA": st.column_config.NumberColumn("Allocated CTC (LPA)", format="₹%.2f", min_value=0.0, max_value=150.0),
                "Designation": st.column_config.TextColumn("Job Designation")
            },
            hide_index=True,
            use_container_width=True
        )

        submit_reconciliation = st.form_submit_button("💾 Commit Reconciled Drive Outcomes & Update Student Ledger", type="primary")

        if submit_reconciliation:
            db_session = get_db_session()
            try:
                for _, row in edited_table.iterrows():
                    sid = str(row["Student_ID"])
                    is_selected = bool(row["Offer_Extended"])
                    is_attended = bool(row["Attended_Drive"]) or is_selected
                    pkg_allocated = float(row["Offered_CTC_LPA"]) if is_selected else 0.0
                    desig = str(row["Designation"]) if is_selected else "None"

                    # 1. Update/Add in Drive Selections
                    existing_ds = db_session.query(DriveSelectionModel).filter(
                        DriveSelectionModel.drive_id == selected_drive_id,
                        DriveSelectionModel.student_id == sid
                    ).first()

                    sel_status_label = "Selected" if is_selected else ("Attended" if is_attended else "Absent")

                    if existing_ds:
                        existing_ds.attended = is_attended
                        existing_ds.selection_status = sel_status_label
                        existing_ds.offered_role = desig
                        existing_ds.offered_ctc_lpa = pkg_allocated
                    else:
                        db_session.add(DriveSelectionModel(
                            drive_id=selected_drive_id,
                            company=comp_name,
                            student_id=sid,
                            student_name=str(row["Name"]),
                            dept=str(row["Dept"]),
                            attended=is_attended,
                            selection_status=sel_status_label,
                            offered_role=desig,
                            offered_ctc_lpa=pkg_allocated
                        ))

                    # 2. Update Master Student Model if Offer is Selected
                    if is_selected:
                        stu_record = db_session.query(StudentModel).filter(StudentModel.id == sid).first()
                        if stu_record:
                            stu_record.status = "Placed"
                            stu_record.company = comp_name
                            stu_record.role = desig
                            stu_record.package_lpa = pkg_allocated

                        # 3. Update Pipeline Stage to Offer Extended
                        stage_record = db_session.query(CandidateStageModel).filter(
                            CandidateStageModel.student_id == sid,
                            CandidateStageModel.company == comp_name
                        ).first()

                        if stage_record:
                            stage_record.current_round = "Offer Extended (Selected)"
                            stage_record.next_round_date = "Completed"
                        else:
                            new_stg_id = f"STG-{int(datetime.now().timestamp()) % 100000}-{sid}"
                            db_session.add(CandidateStageModel(
                                stage_id=new_stg_id,
                                student_id=sid,
                                student_name=str(row["Name"]),
                                dept=str(row["Dept"]),
                                company=comp_name,
                                role=desig,
                                current_round="Offer Extended (Selected)",
                                next_round_date="Completed",
                                mode_location=f"{comp_name} Campus HQ"
                            ))

                db_session.commit()

                # Refresh session state
                init_db()

                st.success(f"Drive outcomes for **{comp_name}** committed successfully! Master student ledger & stage pipelines updated.")
                st.rerun()

            except Exception as e:
                db_session.rollback()
                st.error(f"Database commitment failed: {e}")
            finally:
                db_session.close()

# =========================================================
# TAB 2: CANDIDATE STAGE PROGRESSION PIPELINE
# =========================================================
with tab_stages:
    st.subheader("📍 Update Individual Candidate Pipeline Stages")
    st.caption("Log sequential round clearances, schedule subsequent technical juries, and update meeting parameters.")

    with st.form("stage_progression_form"):
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            prog_student_id = col_p1.selectbox("Candidate USN / ID:", students_df["ID"].tolist())
            prog_student = students_df[students_df["ID"] == prog_student_id].iloc[0]
            st.info(f"**{prog_student['Name']}** ({prog_student['Dept']} | CGPA: {prog_student['CGPA']})")

        with col_p2:
            comp_list = sorted(drives_df["Company"].dropna().unique().tolist())
            prog_company = col_p2.selectbox("Recruiting Partner:", comp_list)
            prog_role = col_p2.text_input("Assigned Profile / Role:", "Software Engineer")

        with col_p3:
            prog_round = col_p3.selectbox("Next / Cleared Stage:", [
                "Round 1: Online Coding Cleared",
                "Round 2: Technical Architecture & LLD",
                "Round 3: System Invariants & Live Debugging",
                "Round 4: Leadership & Culture Fit",
                "Offer Extended (Selected)",
                "Eliminated in Round 1",
                "Eliminated in Round 2"
            ])

        col_p4, col_p5 = st.columns(2)
        with col_p4:
            prog_datetime = col_p4.text_input("Scheduled Date & Time:", value=datetime.now().strftime("%Y-%m-%d 10:30 AM"))
        with col_p5:
            prog_location = col_p5.text_input("Mode / Meeting Room / URL:", value="Virtual (Google Meet Room 4)")

        if st.form_submit_button("🚀 Commit Stage Progression", type="primary"):
            stage_payload = {
                "stage_id": f"STG-{int(datetime.now().timestamp()) % 100000}",
                "student_id": prog_student_id,
                "student_name": str(prog_student["Name"]),
                "dept": str(prog_student["Dept"]),
                "company": prog_company,
                "role": prog_role,
                "current_round": prog_round,
                "next_round_date": prog_datetime,
                "mode_location": prog_location
            }

            try:
                db_update_candidate_stage(stage_payload)
                init_db()

                st.success(f"Candidate **{prog_student['Name']}** progression updated to: `{prog_round}` for **{prog_company}**.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to update stage: {e}")

    st.markdown("---")
    st.subheader("📋 Active Candidate Recruitment Pipeline Roster")
    stages_live = st.session_state.get("candidate_stages", pd.DataFrame())
    if not stages_live.empty:
        st.dataframe(stages_live, use_container_width=True, hide_index=True)
    else:
        st.info("No active candidate pipeline stages recorded.")

# =========================================================
# TAB 3: PLACEMENT OPERATIONS AI COPILOT
# =========================================================
with tab_chat:
    render_chat_interface("Placement Team")

# =========================================================
# TAB 4: FUNNEL & PIPELINE ANALYTICS
# =========================================================
with tab_analytics:
    st.subheader("📊 Candidate Pipeline Funnel & Stage Telemetry")
    stages_analytics = st.session_state.get("candidate_stages", pd.DataFrame())

    if stages_analytics.empty:
        st.info("Insufficient pipeline stage data for visualization.")
    else:
        col_fa1, col_fa2 = st.columns(2)

        with col_fa1:
            stage_volume = stages_analytics.groupby("Current_Round")["Student_ID"].count().reset_index()
            stage_volume.columns = ["Pipeline Stage", "Candidate Volume"]
            fig_funnel = px.bar(
                stage_volume.sort_values(by="Candidate Volume", ascending=True),
                x="Candidate Volume",
                y="Pipeline Stage",
                orientation="h",
                title="Candidate Volume by Recruitment Pipeline Stage",
                text="Candidate Volume",
                color="Candidate Volume",
                color_continuous_scale="Teal"
            )
            st.plotly_chart(fig_funnel, use_container_width=True)

        with col_fa2:
            fig_dept_pipe = px.histogram(
                stages_analytics,
                x="Dept",
                color="Company",
                title="Active Candidate Pipeline Distribution across Departments",
                barmode="stack",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            st.plotly_chart(fig_dept_pipe, use_container_width=True)

# =========================================================
# TAB 5: MASTER STUDENT PLACEMENT LEDGER
# =========================================================
with tab_roster:
    st.subheader("📑 Institution Master Student Placement Ledger")
    st.caption("Complete verified institutional ledger with single-click filtering and CSV export.")

    col_r1, col_r2, col_r3 = st.columns(3)
    
    with col_r1:
        depts_unique = sorted(students_df["Dept"].dropna().unique().tolist())
        f_dept = st.multiselect("Filter Dept:", depts_unique, default=depts_unique, key="ros_dept")
    
    with col_r2:
        status_unique = sorted(students_df["Status"].dropna().unique().tolist())
        f_status = st.multiselect("Filter Status:", status_unique, default=status_unique, key="ros_stat")
    
    with col_r3:
        years_unique = sorted(students_df["Grad_Year"].dropna().unique().tolist(), reverse=True)
        f_year = st.multiselect("Graduation Year:", years_unique, default=years_unique, key="ros_yr")

    filtered_roster = students_df[
        (students_df["Dept"].isin(f_dept)) &
        (students_df["Status"].isin(f_status)) &
        (students_df["Grad_Year"].isin(f_year))
    ].copy()

    display_roster_cols = ["ID", "Name", "Dept", "Grad_Year", "CGPA", "Status", "Company", "Role", "Package_LPA", "Skills"]
    available_cols = [c for c in display_roster_cols if c in filtered_roster.columns]

    st.dataframe(
        filtered_roster[available_cols].sort_values(by=["Status", "Package_LPA"], ascending=[True, False]),
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered_roster[available_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Master Placement Ledger (CSV)",
        data=csv_data,
        file_name="master_placement_roster_report.csv",
        mime="text/csv",
        type="primary"
    )
