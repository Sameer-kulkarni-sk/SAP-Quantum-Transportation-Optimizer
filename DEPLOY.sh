#!/bin/bash
# Deployment script for Quantum Transport Optimizer to RasQberry
# Usage: ./DEPLOY.sh [rasqberry_ip] [password]

set -e

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo "Error: sshpass is not installed"
    echo "Please install it first:"
    echo "  macOS: brew install hudochenkov/sshpass/sshpass"
    echo "  Linux: sudo apt-get install sshpass"
    exit 1
fi

# Configuration - UPDATE THESE VALUES FOR YOUR RASQBERRY
RASQBERRY_IP="${1:-YOUR_RASQBERRY_IP}"
RASQBERRY_PASSWORD="${2}"
RASQBERRY_USER="rasqberry"
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
    echo "Usage: ./DEPLOY.sh YOUR_RASQBERRY_IP [PASSWORD]"
    echo "Example: ./DEPLOY.sh 192.168.1.100 mypassword"
    exit 1
fi

# Prompt for password if not provided
if [ -z "$RASQBERRY_PASSWORD" ]; then
    echo "Enter RasQberry password:"
    read -s RASQBERRY_PASSWORD
    echo ""
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
sshpass -p "${RASQBERRY_PASSWORD}" scp -o StrictHostKeyChecking=no /tmp/quantum_transport_optimizer.tar.gz ${RASQBERRY_HOST}:/tmp/

echo "✓ Files transferred"
echo ""

# Extract and setup on RasQberry
echo "📂 Extracting files on RasQberry..."
sshpass -p "${RASQBERRY_PASSWORD}" ssh -o StrictHostKeyChecking=no ${RASQBERRY_HOST} << ENDSSH
    # Create directory
    mkdir -p $TARGET_DIR
    
    # Extract archive
    cd $TARGET_DIR
    tar -xzf /tmp/quantum_transport_optimizer.tar.gz
    
    # Make main.py executable
    chmod +x src/main.py src/gui_main.py 2>/dev/null || true
    
    # Install desktop icon
    mkdir -p /home/$RASQBERRY_USER/Desktop
    cp quantum_transport_optimizer.desktop /home/$RASQBERRY_USER/Desktop/
    chmod +x /home/$RASQBERRY_USER/Desktop/quantum_transport_optimizer.desktop
    
    # Clean up
    rm /tmp/quantum_transport_optimizer.tar.gz
    
    echo "✓ Files extracted and configured"
    echo "✓ Desktop icon installed"
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