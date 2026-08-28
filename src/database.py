import os
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# ----------------------------------------------------
# 1. DATABASE CONFIGURATION & ENGINE
# ----------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DB_DIR = os.path.join(PROJECT_ROOT, "database")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "placement_portal.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ----------------------------------------------------
# 2. RELATIONAL ORM SCHEMAS
# ----------------------------------------------------
class StudentModel(Base):
    __tablename__ = "students"

    id = Column(String(20), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    dept = Column(String(20), nullable=False, index=True)
    grad_year = Column(Integer, nullable=False, index=True)
    cgpa = Column(Float, nullable=False, index=True)
    skills = Column(Text, nullable=False)
    projects = Column(Text, default="")
    experience = Column(Text, default="")
    linkedin = Column(String(255), default="")
    github = Column(String(255), default="")
    dream_roles = Column(String(255), default="")
    dream_companies = Column(String(255), default="")
    salary_expected_lpa = Column(Float, default=0.0)
    status = Column(String(20), default="Not Placed", index=True)
    company = Column(String(100), default="None", index=True)
    role = Column(String(100), default="None", index=True)
    package_lpa = Column(Float, default=0.0)

    stages = relationship("CandidateStageModel", back_populates="student", cascade="all, delete-orphan")
    selections = relationship("DriveSelectionModel", back_populates="student", cascade="all, delete-orphan")
    experiences = relationship("InterviewExperienceModel", back_populates="student", cascade="all, delete-orphan")

class CompanyModel(Base):
    __tablename__ = "companies"

    company = Column(String(100), primary_key=True, index=True)
    domain = Column(String(100), default="General Technology")
    email = Column(String(150), nullable=False)
    status = Column(String(20), default="Pending", index=True)
    openings = Column(Integer, default=5)

    drives = relationship("DriveModel", back_populates="company_rel", cascade="all, delete-orphan")

class DriveModel(Base):
    __tablename__ = "drives"

    drive_id = Column(String(20), primary_key=True, index=True)
    company = Column(String(100), ForeignKey("companies.company"), nullable=False, index=True)
    role = Column(String(100), nullable=False, index=True)
    min_cgpa = Column(Float, default=0.0)
    eligible_depts = Column(String(255), nullable=False)
    required_skills = Column(Text, nullable=False)
    description = Column(Text, default="")
    package_lpa = Column(Float, default=0.0)
    session_date = Column(String(20), nullable=False)
    app_link = Column(String(255), default="")
    seminar_link = Column(String(255), default="")
    ppt_link = Column(String(255), default="")

    company_rel = relationship("CompanyModel", back_populates="drives")
    job_description = relationship("JobDescriptionModel", back_populates="drive_rel", uselist=False, cascade="all, delete-orphan")

class JobDescriptionModel(Base):
    __tablename__ = "job_descriptions"

    jd_id = Column(String(20), primary_key=True, index=True)
    drive_id = Column(String(20), ForeignKey("drives.drive_id"), nullable=False, index=True)
    company = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    target_domain = Column(String(100), default="")
    full_jd_text = Column(Text, nullable=False)
    min_experience_months = Column(Integer, default=0)
    package_lpa = Column(Float, default=0.0)

    drive_rel = relationship("DriveModel", back_populates="job_description")

class CandidateStageModel(Base):
    __tablename__ = "candidate_stages"

    stage_id = Column(String(20), primary_key=True, index=True)
    student_id = Column(String(20), ForeignKey("students.id"), nullable=False, index=True)
    student_name = Column(String(100), nullable=False)
    dept = Column(String(20), nullable=False)
    company = Column(String(100), nullable=False, index=True)
    role = Column(String(100), nullable=False)
    current_round = Column(String(100), nullable=False)
    next_round_date = Column(String(50), default="TBD")
    mode_location = Column(String(150), default="Virtual")

    student = relationship("StudentModel", back_populates="stages")

class DriveSelectionModel(Base):
    __tablename__ = "drive_selections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    drive_id = Column(String(20), nullable=False, index=True)
    company = Column(String(100), nullable=False, index=True)
    student_id = Column(String(20), ForeignKey("students.id"), nullable=False, index=True)
    student_name = Column(String(100), nullable=False)
    dept = Column(String(20), nullable=False)
    attended = Column(Boolean, default=False)
    selection_status = Column(String(50), default="In Progress", index=True)
    offered_role = Column(String(100), default="None")
    offered_ctc_lpa = Column(Float, default=0.0)

    student = relationship("StudentModel", back_populates="selections")

class InterviewExperienceModel(Base):
    __tablename__ = "interview_experiences"

    exp_id = Column(String(20), primary_key=True, index=True)
    student_id = Column(String(20), ForeignKey("students.id"), nullable=False, index=True)
    student_name = Column(String(100), nullable=False)
    dept = Column(String(20), nullable=False)
    company = Column(String(100), nullable=False, index=True)
    role = Column(String(100), nullable=False)
    rounds_faced = Column(Text, nullable=False)
    skills_excelled = Column(Text, default="")
    challenges_faced = Column(Text, default="")
    advice_to_crack = Column(Text, default="")
    photo_attached = Column(Boolean, default=False)
    audio_attached = Column(Boolean, default=False)
    timestamp = Column(String(20), default=datetime.now().strftime("%Y-%m-%d"))

    student = relationship("StudentModel", back_populates="experiences")

class TrainingSessionModel(Base):
    __tablename__ = "training_sessions"

    session_id = Column(String(20), primary_key=True, index=True)
    type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    target_depts = Column(String(255), nullable=False)
    instructor = Column(String(100), nullable=False)
    schedule_date = Column(String(20), nullable=False)
    timing = Column(String(50), default="10:00 AM - 01:00 PM")
    mode = Column(String(20), default="Hybrid")
    location = Column(String(150), default="Pragyan Lab")
    curriculum = Column(Text, default="")
    meeting_link = Column(String(255), default="")
    resource_link = Column(String(255), default="")

class RecruiterFeedbackModel(Base):
    __tablename__ = "recruiter_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company = Column(String(100), nullable=False, index=True)
    drive_id = Column(String(20), default="N/A")
    evaluator = Column(String(100), default="Recruiter")
    dept_evaluated = Column(String(100), nullable=False)
    overall_rating = Column(Float, default=4.0)
    strong_areas = Column(Text, default="")
    observed_gaps = Column(Text, default="")
    recommended_curriculum_fixes = Column(Text, default="")

# ----------------------------------------------------
# 3. DB INITIALIZATION & AUTOMATIC CSV INGESTION
# ----------------------------------------------------
def init_database_from_csv():
    """Creates all SQLite tables and loads CSV files into DB if tables are empty."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    try:
        # 1. Ingest Students
        if session.query(StudentModel).count() == 0:
            csv_path = os.path.join(DATA_DIR, "students.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                for _, r in df.iterrows():
                    session.add(StudentModel(
                        id=str(r["ID"]), name=str(r["Name"]), dept=str(r["Dept"]),
                        grad_year=int(r["Grad_Year"]), cgpa=float(r["CGPA"]),
                        skills=str(r["Skills"]), projects=str(r.get("Projects", "")),
                        experience=str(r.get("Experience", "")), linkedin=str(r.get("Linkedin", "")),
                        github=str(r.get("Github", "")), dream_roles=str(r.get("Dream_Roles", "")),
                        dream_companies=str(r.get("Dream_Companies", "")),
                        salary_expected_lpa=float(r.get("Salary_Expected_LPA", 0.0)),
                        status=str(r.get("Status", "Not Placed")),
                        company=str(r.get("Company", "None")),
                        role=str(r.get("Role", "None")),
                        package_lpa=float(r.get("Package_LPA", 0.0))
                    ))
                session.commit()

        # 2. Ingest Companies
        if session.query(CompanyModel).count() == 0:
            csv_path = os.path.join(DATA_DIR, "companies.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                for _, r in df.iterrows():
                    session.add(CompanyModel(
                        company=str(r["Company"]), domain=str(r.get("Domain", "General")),
                        email=str(r["Email"]), status=str(r.get("Status", "Approved")),
                        openings=int(r.get("Openings", 5))
                    ))
                session.commit()

        # 3. Ingest Drives
        if session.query(DriveModel).count() == 0:
            csv_path = os.path.join(DATA_DIR, "drives.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                for _, r in df.iterrows():
                    session.add(DriveModel(
                        drive_id=str(r["Drive_ID"]), company=str(r["Company"]),
                        role=str(r["Role"]), min_cgpa=float(r.get("Min_CGPA", 0.0)),
                        eligible_depts=str(r["Eligible_Depts"]), required_skills=str(r["Required_Skills"]),
                        description=str(r.get("Description", "")), package_lpa=float(r.get("Package_LPA", 0.0)),
                        session_date=str(r["Session_Date"]), app_link=str(r.get("App_Link", "")),
                        seminar_link=str(r.get("Seminar_Link", "")), ppt_link=str(r.get("PPT_Link", ""))
                    ))
                session.commit()

        # 4. Ingest Job Descriptions
        if session.query(JobDescriptionModel).count() == 0:
            csv_path = os.path.join(DATA_DIR, "job_descriptions.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                for _, r in df.iterrows():
                    session.add(JobDescriptionModel(
                        jd_id=str(r["JD_ID"]), drive_id=str(r["Drive_ID"]),
                        company=str(r["Company"]), role=str(r["Role"]),
                        target_domain=str(r.get("Target_Domain", "")),
                        full_jd_text=str(r["Full_JD_Text"]),
                        min_experience_months=int(r.get("Min_Experience_Months", 0)),
                        package_lpa=float(r.get("Package_LPA", 0.0))
                    ))
                session.commit()

        # 5. Ingest Candidate Stages
        if session.query(CandidateStageModel).count() == 0:
            csv_path = os.path.join(DATA_DIR, "candidate_stages.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                for _, r in df.iterrows():
                    session.add(CandidateStageModel(
                        stage_id=str(r["Stage_ID"]), student_id=str(r["Student_ID"]),
                        student_name=str(r["Student_Name"]), dept=str(r["Dept"]),
                        company=str(r["Company"]), role=str(r["Role"]),
                        current_round=str(r["Current_Round"]),
                        next_round_date=str(r.get("Next_Round_Date", "TBD")),
                        mode_location=str(r.get("Mode_Location", "Virtual"))
                    ))
                session.commit()

        # 6. Ingest Drive Selections
        if session.query(DriveSelectionModel).count() == 0:
            csv_path = os.path.join(DATA_DIR, "drive_selections.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                for _, r in df.iterrows():
                    session.add(DriveSelectionModel(
                        drive_id=str(r["Drive_ID"]), company=str(r["Company"]),
                        student_id=str(r["Student_ID"]), student_name=str(r["Student_Name"]),
                        dept=str(r["Dept"]), attended=bool(r.get("Attended", False)),
                        selection_status=str(r.get("Selection_Status", "In Progress")),
                        offered_role=str(r.get("Offered_Role", "None")),
                        offered_ctc_lpa=float(r.get("Offered_CTC_LPA", 0.0))
                    ))
                session.commit()

        # 7. Ingest Interview Experiences
        if session.query(InterviewExperienceModel).count() == 0:
            csv_path = os.path.join(DATA_DIR, "interview_experiences.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                for _, r in df.iterrows():
                    session.add(InterviewExperienceModel(
                        exp_id=str(r["Exp_ID"]), student_id=str(r["Student_ID"]),
                        student_name=str(r["Student_Name"]), dept=str(r["Dept"]),
                        company=str(r["Company"]), role=str(r["Role"]),
                        rounds_faced=str(r["Rounds_Faced"]),
                        skills_excelled=str(r.get("Skills_Excelled", "")),
                        challenges_faced=str(r.get("Challenges_Faced", "")),
                        advice_to_crack=str(r.get("Advice_To_Crack", "")),
                        photo_attached=bool(r.get("Photo_Attached", False)),
                        audio_attached=bool(r.get("Audio_Attached", False)),
                        timestamp=str(r.get("Timestamp", datetime.now().strftime("%Y-%m-%d")))
                    ))
                session.commit()

        # 8. Ingest Training Sessions
        if session.query(TrainingSessionModel).count() == 0:
            csv_path = os.path.join(DATA_DIR, "training_sessions.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                for _, r in df.iterrows():
                    session.add(TrainingSessionModel(
                        session_id=str(r["Session_ID"]), type=str(r["Type"]),
                        title=str(r["Title"]), target_depts=str(r["Target_Depts"]),
                        instructor=str(r["Instructor"]), schedule_date=str(r["Schedule_Date"]),
                        timing=str(r.get("Timing", "")), mode=str(r.get("Mode", "Hybrid")),
                        location=str(r.get("Location", "")), curriculum=str(r.get("Curriculum", "")),
                        meeting_link=str(r.get("Meeting_Link", "")), resource_link=str(r.get("Resource_Link", ""))
                    ))
                session.commit()

        # 9. Ingest Recruiter Feedback
        if session.query(RecruiterFeedbackModel).count() == 0:
            csv_path = os.path.join(DATA_DIR, "recruiter_feedback.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                for _, r in df.iterrows():
                    session.add(RecruiterFeedbackModel(
                        company=str(r["Company"]), drive_id=str(r.get("Drive_ID", "N/A")),
                        evaluator=str(r.get("Evaluator", "Lead Recruiter")),
                        dept_evaluated=str(r["Dept_Evaluated"]),
                        overall_rating=float(r.get("Overall_Rating", 4.0)),
                        strong_areas=str(r.get("Strong_Areas", "")),
                        observed_gaps=str(r.get("Observed_Gaps", "")),
                        recommended_curriculum_fixes=str(r.get("Recommended_Curriculum_Fixes", ""))
                    ))
                session.commit()

    finally:
        session.close()

# ----------------------------------------------------
# 4. HIGH-PERFORMANCE QUERY & CRUD METHODS
# ----------------------------------------------------
def get_db_session():
    return SessionLocal()

def fetch_table_as_df(model_class) -> pd.DataFrame:
    """Reads any table directly into a clean Pandas DataFrame for analytics/pivots."""
    session = SessionLocal()
    try:
        query = session.query(model_class)
        df = pd.read_sql(query.statement, session.bind)
        return df
    finally:
        session.close()

def db_add_or_update_student(student_dict: dict):
    session = SessionLocal()
    try:
        existing = session.query(StudentModel).filter(StudentModel.id == student_dict["id"]).first()
        if existing:
            for k, v in student_dict.items():
                setattr(existing, k, v)
        else:
            session.add(StudentModel(**student_dict))
        session.commit()
    finally:
        session.close()

def db_add_drive(drive_dict: dict, jd_text: str = None):
    session = SessionLocal()
    try:
        drive_obj = DriveModel(**drive_dict)
        session.add(drive_obj)
        if jd_text:
            jd_obj = JobDescriptionModel(
                jd_id=f"JD-{drive_dict['drive_id']}",
                drive_id=drive_dict["drive_id"],
                company=drive_dict["company"],
                role=drive_dict["role"],
                target_domain="Enterprise Track",
                full_jd_text=jd_text,
                package_lpa=drive_dict["package_lpa"]
            )
            session.add(jd_obj)
        session.commit()
    finally:
        session.close()

def db_add_interview_experience(exp_dict: dict):
    session = SessionLocal()
    try:
        session.add(InterviewExperienceModel(**exp_dict))
        session.commit()
    finally:
        session.close()
