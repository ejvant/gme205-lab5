import json
import sys
from pathlib import Path

import pytest
from shapely.geometry import box

# Run pytest from the repository root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from assessment import ParcelAssessment  # noqa: E402
from rules import AllowedZoneRule, MinimumAreaRule, NoHazardOverlapRule, RuleResult  # noqa: E402
from spatial import HazardZone, Parcel  # noqa: E402


# Same coordinates as run_lab5.py
@pytest.fixture
def parcel_a():
    return Parcel("P-001", box(0, 0, 80, 90), "Residential", 7200)


@pytest.fixture
def parcel_b():
    return Parcel("P-002", box(120, 0, 190, 80), "Commercial", 5600)


@pytest.fixture
def hazard():
    return HazardZone("HZ-01", box(60, 50, 110, 100), "Flood", "High")


@pytest.fixture
def scenario_rules(hazard):
    return [
        MinimumAreaRule(5000),
        AllowedZoneRule({"Residential", "Commercial"}),
        NoHazardOverlapRule(hazard),
    ]


# One polymorphism test worth writing
def test_assessment_accepts_mixed_rule_subclasses(parcel_b, hazard):
    rules = [
        MinimumAreaRule(5000),
        AllowedZoneRule({"Residential", "Commercial"}),
        NoHazardOverlapRule(hazard),
    ]

    assessment = ParcelAssessment(parcel_b, rules)
    results = assessment.evaluate()

    assert len(results) == 3
    assert all(isinstance(result, RuleResult) for result in results)


# UML multiplicities: exactly 1 parcel, 1..* rules
def test_requires_a_parcel(scenario_rules):
    with pytest.raises(ValueError):
        ParcelAssessment(None, scenario_rules)


def test_requires_at_least_one_rule(parcel_a):
    with pytest.raises(ValueError):
        ParcelAssessment(parcel_a, [])


# P-001 fails only the hazard-overlap rule
def test_p001_fails_only_hazard_rule(parcel_a, scenario_rules):
    assessment = ParcelAssessment(parcel_a, scenario_rules)
    failed = [r.rule_name for r in assessment.evaluate() if not r.passed]
    assert failed == ["NoHazardOverlapRule"]
    assert assessment.passed() is False


# P-002 passes all three rules
def test_p002_passes_all_rules(parcel_b, scenario_rules):
    assessment = ParcelAssessment(parcel_b, scenario_rules)
    assert all(r.passed for r in assessment.evaluate())
    assert assessment.passed() is True


def test_to_dict_is_json_ready(parcel_a, scenario_rules):
    data = ParcelAssessment(parcel_a, scenario_rules).to_dict()
    json.dumps(data)   # raises if a Shapely geometry slipped into the report
    assert data["parcel_id"] == "P-001"
    assert data["passed"] is False