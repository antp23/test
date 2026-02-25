"""Tests for the pharmacy segment classifier."""

from src.enrichment.classifier import classify_pharmacy


class TestClassifier:
    """Test segment classification logic."""

    def test_503b_outsourcing_keyword(self):
        assert classify_pharmacy("ABC Outsourcing Facility") == "503B"

    def test_503b_keyword_in_name(self):
        assert classify_pharmacy("National 503B Sterile Compounding") == "503B"

    def test_503b_fda_registered_override(self):
        """FDA 503B registration should override keyword matching."""
        assert classify_pharmacy("Generic Pharmacy LLC", is_503b_registered=True) == "503B"

    def test_503a_compounding(self):
        assert classify_pharmacy("Sunshine Compounding Pharmacy") == "503A"

    def test_503a_compound_keyword(self):
        assert classify_pharmacy("Custom Compound Rx") == "503A"

    def test_503a_license_type(self):
        assert classify_pharmacy("Smith Pharmacy", license_type="Compounding Pharmacy") == "503A"

    def test_mail_order_keyword(self):
        assert classify_pharmacy("MedMail Order Pharmacy") == "Mail Order"

    def test_mail_order_online(self):
        assert classify_pharmacy("Online Pharmacy Direct") == "Mail Order"

    def test_mail_order_non_resident(self):
        assert classify_pharmacy("ABC Pharmacy", license_type="Non-Resident Pharmacy") == "Mail Order"

    def test_specialty(self):
        assert classify_pharmacy("Oncology Specialty Pharmacy") == "Specialty"

    def test_specialty_infusion(self):
        assert classify_pharmacy("Home Infusion Solutions") == "Specialty"

    def test_hospital(self):
        assert classify_pharmacy("Memorial Hospital Pharmacy") == "Hospital"

    def test_hospital_medical_center(self):
        assert classify_pharmacy("Regional Medical Center Pharmacy") == "Hospital"

    def test_bm_default(self):
        """Generic names should default to B&M."""
        assert classify_pharmacy("Corner Drug Store") == "B&M"

    def test_bm_retail(self):
        assert classify_pharmacy("ABC Pharmacy") == "B&M"

    def test_sterile_license_type(self):
        """Sterile compounding license type → 503A."""
        assert classify_pharmacy("XYZ Pharmacy", license_type="Sterile Compounding") == "503A"

    def test_empty_name(self):
        assert classify_pharmacy("") == "B&M"

    def test_case_insensitive(self):
        assert classify_pharmacy("COMPOUNDING PHARMACY OF FLORIDA") == "503A"
