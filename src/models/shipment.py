"""Shipment data model"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Shipment:
    """Represents a shipment to be transported"""

    shipment_id: str
    origin: str
    destination: str
    weight_kg: float
    volume_m3: float
    priority: int  # 1-5, where 5 is highest priority
    deadline: datetime
    value_eur: float

    def __post_init__(self):
        """Validate shipment data"""
        if self.priority < 1 or self.priority > 5:
            raise ValueError("Priority must be between 1 and 5")
        if self.weight_kg <= 0:
            raise ValueError("Weight must be positive")
        if self.volume_m3 <= 0:
            raise ValueError("Volume must be positive")
        if self.value_eur < 0:
            raise ValueError("Value cannot be negative")

    def urgency_score(self, current_time: Optional[datetime] = None) -> float:
        """
        Calculate urgency score based on deadline and priority

        Args:
            current_time: Current time (defaults to now)

        Returns:
            Urgency score (higher = more urgent)
        """
        if current_time is None:
            current_time = datetime.now()

        hours_until_deadline = (
            self.deadline - current_time).total_seconds() / 3600

        # Avoid division by zero and handle past deadlines
        if hours_until_deadline <= 0:
            return float('inf')  # Past deadline - extremely urgent

        # Urgency increases with priority and decreases with time remaining
        return self.priority * (100.0 / hours_until_deadline)

    def is_overdue(self, current_time: Optional[datetime] = None) -> bool:
        """Check if shipment is past its deadline"""
        if current_time is None:
            current_time = datetime.now()
        return current_time > self.deadline

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'shipment_id': self.shipment_id,
            'origin': self.origin,
            'destination': self.destination,
            'weight_kg': self.weight_kg,
            'volume_m3': self.volume_m3,
            'priority': self.priority,
            'deadline': self.deadline.isoformat(),
            'value_eur': self.value_eur
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Shipment':
        """Create Shipment from dictionary"""
        data_copy = data.copy()
        if isinstance(data_copy['deadline'], str):
            data_copy['deadline'] = datetime.fromisoformat(
                data_copy['deadline'])
        return cls(**data_copy)

    def __str__(self) -> str:
        """String representation"""
        return (f"Shipment({self.shipment_id}: {self.origin}->{self.destination}, "
                f"{self.weight_kg}kg, Priority {self.priority})")
