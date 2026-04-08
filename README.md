
# Quantum Transport Optimizer for RasQberry

An educational transport optimization application comparing classical and quantum algorithms for vehicle routing problems. Designed for SAP TM-like data with support for CSV/REST input and touchscreen display on Raspberry Pi.

> ** Important Note on Quantum Computing**: This project demonstrates quantum algorithms for educational purposes. At the current state of quantum computing technology (NISQ era), **quantum advantage has not been achieved** for optimization problems. Classical algorithms will consistently outperform quantum approaches on available hardware. QAOA is included for research, education, and future readiness.

## Features

- **Comprehensive Classical Algorithms**:
  - **Greedy Optimizer**: Fast baseline heuristic
  - **Simulated Annealing**: Global search with adaptive cooling (Pi-optimized)
  - **Genetic Algorithm**: Evolutionary optimization approach
  - **Exact Solver**: Optimal solutions for small problems (<12 variables)

- **Quantum Algorithm (Educational)**:
  - **QAOA**: Quantum Approximate Optimization Algorithm
  - For research and educational purposes
  - Demonstrates quantum computing concepts
  - Not recommended for production use

- **Multi-Objective Optimization**:
  - Minimize transportation costs
  - Minimize CO₂ emissions
  - Balance cost and environmental impact

- **Flexible Data Input**:
  - CSV files
  - REST API integration
  - Sample datasets included

- **Rich Visualization**:
  - CLI interface with detailed results
  - Touchscreen GUI (coming soon)
  - LED matrix display support (optional)
  - Comparison tables and metrics

## Installation

### Prerequisites
- Python 3.8+
- RasQberry device (optional, for deployment)
- `sshpass` for deployment (macOS: `brew install hudochenkov/sshpass/sshpass`)

### Local Installation
```bash
pip install -r requirements.txt
```

### Deploy to RasQberry
```bash
# Deploy with password authentication
./scripts/deploy_to_rasqberry.sh YOUR_RASQBERRY_IP [PASSWORD]

# Or use the simpler script
./DEPLOY.sh YOUR_RASQBERRY_IP [PASSWORD]
```

After deployment, a desktop icon will be automatically created on the RasQberry device for easy access to the GUI application.

## Quick Start

### 1. Run with Sample Data

```bash
cd src
python main.py
```

This will:
- Load sample shipments, trucks, and lanes from CSV files
- Run both classical and quantum optimizers
- Display comparison results

### 2. Using the CLI Interface

```python
from data_loader.csv_loader import CSVLoader
from optimizers.classical.greedy_optimizer import GreedyOptimizer
from optimizers.quantum.qaoa_optimizer import QAOAOptimizer

# Load data
loader = CSVLoader("../data/input")
data = loader.load_all()

# Run greedy optimizer
greedy = GreedyOptimizer(
    data['shipments'],
    data['trucks'],
    data['lanes']
)
greedy_result = greedy.optimize(objective='balanced')
print(greedy_result.summary())

# Run QAOA optimizer
qaoa = QAOAOptimizer(
    data['shipments'],
    data['trucks'],
    data['lanes'],
    qaoa_reps=3
)
qaoa_result = qaoa.optimize()
print(qaoa_result.summary())
```

### 3. Compare Results

```python
print(f"\n{'='*60}")
print("COMPARISON")
print(f"{'='*60}")
print(f"{'Algorithm':<30} {'Cost (€)':<15} {'CO₂ (kg)':<15}")
print(f"{'-'*60}")
print(f"{'Greedy':<30} {greedy_result.total_cost:<15.2f} {greedy_result.total_co2:<15.2f}")
print(f"{'QAOA':<30} {qaoa_result.total_cost:<15.2f} {qaoa_result.total_co2:<15.2f}")
print(f"{'-'*60}")

# Calculate improvements
cost_improvement = ((greedy_result.total_cost - qaoa_result.total_cost) / 
                   greedy_result.total_cost * 100)
co2_improvement = ((greedy_result.total_co2 - qaoa_result.total_co2) / 
                  greedy_result.total_co2 * 100)

print(f"Cost Improvement: {cost_improvement:+.2f}%")
print(f"CO₂ Improvement: {co2_improvement:+.2f}%")
```



This will:
1. Run all available optimizers on the same problem
2. Compare against optimal solution (if problem is small enough)
3. Calculate optimality gaps for each algorithm
4. Generate detailed performance report
5. Provide recommendations based on results
