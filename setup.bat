@echo off
REM Setup for the YouTube -> MP3 bot on Windows (requires winget, included in Windows 10/11)
cd /d "%~dp0"

where winget >nul 2>nul
if errorlevel 1 (
    echo winget is required. Install "App Installer" from the Microsoft Store and run this script again.
    exit /b 1
)

echo ==^> Installing ffmpeg (needed to convert to MP3)...
where ffmpeg >nul 2>nul
if errorlevel 1 (
    winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
) else (
    echo     ffmpeg is already installed.
)

echo ==^> Installing Deno (yt-dlp needs it to solve YouTube signatures)...
where deno >nul 2>nul
if errorlevel 1 (
    winget install --id DenoLand.Deno -e --accept-source-agreements --accept-package-agreements
) else (
    echo     Deno is already installed.
)

echo ==^> Creating Python virtual environment...
if not exist .venv (
    python -m venv .venv
    if errorlevel 1 (
        echo Python is required. Install it from https://www.python.org/downloads/ ^(check "Add to PATH"^) and run this script again.
        exit /b 1
    )
)

echo ==^> Installing yt-dlp...
.venv\Scripts\pip install --upgrade pip yt-dlp --quiet

echo.
echo Done. If ffmpeg or Deno were just installed, CLOSE this window and open a new one so PATH updates.
echo To use the bot:
echo    bot.bat                                      (interactive mode)
echo    bot.bat "https://youtube.com/watch?v=..."    (direct download)
