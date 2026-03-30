#!/bin/bash
# Deployment script for Quantum Transport Optimizer to RasQberry
# Usage: ./DEPLOY.sh [rasqberry_ip] [username]

set -e

# Configuration - UPDATE THESE VALUES FOR YOUR RASQBERRY
RASQBERRY_IP="${1:-YOUR_RASQBERRY_IP}"
RASQBERRY_USER="${2:-rasqberry}"
RASQBERRY_HOST="${RASQBERRY_USER}@${RASQBERRY_IP}"
TARGET_DIR="/home/${RASQBERRY_USER}/RasQberry-Two/examples/quantum_transport_optimizer"

echo "========================================================================"
echo "  Deploying Quantum Transport Optimizer to RasQberry"
echo "========================================================================"
echo "Target: ${RASQBERRY_HOST}"
echo "Directory: ${TARGET_DIR}"
echo ""

# Validate IP address is set
if [ "$RASQBERRY_IP" = "YOUR_RASQBERRY_IP" ]; then
    echo "ERROR: Please provide your RasQberry IP address"
    echo "Usage: ./DEPLOY.sh YOUR_RASQBERRY_IP [username]"
    echo "Example: ./DEPLOY.sh 192.168.1.100 rasqberry"
    exit 1
fi

# Create archive
echo "📦 Creating deployment archive..."
cd "$(dirname "$0")"
tar -czf /tmp/quantum_transport_optimizer.tar.gz \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.tar.gz' \
    .

echo "✓ Archive created: /tmp/quantum_transport_optimizer.tar.gz"
echo ""

# Transfer to RasQberry
echo "🚀 Transferring files to RasQberry..."
echo "You will be prompted for the RasQberry password..."
scp /tmp/quantum_transport_optimizer.tar.gz ${RASQBERRY_HOST}:/tmp/

echo "✓ Files transferred"
echo ""

# Extract and setup on RasQberry
echo "📂 Extracting files on RasQberry..."
ssh ${RASQBERRY_HOST} << 'ENDSSH'
    # Create directory
    mkdir -p ${TARGET_DIR}
    
    # Extract archive
    cd ${TARGET_DIR}
    tar -xzf /tmp/quantum_transport_optimizer.tar.gz
    
    # Make main.py executable
    chmod +x src/main.py
    
    # Clean up
    rm /tmp/quantum_transport_optimizer.tar.gz
    
    echo "✓ Files extracted and configured"
ENDSSH

echo ""
echo "✅ Deployment complete!"
echo ""
echo "To run the application on RasQberry:"
echo "  1. SSH to RasQberry: ssh ${RASQBERRY_HOST}"
echo "  2. Activate venv: source /home/${RASQBERRY_USER}/RasQberry-Two/venv/RQB2/bin/activate"
echo "  3. Navigate: cd ${TARGET_DIR}/src"
echo "  4. Run demo: python main.py --demo"
echo ""
echo "========================================================================"

# Clean up local archive
rm /tmp/quantum_transport_optimizer.tar.gz