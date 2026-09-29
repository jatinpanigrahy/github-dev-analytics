"""Utility functions for data transformations and date handling."""

from datetime import datetime, timezone


def calculate_account_age(created_at_str: str | None) -> tuple[str, str]:
    """Compute human-readable account tenure and formatted creation date.

    Args:
        created_at_str: ISO-8601 formatted date string from GitHub (UTC), or None.

    Returns:
        A tuple containing:
            - tenure_duration_string: Human-readable tenure in years and months (e.g. '2y 4m').
            - formatted_date_string: Formatted calendar date (e.g. 'Sep 30, 2026').
    """
    if not created_at_str:
        return "Unknown", "Unknown"

    created_dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
    delta = datetime.now(timezone.utc) - created_dt
    years = delta.days // 365
    months = (delta.days % 365) // 30

    return f"{years}y {months}m", created_dt.strftime("%b %d, %Y")
