import pytest
import pandas as pd
import streamlit as st
from src.rag_engine import (
    clean_tokens,
    calculate_cosine_similarity,
    rag_resume_vs_jd_analysis,
    analyze_selection_differences,
    handle_placement_chat
)


# ----------------------------------------------------
# 1. TEXT VECTORIZATION & TOKENIZER TESTS
# ----------------------------------------------------
def test_clean_tokens_standard():
    """Validates alphanumeric extraction, stop character stripping, and lowercase normalization."""
    raw_text = "Python 3.11, PyTorch 2.0 & FastEngine / Docker (Kubernetes)!"
    tokens = clean_tokens(raw_text)
    assert "python" in tokens
    assert "pytorch" in tokens
    assert "fastengine" in tokens
    assert "docker" in tokens
    assert "kubernetes" in tokens
    assert "&" not in tokens
    assert "/" not in tokens
    assert "(" not in tokens
    assert ")" not in tokens


def test_clean_tokens_edge_cases():
    """Validates tokenization behavior on empty, numeric, or single-character inputs."""
    assert clean_tokens("") == set()
    assert clean_tokens(None) == set()
    assert clean_tokens("a b c d") == set()  # Tokens with length <= 1 are omitted
    assert clean_tokens("C++ Go SQL") == {"go", "sql"}


# ----------------------------------------------------
# 2. COSINE SIMILARITY FORMULATION TESTS
# ----------------------------------------------------
def test_calculate_cosine_similarity_orthogonal():
    """Validates that disjoint token sets yield zero similarity."""
    set_a = {"python", "fastapi", "docker"}
    set_b = {"solidworks", "ansys", "catia"}
    sim = calculate_cosine_similarity(set_a, set_b)
    assert sim == 0.0


def test_calculate_cosine_similarity_identical():
    """Validates that identical token sets produce unit similarity (1.0)."""
    set_a = {"python", "pytorch", "langchain", "faiss"}
    sim = calculate_cosine_similarity(set_a, set_a)
    assert pytest.approx(sim, 0.001) == 1.0


def test_calculate_cosine_similarity_partial_overlap():
    """Validates fractional cosine similarity computation on intersecting sets."""
    set_a = {"python", "pytorch", "cuda", "c++"}
    set_b = {"python", "pytorch", "tensorrt", "docker"}
    sim = calculate_cosine_similarity(set_a, set_b)
    assert 0.0 < sim < 1.0
    # Expected: 2 common / sqrt(4 * 4) = 2/4 = 0.5
    assert pytest.approx(sim, 0.001) == 0.5


def test_calculate_cosine_similarity_empty():
    """Validates handling of empty inputs."""
    assert calculate_cosine_similarity(set(), {"python"}) == 0.0
    assert calculate_cosine_similarity(set(), set()) == 0.0


# ----------------------------------------------------
# 3. RAG RESUME VS. JOB DESCRIPTION MATCHER TESTS
# ----------------------------------------------------
def test_rag_resume_vs_jd_analysis_matched():
    """Validates end-to-end vector RAG matching on aligned candidate and JD profiles."""
    st.session_state.students = pd.DataFrame([{
        "ID": "STU_RAG_001",
        "Name": "Kiran Rao",
        "Dept": "AIML",
        "CGPA": 9.2,
        "Skills": "Python, PyTorch, LangChain, FAISS, FastEngine, Docker",
        "Projects": "Agentic Multi-Modal RAG pipeline using LangGraph and TensorRT",
        "Experience": "AI Research Fellow (6 months)",
        "Dream_Roles": "Generative AI Engineer"
    }])

    st.session_state.drives = pd.DataFrame([{
        "Drive_ID": "DRV_RAG_001",
        "Company": "Synthlinx AI",
        "Role": "Generative AI Systems Architect",
        "Required_Skills": "Python, PyTorch, LangChain, FAISS, Docker, CUDA",
        "Description": "Design high-throughput agentic workflows and low-latency inference pipelines."
    }])

    st.session_state.job_descriptions = pd.DataFrame([{
        "JD_ID": "JD_RAG_001",
        "Drive_ID": "DRV_RAG_001",
        "Company": "Synthlinx AI",
        "Role": "Generative AI Systems Architect",
        "Full_JD_Text": "Looking for architects experienced in Python, PyTorch, LangChain, and Dockerized inference servers."
    }])

    result = rag_resume_vs_jd_analysis("STU_RAG_001", "DRV_RAG_001")

    assert result["candidate_id"] == "STU_RAG_001"
    assert result["candidate_name"] == "Kiran Rao"
    assert result["company"] == "Synthlinx AI"
    assert result["match_score"] >= 75
    assert "Strong Fit" in result["recommendation"]
    assert any("Python" in s or "PyTorch" in s for s in result["matched_skills"])


