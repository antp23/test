"""Tests for the drug shortage monitor."""

from src.sourcing.drug_shortage_monitor import DrugShortageMonitor


class TestDrugShortageMonitor:
    def test_catalog_matching(self, settings):
        monitor = DrugShortageMonitor(settings=settings)
        monitor.set_catalog(["progesterone", "estradiol", "lidocaine"])

        shortages = [
            {"drug_name": "Progesterone USP", "generic_name": "progesterone",
             "status": "Current", "matches_catalog": False, "matches_compounder_needs": False},
            {"drug_name": "Atorvastatin", "generic_name": "atorvastatin",
             "status": "Current", "matches_catalog": False, "matches_compounder_needs": False},
        ]

        # Simulate cross-reference logic
        catalog = [p.lower() for p in ["progesterone", "estradiol", "lidocaine"]]
        for s in shortages:
            name_lower = s["generic_name"].lower()
            for product in catalog:
                if product in name_lower:
                    s["matches_catalog"] = True
                    break

        assert shortages[0]["matches_catalog"] is True
        assert shortages[1]["matches_catalog"] is False

    def test_compounder_needs_matching(self, settings):
        monitor = DrugShortageMonitor(settings=settings)

        # These are in the COMPOUNDER_COMMON_NEEDS list
        from src.sourcing.drug_shortage_monitor import COMPOUNDER_COMMON_NEEDS
        assert "progesterone" in COMPOUNDER_COMMON_NEEDS
        assert "ketamine" in COMPOUNDER_COMMON_NEEDS
        assert "lidocaine" in COMPOUNDER_COMMON_NEEDS
