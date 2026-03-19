"""
02_census_data.py
-----------------
Pulls median household income and median home price for every city
in cities_master.csv using the Census Bureau ACS 5-Year API.

Data source: American Community Survey 5-Year Estimates (2022)
  - B19013_001E  →  Median Household Income
  - B25077_001E  →  Median Home Value (owner-occupied units)

Geography level: Place (city) within each state

Input:  cities_master.csv
Output: cities_master.csv (updated in place — adds median_household_income
        and median_home_price columns)

Requirements:
    pip install pandas requests

Get a free Census API key at:
    https://api.census.gov/data/key_signup.html
"""

import re
import sys
import time
import requests
import pandas as pd

# ── config ────────────────────────────────────────────────────────────────────

MASTER_FILE = "cities_master.csv"
API_KEY     = "46065597a2b3cbe59756605ab4f6bb668b0ebf49"   # ← paste your key here
ACS_YEAR    = 2022
API_BASE    = f"https://api.census.gov/data/{ACS_YEAR}/acs/acs5"

# Variables we want
VARS = {
    "B19013_001E": "median_household_income",
    "B25077_001E": "median_home_price",
}

# State name → FIPS code mapping (all 50 states + DC)
STATE_FIPS = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06",
    "CO": "08", "CT": "09", "DE": "10", "DC": "11", "FL": "12",
    "GA": "13", "HI": "15", "ID": "16", "IL": "17", "IN": "18",
    "IA": "19", "KS": "20", "KY": "21", "LA": "22", "ME": "23",
    "MD": "24", "MA": "25", "MI": "26", "MN": "27", "MS": "28",
    "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33",
    "NJ": "34", "NM": "35", "NY": "36", "NC": "37", "ND": "38",
    "OH": "39", "OK": "40", "OR": "41", "PA": "42", "RI": "44",
    "SC": "45", "SD": "46", "TN": "47", "TX": "48", "UT": "49",
    "VT": "50", "VA": "51", "WA": "53", "WV": "54", "WI": "55",
    "WY": "56",
}

# ── step 1: validate API key ──────────────────────────────────────────────────

def validate_key(api_key: str):
    if api_key == "YOUR_CENSUS_API_KEY_HERE" or not api_key.strip():
        print("ERROR: You need to set your Census API key.")
        print("  1. Go to https://api.census.gov/data/key_signup.html")
        print("  2. Sign up — they email you a key instantly")
        print("  3. Open this script and replace YOUR_CENSUS_API_KEY_HERE")
        sys.exit(1)

# ── step 2: fetch ACS data for all places in one state ───────────────────────

def fetch_state_places(state_fips: str, api_key: str) -> list[dict]:
    """
    Fetches income + home price for ALL places (cities/towns) in one state.
    Returns a list of dicts with NAME, state, place, and the two variables.
    One API call per state — very efficient.
    """
    var_string = "NAME," + ",".join(VARS.keys())

    params = {
        "get":      var_string,
        "for":      "place:*",
        "in":       f"state:{state_fips}",
        "key":      api_key,
    }

    try:
        resp = requests.get(API_BASE, params=params, timeout=20)

        if resp.status_code == 204:
            return []  # no data for this state

        resp.raise_for_status()
        data = resp.json()

        if len(data) < 2:
            return []

        headers = data[0]
        rows    = data[1:]

        results = []
        for row in rows:
            record = dict(zip(headers, row))
            results.append(record)

        return results

    except requests.exceptions.HTTPError as e:
        print(f"  [HTTP ERROR] State {state_fips}: {e}")
        return []
    except Exception as e:
        print(f"  [ERROR] State {state_fips}: {e}")
        return []


# ── step 3: fetch data for all states ────────────────────────────────────────

def fetch_all_states(api_key: str) -> pd.DataFrame:
    """
    Loops through all 51 state FIPS codes, fetches place-level ACS data,
    and combines into one DataFrame.
    """
    print(f"Fetching ACS {ACS_YEAR} 5-year estimates for all states...")
    print(f"  Variables: median household income + median home price")
    print(f"  Geography: all places (cities) within each state\n")

    all_records = []

    for abbr, fips in STATE_FIPS.items():
        records = fetch_state_places(fips, api_key)
        all_records.extend(records)
        print(f"  {abbr} ({fips}): {len(records)} places fetched")
        time.sleep(0.1)  # be polite to the API

    print(f"\n  Total places fetched: {len(all_records)}")
    return pd.DataFrame(all_records)


