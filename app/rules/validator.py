REQUIRED_RULE_KEYS = {
    "symptom",
    "question",
    "probable_causes",
    "next_tests",
}


def validate_rules(rules: list[dict]) -> None:
    # Validate diagnostic rules to ensure required structure.
    # Raises ValueError if a rule is malformed.
    for idx, rule in enumerate(rules):
        missing = REQUIRED_RULE_KEYS - rule.keys()
        if missing:
            raise ValueError(
                f"Rule at index {idx} is missing required keys: {missing}"
            )

        if not isinstance(rule["probable_causes"], list) or not rule["probable_causes"]:
            raise ValueError(
                f"Rule '{rule['symptom']}' must have a non-empty probable_causes list"
            )

        if not isinstance(rule["next_tests"], list) or not rule["next_tests"]:
            raise ValueError(
                f"Rule '{rule['symptom']}' must have a non-empty next_tests list"
            )
