from pathlib import Path

from app.rules.engine import DiagnosticEngine
from app.rules.knowledge_base import DIAGNOSTIC_RULES
from app.data.db import init_db, save_session, save_results
from app.data.queries import (
    get_session,
    get_results_for_session,
    list_recent_sessions,
)
from app.reports.pdf_report import generate_pdf_report


def ask_yes_no(prompt: str) -> bool:
    while True:
        response = input(prompt).lower().strip()
        if response in ("y", "n"):
            return response == "y"
        print("Please type 'y' or 'n'.")


def ask_int(prompt: str) -> int | None:
    raw = input(prompt).strip()
    if not raw.isdigit():
        return None
    return int(raw)


def run_new_diagnostic() -> int:
    print("\n=== New Diagnostic Session ===\n")

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

    if ask_yes_no("Generate a PDF report now? (y/n): "):
        generate_pdf_for_session(session_id)

    return session_id


def show_recent_sessions():
    sessions = list_recent_sessions(limit=10)

    print("\n=== Recent Sessions (last 10) ===\n")
    if not sessions:
        print("No sessions found yet.\n")
        return

    for s in sessions:
        note_preview = (s["user_notes"][:50] + "...") if len(s["user_notes"]) > 50 else s["user_notes"]
        note_preview = note_preview if note_preview else "(no notes)"
        print(f"#{s['id']} | {s['created_at']} | {note_preview}")
    print()


def generate_pdf_for_session(session_id: int):
    session = get_session(session_id)
    if not session:
        print(f"\nNo session found with id {session_id}\n")
        return

    results = get_results_for_session(session_id)
    output_dir = Path("reports_out")
    pdf_path = generate_pdf_report(session, results, output_dir)

    print(f"\nPDF generated: {pdf_path.resolve()}\n")


def menu_loop():
    init_db()

    while True:
        print("=== PC Builder Troubleshooter ===")
        print("1) New diagnostic")
        print("2) List recent sessions")
        print("3) Generate PDF for a session ID")
        print("4) Quit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            run_new_diagnostic()
        elif choice == "2":
            show_recent_sessions()
        elif choice == "3":
            session_id = ask_int("Enter session ID: ")
            if session_id is None:
                print("\nPlease enter a valid numeric session ID.\n")
            else:
                generate_pdf_for_session(session_id)
        elif choice == "4":
            print("\nGoodbye!\n")
            break
        else:
            print("\nInvalid option. Choose 1-4.\n")


if __name__ == "__main__":
    menu_loop()
