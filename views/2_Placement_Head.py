import streamlit as st
import plotly.express as px
from src.chat_widget import render_chat_interface

st.title("Placement Head Directorate")

df = st.session_state.students
drives = st.session_state.drives

# High-Level Metrics
m1, m2, m3, m4 = st.columns(4)
placed_cnt = len(df[df["Status"] == "Placed"])
m1.metric("Total Batch Size", len(df))
m2.metric("Offers Secured", placed_cnt)
m3.metric("Placement Rate", f"{(placed_cnt/len(df)*100):.1f}%")
m4.metric("Active Drives", len(drives))

tab_chat, tab_analytics, tab_approvals, tab_broadcast = st.tabs([
    "1. Directorate Copilot",
    "2. Placement Analytics & Drive Conversions",
    "3. Company Approvals",
    "4. Broadcast Drive"
])

with tab_chat:
    render_chat_interface("Placement Head")

with tab_analytics:
    c1, c2 = st.columns(2)
    with c1:
        fig_domain = px.pie(drives, names="Company", title="Drive Distribution by Company", hole=0.4)
        st.plotly_chart(fig_domain, use_container_width=True)
    with c2:
        top_hiring = df[df["Status"] == "Placed"].groupby("Company")["ID"].count().reset_index().sort_values(by="ID", ascending=False).head(8)
        fig_hires = px.bar(top_hiring, x="ID", y="Company", orientation="h", title="Top Recruiters by Hires", text="ID")
        st.plotly_chart(fig_hires, use_container_width=True)

with tab_approvals:
    st.subheader("Pending Company Registrations")
    st.dataframe(st.session_state.companies[st.session_state.companies["Status"] == "Pending"], use_container_width=True)

with tab_broadcast:
    st.subheader("Publish New Campus Drive")
    st.info("Drive creation module ready.")
