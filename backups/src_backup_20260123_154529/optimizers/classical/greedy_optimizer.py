"""Greedy heuristic optimizer"""

from optimizers.base_optimizer import BaseOptimizer, OptimizationResult
from models.lane import Lane
from models.truck import Truck
from models.shipment import Shipment
import time
import sys
from pathlib import Path
from typing import List, Dict, Optional
from copy import deepcopy

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class GreedyOptimizer(BaseOptimizer):
    """
    Greedy heuristic optimizer

    Strategy:
    1. Sort shipments by urgency (priority + deadline)
    2. For each shipment, assign to the cheapest available truck
    3. Select the best lane for each route
    """

    def optimize(self, objective: str = 'cost', **kwargs) -> OptimizationResult:
        """
        Run greedy optimization

        Args:
            objective: Optimization objective ('cost', 'co2', or 'balanced')
            **kwargs: Additional parameters

        Returns:
            OptimizationResult with assignments and metrics
        """
        start_time = time.time()

        # Reset trucks
        self.reset_trucks()

        # Sort shipments by urgency
        sorted_shipments = sorted(
            self.shipments,
            key=lambda s: s.urgency_score(),
            reverse=True
        )

        assignments = []
        unassigned_shipments = []

        # Assign each shipment
        for shipment in sorted_shipments:
            assignment = self._find_best_assignment(shipment, objective)

            if assignment:
                assignments.append(assignment)
                # Update truck state
                assignment['truck'].add_load(
                    shipment.weight_kg,
                    shipment.volume_m3,
                    shipment.shipment_id
                )
            else:
                unassigned_shipments.append(shipment)

        # Calculate metrics
        metrics = self.calculate_total_metrics(assignments)
        trucks_used = self.count_trucks_used(assignments)

        computation_time = time.time() - start_time

        return OptimizationResult(
            algorithm=f"Greedy ({objective})",
            assignments=assignments,
            total_cost=metrics['cost'],
            total_co2=metrics['co2'],
            computation_time=computation_time,
            trucks_used=trucks_used,
            shipments_assigned=len(assignments),
            shipments_unassigned=len(unassigned_shipments),
            metadata={
                'objective': objective,
                'unassigned_shipments': [s.shipment_id for s in unassigned_shipments]
            }
        )

    def _find_best_assignment(self, shipment: Shipment,
                              objective: str) -> Optional[Dict]:
        """
        Find best truck-lane combination for a shipment

        Args:
            shipment: Shipment to assign
            objective: Optimization objective

        Returns:
            Assignment dictionary or None if no feasible assignment
        """
        # Find matching lanes
        matching_lanes = self.find_matching_lanes(
            shipment.origin,
            shipment.destination
        )

        if not matching_lanes:
            return None

        best_score = float('inf')
        best_assignment = None

        # Try each available truck
        for truck in self.get_available_trucks():
            # Check if truck can accommodate shipment
            if not truck.can_accommodate(shipment.weight_kg, shipment.volume_m3):
                continue

            # Find best lane for this truck
            for lane in matching_lanes:
                score = self._calculate_objective_score(
                    shipment, truck, lane, objective
                )

                if score < best_score:
                    best_score = score
                    cost = self.calculate_assignment_cost(
                        shipment, truck, lane)
                    co2 = self.calculate_assignment_co2(shipment, truck, lane)

                    best_assignment = {
                        'shipment': shipment,
                        'truck': truck,
                        'lane': lane,
                        'cost': cost,
                        'co2': co2,
                        'score': score
                    }

        return best_assignment

    def _calculate_objective_score(self, shipment: Shipment,
                                   truck: Truck,
                                   lane: Lane,
                                   objective: str) -> float:
        """
        Calculate objective score for an assignment

        Args:
            shipment: Shipment
            truck: Truck
            lane: Lane
            objective: Objective type

        Returns:
            Score (lower is better)
        """
        cost = self.calculate_assignment_cost(shipment, truck, lane)
        co2 = self.calculate_assignment_co2(shipment, truck, lane)

        if objective == 'cost':
            return cost
        elif objective == 'co2':
            return co2
        elif objective == 'balanced':
            # Weight CO₂ at 0.1 EUR/kg
            return cost + 0.1 * co2
        else:
            raise ValueError(f"Unknown objective: {objective}")

    def optimize_multi_objective(self,
                                 cost_weight: float = 0.7,
                                 co2_weight: float = 0.3) -> OptimizationResult:
        """
        Optimize with custom weights for cost and CO₂

        Args:
            cost_weight: Weight for cost objective (0-1)
            co2_weight: Weight for CO₂ objective (0-1)

        Returns:
            OptimizationResult
        """
        if abs(cost_weight + co2_weight - 1.0) > 0.001:
            raise ValueError("Weights must sum to 1.0")

        start_time = time.time()
        self.reset_trucks()

        sorted_shipments = sorted(
            self.shipments,
            key=lambda s: s.urgency_score(),
            reverse=True
        )

        assignments = []
        unassigned_shipments = []

        for shipment in sorted_shipments:
            best_score = float('inf')
            best_assignment = None

            matching_lanes = self.find_matching_lanes(
                shipment.origin,
                shipment.destination
            )

            if not matching_lanes:
                unassigned_shipments.append(shipment)
                continue

            for truck in self.get_available_trucks():
                if not truck.can_accommodate(shipment.weight_kg, shipment.volume_m3):
                    continue

                for lane in matching_lanes:
                    cost = self.calculate_assignment_cost(
                        shipment, truck, lane)
                    co2 = self.calculate_assignment_co2(shipment, truck, lane)

                    # Normalize and combine objectives
                    score = cost_weight * cost + co2_weight * co2 * 100  # Scale CO₂

                    if score < best_score:
                        best_score = score
                        best_assignment = {
                            'shipment': shipment,
                            'truck': truck,
                            'lane': lane,
                            'cost': cost,
                            'co2': co2,
                            'score': score
                        }

            if best_assignment:
                assignments.append(best_assignment)
                best_assignment['truck'].add_load(
                    shipment.weight_kg,
                    shipment.volume_m3,
                    shipment.shipment_id
                )
            else:
                unassigned_shipments.append(shipment)

        metrics = self.calculate_total_metrics(assignments)
        trucks_used = self.count_trucks_used(assignments)
        computation_time = time.time() - start_time

        return OptimizationResult(
            algorithm=f"Greedy (Multi-objective)",
            assignments=assignments,
            total_cost=metrics['cost'],
            total_co2=metrics['co2'],
            computation_time=computation_time,
            trucks_used=trucks_used,
            shipments_assigned=len(assignments),
            shipments_unassigned=len(unassigned_shipments),
            metadata={
                'cost_weight': cost_weight,
                'co2_weight': co2_weight,
                'unassigned_shipments': [s.shipment_id for s in unassigned_shipments]
            }
        )
