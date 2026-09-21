@echo off
REM Bot launcher: uses the virtual environment created by setup.bat
cd /d "%~dp0"

if not exist .venv (
    echo Run setup.bat first to install the dependencies.
    exit /b 1
)

.venv\Scripts\python bot.py %*
if %errorlevel%==0 exit /b 0

REM YouTube breaks old yt-dlp versions (HTTP 403). Update once and retry.
echo ==^> Updating yt-dlp and retrying...
.venv\Scripts\pip install --upgrade yt-dlp --quiet
.venv\Scripts\python bot.py %*
