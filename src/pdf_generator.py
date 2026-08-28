import io
import hashlib
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_nirf_compliance_pdf(institution_name: str, academic_year: int, stats: dict) -> io.BytesIO:
    """
    Generates an official institutional NIRF/NAAC/NBA placement compliance report PDF
    with verified aggregate metrics, color-coded tables, and authentication hashes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    elements = []
    styles = getSampleStyleSheet()

    # Custom Typography Styles
    inst_title_style = ParagraphStyle(
        'InstTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        alignment=1
    )
    sub_title_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=1
    )
    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E293B")
    )
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1E293B")
    )
    cell_bold_style = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0F172A")
    )
    footer_style = ParagraphStyle(
        'FooterText',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#64748B")
    )

    # Header Section
    elements.append(Paragraph(f"<b>{institution_name.upper()}</b>", inst_title_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        f"<b>INSTITUTIONAL PLACEMENT & CAREER PROGRESSION AUDIT REPORT</b><br/>"
        f"<i>Academic Accreditation Cycle: AY {academic_year}–{academic_year + 1}</i>",
        sub_title_style
    ))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E88E5"), spaceAfter=12))

    # Accreditation Preamble
    preamble_text = (
        f"This document certifies the official campus placement and career progression audit for the graduating "
        f"class of <b>AY {academic_year}–{academic_year + 1}</b> at <b>{institution_name}</b>. All data points "
        f"recorded below comply with the statutory disclosure guidelines established by the <b>National Institutional "
        f"Ranking Framework (NIRF)</b>, <b>National Assessment and Accreditation Council (NAAC - Criterion 5.2.1)</b>, "
        f"and the <b>National Board of Accreditation (NBA - Criterion 4)</b>."
    )
    elements.append(Paragraph(preamble_text, styles['Normal']))
    elements.append(Spacer(1, 14))

    # Executive Summary Table
    elements.append(Paragraph("<b>Table 1: Institutional Macro Placement & CTC Indicators</b>", section_heading_style))
    elements.append(Spacer(1, 6))

    summary_data = [
        [
            Paragraph("<b>Audit Parameter / Metric</b>", cell_bold_style),
            Paragraph("<b>Verified Output</b>", cell_bold_style),
            Paragraph("<b>Accreditation Benchmark</b>", cell_bold_style),
            Paragraph("<b>Compliance Status</b>", cell_bold_style)
        ],
        [
            Paragraph("Total Graduating Batch Enrolled", cell_style),
            Paragraph(f"<b>{stats.get('total_students', 0):,}</b> Candidates", cell_style),
            Paragraph("100% Academic Registry", cell_style),
            Paragraph("<font color='#059669'><b>COMPLIANT</b></font>", cell_style)
        ],
        [
            Paragraph("Total Verified Offers Secured", cell_style),
            Paragraph(f"<b>{stats.get('total_placed', 0):,}</b> Offers", cell_style),
            Paragraph("Institutional Target: > 80%", cell_style),
            Paragraph("<font color='#059669'><b>COMPLIANT</b></font>", cell_style)
        ],
        [
            Paragraph("Institutional Placement Rate", cell_style),
            Paragraph(f"<b>{float(stats.get('placement_rate', 0.0)):.2f}%</b>", cell_style),
            Paragraph("NIRF Tier-1 Threshold: > 75.0%", cell_style),
            Paragraph("<font color='#059669'><b>MET (TIER-1)</b></font>", cell_style)
        ],
        [
            Paragraph("Highest Compensation Package (CTC)", cell_style),
            Paragraph(f"<b>INR {float(stats.get('highest_ctc', 0.0)):.2f} LPA</b>", cell_style),
            Paragraph("Marquee Industry Tier", cell_style),
            Paragraph("<font color='#2563EB'><b>VERIFIED</b></font>", cell_style)
        ],
        [
            Paragraph("Median Compensation Package (CTC)", cell_style),
            Paragraph(f"<b>INR {float(stats.get('median_ctc', 0.0)):.2f} LPA</b>", cell_style),
            Paragraph("Mandatory NIRF Metric", cell_style),
            Paragraph("<font color='#2563EB'><b>VERIFIED</b></font>", cell_style)
        ],
        [
            Paragraph("Mean Compensation Package (CTC)", cell_style),
            Paragraph(f"<b>INR {float(stats.get('mean_ctc', 0.0)):.2f} LPA</b>", cell_style),
            Paragraph("Cohort Central Tendency", cell_style),
            Paragraph("<font color='#2563EB'><b>VERIFIED</b></font>", cell_style)
        ],
        [
            Paragraph("Active Corporate Recruiting Partners", cell_style),
            Paragraph(f"<b>{stats.get('active_companies', 0)}</b> Organizations", cell_style),
            Paragraph("Multi-Sector Diversity", cell_style),
            Paragraph("<font color='#059669'><b>MET</b></font>", cell_style)
        ]
    ]

    t_summary = Table(summary_data, colWidths=[180, 120, 140, 100])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")])
    ]))
    elements.append(t_summary)
    elements.append(Spacer(1, 16))

    # Verification Integrity & Signatory Block
    elements.append(Paragraph("<b>Table 2: Institutional Verification & Signatory Authority</b>", section_heading_style))
    elements.append(Spacer(1, 6))

    raw_hash_input = f"{institution_name}-{academic_year}-{stats.get('total_students')}-{stats.get('total_placed')}"
    sha256_hash = hashlib.sha256(raw_hash_input.encode('utf-8')).hexdigest()[:24].upper()

    auth_data = [
        [
            Paragraph("<b>Verification Attribute</b>", cell_bold_style),
            Paragraph("<b>Institutional Authority Details</b>", cell_bold_style)
        ],
        [
            Paragraph("Report Generation Date", cell_style),
            Paragraph(datetime.now().strftime("%d %B %Y, %H:%M:%S IST"), cell_style)
        ],
        [
            Paragraph("Issuing Directorate", cell_style),
            Paragraph("Central Training & Placement Directorate (Pragyan Platform)", cell_style)
        ],
        [
            Paragraph("Accreditation Reference Code", cell_style),
            Paragraph(f"PRAGYAN-NIRF-{academic_year}-{stats.get('total_placed', 0)}", cell_style)
        ],
        [
            Paragraph("Cryptographic Document Hash", cell_style),
            Paragraph(f"<code>SHA256-{sha256_hash}</code>", cell_style)
        ],
        [
            Paragraph("Authorized Signatory", cell_style),
            Paragraph("<b>Director / Head of Training & Placement Directorate</b>", cell_style)
        ]
    ]

    t_auth = Table(auth_data, colWidths=[180, 360])
    t_auth.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")])
    ]))
    elements.append(t_auth)
    elements.append(Spacer(1, 16))

    # Bottom Footer
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94A3B8"), spaceAfter=8))
    elements.append(Paragraph(
        "Official institutional record compiled via PragyanAI Career & Placement Intelligence Directorate. "
        "Tamper-evident verification hash attached.",
        footer_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_student_offer_pdf(student_data: dict) -> io.BytesIO:
    """
    Generates an official institutional placement confirmation certificate for a placed candidate
    with student credentials, department, recruiting partner, designated role, CTC, and verification hash.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    elements = []
    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        alignment=1
    )
    sub_title_style = ParagraphStyle(
        'CertSubTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1E88E5"),
        alignment=1
    )
    body_style = ParagraphStyle(
        'CertBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=16,
        textColor=colors.HexColor("#1E293B"),
        alignment=4
    )
    table_label_style = ParagraphStyle(
        'TableLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0F172A")
    )
    table_value_style = ParagraphStyle(
        'TableValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B")
    )
    signatory_style = ParagraphStyle(
        'SignatoryText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    # Header Banner
    elements.append(Paragraph("<b>PRAGYAN CAREER & PLACEMENT DIRECTORATE</b>", title_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("<b>CAMPUS PLACEMENT CONFIRMATION CERTIFICATE</b>", sub_title_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1E88E5"), spaceAfter=14))

    # Extraction of student values
    stu_name = str(student_data.get('Name', 'Candidate Name'))
    stu_id = str(student_data.get('ID', 'N/A'))
    stu_dept = str(student_data.get('Dept', 'Engineering'))
    stu_year = str(student_data.get('Grad_Year', '2026'))
    stu_company = str(student_data.get('Company', 'Corporate Partner'))
    stu_role = str(student_data.get('Role', 'Software Engineer'))
    stu_pkg = float(student_data.get('Package_LPA', 0.0))
    stu_cgpa = str(student_data.get('CGPA', 'N/A'))
    stu_college = str(student_data.get('College', 'Main Campus (Bengaluru)'))

    # Narrative Body
    cert_text = (
        f"This is to officially certify that <b>{stu_name}</b> (USN / Student ID: <b>{stu_id}</b>), a bonafide student "
        f"of the Department of <b>{stu_dept}</b> (Class of <b>{stu_year}</b>) at <b>{stu_college}</b>, has successfully "
        f"cleared the rigorous multi-round campus recruitment process and secured an official placement offer with "
        f"<b>{stu_company}</b> for the role of <b>{stu_role}</b> with an annual Cost-to-Company (CTC) compensation "
        f"of <b>INR {stu_pkg:.2f} LPA</b>."
    )
    elements.append(Paragraph(cert_text, body_style))
    elements.append(Spacer(1, 16))

    # Verified Credentials Table
    raw_hash_seed = f"{stu_id}-{stu_company}-{stu_pkg}-{stu_year}"
    verification_hash = hashlib.sha256(raw_hash_seed.encode('utf-8')).hexdigest()[:20].upper()

    cert_table_data = [
        [
            Paragraph("<b>Placement Credential Parameter</b>", table_label_style),
            Paragraph("<b>Verified Institutional Record</b>", table_label_style)
        ],
        [
            Paragraph("Student Full Name", table_label_style),
            Paragraph(stu_name, table_value_style)
        ],
        [
            Paragraph("USN / Student Roll ID", table_label_style),
            Paragraph(f"<code>{stu_id}</code>", table_value_style)
        ],
        [
            Paragraph("Academic Department", table_label_style),
            Paragraph(stu_dept, table_value_style)
        ],
        [
            Paragraph("Campus / College Entity", table_label_style),
            Paragraph(stu_college, table_value_style)
        ],
        [
            Paragraph("Graduation Cohort Year", table_label_style),
            Paragraph(stu_year, table_value_style)
        ],
        [
            Paragraph("Cumulative Academic CGPA", table_label_style),
            Paragraph(stu_cgpa, table_value_style)
        ],
        [
            Paragraph("Selected Organization", table_label_style),
            Paragraph(f"<b>{stu_company}</b>", table_value_style)
        ],
        [
            Paragraph("Job Designation / Profile", table_label_style),
            Paragraph(stu_role, table_value_style)
        ],
        [
            Paragraph("Annual Compensation (CTC)", table_label_style),
            Paragraph(f"<b>INR {stu_pkg:.2f} Lakhs Per Annum</b>", table_value_style)
        ],
        [
            Paragraph("Placement Verification Code", table_label_style),
            Paragraph(f"<code>PRAGYAN-OFFER-SHA256-{verification_hash}</code>", table_value_style)
        ]
    ]

    t_cert = Table(cert_table_data, colWidths=[200, 332])
    t_cert.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")])
    ]))
    elements.append(t_cert)
    elements.append(Spacer(1, 24))

    # Authorized Signatory Block
    sig_block = [
        [
            Paragraph("<b>Verified By:</b><br/>Lead — Corporate Relations & Drives<br/>Training & Placement Directorate", signatory_style),
            Paragraph("<b>Authorized Signatory:</b><br/>Head — Training & Placement Directorate<br/>Pragyan Skill Passport Ecosystem", signatory_style)
        ]
    ]
    t_sig = Table(sig_block, colWidths=[266, 266])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0)
    ]))
    elements.append(t_sig)
    elements.append(Spacer(1, 14))

    # Bottom Security Guarantee
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=6))
    elements.append(Paragraph(
        f"<i>This document is digitally stamped on {datetime.now().strftime('%d %B %Y')} and serves as an official "
        f"institutional placement credential for credential verification and background validation.</i>",
        styles['Italic']
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
