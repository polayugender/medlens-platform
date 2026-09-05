import io
from datetime import datetime
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_patient_clinical_pdf(
    patient: Dict[str, Any],
    intake: Optional[Dict[str, Any]],
    verified_tests: List[Dict[str, Any]],
    summary: Optional[Dict[str, Any]],
    audit_logs: List[Dict[str, Any]]
) -> bytes:
    """
    Generates a high-quality clinical PDF document of the unified patient record using ReportLab.
    Includes:
    - Patient header and demographics
    - Non-diagnostic clinical safety disclaimer
    - Self-reported intake details (provenance: user_input)
    - AI-generated plain-language summary block (provenance: ai_generated)
    - Verified laboratory test results table with deterministic flags
    - Audit log trail snippet for governance
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    brand_style = ParagraphStyle(
        name='BrandHeader',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0267c1")
    )
    sub_brand = ParagraphStyle(
        name='SubBrand',
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748b")
    )
    disclaimer_title = ParagraphStyle(
        name='DiscTitle',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#78350f")
    )
    disclaimer_text = ParagraphStyle(
        name='DiscText',
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#92400e")
    )
    section_heading = ParagraphStyle(
        name='SecHead',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        name='BodySm',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )
    table_text = ParagraphStyle(
        name='TText',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1e293b")
    )
    table_bold = ParagraphStyle(
        name='TBold',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0f172a")
    )

    # 1. Document Header
    header_data = [
        [
            Paragraph("MedLens Clinical Intelligence", brand_style),
            Paragraph(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}<br/>Record ID: {patient.get('id', '')[:8]}", ParagraphStyle('HRight', fontName='Helvetica', fontSize=8, leading=11, alignment=2, textColor=colors.HexColor("#64748b")))
        ],
        [
            Paragraph("Unified Patient Provenance & Document Synthesis Record", sub_brand),
            ""
        ]
    ]
    h_table = Table(header_data, colWidths=[360, 180])
    h_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(h_table)
    story.append(Spacer(1, 10))

    # 2. Non-Diagnostic Disclaimer Box
    disclaimer_content = [
        [
            Paragraph("<b>CLINICAL INFORMATION INTELLIGENCE ADVISORY & NON-DIAGNOSTIC GUARDRAIL</b>", disclaimer_title)
        ],
        [
            Paragraph(
                "MedLens is an information-organization and source-traceability tool, <b>not a medical diagnostic system</b>. "
                "It does not formulate medical diagnoses, clinical prognoses, or treatment recommendations. "
                "All laboratory values and reference ranges are transcribed directly from source documents; reference ranges are never inferred or estimated. "
                "Always review this record with a licensed healthcare practitioner for clinical decision-making.",
                disclaimer_text
            )
        ]
    ]
    d_table = Table(disclaimer_content, colWidths=[540])
    d_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fef3c7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#f59e0b")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(d_table)
    story.append(Spacer(1, 12))

    # 3. Patient Demographics Summary Box
    age_str = f"{intake.get('age')} years" if intake and intake.get('age') else "—"
    p_info_data = [
        [
            Paragraph(f"<b>Patient Name:</b> {patient.get('name', 'N/A')}", body_style),
            Paragraph(f"<b>Date of Birth:</b> {patient.get('dob', 'N/A')}", body_style),
            Paragraph(f"<b>Sex:</b> {patient.get('sex', 'N/A')}", body_style),
            Paragraph(f"<b>Current Age:</b> {age_str}", body_style),
        ]
    ]
    p_box = Table(p_info_data, colWidths=[160, 130, 110, 140])
    p_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(p_box)
    story.append(Spacer(1, 14))

    # 4. Self-Reported Health Profile (Provenance: user_input)
    story.append(Paragraph("1. Self-Reported Health Profile <font color='#0284c7' size='8'>[Source: User Input]</font>", section_heading))
    if intake:
        symptoms_str = ", ".join(intake.get("symptoms", [])) or "None reported"
        conditions_str = ", ".join(intake.get("existing_conditions", [])) or "None reported"
        allergies_str = ", ".join(intake.get("allergies", [])) or "No known drug/food allergies"
        
        meds_list = []
        for m in intake.get("medications", []):
            meds_list.append(f"{m.get('name')} ({m.get('dosage', 'dose unstated')}, {m.get('frequency', '')})")
        meds_str = "; ".join(meds_list) or "None recorded"

        intake_table_data = [
            [Paragraph("<b>Reported Symptoms:</b>", table_bold), Paragraph(symptoms_str, table_text)],
            [Paragraph("<b>Existing Conditions:</b>", table_bold), Paragraph(conditions_str, table_text)],
            [Paragraph("<b>Documented Allergies:</b>", table_bold), Paragraph(allergies_str, table_text)],
            [Paragraph("<b>Active Medications:</b>", table_bold), Paragraph(meds_str, table_text)],
        ]
        it_table = Table(intake_table_data, colWidths=[130, 410])
        it_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f8fafc")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(it_table)
    else:
        story.append(Paragraph("No patient intake profile recorded.", body_style))
    
    story.append(Spacer(1, 14))

    # 5. AI Plain-Language Clinical Summary (Provenance: ai_generated)
    story.append(Paragraph("2. AI Plain-Language Clinical Summary <font color='#9333ea' size='8'>[Source: AI Generated]</font>", section_heading))
    if summary and summary.get("summary_text"):
        sum_text = summary.get("summary_text", "").replace("\n", "<br/>")
        sum_p = Paragraph(f"<font color='#1e293b'>{sum_text}</font>", ParagraphStyle('SummaryStyle', fontName='Helvetica', fontSize=8, leading=11))
        
        sum_box = Table([[sum_p]], colWidths=[540])
        sum_box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#faf5ff")),
            ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#d8b4fe")),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(sum_box)
    else:
        story.append(Paragraph("No AI plain-language summary on file.", body_style))

    story.append(Spacer(1, 14))

    # 6. Verified Diagnostic Test Results Table (Provenance: ai_extracted / verified)
    story.append(Paragraph(f"3. Verified Diagnostic Laboratory Findings ({len(verified_tests)} tests) <font color='#059669' size='8'>[Source: Verified Medical Reports]</font>", section_heading))
    if verified_tests:
        table_rows = [
            [
                Paragraph("<b>Test Marker</b>", table_bold),
                Paragraph("<b>Result</b>", table_bold),
                Paragraph("<b>Unit</b>", table_bold),
                Paragraph("<b>Reference Range</b>", table_bold),
                Paragraph("<b>Computed Flag</b>", table_bold),
                Paragraph("<b>Verified By</b>", table_bold),
            ]
        ]

        for t in verified_tests:
            flag_val = (t.get("flag") or "unavailable").lower()
            if flag_val == "high":
                flag_str = "<font color='#b91c1c'><b>↑ HIGH</b></font>"
            elif flag_val == "low":
                flag_str = "<font color='#b45309'><b>↓ LOW</b></font>"
            elif flag_val == "normal":
                flag_str = "<font color='#047857'>✓ Normal</font>"
            else:
                flag_str = "<font color='#64748b'>– Unavailable</font>"

            table_rows.append([
                Paragraph(t.get("test_name", ""), table_text),
                Paragraph(f"<b>{t.get('value', '')}</b>", table_text),
                Paragraph(t.get("unit") or "—", table_text),
                Paragraph(t.get("reference_range_raw") or "range_unavailable", table_text),
                Paragraph(flag_str, table_text),
                Paragraph(t.get("verified_by") or "Clinician", table_text),
            ])

        lab_table = Table(table_rows, colWidths=[160, 65, 60, 110, 75, 70])
        lab_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(lab_table)
    else:
        story.append(Paragraph("No verified laboratory tests linked to this record.", body_style))

    story.append(Spacer(1, 14))

    # 7. Governance & Audit Log Highlights
    if audit_logs:
        story.append(Paragraph("4. Governance & Audit Trail Summary", section_heading))
        audit_rows = [
            [
                Paragraph("<b>Action</b>", table_bold),
                Paragraph("<b>Actor</b>", table_bold),
                Paragraph("<b>Entity</b>", table_bold),
                Paragraph("<b>Timestamp (UTC)</b>", table_bold),
            ]
        ]
        for log in audit_logs[:5]: # top 5 recent events
            audit_rows.append([
                Paragraph(log.get("action", ""), table_text),
                Paragraph(log.get("actor", ""), table_text),
                Paragraph(log.get("entity", ""), table_text),
                Paragraph(str(log.get("timestamp", ""))[:19], table_text),
            ])

        a_table = Table(audit_rows, colWidths=[180, 120, 100, 140])
        a_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(a_table)

    doc.build(story)
    return buffer.getvalue()
