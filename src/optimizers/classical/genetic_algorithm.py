"""Genetic Algorithm optimizer for transport optimization"""

from optimizers.base_optimizer import BaseOptimizer, OptimizationResult
from models.lane import Lane
from models.truck import Truck
from models.shipment import Shipment
import time
import random
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from copy import deepcopy

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class GeneticAlgorithm(BaseOptimizer):
    """
    Genetic Algorithm optimizer for transport optimization

    Strategy:
    1. Initialize population of random solutions
    2. Evaluate fitness of each solution
    3. Select parents based on fitness
    4. Create offspring through crossover and mutation
    5. Replace population with best solutions
    6. Repeat until convergence or max generations

    This is a global search method suitable for medium-sized problems.
    """

    def __init__(self,
                 shipments: List[Shipment],
                 trucks: List[Truck],
                 lanes: List[Lane],
                 population_size: int = 50,
                 generations: int = 100,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 elitism_rate: float = 0.1):
        """
        Initialize Genetic Algorithm optimizer

        Args:
            shipments: List of shipments
            trucks: List of trucks
            lanes: List of lanes
            population_size: Number of solutions in population (Pi: 50-100)
            generations: Number of generations to evolve (Pi: 100-200)
            mutation_rate: Probability of mutation (0-1)
            crossover_rate: Probability of crossover (0-1)
            elitism_rate: Fraction of best solutions to preserve (0-1)
        """
        super().__init__(shipments, trucks, lanes)
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_count = max(1, int(population_size * elitism_rate))

    def optimize(self, objective: str = 'balanced', **kwargs) -> OptimizationResult:
        """
        Run genetic algorithm optimization

        Args:
            objective: Optimization objective ('cost', 'co2', or 'balanced')
            **kwargs: Additional parameters

        Returns:
            OptimizationResult with best solution found
        """
        start_time = time.time()

        print(
            f"Genetic Algorithm: Initializing population of {self.population_size}...")

        # Initialize population
        population = self._initialize_population()

        # Track best solution
        best_solution = None
        best_fitness = float('inf')
        fitness_history = []

        # Evolution loop
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = [
                self._evaluate_fitness(individual, objective)
                for individual in population
            ]

            # Track best solution
            min_fitness_idx = fitness_scores.index(min(fitness_scores))
            if fitness_scores[min_fitness_idx] < best_fitness:
                best_fitness = fitness_scores[min_fitness_idx]
                best_solution = deepcopy(population[min_fitness_idx])

            fitness_history.append(best_fitness)

            # Progress update
            if (generation + 1) % 10 == 0:
                print(f"  Generation {generation + 1}/{self.generations}: "
                      f"Best fitness = {best_fitness:.2f}")

            # Create next generation
            new_population = []

            # Elitism: Keep best solutions
            elite_indices = sorted(range(len(fitness_scores)),
                                   key=lambda i: fitness_scores[i])[:self.elitism_count]
            for idx in elite_indices:
                new_population.append(deepcopy(population[idx]))

            # Generate offspring
            while len(new_population) < self.population_size:
                # Select parents
                parent1 = self._tournament_selection(
                    population, fitness_scores)
                parent2 = self._tournament_selection(
                    population, fitness_scores)

                # Crossover
                if random.random() < self.crossover_rate:
                    offspring1, offspring2 = self._crossover(parent1, parent2)
                else:
                    offspring1, offspring2 = deepcopy(
                        parent1), deepcopy(parent2)

                # Mutation
                if random.random() < self.mutation_rate:
                    offspring1 = self._mutate(offspring1)
                if random.random() < self.mutation_rate:
                    offspring2 = self._mutate(offspring2)

                new_population.append(offspring1)
                if len(new_population) < self.population_size:
                    new_population.append(offspring2)

            population = new_population

        computation_time = time.time() - start_time

        print(f"Genetic Algorithm: Completed {self.generations} generations")
        print(f"Best fitness: {best_fitness:.2f}")

        if best_solution is None or not best_solution:
            # No feasible solution found
            return OptimizationResult(
                algorithm=f"Genetic Algorithm ({objective})",
                assignments=[],
                total_cost=0.0,
                total_co2=0.0,
                computation_time=computation_time,
                trucks_used=0,
                shipments_assigned=0,
                shipments_unassigned=len(self.shipments),
                metadata={
                    'objective': objective,
                    'generations': self.generations,
                    'population_size': self.population_size,
                    'status': 'no_feasible_solution'
                }
            )

        # Calculate metrics for best solution
        metrics = self.calculate_total_metrics(best_solution)
        trucks_used = self.count_trucks_used(best_solution)

        assigned_ids = set(a['shipment'].shipment_id for a in best_solution)
        unassigned_count = len(self.shipments) - len(assigned_ids)

        # Calculate improvement
        initial_fitness = fitness_history[0] if fitness_history else 0
        improvement_pct = ((initial_fitness - best_fitness) / initial_fitness * 100) \
            if initial_fitness > 0 else 0

        return OptimizationResult(
            algorithm=f"Genetic Algorithm ({objective})",
            assignments=best_solution,
            total_cost=metrics['cost'],
            total_co2=metrics['co2'],
            computation_time=computation_time,
            trucks_used=trucks_used,
            shipments_assigned=len(best_solution),
            shipments_unassigned=unassigned_count,
            metadata={
                'objective': objective,
                'generations': self.generations,
                'population_size': self.population_size,
                'mutation_rate': self.mutation_rate,
                'crossover_rate': self.crossover_rate,
                'best_fitness': best_fitness,
                'initial_fitness': initial_fitness,
                'improvement_pct': improvement_pct,
                'fitness_history': fitness_history[::10]  # Sample every 10th
            }
        )

    def _initialize_population(self) -> List[List[Dict]]:
        """
        Create initial population of random solutions

        Returns:
            List of solutions (each solution is a list of assignments)
        """
        population = []

        for _ in range(self.population_size):
            solution = self._create_random_solution()
            population.append(solution)

        return population

    def _create_random_solution(self) -> List[Dict]:
        """
        Create a random feasible solution

        Returns:
            List of assignments
        """
        assignments = []
        available_trucks = [t for t in self.trucks if t.available]

        # Shuffle shipments for randomness
        shuffled_shipments = self.shipments.copy()
        random.shuffle(shuffled_shipments)

        # Track truck loads
        truck_loads = {
            truck.truck_id: {'weight': 0.0, 'volume': 0.0}
            for truck in available_trucks
        }

        for shipment in shuffled_shipments:
            # Find matching lanes
            matching_lanes = self.find_matching_lanes(
                shipment.origin,
                shipment.destination
            )

            if not matching_lanes:
                continue

            # Try to assign to a random truck
            random.shuffle(available_trucks)

            for truck in available_trucks:
                # Check capacity
                new_weight = truck_loads[truck.truck_id]['weight'] + \
                    shipment.weight_kg
                new_volume = truck_loads[truck.truck_id]['volume'] + \
                    shipment.volume_m3

                if (new_weight <= truck.capacity_weight_kg and
                        new_volume <= truck.capacity_volume_m3):

                    # Select random lane
                    lane = random.choice(matching_lanes)

                    cost = self.calculate_assignment_cost(
                        shipment, truck, lane)
                    co2 = self.calculate_assignment_co2(shipment, truck, lane)

                    assignments.append({
                        'shipment': shipment,
                        'truck': truck,
                        'lane': lane,
                        'cost': cost,
                        'co2': co2
                    })

                    # Update loads
                    truck_loads[truck.truck_id]['weight'] = new_weight
                    truck_loads[truck.truck_id]['volume'] = new_volume
                    break

        return assignments

    def _evaluate_fitness(self, solution: List[Dict], objective: str) -> float:
        """
        Evaluate fitness of a solution (lower is better)

        Args:
            solution: List of assignments
            objective: Optimization objective

        Returns:
            Fitness score (lower is better)
        """
        if not solution:
            return float('inf')

        total_cost = sum(a['cost'] for a in solution)
        total_co2 = sum(a['co2'] for a in solution)

        # Penalty for unassigned shipments
        assigned_ids = set(a['shipment'].shipment_id for a in solution)
        unassigned_penalty = (len(self.shipments) - len(assigned_ids)) * 10000

        if objective == 'cost':
            return total_cost + unassigned_penalty
        elif objective == 'co2':
            return total_co2 + unassigned_penalty
        elif objective == 'balanced':
            return total_cost + 0.1 * total_co2 + unassigned_penalty
        else:
            raise ValueError(f"Unknown objective: {objective}")

    def _tournament_selection(self,
                              population: List[List[Dict]],
                              fitness_scores: List[float],
                              tournament_size: int = 3) -> List[Dict]:
        """
        Select parent using tournament selection

        Args:
            population: Current population
            fitness_scores: Fitness scores for population
            tournament_size: Number of individuals in tournament

        Returns:
            Selected parent solution
        """
        tournament_indices = random.sample(
            range(len(population)), tournament_size)
        best_idx = min(tournament_indices, key=lambda i: fitness_scores[i])
        return population[best_idx]

    def _crossover(self,
                   parent1: List[Dict],
                   parent2: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Perform crossover between two parents

        Args:
            parent1: First parent solution
            parent2: Second parent solution

        Returns:
            Two offspring solutions
        """
        if not parent1 or not parent2:
            return deepcopy(parent1), deepcopy(parent2)

        # Single-point crossover on shipment assignments
        shipment_ids_1 = [a['shipment'].shipment_id for a in parent1]
        shipment_ids_2 = [a['shipment'].shipment_id for a in parent2]

        # Find common shipments
        common_ids = set(shipment_ids_1) & set(shipment_ids_2)

        if not common_ids:
            return deepcopy(parent1), deepcopy(parent2)

        # Random crossover point
        crossover_point = random.randint(1, len(common_ids) - 1)
        common_list = list(common_ids)

        # Create offspring
        offspring1 = []
        offspring2 = []

        for i, shipment_id in enumerate(common_list):
            if i < crossover_point:
                # Take from parent1 for offspring1, parent2 for offspring2
                for a in parent1:
                    if a['shipment'].shipment_id == shipment_id:
                        offspring1.append(deepcopy(a))
                        break
                for a in parent2:
                    if a['shipment'].shipment_id == shipment_id:
                        offspring2.append(deepcopy(a))
                        break
            else:
                # Swap
                for a in parent2:
                    if a['shipment'].shipment_id == shipment_id:
                        offspring1.append(deepcopy(a))
                        break
                for a in parent1:
                    if a['shipment'].shipment_id == shipment_id:
                        offspring2.append(deepcopy(a))
                        break

        return offspring1, offspring2

    def _mutate(self, solution: List[Dict]) -> List[Dict]:
        """
        Mutate a solution

        Args:
            solution: Solution to mutate

        Returns:
            Mutated solution
        """
        if not solution:
            return solution

        mutated = deepcopy(solution)

        # Choose mutation type
        mutation_type = random.choice(['change_truck', 'change_lane', 'swap'])

        if mutation_type == 'change_truck' and len(mutated) > 0:
            # Change truck for random assignment
            idx = random.randint(0, len(mutated) - 1)
            available_trucks = [t for t in self.trucks if t.available]

            if available_trucks:
                new_truck = random.choice(available_trucks)
                mutated[idx]['truck'] = new_truck
                mutated[idx]['cost'] = self.calculate_assignment_cost(
                    mutated[idx]['shipment'],
                    new_truck,
                    mutated[idx]['lane']
                )
                mutated[idx]['co2'] = self.calculate_assignment_co2(
                    mutated[idx]['shipment'],
                    new_truck,
                    mutated[idx]['lane']
                )

        elif mutation_type == 'change_lane' and len(mutated) > 0:
            # Change lane for random assignment
            idx = random.randint(0, len(mutated) - 1)
            assignment = mutated[idx]

            alternative_lanes = [
                lane for lane in self.lanes
                if lane.matches_route(
                    assignment['shipment'].origin,
                    assignment['shipment'].destination
                ) and lane.lane_id != assignment['lane'].lane_id
            ]

            if alternative_lanes:
                new_lane = random.choice(alternative_lanes)
                mutated[idx]['lane'] = new_lane
                mutated[idx]['cost'] = self.calculate_assignment_cost(
                    assignment['shipment'],
                    assignment['truck'],
                    new_lane
                )
                mutated[idx]['co2'] = self.calculate_assignment_co2(
                    assignment['shipment'],
                    assignment['truck'],
                    new_lane
                )

        elif mutation_type == 'swap' and len(mutated) >= 2:
            # Swap trucks between two assignments
            idx1, idx2 = random.sample(range(len(mutated)), 2)
            mutated[idx1]['truck'], mutated[idx2]['truck'] = \
                mutated[idx2]['truck'], mutated[idx1]['truck']

            # Recalculate costs
            for idx in [idx1, idx2]:
                mutated[idx]['cost'] = self.calculate_assignment_cost(
                    mutated[idx]['shipment'],
                    mutated[idx]['truck'],
                    mutated[idx]['lane']
                )
                mutated[idx]['co2'] = self.calculate_assignment_co2(
                    mutated[idx]['shipment'],
                    mutated[idx]['truck'],
                    mutated[idx]['lane']
                )

        return mutated
