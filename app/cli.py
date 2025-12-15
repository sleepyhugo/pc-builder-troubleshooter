from rules.engine import DiagnosticEngine
from rules.knowledge_base import DIAGNOSTIC_RULES
from data.db import init_db, save_session, save_results


def run_cli():
    print("\n=== PC Builder Troubleshooter ===\n")

    init_db()

    user_notes = input("Optional: add a short note (build specs / what happened): ").strip()
    answers = {}

    print("\nAnswer the symptom questions:\n")

    for rule in DIAGNOSTIC_RULES:
        while True:
            response = input(f"{rule['question']} (y/n): ").lower().strip()
            if response in ("y", "n"):
                answers[rule["symptom"]] = (response == "y")
                break
            print("Please type 'y' or 'n'.")

    engine = DiagnosticEngine()
    results = engine.run(answers)

    session_id = save_session(user_notes=user_notes, answers=answers)
    save_results(session_id=session_id, results=results)

    print("\n--- Diagnostic Results ---\n")

    if not results:
        print(f"No matching issues detected. (Saved session #{session_id})")
        return

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


if __name__ == "__main__":
    run_cli()
