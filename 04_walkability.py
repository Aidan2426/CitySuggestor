"""
04_walkability.py
-----------------
Computes city-level walkability scores from the EPA National Walkability Index.

Strategy: matches cities to EPA block groups using CBSA_Name which contains
city names, then averages NatWalkInd scores across all matching block groups.
Falls back to state-level average for unmatched cities.

Input:  cities_master.csv
        walkability.csv  (EPA Smart Location Database)
Output: cities_master.csv (updated in place)

Download walkability.csv from:
https://edg.epa.gov/EPADataCommons/public/OA/EPA_SmartLocationDatabase_V3_Jan_2021_Final.csv

Requirements:
    pip install pandas
"""

import sys
import re
import pandas as pd

MASTER_FILE      = "cities_master.csv"
WALKABILITY_FILE = "walkability.csv"

STATE_FIPS = {
    "AL":"01","AK":"02","AZ":"04","AR":"05","CA":"06","CO":"08","CT":"09",
    "DE":"10","DC":"11","FL":"12","GA":"13","HI":"15","ID":"16","IL":"17",
    "IN":"18","IA":"19","KS":"20","KY":"21","LA":"22","ME":"23","MD":"24",
    "MA":"25","MI":"26","MN":"27","MS":"28","MO":"29","MT":"30","NE":"31",
    "NV":"32","NH":"33","NJ":"34","NM":"35","NY":"36","NC":"37","ND":"38",
    "OH":"39","OK":"40","OR":"41","PA":"42","RI":"44","SC":"45","SD":"46",
    "TN":"47","TX":"48","UT":"49","VT":"50","VA":"51","WA":"53","WV":"54",
    "WI":"55","WY":"56",
}

def load_epa(path: str):
    print(f"Loading EPA walkability data...")
    try:
        df = pd.read_csv(path, dtype=str, low_memory=False)
    except FileNotFoundError:
        print(f"ERROR: '{path}' not found.")
        print("Download from: https://edg.epa.gov/EPADataCommons/public/OA/EPA_SmartLocationDatabase_V3_Jan_2021_Final.csv")
        sys.exit(1)

    df.columns = [c.strip() for c in df.columns]
    print(f"  Loaded {len(df):,} block groups")

    # Convert score columns to numeric
    df["NatWalkInd"] = pd.to_numeric(df["NatWalkInd"], errors="coerce")
    df["D4A"]        = pd.to_numeric(df.get("D4A", pd.Series()), errors="coerce")
    df["STATEFP"]    = df["STATEFP"].astype(str).str.zfill(2)

    return df

def build_lookups(df: pd.DataFrame):
    """
    Builds two lookup dicts:
    1. city_lookup: city_lower → avg walkability score
       Built by extracting city names from CBSA_Name
    2. state_lookup: state_fips → avg walkability score
       Fallback for unmatched cities
    """

    # ── city-level lookup from CBSA_Name ──────────────────────────────────────
    # CBSA_Name looks like "Dallas-Fort Worth-Arlington, TX"
    # We extract every city name mentioned and map it to the avg score

    city_scores = {}  # city_lower → list of scores

    for _, row in df.iterrows():
        score = row["NatWalkInd"]
        if pd.isna(score):
            continue

        cbsa = str(row.get("CBSA_Name", ""))
        if not cbsa or cbsa == "nan":
            continue

        # Split "Dallas-Fort Worth-Arlington, TX" into city part and state
        parts = cbsa.split(",")
        if len(parts) < 2:
            continue

        city_part = parts[0].strip()
        # Split on hyphen/en-dash to get individual city names
        city_names = re.split(r"[-–]", city_part)

        for city in city_names:
            city = city.strip().lower()
            if len(city) < 2:
                continue
            if city not in city_scores:
                city_scores[city] = []
            city_scores[city].append(score)

    # Average scores per city name
    city_lookup = {
        city: round(sum(scores) / len(scores), 2)
        for city, scores in city_scores.items()
        if len(scores) > 0
    }

    # ── state-level fallback ──────────────────────────────────────────────────
    state_agg = df.groupby("STATEFP")["NatWalkInd"].mean().round(2)
    state_lookup = state_agg.to_dict()

    print(f"  City-level entries: {len(city_lookup)}")
    print(f"  State-level entries: {len(state_lookup)}")

    return city_lookup, state_lookup

def match_cities(cities: pd.DataFrame, city_lookup: dict, state_lookup: dict) -> pd.DataFrame:
    print(f"\nMatching {len(cities)} cities to walkability scores...")

    walk_scores = []
    match_types = []

    for _, row in cities.iterrows():
        city      = str(row["city"]).lower().strip()
        state     = str(row["state"]).upper().strip()
        state_fp  = STATE_FIPS.get(state, "")

        # Try exact city name match
        if city in city_lookup:
            walk_scores.append(city_lookup[city])
            match_types.append("exact")
            continue

        # Try partial match — check if city name appears in any key
        partial = next(
            (v for k, v in city_lookup.items()
             if city in k or k in city),
            None
        )
        if partial:
            walk_scores.append(partial)
            match_types.append("partial")
            continue

        # Fallback to state average
        if state_fp and state_fp in state_lookup:
            walk_scores.append(state_lookup[state_fp])
            match_types.append("state_avg")
        else:
            walk_scores.append(None)
            match_types.append("failed")

    cities["walkability_score"] = walk_scores
    cities["walk_match_type"]   = match_types

    exact   = match_types.count("exact")
    partial = match_types.count("partial")
    state   = match_types.count("state_avg")
    failed  = match_types.count("failed")

    print(f"  Exact match:   {exact}")
    print(f"  Partial match: {partial}")
    print(f"  State average: {state}")
    print(f"  Failed:        {failed}")

    return cities

def main():
    print("=" * 55)
    print("  04_walkability.py — EPA National Walkability Index")
    print("=" * 55)

    try:
        cities = pd.read_csv(MASTER_FILE)
        print(f"Loaded {len(cities)} cities from '{MASTER_FILE}'")
    except FileNotFoundError:
        print(f"ERROR: '{MASTER_FILE}' not found.")
        sys.exit(1)

    df = load_epa(WALKABILITY_FILE)
    city_lookup, state_lookup = build_lookups(df)
    cities = match_cities(cities, city_lookup, state_lookup)

    # Normalize 1-20 scale to 0-100
    cities["walkability_score_100"] = (
        (cities["walkability_score"] - 1) / (20 - 1) * 100
    ).round(1)

    # Drop the match type debug column before saving
    cities = cities.drop(columns=["walk_match_type"], errors="ignore")

    cities.to_csv(MASTER_FILE, index=False)
    print(f"\nSaved -> '{MASTER_FILE}'")
    print("\nSample (first 15 rows):")
    cols = ["city", "state", "walkability_score", "walkability_score_100"]
    print(cities[cols].head(15).to_string(index=False))
    print("\nNext step: run 05_distances.py")

if __name__ == "__main__":
    main()