import json
import sys
from pathlib import Path

import pytest
from shapely.geometry import LineString, box

# Run pytest from the repository root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from assessment import ParcelAssessment 
from rules import AllowedZoneRule, MinimumAreaRule, NoHazardOverlapRule, RoadAccessRule, RuleResult 
from spatial import HazardZone, Parcel, Road 


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

# Part I: the new rule joins by adding one object to the list
def test_new_rule_joins_without_coordinator_change(parcel_b, scenario_rules):
    road = Road("RD-01", LineString([(0, -10), (200, -10)]))
    rules = scenario_rules + [RoadAccessRule(road, 20)]
    results = ParcelAssessment(parcel_b, rules).evaluate()
    assert len(results) == 4
    assert results[-1].rule_name == "RoadAccessRule"
    assert results[-1].passed is True