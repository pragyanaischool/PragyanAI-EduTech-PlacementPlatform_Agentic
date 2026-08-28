import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from src.chat_widget import render_chat_interface
from src.rag_engine import rag_resume_vs_jd_analysis
from src.pdf_generator import generate_student_offer_pdf
from src.database import (
    db_add_or_update_student,
    db_add_interview_experience,
    fetch_table_as_df,
    StudentModel,
    InterviewExperienceModel
)

st.title("👩‍🎓 Student Career Hub, RAG Analyzer & Experience Terminal")
st.caption("Manage your profile, analyze JD compatibility, record interview debriefs, and track ongoing recruitment drives.")

# ---------------------------------------------------------
# 1. VERIFY SYSTEM STATE & LOAD ACTIVE STUDENT
# ---------------------------------------------------------
if "students" not in st.session_state or st.session_state.students.empty:
    st.info("No student records available in the database. Please initialize data.")
    st.stop()

df = st.session_state.students

# Student Selector / Active Session Simulation
student_options = df["ID"] + " - " + df["Name"] + " (" + df["Dept"] + ")"
selected_student_str = st.selectbox("Select Active Student USN:", student_options, index=0)
active_stu_id = selected_student_str.split(" - ")[0].strip()

# Fetch latest active record
curr_student = df[df["ID"] == active_stu_id].iloc[0]

# High-Level Metrics Banner
c1, c2, c3, c4 = st.columns(4)
c1.metric("Academic CGPA", f"{float(curr_student.get('CGPA', 0.0)):.2f}")
c2.metric("Placement Status", str(curr_student.get("Status", "Not Placed")))
pkg_val = float(curr_student.get("Package_LPA", 0.0))
c3.metric("Package Secured", f"₹{pkg_val:.2f} LPA" if curr_student.get("Status") in ["Placed", "Selected"] else "In Process")
readiness_idx = min(int(float(curr_student.get("CGPA", 7.0)) * 10.2), 99)
c4.metric("Pragyan Readiness", f"{readiness_idx}%")

st.markdown("---")

# ---------------------------------------------------------
# 2. MAIN WORKSPACE TABS
# ---------------------------------------------------------
tab_chat, tab_rag, tab_analytics, tab_drives, tab_workshops, tab_debrief, tab_offer, tab_profile = st.tabs([
    "💬 Placement Copilot",
    "🎯 RAG Resume vs. JD",
    "📊 Cohort Analytics",
    "🏢 Active Drives",
    "📅 Workshops & Bootcamps",
    "🎙️ Interview Debrief",
    "📄 Offer Certificate",
    "👤 Career Profile & CV"
])

# =========================================================
# TAB 1: PLACEMENT CHAT COPILOT
# =========================================================
with tab_chat:
    render_chat_interface("Student", user_context={"student_id": active_stu_id})

# =========================================================
# TAB 2: RAG RESUME VS. JOB DESCRIPTION ANALYZER
# =========================================================
with tab_rag:
    st.subheader("🎯 Deep RAG Candidate-to-JD Compatibility Analysis")
    st.caption("Vector similarity analysis comparing your profile, projects, and skills against corporate job descriptions.")

    drives_df = st.session_state.get("drives", pd.DataFrame())
    if drives_df.empty:
        st.warning("No active drives posted currently.")
    else:
        drive_opts = drives_df["Drive_ID"] + " - " + drives_df["Company"] + " (" + drives_df["Role"] + ")"
        sel_drive_str = st.selectbox("Select Target Campus Drive:", drive_opts)
        target_drive_id = sel_drive_str.split(" - ")[0].strip()

        if st.button("Run Deep RAG Match Analysis", type="primary"):
            with st.spinner("Analyzing semantic overlap & skill vector projections..."):
                res = rag_resume_vs_jd_analysis(active_stu_id, target_drive_id)

            m1, m2 = st.columns([1, 2])
            with m1:
                score = res["match_score"]
                st.metric("RAG Match Score", f"{score}%")
                if score >= 75:
                    st.success("Strong Fit for Interview Rounds ✅")
                elif score >= 60:
                    st.warning("Moderate Alignment (Minor Gaps) ⚠️")
                else:
                    st.error("Skill Gap Detected ❌")

            with m2:
                st.info(f"Targeting **{res['role']}** at **{res['company']}**\n\n**Recommendation:** {res['recommendation']}")

            st.markdown("---")
            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown("#### ✅ Matched Competencies & Keywords")
                for s in res["matched_skills"]:
                    st.success(f"✔ {s}")

            with col_r:
                st.markdown("#### ❌ Critical Keyword Gaps & Missing Skills")
                for g in res["missing_skills"]:
                    st.error(f"✖ {g}")

