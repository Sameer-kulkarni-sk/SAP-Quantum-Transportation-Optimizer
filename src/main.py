#!/usr/bin/env python3
"""
Quantum Transport Optimizer - Main Entry Point

Educational transport optimization comparing classical and quantum algorithms
"""

from optimizers.classical.local_search import LocalSearchOptimizer
from optimizers.classical.greedy_optimizer import GreedyOptimizer
from optimizers.classical.exact_solver import ExactSolver
from optimizers.classical.genetic_algorithm import GeneticAlgorithm
from comparison.benchmark import BenchmarkSuite
from data_loader.csv_loader import CSVLoader
import sys
import os
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


# Try to import quantum optimizer (requires qiskit + qiskit-aer)
try:
    from optimizers.quantum.qaoa_optimizer import QAOAOptimizer, QISKIT_AVAILABLE
    QUANTUM_AVAILABLE = QISKIT_AVAILABLE
except ImportError:
    QUANTUM_AVAILABLE = False
    print("Note: Quantum optimizer not available. Install: pip install qiskit qiskit-aer scipy")


def print_header():
    """Print application header"""
    print("\n" + "="*70)
    print(" " * 15 + "QUANTUM TRANSPORT OPTIMIZER")
    print(" " * 20 + "for RasQberry")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


def print_menu():
    """Print main menu"""
    print("\n" + "-"*70)
    print("MAIN MENU")
    print("-"*70)
    print("1. Load Data from CSV")
    print("2. Run Greedy Optimizer (Fast Baseline)")
    print("3. Run Simulated Annealing (Recommended)")
    print("4. Run Genetic Algorithm")
    print("5. Run Exact Solver (Small Problems Only)")
    if QUANTUM_AVAILABLE:
        print("6. Run QAOA (Educational)")
        print("7. Run Comprehensive Benchmark")
        print("8. Compare All Results")
    print("0. Exit")
    print("-"*70)


def load_data():
    """Load data from CSV files"""
    print("\nLoading data from CSV files...")
    data_dir = Path(__file__).parent.parent / "data" / "input"

    loader = CSVLoader(str(data_dir))
    data = loader.load_all()

    print(f"\n✓ Loaded {len(data['shipments'])} shipments")
    print(f"✓ Loaded {len(data['trucks'])} trucks")
    print(f"✓ Loaded {len(data['lanes'])} lanes")

    return data


def print_result(result):
    """Print optimization result"""
    print("\n" + "="*70)
    print(f"RESULTS: {result.algorithm}")
    print("="*70)
    print(f"Total Cost:           €{result.total_cost:,.2f}")
    print(f"Total CO₂:            {result.total_co2:,.2f} kg")
    print(f"Computation Time:     {result.computation_time:.3f} seconds")
    print(f"Trucks Used:          {result.trucks_used}")
    print(f"Shipments Assigned:   {result.shipments_assigned}")
    print(f"Shipments Unassigned: {result.shipments_unassigned}")

    if result.assignments:
        print(f"\nAssignments:")
        print(
            f"{'Shipment':<12} {'Truck':<10} {'Lane':<10} {'Cost (€)':<12} {'CO₂ (kg)':<10}")
        print("-"*70)
        for assignment in result.assignments[:10]:  # Show first 10
            print(f"{assignment['shipment'].shipment_id:<12} "
                  f"{assignment['truck'].truck_id:<10} "
                  f"{assignment['lane'].lane_id:<10} "
                  f"{assignment['cost']:<12.2f} "
                  f"{assignment['co2']:<10.2f}")

        if len(result.assignments) > 10:
            print(f"... and {len(result.assignments) - 10} more assignments")

    print("="*70)


def compare_results(results):
    """Compare multiple optimization results"""
    print("\n" + "="*70)
    print("ALGORITHM COMPARISON")
    print("="*70)

    # Header
    print(f"{'Algorithm':<30} {'Cost (€)':<15} {'CO₂ (kg)':<15} {'Time (s)':<12}")
    print("-"*70)

    # Results
    for result in results:
        print(f"{result.algorithm:<30} "
              f"{result.total_cost:<15,.2f} "
              f"{result.total_co2:<15,.2f} "
              f"{result.computation_time:<12.3f}")

    print("-"*70)

    # Find best solutions
    if len(results) > 1:
        best_cost = min(results, key=lambda r: r.total_cost)
        best_co2 = min(results, key=lambda r: r.total_co2)
        fastest = min(results, key=lambda r: r.computation_time)

        print(
            f"\n✓ Best Cost:    {best_cost.algorithm} (€{best_cost.total_cost:,.2f})")
        print(
            f"✓ Best CO₂:     {best_co2.algorithm} ({best_co2.total_co2:,.2f} kg)")
        print(
            f"✓ Fastest:      {fastest.algorithm} ({fastest.computation_time:.3f}s)")

        # Calculate improvements
        if len(results) >= 2:
            baseline = results[0]
            for result in results[1:]:
                cost_imp = (
                    (baseline.total_cost - result.total_cost) / baseline.total_cost * 100)
                co2_imp = ((baseline.total_co2 - result.total_co2) /
                           baseline.total_co2 * 100)

                print(f"\n{result.algorithm} vs {baseline.algorithm}:")
                print(f"  Cost Improvement: {cost_imp:+.2f}%")
                print(f"  CO₂ Improvement:  {co2_imp:+.2f}%")

    print("="*70)


