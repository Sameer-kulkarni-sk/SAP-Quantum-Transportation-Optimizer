"""Comprehensive benchmarking suite for optimizer comparison"""

from optimizers.classical.greedy_optimizer import GreedyOptimizer
from optimizers.classical.local_search import LocalSearchOptimizer
from optimizers.classical.exact_solver import ExactSolver
from optimizers.classical.genetic_algorithm import GeneticAlgorithm


# Try to import quantum optimizers (requires qiskit + qiskit-aer)
try:
    from optimizers.quantum.qaoa_optimizer import QAOAOptimizer, QISKIT_AVAILABLE
    from optimizers.quantum.hybrid_qaoa_optimizer import HybridQAOAOptimizer
    QUANTUM_AVAILABLE = QISKIT_AVAILABLE
except ImportError:
    QUANTUM_AVAILABLE = False
from models.shipment import Shipment
from models.truck import Truck
from models.lane import Lane
import time
import sys
from pathlib import Path
from typing import List, Dict
import json

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class BenchmarkSuite:
    """
    Comprehensive benchmarking suite for comparing optimization algorithms

    Provides fair comparison by:
    1. Running all algorithms on the same problem instance
    2. Comparing against optimal solution (when available)
    3. Tracking multiple metrics (cost, CO2, time, quality)
    4. Generating detailed comparison reports
    """

    def __init__(self,
                 shipments: List[Shipment],
                 trucks: List[Truck],
                 lanes: List[Lane]):
        """
        Initialize benchmark suite

        Args:
            shipments: List of shipments
            trucks: List of trucks
            lanes: List of lanes
        """
        self.shipments = shipments
        self.trucks = trucks
        self.lanes = lanes
        self.results = {}

    def run_comprehensive_comparison(self,
                                     include_exact: bool = True,
                                     include_quantum: bool = True,
                                     objective: str = 'balanced') -> Dict:
        """
        Run all optimizers and compare results

        Args:
            include_exact: Whether to run exact solver (only for small problems)
            include_quantum: Whether to run QAOA
            objective: Optimization objective

        Returns:
            Dictionary with all results and comparisons
        """
        print("\n" + "="*70)
        print("COMPREHENSIVE OPTIMIZER BENCHMARK")
        print("="*70)
        print(f"Problem Size: {len(self.shipments)} shipments, "
              f"{len(self.trucks)} trucks, {len(self.lanes)} lanes")
        print(f"Objective: {objective}")
        print("="*70 + "\n")

        # Check if exact solver can be used
        n_vars = len(self.shipments) * len(self.trucks)
        can_solve_exactly = n_vars <= 12

        if include_exact and not can_solve_exactly:
            print(
                f"⚠️  Problem too large for exact solver ({n_vars} variables > 12)")
            print("    Exact solver will be skipped\n")
            include_exact = False

        # Run optimizers
        self.results = {}

        # 1. Exact Solver (if applicable)
        if include_exact and can_solve_exactly:
            print("🎯 Running Exact Solver (optimal solution)...")
            try:
                exact = ExactSolver(self.shipments, self.trucks, self.lanes)
                self.results['exact'] = exact.optimize(objective=objective)
                print(
                    f"   ✓ Completed in {self.results['exact'].computation_time:.2f}s\n")
            except Exception as e:
                print(f"   ✗ Error: {e}\n")

        # 2. Greedy Optimizer
        print("⚡ Running Greedy Optimizer (fast baseline)...")
        try:
            greedy = GreedyOptimizer(self.shipments, self.trucks, self.lanes)
            self.results['greedy'] = greedy.optimize(objective=objective)
            print(
                f"   ✓ Completed in {self.results['greedy'].computation_time:.2f}s\n")
        except Exception as e:
            print(f"   ✗ Error: {e}\n")

        # 3. Simulated Annealing
        print("🔥 Running Simulated Annealing (global search)...")
        try:
            sa = LocalSearchOptimizer(self.shipments, self.trucks, self.lanes)
            self.results['simulated_annealing'] = sa.optimize(
                max_iterations=2000,
                adaptive_cooling=True
            )
            print(
                f"   ✓ Completed in {self.results['simulated_annealing'].computation_time:.2f}s\n")
        except Exception as e:
            print(f"   ✗ Error: {e}\n")

        # 4. Genetic Algorithm
        print("🧬 Running Genetic Algorithm (evolutionary search)...")
        try:
            ga = GeneticAlgorithm(
                self.shipments, self.trucks, self.lanes,
                population_size=50,
                generations=100
            )
            self.results['genetic'] = ga.optimize(objective=objective)
            print(
                f"   ✓ Completed in {self.results['genetic'].computation_time:.2f}s\n")
        except Exception as e:
            print(f"   ✗ Error: {e}\n")

        # 5. Hybrid QAOA (if requested) - Solves ALL shipments, comparable to classical
        if include_quantum:
            print("⚛️  Running Hybrid QAOA (quantum-classical hybrid)...")
            print("   ✓ Can solve ALL shipments using divide-and-conquer approach")
            print(
                f"   Processing {len(self.shipments)} shipments in quantum-optimized chunks\n")

            try:
                hybrid_qaoa = HybridQAOAOptimizer(
                    self.shipments, self.trucks, self.lanes,
                    chunk_size=10,
                    qaoa_reps=2,
                    max_iter=50
                )
                self.results['hybrid_qaoa'] = hybrid_qaoa.optimize()
                print(
                    f"   ✓ Completed in {self.results['hybrid_qaoa'].computation_time:.2f}s")
                quantum_pct = self.results['hybrid_qaoa'].metadata.get(
                    'quantum_percentage', 0)
                print(
                    f"   ✓ Quantum optimization: {quantum_pct:.0f}% of chunks")
                print(
                    f"   ✓ Solved {self.results['hybrid_qaoa'].shipments_assigned}/{len(self.shipments)} shipments\n")
            except Exception as e:
                print(f"   ✗ Error: {e}\n")

            # Pure QAOA runs on a reduced subset due to qubit limits.
            # Results are stored separately and NOT mixed into the main
            # comparison table — comparing a 3-shipment result against
            # full-problem classical results would be misleading.
            print("⚛️  Running Pure QAOA (educational - reduced subset only)...")
            print(
                "   ⚠️  Pure QAOA is limited by qubit count; runs on a small subset.")

            qaoa_shipments = self.shipments[:3]
            qaoa_trucks = self.trucks[:2]

            print(
                f"   Using subset: {len(qaoa_shipments)} shipments × "
                f"{len(qaoa_trucks)} trucks "
                f"({len(qaoa_shipments)*len(qaoa_trucks)} qubits)")

            try:
                qaoa = QAOAOptimizer(
                    qaoa_shipments, qaoa_trucks, self.lanes,
                    qaoa_reps=2,
                    max_iter=50
                )
                # Store under a key that the comparison report will skip
                # for the main table but will print in a separate section.
                self.results['qaoa_subset'] = qaoa.optimize()
                self.results['qaoa_subset'].metadata['subset_shipments'] = len(qaoa_shipments)
                self.results['qaoa_subset'].metadata['total_shipments'] = len(self.shipments)
                print(
                    f"   ✓ Completed in {self.results['qaoa_subset'].computation_time:.2f}s\n")
            except Exception as e:
                print(f"   ✗ Error: {e}\n")

        # Generate comparison report
        return self._generate_comparison_report(include_exact and can_solve_exactly)

    def _generate_comparison_report(self, has_optimal: bool) -> Dict:
        """
        Generate detailed comparison report

        Args:
            has_optimal: Whether optimal solution is available

        Returns:
            Dictionary with comparison metrics
        """
        print("\n" + "="*70)
        print("BENCHMARK RESULTS")
        print("="*70)

        # Determine optimal/best cost
        if has_optimal and 'exact' in self.results:
            optimal_cost = self.results['exact'].total_cost
            optimal_co2 = self.results['exact'].total_co2
            print(f"\n🎯 OPTIMAL SOLUTION (Exact Solver):")
            print(f"   Cost: €{optimal_cost:.2f}")
            print(f"   CO₂: {optimal_co2:.2f} kg")
        else:
            # Find best classical solution
            classical_algos = ['greedy', 'simulated_annealing', 'genetic']
            best_cost = min(
                self.results[algo].total_cost
                for algo in classical_algos
                if algo in self.results and self.results[algo].total_cost > 0
            )
            optimal_cost = best_cost
            print(f"\n⭐ BEST CLASSICAL SOLUTION:")
            print(f"   Cost: €{optimal_cost:.2f}")
            print("   (No optimal baseline available for this problem size)")

        # Print comparison table
        print("\n" + "-"*70)
        print(
            f"{'Algorithm':<25} {'Cost (€)':<12} {'CO₂ (kg)':<12} {'Time (s)':<10} {'Gap':<10}")
        print("-"*70)

        comparison_data = {}

        # qaoa_subset ran on a different (smaller) problem — exclude from the
        # main table so numbers stay comparable, then print it separately below.
        subset_result = self.results.get('qaoa_subset')
        main_results = {k: v for k, v in self.results.items() if k != 'qaoa_subset'}

        for algo_name, result in main_results.items():
            if result.total_cost == 0:
                continue

            gap = ((result.total_cost - optimal_cost) / optimal_cost * 100) \
                if optimal_cost > 0 else 0

            gap_str = f"{gap:+.2f}%" if has_optimal else "N/A"

            print(f"{result.algorithm:<25} "
                  f"{result.total_cost:<12.2f} "
                  f"{result.total_co2:<12.2f} "
                  f"{result.computation_time:<10.2f} "
                  f"{gap_str:<10}")

            comparison_data[algo_name] = {
                'algorithm': result.algorithm,
                'cost': result.total_cost,
                'co2': result.total_co2,
                'time': result.computation_time,
                'gap_percent': gap if has_optimal else None,
                'trucks_used': result.trucks_used,
                'shipments_assigned': result.shipments_assigned,
                'shipments_unassigned': result.shipments_unassigned
            }

        print("-"*70)

        # ── Pure QAOA subset result (separate section, not in main comparison) ──
        if subset_result:
            sub_n = subset_result.metadata.get('subset_shipments', '?')
            total_n = subset_result.metadata.get('total_shipments', '?')
            print(f"\n{'='*70}")
            print(f"PURE QAOA RESULT  (educational — subset only: "
                  f"{sub_n}/{total_n} shipments)")
            print(f"{'='*70}")
            print("⚠️  These numbers are NOT comparable to the table above.")
            print(f"   The problem solved here ({sub_n} shipments) is smaller than")
            print(f"   the full dataset ({total_n} shipments), so cost and CO₂ will")
            print("   appear lower simply because fewer shipments were assigned.\n")
            print(f"  Algorithm : {subset_result.algorithm}")
            print(f"  Cost      : €{subset_result.total_cost:,.2f}  "
                  f"(for {sub_n}/{total_n} shipments)")
            print(f"  CO₂       : {subset_result.total_co2:,.2f} kg")
            print(f"  Time      : {subset_result.computation_time:.2f}s")
            print(f"{'='*70}")

        # Key insights
        print("\n📊 KEY INSIGHTS:")

        if has_optimal:
            print("\n1. Solution Quality (vs Optimal):")
            for algo_name, data in comparison_data.items():
                if algo_name != 'exact' and data['gap_percent'] is not None:
                    quality = self._assess_quality(data['gap_percent'])
                    print(f"   • {data['algorithm']:<30} {quality}")

        print("\n2. Computational Efficiency:")
        sorted_by_time = sorted(
            comparison_data.items(),
            key=lambda x: x[1]['time']
        )
        for algo_name, data in sorted_by_time:
            speed = self._assess_speed(data['time'])
            print(f"   • {data['algorithm']:<30} {speed}")

        print("\n3. Recommended Usage:")
        print("   • Quick Estimates:        Greedy Optimizer")
        print("   • Production Use:         Simulated Annealing or Genetic Algorithm")
        print("   • Small Problems (<12):   Exact Solver (optimal)")
        print("   • Research/Education:     QAOA")

        print("\n4. Current State of Quantum Computing:")
        print("   ⚠️  Quantum advantage has NOT been achieved for optimization")
        print("   ⚠️  Classical algorithms will outperform quantum on current hardware")
        print("   ⚠️  QAOA is included for educational and research purposes")

        print("\n" + "="*70 + "\n")

        return {
            'problem_size': {
                'shipments': len(self.shipments),
                'trucks': len(self.trucks),
                'lanes': len(self.lanes),
                'variables': len(self.shipments) * len(self.trucks)
            },
            'has_optimal': has_optimal,
            'optimal_cost': optimal_cost if has_optimal else None,
            'results': comparison_data,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def _assess_quality(self, gap_percent: float) -> str:
        """Assess solution quality based on optimality gap"""
        if gap_percent == 0:
            return "✓ Optimal"
        elif gap_percent < 1:
            return f"✓ Excellent ({gap_percent:+.2f}%)"
        elif gap_percent < 5:
            return f"✓ Very Good ({gap_percent:+.2f}%)"
        elif gap_percent < 10:
            return f"○ Good ({gap_percent:+.2f}%)"
        elif gap_percent < 20:
            return f"○ Acceptable ({gap_percent:+.2f}%)"
        else:
            return f"✗ Poor ({gap_percent:+.2f}%)"

    def _assess_speed(self, time_seconds: float) -> str:
        """Assess computational speed"""
        if time_seconds < 1:
            return f"⚡ Very Fast ({time_seconds:.2f}s)"
        elif time_seconds < 5:
            return f"✓ Fast ({time_seconds:.2f}s)"
        elif time_seconds < 30:
            return f"○ Moderate ({time_seconds:.2f}s)"
        elif time_seconds < 120:
            return f"○ Slow ({time_seconds:.2f}s)"
        else:
            return f"✗ Very Slow ({time_seconds:.2f}s)"

    def export_results(self, filename: str = 'benchmark_results.json'):
        """
        Export benchmark results to JSON file

        Args:
            filename: Output filename
        """
        export_data = {
            'problem_size': {
                'shipments': len(self.shipments),
                'trucks': len(self.trucks),
                'lanes': len(self.lanes)
            },
            'results': {}
        }

        for algo_name, result in self.results.items():
            export_data['results'][algo_name] = {
                'algorithm': result.algorithm,
                'comparable_to_full_problem': algo_name != 'qaoa_subset',
                'total_cost': result.total_cost,
                'total_co2': result.total_co2,
                'computation_time': result.computation_time,
                'trucks_used': result.trucks_used,
                'shipments_assigned': result.shipments_assigned,
                'shipments_unassigned': result.shipments_unassigned,
                'metadata': result.metadata
            }

        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"Results exported to {filename}")

    def run_scalability_test(self, max_shipments: int = 20):
        """
        Test how algorithms scale with problem size

        Args:
            max_shipments: Maximum number of shipments to test
        """
        print("\n" + "="*70)
        print("SCALABILITY TEST")
        print("="*70)

        for n in range(5, min(max_shipments + 1, len(self.shipments) + 1), 5):
            print(f"\nTesting with {n} shipments...")

            # Use subset of shipments
            subset_shipments = self.shipments[:n]

            # Run quick benchmark
            suite = BenchmarkSuite(subset_shipments, self.trucks, self.lanes)
            suite.run_comprehensive_comparison(
                include_exact=(n * len(self.trucks) <= 12),
                include_quantum=False
            )
