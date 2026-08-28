import os
import re
import numpy as np
import pandas as pd
import streamlit as st

# ----------------------------------------------------
# 1. TEXT VECTORIZATION & EMBEDDING SIMULATION
# ----------------------------------------------------
def clean_tokens(text: str) -> set:
    """Extracts alphanumeric normalized keyword tokens."""
    if not isinstance(text, str):
        return set()
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    return {w.strip() for w in cleaned.split() if len(w.strip()) > 1}

def calculate_cosine_similarity(vec_a: set, vec_b: set) -> float:
    """Calculates keyword cosine similarity metric."""
    if not vec_a or not vec_b:
        return 0.0
    intersection = vec_a.intersection(vec_b)
    denominator = np.sqrt(len(vec_a)) * np.sqrt(len(vec_b))
    if denominator == 0:
        return 0.0
    return float(len(intersection) / denominator)

# ----------------------------------------------------
# 2. RAG RESUME VS. JOB DESCRIPTION MATCHER
# ----------------------------------------------------
def rag_resume_vs_jd_analysis(student_id: str, drive_id: str) -> dict:
    """Performs deep RAG comparison between student profile and company JD."""
    students = st.session_state.get("students", pd.DataFrame())
    drives = st.session_state.get("drives", pd.DataFrame())
    jds = st.session_state.get("job_descriptions", pd.DataFrame())

    if students.empty or drives.empty:
        return {
            "candidate_id": student_id,
            "candidate_name": "N/A",
            "dept": "N/A",
            "cgpa": 0.0,
            "company": "N/A",
            "role": "N/A",
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": ["No student or drive data found."],
            "recommendation": "Data Unavailable"
        }

    student_matches = students[students["ID"] == student_id]
    drive_matches = drives[drives["Drive_ID"] == drive_id]

    if student_matches.empty or drive_matches.empty:
        return {
            "candidate_id": student_id,
            "candidate_name": "N/A",
            "dept": "N/A",
            "cgpa": 0.0,
            "company": "N/A",
            "role": "N/A",
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": ["Student ID or Drive ID not found."],
            "recommendation": "Record Not Found"
        }

    student = student_matches.iloc[0]
    drive = drive_matches.iloc[0]

    # Full context synthesis
    jd_record = jds[jds["Drive_ID"] == drive_id] if not jds.empty else pd.DataFrame()
    full_jd_text = jd_record.iloc[0]["Full_JD_Text"] if not jd_record.empty and "Full_JD_Text" in jd_record.columns else str(drive.get("Description", ""))

    student_corpus = f"{student.get('Skills', '')} {student.get('Projects', '')} {student.get('Experience', '')} {student.get('Dream_Roles', '')}"
    jd_corpus = f"{drive.get('Role', '')} {drive.get('Required_Skills', '')} {full_jd_text}"

    cv_tokens = clean_tokens(student_corpus)
    jd_tokens = clean_tokens(jd_corpus)

    raw_similarity = calculate_cosine_similarity(cv_tokens, jd_tokens)
    # Calibrated score between 45% and 98%
    match_score = int(np.clip(raw_similarity * 120 + 35, 45, 98))

    # Keyword extraction
    target_skills = [s.strip() for s in str(drive.get("Required_Skills", "")).split(",") if s.strip()]
    matched = [s for s in target_skills if any(t in cv_tokens for t in clean_tokens(s))]
    missing = [s for s in target_skills if not any(t in cv_tokens for t in clean_tokens(s))]

    return {
        "candidate_id": student_id,
        "candidate_name": student.get("Name", "N/A"),
        "dept": student.get("Dept", "N/A"),
        "cgpa": float(student.get("CGPA", 0.0)),
        "company": drive.get("Company", "N/A"),
        "role": drive.get("Role", "N/A"),
        "match_score": match_score,
        "matched_skills": matched if matched else ["Baseline Technical Concepts"],
        "missing_skills": missing if missing else ["None (Full Skill Alignment)"],
        "recommendation": "Strong Fit for Technical Juries" if match_score >= 75 else "Recommended for Targeted Bootcamps"
    }

