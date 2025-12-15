from pathlib import Path
from app.data.queries import get_session, get_results_for_session
from app.reports.pdf_report import generate_pdf_report


def main():
    session_id = int(input("Enter session ID to generate PDF for: ").strip())

    session = get_session(session_id)
    if not session:
        print(f"No session found with id {session_id}")
        return

    results = get_results_for_session(session_id)

    output_dir = Path("reports_out")
    pdf_path = generate_pdf_report(session, results, output_dir)

    print(f"\n✅ PDF generated: {pdf_path.resolve()}\n")


if __name__ == "__main__":
    main()
