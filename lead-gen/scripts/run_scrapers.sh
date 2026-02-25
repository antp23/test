#!/bin/bash
# Cron wrapper: Run all Tier 1 state board scrapers
# Schedule: Weekly on Sunday at 2 AM
# Cron: 0 2 * * 0 /path/to/lead-gen/scripts/run_scrapers.sh
#
# Usage:
#   ./scripts/run_scrapers.sh              # All Tier 1 states
#   ./scripts/run_scrapers.sh FL TX        # Specific states only

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Load .env
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

echo "[$(date)] Starting scraper run..."

if [ $# -gt 0 ]; then
    # Run specific states
    for state in "$@"; do
        echo "[$(date)] Scraping $state..."
        python -m src.cli scrape --state "$state" || echo "[$(date)] WARNING: $state scraper failed"
    done
else
    # Run all Tier 1 states
    python -m src.cli scrape --all-states
fi

echo "[$(date)] Scraper run complete."
