# Deployment Guide for RasQberry

This guide explains how to deploy the Quantum Transport Optimizer to your RasQberry device.

## Prerequisites

- A RasQberry device with RasQberry-Two installed
- SSH access to your RasQberry
- Network connectivity between your computer and RasQberry
- `sshpass` installed on your local machine:
  - **macOS**: `brew install hudochenkov/sshpass/sshpass`
  - **Linux**: `sudo apt-get install sshpass`

## Quick Deployment

### Option 1: Using the Deployment Script

```bash
# Replace YOUR_RASQBERRY_IP with your device's IP address
# You can provide the password as an argument or you'll be prompted
./DEPLOY.sh YOUR_RASQBERRY_IP [PASSWORD]

# Example with password
./DEPLOY.sh 192.168.1.100 mypassword

# Example without password (will prompt)
./DEPLOY.sh 192.168.1.100
```

### Option 2: Using the Advanced Script

```bash
# Replace YOUR_RASQBERRY_IP with your device's IP address
# You can provide the password as an argument or you'll be prompted
./scripts/deploy_to_rasqberry.sh YOUR_RASQBERRY_IP [PASSWORD]

# Example with password
./scripts/deploy_to_rasqberry.sh 192.168.1.100 mypassword

# Example without password (will prompt)
./scripts/deploy_to_rasqberry.sh 192.168.1.100
```

This script provides more detailed output and includes dependency installation.

**Note**: Both scripts use password-based SSH authentication via `sshpass`. The password can be provided as a command-line argument or you will be prompted to enter it securely.
