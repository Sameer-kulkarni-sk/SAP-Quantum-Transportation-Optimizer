
# Quantum Transport Optimizer for RasQberry

An educational transport optimization application comparing classical and quantum algorithms for vehicle routing problems. Designed for SAP TM-like data with support for CSV/REST input and touchscreen display on Raspberry Pi.

> **⚠️ Important Note on Quantum Computing**: This project demonstrates quantum algorithms for educational purposes. At the current state of quantum computing technology (NISQ era), **quantum advantage has not been achieved** for optimization problems. Classical algorithms will consistently outperform quantum approaches on available hardware. QAOA is included for research, education, and future readiness.

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

**Fields**:
- `shipment_id`: Unique identifier
- `origin`: Starting location
- `destination`: Delivery location
- `weight_kg`: Weight in kilograms
- `volume_m3`: Volume in cubic meters
- `priority`: 1-5 (5 is highest)
- `deadline`: ISO 8601 datetime
- `value_eur`: Shipment value in EUR

### Trucks CSV

```csv
truck_id,capacity_weight_kg,capacity_volume_m3,cost_per_km_eur,co2_per_km_kg,location,available
TR001,1000,5.0,1.2,0.8,Berlin,true
```

**Fields**:
- `truck_id`: Unique identifier
- `capacity_weight_kg`: Maximum weight capacity
- `capacity_volume_m3`: Maximum volume capacity
- `cost_per_km_eur`: Operating cost per kilometer
- `co2_per_km_kg`: CO₂ emissions per kilometer
- `location`: Current location
- `available`: true/false availability status

### Lanes CSV

```csv
lane_id,origin,destination,distance_km,travel_time_hours,toll_cost_eur,traffic_factor
LN001,Berlin,Munich,584,6.5,45.0,1.0
```

**Fields**:
- `lane_id`: Unique identifier
- `origin`: Starting point
- `destination`: End point
- `distance_km`: Distance in kilometers
- `travel_time_hours`: Expected travel time
- `toll_cost_eur`: Toll costs
- `traffic_factor`: Traffic multiplier (1.0 = normal, >1.0 = congested)

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

### Detailed Algorithm Descriptions

#### Exact Solver (NEW)
- **Search Type**: Exhaustive enumeration
- **Speed**: Slow (exponential complexity)
- **Quality**: **Guaranteed optimal solution**
- **Best for**: Small problems (<12 variables), establishing baseline
- **Pi Performance**: Works well, 5-30 seconds for 10-12 variables
- **Limitation**: Only feasible for tiny problems

#### Simulated Annealing (IMPROVED)
- **Search Type**: Global search with adaptive cooling
- **Speed**: Fast to moderate (2-5 seconds on Pi)
- **Quality**: Near-optimal (typically <5% from optimal)
- **Best for**: **Production use**, medium-sized problems
- **Pi Optimized**: Default 2000 iterations (adjustable)
- **Recommendation**: **Primary algorithm for real-world use**

#### Genetic Algorithm (NEW)
- **Search Type**: Population-based evolutionary search
- **Speed**: Medium (5-15 seconds on Pi)
- **Quality**: Near-optimal with good diversity
- **Best for**: Alternative global search, exploring solution space
- **Pi Optimized**: Population 50, Generations 100
- **Recommendation**: Good alternative to Simulated Annealing

#### Greedy Heuristic
- **Search Type**: Local greedy decisions
- **Speed**: Very fast (<1 second)
- **Quality**: Good baseline (10-30% from optimal)
- **Best for**: Quick estimates, initial solutions, large problems
- **Pi Performance**: Instant results
- **Recommendation**: Use for rapid prototyping

#### QAOA (Quantum) - Educational Only
- **Search Type**: Quantum global search
- **Speed**: Very slow (30-120 seconds on Pi)
- **Quality**: Variable (often worse than classical)
- **Best for**: **Education, research, future readiness**
- **Pi Performance**: Slow due to simulation overhead
- **⚠️ Important**: Not recommended for production use

### Current State of Quantum Computing

**Critical Understanding:**

