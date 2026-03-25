# Touchscreen Setup Guide for RasQberry

## Complete Deployment and Setup for Raspberry Pi Touch Display 2

### Step 1: Deploy Application to RasQberry

From your local machine:

```bash
cd examples/quantum_transport_optimizer
./DEPLOY.sh 192.168.0.118 rasqberry
```

Or manually:
```bash
cd examples/quantum_transport_optimizer
tar -czf quantum_transport.tar.gz .
scp quantum_transport.tar.gz rasqberry@192.168.0.118:/tmp/

ssh rasqberry@192.168.0.118
mkdir -p /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
tar -xzf /tmp/quantum_transport.tar.gz
chmod +x src/gui_main.py src/main.py create_icon.py
```

### Step 2: Install Dependencies on RasQberry

```bash
ssh rasqberry@192.168.0.118

# Activate RQB2 environment
source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate

# Navigate to app directory
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer

# Install Python dependencies
pip install pillow  # For icon creation
pip install qiskit-optimization qiskit-algorithms  # For quantum optimization
```

### Step 3: Create Application Icon

```bash
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
python create_icon.py
```

This creates:
- `icon.png` (256x256) - Main icon
- `icon_128.png` (128x128)
- `icon_64.png` (64x64)
- `icon_32.png` (32x32)

### Step 4: Install Desktop Icon

```bash
# Copy desktop file to applications
mkdir -p ~/.local/share/applications
cp quantum_transport.desktop ~/.local/share/applications/

# Make it executable
chmod +x ~/.local/share/applications/quantum_transport.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications/
```

### Step 5: Test the GUI

```bash
# Activate environment
source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate

# Run GUI
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer/src
python gui_main.py
```

### Step 6: Configure Touchscreen (If Needed)

#### For Official Raspberry Pi Touch Display 2

The display should work automatically. If not:

```bash
# Check display configuration
cat /boot/config.txt | grep display

# Should show:
# dtoverlay=vc4-kms-v3d
# dtoverlay=vc4-kms-dsi-7inch  # for 7" display
```

#### Calibrate Touch (If Needed)

```bash
sudo apt-get install xinput-calibrator
xinput_calibrator
```

Follow on-screen instructions and save calibration.

### Step 7: Auto-Start on Boot (Optional)

To launch the app automatically when RasQberry starts:

```bash
# Create autostart directory
mkdir -p ~/.config/autostart

# Copy desktop file
cp ~/.local/share/applications/quantum_transport.desktop ~/.config/autostart/

# Or create custom autostart script
cat > ~/.config/autostart/quantum_transport.sh << 'EOF'
#!/bin/bash
sleep 10  # Wait for system to fully boot
source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer/src
python gui_main.py &
EOF

chmod +x ~/.config/autostart/quantum_transport.sh
```

## GUI Features

