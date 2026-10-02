from rules import AssessmentRule

class ParcelAssessment:
    def __init__(self, parcel, rules):
        if parcel is None:
            raise ValueError("A parcel is required")
        rules = list(rules or [])
        if not rules:
            raise ValueError("At least one rule is required")
        for rule in rules:
            if not isinstance(rule, AssessmentRule):
                raise TypeError(f"{rule!r} is not an AssessmentRule")
        self._parcel = parcel
        self._rules = list(rules)

    @property
    def parcel(self):
        return self._parcel

    @property
    def rules(self):
        return tuple(self._rules)

    def evaluate(self):
        results = []
        for rule in self._rules:
            result = rule.evaluate(self._parcel)
            results.append(result)
        return results

    def passed(self):
        for result in self.evaluate():
            if not result.passed:
                return False
        return True

    def to_dict(self):
        results = self.evaluate()
        return {
            "parcel_id": self._parcel.parcel_id,
            "passed": all(r.passed for r in results),
            "results": [r.to_dict() for r in results],
        }