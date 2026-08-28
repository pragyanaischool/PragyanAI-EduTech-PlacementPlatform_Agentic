import streamlit as st
import pandas as pd
import plotly.express as px
from src.chat_widget import render_chat_interface
from src.rag_engine import analyze_selection_differences

st.title(" Institutional Placement Executive Console")

df = st.session_state.students

tab_chat, tab_analytics, tab_pivots, tab_diff = st.tabs([
    "1. Executive AI Copilot",
    "2. Multi-Dept Analytics & Sunburst",
    "3. Cross-Tabulated Pivots",
    "4. Selection Difference Engine"
])

with tab_chat:
    render_chat_interface("Executive Board")

with tab_analytics:
    c1, c2 = st.columns(2)
    with c1:
        fig_sunburst = px.sunburst(
            df[df["Status"] == "Placed"],
            path=["Grad_Year", "Dept", "Company", "Role"],
            values="Package_LPA",
            title="Placement Hierarchy: Year ➔ Dept ➔ Company ➔ Role",
            color="Package_LPA",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_sunburst, use_container_width=True)
    with c2:
        fig_dept_salary = px.box(df[df["Status"] == "Placed"], x="Dept", y="Package_LPA", title="Package Distribution by Dept", color="Dept")
        st.plotly_chart(fig_dept_salary, use_container_width=True)

with tab_pivots:
    st.subheader("Cross-Tabulated Placement Matrix")
    pivot = pd.pivot_table(
        df[df["Status"] == "Placed"],
        index="Dept",
        columns="Grad_Year",
        values="Package_LPA",
        aggfunc="mean",
        fill_value=0.0
    ).round(2)
    st.dataframe(pivot, use_container_width=True)

with tab_diff:
    st.subheader("Selection Difference Analysis")
    comp = st.selectbox("Select Organization:", [c for c in df["Company"].unique() if c != "None"])
    diff = analyze_selection_differences(comp)
    if diff:
        c1, c2 = st.columns(2)
        c1.metric("Selected Students", diff["selected_count"])
        c2.metric("Avg Selected CGPA", diff["avg_selected_cgpa"])
        for idx, item in enumerate(diff["differentiating_factors"], 1):
            st.info(f"**Factor {idx}:** {item}")
