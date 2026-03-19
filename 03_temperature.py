"""
03_temperature.py
-----------------
Fetches average annual temperature for every city in cities_master.csv
using the Open-Meteo Historical Weather API.

Input:  cities_master.csv
Output: cities_master.csv (updated in place)

Requirements:
    pip install pandas requests
    No API key needed.
"""

import sys
import time
import requests
import pandas as pd

MASTER_FILE   = "cities_master.csv"
START_YEAR    = "2014-01-01"
END_YEAR      = "2023-12-31"
API_BASE      = "https://archive-api.open-meteo.com/v1/archive"
REQUEST_DELAY = 1.0   # seconds between calls — don't lower this

def fetch_temperature(lat: float, lon: float, city: str) -> dict:
    params = {
        "latitude":         round(lat, 4),
        "longitude":        round(lon, 4),
        "start_date":       START_YEAR,
        "end_date":         END_YEAR,
        "daily":            "temperature_2m_max,temperature_2m_min",
        "temperature_unit": "fahrenheit",
        "timezone":         "auto",
    }

    # Retry up to 4 times on 429 rate limit
    for attempt in range(4):
        try:
            resp = requests.get(API_BASE, params=params, timeout=20)

            if resp.status_code == 429:
                wait = 15 * (attempt + 1)
                print(f"  [RATE LIMIT] {city} — waiting {wait}s before retry {attempt+1}/4...")
                time.sleep(wait)
                continue

            resp.raise_for_status()

            data   = resp.json()
            daily  = data.get("daily", {})
            dates  = daily.get("time", [])
            highs  = daily.get("temperature_2m_max", [])
            lows   = daily.get("temperature_2m_min", [])

            if not dates or not highs or not lows:
                return {}

            df = pd.DataFrame({
                "date":  pd.to_datetime(dates),
                "high":  pd.to_numeric(highs, errors="coerce"),
                "low":   pd.to_numeric(lows,  errors="coerce"),
            })
            df["avg"]   = (df["high"] + df["low"]) / 2
            df["month"] = df["date"].dt.month

            avg_temp_f        = round(df["avg"].mean(), 1)
            avg_high_f        = round(df["high"].mean(), 1)
            avg_low_f         = round(df["low"].mean(), 1)
            avg_temp_c        = round((avg_temp_f - 32) * 5 / 9, 1)
            summer            = df[df["month"].isin([6, 7, 8])]
            winter            = df[df["month"].isin([12, 1, 2])]
            avg_summer_high_f = round(summer["high"].mean(), 1) if len(summer) > 0 else None
            avg_winter_low_f  = round(winter["low"].mean(), 1) if len(winter)  > 0 else None

            return {
                "avg_temp_f":        avg_temp_f,
                "avg_temp_c":        avg_temp_c,
                "avg_high_f":        avg_high_f,
                "avg_low_f":         avg_low_f,
                "avg_summer_high_f": avg_summer_high_f,
                "avg_winter_low_f":  avg_winter_low_f,
            }

        except requests.exceptions.HTTPError as e:
            print(f"  [ERROR] {city}: {e}")
            return {}
        except Exception as e:
            print(f"  [ERROR] {city}: {e}")
            return {}

    print(f"  [FAILED] {city}: too many retries")
    return {}


def main():
    print("=" * 55)
    print("  03_temperature.py — Average Temperature")
    print("=" * 55)

    try:
        cities = pd.read_csv(MASTER_FILE)
        print(f"Loaded {len(cities)} cities from '{MASTER_FILE}'")
    except FileNotFoundError:
        print(f"ERROR: '{MASTER_FILE}' not found.")
        sys.exit(1)

    missing_coords = cities[cities["lat"].isna() | cities["lon"].isna()]
    if len(missing_coords) > 0:
        print(f"\n  WARNING: {len(missing_coords)} cities missing lat/lon — will be skipped")

    temp_cols = ["avg_temp_f", "avg_temp_c", "avg_high_f",
                 "avg_low_f", "avg_summer_high_f", "avg_winter_low_f"]
    for col in temp_cols:
        if col not in cities.columns:
            cities[col] = None

    # Only fetch cities that don't have temp data yet
    needs_fetch = cities[cities["avg_temp_f"].isna() & cities["lat"].notna()].index.tolist()

    total   = len(needs_fetch)
    success = 0
    failed  = 0

    print(f"\nFetching temperature data for {total} cities...")
    print(f"  Range: {START_YEAR} to {END_YEAR} (10-year average)")
    print(f"  Delay: {REQUEST_DELAY}s between requests\n")

    for count, idx in enumerate(needs_fetch, start=1):
        row   = cities.loc[idx]
        city  = row["city"]
        state = row["state"]

        result = fetch_temperature(row["lat"], row["lon"], city)

        if result:
            for col, val in result.items():
                cities.at[idx, col] = val
            success += 1
        else:
            failed += 1

        if count % 25 == 0:
            print(f"  {count}/{total} processed ({success} ok, {failed} failed)...")
            # Save progress every 25 cities so you don't lose data if it crashes
            cities.to_csv(MASTER_FILE, index=False)

        time.sleep(REQUEST_DELAY)

    cities.to_csv(MASTER_FILE, index=False)

    print(f"\nDone!")
    print(f"  Successful: {success}/{total}")
    print(f"  Failed:     {failed}/{total}")
    print(f"\nSaved → '{MASTER_FILE}'")
    print("\nSample (first 10 rows):")
    print(cities[["city", "state", "avg_temp_f", "avg_summer_high_f", "avg_winter_low_f"]].head(10).to_string(index=False))
    print("\nNext step: run 04_walkability.py")


if __name__ == "__main__":
    main()