# ── step 4: clean the ACS dataframe ──────────────────────────────────────────

def clean_acs_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts a clean city name from the Census NAME field and converts
    income/home price columns to numeric (Census uses -666666666 for
    missing/suppressed values).
    """
    print("\nCleaning ACS data...")

    # Census NAME looks like "New York city, New York" or "Austin city, Texas"
    # We want just the city name part before the comma
    df["city_raw"] = (
        df["NAME"]
        .str.split(",").str[0]           # "New York city"
        .str.replace(r"\s+(city|town|village|borough|municipality|CDP|charter township|township|unified government|consolidated government|metro government|urban county|city and county)$",
                     "", regex=True, flags=re.IGNORECASE)
        .str.strip()
    )

    # Rename ACS variable columns to friendly names
    df = df.rename(columns=VARS)

    # Convert to numeric — Census uses -666666666 for suppressed/missing data
    for col in VARS.values():
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].where(df[col] > 0, other=None)

    print(f"  {len(df)} places after cleaning")
    print(f"  Income data available: {df['median_household_income'].notna().sum()}")
    print(f"  Home price data available: {df['median_home_price'].notna().sum()}")

    return df


# ── step 5: join onto cities_master ──────────────────────────────────────────

def join_to_master(cities: pd.DataFrame, acs: pd.DataFrame) -> pd.DataFrame:
    """
    Matches each city in cities_master.csv to its ACS record by
    city name + state FIPS code.
    """
    print("\nJoining ACS data onto city list...")

    # Add state FIPS to cities for joining
    cities["_state_fips"] = cities["state"].map(STATE_FIPS)

    # Normalize city names for matching (lowercase, stripped)
    cities["_city_lower"] = cities["city"].str.lower().str.strip()
    acs["_city_lower"]    = acs["city_raw"].str.lower().str.strip()

    # Join on city name + state FIPS
    merged = cities.merge(
        acs[["_city_lower", "state", "median_household_income", "median_home_price"]],
        left_on=["_city_lower", "_state_fips"],
        right_on=["_city_lower", "state"],
        how="left",
        suffixes=("", "_acs")
    )

    # Drop helper columns
    merged = merged.drop(columns=[c for c in merged.columns
                                  if c.startswith("_") or c == "state_acs"],
                         errors="ignore")

    matched_income = merged["median_household_income"].notna().sum()
    matched_home   = merged["median_home_price"].notna().sum()
    total          = len(merged)

    print(f"  Median household income matched: {matched_income}/{total}")
    print(f"  Median home price matched:       {matched_home}/{total}")

    unmatched = merged[merged["median_household_income"].isna()][["city", "state"]]
    if len(unmatched) > 0:
        print(f"\n  Unmatched cities ({len(unmatched)}):")
        print(unmatched.to_string(index=False))

    return merged


# ── step 6: save ──────────────────────────────────────────────────────────────

def save_output(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)
    print(f"\nSaved {len(df)} cities → '{path}'")
    print("\nColumns:", list(df.columns))
    print("\nSample (first 10 rows):")
    cols = ["city", "state", "median_household_income", "median_home_price"]
    print(df[cols].head(10).to_string(index=False))


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  02_census_data.py — Income & Home Price")
    print("=" * 55)

    validate_key(API_KEY)

    # Load master city list
    try:
        cities = pd.read_csv(MASTER_FILE)
        print(f"Loaded {len(cities)} cities from '{MASTER_FILE}'\n")
    except FileNotFoundError:
        print(f"ERROR: '{MASTER_FILE}' not found. Run 01_scrape_cities.py first.")
        sys.exit(1)

    # Fetch ACS data for all states
    acs_raw = fetch_all_states(API_KEY)

    # Clean
    acs_clean = clean_acs_data(acs_raw)

    # Join
    updated = join_to_master(cities, acs_clean)

    # Save
    save_output(updated, MASTER_FILE)

    print("\nDone! cities_master.csv now includes median_household_income")
    print("and median_home_price.")
    print("Next step: run 03_temperature.py")


if __name__ == "__main__":
    main()