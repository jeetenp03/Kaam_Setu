"""Google Sheets backend for Kaam Setu registrations.

Posts each registration to a Google Apps Script Web App URL bound to a
Google Sheet. The script appends a row with [Name, Phone, Village, Category].

No service account, no credentials, no Google Cloud setup — the Apps Script
is deployed from inside the sheet itself with "Anyone" access, so this
backend just needs the deployment URL.

Setup:
    Set APPS_SCRIPT_URL env var (or put it in .env) to the web app URL,
    which looks like: https://script.google.com/macros/s/.../exec

If the URL is missing or the request fails, append_registration returns
False so the caller can fall back to local JSON storage. The form on the
ground never breaks.
"""

import os

import requests

REQUEST_TIMEOUT_SECONDS = 8


def append_registration(entry):
    """Append a registration entry to the linked Google Sheet via Apps Script.

    The Apps Script routes the row to the "Workers" or "Hirers" tab based
    on the role field. Hirer-only fields (workers_needed, dates, etc.) are
    only filled in for hire requests.

    Returns True on success, False if the URL is unset or the call fails.
    """
    url = os.environ.get("APPS_SCRIPT_URL")
    if not url:
        return False

    payload = {
        "role": entry.get("role", ""),
        "name": entry.get("name", ""),
        "phone": entry.get("phone", ""),
        "village": entry.get("village", ""),
        "category": entry.get("category", ""),
        "workers_needed": entry.get("workers_needed", ""),
        "start_date": entry.get("start_date", ""),
        "num_days": entry.get("num_days", ""),
        "start_time": entry.get("start_time", ""),
    }

    response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return True


def fetch_workers():
    """Reading from the sheet is not supported via this backend.

    Returns None so callers fall back to the local JSON store. The campaign
    team views the live data by opening the Google Sheet directly.
    """
    return None
