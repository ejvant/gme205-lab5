from shapely.geometry import box

from assessment import ParcelAssessment
from rules import AllowedZoneRule, AssessmentRule, MinimumAreaRule, NoHazardOverlapRule
from spatial import HazardZone, Parcel

# Encapsulation (Valid Parcels)
p = Parcel("DEMO-1", box(0, 0, 50, 50), "Residential", 2500)
print("Parcel:", p.parcel_id, p.zone, p.area_sqm)

# Encapsulation (Invalid parcel is rejected)
try:
    Parcel("DEMO-2", box(0, 0, 1, 1), "Residential", -10)
except ValueError as e:
    print("Rejected bad parcel:", e)

# Encapsulation (Property cannot be changed from outside)
try:
    p.area_sqm = 1
except AttributeError:
    print("area_sqm is read-only")

# Spatial behavior lives on the Parcel
hz = HazardZone("HZ-X", box(40, 40, 60, 60), "Landslide", "Medium")
print("Intersects hazard:", p.intersects(hz))

# Abstraction (The base rule cannot be created)
try:
    AssessmentRule("generic")
except TypeError as e:
    print("Abstract:", e)

# Inheritance + polymorphism (Same evaluate(parcel) call on every rule)
rules = [
    MinimumAreaRule(5000),
    AllowedZoneRule({"Residential", "Commercial"}),
    NoHazardOverlapRule(hz),
]
for result in ParcelAssessment(p, rules).evaluate():
    print(result)