# =========================================================
# TAB 3: COHORT & STUDENT BENCHMARK ANALYTICS
# =========================================================
with tab_analytics:
    st.subheader(f"📊 Benchmarking {curr_student['Name']} vs. {curr_student['Dept']} Department Cohort")
    
    dept_cohort = df[df["Dept"] == curr_student["Dept"]]
    col_a1, col_a2 = st.columns(2)

    with col_a1:
        fig_cgpa = px.histogram(
            dept_cohort,
            x="CGPA",
            nbins=15,
            title=f"CGPA Distribution across {curr_student['Dept']} Cohort",
            color_discrete_sequence=["#3B82F6"]
        )
        fig_cgpa.add_vline(
            x=float(curr_student["CGPA"]),
            line_color="red",
            line_dash="dash",
            annotation_text=f"Your CGPA: {curr_student['CGPA']}"
        )
        st.plotly_chart(fig_cgpa, use_container_width=True)

    with col_a2:
        placed_cohort = df[df["Status"].isin(["Placed", "Selected"])]
        if not placed_cohort.empty:
            fig_salary = px.box(
                placed_cohort,
                x="Dept",
                y="Package_LPA",
                color="Dept",
                title="Placed Salary Spread (LPA) by Department",
                points="outliers"
            )
            st.plotly_chart(fig_salary, use_container_width=True)
        else:
            st.info("No salary telemetry available yet for comparison.")

# =========================================================
# TAB 4: ACTIVE PLACEMENT DRIVES & SESSIONS
# =========================================================
with tab_drives:
    st.subheader("🏢 Active & Upcoming Campus Placement Drives")
    drives_df = st.session_state.get("drives", pd.DataFrame())

    if drives_df.empty:
        st.info("No active campus placement drives scheduled.")
    else:
        for idx, drive in drives_df.iterrows():
            with st.expander(f"📌 {drive.get('Company', 'Company')} — {drive.get('Role', 'Engineering Role')} | CTC: ₹{drive.get('Package_LPA', 0.0)} LPA"):
                c_d1, c_d2 = st.columns(2)
                with c_d1:
                    st.markdown(f"• **Eligibility Cutoff:** Min **{drive.get('Min_CGPA', 0.0)} CGPA**")
                    st.markdown(f"• **Target Branches:** `{drive.get('Eligible_Depts', 'All')}`")
                    st.markdown(f"• **Key Skills:** `{drive.get('Required_Skills', 'Core Engineering')}`")
                    st.markdown(f"• **Drive Date:** `{drive.get('Session_Date', 'TBD')}`")

                with c_d2:
                    app_link = str(drive.get("App_Link", "")).strip()
                    sem_link = str(drive.get("Seminar_Link", "")).strip()
                    ppt_link = str(drive.get("PPT_Link", "")).strip()

                    if app_link and app_link.startswith("http"):
                        st.markdown(f"🔗 **[Official Application Portal]({app_link})**")
                    if sem_link and sem_link.startswith("http"):
                        st.markdown(f"📹 **[Pre-Placement Seminar Link]({sem_link})**")
                    if ppt_link and ppt_link.startswith("http"):
                        st.markdown(f"📄 **[Company Orientation PPT / Brochure]({ppt_link})**")

                st.info(f"**Role Description:** {drive.get('Description', 'Detailed JD posted on portal.')}")

# =========================================================
# TAB 5: WORKSHOPS, BOOTCAMPS & GUEST LECTURES
# =========================================================
with tab_workshops:
    st.subheader("📅 Scheduled Skill Bootcamps & Guest Lectures")
    workshops_df = st.session_state.get("training_sessions", pd.DataFrame())

    if workshops_df.empty:
        st.info("No training sessions scheduled at this moment.")
    else:
        for idx, s in workshops_df.iterrows():
            with st.expander(f"🛠️ [{s.get('Type', 'Training')}] {s.get('Title', 'Session')} (Date: {s.get('Schedule_Date', 'TBD')})"):
                col_w1, col_w2 = st.columns(2)
                with col_w1:
                    st.write(f"• **Instructor / Speaker:** {s.get('Instructor', 'Faculty Lead')}")
                    st.write(f"• **Target Branches:** `{s.get('Target_Depts', 'All')}`")
                    st.write(f"• **Timing:** {s.get('Timing', 'TBD')} ({s.get('Mode', 'Hybrid')})")
                    st.write(f"• **Location / Room:** {s.get('Location', 'Main Auditorium')}")

                with col_w2:
                    m_link = str(s.get("Meeting_Link", "")).strip()
                    r_link = str(s.get("Resource_Link", "")).strip()
                    if m_link and m_link.startswith("http"):
                        st.markdown(f"📹 **[Join Live Stream / Meeting]({m_link})**")
                    if r_link and r_link.startswith("http"):
                        st.markdown(f"📚 **[Curriculum Repository & Notes]({r_link})**")

                st.markdown("#### 📖 Curriculum Modules Covered:")
                st.info(s.get("Curriculum", "Modules announced in session."))
                st.button(f"RSVP / Add to Calendar", key=f"rsvp_btn_{s.get('Session_ID', idx)}")

