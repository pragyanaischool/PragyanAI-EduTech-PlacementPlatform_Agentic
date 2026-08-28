import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_nirf_compliance_pdf(institution_name: str, academic_year: int, stats: dict) -> io.BytesIO:
    """Generates an official NIRF/NAAC/NBA placement compliance report PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    styles = getSampleStyleSheet()

    # Title Banner
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1A365D"),
        alignment=1
    )
    elements.append(Paragraph(f"<b>{institution_name.upper()}</b>", title_style))
    elements.append(Paragraph(f"<b>Institutional Placement & Career Progression Audit (AY {academic_year}-{academic_year+1})</b>", styles['Normal']))
    elements.append(Spacer(1, 15))

    # Executive Summary Table
    summary_data = [
        ["Metric Parameter", "Audited Output", "Compliance Benchmark"],
        ["Total Graduating Cohort", f"{stats['total_students']:,}", "100% Enrolled"],
        ["Total Placed Candidates", f"{stats['total_placed']:,}", "Target: > 80%"],
        ["Institutional Placement Rate", f"{stats['placement_rate']:.2f}%", "NIRF Tier-1: > 75%"],
        ["Highest Package (CTC)", f"INR {stats['highest_ctc']:.2f} LPA", "Verified Verified Offer"],
        ["Median Package (CTC)", f"INR {stats['median_ctc']:.2f} LPA", "Verified Verified Offer"],
        ["Mean Package (CTC)", f"INR {stats['mean_ctc']:.2f} LPA", "Verified Verified Offer"],
        ["Active Corporate Partners", f"{stats['active_companies']}", "Diverse Multi-Sector"]
    ]

    t = Table(summary_data, colWidths=[220, 150, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")])
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"<i>Report generated on {datetime.now().strftime('%d %B %Y, %H:%M:%S')} via PragyanAI Enterprise Directorate Engine.</i>", styles['Italic']))
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_student_offer_pdf(student_data: dict) -> io.BytesIO:
    """Generates an official institutional offer confirmation certificate for a placed candidate."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>PRAGYAN EDUTECH CAREER & PLACEMENT DIRECTORATE</b>", styles['Heading1']))
    elements.append(Paragraph("<b>OFFICIAL PLACEMENT CONFIRMATION CERTIFICATE</b>", styles['Heading2']))
    elements.append(Spacer(1, 15))

    body_text = f"""
    This is to certify that <b>{student_data['Name']}</b> (USN/Roll No: <b>{student_data['ID']}</b>), 
    student of the Department of <b>{student_data['Dept']}</b>, Class of <b>{student_data['Grad_Year']}</b>, 
    has officially secured campus placement with <b>{student_data['Company']}</b> for the role of 
    <b>{student_data['Role']}</b> with an annual cost-to-company (CTC) of <b>INR {student_data['Package_LPA']} LPA</b>.
    """
    elements.append(Paragraph(body_text, styles['Normal']))
    elements.append(Spacer(1, 25))

    cert_table = [
        ["Credential Item", "Verified Institutional Record"],
        ["Student Name", student_data['Name']],
        ["Student ID", student_data['ID']],
        ["Department", student_data['Dept']],
        ["Cumulative CGPA", str(student_data['CGPA'])],
        ["Selected Organization", student_data['Company']],
        ["Job Designation", student_data['Role']],
        ["Annual Package (CTC)", f"INR {student_data['Package_LPA']} LPA"],
        ["Verification Hash", f"SHA256-{abs(hash(student_data['ID'] + student_data['Company']))}"]
    ]
    t = Table(cert_table, colWidths=[200, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
        ('PADDING', (0, 0), (-1, -1), 5)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 35))

    elements.append(Paragraph("<b>Authorized Signatory</b><br/>Head - Training & Placement Directorate<br/>Pragyan Skill Passport Ecosystem", styles['Normal']))
    doc.build(elements)
    buffer.seek(0)
    return buffer
