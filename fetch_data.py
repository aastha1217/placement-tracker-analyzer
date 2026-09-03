"""
Overnight retry script — fetches data from the placement tracker's API,
retrying every 15 minutes until it succeeds (works around the backend's
Firestore rate-limit / 429 errors). Saves the result once successful and
stops automatically.
"""

import requests
import time
import json
from datetime import datetime

URL = "https://placements25-26.vercel.app/api/placements"
OUTPUT_FILE = "placements_data.json"
LOG_FILE = "scrape_log.txt"
RETRY_INTERVAL_MINUTES = 15

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def try_fetch():
    try:
        response = requests.get(URL, timeout=15)
        data = response.json()

        # Check if it's the same 429/error shape we've been seeing
        if isinstance(data, dict) and data.get("ok") is False:
            log(f"Still failing -> {data.get('error')}")
            return None

        # If we got here, looks like real data
        return data

    except requests.exceptions.RequestException as e:
        log(f"Request error: {e}")
        return None
    except json.JSONDecodeError:
        log("Response wasn't valid JSON")
        return None

log("Starting overnight polling. Will retry every 15 minutes until success.")

attempt = 1
while True:
    log(f"Attempt {attempt}: trying {URL}")
    result = try_fetch()

    if result is not None:
        log("SUCCESS! Got real data. Saving to file and stopping.")
        with open(OUTPUT_FILE, "w") as f:
            json.dump(result, f, indent=2)
        log(f"Saved to {OUTPUT_FILE}. You can stop the laptop now.")
        break

    attempt += 1
    log(f"Sleeping {RETRY_INTERVAL_MINUTES} minutes before next attempt...\n")
    time.sleep(RETRY_INTERVAL_MINUTES * 60)