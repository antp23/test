"""CLI entry point for the Safeway Lead Generation system.

Usage:
    python -m src.cli scrape --state FL
    python -m src.cli scrape --all
    python -m src.cli enrich --batch-size 100
    python -m src.cli score --recalculate
    python -m src.cli import-leads --dry-run
    python -m src.cli import-leads --approve
    python -m src.cli shortages --check
    python -m src.cli demand --report
    python -m src.cli pipeline --states FL,TX
"""

import csv
import logging
from datetime import date
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from src.config import get_settings
from src.utils.logging import setup_logging

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def cli(verbose: bool):
    """Safeway Lead Gen - Pharmacy prospect pipeline automation."""
    level = "DEBUG" if verbose else get_settings().log_level
    setup_logging(level)


# ---------------------------------------------------------------------------
# SCRAPE
# ---------------------------------------------------------------------------
@cli.command()
@click.option("--state", "-s", multiple=True, help="State code(s) to scrape (e.g., FL TX)")
@click.option("--all-states", is_flag=True, help="Scrape all Tier 1 states")
@click.option("--output-dir", "-o", type=click.Path(), default=None, help="Output directory")
def scrape(state: tuple[str, ...], all_states: bool, output_dir: str | None):
    """Scrape state board of pharmacy databases for licensed pharmacies."""
    from src.scrapers import get_scraper, get_all_scrapers

    settings = get_settings()
    out_dir = Path(output_dir) if output_dir else settings.data_dir / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    if all_states:
        states = settings.tier_1_state_list
    elif state:
        states = [s.upper() for s in state]
    else:
        console.print("[red]Specify --state or --all-states[/red]")
        raise SystemExit(1)

    console.print(f"\n[bold]Scraping {len(states)} state(s): {', '.join(states)}[/bold]\n")

    total_records = 0
    results_table = Table(title="Scrape Results")
    results_table.add_column("State", style="cyan")
    results_table.add_column("Records", justify="right")
    results_table.add_column("Status", style="green")
    results_table.add_column("Output File")

    for state_code in states:
        try:
            scraper = get_scraper(state_code)
            records = scraper.run()
            count = len(records)
            total_records += count

            # Write CSV
            out_file = out_dir / f"{state_code}_{date.today().isoformat()}.csv"
            _write_records_csv(records, out_file)
            results_table.add_row(state_code, str(count), "OK", str(out_file))

        except Exception as e:
            logger.error("Failed to scrape %s: %s", state_code, e)
            results_table.add_row(state_code, "0", f"[red]FAILED: {e}[/red]", "")

    console.print(results_table)
    console.print(f"\n[bold green]Total: {total_records} records[/bold green]\n")


# ---------------------------------------------------------------------------
# ENRICH
# ---------------------------------------------------------------------------
@cli.command()
@click.option("--input-dir", "-i", type=click.Path(exists=True), default=None)
@click.option("--batch-size", "-b", type=int, default=None)
@click.option("--skip-apollo", is_flag=True, help="Skip Apollo enrichment")
@click.option("--skip-google", is_flag=True, help="Skip Google Places enrichment")
def enrich(input_dir: str | None, batch_size: int | None, skip_apollo: bool, skip_google: bool):
    """Enrich scraped pharmacy records with contact data and business intelligence."""
    from src.enrichment.pipeline import EnrichmentPipeline

    settings = get_settings()
    in_dir = Path(input_dir) if input_dir else settings.data_dir / "raw"
    out_dir = settings.data_dir / "enriched"
    out_dir.mkdir(parents=True, exist_ok=True)

    batch = batch_size or settings.enrichment_batch_size
    pipeline = EnrichmentPipeline(
        settings=settings,
        skip_apollo=skip_apollo,
        skip_google=skip_google,
    )

    csv_files = sorted(in_dir.glob("*.csv"))
    if not csv_files:
        console.print(f"[yellow]No CSV files found in {in_dir}[/yellow]")
        return

    console.print(f"\n[bold]Enriching {len(csv_files)} file(s), batch size {batch}[/bold]\n")

    for csv_file in csv_files:
        records = _read_records_csv(csv_file)
        enriched = pipeline.enrich_batch(records, batch_size=batch)
        out_file = out_dir / csv_file.name
        _write_records_csv(enriched, out_file)
        console.print(f"  {csv_file.name}: {len(records)} → {len(enriched)} enriched")

    console.print("\n[bold green]Enrichment complete[/bold green]\n")


