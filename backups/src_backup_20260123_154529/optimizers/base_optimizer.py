"""Base optimizer class and result structure"""

from models.lane import Lane
from models.truck import Truck
from models.shipment import Shipment
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class OptimizationResult:
    """Result of an optimization run"""

    algorithm: str
    assignments: List[Dict[str, Any]]
    total_cost: float
    total_co2: float
    computation_time: float
    trucks_used: int
    shipments_assigned: int
    shipments_unassigned: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'algorithm': self.algorithm,
            'total_cost_eur': round(self.total_cost, 2),
            'total_co2_kg': round(self.total_co2, 2),
            'computation_time_sec': round(self.computation_time, 3),
            'trucks_used': self.trucks_used,
            'shipments_assigned': self.shipments_assigned,
            'shipments_unassigned': self.shipments_unassigned,
            'assignments_count': len(self.assignments),
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }

    def summary(self) -> str:
        """Get summary string"""
        return (f"{self.algorithm} Results:\n"
                f"  Total Cost: €{self.total_cost:.2f}\n"
                f"  Total CO₂: {self.total_co2:.2f} kg\n"
                f"  Computation Time: {self.computation_time:.3f}s\n"
                f"  Trucks Used: {self.trucks_used}\n"
                f"  Shipments Assigned: {self.shipments_assigned}/{self.shipments_assigned + self.shipments_unassigned}")


class BaseOptimizer(ABC):
    """Abstract base class for optimization algorithms"""

    def __init__(self, shipments: List[Shipment],
                 trucks: List[Truck],
                 lanes: List[Lane]):
        """
        Initialize optimizer

        Args:
            shipments: List of shipments to assign
            trucks: List of available trucks
            lanes: List of available lanes/routes
        """
        self.shipments = shipments
        self.trucks = trucks
        self.lanes = lanes
        self.assignments = []

    @abstractmethod
    def optimize(self, **kwargs) -> OptimizationResult:
        """
        Run optimization algorithm

        Returns:
            OptimizationResult with assignments and metrics
        """
        pass

    def find_matching_lanes(self, origin: str, destination: str) -> List[Lane]:
        """
        Find lanes matching a route

        Args:
            origin: Origin location
            destination: Destination location

        Returns:
            List of matching lanes
        """
        return [lane for lane in self.lanes
                if lane.matches_route(origin, destination)]

    def calculate_assignment_cost(self, shipment: Shipment,
                                  truck: Truck,
                                  lane: Lane) -> float:
        """
        Calculate cost for a specific assignment

        Args:
            shipment: Shipment to assign
            truck: Truck to use
            lane: Lane to use

        Returns:
            Total cost in EUR
        """
        return lane.total_cost(truck.cost_per_km_eur)

    def calculate_assignment_co2(self, shipment: Shipment,
                                 truck: Truck,
                                 lane: Lane) -> float:
        """
        Calculate CO₂ emissions for a specific assignment

        Args:
            shipment: Shipment to assign
            truck: Truck to use
            lane: Lane to use

        Returns:
            Total CO₂ in kg
        """
        return lane.total_co2(truck.co2_per_km_kg)

    def reset_trucks(self):
        """Reset all trucks to empty state"""
        for truck in self.trucks:
            truck.reset_load()

    def get_available_trucks(self) -> List[Truck]:
        """Get list of available trucks"""
        return [truck for truck in self.trucks if truck.available]

    def validate_solution(self, assignments: List[Dict]) -> bool:
        """
        Validate that a solution is feasible

        Args:
            assignments: List of assignments to validate

        Returns:
            True if solution is valid
        """
        # Check truck capacities
        truck_loads = {truck.truck_id: {'weight': 0.0, 'volume': 0.0}
                       for truck in self.trucks}

        for assignment in assignments:
            truck = assignment['truck']
            shipment = assignment['shipment']

            truck_loads[truck.truck_id]['weight'] += shipment.weight_kg
            truck_loads[truck.truck_id]['volume'] += shipment.volume_m3

            # Check if capacity exceeded
            if (truck_loads[truck.truck_id]['weight'] > truck.capacity_weight_kg or
                    truck_loads[truck.truck_id]['volume'] > truck.capacity_volume_m3):
                return False

        return True

    def calculate_total_metrics(self, assignments: List[Dict]) -> Dict[str, float]:
        """
        Calculate total cost and CO₂ for assignments

        Args:
            assignments: List of assignments

        Returns:
            Dictionary with 'cost' and 'co2' keys
        """
        total_cost = sum(a.get('cost', 0) for a in assignments)
        total_co2 = sum(a.get('co2', 0) for a in assignments)

        return {
            'cost': total_cost,
            'co2': total_co2
        }

    def count_trucks_used(self, assignments: List[Dict]) -> int:
        """Count number of unique trucks used"""
        truck_ids = set(a['truck'].truck_id for a in assignments)
        return len(truck_ids)
