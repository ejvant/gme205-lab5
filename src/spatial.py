class Parcel:
    def __init__(self, parcel_id, geometry, zone, area_sqm):
        ...

    def intersects(self, other):
        ...

class HazardZone:
    def __init__(self, zone_id, geometry, hazard_type, severity):
        ...
