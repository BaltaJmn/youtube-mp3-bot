#!/bin/bash
# Bot launcher: uses the virtual environment created by setup.sh
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Run ./setup.sh first to install the dependencies."
    exit 1
fi

./.venv/bin/python bot.py "$@" && exit 0

# YouTube breaks old yt-dlp versions (HTTP 403). Update once and retry.
echo "==> Updating yt-dlp and retrying..."
./.venv/bin/pip install --upgrade "yt-dlp[default]" --quiet
exec ./.venv/bin/python bot.py "$@"
