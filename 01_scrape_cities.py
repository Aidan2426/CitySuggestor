"""
01_scrape_cities.py
-------------------
Scrapes the master city list from Wikipedia's
"List of United States cities by population" page.

Output: cities_master.csv
Columns: city, state, city_state, population, land_area_sq_mi, lat, lon

Requirements:
    pip install pandas requests beautifulsoup4 lxml geopy
"""

import re
import sys
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# ── config ────────────────────────────────────────────────────────────────────

WIKI_URL = "https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population"
OUTPUT_FILE = "cities_master.csv"
GEOCODE_DELAY = 1.1

# ── helpers ───────────────────────────────────────────────────────────────────

def clean_cell(cell):
    """Strip footnotes like [c] and extra whitespace from a cell."""
    return re.sub(r"\[.*?\]", "", cell.get_text(separator=" ")).strip()

# ── step 1: scrape ────────────────────────────────────────────────────────────

def scrape_wikipedia_table(url: str) -> pd.DataFrame:
    print("Fetching Wikipedia page...")

    headers = {"User-Agent": "Mozilla/5.0 (compatible; CityDataBot/1.0; personal research project)"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    # Table 1 is the main 348-row cities table (Table 0 is the legend key)
    tables = soup.find_all("table", {"class": "wikitable"})
    if len(tables) < 2:
        raise ValueError(f"Expected at least 2 wikitables, found {len(tables)}")

    table = tables[1]
    cities = []

    for row in table.find_all("tr"):
        cells = row.find_all(["td", "th"])

        # Data rows have 10 cells, all <td scope=none>
        # Skip header rows (all <th>) and short rows
        if len(cells) < 10:
            continue

        # Skip if first cell is a header (column label row)
        if cells[0].name == "th":
            continue

        try:
            # [0] city name
            city = clean_cell(cells[0])

            # [1] state abbreviation
            state = clean_cell(cells[1])

            # [2] 2024 population estimate
            pop_text = re.sub(r"[^\d]", "", clean_cell(cells[2]))
            population = int(pop_text) if pop_text else 0

            # [5] land area in sq mi (format: "302.6 sq mi ...")
            area_text = clean_cell(cells[5])
            area_match = re.search(r"[\d,]+\.?\d*", area_text)
            land_area = float(area_match.group().replace(",", "")) if area_match else None

            if not city or population == 0:
                continue

            cities.append({
                "city":            city,
                "state":           state,
                "population":      population,
                "land_area_sq_mi": land_area,
            })

        except (IndexError, ValueError):
            continue

    print(f"  Parsed {len(cities)} cities")
    return pd.DataFrame(cities)


# ── step 2: clean ─────────────────────────────────────────────────────────────

def clean_table(df: pd.DataFrame) -> pd.DataFrame:
    print("\nCleaning table...")

    df["city"]  = df["city"].str.replace(r"\[.*?\]", "", regex=True).str.strip()
    df["state"] = df["state"].str.replace(r"\[.*?\]", "", regex=True).str.strip()

    df = df[df["city"].notna() & (df["city"] != "")]
    df = df.drop_duplicates(subset=["city", "state"])
    df = df.sort_values("population", ascending=False).reset_index(drop=True)

    print(f"  {len(df)} cities after cleaning")
    print(f"  Population range: {df['population'].min():,} — {df['population'].max():,}")
    print(f"\n  First 5 rows:")
    print(df[["city", "state", "population"]].head(5).to_string(index=False))

    return df


# ── step 3: add join key ──────────────────────────────────────────────────────

def add_city_state_key(df: pd.DataFrame) -> pd.DataFrame:
    df["city_state"] = df["city"] + ", " + df["state"]
    return df


# ── step 4: geocode ───────────────────────────────────────────────────────────

def geocode_cities(df: pd.DataFrame) -> pd.DataFrame:
    print(f"\nGeocoding {len(df)} cities (~6-8 minutes due to rate limiting)...")
    print("  Progress shown every 25 cities.\n")

    geolocator = Nominatim(user_agent="city_data_project_v4")
    lats, lons = [], []

    for idx, row in enumerate(df.itertuples(), start=1):
        query = f"{row.city}, {row.state}, United States"
        try:
            loc = geolocator.geocode(query, timeout=10)
            if loc:
                lats.append(round(loc.latitude, 6))
                lons.append(round(loc.longitude, 6))
            else:
                print(f"  [WARNING] No result: {query}")
                lats.append(None)
                lons.append(None)
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"  [ERROR] {query}: {e}")
            lats.append(None)
            lons.append(None)

        if idx % 25 == 0:
            print(f"  {idx}/{len(df)} geocoded...")

        time.sleep(GEOCODE_DELAY)

    df["lat"] = lats
    df["lon"] = lons

    failed = df["lat"].isna().sum()
    print(f"\n  Done. {len(df) - failed}/{len(df)} cities geocoded successfully.")
    if failed > 0:
        print(f"  Failed ({failed}):")
        print(df[df["lat"].isna()][["city", "state"]].to_string(index=False))

    return df


# ── step 5: save ──────────────────────────────────────────────────────────────

def save_output(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)
    print(f"\nSaved {len(df)} cities → '{path}'")
    print("\nColumns:", list(df.columns))
    print("\nFirst 10 rows:")
    print(df[["city", "state", "population", "lat", "lon"]].head(10).to_string(index=False))


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  01_scrape_cities.py — Master City List Builder")
    print("=" * 55)

    raw     = scrape_wikipedia_table(WIKI_URL)
    cleaned = clean_table(raw)
    cleaned = add_city_state_key(cleaned)

    if "--no-geocode" not in sys.argv:
        cleaned = geocode_cities(cleaned)
    else:
        print("\nSkipping geocoding (--no-geocode flag set)")
        cleaned["lat"] = None
        cleaned["lon"] = None

    save_output(cleaned, OUTPUT_FILE)
    print("\nDone! Next step: run 02_census_data.py")


if __name__ == "__main__":
    main()