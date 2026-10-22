#!/usr/bin/env python3
"""Fetch and persist the latest USD/JPY reference rate."""

import json
import os
import sys
import tempfile
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

API_URL = "https://api.frankfurter.dev/v1/latest?base=USD&symbols=JPY"
DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "usd-jpy.json"


def fetch_rate():
    request = Request(API_URL, headers={"User-Agent": "usd-jpy-daily-chart/1.0"})
    with urlopen(request, timeout=20) as response:
        payload = json.load(response)

    try:
        rate_date = date.fromisoformat(payload["date"]).isoformat()
        rate = Decimal(str(payload["rates"]["JPY"]))
    except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
        raise ValueError("Frankfurter returned an invalid rate response") from exc

    if not rate.is_finite() or rate <= 0:
        raise ValueError("Frankfurter returned a non-positive or non-finite rate")
    return {"date": rate_date, "usd_jpy": float(rate)}


def read_observations(path):
    try:
        observations = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    if not isinstance(observations, list):
        raise ValueError(f"{path} must contain a JSON array")

    dates = []
    for row in observations:
        if not isinstance(row, dict):
            raise ValueError(f"{path} contains an invalid observation")
        try:
            parsed_date = date.fromisoformat(row["date"])
            rate = Decimal(str(row["usd_jpy"]))
        except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
            raise ValueError(f"{path} contains an invalid observation") from exc
        if not rate.is_finite() or rate <= 0:
            raise ValueError(f"{path} contains a non-positive or non-finite rate")
        dates.append(parsed_date.isoformat())
    if dates != sorted(set(dates)):
        raise ValueError(f"{path} dates must be unique and in ascending order")
    return observations


def save_observations(path, observations):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(observations, output, ensure_ascii=False, indent=2)
            output.write("\n")
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def update(path=DATA_FILE, fetch=fetch_rate):
    observation = fetch()
    existing = read_observations(path)
    if any(row["date"] == observation["date"] for row in existing):
        print(f"Rate for {observation['date']} already recorded; no update.")
        return False

    existing.append(observation)
    existing.sort(key=lambda row: row["date"])
    save_observations(path, existing)
    print(f"Recorded USD/JPY {observation['usd_jpy']} for {observation['date']}.")
    return True


if __name__ == "__main__":
    try:
        update()
    except (OSError, URLError, ValueError, json.JSONDecodeError) as error:
        print(f"Failed to update USD/JPY rate: {error}", file=sys.stderr)
        sys.exit(1)
