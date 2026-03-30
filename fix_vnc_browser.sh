#!/bin/bash
# Fix VNC browser issue on RasQberry

echo "Connecting to RasQberry to fix VNC browser issue..."
echo "Password: Qiskit1!"

ssh -t rasqberry@100.67.33.252 << 'ENDSSH'
echo "Killing browser processes..."
pkill -9 chromium-browser 2>/dev/null
pkill -9 chromium 2>/dev/null
pkill -9 firefox 2>/dev/null
pkill -9 epiphany 2>/dev/null

echo "Checking running processes..."
ps aux | grep -i "chrom\|firefox\|browser" | grep -v grep

echo ""
echo "Restarting VNC server..."
vncserver -kill :1 2>/dev/null
sleep 2
vncserver :1 -geometry 1920x1080 -depth 24

echo ""
echo "VNC server restarted. Try reconnecting with VNC viewer."
echo ""
echo "If desktop still doesn't show, try:"
echo "  DISPLAY=:1 startlxde &"
echo ""
ENDSSH

echo ""
echo "Done! Reconnect to VNC viewer now."