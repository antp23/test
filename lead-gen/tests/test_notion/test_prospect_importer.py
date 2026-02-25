"""Tests for Notion prospect importer property mapping."""

from src.notion.prospect_importer import (
    _checkbox,
    _date,
    _email,
    _number,
    _phone,
    _rich_text,
    _select,
    _title,
    _url,
)


class TestPropertyBuilders:
    """Test Notion property type builders."""

    def test_title(self):
        result = _title("Test Pharmacy")
        assert result == {"title": [{"text": {"content": "Test Pharmacy"}}]}

    def test_title_empty(self):
        result = _title("")
        assert result == {"title": [{"text": {"content": ""}}]}

    def test_rich_text(self):
        result = _rich_text("Some notes")
        assert result == {"rich_text": [{"text": {"content": "Some notes"}}]}

    def test_number_valid(self):
        assert _number(42) == {"number": 42.0}
        assert _number("42") == {"number": 42.0}

    def test_number_none(self):
        assert _number(None) == {"number": None}
        assert _number("") == {"number": None}

    def test_select(self):
        assert _select("503A") == {"select": {"name": "503A"}}

    def test_select_empty(self):
        assert _select("") == {"select": None}

    def test_checkbox_bool(self):
        assert _checkbox(True) == {"checkbox": True}
        assert _checkbox(False) == {"checkbox": False}

    def test_checkbox_string(self):
        assert _checkbox("True") == {"checkbox": True}
        assert _checkbox("False") == {"checkbox": False}

    def test_url(self):
        assert _url("https://example.com") == {"url": "https://example.com"}
        assert _url("") == {"url": None}

    def test_phone(self):
        assert _phone("(813) 555-1234") == {"phone_number": "(813) 555-1234"}
        assert _phone("") == {"phone_number": None}

    def test_email(self):
        assert _email("test@example.com") == {"email": "test@example.com"}
        assert _email("") == {"email": None}

    def test_date(self):
        assert _date("2026-02-25") == {"date": {"start": "2026-02-25"}}
        assert _date("") == {"date": None}
