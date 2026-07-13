@echo off
REM Bot launcher: uses the virtual environment created by setup.bat
cd /d "%~dp0"

if not exist .venv (
    echo Run setup.bat first to install the dependencies.
    exit /b 1
)

.venv\Scripts\python bot.py %*
