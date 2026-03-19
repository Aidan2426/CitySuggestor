"""
01c_fix_metro_population.py
---------------------------
Fills in missing metro_population values in cities_master.csv using:

  Step 1 — Download the official Census Bureau CBSA delineation file
           (county → MSA crosswalk, July 2023 definitions)
  Step 2 — Use Census Geocoder API to find which county each unmatched
           city belongs to
  Step 3 — Match county → CBSA code → MSA name → metro_population
           (from the Wikipedia MSA populations already in cities_master.csv
           or re-scraped from the MSA list)

Input:  cities_master.csv
Output: cities_master.csv (updated in place)

Requirements:
    pip install pandas requests openpyxl
"""

import re
import sys
import time
import requests
import pandas as pd
from io import BytesIO

# ── config ────────────────────────────────────────────────────────────────────

MASTER_FILE   = "cities_master.csv"
GEOCODER_DELAY = 0.5  # seconds between Census Geocoder API calls
WIKI_MSA_URL  = "https://en.wikipedia.org/wiki/Metropolitan_statistical_area"

# Official Census Bureau CBSA delineation file (July 2023)
DELINEATION_URL = (
    "https://www.census.gov/geographies/reference-files/time-series/demo/"
    "metro-micro/delineation-files.html"
)

# Direct Excel download for the July 2023 delineation file
CBSA_EXCEL_URL = (
    "https://www2.census.gov/programs-surveys/metro-micro/geographies/"
    "reference-files/2023/delineation-files/list1_2023.xlsx"
)

# ── step 1: download census CBSA delineation file ─────────────────────────────

def download_cbsa_crosswalk() -> pd.DataFrame:
    """
    Downloads the official Census Bureau CBSA delineation Excel file and
    returns a DataFrame mapping (state_fips, county_fips) → (cbsa_code, cbsa_title).
    Only keeps Metropolitan Statistical Areas (not Micropolitan).
    """
    print("Downloading Census CBSA delineation file...")

    response = requests.get(CBSA_EXCEL_URL, timeout=30)
    response.raise_for_status()

    # The Excel file has a header row we need to skip — row 3 is the actual header
    df = pd.read_excel(BytesIO(response.content), skiprows=2, dtype=str)

    print(f"  Raw delineation file: {len(df)} rows, columns: {list(df.columns)}")

    # Normalize column names
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    # Find the relevant columns (names vary slightly between file versions)
    cbsa_col   = next(c for c in df.columns if "cbsa" in c and "code" in c)
    title_col  = next(c for c in df.columns if "cbsa" in c and "title" in c)
    type_col   = next(c for c in df.columns if "metropolitan" in c or "metro/micro" in c or "statistical_area" in c.replace(" ","_"))
    state_col  = next(c for c in df.columns if "state" in c and "fips" in c)
    county_col = next(c for c in df.columns if "county" in c and "fips" in c)

    print(f"  Using: cbsa={cbsa_col}, title={title_col}, type={type_col}")
    print(f"         state_fips={state_col}, county_fips={county_col}")

    # Keep only Metropolitan Statistical Areas (not Micropolitan)
    df_metro = df[df[type_col].str.contains("Metropolitan Statistical Area", na=False)].copy()
    print(f"  Metropolitan Statistical Areas: {len(df_metro)} county entries")

    # Build clean crosswalk
    crosswalk = df_metro[[state_col, county_col, cbsa_col, title_col]].copy()
    crosswalk.columns = ["state_fips", "county_fips", "cbsa_code", "cbsa_title"]
    crosswalk = crosswalk.dropna()

    # Pad FIPS codes to correct lengths
    crosswalk["state_fips"]  = crosswalk["state_fips"].str.zfill(2)
    crosswalk["county_fips"] = crosswalk["county_fips"].str.zfill(3)
    crosswalk["fips"] = crosswalk["state_fips"] + crosswalk["county_fips"]

    print(f"  Crosswalk built: {len(crosswalk)} county→MSA mappings")
    return crosswalk


# ── step 2: geocode city to county via Census Geocoder ────────────────────────

def geocode_city_to_county(city: str, state: str) -> tuple:
    """
    Uses the Census Geocoder API to find the county FIPS code for a city.
    Returns (state_fips, county_fips) or (None, None) if not found.

    Free API, no key required. Rate limit: be polite with delays.
    """
    url = "https://geocoding.geo.census.gov/geocoder/geographies/address"
    params = {
        "street":     "",
        "city":       city,
        "state":      state,
        "benchmark":  "Public_AR_Current",
        "vintage":    "Current_Current",
        "format":     "json",
        "layers":     "Counties"
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        matches = data.get("result", {}).get("addressMatches", [])
        if not matches:
            return None, None

        geo = matches[0].get("geographies", {})
        counties = geo.get("Counties", [])
        if not counties:
            return None, None

        state_fips  = counties[0].get("STATE")
        county_fips = counties[0].get("COUNTY")
        return state_fips, county_fips

    except Exception:
        return None, None


# ── step 3: scrape MSA populations from Wikipedia ─────────────────────────────

def scrape_msa_populations() -> dict:
    """
    Returns a dict: cbsa_title_lower → metro_population
    Scrapes the Wikipedia MSA table for population figures.
    """
    from bs4 import BeautifulSoup

    print("\nScraping MSA populations from Wikipedia...")
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CityDataBot/1.0)"}
    resp = requests.get(WIKI_MSA_URL, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, "lxml")

    tables = soup.find_all("table", {"class": "wikitable"})
    main   = max(tables, key=lambda t: len(t.find_all("tr")))

    msa_pops = {}
    for row in main.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) < 2 or all(c.name == "th" for c in cells):
            continue
        name = re.sub(r"\[.*?\]", "", cells[0].get_text()).strip()
        pop_text = re.sub(r"[^\d]", "", cells[1].get_text())
        if name and pop_text:
            msa_pops[name.lower()] = int(pop_text)

    print(f"  Scraped {len(msa_pops)} MSA population entries")
    return msa_pops