### Main Screen Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🔷 Quantum Transport Optimizer                             │
│  SAP TM Integration • RasQberry Edition          12:34:56   │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│  📂 Load     │         Results Display Area                │
│   Data       │                                              │
│              │  - Algorithm outputs                         │
│  ⚡ Greedy   │  - Cost and CO₂ metrics                     │
│              │  - Comparison tables                         │
│  🔄 Local    │  - Assignment details                        │
│   Search     │                                              │
│              │                                              │
│  ⚛️ QAOA     │                                              │
│   Quantum    │                                              │
│              │                                              │
│  📊 Compare  │                                              │
│   All        │                                              │
│              │                                              │
│  🗑️ Clear    │                                              │
│   Results    │                                              │
│              │                                              │
├──────────────┴──────────────────────────────────────────────┤
│  Status: Ready                                    [Exit]    │
└─────────────────────────────────────────────────────────────┘
```

### Touch Controls

- **Large Buttons**: Optimized for finger touch (minimum 60x60 pixels)
- **Clear Labels**: High contrast text with icons
- **Scrollable Results**: Touch and drag to scroll
- **Status Updates**: Real-time feedback on operations

### Color Scheme (SAP-Inspired)

- **Primary Blue**: #003366 (SAP Blue)
- **Accent Gold**: #F0AB00 (SAP Gold)
- **Success Green**: #00A65A
- **Error Red**: #E52929
- **Background**: White/Light Gray

## Usage Instructions

### 1. Load Data
Touch "📂 Load Data" to load sample shipments, trucks, and lanes from CSV files.

### 2. Run Optimizers
Touch any optimizer button:
- **⚡ Greedy**: Fast baseline (< 1 second)
- **🔄 Local Search**: Improved solution (1-10 seconds)
- **⚛️ QAOA Quantum**: Quantum optimization (10-60 seconds)

### 3. View Results
Results appear in the right panel showing:
- Total cost (€)
- Total CO₂ emissions (kg)
- Computation time
- Trucks used
- Shipment assignments

### 4. Compare Algorithms
After running multiple algorithms, touch "📊 Compare All" to see side-by-side comparison.

### 5. Clear Results
Touch "🗑️ Clear Results" to start fresh.

## Troubleshooting

### GUI Doesn't Start

```bash
# Check if tkinter is installed
python -c "import tkinter; print('OK')"

# If not, install:
sudo apt-get install python3-tk
```

### Display Issues

```bash
# Check display resolution
xrandr

# For 800x480 display, the GUI is optimized
# For 1024x600, it will auto-adjust
```

### Touch Not Working

```bash
# Check touch device
xinput list

# Test touch
evtest
# Select your touch device and test
```

### Performance Issues

```bash
# Reduce QAOA complexity in gui_main.py:
# Change qaoa_reps=2 to qaoa_reps=1
# Change max_iter=50 to max_iter=25

# Or disable quantum optimizer for faster operation
```

### Icon Not Showing

```bash
# Regenerate icon
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
python create_icon.py

# Update desktop database
update-desktop-database ~/.local/share/applications/
```

## Customization

### Change Window Size

Edit `gui_main.py`, line ~30:
```python
self.root.geometry("800x480")  # Change to your display size
```

### Enable Fullscreen

Edit `gui_main.py`, line ~33:
```python
self.root.attributes('-fullscreen', True)  # Uncomment this line
```

### Adjust Button Sizes

Edit `gui_main.py`, button creation section:
```python
height=2  # Change button height
font=('Arial', 12, 'bold')  # Change font size
```

### Modify Colors

Edit `gui_main.py`, `setup_styles()` method to change color scheme.

## Advanced Features

### Remote Access

Access the GUI remotely via VNC:
```bash
# On RasQberry, enable VNC
sudo raspi-config
# Interface Options -> VNC -> Enable

# From your computer:
vncviewer 192.168.0.118
```

### Screen Rotation

```bash
# Rotate display 180 degrees
sudo nano /boot/config.txt
# Add: display_rotate=2

# Reboot
sudo reboot
```

### Brightness Control

```bash
# Adjust backlight (0-255)
echo 200 | sudo tee /sys/class/backlight/*/brightness
```

## Performance Tips

1. **Close Other Applications**: Free up memory
2. **Use Greedy First**: Get quick baseline results
3. **Reduce Problem Size**: Fewer shipments = faster quantum optimization
4. **Monitor Temperature**: `vcgencmd measure_temp`
5. **Increase Swap**: If memory issues occur

## Support

For issues:
- Check logs: `~/.local/share/quantum_transport/logs/`
- Test CLI version: `python main.py --demo`
- Verify data files: `ls data/input/`

## Next Steps

1. **Add Your Data**: Replace CSV files in `data/input/`
2. **Integrate SAP TM**: Configure REST API in settings
3. **Customize UI**: Modify colors, layout, button sizes
4. **Add Charts**: Integrate matplotlib for visual comparisons
5. **LED Display**: Add LED matrix visualization

Enjoy your Quantum Transport Optimizer on RasQberry! 🚀