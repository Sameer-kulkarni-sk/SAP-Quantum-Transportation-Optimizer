"""QAOA optimizer for transport optimization"""

from optimizers.quantum.qubo_formulation import QUBOFormulation
from optimizers.base_optimizer import BaseOptimizer, OptimizationResult
from models.lane import Lane
from models.truck import Truck
from models.shipment import Shipment
import time
import sys
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np

try:
    from qiskit_optimization.algorithms import MinimumEigenOptimizer
    from qiskit_algorithms import QAOA
    from qiskit_algorithms.optimizers import COBYLA
    from qiskit.primitives import StatevectorSampler
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    print("Warning: Qiskit optimization packages not available. Install with: pip install qiskit-optimization qiskit-algorithms")

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class QAOAOptimizer(BaseOptimizer):
    """
    QAOA (Quantum Approximate Optimization Algorithm) optimizer

    Uses Qiskit to solve the transport optimization problem
    as a QUBO (Quadratic Unconstrained Binary Optimization) problem
    """

    def __init__(self,
                 shipments: List[Shipment],
                 trucks: List[Truck],
                 lanes: List[Lane],
                 qaoa_reps: int = 3,
                 max_iter: int = 100):
        """
        Initialize QAOA optimizer

        Args:
            shipments: List of shipments
            trucks: List of trucks
            lanes: List of lanes
            qaoa_reps: Number of QAOA layers (p parameter)
            max_iter: Maximum iterations for classical optimizer
        """
        super().__init__(shipments, trucks, lanes)
        self.qaoa_reps = qaoa_reps
        self.max_iter = max_iter

        if not QISKIT_AVAILABLE:
            raise ImportError(
                "Qiskit optimization packages required. "
                "Install with: pip install qiskit-optimization qiskit-algorithms"
            )

    def optimize(self,
                 weights: Optional[Dict[str, float]] = None,
                 progress_callback=None,
                 **kwargs) -> OptimizationResult:
        """
        Run QAOA optimization

        Args:
            weights: Dictionary of weights for objective and penalties
            progress_callback: Optional callback function for progress updates
            **kwargs: Additional parameters

        Returns:
            OptimizationResult with assignments and metrics
        """
        start_time = time.time()

        def log(message):
            """Helper to log messages"""
            print(message)
            if progress_callback:
                progress_callback(message)

        try:
            # Create QUBO formulation
            log("Creating QUBO formulation...")
            qubo_form = QUBOFormulation(
                self.shipments,
                self.trucks,
                self.lanes,
                weights
            )

            qp = qubo_form.create_qubo()

            # Get problem size
            n_vars, n_constraints = qubo_form.get_problem_size()
            log(f"QUBO problem size: {n_vars} variables, {n_constraints} constraints")

            # Check if problem is too large for quantum simulation
            if n_vars > 20:
                log(f"Warning: Problem size ({n_vars} variables) may be too large")
                log("Consider using a smaller problem or classical optimizer")

            # Set up QAOA
            log(f"Setting up QAOA with {self.qaoa_reps} layers...")
            sampler = StatevectorSampler()
            qaoa = QAOA(
                sampler=sampler,
                optimizer=COBYLA(maxiter=self.max_iter),
                reps=self.qaoa_reps
            )

            # Solve using QAOA
            log("Running QAOA optimization (this may take a few minutes)...")
            log("Building quantum circuit and optimizing parameters...")
            optimizer = MinimumEigenOptimizer(qaoa)
            result = optimizer.solve(qp)
            log("QAOA optimization completed!")

            # Decode solution - handle different result formats
            log("Decoding quantum solution...")
            solution_dict = {}
            if hasattr(result, 'x'):
                # result.x contains the solution vector
                var_names = [v.name for v in qp.variables]
                solution_dict = {name: int(round(val))
                                 for name, val in zip(var_names, result.x)}
            elif hasattr(result, 'variables'):
                # Try to extract from variables list
                for i, var in enumerate(result.variables):
                    var_name = var.name if hasattr(var, 'name') else f"x{i}"
                    if hasattr(var, 'value'):
                        solution_dict[var_name] = int(round(var.value))
                    else:
                        # Try to get value from result.x
                        if hasattr(result, 'x') and i < len(result.x):
                            solution_dict[var_name] = int(round(result.x[i]))

            assignments = qubo_form.decode_solution(solution_dict)

            # Calculate metrics
            log("Calculating final metrics...")
            metrics = self.calculate_total_metrics(assignments)
            trucks_used = self.count_trucks_used(assignments)

            computation_time = time.time() - start_time

            assigned_ids = set(a['shipment'].shipment_id for a in assignments)
            unassigned_count = len(self.shipments) - len(assigned_ids)

            return OptimizationResult(
                algorithm=f"QAOA (p={self.qaoa_reps})",
                assignments=assignments,
                total_cost=metrics['cost'],
                total_co2=metrics['co2'],
                computation_time=computation_time,
                trucks_used=trucks_used,
                shipments_assigned=len(assignments),
                shipments_unassigned=unassigned_count,
                metadata={
                    'qaoa_reps': self.qaoa_reps,
                    'max_iter': self.max_iter,
                    'problem_size': n_vars,
                    'objective_value': result.fval,
                    'status': str(result.status)
                }
            )

        except Exception as e:
            error_msg = f"Error in QAOA optimization: {e}"
            print(error_msg)
            if progress_callback:
                progress_callback(error_msg)
            computation_time = time.time() - start_time

            return OptimizationResult(
                algorithm=f"QAOA (p={self.qaoa_reps})",
                assignments=[],
                total_cost=0.0,
                total_co2=0.0,
                computation_time=computation_time,
                trucks_used=0,
                shipments_assigned=0,
                shipments_unassigned=len(self.shipments),
                metadata={
                    'error': str(e),
                    'status': 'failed'
                }
            )

    def optimize_with_fallback(self,
                               weights: Optional[Dict[str, float]] = None,
                               progress_callback=None,
                               **kwargs) -> OptimizationResult:
        """
        Run QAOA with fallback to classical if problem is too large

        Args:
            weights: Dictionary of weights
            progress_callback: Optional callback function for progress updates
            **kwargs: Additional parameters

        Returns:
            OptimizationResult
        """
        # Check problem size
        n_vars = len(self.shipments) * len(self.trucks)

        if n_vars > 20:
            msg = f"Problem too large for QAOA ({n_vars} variables). Using classical optimizer."
            print(msg)
            if progress_callback:
                progress_callback(msg)
            from optimizers.classical.greedy_optimizer import GreedyOptimizer
            classical = GreedyOptimizer(
                self.shipments, self.trucks, self.lanes)
            return classical.optimize(objective='balanced')

        return self.optimize(weights=weights, progress_callback=progress_callback, **kwargs)
