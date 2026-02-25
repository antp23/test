#!/bin/bash
# Cron wrapper: Check FDA drug shortage database
# Schedule: Daily at 7 AM
# Cron: 0 7 * * * /path/to/lead-gen/scripts/run_shortage_monitor.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

echo "[$(date)] Checking FDA drug shortages..."
python -m src.cli shortages --check --alert
echo "[$(date)] Shortage check complete."
