import streamlit as st
import pandas as pd
from src.database import (
    init_database_from_csv,
    fetch_table_as_df,
    StudentModel,
    CompanyModel,
    DriveModel,
    JobDescriptionModel,
    CandidateStageModel,
    DriveSelectionModel,
    InterviewExperienceModel,
    TrainingSessionModel,
    RecruiterFeedbackModel,
    UserModel
)


def init_db():
    """
    Initializes tables, seeds default datasets if empty,
    and maps all relational tables to Streamlit session state.
    """
    # 1. Initialize schema and populate baseline dataset if unpopulated
    init_database_from_csv()

    # 2. Synchronize Students table
    students_raw = fetch_table_as_df(StudentModel)
    if not students_raw.empty:
        st.session_state.students = students_raw.rename(columns={
            "id": "ID",
            "name": "Name",
            "dept": "Dept",
            "college": "College",
            "grad_year": "Grad_Year",
            "cgpa": "CGPA",
            "skills": "Skills",
            "projects": "Projects",
            "experience": "Experience",
            "linkedin": "Linkedin",
            "github": "Github",
            "dream_roles": "Dream_Roles",
            "dream_companies": "Dream_Companies",
            "salary_expected_lpa": "Salary_Expected_LPA",
            "status": "Status",
            "company": "Company",
            "role": "Role",
            "package_lpa": "Package_LPA"
        })
    else:
        st.session_state.students = pd.DataFrame()

    # 3. Synchronize Companies table
    companies_raw = fetch_table_as_df(CompanyModel)
    if not companies_raw.empty:
        st.session_state.companies = companies_raw.rename(columns={
            "company": "Company",
            "domain": "Domain",
            "email": "Email",
            "status": "Status",
            "openings": "Openings"
        })
    else:
        st.session_state.companies = pd.DataFrame()

    # 4. Synchronize Drives table
    drives_raw = fetch_table_as_df(DriveModel)
    if not drives_raw.empty:
        st.session_state.drives = drives_raw.rename(columns={
            "drive_id": "Drive_ID",
            "company": "Company",
            "role": "Role",
            "min_cgpa": "Min_CGPA",
            "eligible_depts": "Eligible_Depts",
            "required_skills": "Required_Skills",
            "description": "Description",
            "package_lpa": "Package_LPA",
            "session_date": "Session_Date",
            "app_link": "App_Link",
            "seminar_link": "Seminar_Link",
            "ppt_link": "PPT_Link"
        })
    else:
        st.session_state.drives = pd.DataFrame()

    # 5. Synchronize Job Descriptions table
    jds_raw = fetch_table_as_df(JobDescriptionModel)
    if not jds_raw.empty:
        st.session_state.job_descriptions = jds_raw.rename(columns={
            "jd_id": "JD_ID",
            "drive_id": "Drive_ID",
            "company": "Company",
            "role": "Role",
            "target_domain": "Target_Domain",
            "full_jd_text": "Full_JD_Text",
            "min_experience_months": "Min_Experience_Months",
            "package_lpa": "Package_LPA"
        })
    else:
        st.session_state.job_descriptions = pd.DataFrame()

    # 6. Synchronize Candidate Stages table
    stages_raw = fetch_table_as_df(CandidateStageModel)
    if not stages_raw.empty:
        st.session_state.candidate_stages = stages_raw.rename(columns={
            "stage_id": "Stage_ID",
            "student_id": "Student_ID",
            "student_name": "Student_Name",
            "dept": "Dept",
            "company": "Company",
            "role": "Role",
            "current_round": "Current_Round",
            "next_round_date": "Next_Round_Date",
            "mode_location": "Mode_Location"
        })
    else:
        st.session_state.candidate_stages = pd.DataFrame()

    # 7. Synchronize Drive Selections table
    selections_raw = fetch_table_as_df(DriveSelectionModel)
    if not selections_raw.empty:
        st.session_state.drive_selections = selections_raw.rename(columns={
            "drive_id": "Drive_ID",
            "company": "Company",
            "student_id": "Student_ID",
            "student_name": "Student_Name",
            "dept": "Dept",
            "attended": "Attended",
            "selection_status": "Selection_Status",
            "offered_role": "Offered_Role",
            "offered_ctc_lpa": "Offered_CTC_LPA"
        })
    else:
        st.session_state.drive_selections = pd.DataFrame()

    # 8. Synchronize Interview Experiences table
    exp_raw = fetch_table_as_df(InterviewExperienceModel)
    if not exp_raw.empty:
        st.session_state.interview_experiences = exp_raw.rename(columns={
            "exp_id": "Exp_ID",
            "student_id": "Student_ID",
            "student_name": "Student_Name",
            "dept": "Dept",
            "company": "Company",
            "role": "Role",
            "rounds_faced": "Rounds_Faced",
            "skills_excelled": "Skills_Excelled",
            "challenges_faced": "Challenges_Faced",
            "advice_to_crack": "Advice_To_Crack",
            "photo_attached": "Photo_Attached",
            "audio_attached": "Audio_Attached",
            "timestamp": "Timestamp"
        })
    else:
        st.session_state.interview_experiences = pd.DataFrame()

    # 9. Synchronize Training Sessions table
    train_raw = fetch_table_as_df(TrainingSessionModel)
    if not train_raw.empty:
        st.session_state.training_sessions = train_raw.rename(columns={
            "session_id": "Session_ID",
            "type": "Type",
            "title": "Title",
            "target_depts": "Target_Depts",
            "instructor": "Instructor",
            "schedule_date": "Schedule_Date",
            "timing": "Timing",
            "mode": "Mode",
            "location": "Location",
            "curriculum": "Curriculum",
            "meeting_link": "Meeting_Link",
            "resource_link": "Resource_Link"
        })
    else:
        st.session_state.training_sessions = pd.DataFrame()

    # 10. Synchronize Recruiter Feedback table
    feedback_raw = fetch_table_as_df(RecruiterFeedbackModel)
    if not feedback_raw.empty:
        st.session_state.recruiter_feedback = feedback_raw.rename(columns={
            "company": "Company",
            "drive_id": "Drive_ID",
            "evaluator": "Evaluator",
            "dept_evaluated": "Dept_Evaluated",
            "overall_rating": "Overall_Rating",
            "strong_areas": "Strong_Areas",
            "observed_gaps": "Observed_Gaps",
            "recommended_curriculum_fixes": "Recommended_Curriculum_Fixes"
        })
    else:
        st.session_state.recruiter_feedback = pd.DataFrame()

    # 11. Synchronize Users Registry
    users_raw = fetch_table_as_df(UserModel)
    st.session_state.users_df = users_raw if not users_raw.empty else pd.DataFrame()
