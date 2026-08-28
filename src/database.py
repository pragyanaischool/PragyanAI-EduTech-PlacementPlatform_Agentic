import os
import random
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
    event
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# ----------------------------------------------------
# 1. DATABASE CONFIGURATION & ENGINE INITIALIZATION
# ----------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(PROJECT_ROOT, "database")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "placement_portal.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
    echo=False
)

# Enable WAL mode on SQLite to prevent locks and concurrency conflicts
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def hash_password(password: str) -> str:
    """Computes a SHA-256 hash for secure credential persistence."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ----------------------------------------------------
# 2. RELATIONAL ORM SCHEMAS
# ----------------------------------------------------
class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(64), nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(String(50), nullable=False, index=True)
    organization_or_dept = Column(String(120), default="")
    status = Column(String(20), default="Pending", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_by = Column(String(80), default="PragyanAI Admin")


class StudentModel(Base):
    __tablename__ = "students"

    id = Column(String(20), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    dept = Column(String(20), nullable=False, index=True)
    college = Column(String(100), default="Main Campus (Bengaluru)", index=True)
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


Base.metadata.create_all(bind=engine)


# ----------------------------------------------------
# 3. CSV SEED INGESTION & DATA SYNTHESIS
# ----------------------------------------------------
DEPTS_TAXONOMY = {
    "CSE": {"weight": 0.22, "skills": ["Python", "Java", "C++", "FastAPI", "React", "Docker", "Kubernetes", "SQL", "Redis", "Kafka", "Data Structures", "System Design", "Go"]},
    "AIML": {"weight": 0.16, "skills": ["Python", "PyTorch", "TensorFlow", "LangChain", "LangGraph", "FAISS", "Scikit-Learn", "OpenCV", "NLP", "RAG", "MLOps", "HuggingFace", "TensorRT", "CUDA"]},
    "AIDS": {"weight": 0.14, "skills": ["Python", "R", "SQL", "Pandas", "PowerBI", "Tableau", "PySpark", "Machine Learning", "Data Mining", "Statistics", "BigQuery", "Snowflake"]},
    "ISE": {"weight": 0.12, "skills": ["Java", "Spring Boot", "Go", "AWS", "GCP", "Microservices", "REST APIs", "PostgreSQL", "CI/CD", "Linux", "Algorithms", "Terraform"]},
    "ECE": {"weight": 0.14, "skills": ["Embedded C", "C++", "Verilog", "VHDL", "ARM Cortex", "RTOS", "Linux Device Drivers", "PCB Design", "SPI", "I2C", "DSP", "SystemVerilog"]},
    "EEE": {"weight": 0.08, "skills": ["MATLAB", "Simulink", "PLC/SCADA", "Power Electronics", "Embedded C", "Control Systems", "IoT", "AutoCAD Electrical", "BMS", "Inverter Design"]},
    "MECH": {"weight": 0.06, "skills": ["SolidWorks", "AutoCAD", "ANSYS", "CATIA", "GD&T", "Thermodynamics", "Python", "FEA", "CFD", "CAM", "Additive Manufacturing"]},
    "ROBOTICS": {"weight": 0.04, "skills": ["ROS2", "Python", "C++", "Gazebo", "SLAM", "Computer Vision", "Kinematics", "Microcontrollers", "LiDAR Interfacing", "Path Planning"]},
    "CIVIL": {"weight": 0.02, "skills": ["AutoCAD Civil 3D", "Revit", "STAAD Pro", "GIS", "Structural Analysis", "Geotechnical Modeling", "Primavera"]},
    "BIOTECH": {"weight": 0.02, "skills": ["Bioinformatics", "Python", "R", "Biostatistics", "CRISPR Data Analysis", "Molecular Docking", "NGS Pipelines"]}
}

COLLEGES_LIST = [
    "Main Campus (Bengaluru)",
    "East Campus (Tech Park)",
    "South Campus (DeepTech Lab)"
]

DOMAINS_DATA = {
    "Tier-1 Tech & Cloud Infrastructure": [
        "Google", "Microsoft", "Amazon", "Apple", "Meta", "Adobe", "Salesforce", "Oracle",
        "Atlassian", "Uber", "Cisco", "VMware", "ServiceNow", "Intuit", "PayPal"
    ],
    "AI, Generative Systems & Big Data": [
        "NVIDIA", "OpenAI", "Synthlinx AI", "Databricks", "Snowflake", "Palantir", "Cohere",
        "Scale AI", "C3.ai", "Hugging Face", "Fractal Analytics", "Tiger Analytics"
    ],
    "Semiconductors, VLSI & Embedded": [
        "Qualcomm", "Intel", "Texas Instruments", "AMD", "Broadcom", "MediaTek", "NXP Semiconductors",
        "Synopsys", "Cadence Design", "Arm", "Microchip Technology", "Analog Devices"
    ],
    "Automotive, EV & Robotics": [
        "Tesla", "Tata Motors", "Mahindra & Mahindra", "Bosch", "Continental", "Mercedes-Benz R&D",
        "Volvo Group", "Ather Energy", "Ola Electric", "Hyundai Mobis", "ZF Group"
    ],
    "FinTech, Banking & Quant": [
        "Goldman Sachs", "Morgan Stanley", "JPMorgan Chase", "Barclays", "American Express",
        "BNY Mellon", "Deutsche Bank", "Mastercard", "Visa"
    ],
    "Enterprise IT, Consulting & Systems": [
        "Infosys", "TCS", "Wipro", "Accenture", "Capgemini", "Cognizant", "HCLTech", "LTI-Mindtree",
        "Tech Mahindra", "IBM", "Deloitte", "PwC", "EY"
    ]
}

DOMAIN_ROLES_DATA = {
    "Tier-1 Tech & Cloud Infrastructure": ["Software Development Engineer I (SDE-1)", "Backend Microservices Architect", "Cloud Platform Engineer", "Site Reliability Engineer (SRE)", "Full Stack Developer"],
    "AI, Generative Systems & Big Data": ["Generative AI Engineer", "LLM Inference Specialist", "RAG Pipeline Architect", "Machine Learning Engineer", "Computer Vision Specialist"],
    "Semiconductors, VLSI & Embedded": ["Firmware & Kernel Engineer", "Silicon Bring-Up Specialist", "ASIC Design Verification Engineer", "RTL Design Engineer", "RTOS Systems Architect"],
    "Automotive, EV & Robotics": ["EV Battery Management System (BMS) Engineer", "AUTOSAR Software Architect", "ADAS Perception Engineer", "Robotics Navigation Specialist (ROS2)"],
    "FinTech, Banking & Quant": ["Quantitative Analyst", "Financial Risk Software Engineer", "Payment Gateway Engineer", "Algorithmic Systems Engineer"],
    "Enterprise IT, Consulting & Systems": ["Associate Consultant (Enterprise AI)", "Specialist Programmer", "Digital Transformation Architect", "Cybersecurity Analyst"]
}

FIRST_NAMES = ["Aarav", "Priya", "Rohan", "Sneha", "Ananya", "Kiran", "Vikram", "Neha", "Aditya", "Pooja", "Rahul", "Divya", "Sanjay", "Meera", "Varun", "Kavya", "Siddharth", "Ishita", "Arjun", "Ritu", "Gaurav", "Swati", "Naveen", "Tanvi", "Akash", "Shruti"]
LAST_NAMES = ["Sharma", "Patel", "Iyer", "Reddy", "Roy", "Varma", "Sen", "Nair", "Kulkarni", "Hegde", "Deshmukh", "Bhat", "Rao", "Joshi", "Gupta", "Agarwal", "Mishra", "Pillai", "Menon", "Shetty"]


def seed_default_users_safe(session):
    """Safely seeds default users only if they do not already exist in the database."""
    default_users_data = [
        {"username": "admin", "email": "admin@pragyan.ai", "password_hash": hash_password("admin123"), "full_name": "PragyanAI Executive Admin", "role": "PragyanAI Engine", "organization_or_dept": "PragyanAI Core", "status": "Approved", "approved_by": "System Genesis"},
        {"username": "placement_head", "email": "head@pragyan.edu", "password_hash": hash_password("head123"), "full_name": "Dr. Director Placement", "role": "Placement Head", "organization_or_dept": "Central T&P Cell", "status": "Approved", "approved_by": "PragyanAI Admin"},
        {"username": "student_arjun", "email": "arjun@pragyan.edu", "password_hash": hash_password("student123"), "full_name": "Arjun Sharma", "role": "Student", "organization_or_dept": "AIML", "status": "Approved", "approved_by": "Placement Cell"},
        {"username": "nvidia_recruiter", "email": "hiring@nvidia.com", "password_hash": hash_password("nvidia123"), "full_name": "Lead Technical Recruiter", "role": "Hiring Partner", "organization_or_dept": "NVIDIA Corporation", "status": "Approved", "approved_by": "Placement Head"}
    ]

    for u in default_users_data:
        existing = session.query(UserModel).filter(UserModel.username == u["username"]).first()
        if not existing:
            session.add(UserModel(**u))
    session.commit()


def bootstrap_synthetic_dataset(session):
    """Dynamically populates 1,500+ records across all 10 schemas."""
    random.seed(42)
    np.random.seed(42)

    # 1. Safely Seed Users
    seed_default_users_safe(session)

    # 2. Seed Companies, Drives, and Job Descriptions
    companies_objs = []
    drives_objs = []
    jds_objs = []
    drive_counter = 1

    for domain, comp_names in DOMAINS_DATA.items():
        roles_pool = DOMAIN_ROLES_DATA[domain]
        for comp in comp_names:
            base_ctc = round(random.uniform(18.0, 32.0) if "Tier-1" in domain or "AI" in domain else random.uniform(8.0, 20.0), 2)
            min_cgpa = round(random.uniform(7.5, 8.5) if "Tier-1" in domain else random.uniform(6.5, 7.5), 1)
            eligible_depts = ["CSE", "AIML", "AIDS", "ISE"] if "Tier-1" in domain or "AI" in domain else ["ECE", "EEE", "CSE", "ROBOTICS"]

            companies_objs.append(CompanyModel(
                company=comp,
                domain=domain,
                email=f"campus-hiring@{comp.lower().replace(' ', '').replace('&', 'and')}.com",
                status="Approved" if random.random() > 0.05 else "Pending",
                openings=random.randint(10, 45)
            ))

            for role in roles_pool[:2]:
                drive_id = f"DRV-{drive_counter:03d}"
                role_ctc = round(base_ctc * random.uniform(0.95, 1.15), 2)
                req_skills = ", ".join(DEPTS_TAXONOMY[eligible_depts[0]]["skills"][:6])
                full_jd = f"Hiring for {role} at {comp} under {domain}. Mandates proficiency in {req_skills} and low-latency architectural delivery."

                drives_objs.append(DriveModel(
                    drive_id=drive_id,
                    company=comp,
                    role=role,
                    min_cgpa=min_cgpa,
                    eligible_depts=", ".join(eligible_depts),
                    required_skills=req_skills,
                    description=full_jd,
                    package_lpa=role_ctc,
                    session_date=(datetime.now() + timedelta(days=random.randint(5, 45))).strftime("%Y-%m-%d"),
                    app_link=f"https://careers.{comp.lower().replace(' ', '')}.com",
                    seminar_link=f"https://meet.google.com/{comp.lower().replace(' ', '')}-drive",
                    ppt_link=f"https://pragyan.edu/resources/{comp.lower().replace(' ', '')}_deck.pdf"
                ))

                jds_objs.append(JobDescriptionModel(
                    jd_id=f"JD-{drive_counter + 1000}",
                    drive_id=drive_id,
                    company=comp,
                    role=role,
                    target_domain=domain,
                    full_jd_text=full_jd,
                    min_experience_months=0,
                    package_lpa=role_ctc
                ))
                drive_counter += 1

    session.add_all(companies_objs)
    session.add_all(drives_objs)
    session.add_all(jds_objs)
    session.commit()

    # 3. Seed 1,500 Students & Stages
    dept_keys = list(DEPTS_TAXONOMY.keys())
    dept_weights = [DEPTS_TAXONOMY[d]["weight"] for d in dept_keys]
    
    students_objs = []
    stages_objs = []
    selections_objs = []
    exp_objs = []

    for i in range(1, 1501):
        stu_id = f"STU{i:04d}"
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        name = f"{fname} {lname}"
        dept = np.random.choice(dept_keys, p=dept_weights)
        college = random.choice(COLLEGES_LIST)
        grad_year = np.random.choice([2024, 2025, 2026], p=[0.20, 0.50, 0.30])
        cgpa = round(float(np.clip(np.random.normal(7.85, 0.95), 5.5, 9.95)), 2)

        skills = random.sample(DEPTS_TAXONOMY[dept]["skills"], random.randint(4, 7))
        skills_str = ", ".join(skills)
        projects = f"Engineering capstone in {dept}: Implemented architecture prototype using {skills[0]} and {skills[1]}."
        experience = f"{random.choice(['Intern at Core Industry Partner', 'Research Assistant at PragyanAI Labs', 'Open Source Contributor'])} ({random.randint(2, 6)} months)."

        placement_prob = 0.88 if grad_year == 2024 else (0.75 if grad_year == 2025 else 0.30)
        if cgpa < 6.5:
            placement_prob *= 0.4
        elif cgpa > 8.8:
            placement_prob = min(placement_prob * 1.25, 0.98)

        is_placed = random.random() < placement_prob

        if is_placed:
            status = "Placed"
            chosen_drive = random.choice(drives_objs)
            comp_name = chosen_drive.company
            role_name = chosen_drive.role
            package_lpa = chosen_drive.package_lpa

            selections_objs.append(DriveSelectionModel(
                drive_id=chosen_drive.drive_id,
                company=comp_name,
                student_id=stu_id,
                student_name=name,
                dept=dept,
                attended=True,
                selection_status="Selected",
                offered_role=role_name,
                offered_ctc_lpa=package_lpa
            ))

            stages_objs.append(CandidateStageModel(
                stage_id=f"STG-{i:04d}",
                student_id=stu_id,
                student_name=name,
                dept=dept,
                company=comp_name,
                role=role_name,
                current_round="Offer Extended (Selected)",
                next_round_date="Completed",
                mode_location=f"{comp_name} Corporate Campus"
            ))

            if len(exp_objs) < 150:
                exp_objs.append(InterviewExperienceModel(
                    exp_id=f"EXP-{len(exp_objs) + 1001}",
                    student_id=stu_id,
                    student_name=name,
                    dept=dept,
                    company=comp_name,
                    role=role_name,
                    rounds_faced="Round 1: Online Coding, Round 2: Architecture & LLD, Round 3: Leadership/HR",
                    skills_excelled=f"{skills[0]}, {skills[1]}, Low-Level Invariants",
                    challenges_faced="Edge failure recovery, race conditions, and distributed caching trade-offs.",
                    advice_to_crack="Dry run edge cases out loud and state algorithmic complexity assumptions upfront.",
                    photo_attached=True if random.random() > 0.3 else False,
                    audio_attached=True if random.random() > 0.2 else False,
                    timestamp=(datetime.now() - timedelta(days=random.randint(2, 45))).strftime("%Y-%m-%d")
                ))
        else:
            status = "Not Placed"
            comp_name = "None"
            role_name = "None"
            package_lpa = 0.0

            if random.random() < 0.35:
                random_drive = random.choice(drives_objs)
                stages_objs.append(CandidateStageModel(
                    stage_id=f"STG-{i:04d}",
                    student_id=stu_id,
                    student_name=name,
                    dept=dept,
                    company=random_drive.company,
                    role=random_drive.role,
                    current_round=random.choice(["Round 1: Screening Cleared", "Round 2: Technical Interview", "Round 3: Final Managerial"]),
                    next_round_date=(datetime.now() + timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d 10:30 AM"),
                    mode_location="Virtual / MS Teams"
                ))

        students_objs.append(StudentModel(
            id=stu_id,
            name=name,
            dept=dept,
            college=college,
            grad_year=grad_year,
            cgpa=cgpa,
            skills=skills_str,
            projects=projects,
            experience=experience,
            linkedin=f"https://linkedin.com/in/{fname.lower()}-{lname.lower()}-{i}",
            github=f"https://github.com/{fname.lower()}{i}",
            dream_roles=DOMAIN_ROLES_DATA["Tier-1 Tech & Cloud Infrastructure"][0],
            dream_companies="Google, NVIDIA",
            salary_expected_lpa=round(float(np.clip(cgpa * 2.2 + random.uniform(-1, 3), 6.0, 32.0)), 1),
            status=status,
            company=comp_name,
            role=role_name,
            package_lpa=package_lpa
        ))

    session.add_all(students_objs)
    session.add_all(stages_objs)
    session.add_all(selections_objs)
    session.add_all(exp_objs)

    # 4. Seed Training Sessions & Recruiter Feedback
    session.add_all([
        TrainingSessionModel(
            session_id="TRN-101",
            type="Bootcamp",
            title="Generative AI & Agentic Workflows with LangGraph",
            target_depts="CSE, AIML, AIDS, ISE",
            instructor="Dr. Sateesh Ambesange",
            schedule_date=(datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            timing="10:00 AM - 04:00 PM",
            mode="Hybrid",
            location="Pragyan DeepTech Lab / Zoom",
            curriculum="1. Multi-Agent Swarms 2. Vector DB Indexing 3. Production RAG 4. FastEngine APIs",
            meeting_link="https://zoom.us/j/pragyan-genai-bootcamp",
            resource_link="https://github.com/pragyan-ai/agentic-curriculum-2026"
        ),
        TrainingSessionModel(
            session_id="TRN-102",
            type="Workshop",
            title="Bare-Metal ARM Firmware & RTOS Preemption Intensive",
            target_depts="ECE, EEE, ROBOTICS",
            instructor="Lead Architect (Qualcomm)",
            schedule_date=(datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d"),
            timing="09:30 AM - 01:30 PM",
            mode="Offline",
            location="Embedded Systems Lab (Block B)",
            curriculum="1. ARM Cortex-M Register Mapping 2. Mutexes & Priority Inversion 3. Custom SPI Drivers",
            meeting_link="N/A (Physical Event)",
            resource_link="https://pragyan.edu/resources/arm_firmware_workshop.pdf"
        ),
        TrainingSessionModel(
            session_id="TRN-103",
            type="Masterclass",
            title="Distributed Systems & Raft Consensus in High-Scale FinTech",
            target_depts="CSE, ISE, AIDS",
            instructor="Principal Systems Engineer (Amazon)",
            schedule_date=(datetime.now() + timedelta(days=12)).strftime("%Y-%m-%d"),
            timing="02:00 PM - 05:00 PM",
            mode="Online",
            location="Google Meet",
            curriculum="1. Partition Tolerance 2. Log Replication 3. High-Throughput RPCs",
            meeting_link="https://meet.google.com/distributed-systems-talk",
            resource_link="https://pragyan.edu/resources/distributed_consensus.pdf"
        )
    ])

    session.add_all([
        RecruiterFeedbackModel(
            company="Google",
            drive_id="DRV-001",
            evaluator="Staff Engineering Manager",
            dept_evaluated="CSE, AIML, ISE",
            overall_rating=4.3,
            strong_areas="Strong algorithmic thinking and clean Python/C++ code structure.",
            observed_gaps="Struggled with multi-threaded synchronization, concurrency locks, and distributed caching (Redis).",
            recommended_curriculum_fixes="Include hands-on low-level system design labs and live debugging sessions."
        ),
        RecruiterFeedbackModel(
            company="Qualcomm",
            drive_id="DRV-025",
            evaluator="Senior Director of Silicon Software",
            dept_evaluated="ECE, EEE",
            overall_rating=3.9,
            strong_areas="Good basic digital design and state machine understanding.",
            observed_gaps="Lack of hands-on pointer arithmetic in bare-metal C and RTOS scheduler mechanics.",
            recommended_curriculum_fixes="Introduce hardware-in-the-loop debugging with ARM Cortex-M microcontrollers."
        ),
        RecruiterFeedbackModel(
            company="Synthlinx AI",
            drive_id="DRV-019",
            evaluator="Head of AI Research",
            dept_evaluated="AIML, AIDS",
            overall_rating=4.5,
            strong_areas="Excellent grasp of RAG chunking and vector index retrieval.",
            observed_gaps="Need deeper exposure to LLM quantization, KV-caching, and inference engine latency benchmarking.",
            recommended_curriculum_fixes="Run production agent deployment hackathons with LangGraph and FastEngine."
        )
    ])

    session.commit()


def init_database_from_csv():
    """Initializes tables and seeds default records safely."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        # 1. Ensure default users exist
        seed_default_users_safe(session)
        
        # 2. Ensure students & drives exist
        if session.query(StudentModel).count() == 0:
            bootstrap_synthetic_dataset(session)
    finally:
        session.close()


