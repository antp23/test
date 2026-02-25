"""Tests for the base scraper and scraper registry."""

import pytest

from src.scrapers import SCRAPER_REGISTRY, get_scraper
from src.scrapers.base import BaseScraper, PharmacyRecord


class TestPharmacyRecord:
    def test_to_dict(self):
        record = PharmacyRecord(
            business_name="Test Pharmacy",
            license_number="PH-001",
            license_type="Retail",
            address="123 Main St",
            city="Tampa",
            state="FL",
            zip_code="33601",
            phone="(813) 555-1234",
            license_status="Active",
        )
        d = record.to_dict()
        assert d["business_name"] == "Test Pharmacy"
        assert d["license_number"] == "PH-001"
        assert d["state"] == "FL"
        assert d["phone"] == "(813) 555-1234"

    def test_phone_normalization(self):
        record = PharmacyRecord(
            business_name="Test",
            license_number="001",
            phone="8135551234",
        )
        d = record.to_dict()
        assert d["phone"] == "(813) 555-1234"

    def test_empty_phone(self):
        record = PharmacyRecord(
            business_name="Test",
            license_number="001",
            phone="",
        )
        d = record.to_dict()
        assert d["phone"] == ""


class TestScraperRegistry:
    def test_all_tier1_states_registered(self):
        tier1_states = ["FL", "TX", "CA", "NY", "NJ", "PA", "OH", "GA", "NC", "AZ"]
        for state in tier1_states:
            assert state in SCRAPER_REGISTRY, f"Missing scraper for {state}"

    def test_get_scraper_valid(self):
        scraper = get_scraper("FL")
        assert isinstance(scraper, BaseScraper)
        assert scraper.state_code == "FL"

    def test_get_scraper_case_insensitive(self):
        scraper = get_scraper("fl")
        assert scraper.state_code == "FL"

    def test_get_scraper_invalid(self):
        with pytest.raises(ValueError, match="No scraper available"):
            get_scraper("ZZ")

    def test_each_scraper_has_required_properties(self):
        for code, cls in SCRAPER_REGISTRY.items():
            scraper = cls()
            assert scraper.state_code == code
            assert len(scraper.state_name) > 0
            assert scraper.source_url.startswith("http")
