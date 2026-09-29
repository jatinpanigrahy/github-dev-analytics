"""Unit tests for utility functions and date parsing helpers."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from src.utils import calculate_account_age


def test_calculate_account_age_none() -> None:
    """Verify calculate_account_age handles missing or null timestamps gracefully."""
    tenure, formatted_date = calculate_account_age(None)
    assert tenure == "Unknown"
    assert formatted_date == "Unknown"


@patch("src.utils.datetime")
def test_calculate_account_age_valid(mock_datetime: MagicMock) -> None:
    """Verify tenure calculation and date formatting against a deterministic reference date."""
    fixed_now = datetime(2026, 10, 1, tzinfo=timezone.utc)
    mock_datetime.now.return_value = fixed_now

    mock_datetime.fromisoformat.side_effect = datetime.fromisoformat

    test_date_str = "2024-08-30T12:00:00Z"

    tenure, formatted_date = calculate_account_age(test_date_str)
    assert tenure == "2y 1m"
    assert formatted_date == "Aug 30, 2024"
