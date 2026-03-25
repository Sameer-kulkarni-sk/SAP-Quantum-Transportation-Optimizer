#!/bin/bash
# RasQberry Connection Diagnostic Script
# Run this from your Mac to diagnose connection issues

echo "========================================================================"
echo "  RasQberry Connection Diagnostics"
echo "========================================================================"
echo ""

RASQBERRY_IP="${1:-192.168.0.108}"
RASQBERRY_USER="rasqberry"

echo "Testing connection to: ${RASQBERRY_IP}"
echo ""

# Test 1: Ping
echo "Test 1: Network Reachability (ping)"
echo "------------------------------------"
if ping -c 3 -W 2 ${RASQBERRY_IP} > /dev/null 2>&1; then
    echo "✅ SUCCESS: RasQberry is reachable on the network"
    PING_OK=true
else
    echo "❌ FAILED: Cannot reach RasQberry at ${RASQBERRY_IP}"
    echo ""
    echo "Possible causes:"
    echo "  1. RasQberry is powered off"
    echo "  2. RasQberry is not connected to network"
    echo "  3. IP address has changed"
    echo "  4. Network issue"
    echo ""
    echo "Solutions:"
    echo "  - Check if RasQberry is powered on (look for LED lights)"
    echo "  - Check network cable or WiFi connection"
    echo "  - Try scanning for the device: nmap -sn 192.168.0.0/24"
    echo "  - Connect RasQberry to monitor via HDMI and run: hostname -I"
    PING_OK=false
fi
echo ""

if [ "$PING_OK" = false ]; then
    echo "Cannot proceed with further tests. Fix network connectivity first."
    exit 1
fi

# Test 2: SSH Port
echo "Test 2: SSH Port (22)"
echo "------------------------------------"
if nc -z -w 2 ${RASQBERRY_IP} 22 2>/dev/null; then
    echo "✅ SUCCESS: SSH port 22 is open"
    SSH_PORT_OK=true
else
    echo "❌ FAILED: SSH port 22 is not accessible"
    echo ""
    echo "Possible causes:"
    echo "  1. SSH service not running"
    echo "  2. Firewall blocking port 22"
    echo ""
    echo "Solutions:"
    echo "  - Connect via HDMI and run: sudo systemctl start ssh"
    echo "  - Enable SSH: sudo raspi-config → Interface Options → SSH → Enable"
    SSH_PORT_OK=false
fi
echo ""

# Test 3: SSH Connection
if [ "$SSH_PORT_OK" = true ]; then
    echo "Test 3: SSH Authentication"
    echo "------------------------------------"
    echo "Attempting SSH connection (you may be prompted for password)..."
    echo "Default password is usually: rasqberry"
    echo ""
    
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ${RASQBERRY_USER}@${RASQBERRY_IP} "echo 'SSH connection successful'" 2>/dev/null; then
        echo "✅ SUCCESS: SSH connection works"
        SSH_OK=true
    else
        echo "❌ FAILED: Cannot authenticate via SSH"
        echo ""
        echo "Possible causes:"
        echo "  1. Wrong username (try: pi or rasqberry)"
        echo "  2. Wrong password"
        echo "  3. SSH keys not set up"
        echo ""
        echo "Solutions:"
        echo "  - Try manual SSH: ssh ${RASQBERRY_USER}@${RASQBERRY_IP}"
        echo "  - Default password: rasqberry"
        echo "  - Reset password via HDMI connection"
        SSH_OK=false
    fi
    echo ""
fi

# Test 4: VNC Port
echo "Test 4: VNC Port (5900)"
echo "------------------------------------"
if nc -z -w 2 ${RASQBERRY_IP} 5900 2>/dev/null; then
    echo "✅ SUCCESS: VNC port 5900 is open"
    VNC_PORT_OK=true
