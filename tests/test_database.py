import pytest
from sqlalchemy.orm import Session
from src.database import (
    StudentModel,
    CompanyModel,
    DriveModel,
    JobDescriptionModel,
    CandidateStageModel,
    DriveSelectionModel,
    InterviewExperienceModel,
    TrainingSessionModel,
    RecruiterFeedbackModel,
    fetch_table_as_df
)


# ----------------------------------------------------
# 1. STUDENT MODEL & CRUD TESTS
# ----------------------------------------------------
def test_create_and_read_student(db_session: Session, sample_student_payload: dict):
    """Validates inserting and retrieving a student record with all profile attributes."""
    student_obj = StudentModel(**sample_student_payload)
    db_session.add(student_obj)
    db_session.commit()

    queried = db_session.query(StudentModel).filter(StudentModel.id == "STU_TEST_001").first()
    assert queried is not None
    assert queried.name == "Arjun Sharma"
    assert queried.dept == "AIML"
    assert queried.cgpa == 9.15
    assert queried.college == "Main Campus (Bengaluru)"
    assert queried.status == "Placed"
    assert queried.package_lpa == 26.5
    assert "PyTorch" in queried.skills


def test_update_student_profile(db_session: Session, sample_student_payload: dict):
    """Validates updating mutable student fields (CGPA, Package, Status)."""
    student_obj = StudentModel(**sample_student_payload)
    db_session.add(student_obj)
    db_session.commit()

    queried = db_session.query(StudentModel).filter(StudentModel.id == "STU_TEST_001").first()
    queried.cgpa = 9.45
    queried.package_lpa = 30.0
    queried.role = "Senior AI Engineer"
    db_session.commit()

    updated = db_session.query(StudentModel).filter(StudentModel.id == "STU_TEST_001").first()
    assert updated.cgpa == 9.45
    assert updated.package_lpa == 30.0
    assert updated.role == "Senior AI Engineer"


def test_delete_student_cascade(db_session: Session, sample_student_payload: dict, sample_candidate_stage_payload: dict):
    """Validates cascade deletion of relational child stages when a student is removed."""
    student_obj = StudentModel(**sample_student_payload)
    stage_obj = CandidateStageModel(**sample_candidate_stage_payload)
    
    db_session.add(student_obj)
    db_session.add(stage_obj)
    db_session.commit()

    assert db_session.query(CandidateStageModel).count() == 1

    # Delete parent student record
    db_session.delete(student_obj)
    db_session.commit()

    assert db_session.query(StudentModel).count() == 0
    assert db_session.query(CandidateStageModel).count() == 0


# ----------------------------------------------------
# 2. COMPANY & DRIVE RELATIONAL INTEGRITY TESTS
# ----------------------------------------------------
def test_company_registration_and_status_update(db_session: Session, sample_company_payload: dict):
    """Validates registering a company and updating its verification status."""
    comp_obj = CompanyModel(**sample_company_payload)
    db_session.add(comp_obj)
    db_session.commit()

    queried_comp = db_session.query(CompanyModel).filter(CompanyModel.company == "NVIDIA").first()
    assert queried_comp is not None
    assert queried_comp.status == "Approved"
    assert queried_comp.openings == 15

    # Change approval status
    queried_comp.status = "Pending"
    db_session.commit()

    reloaded = db_session.query(CompanyModel).filter(CompanyModel.company == "NVIDIA").first()
    assert reloaded.status == "Pending"


def test_drive_and_job_description_linkage(
    db_session: Session, 
    sample_company_payload: dict, 
    sample_drive_payload: dict
):
    """Validates creating a drive linked via foreign key to an existing corporate partner."""
    comp_obj = CompanyModel(**sample_company_payload)
    db_session.add(comp_obj)
    db_session.commit()

    drive_obj = DriveModel(**sample_drive_payload)
    jd_obj = JobDescriptionModel(
        jd_id="JD_TEST_001",
        drive_id="DRV_TEST_001",
        company="NVIDIA",
        role="LLM Inference Acceleration Engineer",
        target_domain="AI, Generative Systems & Big Data",
        full_jd_text="Optimize transformer models on TensorRT and Triton inference server.",
        min_experience_months=0,
        package_lpa=28.0
    )
    db_session.add(drive_obj)
    db_session.add(jd_obj)
    db_session.commit()

    queried_drive = db_session.query(DriveModel).filter(DriveModel.drive_id == "DRV_TEST_001").first()
    assert queried_drive is not None
    assert queried_drive.company == "NVIDIA"
    assert queried_drive.company_rel.domain == "AI, Generative Systems & Big Data"
    assert queried_drive.job_description is not None
    assert "TensorRT" in queried_drive.job_description.full_jd_text


