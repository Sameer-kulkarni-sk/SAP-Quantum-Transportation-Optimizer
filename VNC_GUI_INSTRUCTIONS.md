# How to View the Updated Application via VNC

## Current Status
✅ Application deployed to RasQBerry at **192.168.0.108**
✅ New dataset with **1000 shipments, 200 trucks, 1120 lanes** is loaded
✅ All algorithms working correctly
✅ GUI application is running

## Viewing the Application via VNC

### Step 1: Connect to VNC
1. Open **VNC Viewer** on your computer
2. Connect to: `192.168.0.108:5900` or `192.168.0.108`
3. Enter the VNC password when prompted

### Step 2: Launch the GUI Application

The GUI should already be running. If not, open a terminal on the RasQBerry desktop and run:

```bash
source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
python src/gui_main.py
```

### Step 3: Load the New Dataset

Once the GUI opens:

1. Click **"Load Data"** button
2. You should see:
   - ✓ Loaded **1000 shipments** (previously 5)
   - ✓ Loaded **200 trucks** (previously 4)
   - ✓ Loaded **1120 lanes** (previously 8)

### Step 4: Run Optimizations

Now you can test the algorithms with the large dataset:

1. **Greedy Optimizer**: Fast baseline (< 1 second)
2. **Simulated Annealing**: Better quality (1-2 seconds for 50 shipments)
3. **Genetic Algorithm**: Best quality (2-5 seconds for 50 shipments)

**Note**: The GUI will automatically use a subset of the data for reasonable performance:
- Small test: 50 shipments, 20 trucks
- Medium test: 100 shipments, 40 trucks
- Large test: 200 shipments, 80 trucks

### Step 5: View Results

After running an optimizer, you'll see:
- **Total Cost**: Optimized transportation cost
- **Shipments Assigned**: Number successfully assigned (should be 70-80%)
- **Trucks Used**: Number of trucks utilized
- **Computation Time**: How long the optimization took
- **Assignment Details**: List of shipment-truck-lane assignments

## What's Different from Before?

### Before (Old Dataset):
- Only 5 shipments, 4 trucks, 8 lanes
- Very limited testing capability
- Poor lane coverage (36% assignment rate)

### Now (New Dataset):
- 1000 shipments, 200 trucks, 1120 lanes
- Realistic large-scale testing
- Complete lane coverage (72-76% assignment rate)
- All shipment routes have matching lanes

## Command-Line Demo (Alternative)

If you prefer to see results in the terminal via SSH:

```bash
ssh rasqberry@192.168.0.108
source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer/src
python main.py --demo
```

This will run a comprehensive benchmark showing all algorithms with the new dataset.

## Troubleshooting

### GUI Not Showing?
```bash
# Check if GUI is running
ps aux | grep gui_main

# Kill old instance if needed
pkill -f gui_main.py

# Restart GUI
DISPLAY=:0 python src/gui_main.py
```

### VNC Not Connecting?
See [`VNC_TROUBLESHOOTING.md`](VNC_TROUBLESHOOTING.md) for detailed VNC connection help.

### Want to Generate Different Dataset?
```bash
# On your Mac, in the project directory:
python3 generate_large_dataset.py

# Then redeploy:
./DEPLOY.sh 192.168.0.108 rasqberry
```

## Performance Expectations on RasQBerry

With the new 1000-entry dataset:

| Problem Size | Greedy | Simulated Annealing | Genetic Algorithm |
|--------------|--------|---------------------|-------------------|
| 50 shipments | 0.01s  | 0.8s                | 0.9s              |
| 100 shipments| 0.03s  | 1.0s                | 2.0s              |
| 200 shipments| 0.05s  | 2.0s                | 5.0s              |

## Summary

The application is now fully functional with a realistic large-scale dataset. You should see:
- ✅ Much larger dataset (1000 vs 5 shipments)
- ✅ Better assignment rates (72-76% vs 36%)
- ✅ All algorithms working correctly
- ✅ Realistic optimization scenarios

Connect via VNC to `192.168.0.108` and click "Load Data" to see the improvements!