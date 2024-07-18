from dataclasses import dataclass


@dataclass
class Location:
    lat: float
    lon: float

    def to_dict(self):
        return {
            "lat": self.lat,
            "lon": self.lon,
        }