# ----------------------------------------------------
# 4. CRUD OPERATIONS & EXPORTED HELPERS
# ----------------------------------------------------
def get_db_session():
    """Provides a thread-safe database session."""
    return SessionLocal()


def fetch_table_as_df(model_class) -> pd.DataFrame:
    """Reads any SQLAlchemy model table into a Pandas DataFrame."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        query = session.query(model_class)
        return pd.read_sql(query.statement, session.bind)
    finally:
        session.close()


def authenticate_user(username: str, password: str):
    """Validates user credentials with auto-healing schema check."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        if session.query(UserModel).count() == 0:
            init_database_from_csv()

        user = session.query(UserModel).filter(UserModel.username == username.strip()).first()
        if not user:
            return False, None, "User does not exist in the institutional registry."
        
        hashed_input = hash_password(password)
        if user.password_hash != hashed_input:
            return False, None, "Invalid credentials provided."
        
        if user.status != "Approved":
            return False, None, f"Account status is '{user.status}'. Approval by PragyanAI Admin is required."
        
        return True, {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "organization_or_dept": user.organization_or_dept,
            "status": user.status
        }, "Authenticated successfully."
    finally:
        session.close()


def register_user(username: str, email: str, password: str, full_name: str, role: str, org_or_dept: str = ""):
    """Creates a new registration request with status 'Pending' awaiting PragyanAI review."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        if session.query(UserModel).filter(UserModel.username == username.strip()).first():
            return False, "Username already registered."
        if session.query(UserModel).filter(UserModel.email == email.strip().lower()).first():
            return False, "Email address is already in use."

        new_user = UserModel(
            username=username.strip(),
            email=email.strip().lower(),
            password_hash=hash_password(password),
            full_name=full_name.strip(),
            role=role,
            organization_or_dept=org_or_dept.strip(),
            status="Pending",
            approved_by="Awaiting PragyanAI Approval"
        )
        session.add(new_user)
        session.commit()
        return True, "Registration request submitted. Awaiting PragyanAI / Placement Directorate approval."
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


def update_user_status(user_id: int, new_status: str, approved_by_name: str = "PragyanAI Admin"):
    """Approves or Rejects a user registration and syncs changes."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        user = session.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            user.status = new_status
            user.approved_by = approved_by_name
            session.commit()
            return True, f"User {user.username} has been {new_status}."
        return False, "User not found."
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


