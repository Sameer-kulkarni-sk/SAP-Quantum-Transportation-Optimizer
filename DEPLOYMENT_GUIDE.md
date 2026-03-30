# Deployment Guide for RasQberry

This guide explains how to deploy the Quantum Transport Optimizer to your RasQberry device.

## Prerequisites

- A RasQberry device with RasQberry-Two installed
- SSH access to your RasQberry
- Network connectivity between your computer and RasQberry

## Quick Deployment

### Option 1: Using the Deployment Script

```bash
# Replace YOUR_RASQBERRY_IP with your device's IP address
./DEPLOY.sh YOUR_RASQBERRY_IP rasqberry
```

You'll be prompted for your RasQberry password during deployment.

### Option 2: Using the Advanced Script

```bash
# Replace YOUR_RASQBERRY_IP with your device's IP address
./scripts/deploy_to_rasqberry.sh YOUR_RASQBERRY_IP
```

This script provides more detailed output and includes dependency installation.
