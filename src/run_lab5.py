import json
from pathlib import Path

from shapely.geometry import LineString, box   # LineString

from assessment import ParcelAssessment
from rules import AllowedZoneRule, MinimumAreaRule, NoHazardOverlapRule, RoadAccessRule  
from spatial import HazardZone, Parcel, Road 

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "output" / "lab5_report.json"


def main():
    # 1. construct spatial objects
    parcel_a = Parcel(
        "P-001",
        box(0, 0, 80, 90),
        "Residential",
        7200,
    )

    parcel_b = Parcel(
        "P-002",
        box(120, 0, 190, 80),
        "Commercial",
        5600,
    )

    hazard = HazardZone(
        "HZ-01",
        box(60, 50, 110, 100),
        "Flood",
        "High",
    )

    road = Road(                
        "RD-01",
        LineString([(0, -10), (200, -10)]),
    )

    # 2. construct rule objects
    rules = [
        MinimumAreaRule(5000),
        AllowedZoneRule({"Residential", "Commercial"}),
        NoHazardOverlapRule(hazard),
        RoadAccessRule(road, 20),                 
    ]

    # 3. compose ParcelAssessment objects
    assessments = [
        ParcelAssessment(parcel_a, rules),
        ParcelAssessment(parcel_b, rules),
    ]

    # 4 + 5. evaluate each parcel and assemble JSON-ready dictionaries
    report = {
        "scenario": "parcel-development-assessment",
        "parcels": [a.to_dict() for a in assessments],
    }

    # 6. write output/lab5_report.json
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    for entry in report["parcels"]:
        status = "PASS" if entry["passed"] else "FAIL"
        print(f"{entry['parcel_id']}: {status}")
        for r in entry["results"]:
            mark = "ok " if r["passed"] else "X  "
            print(f"   {mark}{r['rule_name']}: {r['message']}")
    print(f"\nReport written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()