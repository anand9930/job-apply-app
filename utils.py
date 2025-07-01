from datetime import datetime, timedelta
import json
import re

import pytz
from dateutil.relativedelta import relativedelta


def linkedin_to_pgdate(text: str,
                       *,
                       now: datetime | None = None,
                       tz: str = "Asia/Tokyo") -> str:
    """
    Convert strings like “3 days ago” (or “yesterday”, “just now”, etc.)
    to a date string PostgreSQL accepts (YYYY-MM-DD).

    Parameters
    ----------
    text : str
        LinkedIn relative time description.
    now : datetime, optional
        Reference point; defaults to current time in `tz`.
    tz : str
        IANA timezone name (defaults to Asia/Tokyo).

    Returns
    -------
    str
        Date formatted as 'YYYY-MM-DD'.
    """
    if now is None:
        now = datetime.now(pytz.timezone(tz))

    t = text.strip().lower()

    # Easy absolutes
    if t in {"today", "just now"}:
        return now.strftime("%Y-%m-%d")
    if t == "yesterday":
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")

    # Generic “n unit(s) ago”
    m = re.match(r"(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+ago", t)
    if not m:
        raise ValueError(f"Unrecognized LinkedIn date format: {text!r}")

    n, unit = int(m[1]), m[2]

    if unit == "second":
        delta = timedelta(seconds=n)
    elif unit == "minute":
        delta = timedelta(minutes=n)
    elif unit == "hour":
        delta = timedelta(hours=n)
    elif unit == "day":
        delta = timedelta(days=n)
    elif unit == "week":
        delta = timedelta(weeks=n)
    elif unit == "month":
        delta = relativedelta(months=n)
    else:  # "year"
        delta = relativedelta(years=n)

    return (now - delta).strftime("%Y-%m-%d")


def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
def load_prompt(filepath):
    """Load and return the content of a prompt file."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return None
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None
