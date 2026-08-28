import io
import pytest
from src.pdf_generator import generate_nirf_compliance_pdf, generate_student_offer_pdf


# ----------------------------------------------------
# 1. NIRF COMPLIANCE PDF GENERATION TESTS
# ----------------------------------------------------
def test_generate_nirf_compliance_pdf_structure():
    """Validates structure, stream type, and byte headers of the NIRF compliance report."""
    institution = "National Institute of Technology Karnataka"
    year = 2026
    stats = {
        "total_students": 1500,
        "total_placed": 1260,
        "placement_rate": 84.0,
        "highest_ctc": 32.5,
        "median_ctc": 12.0,
        "mean_ctc": 13.8,
        "active_companies": 112
    }

    pdf_stream = generate_nirf_compliance_pdf(institution, year, stats)

    # Validate output type
    assert isinstance(pdf_stream, io.BytesIO)

    # Validate non-empty payload
    pdf_bytes = pdf_stream.getvalue()
    assert len(pdf_bytes) > 2000

    # Validate standard PDF magic bytes header
    assert pdf_bytes.startswith(b"%PDF-")


def test_generate_nirf_compliance_pdf_zero_state():
    """Validates robust PDF generation when handling zero or default stats."""
    institution = "Pragyan University"
    year = 2025
    stats = {
        "total_students": 0,
        "total_placed": 0,
        "placement_rate": 0.0,
        "highest_ctc": 0.0,
        "median_ctc": 0.0,
        "mean_ctc": 0.0,
        "active_companies": 0
    }

    pdf_stream = generate_nirf_compliance_pdf(institution, year, stats)
    assert isinstance(pdf_stream, io.BytesIO)
    pdf_bytes = pdf_stream.getvalue()
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")


# ----------------------------------------------------
# 2. STUDENT OFFER CERTIFICATE PDF TESTS
# ----------------------------------------------------
def test_generate_student_offer_pdf_valid(sample_student_payload):
    """Validates student offer confirmation certificate generation with complete profile data."""
    pdf_stream = generate_student_offer_pdf(sample_student_payload)

    # Validate output type
    assert isinstance(pdf_stream, io.BytesIO)

    # Validate byte length and magic header
    pdf_bytes = pdf_stream.getvalue()
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF-")


def test_generate_student_offer_pdf_partial_data():
    """Validates offer certificate generation when optional fields are missing."""
    sparse_student_payload = {
        "ID": "STU_SPARSE_01",
        "Name": "Sneha Reddy",
        "Dept": "CSE",
        "Grad_Year": 2026,
        "CGPA": 8.9,
        "Company": "Google",
        "Role": "Software Engineer",
        "Package_LPA": 22.0
    }

    pdf_stream = generate_student_offer_pdf(sparse_student_payload)
    assert isinstance(pdf_stream, io.BytesIO)
    pdf_bytes = pdf_stream.getvalue()
    assert len(pdf_bytes) > 1500
    assert pdf_bytes.startswith(b"%PDF-")
