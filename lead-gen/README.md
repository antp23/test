# Safeway Lead Gen & Sourcing Automation

Automated pharmacy prospect pipeline for Safeway Distributors. Scrapes state boards of pharmacy, enriches with Apollo/Google/FDA data, scores leads, and imports to Notion.

## Architecture

```
SCRAPE → ENRICH → SCORE → DEDUP → NOTIFY (Slack) → IMPORT (Notion)
```

**Pipeline stages:**
1. **Scrape** - Pull pharmacy license data from 10 state boards
2. **Enrich** - Apollo.io contacts, Google Places verification, FDA 503B/PCAB/ACHC cross-reference
3. **Score** - Numeric scoring (0-100) with priority tiers (Hot/Warm/Cold/Watch)
4. **Dedup** - Check against existing Notion Prospects database
5. **Notify** - Slack summary for Anthony's approval
6. **Import** - Bulk create Prospect pages in Notion

## Quick Start

```bash
cd lead-gen

# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Run a scraper
python -m src.cli scrape --state FL

# 5. Enrich + score
python -m src.cli enrich
python -m src.cli score

# 6. Import to Notion (with Slack approval)
python -m src.cli import-leads          # Send preview to Slack
python -m src.cli import-leads --approve  # Import approved records

# Or run the full pipeline
python -m src.cli pipeline --states FL,TX --notify
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `scrape --state FL` | Scrape a specific state |
| `scrape --all-states` | Scrape all 10 Tier 1 states |
| `enrich` | Enrich latest scraped data |
| `score` | Score enriched records |
| `import-leads --dry-run` | Preview import without executing |
| `import-leads --approve` | Import to Notion |
| `shortages --check --alert` | Check FDA drug shortages |
| `demand --report` | Product demand report |
| `pipeline --states FL,TX` | Full end-to-end pipeline |

Add `-v` to any command for verbose output.

## Supported States

**Tier 1 (10 states):** FL, TX, CA, NY, NJ, PA, OH, GA, NC, AZ

| State | Method | Data Source |
|-------|--------|-------------|
| FL | Bulk download | FL DOH Data Download Portal |
| TX | CSV download | TX Board of Pharmacy |
| CA | Flat file | CA DCA Public Info |
| NY | Selenium | NYSED Verification Search |
| NJ | Selenium | NJ Division of Consumer Affairs |
| PA | API/Web | PA PALS System |
| OH | API/Web | OH eLicense |
| GA | Web scrape | GA Secretary of State |
| NC | Web scrape | NC Board of Pharmacy |
| AZ | Web scrape | AZ Board of Pharmacy |

## Lead Scoring

| Factor | Points |
|--------|--------|
| Segment = 503B | +30 |
| Segment = 503A | +25 |
| Segment = Mail Order | +20 |
| Segment = B&M | +10 |
| PCAB accredited | +15 |
| FDA 503B registered | +15 |
| ACHC accredited | +10 |
| Employees > 50 | +15 |
| Employees 10-49 | +10 |
| Tier 1 state | +10 |
| Has website | +5 |
| Google reviews > 50 | +5 |
| Sterile license | +10 |
| Source = referral | +25 |

**Score → Priority:**
- 70+ = Hot (Tier 1)
- 50-69 = Warm (Tier 2)
- 30-49 = Cold (Tier 3)
- <30 = Watch List (Tier 4)

## API Keys Required

| Service | Purpose | Get Key |
|---------|---------|---------|
| Apollo.io | Contact enrichment | [apollo.io/settings](https://app.apollo.io/#/settings/integrations/api) |
| Google Places | Business verification | [console.cloud.google.com](https://console.cloud.google.com/apis/credentials) |
| Notion | Database import | [notion.so/my-integrations](https://www.notion.so/my-integrations) |
| Slack | Notifications | [api.slack.com/webhooks](https://api.slack.com/messaging/webhooks) |
| FDA (optional) | Higher rate limits | [open.fda.gov](https://open.fda.gov/apis/authentication/) |

## Cron Schedules (DigitalOcean)

```cron
# Weekly: scrape all states (Sunday 2 AM)
0 2 * * 0 /path/to/lead-gen/scripts/run_scrapers.sh

# Weekly: enrich + score + notify (Sunday 4 AM)
0 4 * * 0 /path/to/lead-gen/scripts/run_enrichment.sh

# Daily: check drug shortages (7 AM)
0 7 * * * /path/to/lead-gen/scripts/run_shortage_monitor.sh
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/test_enrichment/ -v
pytest tests/test_scoring/ -v
pytest tests/test_scrapers/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## Project Structure

```
lead-gen/
├── src/
│   ├── config.py              # Settings (pydantic-settings)
│   ├── db.py                  # SQLAlchemy engine
│   ├── cli.py                 # Click CLI commands
│   ├── models/                # SQLAlchemy ORM models
│   ├── scrapers/              # State board scrapers (10 states)
│   ├── enrichment/            # API clients + classifier + pipeline
│   ├── scoring/               # Lead scoring engine
│   ├── notion/                # Notion API integration
│   ├── notifications/         # Slack notifications
│   ├── sourcing/              # Drug shortages + demand tracking
│   └── utils/                 # Phone normalization, retry, rate limiting
├── scripts/                   # Cron wrapper scripts
├── data/reference/            # Cached reference data (503B, PCAB)
├── tests/                     # pytest test suite
└── alembic/                   # Database migrations
```
