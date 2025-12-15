from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


def generate_pdf_report(session: dict, results: list[dict], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    session_id = session["id"]
    pdf_path = output_dir / f"pc_diagnostic_report_session_{session_id}.pdf"

    c = canvas.Canvas(str(pdf_path), pagesize=LETTER)
    width, height = LETTER

    y = height - 60

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "PC Builder Troubleshooter Report")
    y -= 30

    # Meta
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Session ID: {session_id}")
    y -= 16
    c.drawString(50, y, f"Created (UTC): {session['created_at']}")
    y -= 24

    # Notes
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "User Notes:")
    y -= 16
    c.setFont("Helvetica", 11)
    notes = session["user_notes"].strip() or "(none)"
    c.drawString(60, y, notes)
    y -= 24

    # Answers
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Answers:")
    y -= 16
    c.setFont("Helvetica", 11)

    for key, value in session["answers"].items():
        line = f"- {key.replace('_', ' ')}: {'YES' if value else 'NO'}"
        c.drawString(60, y, line)
        y -= 14
        if y < 80:
            c.showPage()
            y = height - 60
            c.setFont("Helvetica", 11)

    y -= 10

    # Results
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Diagnostic Results:")
    y -= 18

    if not results:
        c.setFont("Helvetica", 11)
        c.drawString(60, y, "No matching issues detected.")
    else:
        for r in results:
            c.setFont("Helvetica-Bold", 11)
            c.drawString(55, y, f"Symptom: {r['symptom'].replace('_', ' ').title()}")
            y -= 16

            c.setFont("Helvetica-Bold", 11)
            c.drawString(60, y, "Probable Causes:")
            y -= 14
            c.setFont("Helvetica", 11)
            for cause in r["probable_causes"]:
                c.drawString(75, y, f"- {cause}")
                y -= 14
                if y < 80:
                    c.showPage()
                    y = height - 60
                    c.setFont("Helvetica", 11)

            c.setFont("Helvetica-Bold", 11)
            c.drawString(60, y, "Next Tests:")
            y -= 14
            c.setFont("Helvetica", 11)
            for test in r["next_tests"]:
                c.drawString(75, y, f"- {test}")
                y -= 14
                if y < 80:
                    c.showPage()
                    y = height - 60
                    c.setFont("Helvetica", 11)

            y -= 10
            if y < 80:
                c.showPage()
                y = height - 60

    c.save()
    return pdf_path
