
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

On your RasQberry device, ensure you have:
- Python 3.9+
- Qiskit 1.x (already installed in RQB2 venv)
- Active RQB2 virtual environment

### Setup

1. **Activate the RQB2 virtual environment**:
```bash
source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate
```

2. **Navigate to the application directory**:
```bash
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
```

3. **Install additional dependencies** (if needed):
```bash
pip install qiskit-optimization qiskit-algorithms
```

## Project Structure

```
quantum_transport_optimizer/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── config/                           # Configuration files
│   ├── optimizer_config.yaml
│   ├── cost_factors.json
│   └── co2_factors.json
├── data/
│   ├── input/                        # Input data files
│   │   ├── shipments.csv
│   │   ├── trucks.csv
│   │   └── lanes.csv
│   └── output/                       # Results directory
├── src/
│   ├── main.py                       # Main entry point
│   ├── models/                       # Data models
│   │   ├── shipment.py
│   │   ├── truck.py
│   │   └── lane.py
│   ├── data_loader/                  # Data loading
│   │   ├── csv_loader.py
│   │   └── rest_loader.py
│   ├── optimizers/                   # Optimization algorithms
│   │   ├── base_optimizer.py
│   │   ├── classical/
│   │   │   ├── greedy_optimizer.py
│   │   │   └── local_search.py
│   │   └── quantum/
│   │       ├── qaoa_optimizer.py
│   │       └── qubo_formulation.py
│   ├── metrics/                      # Cost and CO₂ calculations
│   ├── comparison/                   # Result comparison
│   └── visualization/                # Display interfaces
└── tests/                            # Unit tests
```

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

## Data Format

### Shipments CSV

```csv
shipment_id,origin,destination,weight_kg,volume_m3,priority,deadline,value_eur
SH001,Berlin,Munich,500,2.5,3,2026-01-20T18:00:00,5000
```
 

### Trucks CSV

```csv
truck_
## REST API Integration

### Loading Data from API

```python
from data_loader.rest_loader import RESTLoader

# Initialize REST loader
loader = RESTLoader(
    base_url="https://your-api.com/api",
    api_key="your_api_key"
)

# Load all data
data = loader.load_all()

# Or load individually
shipments = loader.load_shipments()
trucks = loader.load_trucks()
lanes = loader.load_lanes()
```

### Expected API Endpoints

- `GET /shipments` - Returns list of shipments
- `GET /trucks` - Returns list of trucks
- `GET /lanes` - Returns list of lanes
- `POST /results` - Submit optimization results

## Touchscreen Display Support

The application includes support for touchscreen displays on RasQberry:

### Features (Coming Soon)
- Interactive GUI with touch controls
- Real-time optimization progress
- Visual comparison charts
- Truck assignment visualization
- Cost and CO₂ metrics dashboard

### Display Configuration

For the official RasQberry touchscreen (7" or 10"):
```bash
# The display should be auto-detected
# If not, configure in /boot/config.txt
```

## Algorithm Comparison & Benchmarking

### Performance Characteristics

| Algorithm | Search Type | Problem Size | Speed (Pi) | Solution Quality | Production Ready |
|-----------|-------------|--------------|------------|------------------|------------------|
| **Exact Solver** | Exhaustive | <12 vars | Slow | **Optimal** ✓ | Yes (small only) |
| **Simulated Annealing** | Global | <1000 vars | Fast-Medium | Near-optimal | **Yes** ✓ |
| **Genetic Algorithm** | Global | <500 vars | Medium | Near-optimal | **Yes** ✓ |
| **Greedy** | Local | Any | Very Fast | Good baseline | Yes (estimates) |
| **QAOA** | Global | <20 vars | Very Slow | Educational | No (research only) |


This will:
1. Run all available optimizers on the same problem
2. Compare against optimal solution (if problem is small enough)
3. Calculate optimality gaps for each algorithm
4. Generate detailed performance report
5. Provide recommendations based on results