# ---------------------------------------------------------------------------
# SCORE
# ---------------------------------------------------------------------------
@cli.command()
@click.option("--input-dir", "-i", type=click.Path(exists=True), default=None)
@click.option("--recalculate", is_flag=True, help="Recalculate all scores")
def score(input_dir: str | None, recalculate: bool):
    """Score enriched pharmacy records and assign priority tiers."""
    from src.scoring.scorer import LeadScorer

    settings = get_settings()
    in_dir = Path(input_dir) if input_dir else settings.data_dir / "enriched"
    out_dir = settings.data_dir / "scored"
    out_dir.mkdir(parents=True, exist_ok=True)

    scorer = LeadScorer(settings=settings)
    csv_files = sorted(in_dir.glob("*.csv"))

    if not csv_files:
        console.print(f"[yellow]No CSV files found in {in_dir}[/yellow]")
        return

    console.print(f"\n[bold]Scoring {len(csv_files)} file(s)[/bold]\n")

    for csv_file in csv_files:
        records = _read_records_csv(csv_file)
        scored = [scorer.score_record(r) for r in records]
        out_file = out_dir / csv_file.name
        _write_records_csv(scored, out_file)

        # Summary stats
        scores = [int(r.get("score", 0)) for r in scored]
        hot = sum(1 for s in scores if s >= 70)
        warm = sum(1 for s in scores if 50 <= s < 70)
        cold = sum(1 for s in scores if 30 <= s < 50)
        watch = sum(1 for s in scores if s < 30)
        console.print(
            f"  {csv_file.name}: {len(scored)} scored | "
            f"[red]{hot} hot[/red] | [yellow]{warm} warm[/yellow] | "
            f"[blue]{cold} cold[/blue] | {watch} watch"
        )

    console.print("\n[bold green]Scoring complete[/bold green]\n")


# ---------------------------------------------------------------------------
# IMPORT LEADS
# ---------------------------------------------------------------------------
@cli.command("import-leads")
@click.option("--input-dir", "-i", type=click.Path(exists=True), default=None)
@click.option("--dry-run", is_flag=True, help="Preview without importing")
@click.option("--approve", is_flag=True, help="Skip Slack approval gate")
def import_leads(input_dir: str | None, dry_run: bool, approve: bool):
    """Import scored leads into Notion Prospects database."""
    from src.notion.prospect_importer import ProspectImporter
    from src.notifications.slack_notifier import SlackNotifier

    settings = get_settings()
    in_dir = Path(input_dir) if input_dir else settings.data_dir / "scored"
    csv_files = sorted(in_dir.glob("*.csv"))

    if not csv_files:
        console.print(f"[yellow]No CSV files found in {in_dir}[/yellow]")
        return

    all_records = []
    for csv_file in csv_files:
        all_records.extend(_read_records_csv(csv_file))

    importer = ProspectImporter(settings=settings)
    new_records, duplicates = importer.check_duplicates(all_records)

    console.print(f"\n[bold]Import Preview[/bold]")
    console.print(f"  Total records: {len(all_records)}")
    console.print(f"  New records: {len(new_records)}")
    console.print(f"  Duplicates: {len(duplicates)}")

    if dry_run:
        console.print("\n[yellow]Dry run - no records imported[/yellow]\n")
        return

    # Slack approval gate
    if not approve:
        notifier = SlackNotifier(settings=settings)
        notifier.send_import_preview(new_records, duplicates)
        console.print("\n[yellow]Approval request sent to Slack. Use --approve to import.[/yellow]\n")
        return

    # Import
    imported = importer.import_batch(new_records)
    console.print(f"\n[bold green]{len(imported)} records imported to Notion[/bold green]\n")


# ---------------------------------------------------------------------------
# SHORTAGES
# ---------------------------------------------------------------------------
@cli.command()
@click.option("--check", is_flag=True, help="Check for new shortages")
@click.option("--alert", is_flag=True, help="Send alerts via Slack")
def shortages(check: bool, alert: bool):
    """Monitor FDA Drug Shortage database for opportunities."""
    from src.sourcing.drug_shortage_monitor import DrugShortageMonitor

    settings = get_settings()
    monitor = DrugShortageMonitor(settings=settings)

    console.print("\n[bold]Checking FDA Drug Shortage database...[/bold]\n")
    results = monitor.check_shortages()

    table = Table(title="Drug Shortages")
    table.add_column("Drug Name", style="cyan")
    table.add_column("Status")
    table.add_column("Catalog Match", justify="center")
    table.add_column("Compounder Need", justify="center")

    for s in results:
        table.add_row(
            s["drug_name"],
            s["status"],
            "[green]YES[/green]" if s.get("matches_catalog") else "",
            "[green]YES[/green]" if s.get("matches_compounder_needs") else "",
        )

    console.print(table)
    console.print(f"\n[bold]{len(results)} shortages found[/bold]\n")

    if alert:
        from src.notifications.slack_notifier import SlackNotifier
        notifier = SlackNotifier(settings=settings)
        notifier.send_shortage_alert(results)
        console.print("[green]Alert sent to Slack[/green]\n")


