#!/bin/bash
# Setup for the YouTube → MP3 bot on macOS
set -e

cd "$(dirname "$0")"

echo "==> Checking Homebrew..."
if ! command -v brew &>/dev/null; then
    echo "Homebrew is not installed. Get it from https://brew.sh and run this script again."
    exit 1
fi

echo "==> Installing ffmpeg (needed to convert to MP3)..."
if ! command -v ffmpeg &>/dev/null; then
    brew install ffmpeg
else
    echo "    ffmpeg is already installed."
fi

echo "==> Installing Deno (yt-dlp needs it to solve YouTube signatures)..."
if ! command -v deno &>/dev/null; then
    brew install deno
else
    echo "    Deno is already installed."
fi

echo "==> Creating Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

echo "==> Installing yt-dlp..."
./.venv/bin/pip install --upgrade pip yt-dlp --quiet

echo ""
echo "✅ Done. To use the bot:"
echo "   ./bot.sh                                    (interactive mode)"
echo "   ./bot.sh 'https://youtube.com/watch?v=...'  (direct download)"
