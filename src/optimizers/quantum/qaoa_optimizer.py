"""
Real QAOA optimizer using Qiskit 2.x native primitives.

Uses:
  • qiskit.circuit.library.QAOAAnsatz  — standard p-layer QAOA circuit
  • qiskit_aer.primitives.Sampler      — statevector / shot-based simulation
  • scipy.optimize.minimize (COBYLA)   — classical parameter optimiser
  • qiskit.quantum_info.SparsePauliOp  — Ising cost Hamiltonian

No qiskit-optimization or qiskit-algorithms dependency required.
"""

from optimizers.quantum.qubo_formulation import QUBOFormulation
from optimizers.base_optimizer import BaseOptimizer, OptimizationResult
from optimizers.classical.greedy_optimizer import GreedyOptimizer
from models.lane import Lane
from models.truck import Truck
from models.shipment import Shipment

import time
import sys
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Callable

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# ── Qiskit 2.x imports ──────────────────────────────────────────────────────
try:
    from qiskit.circuit.library import QAOAAnsatz
    from qiskit.quantum_info import SparsePauliOp
    from qiskit.compiler import transpile
    from qiskit_aer import AerSimulator
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    from scipy.optimize import minimize as scipy_minimize
    QISKIT_AVAILABLE = True
except ImportError as _qiskit_err:
    QISKIT_AVAILABLE = False
    _qiskit_import_error = str(_qiskit_err)


