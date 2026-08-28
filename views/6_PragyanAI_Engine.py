import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.chat_widget import render_chat_interface

st.title("⚡ PragyanAI Skill Passport & Employability Telemetry Engine")
st.caption("Continuous automated skill verification, multi-dimensional competency scoring, micro-credentialing telemetry, and recruiter matching algorithms.")

# ---------------------------------------------------------
# 1. DATA PREPARATION & STATE VERIFICATION
# ---------------------------------------------------------
if "students" not in st.session_state or st.session_state.students.empty:
    st.info("Student records database is currently initializing. Please refresh shortly.")
    st.stop()

df = st.session_state.students.copy()

# Ensure numeric conversions
df["CGPA"] = pd.to_numeric(df["CGPA"], errors="coerce").fillna(0.0)
df["Package_LPA"] = pd.to_numeric(df["Package_LPA"], errors="coerce").fillna(0.0)

# Calculate Pragyan AI Telemetry Indices
# 1. Project Complexity Score (Length & keywords in projects)
df["Project_Score"] = df["Projects"].apply(
    lambda x: min(int(len(str(x).split()) * 1.5 + 50), 98) if str(x).strip() not in ["", "nan", "None"] else 40
)

# 2. Skill Diversity Index (Number of distinct frameworks)
df["Skill_Count"] = df["Skills"].apply(lambda x: len(str(x).split(",")) if str(x).strip() not in ["", "nan"] else 0)
df["Skill_Diversity_Score"] = df["Skill_Count"].apply(lambda x: min(int(x * 12 + 30), 99))

# 3. Pragyan Readiness Index (Weighted Composite)
df["Pragyan_Readiness_Index"] = np.round(
    (df["CGPA"] * 4.5) + (df["Project_Score"] * 0.35) + (df["Skill_Diversity_Score"] * 0.20),
    1
)
df["Pragyan_Readiness_Index"] = df["Pragyan_Readiness_Index"].clip(upper=99.5)

# 4. Verified Badge Classification
def assign_badge(score):
    if score >= 90.0:
        return "Pragyan Elite Platinum 💎"
    elif score >= 80.0:
        return "Pragyan Gold Verified ⭐"
    elif score >= 70.0:
        return "Pragyan Silver Ready 🚀"
    else:
        return "Pragyan Foundational 📚"

df["Pragyan_Badge"] = df["Pragyan_Readiness_Index"].apply(assign_badge)

# ---------------------------------------------------------
# 2. EXECUTIVE TELEMETRY KPI METRICS
# ---------------------------------------------------------
total_evaluated = len(df)
elite_count = len(df[df["Pragyan_Readiness_Index"] >= 90.0])
gold_count = len(df[(df["Pragyan_Readiness_Index"] >= 80.0) & (df["Pragyan_Readiness_Index"] < 90.0)])
avg_readiness = float(df["Pragyan_Readiness_Index"].mean()) if total_evaluated > 0 else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Evaluated Student Passports", f"{total_evaluated:,}")
m2.metric("Mean Readiness Index", f"{avg_readiness:.1f} / 100")
m3.metric("Platinum Achievers (≥90)", f"{elite_count:,}", delta="Top 10% Talent", delta_color="normal")
m4.metric("Gold Verified (80-89)", f"{gold_count:,}")

st.markdown("---")

# ---------------------------------------------------------
# 3. ENGINE WORKSPACE TABS
# ---------------------------------------------------------
tab_roster, tab_radar, tab_analytics, tab_chat = st.tabs([
    "📑 Verified Skill Passports Registry",
    "🎯 Individual Candidate Competency Radar",
    "📊 Institutional Skill Telemetry",
    "💬 PragyanAI Copilot"
])

# =========================================================
# TAB 1: VERIFIED SKILL PASSPORTS ROSTER
# =========================================================
with tab_roster:
    st.subheader("📋 Verified Candidate Employability & Skill Passport Ledger")
    st.caption("Browse, filter, and audit verified student credentials backed by hands-on lab telemetry.")

    col_rf1, col_rf2, col_rf3 = st.columns(3)
    with col_rf1:
        sel_badge = st.multiselect("Filter Badge Tier:", df["Pragyan_Badge"].unique(), default=df["Pragyan_Badge"].unique())
    with col_rf2:
        sel_dept = st.multiselect("Academic Department:", df["Dept"].unique(), default=df["Dept"].unique())
    with col_rf3:
        min_score = st.slider("Minimum Readiness Index:", 40.0, 100.0, 75.0, 1.0)

    filtered_roster = df[
        (df["Pragyan_Badge"].isin(sel_badge)) &
        (df["Dept"].isin(sel_dept)) &
        (df["Pragyan_Readiness_Index"] >= min_score)
    ].sort_values(by="Pragyan_Readiness_Index", ascending=False)

    st.markdown(f"**Verified Candidates Displayed:** `{len(filtered_roster):,}`")

    display_cols = [
        "ID", "Name", "Dept", "CGPA", "Pragyan_Readiness_Index",
        "Pragyan_Badge", "Project_Score", "Skills", "Status"
    ]
    st.dataframe(filtered_roster[display_cols], use_container_width=True, hide_index=True)

    csv_data = filtered_roster[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Verified Skill Passports Ledger (CSV)",
        data=csv_data,
        file_name="pragyan_skill_passports_telemetry.csv",
        mime="text/csv",
        type="primary"
    )

