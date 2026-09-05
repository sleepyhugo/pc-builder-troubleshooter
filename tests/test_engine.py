import copy

import pytest

from app.rules.engine import DiagnosticEngine
from app.rules.knowledge_base import DIAGNOSTIC_RULES


@pytest.fixture(autouse=True)
def restore_knowledge_base():
    """Undo any mutation of the shared rule list between tests."""
    pristine = copy.deepcopy(DIAGNOSTIC_RULES)
    yield
    DIAGNOSTIC_RULES[:] = pristine


def test_no_symptoms_reported_returns_nothing():
    results = DiagnosticEngine().run({symptom: False for symptom in
                                      [r["symptom"] for r in DIAGNOSTIC_RULES]})
    assert results == []


def test_empty_answers_returns_nothing():
    assert DiagnosticEngine().run({}) == []


def test_single_symptom_returns_matching_rule():
    results = DiagnosticEngine().run({"no_power": True})

    assert len(results) == 1
    assert results[0]["symptom"] == "no_power"
    assert results[0]["probable_causes"]
    assert results[0]["next_tests"]


def test_multiple_symptoms_return_multiple_rules():
    results = DiagnosticEngine().run({"no_power": True, "random_shutdowns": True})

    assert {r["symptom"] for r in results} == {"no_power", "random_shutdowns"}


def test_unknown_symptom_is_ignored():
    assert DiagnosticEngine().run({"cpu_on_fire": True}) == []


def test_engine_is_reusable_across_runs():
    engine = DiagnosticEngine()
    engine.run({"no_power": True})
    second = engine.run({"random_shutdowns": True})

    assert [r["symptom"] for r in second] == ["random_shutdowns"]


@pytest.mark.xfail(
    reason="Engine returns references to the shared DIAGNOSTIC_RULES dicts, "
           "so a caller mutating a result corrupts the knowledge base "
           "process-wide. Fix by returning copies.",
    strict=True,
)
def test_results_do_not_alias_the_knowledge_base():
    results = DiagnosticEngine().run({"no_power": True})
    results[0]["probable_causes"].append("polluted")

    fresh = DiagnosticEngine().run({"no_power": True})
    assert "polluted" not in fresh[0]["probable_causes"]


@pytest.mark.xfail(
    reason="Engine tests truthiness, so the string 'n' counts as yes. "
           "Harmless while both callers pass real bools, but a JSON API "
           "would report false positives.",
    strict=True,
)
def test_string_no_is_not_treated_as_yes():
    assert DiagnosticEngine().run({"no_power": "n"}) == []