#!/bin/bash
# Start VNC with desktop environment

echo "Starting VNC desktop on RasQberry..."
echo "Password: Qiskit1!"

ssh -t rasqberry@100.67.33.252 << 'ENDSSH'
echo "Starting VNC Server in Virtual Mode..."
vncserver-virtual -geometry 1920x1080 -depth 24 :1

sleep 3

echo ""
echo "Starting desktop environment..."
export DISPLAY=:1
startlxde &

sleep 2

echo ""
echo "VNC Desktop started!"
echo "Connect with VNC Viewer to: 100.67.33.252:5901"
echo ""
ENDSSH

echo ""
echo "Done! Connect to VNC Viewer at 100.67.33.252:5901"