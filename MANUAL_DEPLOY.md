# Manual Deployment to RasQberry (192.168.0.118)

Since automated deployment requires SSH credentials, here are **3 easy methods** to deploy the application to your RasQberry device.

## Method 1: Using the Deployment Script (Recommended)

From your local machine (where this code is):

```bash
cd examples/quantum_transport_optimizer
./DEPLOY.sh 192.168.0.118 rasqberry
```

You'll be prompted for the RasQberry password twice (for SCP and SSH).

## Method 2: Manual SCP Transfer

### Step 1: Create archive on your local machine
```bash
cd examples/quantum_transport_optimizer
tar -czf quantum_transport_optimizer.tar.gz .
```

### Step 2: Transfer to RasQberry
```bash
scp quantum_transport_optimizer.tar.gz rasqberry@192.168.0.118:/tmp/
```

### Step 3: SSH to RasQberry and extract
```bash
ssh rasqberry@192.168.0.118

# On RasQberry:
mkdir -p /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
tar -xzf /tmp/quantum_transport_optimizer.tar.gz
chmod +x src/main.py
rm /tmp/quantum_transport_optimizer.tar.gz
```

## Method 3: Direct Git Clone (If this is in a Git repo)

On your RasQberry device:

```bash
ssh rasqberry@192.168.0.118

# On RasQberry:
cd /home/rasqberry/RasQberry-Two/examples
git clone <your-repo-url> quantum_transport_optimizer
# OR if already cloned:
cd /home/rasqberry/RasQberry-Two
git pull
```

## Method 4: Using VS Code Remote SSH

If you have VS Code with Remote SSH extension:

1. Open VS Code
2. Press `F1` and select "Remote-SSH: Connect to Host"
3. Enter: `rasqberry@192.168.0.118`
4. Enter password when prompted
5. Open folder: `/home/rasqberry/RasQberry-Two/examples`
6. Copy the `quantum_transport_optimizer` folder from your local machine

## Method 5: Using rsync (Most Efficient)

```bash
cd examples
rsync -avz --progress quantum_transport_optimizer/ rasqberry@192.168.0.118:/home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer/
```

## After Deployment - First Run

Once files are on RasQberry:

```bash
# SSH to RasQberry
ssh rasqberry@192.168.0.118

# Activate RQB2 environment
source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate

# Install dependencies (if needed)
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
pip install -r requirements.txt

# Run the demo
cd src
python main.py --demo
```

## Verify Installation

```bash
# Check files are present
ls -la /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer/

# Should show:
# - README.md
# - QUICKSTART.md
# - requirements.txt
# - src/
# - data/
# - config/
```

## Troubleshooting

### "Permission denied" during SCP
- Verify RasQberry is accessible: `ping 192.168.0.118`
- Check SSH is enabled on RasQberry
- Verify username and password

### "No such file or directory"
- Create parent directories first:
  ```bash
  ssh rasqberry@192.168.0.118 "mkdir -p /home/rasqberry/RasQberry-Two/examples"
  ```

### Files already exist
- Remove old version first:
  ```bash
  ssh rasqberry@192.168.0.118 "rm -rf /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer"
  ```

## Quick Test After Deployment

```bash
ssh rasqberry@192.168.0.118
source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate
cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer/src
python -c "from models.shipment import Shipment; print('✓ Import successful')"
python main.py --demo
```

If you see the demo output with optimization results, deployment was successful! 🎉