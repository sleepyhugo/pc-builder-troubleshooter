def summarize_results(results: list[dict]) -> str:
    # Generates a short readable summary of diagnostic results.
    if not results:
        return "No obvious hardware issues detected based on provided symptoms."

    symptoms = {r["symptom"].replace("_", " ") for r in results}

    return (
        "Potential issues detected related to: "
        + ", ".join(sorted(symptoms))
        + "."
    )
