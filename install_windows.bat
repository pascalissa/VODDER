@echo off
setlocal enabledelayedexpansion

echo Setting up VODDER on Windows...

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.12.
    exit /b 1
)

echo Using Python command: python

echo Creating virtual environment in .venv...
python -m venv .venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment.
    exit /b 1
)

echo Activating virtual environment and installing dependencies...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    exit /b 1
)

python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install requirements.
    exit /b 1
)

echo Running database migrations...
python manage.py makemigrations
python manage.py migrate

echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo ==================================================
echo Installation complete!
echo To run the application, simply execute the run script:
echo   run_windows.bat
echo ==================================================

endlocal
