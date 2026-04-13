#!/usr/bin/env bash
set -e

echo "Starting VODDER application..."

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment (.venv) not found."
    echo "Please run the installation script first (e.g., ./install_mac.sh or ./install_ubuntu.sh)."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Run the Django development server
echo "Running the development server..."
python manage.py runserver
