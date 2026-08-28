import os
import sys
import pytest
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ----------------------------------------------------
# 1. PATH RESOLUTION & ENVIRONMENT SETUP
# ----------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.database import (
    Base,
    StudentModel,
    CompanyModel,
    DriveModel,
    JobDescriptionModel,
    CandidateStageModel,
    DriveSelectionModel,
    InterviewExperienceModel,
    TrainingSessionModel,
    RecruiterFeedbackModel
)


# ----------------------------------------------------
# 2. IN-MEMORY DATABASE FIXTURES
# ----------------------------------------------------
@pytest.fixture(scope="session")
def in_memory_engine():
    """
    Creates an isolated in-memory SQLite database engine for the test session.
    Builds all ORM table schemas once and drops them upon teardown.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(in_memory_engine):
    """
    Provides a transactional database session for each test function.
    Automatically rolls back any committed mutations after test execution.
    """
    connection = in_memory_engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = session_factory()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ----------------------------------------------------
# 3. SAMPLE DATA PAYLOAD FIXTURES
# ----------------------------------------------------
@pytest.fixture
def sample_student_payload():
    """Provides a realistic student dictionary for ORM and CRUD testing."""
    return {
        "id": "STU_TEST_001",
        "name": "Arjun Sharma",
        "dept": "AIML",
        "college": "Main Campus (Bengaluru)",
        "grad_year": 2026,
        "cgpa": 9.15,
        "skills": "Python, PyTorch, LangChain, FastEngine, Docker, SQL",
        "projects": "Autonomous RAG Evaluation Engine with FAISS and Vector Retrieval",
        "experience": "AI Research Fellow (6 months)",
        "linkedin": "https://linkedin.com/in/arjun-sharma-test",
        "github": "https://github.com/arjun-test",
        "dream_roles": "Generative AI Engineer",
        "dream_companies": "Synthlinx AI, NVIDIA",
        "salary_expected_lpa": 24.0,
        "status": "Placed",
        "company": "Synthlinx AI",
        "role": "Generative AI Engineer",
        "package_lpa": 26.5
    }


@pytest.fixture
def sample_company_payload():
    """Provides a realistic corporate recruiting partner dictionary."""
    return {
        "company": "NVIDIA",
        "domain": "AI, Generative Systems & Big Data",
        "email": "campus-hiring@nvidia.com",
        "status": "Approved",
        "openings": 15
    }


@pytest.fixture
def sample_drive_payload():
    """Provides a campus recruitment drive dictionary."""
    return {
        "drive_id": "DRV_TEST_001",
        "company": "NVIDIA",
        "role": "LLM Inference Acceleration Engineer",
        "min_cgpa": 8.0,
        "eligible_depts": "CSE, AIML, AIDS, ECE",
        "required_skills": "Python, CUDA, TensorRT, C++, PyTorch",
        "description": "Develop low-latency model serving pipelines with TensorRT and Triton server.",
        "package_lpa": 28.0,
        "session_date": "2026-09-15",
        "app_link": "https://nvidia.com/careers",
        "seminar_link": "https://meet.google.com/nvd-test",
        "ppt_link": "https://pragyan.edu/resources/nvidia_deck.pdf"
    }


@pytest.fixture
def sample_candidate_stage_payload():
    """Provides a recruitment round stage tracking payload."""
    return {
        "stage_id": "STG_TEST_001",
        "student_id": "STU_TEST_001",
        "student_name": "Arjun Sharma",
        "dept": "AIML",
        "company": "NVIDIA",
        "role": "LLM Inference Acceleration Engineer",
        "current_round": "Round 2: Technical Architecture",
        "next_round_date": "2026-09-20 11:00 AM",
        "mode_location": "Virtual Google Meet"
    }


@pytest.fixture
def sample_training_session_payload():
    """Provides a skill bootcamp/workshop dictionary."""
    return {
        "session_id": "TRN_TEST_101",
        "type": "Bootcamp",
        "title": "Generative AI & Agentic Workflows with LangGraph",
        "target_depts": "CSE, AIML, AIDS, ISE",
        "instructor": "Dr. Sateesh Ambesange",
        "schedule_date": "2026-09-10",
        "timing": "10:00 AM - 04:00 PM",
        "mode": "Hybrid",
        "location": "Pragyan DeepTech Lab",
        "curriculum": "1. Multi-Agent Swarms 2. Vector DB Indexing 3. FastEngine APIs",
        "meeting_link": "https://zoom.us/j/pragyan-genai-bootcamp",
        "resource_link": "https://github.com/pragyan-ai/agentic-curriculum-2026"
    }


@pytest.fixture
def sample_recruiter_feedback_payload():
    """Provides a post-drive recruiter assessment dictionary."""
    return {
        "company": "NVIDIA",
        "drive_id": "DRV_TEST_001",
        "evaluator": "Director of Silicon Software",
        "dept_evaluated": "AIML, CSE",
        "overall_rating": 4.6,
        "strong_areas": "Vector Retrieval, CUDA kernel reasoning, clean Python syntax",
        "observed_gaps": "Model Quantization benchmarking and KV-cache optimizations",
        "recommended_curriculum_fixes": "Introduce TensorRT inference labs and fast serving benchmarks"
    }
