# Quick Start Guide - Quantum Transport Optimizer on RasQberry

## For RasQberry Device (rasqberry@192.168.0.118)

### Step 1: Connect to Your RasQberry

```bash
ssh rasqberry@192.168.0.118
# Password: (your RasQberry password)
```

### Step 2: Navigate to the Application

```bash
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
```

### Step 3: Activate RQB2 Virtual Environment

```bash
source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate
```

You should see `(RQB2)` in your prompt.

### Step 4: Install Required Packages

```bash
pip install qiskit-optimization qiskit-algorithms
```

### Step 5: Run the Demo

```bash
cd src
python main.py --demo
```

This will:
- Load sample data from CSV files
- Run Greedy optimizer
- Run Local Search optimizer
- Run QAOA quantum optimizer (if problem size allows)
- Display comparison results

### Step 6: Interactive Mode

For interactive mode with menu:

```bash
python main.py
```

Then follow the on-screen menu:
1. Load Data from CSV
2. Run Greedy Optimizer
3. Run Local Search Optimizer
4. Run QAOA Quantum Optimizer
5. Compare All Algorithms
0. Exit

## Using Your Own Data

### Option 1: Edit CSV Files

Edit the files in `data/input/`:
- `shipments.csv` - Your shipment data
- `trucks.csv` - Your truck fleet
- `lanes.csv` - Available routes

### Option 2: Use REST API

```python
from data_loader.rest_loader import RESTLoader

loader = RESTLoader(
    base_url="https://your-sap-tm-api.com/api",
    api_key="your_api_key"
)
data = loader.load_all()
```

## Touchscreen Display Support

### For 7" or 10" Official RasQberry Touchscreen

The touchscreen should be auto-detected. If you have display issues:

```bash
# Check display configuration
cat /boot/config.txt | grep display

# The display should show:
# dtoverlay=vc4-kms-v3d
# dtoverlay=vc4-kms-dsi-7inch (for 7" display)
```

### Running with Touchscreen GUI (Coming Soon)

```bash
python src/gui_main.py
```

This will launch a touch-friendly interface with:
- Large buttons for easy touch control
- Real-time optimization progress
- Visual comparison charts
- Interactive result exploration

## Performance Tips for Raspberry Pi

### 1. Reduce QAOA Complexity

For faster results on Raspberry Pi:

```python
qaoa = QAOAOptimizer(
    shipments, trucks, lanes,
    qaoa_reps=2,      # Reduce from 3 to 2
    max_iter=50       # Reduce from 100 to 50
)
```

### 2. Use Classical Algorithms for Large Problems

If you have more than 5 shipments and 4 trucks (20 variables):

```python
# Use Greedy for quick results
greedy = GreedyOptimizer(shipments, trucks, lanes)
result = greedy.optimize(objective='balanced')

# Or Local Search for better quality
local_search = LocalSearchOptimizer(shipments, trucks, lanes)
result = local_search.optimize(max_iterations=500)
```

### 3. Monitor System Resources

```bash
# Check CPU and memory usage
htop

# Check temperature
vcgencmd measure_temp
```

## Example Output

```
======================================================================
                   QUANTUM TRANSPORT OPTIMIZER
                        for RasQberry
======================================================================
Date: 2026-01-15 12:30:45
======================================================================

Loading data from CSV files...

✓ Loaded 5 shipments
✓ Loaded 4 trucks
✓ Loaded 8 lanes

======================================================================
Running Greedy Optimizer...
======================================================================

======================================================================
RESULTS: Greedy (balanced)
======================================================================
Total Cost:           €4,235.60
Total CO₂:            2,845.30 kg
Computation Time:     0.023 seconds
Trucks Used:          3
Shipments Assigned:   5
Shipments Unassigned: 0

Assignments:
Shipment     Truck      Lane       Cost (€)     CO₂ (kg)  
----------------------------------------------------------------------
SH001        TR001      LN001      856.20       584.80    
SH002        TR002      LN002      742.50       591.60    
...

======================================================================
ALGORITHM COMPARISON
======================================================================
Algorithm                      Cost (€)        CO₂ (kg)        Time (s)    
----------------------------------------------------------------------
Greedy (balanced)              4,235.60        2,845.30        0.023       
Local Search (Simulated Annealing) 4,102.30    2,756.80        2.145       
QAOA (p=2)                     4,089.50        2,748.20        15.678      
----------------------------------------------------------------------

✓ Best Cost:    QAOA (p=2) (€4,089.50)
✓ Best CO₂:     QAOA (p=2) (2,748.20 kg)
✓ Fastest:      Greedy (balanced) (0.023s)

QAOA (p=2) vs Greedy (balanced):
  Cost Improvement: +3.45%
  CO₂ Improvement:  +3.41%

✓ Demo completed successfully!
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'qiskit_optimization'"

**Solution:**
```bash
source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate
pip install qiskit-optimization qiskit-algorithms
```

### Issue: "Memory Error" or System Freezes

**Solution:**
- Reduce problem size (fewer shipments/trucks)
- Use classical algorithms only
- Increase swap space:
```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Issue: No Feasible Solution Found

**Solution:**
- Check truck capacities are sufficient
- Verify lanes exist for all routes
- Adjust shipment deadlines
- Add more trucks or increase capacities

### Issue: QAOA Takes Too Long

**Solution:**
- Reduce `qaoa_reps` to 1 or 2
- Reduce `max_iter` to 25-50
- Use `optimize_with_fallback()` method
- Consider classical algorithms for large problems

## Next Steps

1. **Customize for Your Use Case**
   - Modify data models in `src/models/`
   - Adjust cost factors in configuration
   - Add custom constraints

2. **Integrate with SAP TM**
   - Implement REST API connector
   - Map SAP TM data structures
   - Add authentication

3. **Enhance Visualization**
   - Add LED matrix display
   - Create touchscreen GUI
   - Export results to dashboard

4. **Optimize Performance**
   - Profile code for bottlenecks
   - Implement caching
   - Use problem decomposition

## Support

For issues or questions:
- Check the main README.md
- Visit: https://rasqberry.org
- GitHub: https://github.com/JanLahmann/RasQberry-Two

## License

Part of the RasQberry project. See LICENSE file.