# ── step 4: match CBSA title to Wikipedia MSA population ──────────────────────

def match_cbsa_to_population(cbsa_title: str, msa_pops: dict) -> int:
    """
    Fuzzy-matches a CBSA title to a Wikipedia MSA name to get the population.
    Census titles look like: 'New York-Newark-Jersey City, NY-NJ-PA MSA'
    Wikipedia titles look like: 'New York–Newark–Jersey City, NY-NJ MSA'
    Strategy: match on the first city name + state abbreviation.
    """
    # Normalize: lowercase, replace em-dashes with hyphens
    normalized = cbsa_title.lower().replace("–", "-").replace(" msa", "").strip()

    # Direct match first
    for wiki_name in msa_pops:
        wiki_norm = wiki_name.replace("–", "-").replace(" msa", "").strip()
        if normalized == wiki_norm:
            return msa_pops[wiki_name]

    # Partial match on first city + first state
    # Extract first city from CBSA title (before first hyphen or comma)
    first_city = re.split(r"[-,]", normalized)[0].strip()
    state_match = re.search(r",\s*([a-z]{2})", normalized)
    first_state = state_match.group(1) if state_match else ""

    for wiki_name, pop in msa_pops.items():
        wiki_norm = wiki_name.replace("–", "-").lower()
        wfirst_city = re.split(r"[-,]", wiki_norm)[0].strip()
        wstate = re.search(r",\s*([a-z]{2})", wiki_norm)
        wfirst_state = wstate.group(1) if wstate else ""
        if first_city == wfirst_city and first_state == wfirst_state:
            return pop

    return None


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  01c_fix_metro_population.py")
    print("=" * 55)

    # Load cities
    try:
        cities = pd.read_csv(MASTER_FILE)
    except FileNotFoundError:
        print(f"ERROR: '{MASTER_FILE}' not found.")
        sys.exit(1)

    unmatched = cities[cities["metro_population"].isna()].copy()
    print(f"Loaded {len(cities)} cities, {len(unmatched)} missing metro_population\n")

    if len(unmatched) == 0:
        print("Nothing to fix — all cities already have metro_population!")
        sys.exit(0)

    # Step 1: Download CBSA crosswalk
    crosswalk = download_cbsa_crosswalk()

    # Step 2: Scrape Wikipedia MSA populations
    msa_pops = scrape_msa_populations()

    # Step 3: For each unmatched city, geocode → county → CBSA → population
    print(f"\nGeocoding {len(unmatched)} unmatched cities to counties...")
    print("  This takes ~1-2 minutes.\n")

    fixed = 0
    still_missing = []

    for idx, row in unmatched.iterrows():
        city  = row["city"]
        state = row["state"]

        # Geocode city → county FIPS
        state_fips, county_fips = geocode_city_to_county(city, state)
        time.sleep(GEOCODER_DELAY)

        if not state_fips or not county_fips:
            still_missing.append(f"{city}, {state}")
            continue

        fips = state_fips.zfill(2) + county_fips.zfill(3)

        # Look up county in CBSA crosswalk
        match = crosswalk[crosswalk["fips"] == fips]
        if match.empty:
            still_missing.append(f"{city}, {state} (county {fips} not in MSA)")
            continue

        cbsa_title = match.iloc[0]["cbsa_title"]

        # Match CBSA title to Wikipedia population
        pop = match_cbsa_to_population(cbsa_title, msa_pops)

        if pop:
            cities.at[idx, "metro_population"] = pop
            fixed += 1
        else:
            still_missing.append(f"{city}, {state} (CBSA: {cbsa_title} — no pop match)")

    print(f"\nResults:")
    print(f"  Fixed:         {fixed}")
    print(f"  Still missing: {len(still_missing)}")

    if still_missing:
        print("\n  Remaining NaNs:")
        for c in still_missing:
            print(f"    {c}")

    # Save
    cities.to_csv(MASTER_FILE, index=False)
    remaining_nan = cities["metro_population"].isna().sum()
    print(f"\nSaved → '{MASTER_FILE}'")
    print(f"Total NaNs remaining: {remaining_nan}")
    print("\nFirst 15 rows:")
    print(cities[["city", "state", "population", "metro_population"]].head(15).to_string(index=False))

if __name__ == "__main__":
    main()