# =========================================================
# TAB 6: MULTIMEDIA INTERVIEW DEBRIEF & VOICE NOTES
# =========================================================
with tab_debrief:
    st.subheader("🎙️ Post-Interview Multimedia Experience Debrief")
    st.caption("Contribute technical interview questions, round structures, and voice feedback to the institutional knowledge base.")

    drives_df = st.session_state.get("drives", pd.DataFrame())
    comp_choices = sorted(drives_df["Company"].dropna().unique()) if not drives_df.empty else ["Google", "Qualcomm", "NVIDIA", "Other"]

    with st.form("student_debrief_form"):
        col_db1, col_db2 = st.columns(2)
        with col_db1:
            debrief_company = col_db1.selectbox("Interviewed Organization", comp_choices)
        with col_db2:
            debrief_role = col_db2.text_input("Interviewed Role Title", "Associate Software Engineer")

        st.markdown("#### 📸 Photo & 🎙️ Voice Notes")
        cm1, cm2 = st.columns(2)
        with cm1:
            st.write("**Candidate Photo:**")
            cam_pic = st.camera_input("Take Live Photo (Optional)")
            up_pic = st.file_uploader("Or Upload Picture (JPG/PNG)", type=["jpg", "png", "jpeg"], key="pic_up")
        with cm2:
            st.write("**Voice Notes / Speech Feedback:**")
            audio_rec = st.audio_input("Record Voice Notes Directly")
            audio_up = st.file_uploader("Or Upload Audio File (MP3/WAV)", type=["mp3", "wav", "m4a"], key="aud_up")

        rounds_summary = st.text_area(
            "What occurred across each round? (Coding, LLD, HR, System Design)",
            "Round 1: 2 Graph DP coding problems.\nRound 2: Low-Level System Design (LRU Cache concurrency).\nRound 3: Behavioral & Culture Fit."
        )

        col_sk1, col_sk2 = st.columns(2)
        with col_sk1:
            excelled = col_sk1.text_area("What skills/topics did you excel at?", "Graph DFS/BFS, Async Python, and Clean Code.")
        with col_sk2:
            bottlenecks = col_sk2.text_area("What was the toughest question / bottleneck faced?", "Concurrency locks, race conditions, and distributed caching.")

        advice = st.text_area(
            "🎯 Secret Sauce & Advice to Crack this Company (For Juniors):",
            "1. Dry run edge cases on paper before typing code.\n2. State time and space complexity invariants out loud."
        )

        if st.form_submit_button("🚀 Submit Debrief & Sync with Knowledge Base"):
            new_exp_id = f"EXP-{int(datetime.now().timestamp()) % 100000}"
            exp_payload = {
                "exp_id": new_exp_id,
                "student_id": active_stu_id,
                "student_name": str(curr_student.get("Name", "Candidate")),
                "dept": str(curr_student.get("Dept", "General")),
                "company": debrief_company,
                "role": debrief_role,
                "rounds_faced": rounds_summary,
                "skills_excelled": excelled,
                "challenges_faced": bottlenecks,
                "advice_to_crack": advice,
                "photo_attached": bool(cam_pic or up_pic),
                "audio_attached": bool(audio_rec or audio_up),
                "timestamp": datetime.now().strftime("%Y-%m-%d")
            }

            try:
                db_add_interview_experience(exp_payload)
                st.session_state.interview_experiences = fetch_table_as_df(InterviewExperienceModel).rename(columns={
                    "exp_id": "Exp_ID", "student_id": "Student_ID", "student_name": "Student_Name",
                    "dept": "Dept", "company": "Company", "role": "Role",
                    "rounds_faced": "Rounds_Faced", "skills_excelled": "Skills_Excelled",
                    "challenges_faced": "Challenges_Faced", "advice_to_crack": "Advice_To_Crack",
                    "photo_attached": "Photo_Attached", "audio_attached": "Audio_Attached",
                    "timestamp": "Timestamp"
                })
                st.success("Thank you! Your interview debrief and feedback have been saved to the database.")
            except Exception as e:
                st.error(f"Failed to record debrief: {e}")

