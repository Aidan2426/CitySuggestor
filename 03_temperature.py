"""
03_temperature.py
-----------------
Fetches 30-year climate normals (1991-2020) for every city using Meteostat.
Much faster and more reliable than Open-Meteo archive — no rate limits.

Input:  cities_master.csv
Output: cities_master.csv (updated in place)

Requirements:
    pip install meteostat
"""

import sys
import time
import requests
import pandas as pd
import requests

MASTER_FILE   = "cities_master.csv"
API_BASE      = "https://archive-api.open-meteo.com/v1/archive"
START_DATE    = "2019-01-01"
END_DATE      = "2021-12-31"
REQUEST_DELAY = 10.0  # slow enough to avoid rate limiting

def fetch_temperature(lat: float, lon: float, city: str) -> dict:
    params = {
        "latitude":         round(lat, 4),
        "longitude":        round(lon, 4),
        "start_date":       START_DATE,
        "end_date":         END_DATE,
        "daily":            "temperature_2m_max,temperature_2m_min",
        "temperature_unit": "fahrenheit",
        "timezone":         "auto",
    }
    for attempt in range(6):
        try:
            resp = requests.get(API_BASE, params=params, timeout=30)
            if resp.status_code == 429:
                wait = 30 * (2 ** attempt)   # 30, 60, 120, 240, 480, 960s
                print(f"  [RATE LIMIT] {city} — waiting {wait}s (attempt {attempt+1}/6)...", flush=True)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data  = resp.json()
            daily = data.get("daily", {})
            dates = daily.get("time", [])
            highs = daily.get("temperature_2m_max", [])
            lows  = daily.get("temperature_2m_min", [])
            if not dates:
                return {}
            df = pd.DataFrame({
                "date":  pd.to_datetime(dates),
                "high":  pd.to_numeric(highs, errors="coerce"),
                "low":   pd.to_numeric(lows,  errors="coerce"),
            })
            df["avg"]   = (df["high"] + df["low"]) / 2
            df["month"] = df["date"].dt.month
            summer = df[df["month"].isin([6, 7, 8])]
            winter = df[df["month"].isin([12, 1, 2])]
            return {
                "avg_temp_f":        round(float(df["avg"].mean()), 1),
                "avg_temp_c":        round((float(df["avg"].mean()) - 32) * 5/9, 1),
                "avg_high_f":        round(float(df["high"].mean()), 1),
                "avg_low_f":         round(float(df["low"].mean()), 1),
                "avg_summer_high_f": round(float(summer["high"].mean()), 1) if not summer.empty else None,
                "avg_winter_low_f":  round(float(winter["low"].mean()), 1)  if not winter.empty else None,
            }
        except Exception as e:
            print(f"  [ERROR] {city}: {e}")
            return {}
    print(f"  [FAILED] {city}: gave up after 6 retries")
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

    # ── geocode missing lat/lon via Nominatim ─────────────────────────────────
    if "lat" not in cities.columns:
        cities["lat"] = None
    if "lon" not in cities.columns:
        cities["lon"] = None

    needs_geocode = cities[cities["lat"].isna()].index.tolist()
    if needs_geocode:
        print(f"\nGeocoding {len(needs_geocode)} cities to get lat/lon...")
        for i, idx in enumerate(needs_geocode, 1):
            row   = cities.loc[idx]
            city  = row["city"]
            state = row["state"]
            try:
                resp = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"city": city, "state": state, "country": "US",
                            "format": "json", "limit": 1},
                    headers={"User-Agent": "CitySuggestor/1.0"},
                    timeout=10,
                )
                results = resp.json()
                if results:
                    cities.at[idx, "lat"] = float(results[0]["lat"])
                    cities.at[idx, "lon"] = float(results[0]["lon"])
                    print(f"  [{i}/{len(needs_geocode)}] {city}, {state} → {results[0]['lat']}, {results[0]['lon']}")
                else:
                    print(f"  [{i}/{len(needs_geocode)}] {city}, {state} → NO RESULT")
            except Exception as e:
                print(f"  [{i}/{len(needs_geocode)}] {city}, {state}: ERROR {e}")
            time.sleep(1.0)
            if i % 50 == 0:
                cities.to_csv(MASTER_FILE, index=False)
                print(f"  --- Saved progress ({i}/{len(needs_geocode)}) ---")
        cities.to_csv(MASTER_FILE, index=False)
        print(f"  Geocoding done. Saved.\n")

    # ── temperature columns ────────────────────────────────────────────────────
    temp_cols = ["avg_temp_f", "avg_temp_c", "avg_high_f",
                 "avg_low_f", "avg_summer_high_f", "avg_winter_low_f"]
    for col in temp_cols:
        if col not in cities.columns:
            cities[col] = None

    # Only fetch cities missing temp data — safe to re-run anytime
    needs_fetch = cities[
        cities["avg_temp_f"].isna() & cities["lat"].notna()
    ].index.tolist()

    total   = len(needs_fetch)
    success = 0
    failed  = 0

    print(f"\nFetching temperature data for {total} cities...")
    print(f"  Source: Open-Meteo archive API (ERA5 2019-2021)")
    print(f"  Saves progress every 25 cities\n")

    for count, idx in enumerate(needs_fetch, start=1):
        row  = cities.loc[idx]
        city = row["city"]
        state = row["state"]

        print(f"  [{count}/{total}] {city}, {state}...", end=" ", flush=True)
        result = fetch_temperature(row["lat"], row["lon"], city)

        if result:
            for col, val in result.items():
                cities.at[idx, col] = val
            success += 1
            print(f"✓ {result['avg_temp_f']}°F", flush=True)
        else:
            failed += 1
            print("✗ failed", flush=True)

        if count % 25 == 0:
            cities.to_csv(MASTER_FILE, index=False)
            print(f"  --- Saved ({count}/{total}, {success} ok, {failed} failed) ---", flush=True)

        time.sleep(REQUEST_DELAY)

    cities.to_csv(MASTER_FILE, index=False)

    print(f"\nDone!")
    print(f"  Successful: {success}/{total}")
    print(f"  Failed:     {failed}/{total}")
    if failed > 0:
        print(f"  Re-run this script to retry the {failed} failed cities.")
    print(f"\nSaved -> '{MASTER_FILE}'")
    print("\nSample (first 10 rows):")
    print(cities[["city", "state", "avg_temp_f", "avg_summer_high_f",
                  "avg_winter_low_f"]].head(10).to_string(index=False))
    print("\nNext step: run 04_walkability.py")


if __name__ == "__main__":
    main()

    ####