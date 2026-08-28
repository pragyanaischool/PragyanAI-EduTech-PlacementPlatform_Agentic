import streamlit as st
import plotly.express as px
from src.chat_widget import render_chat_interface
from src.rag_engine import rag_resume_vs_jd_analysis

st.title(" Student Career Hub, Analytics & AI Copilot")

df = st.session_state.students
active_stu_id = st.selectbox("Select Your Student ID for Context:", df["ID"].tolist(), index=0)
curr_student = df[df["ID"] == active_stu_id].iloc[0]

# --- STUDENT ANALYTICS TILES ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current CGPA", curr_student["CGPA"])
col2.metric("Placement Status", curr_student["Status"])
col3.metric("Assigned CTC", f"₹{curr_student['Package_LPA']} LPA" if curr_student["Status"] == "Placed" else "In Progress")
col4.metric("Pragyan Readiness", f"{min(int(curr_student['CGPA'] * 10), 98)}%")

# Tabs with Analytics & Chat
tab_chat, tab_analytics, tab_rag, tab_drives = st.tabs([
    "1. Ask AI Copilot",
    "2. Student Analytics & Benchmark",
    "3. RAG Resume vs. JD",
    "4. Active Placement Drives"
])

with tab_chat:
    render_chat_interface("Student", user_context={"student_id": active_stu_id})

with tab_analytics:
    st.subheader(f" Benchmarking {curr_student['Name']} vs. {curr_student['Dept']} Cohort")
    c1, c2 = st.columns(2)
    with c1:
        dept_df = df[df["Dept"] == curr_student["Dept"]]
        fig_cgpa = px.histogram(dept_df, x="CGPA", nbins=15, title=f"CGPA Distribution in {curr_student['Dept']}")
        fig_cgpa.add_vline(x=curr_student["CGPA"], line_color="red", line_dash="dash", annotation_text="Your CGPA")
        st.plotly_chart(fig_cgpa, use_container_width=True)
    with c2:
        fig_dept_salary = px.box(df[df["Status"] == "Placed"], x="Dept", y="Package_LPA", title="Placed Salary Spread (LPA) by Dept")
        st.plotly_chart(fig_dept_salary, use_container_width=True)

with tab_rag:
    st.subheader(" Deep RAG Candidate-to-JD Compatibility Analysis")
    target_drive = st.selectbox("Select Drive to Evaluate:", st.session_state.drives["Drive_ID"] + " - " + st.session_state.drives["Company"])
    d_id = target_drive.split(" - ")[0]

    if st.button("Run RAG Match", type="primary"):
        res = rag_resume_vs_jd_analysis(active_stu_id, d_id)
        st.metric("RAG Match Score", f"{res['match_score']}%")
        st.info(f"Targeting: **{res['role']}** at **{res['company']}**")
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("#### ✅ Matched Competencies")
            for s in res["matched_skills"]:
                st.success(f"✔ {s}")
        with col_r:
            st.markdown("#### ❌ Missing Skill Gaps")
            for g in res["missing_skills"]:
                st.error(f"✖ {g}")

with tab_drives:
    st.subheader("Scheduled Placement Drives")
    st.dataframe(st.session_state.drives[["Drive_ID", "Company", "Role", "Min_CGPA", "Package_LPA", "Session_Date"]], use_container_width=True)