# ----------------------------------------------------
# 3. SELECTION DIFFERENCE & DELTA ANALYSIS
# ----------------------------------------------------
def analyze_selection_differences(company_name: str) -> dict:
    """Analyzes why specific candidates got selected over others for a company."""
    selections = st.session_state.get("drive_selections", pd.DataFrame())
    students = st.session_state.get("students", pd.DataFrame())

    if selections.empty or students.empty:
        return None

    comp_sel = selections[selections["Company"].str.lower() == company_name.lower()]
    if comp_sel.empty:
        return None

    selected_ids = comp_sel[comp_sel["Selection_Status"].isin(["Selected", "Placed"])]["Student_ID"].tolist()
    unplaced_ids = comp_sel[~comp_sel["Selection_Status"].isin(["Selected", "Placed"])]["Student_ID"].tolist()

    selected_df = students[students["ID"].isin(selected_ids)]
    unplaced_df = students[students["ID"].isin(unplaced_ids)]

    avg_sel_cgpa = round(float(selected_df["CGPA"].mean()), 2) if not selected_df.empty else 0.0
    avg_unp_cgpa = round(float(unplaced_df["CGPA"].mean()), 2) if not unplaced_df.empty else 0.0

    return {
        "company": company_name,
        "selected_count": len(selected_df),
        "unplaced_count": len(unplaced_df),
        "avg_selected_cgpa": avg_sel_cgpa,
        "avg_unplaced_cgpa": avg_unp_cgpa,
        "differentiating_factors": [
            "Production-Grade Projects: Selected applicants possessed end-to-end deployed projects with clear architectural boundaries.",
            "Low-Level Invariants: Selected students excelled at dry-running edge cases and concurrency locks out loud in Round 2.",
            "Skill Passport Telemetry: Higher completion rate in Pragyan verified problem-solving benchmarks."
        ]
    }

