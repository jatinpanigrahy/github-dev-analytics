"""Network integration layer interfacing with the GitHub REST API."""

import requests
import streamlit as st


def handle_response(r: requests.Response) -> dict:
    """Evaluate an HTTP response from the GitHub API and normalize into an outcome dictionary.

    Args:
        r: Raw requests.Response instance.

    Returns:
        Dictionary containing standardized outcome status ('success' or 'error')
        along with the JSON payload or failure diagnostics.
    """
    if r.status_code == 200:
        return {"status": "success", "data": r.json()}
    elif r.status_code == 403:
        return {"status": "error", "reason": "rate_limit", "code": 403}
    elif r.status_code == 404:
        return {"status": "error", "reason": "not_found", "code": 404}
    else:
        return {"status": "error", "reason": "unknown", "code": r.status_code}


@st.cache_data(ttl=3600)
def fetch_profile(username: str) -> dict:
    """Fetch GitHub user profile metadata with client-side caching and timeout guard.

    Args:
        username: Target GitHub username.

    Returns:
        Normalized dictionary with user profile payload or error diagnostics.
    """
    try:
        r = requests.get(
            f"https://api.github.com/users/{username}",
            timeout=10,
        )
        return handle_response(r)
    except requests.exceptions.RequestException:
        return {"status": "error", "reason": "network_timeout"}


@st.cache_data(ttl=3600)
def fetch_repos(username: str) -> dict:
    """Fetch up to 100 public repositories for a user, sorted by last updated.

    Args:
        username: Target GitHub username.

    Returns:
        Normalized dictionary with repository listing or error diagnostics.
    """
    try:
        r = requests.get(
            f"https://api.github.com/users/{username}/repos",
            params={"per_page": 100, "sort": "updated"},
            timeout=10,
        )
        return handle_response(r)
    except requests.exceptions.RequestException:
        return {"status": "error", "reason": "network_timeout"}


@st.cache_data(ttl=3600)
def fetch_events(username: str) -> list[dict]:
    """Fetch recent public events for a user to extract push and contribution trends.

    Args:
        username: Target GitHub username.

    Returns:
        List of event objects, or empty list on failure or network timeout.
    """
    try:
        r = requests.get(
            f"https://api.github.com/users/{username}/events/public",
            params={"per_page": 30},
            timeout=10,
        )
        return r.json() if r.status_code == 200 else []
    except requests.exceptions.RequestException:
        return []
