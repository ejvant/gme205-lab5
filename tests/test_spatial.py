import sys
from pathlib import Path

import pytest
from shapely.geometry import box

# Run pytest from the repository root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

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


# Parcel rejects a missing ID, blank zone, or non-positive area_sqm
def test_parcel_rejects_missing_id():
    with pytest.raises(ValueError):
        Parcel("", box(0, 0, 1, 1), "Residential", 100)


def test_parcel_rejects_blank_zone():
    with pytest.raises(ValueError):
        Parcel("P-X", box(0, 0, 1, 1), "", 100)


def test_parcel_rejects_zero_area():
    with pytest.raises(ValueError):
        Parcel("P-X", box(0, 0, 1, 1), "Residential", 0)


def test_parcel_rejects_negative_area():
    with pytest.raises(ValueError):
        Parcel("P-X", box(0, 0, 1, 1), "Residential", -5)


def test_parcel_rejects_missing_geometry():
    with pytest.raises(ValueError):
        Parcel("P-X", None, "Residential", 100)


# Parcel exposes valid state through properties
def test_parcel_exposes_state_through_properties(parcel_a):
    assert parcel_a.parcel_id == "P-001"
    assert parcel_a.zone == "Residential"
    assert parcel_a.area_sqm == 7200.0


def test_parcel_properties_are_read_only(parcel_a):
    with pytest.raises(AttributeError):
        parcel_a.area_sqm = 1


# intersects(...) delegates to its geometry
def test_intersects_delegates_to_geometry(parcel_a, parcel_b, hazard):
    assert parcel_a.intersects(hazard) is True
    assert parcel_b.intersects(hazard) is False
    assert parcel_a.intersects(hazard) == parcel_a.geometry.intersects(hazard.geometry)


def test_hazard_zone_state(hazard):
    assert hazard.zone_id == "HZ-01"
    assert hazard.hazard_type == "Flood"
    assert hazard.severity == "High"


def test_hazard_zone_rejects_missing_id():
    with pytest.raises(ValueError):
        HazardZone("", box(0, 0, 1, 1), "Flood", "Low")