"""
QUBO formulation for transport assignment.

Converts the shipment→truck assignment problem into a
Quadratic Unconstrained Binary Optimization (QUBO) and then into
the Pauli-Z Ising Hamiltonian required by QAOAAnsatz.

No qiskit-optimization dependency — uses only core Qiskit 2.x.
"""

from models.lane import Lane
from models.truck import Truck
from models.shipment import Shipment

import sys
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from qiskit.quantum_info import SparsePauliOp
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False


class QUBOFormulation:
    """
    Build a QUBO for the transport assignment problem.

    Decision variable:  x[i, j] = 1 if shipment i is assigned to truck j.

    Objective (minimise):
        alpha * sum_ij  cost(i,j)  * x[i,j]
        + beta  * sum_ij  co2(i,j)   * x[i,j]

    Constraints (added as quadratic penalties):
        [A]  Each shipment assigned at most once:  sum_j x[i,j] <= 1
        [B]  Truck weight capacity not exceeded
        [C]  Truck volume capacity not exceeded

    The QUBO matrix Q is defined so that  x^T Q x  is minimised.
    """

    DEFAULT_WEIGHTS = {
        'cost':             1.0,
        'co2':              0.01,
        'assign_penalty':   5.0,   # each double-assignment
        'capacity_penalty': 3.0,   # each kg / m3 over capacity (scaled)
    }

    def __init__(self,
                 shipments: List[Shipment],
                 trucks: List[Truck],
                 lanes: List[Lane],
                 weights: Optional[Dict[str, float]] = None):
        self.shipments = shipments
        self.trucks = trucks
        self.lanes = lanes
        self.weights = {**self.DEFAULT_WEIGHTS, **(weights or {})}

        # Pre-compute best lane cost/co2 for each (shipment, truck) pair
        self._lane_cache: Dict[Tuple[int, int], Tuple[float, float]] = {}
        self._build_lane_cache()

        # n = number of binary variables  (shipment_i × truck_j)
        self.n_vars = len(shipments) * len(trucks)

    # ------------------------------------------------------------------ #
    #  Public API                                                           #
    # ------------------------------------------------------------------ #

    def build_qubo_matrix(self) -> np.ndarray:
        """Return the (n×n) upper-triangular QUBO matrix Q."""
        n = self.n_vars
        Q = np.zeros((n, n))

        ns = len(self.shipments)
        nt = len(self.trucks)

        alpha = self.weights['cost']
        beta  = self.weights['co2']
        P_a   = self.weights['assign_penalty']
        P_c   = self.weights['capacity_penalty']

        # --- linear terms: objective cost ---
        for i, ship in enumerate(self.shipments):
            for j, truck in enumerate(self.trucks):
                idx = i * nt + j
                cost, co2 = self._lane_cache.get((i, j), (0.0, 0.0))
                # Normalise so coefficients are O(1)
                Q[idx, idx] += alpha * cost / 1000.0 + beta * co2

        # --- quadratic penalty [A]: at most one truck per shipment ---
        for i in range(ns):
            for j1 in range(nt):
                for j2 in range(j1 + 1, nt):
                    idx1 = i * nt + j1
                    idx2 = i * nt + j2
                    Q[idx1, idx2] += P_a

        # --- quadratic penalty [B/C]: truck capacity ---
        for j, truck in enumerate(self.trucks):
            max_w = truck.capacity_weight_kg
            max_v = truck.capacity_volume_m3
            for i1, s1 in enumerate(self.shipments):
                for i2 in range(i1 + 1, ns):
                    s2 = self.shipments[i2]
                    idx1 = i1 * nt + j
                    idx2 = i2 * nt + j
                    # weight overflow contribution
                    w_scale = (s1.weight_kg * s2.weight_kg) / (max_w ** 2)
                    v_scale = (s1.volume_m3 * s2.volume_m3) / (max_v ** 2)
                    Q[idx1, idx2] += P_c * (w_scale + v_scale)

        return Q

    def qubo_to_ising(self) -> Tuple[np.ndarray, float]:
        """
        Convert QUBO  x^T Q x  →  Ising  Σ h_i Z_i + Σ J_ij Z_i Z_j + offset.

        Uses substitution  x_k = (1 - Z_k) / 2.

        Returns:
            h      : 1-D array of single-qubit Z fields
            J      : 2-D symmetric matrix of ZZ couplings
            offset : constant energy offset
        """
        Q = self.build_qubo_matrix()
        n = Q.shape[0]
        h = np.zeros(n)
        J = np.zeros((n, n))
        offset = 0.0

        for i in range(n):
            for j in range(i, n):
                if i == j:
                    # x_i = (1-Z_i)/2  →  Q_ii * x_i contributes:
                    # Q_ii/4 - Q_ii/4 * Z_i  (and constant Q_ii/4)
                    h[i] -= Q[i, i] / 4.0
                    offset += Q[i, i] / 4.0
                else:
                    # Q_ij * x_i * x_j  where Q is upper-triangular (Q[i,j] = Q[j,i]/2 each)
                    qij = Q[i, j]
                    J[i, j] += qij / 4.0
                    J[j, i] += qij / 4.0
                    h[i] -= qij / 4.0
                    h[j] -= qij / 4.0
                    offset += qij / 4.0

        return h, J, offset

    def build_cost_operator(self) -> "SparsePauliOp":
        """
        Build the Qiskit SparsePauliOp cost Hamiltonian for QAOAAnsatz.

        H_C = Σ_i h_i Z_i  +  Σ_{i<j} J_ij Z_i Z_j

        Qubit ordering: qubit 0 = variable 0, …, qubit n-1 = variable n-1.
        (Qiskit's Pauli strings are written right-to-left, so qubit k maps
         to position n-1-k in the string.)
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("qiskit is required for build_cost_operator()")

        h, J, _ = self.qubo_to_ising()
        n = len(h)

        pauli_list = []

        # Single-qubit Z terms
        for i in range(n):
            if abs(h[i]) > 1e-9:
                label = ['I'] * n
                label[n - 1 - i] = 'Z'
                pauli_list.append((''.join(label), h[i]))

        # Two-qubit ZZ terms
        for i in range(n):
            for j in range(i + 1, n):
                if abs(J[i, j]) > 1e-9:
                    label = ['I'] * n
                    label[n - 1 - i] = 'Z'
                    label[n - 1 - j] = 'Z'
                    pauli_list.append((''.join(label), J[i, j]))

        if not pauli_list:
            # Identity with zero weight as fallback
            pauli_list = [('I' * n, 0.0)]

        return SparsePauliOp.from_list(pauli_list)

    def decode_solution(self, bitstring: str) -> List[Dict]:
        """
        Decode a measurement bitstring into transport assignments.

        Args:
            bitstring: binary string of length n_vars (MSB = qubit n-1).
                       Qiskit orders results as qubit 0 = rightmost char.

        Returns:
            list of assignment dicts compatible with OptimizationResult.
        """
        nt = len(self.trucks)
        ns = len(self.shipments)

        # Reverse so that index k maps to bit position k from the right
        bits = bitstring[::-1]

        assignments = []
        assigned_shipments = set()
        truck_loads: Dict[str, Dict[str, float]] = {
            t.truck_id: {'weight': 0.0, 'volume': 0.0}
            for t in self.trucks
        }

        for i, ship in enumerate(self.shipments):
            for j, truck in enumerate(self.trucks):
                idx = i * nt + j
                if idx >= len(bits):
                    continue
                if bits[idx] == '1':
                    if ship.shipment_id in assigned_shipments:
                        continue  # skip double-assignment

                    tl = truck_loads[truck.truck_id]
                    if (tl['weight'] + ship.weight_kg > truck.capacity_weight_kg or
                            tl['volume'] + ship.volume_m3 > truck.capacity_volume_m3):
                        continue  # capacity violated

                    # Find best lane for this pair
                    lanes = self._get_matching_lanes(ship)
                    if not lanes:
                        continue
                    best_lane = min(lanes, key=lambda l: l.total_cost(truck.cost_per_km_eur))

                    cost = best_lane.total_cost(truck.cost_per_km_eur)
                    co2  = best_lane.total_co2(truck.co2_per_km_kg)

                    assignments.append({
                        'shipment': ship,
                        'truck':    truck,
                        'lane':     best_lane,
                        'cost':     cost,
                        'co2':      co2,
                    })
                    assigned_shipments.add(ship.shipment_id)
                    tl['weight'] += ship.weight_kg
                    tl['volume'] += ship.volume_m3

        return assignments

    def get_problem_size(self) -> Tuple[int, int]:
        """Return (n_variables, n_constraints)."""
        n_vars = self.n_vars
        n_constraints = len(self.shipments) + len(self.trucks) * 2
        return n_vars, n_constraints

    # ------------------------------------------------------------------ #
    #  Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _build_lane_cache(self):
        for i, ship in enumerate(self.shipments):
            lanes = self._get_matching_lanes(ship)
            for j, truck in enumerate(self.trucks):
                if lanes:
                    best = min(lanes, key=lambda l: l.total_cost(truck.cost_per_km_eur))
                    self._lane_cache[(i, j)] = (
                        best.total_cost(truck.cost_per_km_eur),
                        best.total_co2(truck.co2_per_km_kg),
                    )
                else:
                    self._lane_cache[(i, j)] = (0.0, 0.0)

    def _get_matching_lanes(self, shipment: Shipment) -> List[Lane]:
        return [
            l for l in self.lanes
            if l.origin.lower() == shipment.origin.lower()
            and l.destination.lower() == shipment.destination.lower()
        ]
