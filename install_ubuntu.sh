#!/usr/bin/env bash
set -e

echo "Setting up VODDER on Ubuntu Linux..."

# Check for Python 3.12 or fallback to python3/python
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "Using Python command: $PYTHON_CMD"

# Optional: Suggest installing python3.12-venv if on Ubuntu and it fails
echo "Creating virtual environment in .venv..."
if ! $PYTHON_CMD -m venv .venv; then
    echo "Failed to create virtual environment."
    echo "On Ubuntu, you may need to install the venv package:"
    echo "sudo apt install ${PYTHON_CMD}-venv"
    exit 1
fi

echo "Activating virtual environment and installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "=================================================="
echo "Installation complete!"
echo "To run the application, simply execute the run script:"
echo "  ./run.sh"
echo "=================================================="
