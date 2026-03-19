"""
01b_scrape_metro_population.py
------------------------------
Scrapes US Metropolitan Statistical Area (MSA) populations from Wikipedia
and joins them onto cities_master.csv.

Input:  cities_master.csv  (from 01_scrape_cities.py)
Output: cities_master.csv  (updated in place — adds metro_population column)

Requirements:
    pip install pandas requests beautifulsoup4 lxml
"""

import re
import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ── config ────────────────────────────────────────────────────────────────────

WIKI_URL    = "https://en.wikipedia.org/wiki/Metropolitan_statistical_area"
MASTER_FILE = "cities_master.csv"

# ── helpers ───────────────────────────────────────────────────────────────────

def clean_cell(cell):
    return re.sub(r"\[.*?\]", "", cell.get_text(separator=" ")).strip()

def extract_cities_and_state(msa_name: str):
    """
    Extracts ALL city names and the primary state from an MSA name.

    Examples:
      'New York–Newark–Jersey City, NY-NJ'   → (['New York','Newark','Jersey City'], 'NY')
      'Dallas–Fort Worth–Arlington, TX'       → (['Dallas','Fort Worth','Arlington'], 'TX')
      'San Francisco–Oakland–Fremont, CA'     → (['San Francisco','Oakland','Fremont'], 'CA')
      'Urban Honolulu, HI'                    → (['Urban Honolulu','Honolulu'], 'HI')
      'Louisville/Jefferson County, KY-IN'    → (['Louisville'], 'KY')

    Uses both em dash (–) and regular hyphen (-) as separators.
    """
    # Split on comma to get city part and state part
    parts = msa_name.split(",")
    if len(parts) < 2:
        return [msa_name.strip()], None

    city_part  = parts[0].strip()
    state_part = parts[1].strip()

    # Primary state = first 2-letter uppercase code
    state_match = re.match(r"([A-Z]{2})", state_part)
    primary_state = state_match.group(1) if state_match else None

    # Split city part on em dash (–) or regular hyphen surrounded by spaces
    # Use regex to split on em dash or ' - ' (spaced hyphen)
    raw_cities = re.split(r"[–]|(?<=\s)-(?=\s)", city_part)

    cities = []
    for c in raw_cities:
        c = c.strip()
        # Remove things like 'Urban' prefix (Urban Honolulu → also add Honolulu)
        cities.append(c)
        if c.startswith("Urban "):
            cities.append(c.replace("Urban ", ""))
        # Handle slash names like 'Louisville/Jefferson County' → keep 'Louisville'
        if "/" in c:
            cities.append(c.split("/")[0].strip())
        # Handle 'Nashville-Davidson' style (hyphen within a city name)
        # These are compound city names — keep as-is but also try first word
        if "-" in c:
            cities.append(c.split("-")[0].strip())

    # Deduplicate while preserving order
    seen = set()
    unique_cities = []
    for c in cities:
        if c and c not in seen:
            seen.add(c)
            unique_cities.append(c)

    return unique_cities, primary_state

# ── step 1: scrape MSA table ──────────────────────────────────────────────────

def scrape_msa_table(url: str) -> pd.DataFrame:
    print("Fetching MSA Wikipedia page...")

    headers = {"User-Agent": "Mozilla/5.0 (compatible; CityDataBot/1.0; personal research project)"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    tables = soup.find_all("table", {"class": "wikitable"})
    print(f"  Found {len(tables)} wikitables")

    main_table = max(tables, key=lambda t: len(t.find_all("tr")))
    print(f"  Using table with {len(main_table.find_all('tr'))} rows")

    msas = []

    for row in main_table.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) < 3:
            continue
        if all(c.name == "th" for c in cells):
            continue

        try:
            msa_name = clean_cell(cells[0])
            if not msa_name or "metropolitan" in msa_name.lower():
                continue

            pop_text = re.sub(r"[^\d]", "", clean_cell(cells[1]))
            metro_pop = int(pop_text) if pop_text else 0
            if metro_pop == 0:
                continue

            cities_list, primary_state = extract_cities_and_state(msa_name)

            msas.append({
                "msa_name":       msa_name,
                "cities_list":    cities_list,
                "primary_state":  primary_state,
                "metro_population": metro_pop,
            })

        except (IndexError, ValueError):
            continue

    print(f"  Parsed {len(msas)} MSAs")
    return pd.DataFrame(msas)


# ── step 2: build lookup dict ─────────────────────────────────────────────────

def build_lookup(msas: pd.DataFrame) -> dict:
    """
    Builds a dict: (city_lower, state) → metro_population
    For each MSA, every city name variant gets an entry.
    If a city appears in multiple MSAs, the largest metro wins.
    """
    lookup = {}  # (city_lower, state) → metro_pop

    for _, row in msas.iterrows():
        state = row["primary_state"]
        if not state:
            continue
        for city in row["cities_list"]:
            key = (city.lower().strip(), state.upper())
            # Keep the largest metro population if city appears in multiple MSAs
            if key not in lookup or row["metro_population"] > lookup[key]:
                lookup[key] = row["metro_population"]

    return lookup


# ── step 3: match cities ──────────────────────────────────────────────────────

def join_metro_population(cities: pd.DataFrame, lookup: dict) -> pd.DataFrame:
    print("\nMatching cities to MSA metro populations...")

    metro_pops = []
    for _, row in cities.iterrows():
        key = (row["city"].lower().strip(), row["state"].upper().strip())
        metro_pops.append(lookup.get(key, None))

    cities["metro_population"] = metro_pops

    matched   = sum(1 for v in metro_pops if v is not None)
    unmatched = sum(1 for v in metro_pops if v is None)

    print(f"  Matched:   {matched}/{len(cities)} cities")
    print(f"  Unmatched: {unmatched} cities")

    if unmatched > 0:
        print("\n  Unmatched cities:")
        print(cities[cities["metro_population"].isna()][["city", "state"]].to_string(index=False))

    return cities


# ── step 4: save ──────────────────────────────────────────────────────────────

def save_output(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)
    print(f"\nSaved {len(df)} cities → '{path}'")
    print("\nFirst 10 rows:")
    print(df[["city", "state", "population", "metro_population"]].head(10).to_string(index=False))


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  01b_scrape_metro_population.py")
    print("=" * 55)

    try:
        cities = pd.read_csv(MASTER_FILE)
        print(f"Loaded {len(cities)} cities from '{MASTER_FILE}'")
    except FileNotFoundError:
        print(f"ERROR: '{MASTER_FILE}' not found. Run 01_scrape_cities.py first.")
        sys.exit(1)

    msas    = scrape_msa_table(WIKI_URL)
    lookup  = build_lookup(msas)
    updated = join_metro_population(cities, lookup)
    save_output(updated, MASTER_FILE)

    print("\nDone! cities_master.csv now includes metro_population.")
    print("Next step: run 02_census_data.py")

if __name__ == "__main__":
    main()