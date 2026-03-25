# Step-by-Step Deployment Instructions

## You Need to Deploy Manually (SSH Password Required)

Since automated deployment requires your RasQberry password, please follow these steps:

## Option 1: Using the Deployment Script (Recommended)

Open a terminal on your Mac and run:

```bash
cd /Users/sameerkulkarni/Python/RasQberry-Two-1/examples/quantum_transport_optimizer
./DEPLOY.sh 192.168.0.118 rasqberry
```

**When prompted, enter your RasQberry password** (you'll be asked twice - once for SCP, once for SSH)

## Option 2: Manual Step-by-Step Deployment

### Step 1: Create Archive (On Your Mac)

```bash
cd /Users/sameerkulkarni/Python/RasQberry-Two-1/examples/quantum_transport_optimizer
tar -czf /tmp/quantum_transport_optimizer.tar.gz .
```

### Step 2: Transfer to RasQberry (On Your Mac)

```bash
scp /tmp/quantum_transport_optimizer.tar.gz rasqberry@192.168.0.118:/tmp/
```
Enter password when prompted.

### Step 3: SSH to RasQberry (On Your Mac)

```bash
ssh rasqberry@192.168.0.118
```
Enter password when prompted.

### Step 4: Extract Files (On RasQberry)

```bash
# Create directory
mkdir -p /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer

# Extract files
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
tar -xzf /tmp/quantum_transport_optimizer.tar.gz

# Make scripts executable
chmod +x src/main.py src/gui_main.py create_icon.py DEPLOY.sh

# Clean up
rm /tmp/quantum_transport_optimizer.tar.gz
```

### Step 5: Install Dependencies (On RasQberry)

```bash
# Activate RQB2 environment
source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate

# Install Python packages
pip install pillow qiskit-optimization qiskit-algorithms
```

### Step 6: Create Icon (On RasQberry)

```bash
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
python create_icon.py
```

### Step 7: Install Desktop Icon (On RasQberry)

```bash
# Create applications directory
mkdir -p ~/.local/share/applications

# Copy desktop file
cp quantum_transport.desktop ~/.local/share/applications/

# Make executable
chmod +x ~/.local/share/applications/quantum_transport.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications/
```

### Step 8: Test CLI Version (On RasQberry)

```bash
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer/src
python main.py --demo
```

You should see optimization results!

### Step 9: Launch Touchscreen GUI (On RasQberry)

```bash
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer/src
python gui_main.py
```

The touchscreen GUI should appear!

## Option 3: Using Git (If Available)

If this code is in a Git repository:

```bash
# On RasQberry
ssh rasqberry@192.168.0.118

cd /home/rasqberry/RasQberry-Two/examples
git clone <your-repo-url> quantum_transport_optimizer

# Or if already cloned:
cd /home/rasqberry/RasQberry-Two
git pull

# Then follow steps 5-9 above
```

## Verification Checklist

After deployment, verify:

- [ ] Files exist: `ls /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer/`
- [ ] Scripts executable: `ls -l src/*.py`
- [ ] Icon created: `ls icon*.png`
- [ ] Desktop icon installed: `ls ~/.local/share/applications/quantum_transport.desktop`
- [ ] CLI works: `python src/main.py --demo`
- [ ] GUI launches: `python src/gui_main.py`

## Troubleshooting

### Can't Connect to RasQberry
```bash
# Test connection
ping 192.168.0.118

# Check SSH is running
ssh rasqberry@192.168.0.118 "echo 'Connected!'"
```

### Wrong Password
- Default RasQberry password is usually `raspberry` or `rasqberry`
- Check your RasQberry documentation

### Permission Denied
```bash
# On RasQberry, check permissions
ls -la /home/rasqberry/RasQberry-Two/examples/
```

### GUI Won't Start
```bash
# Check if tkinter is installed
python -c "import tkinter; print('OK')"

# If not:
sudo apt-get install python3-tk
```

## Quick Commands Summary

```bash
# On Your Mac:
cd /Users/sameerkulkarni/Python/RasQberry-Two-1/examples/quantum_transport_optimizer
./DEPLOY.sh 192.168.0.118 rasqberry

# On RasQberry (after deployment):
source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
python create_icon.py
cp quantum_transport.desktop ~/.local/share/applications/
cd src
python gui_main.py
```

## Need Help?

1. Check TOUCHSCREEN_SETUP.md for detailed GUI setup
2. Check QUICKSTART.md for basic usage
3. Check README.md for complete documentation

## Success!

Once deployed, you can:
- Click the desktop icon to launch GUI
- Or run from terminal: `python src/gui_main.py`
- Or run CLI demo: `python src/main.py --demo`

Enjoy your Quantum Transport Optimizer! 🚀