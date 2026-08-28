import streamlit as st
import pandas as pd
from src.database import (
    init_database_from_csv, fetch_table_as_df,
    StudentModel, CompanyModel, DriveModel, JobDescriptionModel,
    CandidateStageModel, DriveSelectionModel, InterviewExperienceModel,
    TrainingSessionModel, RecruiterFeedbackModel
)

def init_db():
    # 1. Initialize SQLite Tables & Seed from CSV if empty
    init_database_from_csv()

    # 2. Sync Database Tables to Session State for Rapid Querying
    st.session_state.students = fetch_table_as_df(StudentModel).rename(columns={
        "id": "ID", "name": "Name", "dept": "Dept", "grad_year": "Grad_Year",
        "cgpa": "CGPA", "skills": "Skills", "projects": "Projects", "experience": "Experience",
        "linkedin": "Linkedin", "github": "Github", "dream_roles": "Dream_Roles",
        "dream_companies": "Dream_Companies", "salary_expected_lpa": "Salary_Expected_LPA",
        "status": "Status", "company": "Company", "role": "Role", "package_lpa": "Package_LPA"
    })

    st.session_state.companies = fetch_table_as_df(CompanyModel).rename(columns={
        "company": "Company", "domain": "Domain", "email": "Email",
        "status": "Status", "openings": "Openings"
    })

    st.session_state.drives = fetch_table_as_df(DriveModel).rename(columns={
        "drive_id": "Drive_ID", "company": "Company", "role": "Role",
        "min_cgpa": "Min_CGPA", "eligible_depts": "Eligible_Depts",
        "required_skills": "Required_Skills", "description": "Description",
        "package_lpa": "Package_LPA", "session_date": "Session_Date",
        "app_link": "App_Link", "seminar_link": "Seminar_Link", "ppt_link": "PPT_Link"
    })

    st.session_state.job_descriptions = fetch_table_as_df(JobDescriptionModel).rename(columns={
        "jd_id": "JD_ID", "drive_id": "Drive_ID", "company": "Company", "role": "Role",
        "target_domain": "Target_Domain", "full_jd_text": "Full_JD_Text",
        "min_experience_months": "Min_Experience_Months", "package_lpa": "Package_LPA"
    })

    st.session_state.candidate_stages = fetch_table_as_df(CandidateStageModel).rename(columns={
        "stage_id": "Stage_ID", "student_id": "Student_ID", "student_name": "Student_Name",
        "dept": "Dept", "company": "Company", "role": "Role",
        "current_round": "Current_Round", "next_round_date": "Next_Round_Date",
        "mode_location": "Mode_Location"
    })

    st.session_state.drive_selections = fetch_table_as_df(DriveSelectionModel).rename(columns={
        "drive_id": "Drive_ID", "company": "Company", "student_id": "Student_ID",
        "student_name": "Student_Name", "dept": "Dept", "attended": "Attended",
        "selection_status": "Selection_Status", "offered_role": "Offered_Role",
        "offered_ctc_lpa": "Offered_CTC_LPA"
    })

    st.session_state.interview_experiences = fetch_table_as_df(InterviewExperienceModel).rename(columns={
        "exp_id": "Exp_ID", "student_id": "Student_ID", "student_name": "Student_Name",
        "dept": "Dept", "company": "Company", "role": "Role",
        "rounds_faced": "Rounds_Faced", "skills_excelled": "Skills_Excelled",
        "challenges_faced": "Challenges_Faced", "advice_to_crack": "Advice_To_Crack",
        "photo_attached": "Photo_Attached", "audio_attached": "Audio_Attached",
        "timestamp": "Timestamp"
    })

    st.session_state.training_sessions = fetch_table_as_df(TrainingSessionModel).rename(columns={
        "session_id": "Session_ID", "type": "Type", "title": "Title",
        "target_depts": "Target_Depts", "instructor": "Instructor",
        "schedule_date": "Schedule_Date", "timing": "Timing", "mode": "Mode",
        "location": "Location", "curriculum": "Curriculum",
        "meeting_link": "Meeting_Link", "resource_link": "Resource_Link"
    })

    st.session_state.recruiter_feedback = fetch_table_as_df(RecruiterFeedbackModel).rename(columns={
        "company": "Company", "drive_id": "Drive_ID", "evaluator": "Evaluator",
        "dept_evaluated": "Dept_Evaluated", "overall_rating": "Overall_Rating",
        "strong_areas": "Strong_Areas", "observed_gaps": "Observed_Gaps",
        "recommended_curriculum_fixes": "Recommended_Curriculum_Fixes"
    })

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "👋 Hello! I am your **PragyanAI Placement Copilot**, connected to the institutional database. Ask me about candidate pipeline stages, selection criteria, or company interview schedules."}
        ]
