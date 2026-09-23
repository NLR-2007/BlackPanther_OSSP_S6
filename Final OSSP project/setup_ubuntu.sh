#!/bin/bash
set -e

echo "=================================================================="
echo " Smart Linux Resource Monitoring and Process Control System Setup "
echo " Target OS: Ubuntu Linux (Terminal & Desktop)                   "
echo "=================================================================="

echo "[1/3] Updating apt package index and installing dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-pyqt6 python3-psutil gcc make cmake qt6-base-dev

echo "[2/3] Compiling native C Systems Engine (libsysmonitor.so)..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/src/c_engine"
make clean
make

echo "[3/3] Setting executable permissions..."
chmod +x "$SCRIPT_DIR/run_task_manager.py"
chmod +x "$SCRIPT_DIR/run_cli_task_manager.py"

echo "=================================================================="
echo " Build & Setup Complete!"
echo " "
echo " To run the GUI Task Manager in Ubuntu:"
echo "   python3 run_task_manager.py"
echo " "
echo " To run the Terminal CLI Task Manager in Ubuntu Terminal:"
echo "   python3 run_cli_task_manager.py"
echo "=================================================================="
