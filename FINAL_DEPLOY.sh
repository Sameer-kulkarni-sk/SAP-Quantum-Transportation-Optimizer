#!/bin/bash
# Final deployment script with password handling
# Password: Qiskit1!

RASQBERRY_IP="100.67.33.252"
RASQBERRY_USER="rasqberry"
RASQBERRY_PASS="Qiskit1!"
RASQBERRY_HOST="${RASQBERRY_USER}@${RASQBERRY_IP}"
APP_DIR="/home/${RASQBERRY_USER}/RasQberry-Two/examples/quantum_transport_optimizer"

echo "=========================================================================="
echo "  Deploying Quantum Transport Optimizer to RasQberry"
echo "=========================================================================="
echo ""

# Check if sshpass is available
if command -v sshpass &> /dev/null; then
    echo "Using sshpass for automated deployment..."
    USE_SSHPASS=true
else
    echo "Note: sshpass not found. You'll need to enter password manually."
    echo "To install sshpass: brew install hudochenkov/sshpass/sshpass"
    echo ""
    USE_SSHPASS=false
fi

# Create archive
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

# Transfer files
echo "Step 2: Transferring files to RasQberry..."
if [ "$USE_SSHPASS" = true ]; then
    sshpass -p "$RASQBERRY_PASS" scp /tmp/quantum_transport_optimizer.tar.gz ${RASQBERRY_HOST}:/tmp/
else
    echo "Password: Qiskit1!"
    scp /tmp/quantum_transport_optimizer.tar.gz ${RASQBERRY_HOST}:/tmp/
fi
echo "✓ Files transferred"
echo ""

# Deploy and run
echo "Step 3: Deploying and running on RasQberry..."
if [ "$USE_SSHPASS" = true ]; then
    sshpass -p "$RASQBERRY_PASS" ssh -t ${RASQBERRY_HOST} << 'ENDSSH'
        echo "Deploying application..."
        mkdir -p /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
        cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
        tar -xzf /tmp/quantum_transport_optimizer.tar.gz
        chmod +x src/main.py src/gui_main.py create_icon.py
        rm /tmp/quantum_transport_optimizer.tar.gz
        
        echo ""
        echo "Activating environment and running demo..."
        source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate
        
        echo "Installing dependencies..."
        pip install -q pillow 2>/dev/null || true
        
        echo ""
        echo "=========================================================================="
        echo "  RUNNING DEMO"
        echo "=========================================================================="
        echo ""
        
        cd src
        python main.py --demo
        
        echo ""
        echo "=========================================================================="
        echo "  DEMO COMPLETE!"
        echo "=========================================================================="
ENDSSH
else
    echo "Password: Qiskit1!"
    ssh -t ${RASQBERRY_HOST} << 'ENDSSH'
        echo "Deploying application..."
        mkdir -p /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
        cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer
        tar -xzf /tmp/quantum_transport_optimizer.tar.gz
        chmod +x src/main.py src/gui_main.py create_icon.py
        rm /tmp/quantum_transport_optimizer.tar.gz
        
        echo ""
        echo "Activating environment and running demo..."
        source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate
        
        echo "Installing dependencies..."
        pip install -q pillow 2>/dev/null || true
        
        echo ""
        echo "=========================================================================="
        echo "  RUNNING DEMO"
        echo "=========================================================================="
        echo ""
        
        cd src
        python main.py --demo
        
        echo ""
        echo "=========================================================================="
        echo "  DEMO COMPLETE!"
        echo "=========================================================================="
ENDSSH
fi

echo ""
echo "=========================================================================="
echo "  DEPLOYMENT SUCCESSFUL!"
echo "=========================================================================="
echo ""
echo "To launch the touchscreen GUI:"
echo "  ssh rasqberry@100.67.33.252"
echo "  Password: Qiskit1!"
echo "  source /home/rasqberry/RasQberry-Two/venv/RQB2/bin/activate"
echo "  cd /home/rasqberry/RasQberry-Two/examples/quantum_transport_optimizer/src"
echo "  python gui_main.py"
echo ""

rm /tmp/quantum_transport_optimizer.tar.gz