def get_all_users_df() -> pd.DataFrame:
    """Returns all users for approval review tables."""
    Base.metadata.create_all(bind=engine)
    return fetch_table_as_df(UserModel)


def db_add_or_update_student(student_dict: dict):
    """Inserts or updates a student profile."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        existing = session.query(StudentModel).filter(StudentModel.id == student_dict["id"]).first()
        if existing:
            for k, v in student_dict.items():
                setattr(existing, k, v)
        else:
            session.add(StudentModel(**student_dict))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_add_drive(drive_dict: dict, jd_text: str = None):
    """Inserts a new campus drive and attached job description atomically."""
    Base.metadata.create_all(bind=engine)
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
                package_lpa=drive_dict.get("package_lpa", 0.0)
            )
            session.add(jd_obj)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_add_company(company_dict: dict):
    """Registers a hiring partner organization."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        session.add(CompanyModel(**company_dict))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_update_company_status(company_name: str, new_status: str = "Approved"):
    """Approves or rejects a company partner account."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        comp = session.query(CompanyModel).filter(CompanyModel.company == company_name).first()
        if comp:
            comp.status = new_status
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_add_training_session(session_dict: dict):
    """Inserts a new training session or workshop."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        session.add(TrainingSessionModel(**session_dict))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_update_candidate_stage(stage_dict: dict):
    """Upserts a candidate recruitment stage progression."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        existing = session.query(CandidateStageModel).filter(
            CandidateStageModel.student_id == stage_dict["student_id"],
            CandidateStageModel.company == stage_dict["company"]
        ).first()

        if existing:
            for k, v in stage_dict.items():
                setattr(existing, k, v)
        else:
            session.add(CandidateStageModel(**stage_dict))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_add_interview_experience(exp_dict: dict):
    """Inserts candidate multimedia debrief record."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        session.add(InterviewExperienceModel(**exp_dict))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
