"""
07_seasons.py
-------------
Derives seasons score entirely from temperature data already in
cities_master.csv — no API calls needed.

Uses existing columns:
  avg_temp_f, avg_high_f, avg_low_f,
  avg_summer_high_f, avg_winter_low_f

Adds columns:
  temp_range_f      - difference between summer high and winter low
  has_winter        - True if avg winter low <= 35F
  has_summer        - True if avg summer high >= 85F
  has_spring_fall   - True if temp range >= 40F (shoulder seasons exist)
  seasons_count     - 1-4
  seasons_score     - 0-100 (4 seasons = 100)

Input:  cities_master.csv
Output: cities_master.csv (updated in place)

Requirements:
    pip install pandas
    No API calls needed.
"""

import sys
import pandas as pd

MASTER_FILE = "cities_master.csv"

WINTER_THRESHOLD  = 35.0   # avg winter low at/below this = real winter
SUMMER_THRESHOLD  = 78.0   # avg summer high at/above this = real summer
RANGE_THRESHOLD   = 40.0   # annual temp range needed for spring/fall seasons

def compute_seasons(row) -> dict:
    summer_high = row.get("avg_summer_high_f")
    winter_low  = row.get("avg_winter_low_f")
    avg_high    = row.get("avg_high_f")
    avg_low     = row.get("avg_low_f")

    # Can't compute without these
    if pd.isna(summer_high) or pd.isna(winter_low):
        return {
            "temp_range_f":    None,
            "has_winter":      None,
            "has_summer":      None,
            "has_spring_fall": None,
            "seasons_count":   None,
            "seasons_score":   None,
        }

    temp_range = round(summer_high - winter_low, 1)

    has_winter     = bool(winter_low  <= WINTER_THRESHOLD)
    has_summer     = bool(summer_high >= SUMMER_THRESHOLD)
    has_spring_fall = bool(temp_range >= RANGE_THRESHOLD)

    # Count seasons
    seasons = 0
    if has_winter:
        seasons += 1
    if has_summer:
        seasons += 1
    if has_spring_fall:
        # If both winter and summer exist, spring+fall add 2
        # If only one extreme exists, add 1 for the transition
        if has_winter and has_summer:
            seasons += 2
        else:
            seasons += 1

    seasons = max(1, min(seasons, 4))
    seasons_score = round((seasons / 4) * 100, 1)

    return {
        "temp_range_f":    temp_range,
        "has_winter":      has_winter,
        "has_summer":      has_summer,
        "has_spring_fall": has_spring_fall,
        "seasons_count":   seasons,
        "seasons_score":   seasons_score,
    }

def main():
    print("=" * 55)
    print("  07_seasons.py — Seasons Score")
    print("=" * 55)

    try:
        cities = pd.read_csv(MASTER_FILE)
        print(f"Loaded {len(cities)} cities")
    except FileNotFoundError:
        print(f"ERROR: '{MASTER_FILE}' not found.")
        sys.exit(1)

    # Check required columns exist
    required = ["avg_summer_high_f", "avg_winter_low_f"]
    missing = [c for c in required if c not in cities.columns]
    if missing:
        print(f"ERROR: Missing columns: {missing}")
        print("Make sure 03_temperature.py has been run first.")
        sys.exit(1)

    print(f"  Using existing temperature data — no API calls needed")
    print(f"  Summer high available: {cities['avg_summer_high_f'].notna().sum()}/{len(cities)}")
    print(f"  Winter low available:  {cities['avg_winter_low_f'].notna().sum()}/{len(cities)}\n")

    # Compute seasons for all cities
    results = cities.apply(compute_seasons, axis=1, result_type="expand")

    for col in results.columns:
        cities[col] = results[col]

    cities.to_csv(MASTER_FILE, index=False)

    print("Done!")
    print(f"Saved -> '{MASTER_FILE}'")
    print("\nSample sorted by seasons count:")
    cols = ["city", "state", "avg_summer_high_f", "avg_winter_low_f",
            "temp_range_f", "seasons_count", "seasons_score"]
    sample = cities[cols].dropna(subset=["seasons_count"])
    print(sample.sort_values("seasons_count", ascending=False).head(20).to_string(index=False))

    print("\n--- Distribution ---")
    print(cities["seasons_count"].value_counts().sort_index().to_string())
    print("\nNext step: run 08_sports.py")

if __name__ == "__main__":
    main()