@echo off
title GPU Video Uniquifier Setup

echo ================================================================
echo       GPU Video Uniquifier - Installation
echo ================================================================
echo.

echo Checking for Python 3.11...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found! Installing Python 3.11...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-installer.exe'"
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install Python. Please install it manually from https://python.org
        pause
        exit /b 1
    )
) else (
    echo Python found!
)

echo.
echo Installing/Updating dependencies...
python -m pip install --upgrade pip
python -m pip install numpy>=2.0,<2.3 tqdm>=4.66 opencv-python==4.10.0.84

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
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
