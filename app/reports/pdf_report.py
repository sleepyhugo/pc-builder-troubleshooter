from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# --- Theme Colors (Matches Void Black UI) ---
ACCENT_COLOR = colors.HexColor("#0ea5e9")
DARK_BG = colors.HexColor("#0e1117")
TEXT_COLOR = colors.HexColor("#1f2630")
MUTED_COLOR = colors.HexColor("#64748b")


def generate_pdf_report(session: dict, results: list[dict], output_dir: Path) -> Path:
    # Setup Output Path
    output_dir.mkdir(parents=True, exist_ok=True)
    session_id = session.get("id", "unknown")
    pdf_path = output_dir / f"pc_diagnostic_report_session_{session_id}.pdf"

    # Initialize PDF Document
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=LETTER,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40,
        title=f"Diagnostic Report #{session_id}"
    )

    # Define Technical Styles
    styles = getSampleStyleSheet()

    # Title Style
    style_title = ParagraphStyle(
        'TechTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        spaceAfter=12
    )

    # Section Header Style
    style_heading = ParagraphStyle(
        'TechHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=ACCENT_COLOR,
        fontName='Helvetica-Bold',
        borderPadding=0,
        borderWidth=0,
        borderBottomWidth=1,
        borderColor=ACCENT_COLOR,
        spaceBefore=15,
        spaceAfter=10
    )

    # Body Text Style
    style_body = ParagraphStyle(
        'TechBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=TEXT_COLOR
    )

    # Monospace/Data Style
    style_mono = ParagraphStyle(
        'TechMono',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9,
        textColor=MUTED_COLOR,
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=6
    )

    # Build Content Elements
    elements = []

    # Header Block (Dark Banner)
    header_data = [
        [Paragraph("DIAGNOSTIC MANIFEST", style_title)],
        [Paragraph(f"SESSION ID: {session_id}",
                   ParagraphStyle('Sub', parent=style_mono, textColor=colors.white, backColor=None))]
    ]
    header_table = Table(header_data, colWidths=[6.5 * inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_BG),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # Meta Data
    date_str = session.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    elements.append(Paragraph(f"<b>TIMESTAMP:</b> {date_str}", style_body))
    elements.append(Spacer(1, 10))

    # User Notes
    elements.append(Paragraph("OBSERVATION LOG", style_heading))
    user_notes = session.get('user_notes', '').strip()
    if not user_notes:
        user_notes = "No user notes provided."
    elements.append(Paragraph(user_notes, style_mono))
    elements.append(Spacer(1, 15))

    # Input Telemetry (Symptom Checklist)
    elements.append(Paragraph("INPUT TELEMETRY", style_heading))

    telemetry_data = [["SYMPTOM CHECKED", "STATUS"]]
    for key, val in session.get('answers', {}).items():
        status_text = "DETECTED" if val else "CLEAR"

        # Style the status text
        if val:
            status_cell = Paragraph(f"<b>{status_text}</b>",
                                    ParagraphStyle('Red', parent=style_body, textColor=colors.red, alignment=1))
        else:
            status_cell = Paragraph(status_text,
                                    ParagraphStyle('Grey', parent=style_body, textColor=MUTED_COLOR, alignment=1))

        telemetry_data.append([key.replace('_', ' ').upper(), status_cell])

    t = Table(telemetry_data, colWidths=[4.5 * inch, 1.5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),  # Header Row Grey
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0, 1), (-1, -1), 'Courier'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # Diagnostic Results
    elements.append(Paragraph("ANALYSIS & RECOMMENDATIONS", style_heading))

    if not results:
        elements.append(Paragraph("No specific hardware faults matched the rule engine.", style_body))
    else:
        for res in results:
            symptom_name = res.get('symptom', 'Unknown Issue').replace('_', ' ').upper()

            # Fault Header
            elements.append(Paragraph(f"⚠ FAULT DETECTED: {symptom_name}",
                                      ParagraphStyle('Warn', parent=styles['Heading3'], textColor=colors.red,
                                                     spaceAfter=6)))

            # Causes
            elements.append(Paragraph("<b>PROBABLE CAUSES:</b>", style_body))
            cause_list = [f"&bull; {c}" for c in res.get('probable_causes', [])]
            for item in cause_list:
                elements.append(Paragraph(item, style_body))

            elements.append(Spacer(1, 8))

            # Next Steps
            elements.append(Paragraph("<b>RECOMMENDED ACTION:</b>", style_body))
            test_list = [f"&bull; {t}" for t in res.get('next_tests', [])]
            for item in test_list:
                elements.append(Paragraph(item, style_body))

            # Divider
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("_" * 65, style_mono))
            elements.append(Spacer(1, 15))

    # Footer
    elements.append(Spacer(1, 30))
    footer_text = "Generated by PC Builder Troubleshooter. Always disconnect power before handling components."
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=style_mono, fontSize=7, alignment=1)))

    # Generate File
    doc.build(elements)

    return pdf_path