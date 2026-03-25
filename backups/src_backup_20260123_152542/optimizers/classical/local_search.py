"""Local search optimizer with simulated annealing"""

from optimizers.classical.greedy_optimizer import GreedyOptimizer
from optimizers.base_optimizer import BaseOptimizer, OptimizationResult
from models.lane import Lane
from models.truck import Truck
from models.shipment import Shipment
import time
import random
import math
import sys
from pathlib import Path
from typing import List, Dict, Optional
from copy import deepcopy

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class LocalSearchOptimizer(BaseOptimizer):
    """
    Local search optimizer with simulated annealing

    Strategy:
    1. Start with greedy solution
    2. Iteratively improve by swapping assignments
    3. Use simulated annealing to escape local optima
    """

    def optimize(self,
                 max_iterations: int = 1000,
                 initial_temperature: float = 1000.0,
                 cooling_rate: float = 0.995,
                 min_temperature: float = 0.1,
                 initial_solution: Optional[List[Dict]] = None,
                 **kwargs) -> OptimizationResult:
        """
        Run local search optimization

        Args:
            max_iterations: Maximum number of iterations
            initial_temperature: Starting temperature for simulated annealing
            cooling_rate: Temperature reduction factor per iteration
            min_temperature: Minimum temperature threshold
            initial_solution: Starting solution (uses greedy if None)
            **kwargs: Additional parameters

        Returns:
            OptimizationResult with assignments and metrics
        """
        start_time = time.time()

        # Get initial solution
        if initial_solution is None:
            greedy = GreedyOptimizer(self.shipments, self.trucks, self.lanes)
            greedy_result = greedy.optimize(objective='balanced')
            current_solution = greedy_result.assignments
        else:
            current_solution = initial_solution

        if not current_solution:
            # No feasible solution found
            return OptimizationResult(
                algorithm="Local Search",
                assignments=[],
                total_cost=0.0,
                total_co2=0.0,
                computation_time=time.time() - start_time,
                trucks_used=0,
                shipments_assigned=0,
                shipments_unassigned=len(self.shipments),
                metadata={'status': 'no_feasible_solution'}
            )

        current_cost = self._evaluate_solution(current_solution)
        best_solution = deepcopy(current_solution)
        best_cost = current_cost

        # Simulated annealing parameters
        temperature = initial_temperature
        iteration = 0
        improvements = 0

        # Track progress
        cost_history = [current_cost]

        # Main optimization loop
        while iteration < max_iterations and temperature > min_temperature:
            # Generate neighbor solution
            neighbor = self._generate_neighbor(current_solution)

            if neighbor is None:
                iteration += 1
                continue

            neighbor_cost = self._evaluate_solution(neighbor)

            # Acceptance criterion
            delta = neighbor_cost - current_cost

            if delta < 0:
                # Better solution - always accept
                current_solution = neighbor
                current_cost = neighbor_cost
                improvements += 1

                # Update best solution
                if current_cost < best_cost:
                    best_solution = deepcopy(current_solution)
                    best_cost = current_cost

            elif random.random() < math.exp(-delta / temperature):
                # Worse solution - accept with probability
                current_solution = neighbor
                current_cost = neighbor_cost

            # Cool down
            temperature *= cooling_rate
            iteration += 1

            # Track progress every 100 iterations
            if iteration % 100 == 0:
                cost_history.append(current_cost)

        # Calculate final metrics
        metrics = self.calculate_total_metrics(best_solution)
        trucks_used = self.count_trucks_used(best_solution)
        computation_time = time.time() - start_time

        assigned_shipment_ids = set(
            a['shipment'].shipment_id for a in best_solution)
        unassigned_count = len(self.shipments) - len(assigned_shipment_ids)

        return OptimizationResult(
            algorithm="Local Search (Simulated Annealing)",
            assignments=best_solution,
            total_cost=metrics['cost'],
            total_co2=metrics['co2'],
            computation_time=computation_time,
            trucks_used=trucks_used,
            shipments_assigned=len(best_solution),
            shipments_unassigned=unassigned_count,
            metadata={
                'iterations': iteration,
                'improvements': improvements,
                'final_temperature': temperature,
                'cost_history': cost_history,
                'initial_cost': cost_history[0] if cost_history else 0,
                'improvement_pct': ((cost_history[0] - best_cost) / cost_history[0] * 100)
                if cost_history and cost_history[0] > 0 else 0
            }
        )

    def _evaluate_solution(self, solution: List[Dict]) -> float:
        """
        Evaluate solution quality

        Args:
            solution: List of assignments

        Returns:
            Total cost (including penalties for constraint violations)
        """
        total_cost = 0.0
        total_co2 = 0.0
        penalty = 0.0

        # Track truck loads
        truck_loads = {truck.truck_id: {'weight': 0.0, 'volume': 0.0}
                       for truck in self.trucks}

        for assignment in solution:
            truck = assignment['truck']
            lane = assignment['lane']
            shipment = assignment['shipment']

            # Calculate costs
            cost = self.calculate_assignment_cost(shipment, truck, lane)
            co2 = self.calculate_assignment_co2(shipment, truck, lane)

            total_cost += cost
            total_co2 += co2

            # Track loads
            truck_loads[truck.truck_id]['weight'] += shipment.weight_kg
            truck_loads[truck.truck_id]['volume'] += shipment.volume_m3

        # Add penalties for constraint violations
        for truck in self.trucks:
            load = truck_loads[truck.truck_id]

            # Weight capacity violation
            if load['weight'] > truck.capacity_weight_kg:
                penalty += 1000 * (load['weight'] - truck.capacity_weight_kg)

            # Volume capacity violation
            if load['volume'] > truck.capacity_volume_m3:
                penalty += 1000 * (load['volume'] - truck.capacity_volume_m3)

        # Combined objective: cost + weighted CO₂ + penalties
        return total_cost + 0.1 * total_co2 + penalty

    def _generate_neighbor(self, solution: List[Dict]) -> Optional[List[Dict]]:
        """
        Generate neighbor solution by applying a random move

        Args:
            solution: Current solution

        Returns:
            Neighbor solution or None if no valid move found
        """
        if len(solution) < 2:
            return None

        neighbor = deepcopy(solution)

        # Choose random move type
        move_type = random.choice(['swap_trucks', 'swap_lanes', 'reassign'])

        try:
            if move_type == 'swap_trucks':
                # Swap two shipments between trucks
                idx1, idx2 = random.sample(range(len(neighbor)), 2)
                neighbor[idx1]['truck'], neighbor[idx2]['truck'] = \
                    neighbor[idx2]['truck'], neighbor[idx1]['truck']

            elif move_type == 'swap_lanes':
                # Try different lane for same route
                idx = random.randint(0, len(neighbor) - 1)
                assignment = neighbor[idx]

                alternative_lanes = [
                    lane for lane in self.lanes
                    if (lane.matches_route(
                        assignment['shipment'].origin,
                        assignment['shipment'].destination
                    ) and lane.lane_id != assignment['lane'].lane_id)
                ]

                if alternative_lanes:
                    new_lane = random.choice(alternative_lanes)
                    neighbor[idx]['lane'] = new_lane
                    neighbor[idx]['cost'] = self.calculate_assignment_cost(
                        assignment['shipment'],
                        assignment['truck'],
                        new_lane
                    )
                    neighbor[idx]['co2'] = self.calculate_assignment_co2(
                        assignment['shipment'],
                        assignment['truck'],
                        new_lane
                    )

            elif move_type == 'reassign':
                # Reassign one shipment to different truck
                idx = random.randint(0, len(neighbor) - 1)
                available_trucks = [t for t in self.trucks if t.available]

                if available_trucks:
                    new_truck = random.choice(available_trucks)
                    neighbor[idx]['truck'] = new_truck
                    neighbor[idx]['cost'] = self.calculate_assignment_cost(
                        neighbor[idx]['shipment'],
                        new_truck,
                        neighbor[idx]['lane']
                    )
                    neighbor[idx]['co2'] = self.calculate_assignment_co2(
                        neighbor[idx]['shipment'],
                        new_truck,
                        neighbor[idx]['lane']
                    )

            return neighbor

        except (IndexError, ValueError):
            return None
