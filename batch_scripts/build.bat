@echo off
:: Batch script to compile a PySide6 application into a single executable file using PyInstaller

:: Set variables
set PYTHON_FILE=splitter_app.py
set ICON_FILE=.\resources\images\wallet-icon.ico
set OUTPUT_DIR=dist

:: Prompt the user for confirmation
echo Would you like to continue with the compiling process? (Y/N)
set /p user_input=

:: Check the user's input
if /i "%user_input%"=="Y" (
    echo Proceeding with the compilation process...
) else if /i "%user_input%"=="N" (
    echo Compilation process canceled.
    exit /b
) else (
    echo Invalid input. Please type Y or N.
    exit /b
)

:: Check if PyInstaller is installed
echo Checking for PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller is not installed. Installing PyInstaller...
    pip install pyinstaller
)

:: Run PyInstaller
echo Compiling %PYTHON_FILE% into a single executable...
pyinstaller --onefile --noconsole --icon=%ICON_FILE% %PYTHON_FILE%

:: Check if compilation succeeded
if exist %OUTPUT_DIR% (
    echo Compilation successful! The executable is in the %OUTPUT_DIR% folder.
) else (
    echo Compilation failed. Please check for errors in the output.
)

pause
