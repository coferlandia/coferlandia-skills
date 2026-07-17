@echo off
setlocal

title Update Coferlandia Skills

cd /d "%~dp0"
if errorlevel 1 (
    echo Could not open the repository folder.
    pause
    exit /b 1
)

where py >nul 2>&1
if errorlevel 1 (
    echo The "py" command was not found.
    echo Install Python with the Windows launcher and try again.
    pause
    exit /b 1
)

echo Updating skills...
py _protocol\scripts\install_global_skills.py
if errorlevel 1 (
    echo.
    echo The update finished with errors.
    pause
    exit /b 1
)

echo.
echo Skills updated successfully.
pause
exit /b 0
