import sys
from pathlib import Path

import pytest
from shapely.geometry import LineString, box

# Run pytest from the repository root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rules import (  # noqa: E402
    AllowedZoneRule,
    AssessmentRule,
    MinimumAreaRule,
    NoHazardOverlapRule,
    RoadAccessRule,
    RuleResult,
)
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


def make_parcel(area=6000, zone="Residential"):
    """A small synthetic parcel for testing one rule at a time."""
    return Parcel("T-1", box(0, 0, 10, 10), zone, area)


# AssessmentRule cannot be instantiated directly
def test_assessment_rule_is_abstract():
    with pytest.raises(TypeError):
        AssessmentRule("generic")


# MinimumAreaRule returns a RuleResult for both pass and fail cases
def test_minimum_area_pass_and_fail():
    rule = MinimumAreaRule(5000)
    ok = rule.evaluate(make_parcel(area=5000))
    bad = rule.evaluate(make_parcel(area=4999))
    assert isinstance(ok, RuleResult)
    assert isinstance(bad, RuleResult)
    assert ok.passed is True
    assert bad.passed is False


# AllowedZoneRule accepts an allowed zone and rejects a disallowed zone
def test_allowed_zone_accepts_and_rejects():
    rule = AllowedZoneRule({"Residential", "Commercial"})
    assert rule.evaluate(make_parcel(zone="Commercial")).passed is True
    assert rule.evaluate(make_parcel(zone="Industrial")).passed is False


# NoHazardOverlapRule fails an intersecting parcel and passes a non-intersecting one
def test_no_hazard_overlap(parcel_a, parcel_b, hazard):
    rule = NoHazardOverlapRule(hazard)
    assert rule.evaluate(parcel_a).passed is False   # P-001 overlaps HZ-01
    assert rule.evaluate(parcel_b).passed is True    # P-002 is clear of HZ-01


def test_rule_result_to_dict():
    result = RuleResult("x", True, "ok")
    assert result.to_dict() == {"rule_name": "x", "passed": True, "message": "ok"}

# Part I: RoadAccessRule
def test_road_access_near_and_far():
    road = Road("RD-T", LineString([(0, -10), (100, -10)]))
    rule = RoadAccessRule(road, 20)
    near = Parcel("T-NEAR", box(0, 0, 10, 10), "Residential", 100)   # 10 m from the road
    far = Parcel("T-FAR", box(0, 50, 10, 60), "Residential", 100)    # 60 m from the road
    assert rule.evaluate(near).passed is True
    assert rule.evaluate(far).passed is False