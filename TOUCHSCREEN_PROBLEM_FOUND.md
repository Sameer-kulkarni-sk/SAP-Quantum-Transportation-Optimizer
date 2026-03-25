# 🔴 TOUCHSCREEN PROBLEM IDENTIFIED

## Critical Issue: USB Touch Device Constantly Disconnecting

**Date:** February 24, 2026  
**Status:** ⚠️ **HARDWARE PROBLEM FOUND**

---

## 🔍 Root Cause

Your Waveshare touchscreen's **USB touch interface is disconnecting and reconnecting every 4 seconds**.

### Evidence from System Logs:
```
[    8.220955] usb 3-1: new full-speed USB device
[   12.407809] usb 3-1: USB disconnect, device number 4
[   12.712973] usb 3-1: new full-speed USB device number 5
[   16.900984] usb 3-1: USB disconnect, device number 5
[   17.212959] usb 3-1: new full-speed USB device number 6
[   21.389520] usb 3-1: USB disconnect, device number 6
... (pattern continues)
```

**This explains why:**
- ✅ Display works (video signal is separate)
- ✅ Touch device is detected
- ❌ Touch doesn't respond (device keeps disconnecting)

---

## 🔧 Solutions (Try in Order)

### Solution 1: Check Power Supply (MOST LIKELY)

**Raspberry Pi 5 requires 5V 3A (15W) minimum**

```bash
# Check if system is being throttled
ssh rasqberry@192.168.0.108
vcgencmd get_throttled
```

**If output shows anything other than `0x0`:**
- Your power supply is insufficient
- **Action:** Use official Raspberry Pi 5 power supply (27W recommended)

### Solution 2: Check USB Cable

**The USB cable for touch input may be:**
- Loose or damaged
- Too long (causing voltage drop)
- Low quality (insufficient power delivery)

**Actions:**
1. Unplug and firmly reconnect the USB cable
2. Try a different, shorter USB cable (< 1 meter)
3. Use a high-quality USB cable with proper shielding

### Solution 3: Try Different USB Port

```bash
# Current connection: Bus 003 Device (USB 2.0)
# Try moving to a different USB port on the Pi
```

**Actions:**
1. Move USB cable to a different USB port
2. Avoid using USB hubs if possible
3. Connect directly to Raspberry Pi USB ports

### Solution 4: Use Powered USB Hub

If the Pi's USB ports can't provide enough power:

**Actions:**
1. Get a powered USB hub (with its own power supply)
2. Connect touchscreen USB to the powered hub
3. Connect hub to Raspberry Pi

### Solution 5: Disable USB Power Management

```bash
ssh rasqberry@192.168.0.108

# Disable USB autosuspend
sudo nano /etc/udev/rules.d/50-usb-power.rules
```

Add this line:
```
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="0712", ATTR{idProduct}=="000a", ATTR{power/autosuspend}="-1"
```

Save and reboot:
```bash
sudo reboot
```

### Solution 6: Add USB Quirks to Boot Config

```bash
ssh rasqberry@192.168.0.108
sudo nano /boot/firmware/cmdline.txt
```

Add at the end of the line (don't create new line):
```
usbcore.quirks=0712:000a:b
```

Save and reboot:
```bash
sudo reboot
```

---

## 🧪 Testing After Each Solution

After trying each solution, test if the disconnections stopped:

```bash
ssh rasqberry@192.168.0.108

# Monitor USB events in real-time
dmesg -w | grep -i 'usb\|disconnect'
```

**Good:** No disconnect messages  
**Bad:** Still seeing "USB disconnect" every few seconds

---

## 📊 Current System Status

### What's Working:
- ✅ Display video output (400x1280)
- ✅ Raspberry Pi 5 system
- ✅ X server (Xwayland)
- ✅ Python GUI applications

### What's NOT Working:
- ❌ Touch input (USB keeps disconnecting)
- ❌ Touch events not reaching applications

### Hardware Detected:
- **Display:** Waveshare -079-HD
- **Touch Controller:** USB HID (Vendor: 0712, Product: 000a)
- **Connection:** USB 2.0 (Bus 003)

---

## 🎯 Recommended Action Plan

### Immediate Steps:

1. **Check your power supply:**
   ```bash
   ssh rasqberry@192.168.0.108
   vcgencmd get_throttled
   vcgencmd measure_volts
   ```

2. **If throttled, get proper power supply:**
   - Official Raspberry Pi 5 27W USB-C power supply
   - Or any quality 5V 5A (25W+) USB-C PD power supply

3. **Check USB cable:**
   - Reconnect firmly
   - Try different cable
   - Use shorter cable

4. **Try different USB port on Pi**

### If Still Not Working:

5. **Disable USB power management** (Solution 5 above)
6. **Add USB quirks** (Solution 6 above)
7. **Use powered USB hub**

---

## 📞 Quick Diagnostic Commands

### Check power status:
```bash
ssh rasqberry@192.168.0.108
vcgencmd get_throttled
# 0x0 = good
# 0x50000 or 0x50005 = under-voltage detected
```

### Monitor USB in real-time:
```bash
ssh rasqberry@192.168.0.108
watch -n 1 'lsusb | grep -i waveshare'
# Should stay constant, not disappear/reappear
```

### Check system voltage:
```bash
ssh rasqberry@192.168.0.108
vcgencmd measure_volts
# Should be close to 5.0V
```

---

## 💡 Why This Happens

**Common causes of USB device disconnections:**

1. **Insufficient Power (80% of cases)**
   - Pi 5 draws more power than Pi 4
   - Touchscreen adds extra power draw
   - Weak power supply can't keep up

2. **Bad USB Cable (15% of cases)**
   - Damaged wires
   - Poor quality cable
   - Too long (voltage drop)

3. **USB Port Issues (5% of cases)**
   - Faulty USB port
   - Electrical interference
   - Driver issues

---

## ✅ Success Criteria

You'll know it's fixed when:

1. **No more USB disconnects in dmesg:**
   ```bash
   dmesg | grep -i disconnect | tail -10
   # Should show old disconnects, not new ones
   ```

2. **Touch device stays in lsusb:**
   ```bash
   lsusb | grep -i waveshare
   # Should always show the device
   ```

3. **Touch input works:**
   - Can tap buttons in GUI
   - Touch events are registered
   - No lag or missed touches

---

## 📁 Next Steps After Fix

Once USB is stable:

1. **Test touch again:**
   ```bash
   ssh rasqberry@192.168.0.108
   DISPLAY=:0 python3 /tmp/test_touch.py
   ```

2. **Launch your app:**
   ```bash
   source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate
   cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer/src
   DISPLAY=:0 python gui_main.py
   ```

---

## 🆘 Still Need Help?

If none of these solutions work:

1. **Check Waveshare documentation** for your specific model
2. **Contact Waveshare support** - this may be a hardware defect
3. **Try touchscreen on different computer** to isolate the problem
4. **Check warranty** if recently purchased

---

**Bottom Line:** Your touchscreen display works, but the touch USB interface needs a better power supply or cable to stop disconnecting.

**Most Likely Fix:** Use official Raspberry Pi 5 27W power supply + quality USB cable