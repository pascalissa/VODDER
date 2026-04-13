@echo off
setlocal

echo Starting VODDER application...

:: Check if .venv exists
if not exist ".venv\" (
    echo Error: Virtual environment (.venv) not found.
    echo Please run install_windows.bat first.
    exit /b 1
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Run the Django development server
echo Running the development server...
python manage.py runserver

endlocal
