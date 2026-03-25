# SSH Connection Troubleshooting for RasQBerry (192.168.0.118)

## Problem
SSH connection to `192.168.0.118` hangs and ping requests timeout, indicating the Raspberry Pi is not reachable on the network.

## Possible Causes & Solutions

### 1. **Raspberry Pi is Not Powered On or Booted**
- **Check**: Verify the Raspberry Pi has power and status LEDs are lit
- **Action**: Power cycle the device (unplug, wait 10 seconds, plug back in)
- **Wait**: Allow 1-2 minutes for full boot

### 2. **Wrong IP Address**
The IP address may have changed if using DHCP.

**Find the correct IP:**

```bash
# Option A: Scan your local network (requires nmap)
nmap -sn 192.168.0.0/24

# Option B: Check your router's DHCP client list
# Access your router's admin panel (usually 192.168.0.1 or 192.168.1.1)
# Look for "Connected Devices" or "DHCP Clients"

# Option C: If you have physical access, connect monitor/keyboard
# On the Pi, run: hostname -I
```

### 3. **Network Configuration Issues**

**Check if Pi is on the same network:**
- Verify your computer's IP: `ifconfig | grep "inet "` (macOS/Linux)
- Your computer should be on 192.168.0.x network
- If you're on a different subnet (e.g., 192.168.1.x), you won't reach the Pi

**If on different networks:**
- Connect to the same WiFi/network as the Raspberry Pi
- Or configure network bridging

### 4. **Firewall Blocking Connection**

**On your Mac:**
```bash
# Check if firewall is blocking outgoing SSH
sudo pfctl -s rules | grep ssh

# Temporarily disable firewall to test (re-enable after!)
sudo pfctl -d
```

**On Raspberry Pi** (if you can access it):
```bash
# Check if SSH service is running
sudo systemctl status ssh

# Enable and start SSH if needed
sudo systemctl enable ssh
sudo systemctl start ssh
```

### 5. **SSH Service Not Running on Pi**

If you have physical access to the Pi:
```bash
# Enable SSH
sudo systemctl enable ssh
sudo systemctl start ssh

# Or create empty 'ssh' file in boot partition
sudo touch /boot/ssh
```

### 6. **Network Cable/WiFi Issues**
- **Ethernet**: Check cable is securely connected, try different cable
- **WiFi**: Verify WiFi credentials are correct, signal strength is adequate

## Quick Diagnostic Steps

### Step 1: Verify Network Connectivity
```bash
# Check if ANY device responds on that network
ping -c 3 192.168.0.1  # Usually the router

# Scan for the Pi (requires nmap: brew install nmap)
nmap -sn 192.168.0.0/24 | grep -B 2 "Raspberry"
```

### Step 2: Check ARP Cache
```bash
# See if your Mac has seen the Pi recently
arp -a | grep 192.168.0.118
```

### Step 3: Try Different Connection Methods
```bash
# Try with verbose output to see where it hangs
ssh -vvv rasqberry@192.168.0.118

# Try with different timeout
ssh -o ConnectTimeout=10 rasqberry@192.168.0.118
```

### Step 4: Physical Access Required
If none of the above works, you'll need physical access to:
1. Connect monitor and keyboard to the Pi
2. Check network configuration: `ip addr show`
3. Check SSH status: `sudo systemctl status ssh`
4. Check WiFi connection: `iwconfig` or `nmcli device status`

## Common Solutions

### Solution 1: Static IP Assignment
To prevent IP changes, assign a static IP on your router:
1. Access router admin panel
2. Find MAC address of Raspberry Pi
3. Assign static IP (e.g., 192.168.0.118)

### Solution 2: Use Hostname Instead
If mDNS/Bonjour is working:
```bash
# Try connecting via hostname
ssh rasqberry@rasqberry.local

# Or
ping rasqberry.local
```

### Solution 3: Check Router Settings
- Ensure AP Isolation is disabled (prevents devices from seeing each other)
- Check if MAC filtering is enabled
- Verify DHCP is working properly

## Emergency Access

If you can't SSH but need to access the Pi:

1. **Remove SD card**, mount on your computer, edit `/boot/wpa_supplicant.conf` for WiFi
2. **Connect monitor/keyboard** directly to Pi
3. **Use serial console** if you have a USB-to-TTL adapter

## Next Steps

1. **Verify Pi is powered on** and booted (check LEDs)
2. **Check your router** for connected devices to find current IP
3. **Try hostname**: `ssh rasqberry@rasqberry.local`
4. **Scan network**: `nmap -sn 192.168.0.0/24`
5. **Physical access**: Connect monitor/keyboard if all else fails

## Testing After Fix

Once you identify the correct IP or fix the issue:

```bash
# Test connection
ping -c 3 <correct-ip>

# Test SSH with verbose output
ssh -v rasqberry@<correct-ip>

# If successful, update your deployment scripts with correct IP
```

## Update Deployment Scripts

After finding the correct IP, update these files:
- `DEPLOY_TO_RASQBERRY.md`
- `DEPLOY.sh`
- `FINAL_DEPLOY.sh`
- `diagnose_connection.sh`

Replace `192.168.0.118` with the correct IP address.