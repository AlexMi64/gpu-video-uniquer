#!/usr/bin/env python3
"""
GPU Video Uniquifier - Python Installation Script
Handles automatic installation of Python dependencies and shortcuts creation
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def print_header():
    print("=" * 60)
    print("      GPU Video Uniquifier - Installation")
    print("=" * 60)
    print()

def check_python():
    """Check if Python is available and get version"""
    try:
        result = subprocess.run([sys.executable, '--version'],
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print(f"✓ Python found: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Python not found!")
        return False

def install_dependencies():
    """Install all required Python packages"""
    print("\nInstalling dependencies...")

    # Upgrade pip first
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        print("✓ Pip upgraded")
    except subprocess.CalledProcessError:
        print("⚠️ Pip upgrade failed, continuing...")

    # Check Python version for compatibility
    version = sys.version_info
    print(f"Installing packages for Python {version.major}.{version.minor}...")

    if version >= (3, 13):
        # Python 3.13 compatibility - use tested precompiled wheels
        print("✓ Using precompiled wheels for Python 3.13+")
    else:
        # Standard versions
        dependencies = [
            'numpy>=2.0,<2.3',
            'tqdm>=4.66',
            'opencv-python==4.10.0.84'
        ]

    # Install packages sequentially for Python 3.13+ with binary-only flag
    if version >= (3, 13):
        dependencies_313 = [
            ['numpy>=2.0,<2.3'],
            ['tqdm>=4.66'],
            ['opencv-contrib-python', '--only-binary=all', '--prefer-binary']
        ]

        for dep_list in dependencies_313:
            try:
                print(f"Installing {dep_list[0]}...")
                cmd = [sys.executable, '-m', 'pip', 'install'] + dep_list
                subprocess.check_call(cmd)
                print(f"✓ {dep_list[0]} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to install {dep_list[0]}: {e}")
                return False
        return True

    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✓ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {dep}: {e}")
            return False

    return True

def test_import():
    """Test if all critical modules can be imported"""
    print("\nTesting imports...")

    try:
        import cv2
        print(f"✓ OpenCV {cv2.__version__} imported successfully")
    except ImportError as e:
        print(f"✗ OpenCV import failed: {e}")
        return False

    try:
        import numpy as np
        print(f"✓ NumPy {np.__version__} imported successfully")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False

    try:
        import tqdm
        print("✓ tqdm imported successfully")
    except ImportError as e:
        print(f"✗ tqdm import failed: {e}")
        return False

    return True

def create_desktop_shortcut():
    """Create desktop shortcut to the application"""
    if platform.system() != "Windows":
        print("⚠️ Shortcut creation only supported on Windows")
        return

    try:
        import winshell
        from win32com.client import Dispatch

        current_dir = Path.cwd()
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "GPU Video Uniquifier.lnk"

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{current_dir / "gui.py"}"'
        shortcut.WorkingDirectory = str(current_dir)
        shortcut.IconLocation = sys.executable + ",0"
        shortcut.save()

        print("✓ Desktop shortcut created")

    except ImportError:
        print("⚠️ winshell not available, desktop shortcut skipped")
        # Basic fallback
        print(f"Create shortcut manually:")
        print(f"Target: {sys.executable}")
        print(f"Arguments: gui.py")
        print(f"Start in: {Path.cwd()}")
    except Exception as e:
        print(f"⚠️ Desktop shortcut creation failed: {e}")

def main():
    print_header()

    if not check_python():
        print("Please install Python 3.11+ first!")
        print("Download from: https://python.org")
        input("Press Enter to exit...")
        return

    if not install_dependencies():
        print("Dependency installation failed!")
        print("Try: pip install numpy tqdm opencv-python")
        input("Press Enter to exit...")
        return

    if not test_import():
        print("Import test failed!")
        print("Check your Python installation and try reinstalling packages")
        input("Press Enter to exit...")
        return

    create_desktop_shortcut()

    print("\n" + "=" * 60)
    print("      Installation completed successfully!")
    print("=" * 60)
    print()

    current_dir = Path.cwd()
    print("How to run:")
    print("1. GUI Interface:")
    print(f"   cd {current_dir}")
    print("   python gui.py")
    print()
    print("2. Command Line:")
    print(f"   cd {current_dir}")
    print("   python video_uniquifier.py --help")
    print()
    print("3. Batch Processing:")
    print(f"   cd {current_dir}")
    print("   run_uniquifier.bat")
    print()
    print("GPU Support:")
    try:
        import cv2
        cuda_count = cv2.cuda.getCudaEnabledDeviceCount()
        if cuda_count > 0:
            print(f"✓ CUDA GPUs detected: {cuda_count}")
        else:
            print("ℹ️ CUDA not detected, using CPU processing")
    except:
        print("ℹ️ OpenCV CUDA status unknown")

    print("\n" + "=" * 60)
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
