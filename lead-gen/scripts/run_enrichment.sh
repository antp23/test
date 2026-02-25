#!/bin/bash
# Cron wrapper: Run enrichment pipeline on latest scraped data
# Schedule: Triggered after scraper run, or manually
# Cron: 0 4 * * 0 /path/to/lead-gen/scripts/run_enrichment.sh

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

echo "[$(date)] Starting enrichment pipeline..."
python -m src.cli enrich
echo "[$(date)] Starting scoring..."
python -m src.cli score
echo "[$(date)] Enrichment + scoring complete."
echo "[$(date)] Sending import preview to Slack..."
python -m src.cli import-leads
echo "[$(date)] Done. Awaiting approval for import."
