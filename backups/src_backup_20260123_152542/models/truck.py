"""Truck data model"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Truck:
    """Represents a truck for transporting shipments"""

    truck_id: str
    capacity_weight_kg: float
    capacity_volume_m3: float
    cost_per_km_eur: float
    co2_per_km_kg: float
    location: str
    available: bool = True

    # Current state (mutable)
    current_load_weight: float = 0.0
    current_load_volume: float = 0.0
    assigned_shipments: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate truck data"""
        if self.capacity_weight_kg <= 0:
            raise ValueError("Weight capacity must be positive")
        if self.capacity_volume_m3 <= 0:
            raise ValueError("Volume capacity must be positive")
        if self.cost_per_km_eur < 0:
            raise ValueError("Cost per km cannot be negative")
        if self.co2_per_km_kg < 0:
            raise ValueError("CO2 per km cannot be negative")

    def can_accommodate(self, weight_kg: float, volume_m3: float) -> bool:
        """
        Check if truck can accommodate additional load

        Args:
            weight_kg: Additional weight to add
            volume_m3: Additional volume to add

        Returns:
            True if truck can accommodate the load
        """
        if not self.available:
            return False

        return (self.current_load_weight + weight_kg <= self.capacity_weight_kg and
                self.current_load_volume + volume_m3 <= self.capacity_volume_m3)

    def add_load(self, weight_kg: float, volume_m3: float, shipment_id: str) -> bool:
        """
        Add load to truck

        Args:
            weight_kg: Weight to add
            volume_m3: Volume to add
            shipment_id: ID of shipment being added

        Returns:
            True if load was added successfully
        """
        if not self.can_accommodate(weight_kg, volume_m3):
            return False

        self.current_load_weight += weight_kg
        self.current_load_volume += volume_m3
        self.assigned_shipments.append(shipment_id)
        return True

    def remove_load(self, weight_kg: float, volume_m3: float, shipment_id: str) -> bool:
        """
        Remove load from truck

        Args:
            weight_kg: Weight to remove
            volume_m3: Volume to remove
            shipment_id: ID of shipment being removed

        Returns:
            True if load was removed successfully
        """
        if shipment_id not in self.assigned_shipments:
            return False

        self.current_load_weight = max(0, self.current_load_weight - weight_kg)
        self.current_load_volume = max(0, self.current_load_volume - volume_m3)
        self.assigned_shipments.remove(shipment_id)
        return True

    def reset_load(self):
        """Reset truck to empty state"""
        self.current_load_weight = 0.0
        self.current_load_volume = 0.0
        self.assigned_shipments = []

    def utilization_weight(self) -> float:
        """Calculate weight utilization percentage"""
        if self.capacity_weight_kg == 0:
            return 0.0
        return (self.current_load_weight / self.capacity_weight_kg) * 100

    def utilization_volume(self) -> float:
        """Calculate volume utilization percentage"""
        if self.capacity_volume_m3 == 0:
            return 0.0
        return (self.current_load_volume / self.capacity_volume_m3) * 100

    def get_category(self) -> str:
        """Get truck category based on capacity"""
        if self.capacity_weight_kg < 3500:
            return 'light'
        elif self.capacity_weight_kg < 12000:
            return 'medium'
        else:
            return 'heavy'

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'truck_id': self.truck_id,
            'capacity_weight_kg': self.capacity_weight_kg,
            'capacity_volume_m3': self.capacity_volume_m3,
            'cost_per_km_eur': self.cost_per_km_eur,
            'co2_per_km_kg': self.co2_per_km_kg,
            'location': self.location,
            'available': self.available,
            'current_load_weight': self.current_load_weight,
            'current_load_volume': self.current_load_volume,
            'assigned_shipments': self.assigned_shipments.copy()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Truck':
        """Create Truck from dictionary"""
        return cls(**data)

    def __str__(self) -> str:
        """String representation"""
        return (f"Truck({self.truck_id}: {self.get_category()}, "
                f"{self.capacity_weight_kg}kg capacity, "
                f"Load: {self.utilization_weight():.1f}%)")