def test_rag_resume_vs_jd_analysis_missing_records():
    """Validates graceful degradation when target candidate or drive ID is not in state."""
    st.session_state.students = pd.DataFrame()
    st.session_state.drives = pd.DataFrame()
    st.session_state.job_descriptions = pd.DataFrame()

    result = rag_resume_vs_jd_analysis("NON_EXISTENT_ID", "DRV_999")
    assert result["match_score"] == 0
    assert result["recommendation"] in ["Data Unavailable", "Record Not Found"]


# ----------------------------------------------------
# 4. SELECTION DELTA ENGINE TESTS
# ----------------------------------------------------
def test_analyze_selection_differences_success():
    """Validates calculation of CGPA deltas and differentiating factors."""
    st.session_state.drive_selections = pd.DataFrame([
        {
            "Drive_ID": "DRV_SEL_01",
            "Company": "Google",
            "Student_ID": "STU_001",
            "Selection_Status": "Selected"
        },
        {
            "Drive_ID": "DRV_SEL_01",
            "Company": "Google",
            "Student_ID": "STU_002",
            "Selection_Status": "Rejected"
        }
    ])

    st.session_state.students = pd.DataFrame([
        {"ID": "STU_001", "CGPA": 9.4, "Name": "Placed Scholar"},
        {"ID": "STU_002", "CGPA": 7.1, "Name": "Unplaced Applicant"}
    ])

    diff_report = analyze_selection_differences("Google")
    assert diff_report is not None
    assert diff_report["company"] == "Google"
    assert diff_report["selected_count"] == 1
    assert diff_report["unplaced_count"] == 1
    assert diff_report["avg_selected_cgpa"] == 9.4
    assert diff_report["avg_unplaced_cgpa"] == 7.1
    assert len(diff_report["differentiating_factors"]) >= 3


def test_analyze_selection_differences_empty():
    """Validates selection delta engine behavior when company data is absent."""
    st.session_state.drive_selections = pd.DataFrame()
    st.session_state.students = pd.DataFrame()

    assert analyze_selection_differences("Unknown Corp") is None


# ----------------------------------------------------
# 5. NATURAL LANGUAGE QUERY ROUTER TESTS
# ----------------------------------------------------
def test_handle_placement_chat_highest_package():
    """Validates top package query routing and formatting."""
    st.session_state.students = pd.DataFrame([
        {
            "ID": "STU_TOP",
            "Name": "Priya Nair",
            "Dept": "CSE",
            "Status": "Placed",
            "Company": "Google",
            "Role": "Staff Software Engineer",
            "Package_LPA": 44.5
        }
    ])
    st.session_state.drives = pd.DataFrame()
    st.session_state.candidate_stages = pd.DataFrame()
    st.session_state.training_sessions = pd.DataFrame()
    st.session_state.recruiter_feedback = pd.DataFrame()

    response = handle_placement_chat("What is the highest package secured?", "Student")
    assert "44.5" in response
    assert "Google" in response
    assert "Priya Nair" in response


def test_handle_placement_chat_candidate_stage_lookup():
    """Validates student round progression query routing with contextual user ID."""
    st.session_state.candidate_stages = pd.DataFrame([
        {
            "Student_ID": "STU_ACTIVE_01",
            "Company": "Qualcomm",
            "Role": "Firmware Engineer",
            "Current_Round": "Round 2: Bare-Metal Architecture",
            "Next_Round_Date": "2026-09-05 10:00 AM",
            "Mode_Location": "Virtual MS Teams"
        }
    ])
    st.session_state.students = pd.DataFrame()
    st.session_state.drives = pd.DataFrame()
    st.session_state.training_sessions = pd.DataFrame()
    st.session_state.recruiter_feedback = pd.DataFrame()

    response = handle_placement_chat(
        "What is my next round schedule?",
        "Student",
        user_context={"student_id": "STU_ACTIVE_01"}
    )
    assert "Qualcomm" in response
    assert "Round 2: Bare-Metal Architecture" in response
    assert "2026-09-05" in response


def test_handle_placement_chat_workshop_schedule():
    """Validates skill bootcamp and training session query routing."""
    st.session_state.training_sessions = pd.DataFrame([
        {
            "Type": "Bootcamp",
            "Title": "Distributed Systems Masterclass",
            "Instructor": "Dr. Sateesh Ambesange",
            "Schedule_Date": "2026-09-12",
            "Timing": "10:00 AM - 01:00 PM",
            "Mode": "Hybrid",
            "Location": "Pragyan Lab",
            "Target_Depts": "CSE, AIML, ISE"
        }
    ])
    st.session_state.students = pd.DataFrame()
    st.session_state.drives = pd.DataFrame()
    st.session_state.candidate_stages = pd.DataFrame()
    st.session_state.recruiter_feedback = pd.DataFrame()

    response = handle_placement_chat("Tell me about upcoming workshops and bootcamps", "Student")
    assert "Distributed Systems Masterclass" in response
    assert "Dr. Sateesh Ambesange" in response
    assert "2026-09-12" in response
