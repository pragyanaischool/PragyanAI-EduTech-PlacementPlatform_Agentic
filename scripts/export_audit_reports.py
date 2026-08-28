import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# ----------------------------------------------------
# 1. PATH RESOLUTION & ENGINE IMPORT
# ----------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.database import (
    fetch_table_as_df,
    StudentModel,
    DriveModel,
    DriveSelectionModel,
    CompanyModel
)
from src.pdf_generator import generate_nirf_compliance_pdf

EXPORT_DIR = os.path.join(PROJECT_ROOT, "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)


# ----------------------------------------------------
# 2. BATCH AUDIT & ACCREDITATION EXPORTER
# ----------------------------------------------------
def export_institutional_compliance_reports():
    """
    Extracts live database records and produces:
    1. Official NIRF/NAAC Compliance Audit PDF
    2. Multi-Sheet Institutional Placement Audit Workbook (.xlsx)
    3. Department-Level Honors & Verification Ledger (.csv)
    """
    print("Beginning institutional placement audit batch execution...")

    # Fetch live records from database
    students_df = fetch_table_as_df(StudentModel).rename(columns={
        "id": "ID", "name": "Name", "dept": "Dept", "college": "College", "grad_year": "Grad_Year",
        "cgpa": "CGPA", "skills": "Skills", "projects": "Projects", "experience": "Experience",
        "linkedin": "Linkedin", "github": "Github", "dream_roles": "Dream_Roles",
        "dream_companies": "Dream_Companies", "salary_expected_lpa": "Salary_Expected_LPA",
        "status": "Status", "company": "Company", "role": "Role", "package_lpa": "Package_LPA"
    })

    drives_df = fetch_table_as_df(DriveModel).rename(columns={
        "drive_id": "Drive_ID", "company": "Company", "role": "Role",
        "min_cgpa": "Min_CGPA", "eligible_depts": "Eligible_Depts",
        "package_lpa": "Package_LPA", "session_date": "Session_Date"
    })

    if students_df.empty:
        print("No student records found in database. Run `python scripts/generate_large_scale_dataset.py` first.")
        return

    # Standardize numerical columns
    students_df["Package_LPA"] = pd.to_numeric(students_df["Package_LPA"], errors="coerce").fillna(0.0)
    students_df["CGPA"] = pd.to_numeric(students_df["CGPA"], errors="coerce").fillna(0.0)

    # Filter placed cohort
    placed_df = students_df[
        (students_df["Status"].isin(["Placed", "Selected"])) &
        (students_df["Company"].notna()) &
        (~students_df["Company"].isin(["None", "N/A", ""]))
    ].copy()

    total_cohort = len(students_df)
    total_placed = len(placed_df)
    placement_rate = round((total_placed / total_cohort * 100), 2) if total_cohort > 0 else 0.0

    mean_ctc = round(float(placed_df["Package_LPA"].mean()), 2) if not placed_df.empty else 0.0
    median_ctc = round(float(placed_df["Package_LPA"].median()), 2) if not placed_df.empty else 0.0
    max_ctc = round(float(placed_df["Package_LPA"].max()), 2) if not placed_df.empty else 0.0
    active_companies_cnt = placed_df["Company"].nunique()

    print(f"Cohort Analyzed: {total_cohort} | Placed: {total_placed} ({placement_rate}%) | Mean CTC: INR {mean_ctc} LPA")

    # ------------------------------------------------
    # 3. GENERATE NIRF ACCREDITATION AUDIT PDF
    # ------------------------------------------------
    inst_name = "Pragyan University / Technical Placement Directorate"
    audit_year = 2026

    stats_payload = {
        "total_students": total_cohort,
        "total_placed": total_placed,
        "placement_rate": placement_rate,
        "highest_ctc": max_ctc,
        "median_ctc": median_ctc,
        "mean_ctc": mean_ctc,
        "active_companies": active_companies_cnt
    }

    pdf_buffer = generate_nirf_compliance_pdf(inst_name, audit_year, stats_payload)
    pdf_filename = f"NIRF_Placement_Compliance_Audit_{audit_year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_out_path = os.path.join(EXPORT_DIR, pdf_filename)

    with open(pdf_out_path, "wb") as f:
        f.write(pdf_buffer.read())
    print(f"Generated NIRF Compliance Audit PDF: {pdf_out_path}")

    # ------------------------------------------------
    # 4. GENERATE MULTI-SHEET EXCEL AUDIT WORKBOOK
    # ------------------------------------------------
    excel_filename = f"Institutional_Placement_Audit_Ledger_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    excel_out_path = os.path.join(EXPORT_DIR, excel_filename)

    with pd.ExcelWriter(excel_out_path, engine="openpyxl") as writer:
        # Sheet 1: Executive KPI Metrics
        kpi_df = pd.DataFrame([
            {"Parameter": "Total Graduating Batch", "Audited Output": total_cohort, "Benchmark": "100% Enrolled"},
            {"Parameter": "Total Offers Verified", "Audited Output": total_placed, "Benchmark": "> 80%"},
            {"Parameter": "Institutional Placement Rate", "Audited Output": f"{placement_rate}%", "Benchmark": "NIRF Tier-1: > 75%"},
            {"Parameter": "Mean Package (CTC)", "Audited Output": f"INR {mean_ctc} LPA", "Benchmark": "Verified Offer"},
            {"Parameter": "Median Package (CTC)", "Audited Output": f"INR {median_ctc} LPA", "Benchmark": "Verified Offer"},
            {"Parameter": "Highest Package (CTC)", "Audited Output": f"INR {max_ctc} LPA", "Benchmark": "Verified Offer"},
            {"Parameter": "Active Corporate Hiring Partners", "Audited Output": active_companies_cnt, "Benchmark": "Multi-Sectoral"}
        ])
        kpi_df.to_excel(writer, sheet_name="Executive_Summary", index=False)

        # Sheet 2: Department-wise Aggregate Audit
        dept_summary = students_df.groupby("Dept").agg(
            Batch_Strength=("ID", "count"),
            Placed_Count=("Status", lambda s: sum(s.isin(["Placed", "Selected"]))),
            Avg_CGPA=("CGPA", "mean"),
        ).reset_index()

        dept_summary["Placement_Rate_%"] = np.round(dept_summary["Placed_Count"] / dept_summary["Batch_Strength"] * 100, 2)

        # Salary metrics for placed students by department
        dept_salary = placed_df.groupby("Dept").agg(
            Mean_CTC_LPA=("Package_LPA", "mean"),
            Median_CTC_LPA=("Package_LPA", "median"),
            Top_CTC_LPA=("Package_LPA", "max")
        ).reset_index()

        dept_audit = pd.merge(dept_summary, dept_salary, on="Dept", how="left").fillna(0.0).round(2)
        dept_audit.to_excel(writer, sheet_name="Department_Breakdown", index=False)

        # Sheet 3: Recruiter Headcount Matrix
        comp_summary = placed_df.groupby("Company").agg(
            Hires_Count=("ID", "count"),
            Mean_CTC=("Package_LPA", "mean"),
            Top_CTC=("Package_LPA", "max")
        ).reset_index().sort_values(by="Hires_Count", ascending=False).round(2)
        comp_summary.to_excel(writer, sheet_name="Recruiter_Headcount", index=False)

        # Sheet 4: Complete Placed Candidate Ledger
        placed_export_cols = [
            "ID", "Name", "Dept", "College", "Grad_Year", "CGPA",
            "Company", "Role", "Package_LPA", "Skills"
        ]
        available_cols = [c for c in placed_export_cols if c in placed_df.columns]
        placed_df[available_cols].to_excel(writer, sheet_name="Placed_Scholars_Roster", index=False)

    print(f"Generated Multi-Sheet Excel Audit: {excel_out_path}")

    # ------------------------------------------------
    # 5. EXPORT RAW CSV PLACEMENT LEDGER
    # ------------------------------------------------
    csv_filename = f"placed_candidates_audit_ledger_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    csv_out_path = os.path.join(EXPORT_DIR, csv_filename)
    placed_df.to_csv(csv_out_path, index=False)
    print(f"Generated Raw CSV Placed Ledger: {csv_out_path}")

    print("\nAudit export completed successfully. All artifacts are available under 'exports/'.")


# ----------------------------------------------------
# 6. SCRIPT ENTRYPOINT
# ----------------------------------------------------
if __name__ == "__main__":
    export_institutional_compliance_reports()