def run_demo():
    """Run a comprehensive demo with all algorithms"""
    print_header()
    print("Running Comprehensive Demo with Benchmarking...")
    print("\n⚠️  Note: This demo includes educational quantum algorithms.")
    print("    Classical algorithms will outperform quantum on current hardware.\n")

    # Load data
    data = load_data()

    if not data['shipments'] or not data['trucks'] or not data['lanes']:
        print("\n❌ Error: No data loaded. Please check CSV files.")
        return

    # Run comprehensive benchmark
    benchmark = BenchmarkSuite(
        data['shipments'],
        data['trucks'],
        data['lanes']
    )

    results = benchmark.run_comprehensive_comparison(
        include_exact=True,
        include_quantum=QUANTUM_AVAILABLE,
        objective='balanced'
    )

    # Export results
    output_file = Path(__file__).parent.parent / "data" / \
        "output" / "benchmark_results.json"
    benchmark.export_results(str(output_file))

    print("\n✓ Demo completed successfully!")
    print(f"✓ Results exported to: {output_file}")


def interactive_mode():
    """Run interactive CLI mode"""
    print_header()

    data = None
    results = []

    while True:
        print_menu()
        choice = input("\nEnter your choice: ").strip()

        if choice == '0':
            print("\nThank you for using Quantum Transport Optimizer!")
            break

        elif choice == '1':
            data = load_data()

        elif choice == '2':
            if data is None:
                print("\n❌ Please load data first (option 1)")
                continue

            print("\nRunning Greedy Optimizer...")
            greedy = GreedyOptimizer(
                data['shipments'], data['trucks'], data['lanes'])
            result = greedy.optimize(objective='balanced')
            print_result(result)
            results.append(result)

        elif choice == '3':
            if data is None:
                print("\n❌ Please load data first (option 1)")
                continue

            print("\nRunning Simulated Annealing (Recommended)...")
            local_search = LocalSearchOptimizer(
                data['shipments'], data['trucks'], data['lanes'])
            result = local_search.optimize(
                max_iterations=2000, adaptive_cooling=True)
            print_result(result)
            results.append(result)

        elif choice == '4':
            if data is None:
                print("\n❌ Please load data first (option 1)")
                continue

            print("\nRunning Genetic Algorithm...")
            ga = GeneticAlgorithm(
                data['shipments'], data['trucks'], data['lanes'],
                population_size=50, generations=100)
            result = ga.optimize(objective='balanced')
            print_result(result)
            results.append(result)

        elif choice == '5':
            if data is None:
                print("\n❌ Please load data first (option 1)")
                continue

            # Check if problem is small enough
            n_vars = len(data['shipments']) * len(data['trucks'])
            if n_vars > 12:
                print(
                    f"\n❌ Problem too large for exact solver ({n_vars} variables > 12)")
                print("   Use Simulated Annealing or Genetic Algorithm instead")
                continue

            print(f"\nRunning Exact Solver (finding optimal solution)...")
            print(f"Problem size: {n_vars} variables")
            exact = ExactSolver(data['shipments'],
                                data['trucks'], data['lanes'])
            result = exact.optimize(objective='balanced')
            print_result(result)
            results.append(result)

        elif choice == '6' and QUANTUM_AVAILABLE:
            if data is None:
                print("\n❌ Please load data first (option 1)")
                continue

            print("\n⚠️  Running QAOA (Educational - Not for Production)")
            print("   Classical algorithms will perform better on current hardware\n")
            try:
                qaoa = QAOAOptimizer(
                    data['shipments'],
                    data['trucks'],
                    data['lanes'],
                    qaoa_reps=2,
                    max_iter=50
                )
                result = qaoa.optimize_with_fallback()
                print_result(result)
                results.append(result)
            except Exception as e:
                print(f"\n❌ Error: {e}")

        elif choice == '7' and QUANTUM_AVAILABLE:
            if data is None:
                print("\n❌ Please load data first (option 1)")
                continue

            print("\nRunning Comprehensive Benchmark...")
            benchmark = BenchmarkSuite(
                data['shipments'], data['trucks'], data['lanes'])
            benchmark.run_comprehensive_comparison(
                include_exact=True,
                include_quantum=True,
                objective='balanced'
            )

        elif choice == '8' and QUANTUM_AVAILABLE:
            if len(results) < 2:
                print("\n❌ Please run at least 2 algorithms first")
                continue

            compare_results(results)

        else:
            print("\n❌ Invalid choice. Please try again.")

        input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        # Run demo mode
        run_demo()
    else:
        # Run interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