else
    echo "❌ FAILED: VNC port 5900 is not accessible"
    echo ""
    echo "This is why VNC Viewer cannot connect!"
    echo ""
    echo "Possible causes:"
    echo "  1. VNC server not running"
    echo "  2. VNC not enabled in raspi-config"
    echo "  3. Firewall blocking port 5900"
    echo ""
    echo "Solutions (via SSH):"
    echo "  ssh ${RASQBERRY_USER}@${RASQBERRY_IP}"
    echo "  sudo raspi-config"
    echo "  → Interface Options → VNC → Enable"
    echo "  sudo systemctl start vncserver-x11-serviced"
    echo "  sudo systemctl enable vncserver-x11-serviced"
    VNC_PORT_OK=false
fi
echo ""

# Test 5: Get detailed info via SSH
if [ "$SSH_OK" = true ]; then
    echo "Test 5: Gathering System Information"
    echo "------------------------------------"
    echo "Connecting via SSH to gather diagnostics..."
    echo ""
    
    ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ${RASQBERRY_USER}@${RASQBERRY_IP} << 'ENDSSH'
        echo "Current IP addresses:"
        hostname -I
        echo ""
        
        echo "VNC Service Status:"
        sudo systemctl status vncserver-x11-serviced.service --no-pager | head -10
        echo ""
        
        echo "Listening ports:"
        sudo netstat -tulpn | grep -E ':(22|5900)' || echo "No SSH/VNC ports found listening"
        echo ""
        
        echo "RasQberry installation:"
        if [ -d "/home/rasqberry/RasQberry-Two" ]; then
            echo "✅ RasQberry-Two directory exists"
        else
            echo "❌ RasQberry-Two directory not found"
        fi
ENDSSH
    echo ""
fi

# Summary
echo "========================================================================"
echo "  DIAGNOSTIC SUMMARY"
echo "========================================================================"
echo ""

if [ "$PING_OK" = true ]; then
    echo "✅ Network: Reachable"
else
    echo "❌ Network: NOT reachable"
fi

if [ "$SSH_PORT_OK" = true ]; then
    echo "✅ SSH Port: Open"
else
    echo "❌ SSH Port: Closed"
fi

if [ "$SSH_OK" = true ]; then
    echo "✅ SSH Auth: Working"
else
    echo "❌ SSH Auth: Failed"
fi

if [ "$VNC_PORT_OK" = true ]; then
    echo "✅ VNC Port: Open"
else
    echo "❌ VNC Port: Closed (THIS IS YOUR VNC ISSUE)"
fi

echo ""
echo "========================================================================"
echo "  RECOMMENDED ACTIONS"
echo "========================================================================"
echo ""

if [ "$PING_OK" = false ]; then
    echo "1. Fix network connectivity first:"
    echo "   - Power on RasQberry"
    echo "   - Check network cable or WiFi"
    echo "   - Verify IP address hasn't changed"
    echo ""
fi

if [ "$SSH_OK" = false ] && [ "$SSH_PORT_OK" = true ]; then
    echo "2. Fix SSH authentication:"
    echo "   ssh ${RASQBERRY_USER}@${RASQBERRY_IP}"
    echo "   (Try password: rasqberry)"
    echo ""
fi

if [ "$VNC_PORT_OK" = false ] && [ "$SSH_OK" = true ]; then
    echo "3. Enable and start VNC service:"
    echo "   ssh ${RASQBERRY_USER}@${RASQBERRY_IP}"
    echo "   sudo raspi-config"
    echo "   → Interface Options → VNC → Enable → Reboot"
    echo ""
    echo "   Or manually:"
    echo "   sudo systemctl enable vncserver-x11-serviced"
    echo "   sudo systemctl start vncserver-x11-serviced"
    echo ""
fi

if [ "$SSH_OK" = true ]; then
    echo "4. Deploy application (SSH works, VNC not required):"
    echo "   ./DEPLOY.sh ${RASQBERRY_IP} ${RASQBERRY_USER}"
    echo ""
fi

echo "For detailed VNC troubleshooting, see: VNC_TROUBLESHOOTING.md"
echo ""