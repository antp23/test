"""Lead scoring engine.

Assigns a numeric score to every prospect so reps automatically work the
most promising targets first.

Score ranges:
  70+ = Priority Hot, Tier 1 (Strategic)
  50-69 = Warm, Tier 2 (Target)
  30-49 = Cold, Tier 3 (Opportunistic)
  <30 = Tier 4 (Watch List)
"""

import logging
from datetime import datetime

from src.config import Settings

logger = logging.getLogger(__name__)

# Scoring weights - configurable tuning knobs
SCORING_RULES = {
    # Segment points
    "segment_scores": {
        "503B": 30,
        "503A": 25,
        "Mail Order": 20,
        "Specialty": 15,
        "Hospital": 15,
        "B&M": 10,
        "Unknown": 0,
    },
    # Accreditation bonuses
    "pcab_bonus": 15,
    "achc_bonus": 10,
    "fda_503b_bonus": 15,
    # Employee count thresholds
    "employee_thresholds": [
        (50, None, 15),   # 50+ employees
        (10, 49, 10),     # 10-49 employees
        (1, 9, 5),        # 1-9 employees
    ],
    # State tier points
    "state_tier_scores": {
        1: 10,  # Tier 1 states
        2: 5,   # Tier 2 states
        3: 0,   # Other states
    },
    # Other bonuses
    "website_bonus": 5,
    "google_reviews_50_plus": 5,
    "google_reviews_20_plus": 3,
    "sterile_license_bonus": 10,
    # Source quality
    "source_scores": {
        "referral": 25,
        "pcab_directory": 10,
        "achc_directory": 10,
        "state_board": 5,
    },
    # Tier thresholds
    "tier_thresholds": {
        "hot": 70,
        "warm": 50,
        "cold": 30,
    },
}


class LeadScorer:
    """Scores and classifies pharmacy prospects."""

    def __init__(self, settings: Settings | None = None, rules: dict | None = None):
        from src.config import get_settings
        self.settings = settings or get_settings()
        self.rules = rules or SCORING_RULES

    def score_record(self, record: dict) -> dict:
        """Score a single enriched pharmacy record.

        Adds score, priority, tier, and score_breakdown fields to the record.
        Returns the updated record dict.
        """
        scored = dict(record)
        breakdown = {}
        total = 0

        # 1. Segment score
        segment = record.get("segment", "Unknown")
        segment_pts = self.rules["segment_scores"].get(segment, 0)
        breakdown["segment"] = segment_pts
        total += segment_pts

        # 2. Accreditation bonuses
        if _is_true(record.get("is_pcab_accredited")):
            pts = self.rules["pcab_bonus"]
            breakdown["pcab"] = pts
            total += pts

        if _is_true(record.get("is_achc_accredited")):
            pts = self.rules["achc_bonus"]
            breakdown["achc"] = pts
            total += pts

        if _is_true(record.get("is_503b_registered")):
            pts = self.rules["fda_503b_bonus"]
            breakdown["fda_503b"] = pts
            total += pts

        # 3. Employee count
        emp_count = _to_int(record.get("employee_count"))
        if emp_count:
            for low, high, pts in self.rules["employee_thresholds"]:
                if high is None:
                    if emp_count >= low:
                        breakdown["employees"] = pts
                        total += pts
                        break
                elif low <= emp_count <= high:
                    breakdown["employees"] = pts
                    total += pts
                    break

        # 4. State tier
        state = record.get("state", "")
        state_tier = self.settings.get_state_tier(state)
        tier_pts = self.rules["state_tier_scores"].get(state_tier, 0)
        if tier_pts:
            breakdown["state_tier"] = tier_pts
            total += tier_pts

        # 5. Website bonus
        if record.get("website") or record.get("google_website"):
            pts = self.rules["website_bonus"]
            breakdown["website"] = pts
            total += pts

        # 6. Google reviews
        review_count = _to_int(record.get("google_review_count"))
        if review_count >= 50:
            pts = self.rules["google_reviews_50_plus"]
            breakdown["reviews"] = pts
            total += pts
        elif review_count >= 20:
            pts = self.rules["google_reviews_20_plus"]
            breakdown["reviews"] = pts
            total += pts

        # 7. Sterile license bonus
        if _is_true(record.get("has_sterile_license")):
            pts = self.rules["sterile_license_bonus"]
            breakdown["sterile_license"] = pts
            total += pts

        # 8. Source quality
        source = record.get("source", "").lower()
        for source_key, pts in self.rules["source_scores"].items():
            if source_key in source:
                breakdown["source"] = pts
                total += pts
                break

        # Determine tier and priority
        thresholds = self.rules["tier_thresholds"]
        if total >= thresholds["hot"]:
            priority = "Hot"
            tier = 1
        elif total >= thresholds["warm"]:
            priority = "Warm"
            tier = 2
        elif total >= thresholds["cold"]:
            priority = "Cold"
            tier = 3
        else:
            priority = "Watch List"
            tier = 4

        scored["score"] = total
        scored["priority"] = priority
        scored["tier"] = tier
        scored["score_breakdown"] = str(breakdown)
        scored["scored_at"] = datetime.utcnow().isoformat()

        return scored


def _is_true(value) -> bool:
    """Check if a value represents True (handles string 'True', bool, etc.)."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes")
    return bool(value)


def _to_int(value) -> int:
    """Safely convert a value to int, defaulting to 0."""
    if value is None:
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0