class QAOAOptimizer(BaseOptimizer):
    """
    QAOA-based transport assignment optimiser.

    The assignment problem is encoded as a QUBO and mapped to an
    Ising Hamiltonian.  QAOAAnsatz builds the standard p-layer
    cost+mixer circuit.  AerSampler runs it on the local Aer
    statevector simulator.  COBYLA minimises ⟨H_C⟩ over the 2p
    variational parameters (γ, β).

    The best bitstring sampled at the optimised angles is decoded
    into concrete truck ↔ shipment assignments.

    Args:
        shipments   : shipments to assign (keep ≤ 4 for p=2, ≤ 6 for p=1)
        trucks      : available trucks (keep ≤ 4)
        lanes       : all lanes
        qaoa_reps   : QAOA depth p  (number of cost+mixer layers)
        max_iter    : COBYLA iteration budget
        shots       : measurement shots for expectation estimation
    """

    MAX_QUBITS = 20   # hard cap — QUBO has n_shipments × n_trucks qubits

    def __init__(self,
                 shipments: List[Shipment],
                 trucks: List[Truck],
                 lanes: List[Lane],
                 qaoa_reps: int = 2,
                 max_iter: int = 100,
                 shots: int = 2048):
        super().__init__(shipments, trucks, lanes)
        self.qaoa_reps = qaoa_reps
        self.max_iter  = max_iter
        self.shots     = shots

        if not QISKIT_AVAILABLE:
            raise ImportError(
                f"Qiskit 2.x + qiskit-aer required. "
                f"Install: pip install qiskit qiskit-aer scipy\n"
                f"Original error: {_qiskit_import_error}"
            )

    # ------------------------------------------------------------------ #
    #  Main entry point                                                    #
    # ------------------------------------------------------------------ #

    def optimize(self,
                 weights: Optional[Dict[str, float]] = None,
                 progress_callback: Optional[Callable] = None) -> OptimizationResult:
        """
        Run QAOA optimisation and return an OptimizationResult.
        Falls back to Greedy if the quantum circuit produces no valid
        assignments (e.g. all-zero measurement).
        """
        start = time.time()

        def log(msg: str):
            print(msg)
            if progress_callback:
                progress_callback(msg)

        n_ships = len(self.shipments)
        n_trucks = len(self.trucks)
        n_qubits = n_ships * n_trucks

        log(f"⚛  QAOA Optimiser  |  {n_ships} shipments × {n_trucks} trucks "
            f"= {n_qubits} qubits  |  p={self.qaoa_reps}")

        if n_qubits > self.MAX_QUBITS:
            log(f"⚠  Problem too large ({n_qubits} qubits > {self.MAX_QUBITS}). "
                f"Using classical fallback.")
            return self._greedy_fallback(start, label="QAOA→Greedy (size)")

        # ── 1. Build QUBO → Ising Hamiltonian ───────────────────────────
        log("   Building QUBO + Ising Hamiltonian …")
        qubo = QUBOFormulation(self.shipments, self.trucks, self.lanes, weights)
        cost_op: SparsePauliOp = qubo.build_cost_operator()
        log(f"   Cost operator: {cost_op.num_qubits} qubits, "
            f"{len(cost_op)} Pauli terms")

        # ── 2. Build QAOAAnsatz circuit ──────────────────────────────────
        log(f"   Building QAOAAnsatz (p={self.qaoa_reps}) …")
        ansatz = QAOAAnsatz(
            cost_operator=cost_op,
            reps=self.qaoa_reps,
            name=f"QAOA_p{self.qaoa_reps}"
        )
        n_params = ansatz.num_parameters
        log(f"   Circuit: depth={ansatz.decompose().depth()}, "
            f"parameters={n_params}")

        # Transpile to Aer basis gates once — reuse for every COBYLA eval
        simulator = AerSimulator(method='statevector')
        ansatz_t = transpile(ansatz, simulator, optimization_level=1)

        # ── 3. Classical optimiser loop (COBYLA) ─────────────────────────
        log(f"   Running COBYLA (max {self.max_iter} iterations, "
            f"{self.shots} shots/eval) …")
        sampler = AerSampler()
        iteration_count = [0]

        def objective(params: np.ndarray) -> float:
            """Estimate ⟨H_C⟩ from shot counts."""
            iteration_count[0] += 1
            bound = ansatz_t.assign_parameters(params)
            bound.measure_all()
            job    = sampler.run([bound], shots=self.shots)
            counts = job.result()[0].data.meas.get_counts()
            n      = qubo.n_vars
            quasi  = {int(k, 2): v / self.shots for k, v in counts.items()}
            return self._expected_energy(quasi, qubo, n)

        # Warm start: γ = π/4 per layer, β = π/8 per layer (standard heuristic)
        rng   = np.random.default_rng(seed=42)
        gamma = rng.uniform(0, np.pi,     self.qaoa_reps)
        beta  = rng.uniform(0, np.pi / 2, self.qaoa_reps)
        x0    = np.concatenate([gamma, beta])

        opt_result = scipy_minimize(
            objective,
            x0,
            method='COBYLA',
            options={'maxiter': self.max_iter, 'rhobeg': 0.5}
        )

        log(f"   COBYLA: {iteration_count[0]} evals, "
            f"converged={opt_result.success}, "
            f"⟨H_C⟩={opt_result.fun:.4f}")

        # ── 4. Sample the optimised circuit ─────────────────────────────
        log(f"   Sampling optimised circuit ({self.shots} shots) …")
        final = ansatz_t.assign_parameters(opt_result.x)
        final.measure_all()
        job    = sampler.run([final], shots=self.shots)
        counts = job.result()[0].data.meas.get_counts()
        n      = qubo.n_vars
        quasi  = {int(k, 2): v / self.shots for k, v in counts.items()}

        # ── 5. Decode best bitstring(s) ──────────────────────────────────
        assignments = self._decode_best(quasi, qubo, n, log)

        elapsed = time.time() - start

        if not assignments:
            log("   No valid QAOA assignments — applying Greedy refinement …")
            return self._greedy_fallback(start, label=f"QAOA+Greedy (p={self.qaoa_reps})")

        metrics = self.calculate_total_metrics(assignments)
        trucks_used = self.count_trucks_used(assignments)
        assigned_ids = {a['shipment'].shipment_id for a in assignments}

        log(f"   ✓ QAOA assigned {len(assignments)}/{n_ships} shipments "
            f"| cost=€{metrics['cost']:,.0f} | CO₂={metrics['co2']:,.0f}kg "
            f"| time={elapsed:.1f}s")

        return OptimizationResult(
            algorithm=f"QAOA (p={self.qaoa_reps}, Qiskit 2.x + Aer)",
            assignments=assignments,
            total_cost=metrics['cost'],
            total_co2=metrics['co2'],
            computation_time=elapsed,
            trucks_used=trucks_used,
            shipments_assigned=len(assignments),
            shipments_unassigned=n_ships - len(assigned_ids),
            metadata={
                'qaoa_reps':       self.qaoa_reps,
                'n_qubits':        n_qubits,
                'n_pauli_terms':   len(cost_op),
                'cobyla_iters':    iteration_count[0],
                'cobyla_success':  opt_result.success,
                'final_energy':    opt_result.fun,
                'shots':           self.shots,
                'simulator':       'AerSimulator (statevector)',
            }
        )

    def optimize_with_fallback(self,
                               weights: Optional[Dict[str, float]] = None,
                               progress_callback: Optional[Callable] = None,
                               **kwargs) -> OptimizationResult:
        """
        Run QAOA if the problem fits in MAX_QUBITS; otherwise Greedy.
        Called by the GUI and benchmark suite.
        """
        n_qubits = len(self.shipments) * len(self.trucks)
        if n_qubits > self.MAX_QUBITS:
            msg = (f"Problem too large for QAOA ({n_qubits} vars > {self.MAX_QUBITS}). "
                   f"Using Greedy.")
            print(msg)
            if progress_callback:
                progress_callback(msg)
            return self._greedy_fallback(time.time(), label="QAOA→Greedy (size)")

        return self.optimize(
            weights=weights,
            progress_callback=progress_callback,
            **kwargs
        )

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _expected_energy(self,
                         quasi: Dict[int, float],
                         qubo: QUBOFormulation,
                         n: int) -> float:
        """Estimate ⟨H_C⟩ = Σ P(bitstring) × x^T Q x."""
        Q = qubo.build_qubo_matrix()
        energy = 0.0
        for int_key, prob in quasi.items():
            bits = format(int_key, f'0{n}b')[::-1]
            x = np.array([int(b) for b in bits[:n]], dtype=float)
            energy += prob * float(x @ Q @ x)
        return energy

    def _decode_best(self,
                     quasi: Dict[int, float],
                     qubo: QUBOFormulation,
                     n_qubits: int,
                     log: Callable) -> List[Dict]:
        """
        Try top-K most probable bitstrings; return the first that gives
        at least one valid assignment.
        """
        sorted_shots = sorted(quasi.items(), key=lambda kv: -kv[1])
        log(f"   Top-5 bitstrings: "
            + "  ".join(f"|{format(k, f'0{n_qubits}b')}⟩ {p:.3f}"
                        for k, p in sorted_shots[:5]))

        for int_key, prob in sorted_shots[:20]:
            bitstring = format(int_key, f'0{n_qubits}b')
            assignments = qubo.decode_solution(bitstring)
            if assignments:
                log(f"   Best valid bitstring |{bitstring}⟩ "
                    f"(prob={prob:.3f}) → {len(assignments)} assignments")
                return assignments

        return []

    def _greedy_fallback(self, start: float, label: str) -> OptimizationResult:
        """Return a Greedy result re-labelled as the given algorithm name."""
        greedy = GreedyOptimizer(self.shipments, self.trucks, self.lanes)
        result = greedy.optimize(objective='balanced')
        result.algorithm = label
        result.computation_time = time.time() - start
        return result