1. **Quantum Advantage Not Achieved**: Current quantum computers (NISQ era) cannot outperform classical algorithms for optimization problems
2. **Classical Superiority**: Simulated Annealing and Genetic Algorithms will consistently find better solutions faster
3. **Hardware Limitations**:
   - Limited qubit count and coherence time
   - High error rates requiring mitigation
   - Simulation overhead on classical hardware (like Raspberry Pi)
4. **Future Outlook**: Quantum advantage expected later this year for specific problem types (likely not routing/optimization)
5. **Educational Value**: QAOA demonstrates quantum concepts and prepares for future quantum computing

### When to Use Each Algorithm

**For Production/Real-World Use:**
- ✅ **First Choice**: Simulated Annealing (best balance of speed and quality)
- ✅ **Alternative**: Genetic Algorithm (good for exploring diverse solutions)
- ✅ **Quick Estimates**: Greedy Optimizer (instant results)
- ✅ **Small Problems**: Exact Solver (guaranteed optimal for <12 variables)

**For Research/Education:**
- 📚 **QAOA**: Understanding quantum algorithms
- 📚 **Benchmarking**: Comparing classical vs quantum approaches
- 📚 **Future Readiness**: Preparing for quantum advantage era

**NOT Recommended:**
- ❌ Using QAOA for production workloads
- ❌ Claiming quantum superiority with current hardware
- ❌ Using Exact Solver for problems >15 variables

## Performance Tips

1. **Problem Size**: QAOA works best with < 20 variables (shipments × trucks)
2. **For Larger Problems**: Use classical algorithms or problem decomposition
3. **Raspberry Pi Optimization**: Reduce QAOA reps to 2-3 for faster results
4. **Memory**: Close other applications when running quantum optimization

## Metrics Explained

### Cost Metrics
- **Transport Cost**: Base cost per km × distance
- **Fuel Cost**: Based on truck category and distance
- **Toll Cost**: Highway tolls
- **Driver Cost**: Time-based driver wages
- **Maintenance Cost**: Per-km maintenance

### CO₂ Metrics
- **Direct Emissions**: Based on truck type and load
- **Fuel Emissions**: Diesel combustion emissions
- **Traffic Impact**: Increased emissions in congestion
- **Total CO₂e**: Including other greenhouse gases

## Troubleshooting

### Qiskit Import Errors
```bash
pip install --upgrade qiskit qiskit-optimization qiskit-algorithms
```

### Memory Issues
- Reduce problem size
- Use classical algorithms
- Increase swap space

### No Feasible Solution
- Check truck capacities
- Verify lane availability
- Adjust deadlines

## Examples

See the `examples/` directory for:
- Basic usage examples
- API integration examples
- Custom objective functions
- Batch processing scripts

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

This project is part of the RasQberry project.
See the main RasQberry LICENSE file for details.

## Contact

For questions or support:
- RasQberry GitHub: https://github.com/JanLahmann/RasQberry-Two
- RasQberry Website: https://rasqberry.org

## Acknowledgments

- Built on Qiskit quantum computing framework
- Inspired by SAP Transportation Management
- Part of the RasQberry quantum education project

## Running Comprehensive Benchmarks

The project includes a comprehensive benchmarking suite to fairly compare all algorithms:

```python
from comparison.benchmark import BenchmarkSuite
from data_loader.csv_loader import CSVLoader

# Load data
loader = CSVLoader("../data/input")
data = loader.load_all()

# Create benchmark suite
benchmark = BenchmarkSuite(
    data['shipments'],
    data['trucks'],
    data['lanes']
)

# Run comprehensive comparison
results = benchmark.run_comprehensive_comparison(
    include_exact=True,      # Include exact solver if problem is small enough
    include_quantum=True,    # Include QAOA for comparison
    objective='balanced'
)

# Export results
benchmark.export_results('benchmark_results.json')
```

This will:
1. Run all available optimizers on the same problem
2. Compare against optimal solution (if problem is small enough)
3. Calculate optimality gaps for each algorithm
4. Generate detailed performance report
5. Provide recommendations based on results
