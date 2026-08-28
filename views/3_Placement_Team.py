import streamlit as st
import plotly.express as px
from src.chat_widget import render_chat_interface

st.title("Placement Team Operations & Reconciliation")

stages_df = st.session_state.candidate_stages

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Candidates in Active Pipeline", len(stages_df))
col2.metric("Offers Extended", len(stages_df[stages_df["Current_Round"].str.contains("Selected|Offer", na=False)]))
col3.metric("Interviews in Progress", len(stages_df[~stages_df["Current_Round"].str.contains("Selected|Offer", na=False)]))

tab_chat, tab_analytics, tab_reconcile = st.tabs([
    "1. Placement Operations Copilot",
    "2. Pipeline Funnel Analytics",
    "3. Post-Drive Reconciliation"
])

with tab_chat:
    render_chat_interface("Placement Team")

with tab_analytics:
    c1, c2 = st.columns(2)
    with c1:
        fig_stages = px.bar(stages_df.groupby("Current_Round")["Student_ID"].count().reset_index(),
                            x="Student_ID", y="Current_Round", orientation="h", title="Pipeline Stage Volume")
        st.plotly_chart(fig_stages, use_container_width=True)
    with c2:
        fig_dept_pipeline = px.histogram(stages_df, x="Dept", color="Company", title="Active Pipeline by Department")
        st.plotly_chart(fig_dept_pipeline, use_container_width=True)

with tab_reconcile:
    st.subheader("Active Pipeline Stages")
    st.dataframe(stages_df, use_container_width=True)
