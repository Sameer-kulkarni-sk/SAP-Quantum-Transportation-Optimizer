# VNC Connection Troubleshooting for RasQberry

If you cannot connect to your RasQberry at 192.168.0.118 using RealVNC Viewer, follow these steps:

## Quick Diagnostics

### 1. Check if RasQberry is Reachable

```bash
# From your Mac terminal
ping 192.168.0.118
```

**If ping fails:**
- RasQberry may be off or not connected to network
- IP address may have changed
- Network issue

**If ping succeeds:**
- RasQberry is on the network
- Issue is with VNC service

### 2. Find RasQberry's Current IP Address

The IP may have changed. Try these methods:

#### Method A: Check your router's DHCP client list
- Log into your router (usually 192.168.0.1 or 192.168.1.1)
- Look for device named "rasqberry" or "raspberrypi"
- Note the IP address

#### Method B: Use network scanner
```bash
# Install nmap if needed
brew install nmap

# Scan your network
nmap -sn 192.168.0.0/24

# Look for Raspberry Pi devices
```

#### Method C: Connect via HDMI
- Connect RasQberry to a monitor
- Login (user: rasqberry, password: rasqberry)
- Run: `hostname -I`
- This shows the current IP address

## Common VNC Issues and Solutions

### Issue 1: VNC Server Not Running

SSH into RasQberry and check VNC status:

```bash
ssh rasqberry@192.168.0.118
# Password: rasqberry

# Check VNC status
sudo systemctl status vncserver-x11-serviced.service

# If not running, start it
sudo systemctl start vncserver-x11-serviced.service

# Enable on boot
sudo systemctl enable vncserver-x11-serviced.service
```

### Issue 2: VNC Not Enabled

Enable VNC through raspi-config:

```bash
ssh rasqberry@192.168.0.118

# Open configuration
sudo raspi-config

# Navigate to:
# 3. Interface Options
# → I3 VNC
# → Yes (Enable)
# → OK
# → Finish
# → Reboot? Yes
```

### Issue 3: Firewall Blocking VNC

```bash
ssh rasqberry@192.168.0.118

# Check if firewall is active
sudo ufw status

# If active, allow VNC
sudo ufw allow 5900/tcp

# Or disable firewall temporarily for testing
sudo ufw disable
```

### Issue 4: Wrong VNC Port

RealVNC typically uses port 5900. Try connecting with explicit port:

```
192.168.0.118:5900
```

Or try display numbers:
```
192.168.0.118:0
192.168.0.118:1
```

### Issue 5: VNC Authentication Issues

Reset VNC password:

```bash
ssh rasqberry@192.168.0.118

# Set VNC password
vncpasswd

# Restart VNC
sudo systemctl restart vncserver-x11-serviced.service
```

## Alternative: Use TightVNC Instead of RealVNC

If RealVNC doesn't work, try TightVNC:

### On RasQberry:
```bash
ssh rasqberry@192.168.0.118

# Install TightVNC server
sudo apt-get update
sudo apt-get install tightvncserver

# Start VNC server
vncserver :1 -geometry 1920x1080 -depth 24

# Set password when prompted
```

### On Your Mac:
```bash
# Install TightVNC Viewer
brew install --cask vnc-viewer

# Or download from: https://www.tightvnc.com/download.php

# Connect to:
192.168.0.118:5901
```

## Check VNC Service Logs

```bash
ssh rasqberry@192.168.0.118

# View VNC logs
sudo journalctl -u vncserver-x11-serviced.service -n 50

# Check for errors
```

## Verify Network Configuration

```bash
ssh rasqberry@192.168.0.118

# Check network interfaces
ip addr show

# Check if VNC is listening
sudo netstat -tulpn | grep vnc

# Or
sudo ss -tulpn | grep 5900
```

## Deploy Without VNC

You can still deploy and run the application without VNC:

### Option 1: SSH Only (Recommended)
```bash
# Deploy via SSH
./DEPLOY.sh 192.168.0.118 rasqberry

# Run via SSH
ssh rasqberry@192.168.0.118
source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer/src
python main.py --demo
```

### Option 2: Direct HDMI Connection
- Connect RasQberry to monitor via HDMI
- Connect keyboard and mouse
- Login and run application directly

## Quick Fix Checklist

Try these in order:

1. ✅ **Verify IP address hasn't changed**
   ```bash
   ping 192.168.0.118
   ```

2. ✅ **Try SSH first** (easier to troubleshoot)
   ```bash
   ssh rasqberry@192.168.0.118
   ```

3. ✅ **Check VNC service**
   ```bash
   ssh rasqberry@192.168.0.118
   sudo systemctl status vncserver-x11-serviced.service
   ```

4. ✅ **Restart VNC service**
   ```bash
   sudo systemctl restart vncserver-x11-serviced.service
   ```

5. ✅ **Enable VNC in raspi-config**
   ```bash
   sudo raspi-config
   # Interface Options → VNC → Enable
   ```

6. ✅ **Reboot RasQberry**
   ```bash
   sudo reboot
   ```

7. ✅ **Try different VNC client**
   - RealVNC Viewer
   - TightVNC Viewer
   - Built-in macOS Screen Sharing (vnc://192.168.0.118)

## For RasQberry-Specific Issues

RasQberry may have custom VNC configuration. Check:

```bash
ssh rasqberry@192.168.0.118

# Check RasQberry-specific services
systemctl list-units | grep vnc
systemctl list-units | grep rasq

# Check RasQberry documentation
ls -la /home/rasqberry/RasQberry-Two/
cat /home/rasqberry/RasQberry-Two/README.md
```

## Still Not Working?

### Get Help:
1. **RasQberry Community**: https://rasqberry.org
2. **Check RasQberry GitHub**: https://github.com/JanLahmann/RasQberry-Two
3. **Raspberry Pi Forums**: https://forums.raspberrypi.com/

### Provide This Info When Asking for Help:
```bash
ssh rasqberry@192.168.0.118

# Gather diagnostic info
echo "=== System Info ==="
uname -a
cat /etc/os-release

echo "=== Network Info ==="
hostname -I
ip addr show

echo "=== VNC Status ==="
sudo systemctl status vncserver-x11-serviced.service

echo "=== Listening Ports ==="
sudo netstat -tulpn | grep 5900

echo "=== VNC Logs ==="
sudo journalctl -u vncserver-x11-serviced.service -n 20
```

## Deploy Application Anyway

**Good news**: You don't need VNC to deploy and test the application!

```bash
# Deploy via SSH (works without VNC)
./DEPLOY.sh 192.168.0.118 rasqberry

# Test via SSH
ssh rasqberry@192.168.0.118
source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer/src
python main.py --demo
```

The application will run and show results in the terminal. VNC is only needed for the GUI version.