from pathlib import Path

from app.rules.engine import DiagnosticEngine
from app.rules.knowledge_base import DIAGNOSTIC_RULES
from app.data.db import init_db, save_session, save_results
from app.data.queries import get_session, get_results_for_session
from app.reports.pdf_report import generate_pdf_report


def ask_yes_no(prompt: str) -> bool:
    while True:
        response = input(prompt).lower().strip()
        if response in ("y", "n"):
            return response == "y"
        print("Please type 'y' or 'n'.")


def run_cli():
    print("\n=== PC Builder Troubleshooter ===\n")

    init_db()

    user_notes = input("Optional: add a short note (build specs / what happened): ").strip()
    answers = {}

    print("\nAnswer the symptom questions:\n")

    for rule in DIAGNOSTIC_RULES:
        answers[rule["symptom"]] = ask_yes_no(f"{rule['question']} (y/n): ")

    engine = DiagnosticEngine()
    results = engine.run(answers)

    session_id = save_session(user_notes=user_notes, answers=answers)
    save_results(session_id=session_id, results=results)

    print("\n--- Diagnostic Results ---\n")

    if not results:
        print(f"No matching issues detected. (Saved session #{session_id})")
    else:
        print(f"Saved session #{session_id}\n")
        for result in results:
            print(f"Symptom: {result['symptom'].replace('_', ' ').title()}")
            print("Probable Causes:")
            for cause in result["probable_causes"]:
                print(f" - {cause}")
            print("Next Tests:")
            for test in result["next_tests"]:
                print(f" - {test}")
            print()

    # PDF generation
    if ask_yes_no("Generate a PDF report now? (y/n): "):
        session = get_session(session_id)
        results_for_pdf = get_results_for_session(session_id)

        output_dir = Path("reports_out")
        pdf_path = generate_pdf_report(session, results_for_pdf, output_dir)
        print(f"\n✅ PDF generated: {pdf_path.resolve()}\n")


if __name__ == "__main__":
    run_cli()
