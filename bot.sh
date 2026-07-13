#!/bin/bash
# Bot launcher: uses the virtual environment created by setup.sh
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Run ./setup.sh first to install the dependencies."
    exit 1
fi

exec ./.venv/bin/python bot.py "$@"
