"""Phone number normalization utilities."""

import re
from typing import Optional

import phonenumbers


def normalize_phone(raw: Optional[str]) -> Optional[str]:
    """Normalize a phone number to (XXX) XXX-XXXX format.

    Returns None if the input can't be parsed as a valid US phone number.
    """
    if not raw or not raw.strip():
        return None

    cleaned = re.sub(r"[^\d+]", "", raw.strip())

    if not cleaned:
        return None

    try:
        parsed = phonenumbers.parse(cleaned, "US")
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.NATIONAL
            )
    except phonenumbers.NumberParseException:
        pass

    # Fallback: if we have exactly 10 digits, format manually
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    if len(digits) == 11 and digits[0] == "1":
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"

    return None
