#!/bin/bash
# Deployment script for Quantum Transport Optimizer to RasQberry
# Usage: ./scripts/deploy_to_rasqberry.sh YOUR_RASQBERRY_IP [PASSWORD]

set -e

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo "Error: sshpass is not installed"
    echo "Please install it first:"
    echo "  macOS: brew install hudochenkov/sshpass/sshpass"
    echo "  Linux: sudo apt-get install sshpass"
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if IP address is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: RasQberry IP address required${NC}"
    echo "Usage: ./scripts/deploy_to_rasqberry.sh YOUR_RASQBERRY_IP [PASSWORD]"
    echo "Example: ./scripts/deploy_to_rasqberry.sh 192.168.1.100 mypassword"
    exit 1
fi

RASQBERRY_IP="$1"
RASQBERRY_PASSWORD="${2}"
RASQBERRY_USER="rasqberry"
RASQBERRY_HOST="${RASQBERRY_USER}@${RASQBERRY_IP}"

# Prompt for password if not provided
if [ -z "$RASQBERRY_PASSWORD" ]; then
    echo -e "${YELLOW}Enter RasQberry password:${NC}"
    read -s RASQBERRY_PASSWORD
    echo ""
fi
APP_DIR="/home/${RASQBERRY_USER}/RasQberry-Two/examples/quantum_transport_optimizer"
VENV_PATH="/home/${RASQBERRY_USER}/RasQberry-Two/venv/RQB2"

echo -e "${BLUE}=========================================================================="
echo "  Quantum Transport Optimizer - RasQberry Deployment"
echo -e "==========================================================================${NC}"
echo ""
echo -e "${YELLOW}Target: ${RASQBERRY_HOST}${NC}"
echo -e "${YELLOW}Destination: ${APP_DIR}${NC}"
echo ""

# Step 1: Create deployment archive
echo -e "${BLUE}[1/5] Creating deployment archive...${NC}"
cd "$(dirname "$0")/.."
tar -czf /tmp/quantum_transport_optimizer.tar.gz \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.tar.gz' \
    --exclude='backups' \
    --exclude='.gitignore' \
    .
echo -e "${GREEN}✓ Archive created${NC}"
echo ""

# Step 2: Transfer files
echo -e "${BLUE}[2/5] Transferring files to RasQberry...${NC}"
sshpass -p "${RASQBERRY_PASSWORD}" scp -o StrictHostKeyChecking=no /tmp/quantum_transport_optimizer.tar.gz ${RASQBERRY_HOST}:/tmp/
echo -e "${GREEN}✓ Files transferred${NC}"
echo ""

# Step 3: Deploy on RasQberry
echo -e "${BLUE}[3/5] Deploying on RasQberry...${NC}"
sshpass -p "${RASQBERRY_PASSWORD}" ssh -o StrictHostKeyChecking=no -t ${RASQBERRY_HOST} << ENDSSH
    set -e
    echo "Creating application directory..."
    mkdir -p ${APP_DIR}
    cd ${APP_DIR}
    
    echo "Extracting files..."
    tar -xzf /tmp/quantum_transport_optimizer.tar.gz
    
    echo "Setting permissions..."
    chmod +x src/main.py src/gui_main.py 2>/dev/null || true
    chmod +x scripts/*.sh 2>/dev/null || true
    
    echo "Installing desktop icon..."
    mkdir -p /home/${RASQBERRY_USER}/Desktop
    cp quantum_transport_optimizer.desktop /home/${RASQBERRY_USER}/Desktop/
    chmod +x /home/${RASQBERRY_USER}/Desktop/quantum_transport_optimizer.desktop
    
    echo "Cleaning up..."
    rm /tmp/quantum_transport_optimizer.tar.gz
    
    echo "✓ Deployment complete"
    echo "✓ Desktop icon installed"
ENDSSH
echo -e "${GREEN}✓ Deployed successfully${NC}"
echo ""

# Step 4: Install dependencies
echo -e "${BLUE}[4/5] Installing dependencies...${NC}"
sshpass -p "${RASQBERRY_PASSWORD}" ssh -o StrictHostKeyChecking=no -t ${RASQBERRY_HOST} << ENDSSH
    set -e
    source ${VENV_PATH}/bin/activate
    cd ${APP_DIR}
    
    echo "Installing Python packages..."
    pip install -q --upgrade pip 2>/dev/null || true
    pip install -q -r requirements.txt 2>/dev/null || true
    
    echo "✓ Dependencies installed"
ENDSSH
echo -e "${GREEN}✓ Dependencies ready${NC}"
echo ""

# Step 5: Run demo
echo -e "${BLUE}[5/5] Running demo...${NC}"
echo ""
sshpass -p "${RASQBERRY_PASSWORD}" ssh -o StrictHostKeyChecking=no -t ${RASQBERRY_HOST} << ENDSSH
    source ${VENV_PATH}/bin/activate
    cd ${APP_DIR}/src
    python main.py --demo
ENDSSH

# Cleanup
rm /tmp/quantum_transport_optimizer.tar.gz 2>/dev/null || true

echo ""
echo -e "${GREEN}=========================================================================="
echo "  DEPLOYMENT SUCCESSFUL!"
echo -e "==========================================================================${NC}"
echo ""
echo -e "${YELLOW}Application deployed to: ${APP_DIR}${NC}"
echo ""
echo -e "${BLUE}To run the GUI on RasQberry:${NC}"
echo "  ssh ${RASQBERRY_HOST}"
echo "  source ${VENV_PATH}/bin/activate"
echo "  cd ${APP_DIR}/src"
echo "  python gui_main.py"
echo ""
echo -e "${BLUE}To run the CLI demo:${NC}"
echo "  ssh ${RASQBERRY_HOST}"
echo "  source ${VENV_PATH}/bin/activate"
echo "  cd ${APP_DIR}/src"
echo "  python main.py --demo"
echo ""