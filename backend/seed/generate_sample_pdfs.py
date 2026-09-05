from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_cmp_report(output_path: Path):
    doc = SimpleDocTemplate(str(output_path), pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    # Title & Facility
    title_style = ParagraphStyle(name='TitleStyle', fontSize=16, leading=20, fontName='Helvetica-Bold', textColor=colors.HexColor("#0f2942"))
    meta_style = ParagraphStyle(name='MetaStyle', fontSize=9, leading=13, fontName='Helvetica', textColor=colors.HexColor("#475569"))
    header_style = ParagraphStyle(name='HStyle', fontSize=12, leading=16, fontName='Helvetica-Bold', textColor=colors.HexColor("#1e293b"))

    story.append(Paragraph("APEX HEALTH DIAGNOSTICS & PATHOLOGY", title_style))
    story.append(Paragraph("Facility: Apex Clinical Laboratory - Metropolitan Campus | CLIA # 05D2039481", meta_style))
    story.append(Spacer(1, 10))

    # Patient & Specimen info table
    patient_info = [
        ["Patient Name: Eleanor Vance", "Date of Birth: 1978-04-14", "Sex: Female"],
        ["Ordering Physician: Dr. Marcus Reed, MD", "Date of Service: 2026-08-15", "Specimen: Serum"],
        ["Report Status: Final Verified", "Report Type: Comprehensive Metabolic Panel (CMP)", "Specimen ID: SP-99214"]
    ]
    p_table = Table(patient_info, colWidths=[200, 180, 150])
    p_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#334155")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(p_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("TEST RESULTS", header_style))
    story.append(Spacer(1, 8))

    # Table of tests
    # Headers: Test Name, Result, Units, Reference Interval
    table_data = [
        ["Test Name", "Result", "Units", "Reference Interval"],
        ["Glucose, Fasting", "128", "mg/dL", "70 - 99"],
        ["Blood Urea Nitrogen (BUN)", "18", "mg/dL", "7 - 20"],
        ["Creatinine", "1.1", "mg/dL", "0.6 - 1.3"],
        ["eGFR", "74", "mL/min/1.73m2", "> 60"],
        ["Sodium", "141", "mmol/L", "136 - 145"],
        ["Potassium", "4.6", "mmol/L", "3.5 - 5.1"],
        ["Chloride", "102", "mmol/L", "98 - 107"],
        ["Carbon Dioxide, Total", "25", "mmol/L", "22 - 29"],
        ["Calcium", "9.4", "mg/dL", "8.5 - 10.5"],
        ["Protein, Total", "7.1", "g/dL", "6.0 - 8.3"],
        ["Albumin", "4.3", "g/dL", "3.5 - 5.0"],
        ["Bilirubin, Total", "0.7", "mg/dL", "0.2 - 1.2"],
        ["Alkaline Phosphatase (ALP)", "78", "IU/L", "44 - 147"],
        ["AST (SGOT)", "24", "IU/L", "10 - 40"],
        ["ALT (SGPT)", "28", "IU/L", "9 - 46"]
    ]

    t = Table(table_data, colWidths=[210, 80, 100, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    story.append(Paragraph("LABORATORY COMMENTS & CLINICAL NOTES:", ParagraphStyle('Sub', fontSize=9, fontName='Helvetica-Bold', textColor=colors.HexColor("#1e293b"))))
    story.append(Paragraph("Fasting status: Confirmed 10-hour fasting prior to venipuncture. Test performed via photometric / ion selective electrode assays.", meta_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Electronic Verification: Dr. S. Patel, MD, Laboratory Director", meta_style))

    doc.build(story)

def create_cbc_report(output_path: Path):
    doc = SimpleDocTemplate(str(output_path), pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(name='TitleStyle', fontSize=16, leading=20, fontName='Helvetica-Bold', textColor=colors.HexColor("#0f2942"))
    meta_style = ParagraphStyle(name='MetaStyle', fontSize=9, leading=13, fontName='Helvetica', textColor=colors.HexColor("#475569"))
    header_style = ParagraphStyle(name='HStyle', fontSize=12, leading=16, fontName='Helvetica-Bold', textColor=colors.HexColor("#1e293b"))

    story.append(Paragraph("QUEST DIAGNOSTICS REGIONAL CENTER", title_style))
    story.append(Paragraph("Facility: Quest Central Hematology Laboratory | CLIA # 33D0654321", meta_style))
    story.append(Spacer(1, 10))

    patient_info = [
        ["Patient Name: Arthur Pendelton", "Date of Birth: 1962-11-20", "Sex: Male"],
        ["Ordering Physician: Dr. Sarah Lin, MD", "Date of Service: 2026-07-22", "Specimen: Whole Blood EDTA"],
        ["Report Status: Verified", "Report Type: Complete Blood Count (CBC) with Differential", "Specimen ID: CBC-88192"]
    ]
    p_table = Table(patient_info, colWidths=[200, 180, 150])
    p_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#334155")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(p_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("HEMATOLOGY RESULTS", header_style))
    story.append(Spacer(1, 8))

    table_data = [
        ["Test Name", "Result", "Units", "Reference Interval"],
        ["White Blood Cells (WBC)", "6.8", "x10^3/uL", "4.5 - 11.0"],
        ["Red Blood Cells (RBC)", "4.10", "x10^6/uL", "4.30 - 5.90"],
        ["Hemoglobin", "11.6", "g/dL", "13.5 - 17.5"],
        ["Hematocrit", "34.8", "%", "41.0 - 50.0"],
        ["Mean Corpuscular Volume (MCV)", "84.8", "fL", "80.0 - 100.0"],
        ["MCH", "28.3", "pg", "27.0 - 33.0"],
        ["MCHC", "33.3", "g/dL", "32.0 - 36.0"],
        ["Platelets", "255", "x10^3/uL", "150 - 450"],
        ["Neutrophils", "62.0", "%", "40.0 - 70.0"],
        ["Lymphocytes", "27.5", "%", "20.0 - 45.0"],
        ["Monocytes", "6.2", "%", "2.0 - 10.0"],
        ["Eosinophils", "3.1", "%", "1.0 - 5.0"],
        ["Basophils", "0.8", "%", "0.0 - 2.0"]
    ]

    t = Table(table_data, colWidths=[210, 80, 100, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    story.append(Paragraph("LABORATORY COMMENTS:", ParagraphStyle('Sub', fontSize=9, fontName='Helvetica-Bold', textColor=colors.HexColor("#1e293b"))))
    story.append(Paragraph("Automated differential verified. Red blood cell morphology indicates mild normocytic, normochromic pattern.", meta_style))

    doc.build(story)

def create_lipid_report(output_path: Path):
    doc = SimpleDocTemplate(str(output_path), pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(name='TitleStyle', fontSize=16, leading=20, fontName='Helvetica-Bold', textColor=colors.HexColor("#0f2942"))
    meta_style = ParagraphStyle(name='MetaStyle', fontSize=9, leading=13, fontName='Helvetica', textColor=colors.HexColor("#475569"))
    header_style = ParagraphStyle(name='HStyle', fontSize=12, leading=16, fontName='Helvetica-Bold', textColor=colors.HexColor("#1e293b"))

    story.append(Paragraph("CARDIOVASCULAR RISK PROFILE LABS", title_style))
    story.append(Paragraph("Facility: St. Jude Hospital Pathology Services | CLIA # 14D0987654", meta_style))
    story.append(Spacer(1, 10))

    patient_info = [
        ["Patient Name: Eleanor Vance", "Date of Birth: 1978-04-14", "Sex: Female"],
        ["Ordering Physician: Dr. Marcus Reed, MD", "Date of Service: 2026-08-15", "Specimen: Serum Fasting"],
        ["Report Status: Complete", "Report Type: Lipid Panel", "Specimen ID: LP-33109"]
    ]
    p_table = Table(patient_info, colWidths=[200, 180, 150])
    p_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#334155")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(p_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("LIPID PROFILE RESULTS", header_style))
    story.append(Spacer(1, 8))

    table_data = [
        ["Test Name", "Result", "Units", "Reference Interval"],
        ["Cholesterol, Total", "228", "mg/dL", "< 200"],
        ["Triglycerides", "184", "mg/dL", "< 150"],
        ["HDL Cholesterol", "38", "mg/dL", "> 40"],
        ["LDL Cholesterol (Calc)", "153", "mg/dL", "< 100"],
        ["Non-HDL Cholesterol", "190", "mg/dL", "< 130"],
        ["Cholesterol/HDL Ratio", "6.0", "ratio", "< 5.0"]
    ]

    t = Table(table_data, colWidths=[210, 80, 100, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    story.append(Paragraph("COMMENTS:", ParagraphStyle('Sub', fontSize=9, fontName='Helvetica-Bold', textColor=colors.HexColor("#1e293b"))))
    story.append(Paragraph("Calculated LDL is derived using the Friedewald equation. Triglyceride values over 400 invalidates calculation.", meta_style))

    doc.build(story)

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent / "sample_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    create_cmp_report(out_dir / "sample_cmp_report.pdf")
    create_cbc_report(out_dir / "sample_cbc_report.pdf")
    create_lipid_report(out_dir / "sample_lipid_panel.pdf")
    print(f"Generated sample PDFs in {out_dir}")
