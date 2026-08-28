import streamlit as st
import pandas as pd
from src.pdf_generator import generate_student_offer_pdf

st.title(" Wall of Fame — Institutional Placement Achievers")
st.caption("Celebrating our placed scholars, Tier-1 marquee recruits, and corporate milestone achievers across all campus departments.")

# ---------------------------------------------------------
# 1. DATA PREPARATION & CAMPUS ENRICHMENT
# ---------------------------------------------------------
if "students" not in st.session_state or st.session_state.students.empty:
    st.info("No student placement records found in the system.")
    st.stop()

df = st.session_state.students.copy()

# Ensure College / Campus column exists for multi-campus filtering
if "College" not in df.columns:
    colleges = [
        "Main Campus (Bengaluru)",
        "East Campus (Tech Park)",
        "South Campus (DeepTech Lab)"
    ]
    df["College"] = df["ID"].apply(lambda x: colleges[abs(hash(str(x))) % len(colleges)])

# Filter only successfully placed/selected candidates
placed_df = df[df["Status"].isin(["Placed", "Selected"])].copy()

if placed_df.empty:
    st.info("No placed candidates recorded in the ledger yet.")
    st.stop()

# Ensure numeric package formatting
placed_df["Package_LPA"] = pd.to_numeric(placed_df["Package_LPA"], errors="coerce").fillna(0.0)

# ---------------------------------------------------------
# 2. TOP-LEVEL FILTER MATRIX
# ---------------------------------------------------------
st.markdown("### 🔍 Filter Achievers")
f1, f2, f3, f4, f5 = st.columns(5)

with f1:
    years = sorted(placed_df["Grad_Year"].dropna().unique(), reverse=True)
    sel_year = st.multiselect("Graduation Year", years, default=years)

with f2:
    depts = sorted(placed_df["Dept"].dropna().unique())
    sel_dept = st.multiselect("Department", depts, default=depts)

with f3:
    colleges_list = sorted(placed_df["College"].dropna().unique())
    sel_college = st.multiselect("College / Campus", colleges_list, default=colleges_list)

with f4:
    companies = sorted([c for c in placed_df["Company"].dropna().unique() if str(c).strip() not in ["None", ""]])
    sel_comp = st.multiselect("Hiring Organization", companies, default=companies)

with f5:
    ctc_tier = st.selectbox(
        "CTC Package Tier",
        [
            "All Placed Achievers",
            "Dream Tier (≥ 20 LPA) ",
            "Super Dream (12 - 20 LPA) ",
            "Core & Mass (5 - 12 LPA) "
        ]
    )

# Apply active filters
filtered = placed_df[
    (placed_df["Grad_Year"].isin(sel_year)) &
    (placed_df["Dept"].isin(sel_dept)) &
    (placed_df["College"].isin(sel_college)) &
    (placed_df["Company"].isin(sel_comp))
]

if ctc_tier == "Dream Tier (≥ 20 LPA) ":
    filtered = filtered[filtered["Package_LPA"] >= 20.0]
elif ctc_tier == "Super Dream (12 - 20 LPA) ":
    filtered = filtered[(filtered["Package_LPA"] >= 12.0) & (filtered["Package_LPA"] < 20.0)]
elif ctc_tier == "Core & Mass (5 - 12 LPA) ":
    filtered = filtered[(filtered["Package_LPA"] >= 5.0) & (filtered["Package_LPA"] < 12.0)]

# ---------------------------------------------------------
# 3. EXECUTIVE HIGHLIGHT TILES
# ---------------------------------------------------------
st.markdown("---")
m1, m2, m3, m4, m5 = st.columns(5)
total_achievers = len(filtered)
max_ctc = float(filtered["Package_LPA"].max()) if not filtered.empty else 0.0
mean_ctc = float(filtered["Package_LPA"].mean()) if not filtered.empty else 0.0
top_partners = filtered["Company"].nunique()
dream_offers = len(filtered[filtered["Package_LPA"] >= 20.0])

m1.metric("Achievers Displayed", f"{total_achievers:,}")
m2.metric("Highest Package", f"₹{max_ctc:.2f} LPA")
m3.metric("Average Package", f"₹{mean_ctc:.2f} LPA")
m4.metric("Active Recruiters", f"{top_partners:,}")
m5.metric("Dream Offers (≥20 LPA)", f"{dream_offers:,}")

st.markdown("---")

