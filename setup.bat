@echo off
title Pointer Setup
echo Setting up Pointer...

if not exist "requirements.txt" (
    echo Error: requirements.txt not found!
    echo Make sure you're in the correct directory.
    pause
    exit /b 1
)

if not exist "pointer_app.py" (
    echo Error: pointer_app.py not found!
    echo Make sure you're in the correct directory.
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Installation failed!
    pause
    exit /b 1
)

echo.
echo Building project...
python build.py
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
pause 