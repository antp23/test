"""Slack notification system using Block Kit formatting.

Sends clean, purposeful messages:
- Import preview summaries for approval
- Drug shortage alerts
- Pipeline execution results
- Error notifications
"""

import json
import logging
from collections import Counter

import httpx

from src.config import Settings

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Sends formatted Slack notifications via webhook."""

    def __init__(self, settings: Settings | None = None):
        from src.config import get_settings
        self.settings = settings or get_settings()
        self.webhook_url = self.settings.slack_webhook_url

    def _send(self, blocks: list[dict], text: str = ""):
        """Send a Block Kit message via Slack webhook."""
        if not self.webhook_url:
            logger.warning("SLACK_WEBHOOK_URL not configured, skipping notification")
            return

        payload = {
            "text": text or "Lead Gen Pipeline Notification",
            "blocks": blocks,
        }

        try:
            response = httpx.post(
                self.webhook_url,
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            logger.info("Slack notification sent successfully")
        except Exception as e:
            logger.error("Failed to send Slack notification: %s", e)

    def send_import_preview(self, new_records: list[dict], duplicates: list[dict]):
        """Send pre-import summary for Anthony's approval.

        Format:
        47 new prospects ready:
        12 503A (avg score 62) | 3 503B (avg score 78)
        8 Mail Order (avg score 48) | 24 B&M (avg score 35)
        6 potential duplicates flagged. Approve?
        """
        # Aggregate by segment
        segment_counts = Counter()
        segment_scores: dict[str, list[int]] = {}
        for r in new_records:
            seg = r.get("segment", "Unknown")
            segment_counts[seg] += 1
            score = int(r.get("score", 0))
            segment_scores.setdefault(seg, []).append(score)

        # Build segment summary lines
        segment_lines = []
        for seg in ["503B", "503A", "Mail Order", "Specialty", "Hospital", "B&M", "Unknown"]:
            count = segment_counts.get(seg, 0)
            if count > 0:
                scores = segment_scores[seg]
                avg = sum(scores) // len(scores)
                segment_lines.append(f"*{count}* {seg} (avg score {avg})")

        # Priority breakdown
        priorities = Counter(r.get("priority", "Unknown") for r in new_records)

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "Lead Import Ready for Review"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{len(new_records)} new prospects* ready for import.",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*By Segment:*\n" + " | ".join(segment_lines),
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*By Priority:*\n"
                        f":fire: {priorities.get('Hot', 0)} Hot | "
                        f":large_orange_circle: {priorities.get('Warm', 0)} Warm | "
                        f":large_blue_circle: {priorities.get('Cold', 0)} Cold | "
                        f":white_circle: {priorities.get('Watch List', 0)} Watch"
                    ),
                },
            },
        ]

        if duplicates:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":warning: *{len(duplicates)} potential duplicates* flagged for review.",
                },
            })

        blocks.extend([
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Run `python -m src.cli import-leads --approve` to import.",
                },
            },
        ])

        self._send(blocks, text=f"{len(new_records)} new prospects ready for review")

    def send_shortage_alert(self, shortages: list[dict]):
        """Send drug shortage alert to Anthony."""
        catalog_matches = [s for s in shortages if s.get("matches_catalog")]
        compounder_matches = [s for s in shortages if s.get("matches_compounder_needs")]

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "Drug Shortage Alert"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*{len(shortages)} shortages detected this check.*\n"
                        f":package: {len(catalog_matches)} match Safeway catalog (sales opportunity)\n"
                        f":pill: {len(compounder_matches)} match compounder needs (sourcing opportunity)"
                    ),
                },
            },
        ]

        if catalog_matches:
            blocks.append({"type": "divider"})
            lines = [f"- {s['drug_name']} ({s.get('status', 'Unknown')})" for s in catalog_matches[:10]]
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Catalog Matches (sell now):*\n" + "\n".join(lines),
                },
            })

        if compounder_matches:
            lines = [f"- {s['drug_name']} ({s.get('status', 'Unknown')})" for s in compounder_matches[:10]]
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Compounder Needs (source opportunity):*\n" + "\n".join(lines),
                },
            })

        self._send(blocks, text=f"{len(shortages)} drug shortages detected")

    def send_pipeline_complete(
        self, total_scraped: int, total_enriched: int, total_scored: int,
        hot: int, warm: int, states: list[str],
    ):
        """Send pipeline completion summary."""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "Pipeline Run Complete"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*States:* {', '.join(states)}\n"
                        f"*Scraped:* {total_scraped} | "
                        f"*Enriched:* {total_enriched} | "
                        f"*Scored:* {total_scored}\n"
                        f":fire: {hot} hot | :large_orange_circle: {warm} warm"
                    ),
                },
            },
        ]
        self._send(blocks, text=f"Pipeline complete: {total_scored} records processed")

    def send_error(self, component: str, error: str):
        """Send error alert."""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "Pipeline Error"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Component:* {component}\n*Error:* ```{error}```",
                },
            },
        ]
        self._send(blocks, text=f"Pipeline error in {component}")
