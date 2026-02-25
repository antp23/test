"""Shared test fixtures."""

import pytest

from src.config import Settings


@pytest.fixture
def settings():
    """Test settings with placeholder API keys."""
    return Settings(
        database_url="sqlite:///:memory:",
        apollo_api_key="",
        google_places_api_key="",
        notion_api_key="",
        notion_prospects_db_id="",
        notion_vendors_db_id="",
        slack_webhook_url="",
        tier_1_states="FL,TX,CA,NY,NJ,PA,OH,GA,NC,AZ",
        tier_2_states="IL,MI,VA,MA,TN,MO,WI,MN,MD,IN",
        reps="Colin,Kevin",
    )


@pytest.fixture
def sample_pharmacy_records():
    """Sample raw pharmacy records for testing."""
    return [
        {
            "business_name": "Sunshine Compounding Pharmacy",
            "license_number": "PH-123456",
            "license_type": "Compounding Pharmacy",
            "address": "123 Main St",
            "city": "Tampa",
            "state": "FL",
            "zip_code": "33601",
            "phone": "(813) 555-1234",
            "license_status": "Active",
            "expiration_date": "2026-12-31",
            "scrape_date": "2026-02-25",
            "source": "FL_DOH",
        },
        {
            "business_name": "ABC Outsourcing Facility",
            "license_number": "PH-789012",
            "license_type": "Outsourcing Facility",
            "address": "456 Oak Ave",
            "city": "Dallas",
            "state": "TX",
            "zip_code": "75201",
            "phone": "(214) 555-5678",
            "license_status": "Active",
            "expiration_date": "2027-06-30",
            "scrape_date": "2026-02-25",
            "source": "TX_TSBP",
        },
        {
            "business_name": "MedMail Pharmacy Services",
            "license_number": "PH-345678",
            "license_type": "Non-Resident Pharmacy",
            "address": "789 Elm St",
            "city": "Phoenix",
            "state": "AZ",
            "zip_code": "85001",
            "phone": "(602) 555-9012",
            "license_status": "Active",
            "expiration_date": "2026-09-15",
            "scrape_date": "2026-02-25",
            "source": "AZ_BOP",
        },
        {
            "business_name": "Corner Drug Store",
            "license_number": "PH-111222",
            "license_type": "Retail Pharmacy",
            "address": "321 Pine Rd",
            "city": "Atlanta",
            "state": "GA",
            "zip_code": "30301",
            "phone": "(404) 555-3456",
            "license_status": "Active",
            "expiration_date": "2026-08-01",
            "scrape_date": "2026-02-25",
            "source": "GA_SOS",
        },
    ]


@pytest.fixture
def sample_enriched_records(sample_pharmacy_records):
    """Sample enriched records with Apollo/Google/FDA data."""
    records = [dict(r) for r in sample_pharmacy_records]

    # Compounding pharmacy - 503A
    records[0].update({
        "segment": "503A",
        "is_503b_registered": "False",
        "is_pcab_accredited": "True",
        "is_achc_accredited": "False",
        "has_sterile_license": "True",
        "employee_count": "15",
        "website": "https://sunshinecompounding.com",
        "google_review_count": "52",
        "contact_name": "Dr. Jane Smith",
        "contact_email": "jane@sunshinecompounding.com",
        "contact_title": "Pharmacist in Charge",
    })

    # Outsourcing facility - 503B
    records[1].update({
        "segment": "503B",
        "is_503b_registered": "True",
        "is_pcab_accredited": "False",
        "is_achc_accredited": "True",
        "has_sterile_license": "True",
        "employee_count": "75",
        "website": "https://abcoutsourcing.com",
        "google_review_count": "12",
        "contact_name": "John Doe",
        "contact_email": "john@abcoutsourcing.com",
        "contact_title": "Director of Purchasing",
    })

    # Mail order
    records[2].update({
        "segment": "Mail Order",
        "is_503b_registered": "False",
        "is_pcab_accredited": "False",
        "is_achc_accredited": "False",
        "has_sterile_license": "False",
        "employee_count": "8",
        "website": "https://medmail.com",
        "google_review_count": "200",
        "contact_name": "",
        "contact_email": "",
        "contact_title": "",
    })

    # B&M retail
    records[3].update({
        "segment": "B&M",
        "is_503b_registered": "False",
        "is_pcab_accredited": "False",
        "is_achc_accredited": "False",
        "has_sterile_license": "False",
        "employee_count": "3",
        "website": "",
        "google_review_count": "8",
        "contact_name": "",
        "contact_email": "",
        "contact_title": "",
    })

    return records