# ---------------------------------------------------------
# 4. GALLERY & ROSTER TABS
# ---------------------------------------------------------
tab_cards, tab_table = st.tabs(["1. Hall of Fame Gallery", "2. Tabular Honors Roster"])

with tab_cards:
    if filtered.empty:
        st.info("No placed candidates match the selected filter criteria.")
    else:
        # Sort by Package descending
        filtered_sorted = filtered.sort_values(by="Package_LPA", ascending=False)

        cols_per_row = 3
        rows = [filtered_sorted.iloc[i:i + cols_per_row] for i in range(0, len(filtered_sorted), cols_per_row)]

        for row_chunk in rows:
            grid_cols = st.columns(cols_per_row)
            for idx, (_, student) in enumerate(row_chunk.iterrows()):
                with grid_cols[idx]:
                    pkg = float(student.get("Package_LPA", 0.0))

                    # Visual Tier Badging
                    if pkg >= 20.0:
                        badge_tag = " DREAM OFFER"
                        border_color = "#EAB308"  # Gold
                        bg_badge = "#FEF9C3"
                    elif pkg >= 12.0:
                        badge_tag = " SUPER DREAM"
                        border_color = "#3B82F6"  # Blue
                        bg_badge = "#DBEAFE"
                    else:
                        badge_tag = " PLACED ACHIEVER"
                        border_color = "#10B981"  # Emerald Green
                        bg_badge = "#D1FAE5"

                    with st.container(border=True):
                        # Card Header
                        c_head1, c_head2 = st.columns([2, 1])
                        c_head1.markdown(f"### {student.get('Name', 'Candidate')}")
                        c_head2.markdown(
                            f"<div style='text-align:right;'><span style='background-color:{bg_badge}; color:{border_color}; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:bold;'>{badge_tag}</span></div>",
                            unsafe_allow_html=True
                        )

                        st.caption(f"USN: `{student.get('ID', 'N/A')}` | **{student.get('Dept', 'N/A')}** | Class of {student.get('Grad_Year', 'N/A')}")
                        st.markdown(f" **{student.get('Company', 'N/A')}**")
                        st.markdown(f"  *{student.get('Role', 'Software Engineer')}*")
                        st.markdown(f"  Offered Package: **₹{pkg:.2f} LPA**")
                        st.caption(f"  {student.get('College', 'Main Campus')}")

                        # Key Skills Tags
                        raw_skills = str(student.get("Skills", ""))
                        skills_sample = ", ".join([s.strip() for s in raw_skills.split(",") if s.strip()][:3])
                        if skills_sample:
                            st.markdown(f"🛠️ `{skills_sample}`")

                        st.markdown("---")

                        # Deep links and certificate download
                        btn_c1, btn_c2, btn_c3 = st.columns(3)

                        linkedin_url = str(student.get("Linkedin", "")).strip()
                        if linkedin_url and linkedin_url.startswith("http"):
                            btn_c1.link_button("LinkedIn", linkedin_url, use_container_width=True)
                        else:
                            btn_c1.button("LinkedIn", disabled=True, key=f"li_dis_{student['ID']}", use_container_width=True)

                        github_url = str(student.get("Github", "")).strip()
                        if github_url and github_url.startswith("http"):
                            btn_c2.link_button("GitHub", github_url, use_container_width=True)
                        else:
                            btn_c2.button("GitHub", disabled=True, key=f"gh_dis_{student['ID']}", use_container_width=True)

                        # Dynamic PDF Offer Generation
                        try:
                            pdf_cert = generate_student_offer_pdf(student.to_dict())
                            btn_c3.download_button(
                                label=" Offer",
                                data=pdf_cert,
                                file_name=f"Placement_Certificate_{student['ID']}.pdf",
                                mime="application/pdf",
                                key=f"cert_btn_{student['ID']}",
                                use_container_width=True
                            )
                        except Exception:
                            btn_c3.button(" Offer", disabled=True, key=f"cert_err_{student['ID']}", use_container_width=True)

with tab_table:
    st.subheader("Comprehensive Placed Students Honors Matrix")
    display_cols = [
        "ID", "Name", "Dept", "College", "Grad_Year", "CGPA",
        "Company", "Role", "Package_LPA", "Skills"
    ]
    available_cols = [c for c in display_cols if c in filtered.columns]

    st.dataframe(
        filtered[available_cols].sort_values(by="Package_LPA", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered[available_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label=" Download Wall of Fame Honors Ledger (CSV)",
        data=csv_data,
        file_name="wall_of_fame_placed_students.csv",
        mime="text/csv"
    )