# ----------------------------------------------------
# 3. RECRUITMENT OPERATIONS & SELECTION LEDGER TESTS
# ----------------------------------------------------
def test_drive_selection_reconciliation(
    db_session: Session, 
    sample_student_payload: dict, 
    sample_company_payload: dict,
    sample_drive_payload: dict
):
    """Validates recording attendance and post-drive offer allocations."""
    db_session.add(StudentModel(**sample_student_payload))
    db_session.add(CompanyModel(**sample_company_payload))
    db_session.add(DriveModel(**sample_drive_payload))
    db_session.commit()

    sel_obj = DriveSelectionModel(
        drive_id="DRV_TEST_001",
        company="NVIDIA",
        student_id="STU_TEST_001",
        student_name="Arjun Sharma",
        dept="AIML",
        attended=True,
        selection_status="Selected",
        offered_role="LLM Inference Acceleration Engineer",
        offered_ctc_lpa=28.0
    )
    db_session.add(sel_obj)
    db_session.commit()

    queried_sel = db_session.query(DriveSelectionModel).filter(
        DriveSelectionModel.drive_id == "DRV_TEST_001",
        DriveSelectionModel.student_id == "STU_TEST_001"
    ).first()

    assert queried_sel is not None
    assert queried_sel.attended is True
    assert queried_sel.selection_status == "Selected"
    assert queried_sel.offered_ctc_lpa == 28.0
    assert queried_sel.student.name == "Arjun Sharma"


def test_interview_experience_debrief_logging(db_session: Session, sample_student_payload: dict):
    """Validates logging post-interview multimedia debriefs and advice."""
    db_session.add(StudentModel(**sample_student_payload))
    db_session.commit()

    exp_payload = {
        "exp_id": "EXP_TEST_001",
        "student_id": "STU_TEST_001",
        "student_name": "Arjun Sharma",
        "dept": "AIML",
        "company": "NVIDIA",
        "role": "LLM Inference Acceleration Engineer",
        "rounds_faced": "Round 1: Kernel Memory, Round 2: CUDA Architecture, Round 3: Culture Fit",
        "skills_excelled": "PyTorch internals, CUDA streams, TensorRT",
        "challenges_faced": "Asynchronous thread synchronization under heavy inference load",
        "advice_to_crack": "Understand shared memory limits and hardware register pressure.",
        "photo_attached": True,
        "audio_attached": False,
        "timestamp": "2026-08-28"
    }
    db_session.add(InterviewExperienceModel(**exp_payload))
    db_session.commit()

    queried_exp = db_session.query(InterviewExperienceModel).filter(InterviewExperienceModel.exp_id == "EXP_TEST_001").first()
    assert queried_exp is not None
    assert queried_exp.company == "NVIDIA"
    assert queried_exp.photo_attached is True
    assert queried_exp.audio_attached is False
    assert "CUDA" in queried_exp.skills_excelled


# ----------------------------------------------------
# 4. TRAINING SESSIONS & FEEDBACK TELEMETRY TESTS
# ----------------------------------------------------
def test_training_session_scheduling(db_session: Session, sample_training_session_payload: dict):
    """Validates creating and querying scheduled workshops and bootcamps."""
    session_obj = TrainingSessionModel(**sample_training_session_payload)
    db_session.add(session_obj)
    db_session.commit()

    queried_session = db_session.query(TrainingSessionModel).filter(
        TrainingSessionModel.session_id == "TRN_TEST_101"
    ).first()

    assert queried_session is not None
    assert queried_session.type == "Bootcamp"
    assert "LangGraph" in queried_session.title
    assert "Dr. Sateesh Ambesange" in queried_session.instructor
    assert queried_session.mode == "Hybrid"


def test_recruiter_feedback_telemetry(db_session: Session, sample_recruiter_feedback_payload: dict):
    """Validates storing post-drive evaluation scores and observed skill gaps."""
    fb_obj = RecruiterFeedbackModel(**sample_recruiter_feedback_payload)
    db_session.add(fb_obj)
    db_session.commit()

    queried_fb = db_session.query(RecruiterFeedbackModel).filter(
        RecruiterFeedbackModel.company == "NVIDIA"
    ).first()

    assert queried_fb is not None
    assert queried_fb.overall_rating == 4.6
    assert "TensorRT" in queried_fb.recommended_curriculum_fixes
    assert "Quantization" in queried_fb.observed_gaps