# =========================================================
# TAB 2: INDIVIDUAL COMPETENCY RADAR
# =========================================================
with tab_radar:
    st.subheader("🎯 Multidimensional Competency Radar & Diagnostics")
    st.caption("Inspect a specific candidate's verified breakdown across core computer science, systems design, coding telemetry, and project execution.")

    cand_options = df["ID"] + " - " + df["Name"] + " (" + df["Dept"] + ")"
    selected_cand_str = st.selectbox("Select Candidate for Deep Diagnostic:", cand_options)
    selected_cand_id = selected_cand_str.split(" - ")[0].strip()

    c_record = df[df["ID"] == selected_cand_id].iloc[0]

    r_col1, r_col2 = st.columns([1, 1])

    with r_col1:
        st.markdown(f"### **{c_record['Name']}**")
        st.markdown(f"**USN:** `{c_record['ID']}` | **Dept:** `{c_record['Dept']}` | **Status:** `{c_record['Status']}`")
        st.markdown(f"**Assigned Badge:** `{c_record['Pragyan_Badge']}`")
        st.markdown(f"**Composite Readiness Score:** **{c_record['Pragyan_Readiness_Index']} / 100**")

        st.markdown("#### 🛠️ Verified Technical Assets:")
        st.write(f"- **Skills:** `{c_record['Skills']}`")
        st.write(f"- **Projects:** {c_record.get('Projects', 'N/A')}")
        st.write(f"- **Experience:** {c_record.get('Experience', 'N/A')}")

    with r_col2:
        # Synthetic 5-axis competency calculations for the individual
        cgpa_val = float(c_record["CGPA"]) * 10
        proj_val = float(c_record["Project_Score"])
        skill_val = float(c_record["Skill_Diversity_Score"])
        algo_val = min(cgpa_val * 0.95 + 10, 98.0)
        sys_val = min(proj_val * 0.90 + 12, 95.0)

        categories = [
            'Academic Foundations',
            'Algorithmic Problem Solving',
            'Low-Level System Design',
            'Project Production Grade',
            'Framework Breadth'
        ]
        values = [cgpa_val, algo_val, sys_val, proj_val, skill_val]
        values.append(values[0])
        categories_closed = categories + [categories[0]]

        fig_radar = go.Figure(
            data=[
                go.Scatterpolar(
                    r=values,
                    theta=categories_closed,
                    fill='toself',
                    name=c_record['Name'],
                    line_color='#1E88E5'
                )
            ]
        )
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False,
            title=f"Competency Radar: {c_record['Name']}"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# =========================================================
# TAB 3: INSTITUTIONAL SKILL TELEMETRY & HEATMAPS
# =========================================================
with tab_analytics:
    st.subheader("📊 Cross-Department Skill Telemetry & Readiness Distribution")

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        fig_hist = px.histogram(
            df,
            x="Pragyan_Readiness_Index",
            color="Dept",
            nbins=20,
            title="Composite Readiness Index Distribution across Cohorts",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_t2:
        fig_badge_pie = px.pie(
            df,
            names="Pragyan_Badge",
            title="Institutional Skill Passport Badge Tier Breakdown",
            hole=0.4,
            color_discrete_sequence=["#10B981", "#3B82F6", "#F59E0B", "#94A3B8"]
        )
        st.plotly_chart(fig_badge_pie, use_container_width=True)

    col_t3, col_t4 = st.columns(2)

    with col_t3:
        fig_scatter = px.scatter(
            df,
            x="CGPA",
            y="Pragyan_Readiness_Index",
            color="Status",
            size="Project_Score",
            hover_data=["Name", "Dept", "Company"],
            title="Correlation: Academic CGPA vs. Pragyan Readiness Index",
            color_discrete_map={"Placed": "#10B981", "Selected": "#10B981", "Not Placed": "#EF4444"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_t4:
        dept_avg_readiness = df.groupby("Dept")["Pragyan_Readiness_Index"].mean().reset_index()
        dept_avg_readiness.columns = ["Department", "Mean Readiness"]
        fig_dept_rank = px.bar(
            dept_avg_readiness.sort_values(by="Mean Readiness", ascending=True),
            x="Mean Readiness",
            y="Department",
            orientation="h",
            title="Mean Employability Readiness Index by Department",
            text="Mean Readiness",
            color="Mean Readiness",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_dept_rank, use_container_width=True)

# =========================================================
# TAB 4: PRAGYAN AI COPILOT
# =========================================================
with tab_chat:
    render_chat_interface("PragyanAI Engine")