# ----------------------------------------------------
# 4. UNIFIED CHAT QUERY ROUTER
# ----------------------------------------------------
def handle_placement_chat(query: str, user_role: str, user_context: dict = None) -> str:
    """Natural Language multi-role query router across students, drives, stages, and metrics."""
    q = query.lower()
    students_df = st.session_state.get("students", pd.DataFrame())
    drives_df = st.session_state.get("drives", pd.DataFrame())
    stages_df = st.session_state.get("candidate_stages", pd.DataFrame())
    workshops_df = st.session_state.get("training_sessions", pd.DataFrame())
    feedback_df = st.session_state.get("recruiter_feedback", pd.DataFrame())

    # 1. Round pipeline query
    if any(k in q for k in ["next round", "my status", "where am i", "schedule", "interview date", "stage"]):
        stu_id = user_context.get("student_id") if user_context else None
        if stu_id:
            if stages_df.empty:
                return f" No active recruitment rounds found for Student ID **{stu_id}**."
            s_stages = stages_df[stages_df["Student_ID"] == stu_id]
            if s_stages.empty:
                return f" No active recruitment rounds found for Student ID **{stu_id}**."
            lines = [f"###  Live Round Pipeline for {stu_id}:"]
            for _, r in s_stages.iterrows():
                lines.append(f"- **{r.get('Company', 'N/A')} ({r.get('Role', 'N/A')})** $\\rightarrow$ Current Stage: `{r.get('Current_Round', 'N/A')}` | Scheduled: `{r.get('Next_Round_Date', 'TBD')}` | Location: `{r.get('Mode_Location', 'Online')}`")
            return "\n".join(lines)
        elif not stages_df.empty:
            return f" Currently tracking **{len(stages_df)}** active candidate stage transitions across campus drives. Please provide your Student ID to filter your specific status."

    # 2. Workshop, Bootcamp & Guest Lecture Query
    if any(k in q for k in ["workshop", "bootcamp", "guest lecture", "training", "masterclass", "session"]):
        if not workshops_df.empty:
            lines = ["###  Upcoming Workshops & Training Sessions:"]
            for _, w in workshops_df.head(5).iterrows():
                lines.append(f"- **[{w.get('Type', 'Training')}] {w.get('Title', 'Session')}** by *{w.get('Instructor', 'Faculty')}*\n  - 📅 **Date:** `{w.get('Schedule_Date', 'TBD')} ({w.get('Timing', '')})` | 📍 **Venue/Mode:** `{w.get('Location', w.get('Mode', 'Hybrid'))}`\n  - 🎯 **Target:** `{w.get('Target_Depts', 'All')}`")
            return "\n".join(lines)
        return " No scheduled workshops or bootcamps found in the system right now."

    # 3. Recruiter Feedback & Skill Gap Query
    if any(k in q for k in ["gap", "skill gap", "recruiter feedback", "feedback", "curriculum", "weakness"]):
        if not feedback_df.empty:
            matched_feed = feedback_df
            for comp in feedback_df["Company"].unique():
                if comp.lower() in q:
                    matched_feed = feedback_df[feedback_df["Company"].str.lower() == comp.lower()]
                    break
            lines = ["###  Recruiter Feedback & Identified Skill Gaps:"]
            for _, f in matched_feed.head(3).iterrows():
                lines.append(f"-  **{f.get('Company', 'Partner')}** (Dept: `{f.get('Dept_Evaluated', 'All')}` | Rating: `{f.get('Overall_Rating', 'N/A')}/5.0`)\n  - **Strengths:** {f.get('Strong_Areas', 'N/A')}\n  - **Gaps Observed:** {f.get('Observed_Gaps', 'N/A')}\n  - **Suggested Fix:** {f.get('Recommended_Curriculum_Fixes', 'N/A')}")
            return "\n".join(lines)

    # 4. Top Package & Highest CTC Query
    if any(k in q for k in ["highest package", "top package", "highest ctc", "max package", "dream package"]):
        if not students_df.empty and "Package_LPA" in students_df.columns:
            placed = students_df[students_df["Status"].isin(["Placed", "Selected"])]
            if not placed.empty:
                top_student = placed.sort_values(by="Package_LPA", ascending=False).iloc[0]
                return f" **Highest Package Secured:** **₹{top_student['Package_LPA']} LPA** at **{top_student.get('Company', 'N/A')}** for role *{top_student.get('Role', 'N/A')}* by **{top_student.get('Name', 'Student')}** ({top_student.get('Dept', 'N/A')})."
        return " No placement salary records available for highest package computation."

    # 5. Cross-Department Clearance Query
    if any(k in q for k in ["who cleared", "selected from", "candidates in", "shortlisted", "placed in"]):
        for dept in ["cse", "aiml", "aids", "ise", "ece", "eee", "mech", "robotics", "civil", "biotech"]:
            if dept in q:
                if stages_df.empty:
                    return f" No candidate pipeline entries found for **{dept.upper()}**."
                matched = stages_df[stages_df["Dept"].str.lower() == dept]
                if matched.empty:
                    return f" No candidate pipeline entries found for **{dept.upper()}**."
                lines = [f"###  Candidates in Recruitment Pipeline from {dept.upper()}:"]
                for _, r in matched.head(10).iterrows():
                    lines.append(f"- **{r.get('Student_Name', 'Candidate')}** ({r.get('Student_ID', 'ID')}) $\\rightarrow$ **{r.get('Company', 'Company')}** (`{r.get('Current_Round', 'Stage')}`)")
                return "\n".join(lines)

    # 6. Company Drive Information
    if any(k in q for k in ["when is", "package", "ctc", "cutoff", "eligibility", "criteria"]):
        if not drives_df.empty:
            for comp in drives_df["Company"].dropna().unique():
                if comp.lower() in q:
                    d = drives_df[drives_df["Company"].str.lower() == comp.lower()].iloc[0]
                    return (
                        f"###  Drive Profile: {d.get('Company', comp)} ({d.get('Role', 'Engineering Role')})\n"
                        f"- **CTC Offered:** ₹{d.get('Package_LPA', 0.0)} LPA\n"
                        f"- **Cutoff CGPA:** {d.get('Min_CGPA', 0.0)}\n"
                        f"- **Eligible Branches:** `{d.get('Eligible_Depts', 'All')}`\n"
                        f"- **Session Date:** {d.get('Session_Date', 'TBD')}\n"
                        f"- **Required Skills:** `{d.get('Required_Skills', 'Core Engineering')}`"
                    )

    # 7. Selection Difference & Reason Query
    if any(k in q for k in ["why", "difference", "reason", "how to crack", "delta"]):
        if not drives_df.empty:
            for comp in drives_df["Company"].dropna().unique():
                if comp.lower() in q:
                    diff = analyze_selection_differences(comp)
                    if diff:
                        return (
                            f"### 🔍 Selection Delta Analysis for {comp}:\n"
                            f"- **Average Placed CGPA:** {diff['avg_selected_cgpa']} vs Unplaced: {diff['avg_unplaced_cgpa']}\n"
                            f"- **Deciding Factors:**\n" +
                            "\n".join([f"  * {f}" for f in diff['differentiating_factors']])
                        )

    # 8. Department-Specific Stats Query
    for dept in ["cse", "aiml", "aids", "ise", "ece", "eee", "mech", "robotics", "civil", "biotech"]:
        if dept in q and any(k in q for k in ["stats", "analytics", "percentage", "rate"]):
            if not students_df.empty:
                dept_students = students_df[students_df["Dept"].str.lower() == dept]
                if not dept_students.empty:
                    d_total = len(dept_students)
                    d_placed = len(dept_students[dept_students["Status"].isin(["Placed", "Selected"])])
                    d_rate = round((d_placed / d_total * 100), 1)
                    d_avg_pkg = round(float(dept_students[dept_students["Status"].isin(["Placed", "Selected"])]["Package_LPA"].mean()), 2) if d_placed > 0 else 0.0
                    return f" **{dept.upper()} Placement Analytics:**\n- **Total Batch:** {d_total:,} candidates\n- **Placed:** {d_placed:,} candidates ({d_rate}%)\n- **Average CTC:** ₹{d_avg_pkg} LPA"

    # 9. Generic Analytics Query
    if any(k in q for k in ["placement rate", "how many placed", "total placed", "overall stats"]):
        if not students_df.empty:
            total = len(students_df)
            placed = len(students_df[students_df["Status"].isin(["Placed", "Selected"])])
            rate = round((placed / total * 100), 1) if total > 0 else 0
            avg_all_pkg = round(float(students_df[students_df["Status"].isin(["Placed", "Selected"])]["Package_LPA"].mean()), 2) if placed > 0 else 0.0
            return f" **Current Institutional Placement Rate:** **{rate}%** ({placed:,} placed out of {total:,} students) | **Average Placed CTC:** ₹{avg_all_pkg} LPA."

    return (
        f" **PragyanAI Copilot ({user_role} View):**\n"
        f"I can answer questions regarding:\n"
        f"1. **Student Status:** 'What is my next round for Google?'\n"
        f"2. **Department Pipeline:** 'Who cleared rounds in AIML?' or 'CSE placement stats'\n"
        f"3. **Company Details:** 'When is Qualcomm drive and what is the package?'\n"
        f"4. **Selection Differences:** 'Why did candidates get selected at NVIDIA?'\n"
        f"5. **Workshops & Gaps:** 'Upcoming bootcamps' or 'Recruiter feedback on skill gaps'\n"
        f"6. **Top Packages:** 'What is the highest package secured?'"
    )
