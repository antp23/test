"""Tests for the lead scoring engine."""

import pytest

from src.scoring.scorer import LeadScorer, _is_true, _to_int


@pytest.fixture
def scorer(settings):
    return LeadScorer(settings=settings)


class TestScorer:
    """Test lead scoring calculations."""

    def test_503b_highest_score(self, scorer, sample_enriched_records):
        """503B outsourcing facilities should get the highest base score."""
        record = sample_enriched_records[1]  # ABC Outsourcing (503B)
        scored = scorer.score_record(record)
        assert scored["score"] >= 70  # Should be Hot tier
        assert scored["priority"] == "Hot"
        assert scored["tier"] == 1

    def test_503a_compounding_warm(self, scorer, sample_enriched_records):
        """503A compounding pharmacy should score well."""
        record = sample_enriched_records[0]  # Sunshine Compounding (503A)
        scored = scorer.score_record(record)
        assert scored["score"] >= 50  # Should be at least Warm
        assert scored["priority"] in ("Hot", "Warm")

    def test_bm_retail_lowest(self, scorer, sample_enriched_records):
        """B&M retail with no enrichment should score lowest."""
        record = sample_enriched_records[3]  # Corner Drug Store (B&M)
        scored = scorer.score_record(record)
        assert scored["score"] < 50  # Should be Cold or Watch

    def test_segment_scoring(self, scorer):
        """Test segment base scores."""
        for segment, expected_min in [("503B", 30), ("503A", 25), ("Mail Order", 20), ("B&M", 10)]:
            record = {"segment": segment, "state": "FL"}
            scored = scorer.score_record(record)
            assert scored["score"] >= expected_min

    def test_accreditation_bonus(self, scorer):
        """PCAB accreditation should add 15 points."""
        base = {"segment": "B&M", "state": "FL"}
        with_pcab = {**base, "is_pcab_accredited": "True"}

        base_score = scorer.score_record(base)["score"]
        pcab_score = scorer.score_record(with_pcab)["score"]
        assert pcab_score == base_score + 15

    def test_employee_count_bonus(self, scorer):
        """More employees should mean higher score."""
        base = {"segment": "B&M", "state": "FL"}
        with_emp = {**base, "employee_count": "25"}

        base_score = scorer.score_record(base)["score"]
        emp_score = scorer.score_record(with_emp)["score"]
        assert emp_score > base_score

    def test_state_tier_bonus(self, scorer):
        """Tier 1 states should get more points than Tier 3."""
        tier1 = {"segment": "B&M", "state": "FL"}
        tier3 = {"segment": "B&M", "state": "WY"}

        score1 = scorer.score_record(tier1)["score"]
        score3 = scorer.score_record(tier3)["score"]
        assert score1 > score3

    def test_website_bonus(self, scorer):
        """Having a website adds 5 points."""
        base = {"segment": "B&M", "state": "FL"}
        with_site = {**base, "website": "https://example.com"}

        base_score = scorer.score_record(base)["score"]
        site_score = scorer.score_record(with_site)["score"]
        assert site_score == base_score + 5

    def test_tier_thresholds(self, scorer):
        """Verify tier threshold classifications."""
        # High score → Hot
        hot = scorer.score_record({
            "segment": "503B", "state": "FL",
            "is_503b_registered": "True", "is_pcab_accredited": "True",
            "employee_count": "100",
        })
        assert hot["priority"] == "Hot"
        assert hot["tier"] == 1

    def test_score_breakdown_included(self, scorer):
        """Score breakdown should be included in output."""
        record = {"segment": "503A", "state": "FL"}
        scored = scorer.score_record(record)
        assert "score_breakdown" in scored
        assert scored["scored_at"]

    def test_empty_record(self, scorer):
        """Empty record should still produce a valid score."""
        scored = scorer.score_record({})
        assert "score" in scored
        assert scored["score"] >= 0


class TestHelpers:
    def test_is_true_bool(self):
        assert _is_true(True) is True
        assert _is_true(False) is False

    def test_is_true_string(self):
        assert _is_true("True") is True
        assert _is_true("true") is True
        assert _is_true("1") is True
        assert _is_true("False") is False
        assert _is_true("") is False

    def test_to_int(self):
        assert _to_int("42") == 42
        assert _to_int(42) == 42
        assert _to_int(None) == 0
        assert _to_int("abc") == 0
        assert _to_int("") == 0
