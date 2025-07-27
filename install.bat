@echo off
title Pointer Install
echo Installing dependencies...

if not exist "requirements.txt" (
    echo Error: requirements.txt not found!
    echo Make sure you're in the correct directory.
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo Installation failed!
    pause
    exit /b 1
)

echo Installation completed successfully!
pause 