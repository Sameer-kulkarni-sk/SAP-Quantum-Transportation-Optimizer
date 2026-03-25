"""Lane (route) data model"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Lane:
    """Represents a transportation lane/route between two locations"""

    lane_id: str
    origin: str
    destination: str
    distance_km: float
    travel_time_hours: float
    toll_cost_eur: float
    traffic_factor: float = 1.0  # 1.0 = normal, >1.0 = congested

    def __post_init__(self):
        """Validate lane data"""
        if self.distance_km <= 0:
            raise ValueError("Distance must be positive")
        if self.travel_time_hours <= 0:
            raise ValueError("Travel time must be positive")
        if self.toll_cost_eur < 0:
            raise ValueError("Toll cost cannot be negative")
        if self.traffic_factor < 0.5 or self.traffic_factor > 3.0:
            raise ValueError("Traffic factor must be between 0.5 and 3.0")

    def total_cost(self, cost_per_km: float) -> float:
        """
        Calculate total cost for this lane

        Args:
            cost_per_km: Truck's cost per kilometer

        Returns:
            Total cost including traffic and tolls
        """
        return (cost_per_km * self.distance_km * self.traffic_factor +
                self.toll_cost_eur)

    def total_co2(self, co2_per_km: float) -> float:
        """
        Calculate total CO₂ emissions for this lane

        Args:
            co2_per_km: Truck's CO₂ emissions per kilometer

        Returns:
            Total CO₂ emissions in kg
        """
        return co2_per_km * self.distance_km * self.traffic_factor

    def effective_distance(self) -> float:
        """Calculate effective distance accounting for traffic"""
        return self.distance_km * self.traffic_factor

    def average_speed_kmh(self) -> float:
        """Calculate average speed in km/h"""
        if self.travel_time_hours == 0:
            return 0.0
        return self.distance_km / self.travel_time_hours

    def get_traffic_level(self) -> str:
        """Get traffic level description"""
        if self.traffic_factor < 1.1:
            return 'low'
        elif self.traffic_factor < 1.3:
            return 'medium'
        else:
            return 'high'

    def matches_route(self, origin: str, destination: str) -> bool:
        """Check if lane matches a given route"""
        return (self.origin.lower() == origin.lower() and
                self.destination.lower() == destination.lower())

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'lane_id': self.lane_id,
            'origin': self.origin,
            'destination': self.destination,
            'distance_km': self.distance_km,
            'travel_time_hours': self.travel_time_hours,
            'toll_cost_eur': self.toll_cost_eur,
            'traffic_factor': self.traffic_factor
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Lane':
        """Create Lane from dictionary"""
        return cls(**data)

    def __str__(self) -> str:
        """String representation"""
        return (f"Lane({self.lane_id}: {self.origin}->{self.destination}, "
                f"{self.distance_km}km, Traffic: {self.get_traffic_level()})")
