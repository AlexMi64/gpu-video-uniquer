@echo off
title GPU Video Uniquifier Setup

echo ================================================================
echo       GPU Video Uniquifier - Installation
echo ================================================================
echo.

echo Checking for Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found! Installing Python 3.11...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-installer.exe'"
    echo Starting Python installation...
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install Python. Please install it manually from https://python.org
        echo Make sure to check "Add Python to PATH" during installation!
        pause
        exit /b 1
    )
    echo Python installed successfully!
) else (
    echo Python found!
)

echo.
echo Refreshing environment variables...
call refreshenv.cmd >nul 2>nul || (

)

echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python installation failed or PATH not updated
    echo Please restart this script or add Python to PATH manually
    pause
    exit /b 1
)

echo.
echo Installing/Updating dependencies...
echo Installing pip upgrades first...
python -m pip install --upgrade pip wheel setuptools

echo.
echo Installing core dependencies...
python -m pip install numpy>=2.0,<2.3 tqdm>=4.66

echo.
echo Installing OpenCV (this may take a few minutes)...
python -m pip install opencv-python==4.10.0.84 --verbose

if %errorlevel% neq 0 (
    echo WARNING: OpenCV installation may have failed. Let me try alternative version...
    python -m pip install opencv-python --force-reinstall --no-cache-dir
    if %errorlevel% neq 0 (
        echo ERROR: All OpenCV installations failed
        echo Please install Python 3.11 and dependencies manually:
        echo pip install numpy tqdm opencv-python
        pause
        exit /b 1
    )
)

echo.
echo Testing OpenCV installation...
python -c "import cv2; print('OpenCV version:', cv2.__version__)"
if %errorlevel% neq 0 (
    echo ERROR: OpenCV test failed - module not working
    echo Please check Python installation and try again
    pause
    exit /b 1
)

echo.
echo Creating shortcuts...
powershell -Command "if (!(Test-Path 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\GPU Video Uniquifier')) { New-Item -ItemType Directory -Path 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\GPU Video Uniquifier' }"
powershell -Command "$WScriptShell = New-Object -ComObject WScript.Shell; $Shortcut = $WScriptShell.CreateShortcut('C:\ProgramData\Microsoft\Windows\Start Menu\Programs\GPU Video Uniquifier\GPU Video Uniquifier.lnk'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '\"%~dp0gui.py\"'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = 'python.exe,0'; $Shortcut.Description = 'GPU Video Uniquifier - High-performance video processing'; $Shortcut.Save()"

powershell -Command "$WScriptShell = New-Object -ComObject WScript.Shell; $Shortcut = $WScriptShell.CreateShortcut([System.Environment]::GetFolderPath('Desktop') + '\GPU Video Uniquifier.lnk'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '\"%~dp0gui.py\"'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = 'python.exe,0'; $Shortcut.Description = 'GPU Video Uniquifier - High-performance video processing'; $Shortcut.Save()"

echo.
echo ================================================================
echo       Installation completed successfully!
echo ================================================================
echo.
echo Shortcuts created:
echo - Desktop: GPU Video Uniquifier
echo - Start Menu: GPU Video Uniquifier folder
echo.
echo Run the application by clicking any of the created shortcuts!
echo.
pause
