import streamlit as st
import plotly.express as px
from src.chat_widget import render_chat_interface

st.title(" Hiring Partner & Talent Acquisition Hub")

df = st.session_state.students

tab_chat, tab_analytics, tab_filter, tab_feedback = st.tabs([
    "1. Recruiter AI Copilot",
    "2. Talent Pool Analytics",
    "3. Candidate Discovery Engine",
    "4. Submit Recruiter Feedback"
])

with tab_chat:
    render_chat_interface("Hiring Partner")

with tab_analytics:
    st.subheader("Campus Talent Pool Demographics")
    c1, c2 = st.columns(2)
    with c1:
        fig_cgpa = px.box(df, x="Dept", y="CGPA", title="CGPA Distribution Across Departments", color="Dept")
        st.plotly_chart(fig_cgpa, use_container_width=True)
    with c2:
        fig_status = px.pie(df, names="Status", title="Overall Candidate Availability Ratio", hole=0.3)
        st.plotly_chart(fig_status, use_container_width=True)

with tab_filter:
    st.subheader("Filter Candidates")
    cgpa_cut = st.slider("Minimum CGPA", 0.0, 10.0, 7.5, 0.1)
    dept_sel = st.multiselect("Departments", df["Dept"].unique(), default=["CSE", "AIML", "ECE"])
    res = df[(df["CGPA"] >= cgpa_cut) & (df["Dept"].isin(dept_sel))]
    st.write(f"Matching Candidates: **{len(res)}**")
    st.dataframe(res[["ID", "Name", "Dept", "CGPA", "Skills", "Status"]], use_container_width=True)

with tab_feedback:
    st.subheader("Submit Cohort Feedback")
    st.text_area("Observations on student technical readiness:")
    st.button("Save Feedback")
