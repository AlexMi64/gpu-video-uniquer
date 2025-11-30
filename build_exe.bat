@echo off
echo Проверка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python не найден. Установите Python 3.11+ с python.org и добавьте в PATH.
    echo Или укажите полный путь к python.exe в этом файле.
    pause
    exit /b 1
)

echo Установка зависимостей (pre-built wheels)...
python -m pip install --only-binary=all -r requirements.txt

echo Установка PyInstaller...
python -m pip install pyinstaller

echo Сборка exe...
python -m pyinstaller --onefile --windowed gui.py --name VideoUniquifier

echo Готово! Исполняемый файл: dist\VideoUniquifier.exe
pause
