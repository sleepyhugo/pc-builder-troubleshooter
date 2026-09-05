import pytest

from app.rules.knowledge_base import DIAGNOSTIC_RULES
from app.rules.summary import summarize_results
from app.rules.validator import validate_rules


def valid_rule(**overrides):
    rule = {
        "symptom": "no_power",
        "question": "Does the PC show no signs of power at all?",
        "probable_causes": ["Power supply failure"],
        "next_tests": ["Paperclip test the PSU"],
    }
    rule.update(overrides)
    return rule


def test_shipped_knowledge_base_is_valid():
    """The rules the app actually runs on must pass their own validator."""
    validate_rules(DIAGNOSTIC_RULES)


def test_symptom_keys_are_unique():
    symptoms = [rule["symptom"] for rule in DIAGNOSTIC_RULES]
    assert len(symptoms) == len(set(symptoms))


def test_accepts_a_well_formed_rule():
    validate_rules([valid_rule()])


@pytest.mark.parametrize(
    "missing", ["symptom", "question", "probable_causes", "next_tests"]
)
def test_rejects_rule_missing_a_required_key(missing):
    rule = valid_rule()
    del rule[missing]

    with pytest.raises(ValueError, match="missing required keys"):
        validate_rules([rule])


def test_rejects_empty_probable_causes():
    with pytest.raises(ValueError, match="probable_causes"):
        validate_rules([valid_rule(probable_causes=[])])


def test_rejects_empty_next_tests():
    with pytest.raises(ValueError, match="next_tests"):
        validate_rules([valid_rule(next_tests=[])])


def test_rejects_string_instead_of_list():
    """A JSON rule file makes this an easy mistake to ship."""
    with pytest.raises(ValueError, match="probable_causes"):
        validate_rules([valid_rule(probable_causes="Power supply failure")])


def test_error_names_the_offending_rule_index():
    rule = valid_rule()
    del rule["symptom"]

    with pytest.raises(ValueError, match="index 1"):
        validate_rules([valid_rule(), rule])


class TestSummarize:
    def test_no_results(self):
        assert "No obvious hardware issues" in summarize_results([])

    def test_lists_detected_symptoms_readably(self):
        summary = summarize_results([{"symptom": "no_power"}])
        assert "no power" in summary