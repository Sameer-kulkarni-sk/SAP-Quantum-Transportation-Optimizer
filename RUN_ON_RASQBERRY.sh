#!/bin/bash
# Complete deployment and run script for RasQberry
# Run this from your Mac terminal

echo "=========================================================================="
echo "  Quantum Transport Optimizer - Deploy and Run on RasQberry"
echo "=========================================================================="
echo ""
echo "This script will:"
echo "  1. Deploy the application to RasQberry"
echo "  2. Install dependencies"
echo "  3. Run the demo"
echo ""
echo "You will be prompted for your RasQberry password multiple times."
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Configuration
RASQBERRY_IP="192.168.0.108"
RASQBERRY_USER="rasqberry"
RASQBERRY_HOST="${RASQBERRY_USER}@${RASQBERRY_IP}"
APP_DIR="/home/${RASQBERRY_USER}/RasQberry-Two/examples/quantum_transport_optimizer"

echo ""
echo "Step 1: Creating deployment archive..."
cd "$(dirname "$0")"
tar -czf /tmp/quantum_transport_optimizer.tar.gz \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.tar.gz' \
    .

echo "✓ Archive created"
echo ""

echo "Step 2: Transferring files to RasQberry..."
echo "Enter RasQberry password when prompted:"
scp /tmp/quantum_transport_optimizer.tar.gz ${RASQBERRY_HOST}:/tmp/

echo "✓ Files transferred"
echo ""

echo "Step 3: Deploying on RasQberry..."
echo "Enter RasQberry password when prompted:"
ssh -t ${RASQBERRY_HOST} << 'ENDSSH'
    echo "Creating directory..."
    mkdir -p /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
    
    echo "Extracting files..."
    cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
    tar -xzf /tmp/quantum_transport_optimizer.tar.gz
    
    echo "Making scripts executable..."
    chmod +x src/main.py src/gui_main.py create_icon.py
    
    echo "Cleaning up..."
    rm /tmp/quantum_transport_optimizer.tar.gz
    
    echo "✓ Deployment complete"
ENDSSH

echo ""
echo "Step 4: Installing dependencies and running demo..."
echo "Enter RasQberry password when prompted:"
ssh -t ${RASQBERRY_HOST} << 'ENDSSH'
    echo "Activating RQB2 environment..."
    source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate
    
    echo "Installing dependencies..."
    cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
    pip install -q pillow 2>/dev/null || echo "Pillow already installed"
    
    echo ""
    echo "=========================================================================="
    echo "  Running Demo..."
    echo "=========================================================================="
    echo ""
    
    cd src
    python main.py --demo
    
    echo ""
    echo "=========================================================================="
    echo "  Demo Complete!"
    echo "=========================================================================="
    echo ""
    echo "To run the touchscreen GUI:"
    echo "  ssh rasqberry@192.168.0.108"
    echo "  source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate"
    echo "  cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer/src"
    echo "  python gui_main.py"
    echo ""
ENDSSH

echo ""
echo "=========================================================================="
echo "  All Done!"
echo "=========================================================================="
echo ""
echo "The application is now deployed and tested on your RasQberry!"
echo ""

# Clean up local archive
rm /tmp/quantum_transport_optimizer.tar.gz