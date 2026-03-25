#!/bin/bash
# Script to test QAOA optimizer fix on RasQberry

echo "=========================================="
echo "Testing QAOA Optimizer Fix"
echo "=========================================="
echo ""

# Navigate to the quantum transport optimizer directory
cd "$(dirname "$0")"

echo "1. Checking Python environment..."
python3 --version
echo ""

echo "2. Checking Qiskit installation..."
python3 -c "import qiskit; print(f'Qiskit version: {qiskit.__version__}')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Qiskit not found. Installing required packages..."
    pip3 install -r requirements.txt
fi
echo ""

echo "3. Checking Qiskit Optimization packages..."
python3 -c "from qiskit_optimization import QuadraticProgram; print('✓ qiskit-optimization installed')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing qiskit-optimization..."
    pip3 install qiskit-optimization qiskit-algorithms
fi
echo ""

echo "4. Testing QAOA optimizer import..."
python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from optimizers.quantum.qaoa_optimizer import QAOAOptimizer
    print('✓ QAOA optimizer imported successfully')
except Exception as e:
    print(f'❌ Error importing QAOA optimizer: {e}')
    sys.exit(1)
"
echo ""

echo "5. Running GUI application..."
echo "   The QAOA optimizer should now show progress messages!"
echo "   Steps to test:"
echo "   - Click 'Load Data'"
echo "   - Click 'QAOA Quantum'"
echo "   - Watch for progress messages in the results panel"
echo ""
echo "Starting GUI in 3 seconds..."
sleep 3

cd src
python3 gui_main.py

echo ""
echo "=========================================="
echo "Test completed!"
echo "=========================================="