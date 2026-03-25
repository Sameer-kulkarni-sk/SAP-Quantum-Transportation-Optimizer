#!/bin/bash
# Quick Fix Script for Waveshare Touchscreen on RasQberry
# This script rotates the display and maps touch input correctly

echo "=========================================="
echo "Touchscreen Quick Fix for RasQberry"
echo "=========================================="
echo ""

# Check if we're running on the Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "Error: This script must be run on the Raspberry Pi"
    exit 1
fi

echo "Step 1: Rotating display to landscape mode..."
DISPLAY=:0 xrandr --output XWAYLAND0 --rotate left
if [ $? -eq 0 ]; then
    echo "✓ Display rotated successfully"
else
    echo "✗ Failed to rotate display"
    echo "  Trying alternative method..."
    DISPLAY=:0 xrandr --output XWAYLAND0 --rotate right
fi
echo ""

echo "Step 2: Mapping touch input to display..."
DISPLAY=:0 xinput map-to-output "Waveshare  Waveshare -079-HD" XWAYLAND0
if [ $? -eq 0 ]; then
    echo "✓ Touch input mapped successfully"
else
    echo "✗ Failed to map touch input"
    echo "  You may need to calibrate manually"
fi
echo ""

echo "Step 3: Checking current display configuration..."
DISPLAY=:0 xrandr | grep -A 1 "XWAYLAND0"
echo ""

echo "Step 4: Listing touch input devices..."
DISPLAY=:0 xinput list | grep -i waveshare
echo ""

echo "=========================================="
echo "Quick Fix Complete!"
echo "=========================================="
echo ""
echo "Your touchscreen should now be working in landscape mode."
echo ""
echo "To test, try running:"
echo "  cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer/src"
echo "  source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate"
echo "  DISPLAY=:0 python gui_main.py"
echo ""
echo "To make these changes permanent, see TOUCHSCREEN_DIAGNOSIS_RESULTS.md"
echo ""