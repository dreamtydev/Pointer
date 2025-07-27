@echo off
title Pointer Build
echo Building Pointer...

if not exist "pointer_app.py" (
    echo Error: pointer_app.py not found!
    echo Make sure you're in the correct directory.
    pause
    exit /b 1
)

if not exist "pointer_app.spec" (
    echo Error: pointer_app.spec not found!
    echo Make sure you're in the correct directory.
    pause
    exit /b 1
)

echo Checking Python...

set PYTHON_CMD=python

python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found in PATH, trying alternatives...
    
    if exist "C:\Python39\python.exe" (
        set PYTHON_CMD=C:\Python39\python.exe
        echo Found Python 3.9
    ) else if exist "C:\Python310\python.exe" (
        set PYTHON_CMD=C:\Python310\python.exe
        echo Found Python 3.10
    ) else if exist "C:\Python311\python.exe" (
        set PYTHON_CMD=C:\Python311\python.exe
        echo Found Python 3.11
    ) else if exist "C:\Python312\python.exe" (
        set PYTHON_CMD=C:\Python312\python.exe
        echo Found Python 3.12
    ) else if exist "C:\Python313\python.exe" (
        set PYTHON_CMD=C:\Python313\python.exe
        echo Found Python 3.13
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" (
        set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python39\python.exe
        echo Found Python 3.9 (User)
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
        set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe
        echo Found Python 3.10 (User)
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
        echo Found Python 3.11 (User)
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
        echo Found Python 3.12 (User)
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
        set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python313\python.exe
        echo Found Python 3.13 (User)
    ) else (
        echo Python not found! Please install Python.
        pause
        exit /b 1
    )
) else (
    echo Python found in PATH
)

echo Using: %PYTHON_CMD%
echo.

echo Running build script...
%PYTHON_CMD% build.py
if errorlevel 1 (
    echo Build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo Build completed successfully!
pause 