@echo off
:: Batch script to compile a PySide6 application into a single executable file using PyInstaller
:: Located in batch_scripts folder

:: Set variables (relative to the root of the repository)
set ROOT_DIR=..
set PYTHON_FILE=%ROOT_DIR%\splitter_app.py
set ICON_FILE=%ROOT_DIR%\resources\images\wallet-icon.ico
set DIST_DIR=%ROOT_DIR%\dist
set BUILD_DIR=%ROOT_DIR%\build
set ENV_NAME=splitter_app

:: Convert the icon file path to an absolute path
for %%I in ("%ICON_FILE%") do set ABS_ICON_FILE=%%~fI

:: Activate the virtual environment
echo Activating virtual environment: %ENV_NAME%
call conda activate %ENV_NAME%
if %errorlevel% neq 0 (
    echo Failed to activate environment %ENV_NAME%. Please check your conda setup.
    pause
    exit /b
)

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

:: Display the working directory for debugging
echo Current directory: %cd%
echo Root directory: %ROOT_DIR%
echo Using icon file: %ABS_ICON_FILE%

:: Check if PyInstaller is installed
echo Checking for PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller is not installed. Installing PyInstaller...
    pip install pyinstaller
)

:: Run PyInstaller
echo Compiling %PYTHON_FILE% into a single executable...
pyinstaller --onefile --noconsole --icon="%ABS_ICON_FILE%" --distpath "%DIST_DIR%" --workpath "%BUILD_DIR%" "%PYTHON_FILE%"
if %errorlevel% neq 0 (
    echo Compilation failed due to an error. Please check the output above.
    pause
    exit /b
)

:: Check if the output directory exists
if exist %DIST_DIR% (
    echo Compilation successful! The executable is in the %DIST_DIR% folder.
) else (
    echo Compilation failed. The dist folder was not created.
)

pause
