"""QUBO formulation for transport optimization problem"""

from models.lane import Lane
from models.truck import Truck
from models.shipment import Shipment
import numpy as np
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import QuadraticProgramToQubo

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class QUBOFormulation:
    """
    QUBO formulation for vehicle routing problem

    Decision variables:
    - x[i,j]: Binary variable (1 if shipment i assigned to truck j)

    Objective:
    - Minimize: α*Cost + β*CO₂ + penalties for constraint violations
    """

    def __init__(self,
                 shipments: List[Shipment],
                 trucks: List[Truck],
                 lanes: List[Lane],
                 weights: Dict[str, float] = None):
        """
        Initialize QUBO formulation

        Args:
            shipments: List of shipments
            trucks: List of trucks
            lanes: List of lanes
            weights: Dictionary of weights for objective and penalties
        """
        self.shipments = shipments
        self.trucks = trucks
        self.lanes = lanes

        # Default weights - balanced for QAOA
        # Typical assignment cost is ~700-1000, so penalties should be comparable
        self.weights = weights or {
            'cost': 1.0,           # Cost weight
            'co2': 0.01,           # CO₂ weight (scaled down)
            # Assignment constraint penalty (must be high)
            'assignment': 2000.0,
            # Capacity constraint penalty (hard constraint)
            'capacity': 5000.0,
            'deadline': 1000.0,    # Deadline constraint penalty
            # Availability constraint penalty (hard constraint)
            'available': 10000.0
        }

        # Build lane lookup for efficient access
        self._build_lane_lookup()

    def _build_lane_lookup(self):
        """Build lookup dictionary for lanes by route"""
        self.lane_lookup = {}
        for lane in self.lanes:
            key = (lane.origin.lower(), lane.destination.lower())
            if key not in self.lane_lookup:
                self.lane_lookup[key] = []
            self.lane_lookup[key].append(lane)

    def get_best_lane(self, origin: str, destination: str) -> Lane:
        """Get best (shortest) lane for a route"""
        key = (origin.lower(), destination.lower())
        lanes = self.lane_lookup.get(key, [])
        if not lanes:
            return None
        # Return lane with minimum effective distance
        return min(lanes, key=lambda l: l.effective_distance())

    def create_qubo(self) -> QuadraticProgram:
        """
        Create QUBO formulation of the problem

        Returns:
            QuadraticProgram object
        """
        qp = QuadraticProgram('transport_optimization')

        n_shipments = len(self.shipments)
        n_trucks = len(self.trucks)

        # Add binary variables for shipment-truck assignments
        # x[i,j] = 1 if shipment i is assigned to truck j
        for i in range(n_shipments):
            for j in range(n_trucks):
                qp.binary_var(f'x_{i}_{j}')

        # Build objective function
        linear = {}
        quadratic = {}

        # Add cost and CO₂ terms
        self._add_objective_terms(linear, quadratic)

        # Add constraint penalties
        self._add_assignment_penalty(linear, quadratic)
        self._add_capacity_penalty(linear, quadratic)
        self._add_deadline_penalty(linear, quadratic)
        self._add_availability_penalty(linear, quadratic)

        # Set objective to minimize
        qp.minimize(linear=linear, quadratic=quadratic)

        return qp

    def _add_objective_terms(self, linear: Dict, quadratic: Dict):
        """Add cost and CO₂ objective terms"""
        for i, shipment in enumerate(self.shipments):
            # Find best lane for this shipment's route
            lane = self.get_best_lane(shipment.origin, shipment.destination)

            if lane is None:
                # No lane available - add high penalty
                for j in range(len(self.trucks)):
                    var = f'x_{i}_{j}'
                    linear[var] = linear.get(var, 0) + 10000.0
                continue

            for j, truck in enumerate(self.trucks):
                var = f'x_{i}_{j}'

                # Calculate cost for this assignment
                cost = (self.weights['cost'] *
                        truck.cost_per_km_eur * lane.distance_km * lane.traffic_factor)

                # Calculate CO₂ for this assignment
                co2 = (self.weights['co2'] *
                       truck.co2_per_km_kg * lane.distance_km * lane.traffic_factor)

                # Add to linear terms
                linear[var] = linear.get(var, 0) + cost + co2

    def _add_assignment_penalty(self, linear: Dict, quadratic: Dict):
        """
        Add penalty for assignment constraint
        Each shipment must be assigned to exactly one truck
        Penalty: λ * Σ(i) (1 - Σ(j) x[i,j])²
        Expanded: λ * (1 - 2*Σx + Σx²+ 2*ΣΣx*x)
        """
        lambda_assign = self.weights['assignment']

        for i in range(len(self.shipments)):
            # Constant term λ is added to objective (not needed in variables)

            # Linear term: -2λ * Σ(j) x[i,j] + λ (from x² expansion)
            for j in range(len(self.trucks)):
                var = f'x_{i}_{j}'
                # -2λ from expansion, +λ from x²=x for binary
                linear[var] = linear.get(var, 0) - lambda_assign

            # Quadratic term: 2λ * Σ(j<k) x[i,j] * x[i,k]
            for j in range(len(self.trucks)):
                for k in range(j+1, len(self.trucks)):
                    var_j = f'x_{i}_{j}'
                    var_k = f'x_{i}_{k}'
                    key = (var_j, var_k)
                    quadratic[key] = quadratic.get(key, 0) + 2 * lambda_assign

    def _add_capacity_penalty(self, linear: Dict, quadratic: Dict):
        """
        Add penalty for capacity constraints
        Truck capacity must not be exceeded
        """
        lambda_cap = self.weights['capacity']

        for j, truck in enumerate(self.trucks):
            # Weight capacity penalty
            for i, shipment in enumerate(self.shipments):
                if shipment.weight_kg > truck.capacity_weight_kg:
                    # This assignment would violate capacity
                    var = f'x_{i}_{j}'
                    penalty = lambda_cap * \
                        (shipment.weight_kg / truck.capacity_weight_kg)
                    linear[var] = linear.get(var, 0) + penalty

            # Volume capacity penalty
            for i, shipment in enumerate(self.shipments):
                if shipment.volume_m3 > truck.capacity_volume_m3:
                    # This assignment would violate capacity
                    var = f'x_{i}_{j}'
                    penalty = lambda_cap * \
                        (shipment.volume_m3 / truck.capacity_volume_m3)
                    linear[var] = linear.get(var, 0) + penalty

    def _add_deadline_penalty(self, linear: Dict, quadratic: Dict):
        """
        Add penalty for deadline constraints
        Deliveries should meet deadlines
        """
        lambda_deadline = self.weights['deadline']

        for i, shipment in enumerate(self.shipments):
            lane = self.get_best_lane(shipment.origin, shipment.destination)

            if lane is None:
                continue

            # Check if deadline can be met
            if shipment.is_overdue():
                # Already overdue - high penalty
                for j in range(len(self.trucks)):
                    var = f'x_{i}_{j}'
                    linear[var] = linear.get(var, 0) + lambda_deadline * 10

    def _add_availability_penalty(self, linear: Dict, quadratic: Dict):
        """
        Add penalty for using unavailable trucks
        """
        lambda_avail = self.weights['available']

        for j, truck in enumerate(self.trucks):
            if not truck.available:
                # Add high penalty for using this truck
                for i in range(len(self.shipments)):
                    var = f'x_{i}_{j}'
                    linear[var] = linear.get(var, 0) + lambda_avail

    def decode_solution(self, result: Dict[str, int]) -> List[Dict]:
        """
        Decode QAOA result into truck assignments

        Args:
            result: Dictionary mapping variable names to binary values

        Returns:
            List of assignment dictionaries
        """
        assignments = []

        for i, shipment in enumerate(self.shipments):
            for j, truck in enumerate(self.trucks):
                var_name = f'x_{i}_{j}'

                if result.get(var_name, 0) == 1:
                    # This shipment is assigned to this truck
                    lane = self.get_best_lane(
                        shipment.origin, shipment.destination)

                    if lane:
                        cost = truck.cost_per_km_eur * lane.distance_km * lane.traffic_factor
                        co2 = truck.co2_per_km_kg * lane.distance_km * lane.traffic_factor

                        assignments.append({
                            'shipment': shipment,
                            'truck': truck,
                            'lane': lane,
                            'cost': cost,
                            'co2': co2
                        })

        return assignments

    def get_problem_size(self) -> Tuple[int, int]:
        """
        Get problem size

        Returns:
            Tuple of (number of variables, number of constraints)
        """
        n_vars = len(self.shipments) * len(self.trucks)
        n_constraints = len(self.shipments)  # Assignment constraints
        return n_vars, n_constraints