# ---------------------------------------------------------------------------
# DEMAND
# ---------------------------------------------------------------------------
@cli.command()
@click.option("--report", is_flag=True, help="Generate demand report")
@click.option("--top", "-n", type=int, default=20, help="Show top N products")
def demand(report: bool, top: int):
    """Track product demand from prospect interactions."""
    from src.sourcing.demand_tracker import DemandTracker

    settings = get_settings()
    tracker = DemandTracker(settings=settings)

    console.print("\n[bold]Product Demand Report[/bold]\n")
    rankings = tracker.get_demand_rankings(limit=top)

    table = Table(title=f"Top {top} Requested Products")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Product", style="cyan")
    table.add_column("Requests", justify="right")
    table.add_column("Unique Prospects", justify="right")
    table.add_column("Available", justify="center")

    for i, item in enumerate(rankings, 1):
        table.add_row(
            str(i),
            item["product_name"],
            str(item["request_count"]),
            str(item["unique_prospects"]),
            "[green]YES[/green]" if item.get("is_available") else "[red]NO[/red]",
        )

    console.print(table)


# ---------------------------------------------------------------------------
# PIPELINE (end-to-end)
# ---------------------------------------------------------------------------
@cli.command()
@click.option("--states", "-s", default=None, help="Comma-separated state codes")
@click.option("--notify", is_flag=True, help="Send Slack notification")
@click.option("--auto-approve", is_flag=True, help="Skip approval gate")
def pipeline(states: str | None, notify: bool, auto_approve: bool):
    """Run the full lead generation pipeline end-to-end."""
    settings = get_settings()
    state_list = (
        [s.strip().upper() for s in states.split(",")]
        if states
        else settings.tier_1_state_list
    )

    console.print(f"\n[bold]Running full pipeline for: {', '.join(state_list)}[/bold]\n")

    # Stage 1: Scrape
    console.print("[bold cyan]Stage 1: Scraping...[/bold cyan]")
    from src.scrapers import get_scraper
    raw_dir = settings.data_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    all_records = []
    for state_code in state_list:
        try:
            scraper = get_scraper(state_code)
            records = scraper.run()
            all_records.extend(records)
            out_file = raw_dir / f"{state_code}_{date.today().isoformat()}.csv"
            _write_records_csv(records, out_file)
            console.print(f"  {state_code}: {len(records)} records")
        except Exception as e:
            console.print(f"  [red]{state_code}: FAILED - {e}[/red]")

    # Stage 2: Enrich
    console.print("\n[bold cyan]Stage 2: Enriching...[/bold cyan]")
    from src.enrichment.pipeline import EnrichmentPipeline
    pipeline_inst = EnrichmentPipeline(settings=settings)
    enriched = pipeline_inst.enrich_batch(all_records)
    console.print(f"  {len(enriched)} records enriched")

    # Stage 3: Score
    console.print("\n[bold cyan]Stage 3: Scoring...[/bold cyan]")
    from src.scoring.scorer import LeadScorer
    scorer = LeadScorer(settings=settings)
    scored = [scorer.score_record(r) for r in enriched]

    scores = [int(r.get("score", 0)) for r in scored]
    hot = sum(1 for s in scores if s >= 70)
    warm = sum(1 for s in scores if 50 <= s < 70)
    console.print(f"  {len(scored)} scored | {hot} hot | {warm} warm")

    # Stage 4: Dedup + Import
    console.print("\n[bold cyan]Stage 4: Importing to Notion...[/bold cyan]")
    from src.notion.prospect_importer import ProspectImporter
    importer = ProspectImporter(settings=settings)
    new_records, duplicates = importer.check_duplicates(scored)
    console.print(f"  {len(new_records)} new | {len(duplicates)} duplicates")

    if notify:
        from src.notifications.slack_notifier import SlackNotifier
        notifier = SlackNotifier(settings=settings)
        notifier.send_import_preview(new_records, duplicates)
        console.print("  Slack notification sent")

    if auto_approve and new_records:
        imported = importer.import_batch(new_records)
        console.print(f"  [green]{len(imported)} imported to Notion[/green]")
    elif new_records:
        console.print("  [yellow]Awaiting approval (use --auto-approve to skip)[/yellow]")

    # Write final scored output
    scored_dir = settings.data_dir / "scored"
    scored_dir.mkdir(parents=True, exist_ok=True)
    out_file = scored_dir / f"pipeline_{date.today().isoformat()}.csv"
    _write_records_csv(scored, out_file)

    console.print(f"\n[bold green]Pipeline complete. Output: {out_file}[/bold green]\n")


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------
def _write_records_csv(records: list[dict], path: Path):
    """Write a list of record dicts to a CSV file."""
    if not records:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def _read_records_csv(path: Path) -> list[dict]:
    """Read a CSV file into a list of record dicts."""
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cli()
