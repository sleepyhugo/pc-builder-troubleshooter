from .knowledge_base import DIAGNOSTIC_RULES


class DiagnosticEngine:
    def __init__(self):
        self.results = []

    def run(self, answers: dict):
        self.results.clear()

        for rule in DIAGNOSTIC_RULES:
            symptom = rule["symptom"]
            if answers.get(symptom):
                self.results.append(rule)

        return self.results