# =========================================================
# TAB 7: OFFICIAL OFFER CONFIRMATION CERTIFICATE
# =========================================================
with tab_offer:
    st.subheader("📄 Official Institutional Placement Certificate")
    if curr_student.get("Status") in ["Placed", "Selected"]:
        st.success(f"Congratulations! You have verified placement with **{curr_student.get('Company')}** as **{curr_student.get('Role')}** at **₹{curr_student.get('Package_LPA')} LPA**.")
        
        try:
            pdf_offer = generate_student_offer_pdf(curr_student.to_dict())
            st.download_button(
                label="📥 Download Verified Offer Confirmation Certificate (PDF)",
                data=pdf_offer,
                file_name=f"Placement_Certificate_{curr_student['ID']}.pdf",
                mime="application/pdf",
                type="primary"
            )
        except Exception as e:
            st.error(f"Error generating PDF certificate: {e}")
    else:
        st.info("Your official placement certificate will be unlocked here as soon as an offer is recorded in the institutional ledger.")

# =========================================================
# TAB 8: CAREER PROFILE, RESUME & SKILL PASSPORT
# =========================================================
with tab_profile:
    st.subheader("👤 Candidate Credentials & Skill Passport")
    st.caption("Update your technical skills, portfolio links, and academic scores to sync with recruiter discovery engines.")

    with st.form("student_profile_edit_form"):
        p_c1, p_c2, p_c3 = st.columns(3)
        with p_c1:
            p_name = p_c1.text_input("Full Name", value=str(curr_student.get("Name", "")))
            p_dept = p_c1.selectbox(
                "Department",
                ["CSE", "AIML", "AIDS", "ISE", "ECE", "EEE", "MECH", "ROBOTICS", "CIVIL", "BIOTECH"],
                index=["CSE", "AIML", "AIDS", "ISE", "ECE", "EEE", "MECH", "ROBOTICS", "CIVIL", "BIOTECH"].index(curr_student.get("Dept", "CSE"))
                if curr_student.get("Dept") in ["CSE", "AIML", "AIDS", "ISE", "ECE", "EEE", "MECH", "ROBOTICS", "CIVIL", "BIOTECH"] else 0
            )
            p_year = p_c1.selectbox("Graduation Year", [2024, 2025, 2026, 2027], index=1)

        with p_c2:
            p_cgpa = p_c2.number_input("Cumulative CGPA", 0.0, 10.0, float(curr_student.get("CGPA", 8.0)), 0.01)
            p_roles = p_c2.text_input("Dream Job Roles", value=str(curr_student.get("Dream_Roles", "")))
            p_companies = p_c2.text_input("Dream Target Companies", value=str(curr_student.get("Dream_Companies", "")))

        with p_c3:
            p_salary = p_c3.number_input("Expected Salary (LPA)", 0.0, 100.0, float(curr_student.get("Salary_Expected_LPA", 15.0)))
            p_linkedin = p_c3.text_input("LinkedIn Profile URL", value=str(curr_student.get("Linkedin", "")))
            p_github = p_c3.text_input("GitHub Profile URL", value=str(curr_student.get("Github", "")))

        p_skills = st.text_area("Core Skills (Comma separated)", value=str(curr_student.get("Skills", "")))
        p_projects = st.text_area("Key Projects & Architectures", value=str(curr_student.get("Projects", "")))
        p_exp = st.text_area("Internships & Work Experience", value=str(curr_student.get("Experience", "")))

        if st.form_submit_button("💾 Save & Sync Profile with Database"):
            updated_payload = {
                "id": active_stu_id,
                "name": p_name,
                "dept": p_dept,
                "college": str(curr_student.get("College", "Main Campus (Bengaluru)")),
                "grad_year": p_year,
                "cgpa": p_cgpa,
                "skills": p_skills,
                "projects": p_projects,
                "experience": p_exp,
                "linkedin": p_linkedin,
                "github": p_github,
                "dream_roles": p_roles,
                "dream_companies": p_companies,
                "salary_expected_lpa": p_salary,
                "status": str(curr_student.get("Status", "Not Placed")),
                "company": str(curr_student.get("Company", "None")),
                "role": str(curr_student.get("Role", "None")),
                "package_lpa": float(curr_student.get("Package_LPA", 0.0))
            }

            try:
                db_add_or_update_student(updated_payload)
                st.session_state.students = fetch_table_as_df(StudentModel).rename(columns={
                    "id": "ID", "name": "Name", "dept": "Dept", "college": "College", "grad_year": "Grad_Year",
                    "cgpa": "CGPA", "skills": "Skills", "projects": "Projects", "experience": "Experience",
                    "linkedin": "Linkedin", "github": "Github", "dream_roles": "Dream_Roles",
                    "dream_companies": "Dream_Companies", "salary_expected_lpa": "Salary_Expected_LPA",
                    "status": "Status", "company": "Company", "role": "Role", "package_lpa": "Package_LPA"
                })
                st.success("Profile and Skill Passport synchronized with the institutional database.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to update profile: {e}")
                
