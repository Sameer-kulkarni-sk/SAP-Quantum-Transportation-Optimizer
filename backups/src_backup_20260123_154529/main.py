#!/usr/bin/env python3
"""
Quantum Transport Optimizer - Main Entry Point

A QAOA/QUBO-based transport optimization application for RasQberry
"""

from optimizers.classical.local_search import LocalSearchOptimizer
from optimizers.classical.greedy_optimizer import GreedyOptimizer
from data_loader.csv_loader import CSVLoader
import sys
import os
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


# Try to import quantum optimizer
try:
    from optimizers.quantum.qaoa_optimizer import QAOAOptimizer
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False
    print("Note: Quantum optimizer not available. Install qiskit-optimization and qiskit-algorithms.")


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
    print("2. Run Greedy Optimizer")
    print("3. Run Local Search Optimizer")
    if QUANTUM_AVAILABLE:
        print("4. Run QAOA Quantum Optimizer")
        print("5. Compare All Algorithms")
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
    """Run a quick demo with all algorithms"""
    print_header()
    print("Running Quick Demo...")

    # Load data
    data = load_data()

    if not data['shipments'] or not data['trucks'] or not data['lanes']:
        print("\n❌ Error: No data loaded. Please check CSV files.")
        return

    results = []

    # Run Greedy
    print("\n" + "="*70)
    print("Running Greedy Optimizer...")
    print("="*70)
    greedy = GreedyOptimizer(data['shipments'], data['trucks'], data['lanes'])
    greedy_result = greedy.optimize(objective='balanced')
    print_result(greedy_result)
    results.append(greedy_result)

    # Run Local Search
    print("\n" + "="*70)
    print("Running Local Search Optimizer...")
    print("="*70)
    local_search = LocalSearchOptimizer(
        data['shipments'], data['trucks'], data['lanes'])
    ls_result = local_search.optimize(max_iterations=500)
    print_result(ls_result)
    results.append(ls_result)

    # Run QAOA if available
    if QUANTUM_AVAILABLE:
        print("\n" + "="*70)
        print("Running QAOA Quantum Optimizer...")
        print("="*70)
        try:
            qaoa = QAOAOptimizer(
                data['shipments'],
                data['trucks'],
                data['lanes'],
                qaoa_reps=2,  # Reduced for Raspberry Pi
                max_iter=50
            )
            qaoa_result = qaoa.optimize_with_fallback()
            print_result(qaoa_result)
            results.append(qaoa_result)
        except Exception as e:
            print(f"\n❌ QAOA Error: {e}")
            print("Continuing with classical results...")

    # Compare results
    if len(results) > 1:
        compare_results(results)

    print("\n✓ Demo completed successfully!")


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

            print("\nRunning Local Search Optimizer...")
            local_search = LocalSearchOptimizer(
                data['shipments'], data['trucks'], data['lanes'])
            result = local_search.optimize(max_iterations=500)
            print_result(result)
            results.append(result)

        elif choice == '4' and QUANTUM_AVAILABLE:
            if data is None:
                print("\n❌ Please load data first (option 1)")
                continue

            print("\nRunning QAOA Quantum Optimizer...")
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

        elif choice == '5' and QUANTUM_AVAILABLE:
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
