from rules.engine import DiagnosticEngine
from rules.knowledge_base import DIAGNOSTIC_RULES


def run_cli():
    print("\n=== PC Builder Troubleshooter ===\n")

    answers = {}

    for rule in DIAGNOSTIC_RULES:
        response = input(f"{rule['question']} (y/n): ").lower()
        answers[rule["symptom"]] = response == "y"

    engine = DiagnosticEngine()
    results = engine.run(answers)

    print("\n--- Diagnostic Results ---\n")

    if not results:
        print("No matching issues detected.")
        return

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
