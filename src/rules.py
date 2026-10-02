from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class RuleResult:
    rule_name: str
    passed: bool
    message: str

    def to_dict(self):
        return {"rule_name": self.rule_name, "passed": self.passed, "message": self.message}

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
    def __init__(self, min_area):
        super().__init__("MinimumAreaRule")
        self._min_area = float(min_area)

    @property
    def min_area(self):
        return self._min_area

    def evaluate(self, parcel):
        passed = parcel.area_sqm >= self._min_area
        message = (
            f"{parcel.area_sqm:.0f} m² >= {self._min_area:.0f} m²"
            if passed
            else f"{parcel.area_sqm:.0f} m² < {self._min_area:.0f} m²"
        )
        return RuleResult(self.name, passed, message)

class AllowedZoneRule(AssessmentRule):
    def __init__(self, allowed_zones):
        super().__init__("AllowedZoneRule")
        self._allowed_zones = set(allowed_zones)

    @property
    def allowed_zones(self):
        return self._allowed_zones

    def evaluate(self, parcel):
        passed = parcel.zone in self._allowed_zones
        allowed = ", ".join(sorted(self._allowed_zones))
        message = (
            f"{parcel.zone}' is in allowed zones ({allowed})"
            if passed
            else f"{parcel.zone}' is not in allowed zones ({allowed})"
        )
        return RuleResult(self.name, passed, message)

class NoHazardOverlapRule(AssessmentRule):
    def __init__(self, hazard_zone):
        super().__init__("NoHazardOverlapRule")
        self._hazard_zone = hazard_zone

    @property
    def hazard_zone(self):
        return self._hazard_zone

    def evaluate(self, parcel):
        hz = self._hazard_zone
        overlaps = parcel.intersects(hz)
        passed = not overlaps
        message = (
            f"does not intersect {hz.zone_id} ({hz.hazard_type}, {hz.severity})"
            if passed
            else f"intersects {hz.zone_id} ({hz.hazard_type}, {hz.severity})"
        )
        return RuleResult(self.name, passed, message)

class RoadAccessRule(AssessmentRule):
    def __init__(self, road, max_distance):
        super().__init__("RoadAccessRule")
        self._road = road
        self._max_distance = float(max_distance)

    @property
    def road(self):
        return self._road

    @property
    def max_distance(self):
        return self._max_distance

    def evaluate(self, parcel):
        distance = parcel.geometry.distance(self._road.geometry)
        passed = distance <= self._max_distance
        message = (
            f"{distance:.1f} m to {self._road.road_id} <= {self._max_distance:.1f} m"
            if passed
            else f"{distance:.1f} m to {self._road.road_id} > {self._max_distance:.1f} m"
        )
        return RuleResult(self.name, passed, message)