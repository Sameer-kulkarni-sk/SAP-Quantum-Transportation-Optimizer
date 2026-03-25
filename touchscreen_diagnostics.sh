#!/bin/bash
echo "=========================================="
echo "RasQberry Touchscreen Diagnostics"
echo "=========================================="
echo ""

echo "1. Checking Display Detection..."
echo "-----------------------------------"
if command -v tvservice &> /dev/null; then
    tvservice -l
    tvservice -s
else
    echo "tvservice not available, checking alternative methods..."
fi
echo ""

echo "2. Checking /boot/config.txt for Display Settings..."
echo "-----------------------------------"
if [ -f /boot/config.txt ]; then
    grep -E "display|dtoverlay|hdmi" /boot/config.txt | grep -v "^#"
elif [ -f /boot/firmware/config.txt ]; then
    grep -E "display|dtoverlay|hdmi" /boot/firmware/config.txt | grep -v "^#"
else
    echo "Config file not found in expected locations"
fi
echo ""

echo "3. Checking Display Output (xrandr)..."
echo "-----------------------------------"
if command -v xrandr &> /dev/null; then
    DISPLAY=:0 xrandr 2>&1 || echo "xrandr failed - X server may not be running"
else
    echo "xrandr not installed"
fi
echo ""

echo "4. Checking Touch Input Devices..."
echo "-----------------------------------"
if command -v xinput &> /dev/null; then
    DISPLAY=:0 xinput list 2>&1 || echo "xinput failed - X server may not be running"
else
    echo "xinput not installed"
fi
echo ""

echo "5. Checking /dev/input devices..."
echo "-----------------------------------"
ls -la /dev/input/ 2>&1
echo ""

echo "6. Checking for Touch Events..."
echo "-----------------------------------"
if [ -d /dev/input/by-path ]; then
    ls -la /dev/input/by-path/ | grep -i touch
else
    echo "No /dev/input/by-path directory"
fi
echo ""

echo "7. Checking X Server Status..."
echo "-----------------------------------"
ps aux | grep -E "X|xinit|startx" | grep -v grep
echo ""

echo "8. Checking DISPLAY Environment..."
echo "-----------------------------------"
echo "DISPLAY=$DISPLAY"
who
echo ""

echo "9. Checking dmesg for Display/Touch Messages..."
echo "-----------------------------------"
dmesg | grep -iE "display|touch|dsi|hdmi|fb0" | tail -20
echo ""

echo "10. Checking Framebuffer Devices..."
echo "-----------------------------------"
ls -la /dev/fb* 2>&1
echo ""

echo "11. Testing Python tkinter..."
echo "-----------------------------------"
python3 -c "import tkinter; print('tkinter: OK')" 2>&1 || echo "tkinter: FAILED"
echo ""

echo "12. Checking System Info..."
echo "-----------------------------------"
uname -a
cat /proc/device-tree/model 2>&1 || echo "Model info not available"
echo ""

echo "=========================================="
echo "Diagnostics Complete"
echo "=========================================="
