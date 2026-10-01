from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class RuleResult:
    rule_name: str
    passed: bool
    message: str

class AssessmentRule(ABC):
    def __init__(self, name: str):
        self._name = name
        
    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def evaluate(self, parcel) -> RuleResult:
        pass

class MinimumAreaRule(AssessmentRule):
    def evaluate(self, parcel) -> RuleResult:
        ...

class AllowedZoneRule(AssessmentRule):
    def evaluate(self, parcel) -> RuleResult:
        ...

class NoHazardOverlapRule(AssessmentRule):
    def evaluate(self, parcel) -> RuleResult:
        ...