"""Exact solver for small transport optimization problems"""

from optimizers.base_optimizer import BaseOptimizer, OptimizationResult
from models.lane import Lane
from models.truck import Truck
from models.shipment import Shipment
import time
import sys
from pathlib import Path
from typing import List, Dict, Optional
from itertools import product
from copy import deepcopy

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class ExactSolver(BaseOptimizer):
    """
    Exact solver for transport optimization

    Uses exhaustive search to find the optimal solution.
    Only suitable for small problems (< 12-15 variables).

    Strategy:
    1. Enumerate all feasible assignments
    2. Evaluate each assignment
    3. Return the optimal solution

    Time Complexity: O(n^m) where n=trucks, m=shipments
    """

    def __init__(self,
                 shipments: List[Shipment],
                 trucks: List[Truck],
                 lanes: List[Lane],
                 max_variables: int = 12):
        """
        Initialize exact solver

        Args:
            shipments: List of shipments
            trucks: List of trucks
            lanes: List of lanes
            max_variables: Maximum problem size (shipments * trucks)
        """
        super().__init__(shipments, trucks, lanes)
        self.max_variables = max_variables

    def optimize(self, objective: str = 'cost', **kwargs) -> OptimizationResult:
        """
        Run exact optimization

        Args:
            objective: Optimization objective ('cost', 'co2', or 'balanced')
            **kwargs: Additional parameters

        Returns:
            OptimizationResult with optimal assignments and metrics
        """
        start_time = time.time()

        # Check problem size
        n_vars = len(self.shipments) * len(self.trucks)
        if n_vars > self.max_variables:
            raise ValueError(
                f"Problem too large for exact solver: {n_vars} variables "
                f"(max: {self.max_variables}). Use heuristic methods instead."
            )

        print(f"Exact Solver: Evaluating all feasible solutions...")
        print(
            f"Problem size: {len(self.shipments)} shipments × {len(self.trucks)} trucks")

        # Find all feasible assignments
        best_solution = None
        best_score = float('inf')
        solutions_evaluated = 0
        feasible_solutions = 0

        # Generate all possible assignments
        for assignment_combo in self._generate_all_assignments():
            solutions_evaluated += 1

            # Check feasibility
            if not self._is_feasible(assignment_combo):
                continue

            feasible_solutions += 1

            # Evaluate solution
            score = self._evaluate_solution(assignment_combo, objective)

            if score < best_score:
                best_score = score
                best_solution = assignment_combo

            # Progress update every 10000 solutions
            if solutions_evaluated % 10000 == 0:
                print(f"  Evaluated {solutions_evaluated} solutions, "
                      f"{feasible_solutions} feasible...")

        computation_time = time.time() - start_time

        print(f"Exact Solver: Evaluated {solutions_evaluated} total solutions")
        print(f"Found {feasible_solutions} feasible solutions")
        print(f"Optimal solution found in {computation_time:.2f}s")

        if best_solution is None:
            # No feasible solution found
            return OptimizationResult(
                algorithm=f"Exact Solver ({objective})",
                assignments=[],
                total_cost=0.0,
                total_co2=0.0,
                computation_time=computation_time,
                trucks_used=0,
                shipments_assigned=0,
                shipments_unassigned=len(self.shipments),
                metadata={
                    'objective': objective,
                    'solutions_evaluated': solutions_evaluated,
                    'feasible_solutions': feasible_solutions,
                    'status': 'no_feasible_solution'
                }
            )

        # Calculate metrics for best solution
        metrics = self.calculate_total_metrics(best_solution)
        trucks_used = self.count_trucks_used(best_solution)

        assigned_ids = set(a['shipment'].shipment_id for a in best_solution)
        unassigned_count = len(self.shipments) - len(assigned_ids)

        return OptimizationResult(
            algorithm=f"Exact Solver ({objective}) - OPTIMAL",
            assignments=best_solution,
            total_cost=metrics['cost'],
            total_co2=metrics['co2'],
            computation_time=computation_time,
            trucks_used=trucks_used,
            shipments_assigned=len(best_solution),
            shipments_unassigned=unassigned_count,
            metadata={
                'objective': objective,
                'solutions_evaluated': solutions_evaluated,
                'feasible_solutions': feasible_solutions,
                'optimal': True,
                'optimal_score': best_score
            }
        )

    def _generate_all_assignments(self):
        """
        Generate all possible shipment-truck-lane assignments

        Yields:
            List of assignment dictionaries
        """
        # For each shipment, try all truck-lane combinations
        shipment_options = []

        for shipment in self.shipments:
            options = []

            # Find matching lanes
            matching_lanes = self.find_matching_lanes(
                shipment.origin,
                shipment.destination
            )

            if not matching_lanes:
                # No lanes available - shipment cannot be assigned
                options.append(None)  # Represents unassigned
            else:
                # Try each truck-lane combination
                for truck in self.trucks:
                    for lane in matching_lanes:
                        options.append({
                            'shipment': shipment,
                            'truck': truck,
                            'lane': lane
                        })

                # Also allow unassigned option
                options.append(None)

            shipment_options.append(options)

        # Generate all combinations
        for combo in product(*shipment_options):
            # Filter out None (unassigned) entries
            assignment = [a for a in combo if a is not None]
            yield assignment

    def _is_feasible(self, assignments: List[Dict]) -> bool:
        """
        Check if an assignment is feasible

        Args:
            assignments: List of assignments

        Returns:
            True if feasible, False otherwise
        """
        if not assignments:
            return False

        # Track truck loads
        truck_loads = {
            truck.truck_id: {'weight': 0.0, 'volume': 0.0}
            for truck in self.trucks
        }

        for assignment in assignments:
            truck = assignment['truck']
            shipment = assignment['shipment']

            # Check if truck is available
            if not truck.available:
                return False

            # Update loads
            truck_loads[truck.truck_id]['weight'] += shipment.weight_kg
            truck_loads[truck.truck_id]['volume'] += shipment.volume_m3

            # Check capacity constraints
            if truck_loads[truck.truck_id]['weight'] > truck.capacity_weight_kg:
                return False
            if truck_loads[truck.truck_id]['volume'] > truck.capacity_volume_m3:
                return False

        return True

    def _evaluate_solution(self, assignments: List[Dict], objective: str) -> float:
        """
        Evaluate solution quality

        Args:
            assignments: List of assignments
            objective: Optimization objective

        Returns:
            Score (lower is better)
        """
        if not assignments:
            return float('inf')

        total_cost = 0.0
        total_co2 = 0.0

        for assignment in assignments:
            cost = self.calculate_assignment_cost(
                assignment['shipment'],
                assignment['truck'],
                assignment['lane']
            )
            co2 = self.calculate_assignment_co2(
                assignment['shipment'],
                assignment['truck'],
                assignment['lane']
            )

            total_cost += cost
            total_co2 += co2

        # Calculate objective score
        if objective == 'cost':
            return total_cost
        elif objective == 'co2':
            return total_co2
        elif objective == 'balanced':
            # Weight CO₂ at 0.1 EUR/kg
            return total_cost + 0.1 * total_co2
        else:
            raise ValueError(f"Unknown objective: {objective}")

    def can_solve(self) -> bool:
        """
        Check if problem is small enough for exact solver

        Returns:
            True if problem can be solved exactly
        """
        n_vars = len(self.shipments) * len(self.trucks)
        return n_vars <= self.max_variables

    def estimate_time(self) -> str:
        """
        Estimate computation time

        Returns:
            Human-readable time estimate
        """
        n_shipments = len(self.shipments)
        n_trucks = len(self.trucks)
        n_vars = n_shipments * n_trucks

        # Rough estimates based on exponential complexity
        if n_vars <= 8:
            return "< 1 second"
        elif n_vars <= 10:
            return "1-5 seconds"
        elif n_vars <= 12:
            return "5-30 seconds"
        elif n_vars <= 15:
            return "30 seconds - 5 minutes"
        else:
            return "> 5 minutes (not recommended)"
