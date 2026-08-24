
# SAP Quantum Transportation Optimizer

An educational quantum computing demo for [RasQberry](https://github.com/JanLahmann/RasQberry-Two), built by SAP. It teaches students how the Quantum Approximate Optimization Algorithm (QAOA) solves a real-world transport assignment problem — step by step, on a Raspberry Pi.

> **Note on Quantum Computing:** At the current NISQ era of quantum computing, quantum advantage has not been achieved for optimization problems. This demo is designed for education and research — to understand *how* QAOA works, not to claim it outperforms classical approaches.

---

## What It Does

Given a set of shipments and trucks, the app encodes the assignment problem as a QUBO (Quadratic Unconstrained Binary Optimization), maps it to an Ising Hamiltonian, and runs QAOA on Qiskit's Aer simulator. Students can interactively explore:

- **Problem size** — 2×2 (4 qubits) up to 5×4 (20 qubits)
- **QAOA depth** — p=1, p=2, or p=3 layers
- **Shot count** — 256, 512, or 2048 measurement shots
- **Qubit map** — see exactly which qubit encodes which shipment→truck assignment
- **Circuit viewer** — view the actual Qiskit quantum circuit with a Pauli notation guide
- **Compare runs** — compare multiple QAOA configurations side by side, grouped by qubit count

---

## Installation

### Prerequisites
- Python 3.8+
- Raspberry Pi 
### Local
```bash
pip install -r requirements.txt
cd src
python gui_main.py
```

### Via RasQberry Catalog
This demo is listed in the RasQberry external demo catalog. Install it directly from the RasQberry menu — it fetches the repo, validates the manifest, installs dependencies, and launches the GUI automatically.

---

## Quick Start

Launch the GUI:
```bash
cd src
python gui_main.py
```

1. Click **Load Data** to load shipments, trucks, and lanes from CSV
2. Adjust **Problem Size**, **QAOA Depth**, and **Shots** in the control bar
3. Click **Run QAOA** — watch the optimizer run in the console
4. Click **View Circuit** to inspect the Qiskit quantum circuit
5. Run again with different settings and click **Compare Results**

---

## How QAOA Works (for students)

| Step | What happens |
|---|---|
| QUBO formulation | Assignment problem → quadratic cost matrix Q |
| Ising mapping | Q → Pauli-Z Hamiltonian H_C = Σ h_i Z_i + Σ J_ij Z_i Z_j |
| QAOAAnsatz | p layers of cost unitary exp(-iγ H_C) + mixer unitary exp(-iβ H_B) |
| COBYLA | Classical optimizer tunes 2p parameters (γ, β) to minimize ⟨H_C⟩ |
| Measurement | Sample the optimised circuit → decode best bitstring → assignments |

Qubit index formula: qubit `i × n_trucks + j` = Shipment `i` → Truck `j`

---

## Project Structure

```
src/
  gui_main.py                        # Main GUI entry point (SAP Fiori design)
  main.py                            # Interactive CLI
  optimizers/
    quantum/
      qaoa_optimizer.py              # QAOA with Qiskit 2.x + Aer
      qubo_formulation.py            # QUBO → Ising Hamiltonian
    classical/
      greedy_optimizer.py            # Greedy fallback (used internally)
  data_loader/csv_loader.py          # Loads shipments, trucks, lanes from CSV
data/input/                          # Sample CSV datasets
rqb-demo.json                        # RasQberry manifest
requirements.txt                     # Pinned dependencies
LICENSE                              # MIT
```

---

## Dependencies

All pinned for reproducible installs on ARM64 (Raspberry Pi):

```
qiskit==2.3.0
qiskit-aer==0.17.2
numpy==2.2.6
scipy==1.15.3
pillow==11.2.1
```

---

## License

MIT — see [LICENSE](LICENSE)
