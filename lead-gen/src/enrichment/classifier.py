"""Pharmacy segment classifier.

Classifies pharmacies into segments based on business name and license type:
- 503A (Compounding Pharmacy)
- 503B (Outsourcing Facility)
- Mail Order
- B&M (Brick & Mortar / Retail)
- Specialty
- Hospital
"""

import logging
import re

logger = logging.getLogger(__name__)

# Keyword patterns for each segment (checked in priority order)
SEGMENT_PATTERNS = {
    "503B": [
        r"\boutsourcing\b",
        r"\b503b\b",
        r"\boutsource\b",
    ],
    "503A": [
        r"\bcompound(?:ing)?\b",
        r"\b503a\b",
        r"\bcompound\s+pharmacy\b",
        r"\bcustom\s+compound\b",
    ],
    "Mail Order": [
        r"\bmail\s*order\b",
        r"\bmail[\s-]?order\b",
        r"\bonline\s+pharmacy\b",
        r"\binternet\s+pharmacy\b",
        r"\bnon[\s-]?resident\b",
        r"\bmail\s+service\b",
    ],
    "Specialty": [
        r"\bspecialty\b",
        r"\binfusion\b",
        r"\boncology\b",
        r"\bnuclear\b",
        r"\bradiopharmac\b",
        r"\bhome\s+infusion\b",
    ],
    "Hospital": [
        r"\bhospital\b",
        r"\bmedical\s+center\b",
        r"\bhealth\s+system\b",
        r"\bclinic(?:al)?\s+pharmacy\b",
        r"\binstitution(?:al)?\b",
    ],
}


def classify_pharmacy(
    business_name: str,
    license_type: str = "",
    is_503b_registered: bool = False,
) -> str:
    """Classify a pharmacy into a segment.

    Args:
        business_name: Legal business name from state board.
        license_type: License type/category from state board.
        is_503b_registered: Whether FDA 503B cross-reference matched.

    Returns:
        Segment string: "503B", "503A", "Mail Order", "Specialty",
        "Hospital", or "B&M" (default).
    """
    # FDA 503B registration overrides keyword matching
    if is_503b_registered:
        return "503B"

    # Combine name and license type for matching
    text = f"{business_name} {license_type}".lower()

    # Check patterns in priority order
    for segment, patterns in SEGMENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return segment

    # License type specific checks
    license_lower = license_type.lower()
    if "sterile" in license_lower:
        return "503A"  # Sterile compounding → 503A
    if "non-resident" in license_lower or "nonresident" in license_lower:
        return "Mail Order"

    # Default: Brick & Mortar retail pharmacy
    return "B&M"
