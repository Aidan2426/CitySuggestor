"""
05_distances.py
---------------
Calculates straight-line distances from each city to:
  1. Nearest major US airport (hardcoded list, instant)
  2. Nearest zoo (one bulk Overpass API call for all US zoos)
  3. Nearest theme park (one bulk Overpass API call for all US theme parks)

Total API calls: 2 (instead of 700)
Runtime: ~1-2 minutes

Input:  cities_master.csv
Output: cities_master.csv (updated in place)

Requirements:
    pip install pandas requests geopy
"""

import sys
import time
import requests
import pandas as pd
from geopy.distance import geodesic

MASTER_FILE  = "cities_master.csv"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# ── major US airports ─────────────────────────────────────────────────────────

MAJOR_AIRPORTS = [
    ("Hartsfield-Jackson Atlanta",        33.6407,  -84.4277),
    ("Dallas/Fort Worth",                  32.8998,  -97.0403),
    ("Denver",                             39.8561, -104.6737),
    ("O'Hare Chicago",                     41.9742,  -87.9073),
    ("Los Angeles",                        33.9425, -118.4081),
    ("Dallas Love Field",                  32.8471,  -96.8518),
    ("Charlotte Douglas",                  35.2144,  -80.9431),
    ("McCarran Las Vegas",                 36.0840, -115.1537),
    ("Phoenix Sky Harbor",                 33.4373, -112.0078),
    ("Miami",                              25.7959,  -80.2870),
    ("Seattle-Tacoma",                     47.4502, -122.3088),
    ("Orlando",                            28.4312,  -81.3081),
    ("Newark Liberty",                     40.6895,  -74.1745),
    ("JFK New York",                       40.6413,  -73.7781),
    ("LaGuardia New York",                 40.7772,  -73.8726),
    ("San Francisco",                      37.6213, -122.3790),
    ("George Bush Houston",                29.9902,  -95.3368),
    ("Logan Boston",                       42.3656,  -71.0096),
    ("Minneapolis-Saint Paul",             44.8848,  -93.2223),
    ("Detroit Metro",                      42.2162,  -83.3554),
    ("Philadelphia",                       39.8729,  -75.2437),
    ("Baltimore/Washington",               39.1754,  -76.6682),
    ("Salt Lake City",                     40.7899, -111.9791),
    ("Reagan Washington",                  38.8521,  -77.0377),
    ("Dulles Washington",                  38.9531,  -77.4565),
    ("Portland",                           45.5898, -122.5951),
    ("San Diego",                          32.7338, -117.1933),
    ("Tampa",                              27.9755,  -82.5332),
    ("Nashville",                          36.1263,  -86.6774),
    ("St. Louis Lambert",                  38.7487,  -90.3700),
    ("Kansas City",                        39.2976,  -94.7139),
    ("Austin-Bergstrom",                   30.1975,  -97.6664),
    ("Midway Chicago",                     41.7868,  -87.7522),
    ("Raleigh-Durham",                     35.8776,  -78.7875),
    ("San Jose",                           37.3626, -121.9290),
    ("Cleveland Hopkins",                  41.4117,  -81.8498),
    ("Sacramento",                         38.6954, -121.5908),
    ("Indianapolis",                       39.7173,  -86.2944),
    ("Pittsburgh",                         40.4915,  -80.2329),
    ("Cincinnati/Northern Kentucky",       39.0488,  -84.6678),
    ("Milwaukee Mitchell",                 42.9472,  -87.8966),
    ("Louisville",                         38.1744,  -85.7360),
    ("Memphis",                            35.0424,  -89.9767),
    ("Richmond",                           37.5052,  -77.3197),
    ("Jacksonville",                       30.4941,  -81.6879),
    ("New Orleans",                        29.9934,  -90.2580),
    ("Oklahoma City",                      35.3931,  -97.6007),
    ("Tulsa",                              36.1984,  -95.8881),
    ("Omaha Eppley",                       41.3032,  -95.8940),
    ("Albuquerque",                        35.0402, -106.6090),
    ("Tucson",                             32.1161, -110.9410),
    ("El Paso",                            31.8072, -106.3779),
    ("Burbank Hollywood",                  34.2007, -118.3585),
    ("Long Beach",                         33.8177, -118.1516),
    ("Ontario California",                 34.0560, -117.6012),
    ("John Wayne Orange County",           33.6757, -117.8682),
    ("Spokane",                            47.6199, -117.5338),
    ("Boise",                              43.5644, -116.2228),
    ("Colorado Springs",                   38.8058, -104.7008),
    ("Fresno Yosemite",                    36.7762, -119.7182),
    ("Reno-Tahoe",                         39.4991, -119.7681),
    ("Honolulu",                           21.3245, -157.9251),
    ("Ted Stevens Anchorage",              61.1744, -149.9963),
    ("Buffalo Niagara",                    42.9405,  -78.7322),
    ("Albany",                             42.7483,  -73.8017),
    ("Hartford Bradley",                   41.9389,  -72.6832),
    ("Providence Green",                   41.7236,  -71.4282),
    ("Norfolk",                            36.8946,  -76.0132),
    ("Greenville-Spartanburg",             34.8957,  -82.2189),
    ("Charleston SC",                      32.8987,  -80.0405),
    ("Savannah",                           32.1276,  -81.2021),
    ("Fort Lauderdale",                    26.0726,  -80.1527),
    ("Palm Beach",                         26.6832,  -80.0956),
    ("Little Rock",                        34.7294,  -92.2243),
    ("Des Moines",                         41.5340,  -93.6631),
    ("Grand Rapids",                       42.8808,  -85.5228),
    ("Lexington",                          38.0365,  -84.6060),
    ("Knoxville",                          35.8137,  -83.9940),
    ("Birmingham",                         33.5629,  -86.7535),
    ("Dayton",                             39.9024,  -84.2194),
    ("Columbus Ohio",                      39.9980,  -82.8919),
    ("Wichita",                            37.6499,  -97.4331),
    ("Lubbock",                            33.6636, -101.8228),
    ("Amarillo",                           35.2194, -101.7059),
    ("McAllen",                            26.1758,  -98.2386),
    ("Corpus Christi",                     27.7704,  -97.5012),
    ("San Antonio Intl",                   29.5337,  -98.4698),
    ("Billings",                           45.8077, -108.5430),
    ("Sioux Falls",                        43.5820,  -96.7419),
    ("Fargo",                              46.9207,  -96.8158),
]

# ── airport distance ──────────────────────────────────────────────────────────

def nearest_airport(lat: float, lon: float) -> tuple:
    best_dist = float("inf")
    best_name = None
    for name, alat, alon in MAJOR_AIRPORTS:
        dist = geodesic((lat, lon), (alat, alon)).miles
        if dist < best_dist:
            best_dist = dist
            best_name = name
    return round(best_dist, 1), best_name

# ── bulk Overpass fetch ───────────────────────────────────────────────────────

def fetch_all_pois(poi_type: str) -> list:
    """
    Fetches ALL US locations of a given POI type in one API call.
    Returns list of (lat, lon, name) tuples.
    poi_type: 'zoo' or 'theme_park'
    """
    print(f"  Fetching all US {poi_type}s from OpenStreetMap...")

    if poi_type == "zoo":
        query = """
        [out:json][timeout:60];
        area["ISO3166-1"="US"][admin_level=2]->.usa;
        (
          node["tourism"="zoo"](area.usa);
          way["tourism"="zoo"](area.usa);
          node["amenity"="zoo"](area.usa);
          way["amenity"="zoo"](area.usa);
        );
        out center;
        """
    else:  # theme_park
        query = """
        [out:json][timeout:60];
        area["ISO3166-1"="US"][admin_level=2]->.usa;
        (
          node["tourism"="theme_park"](area.usa);
          way["tourism"="theme_park"](area.usa);
        );
        out center;
        """

    for attempt in range(3):
        try:
            resp = requests.post(
                OVERPASS_URL,
                data={"data": query},
                timeout=90
            )
            resp.raise_for_status()
            data = resp.json()
            elements = data.get("elements", [])

            pois = []
            for el in elements:
                if el["type"] == "node":
                    elat, elon = el.get("lat"), el.get("lon")
                else:
                    center = el.get("center", {})
                    elat, elon = center.get("lat"), center.get("lon")

                if elat is None or elon is None:
                    continue

                name = el.get("tags", {}).get("name", "Unknown")
                pois.append((elat, elon, name))

            print(f"  Found {len(pois)} {poi_type}s in the US")
            return pois

        except Exception as e:
            print(f"  [ERROR attempt {attempt+1}/3] {poi_type}: {e}")
            time.sleep(10)

    return []

def nearest_poi(lat: float, lon: float, pois: list) -> tuple:
    """Find nearest POI from a preloaded list."""
    if not pois:
        return None, None
    best_dist = float("inf")
    best_name = None
    for plat, plon, pname in pois:
        dist = geodesic((lat, lon), (plat, plon)).miles
        if dist < best_dist:
            best_dist = dist
            best_name = pname
    return round(best_dist, 1), best_name

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  05_distances.py — Airport, Zoo, Theme Park")
    print("=" * 55)

    try:
        cities = pd.read_csv(MASTER_FILE)
        print(f"Loaded {len(cities)} cities from '{MASTER_FILE}'")
    except FileNotFoundError:
        print(f"ERROR: '{MASTER_FILE}' not found.")
        sys.exit(1)

    for col in ["dist_airport_miles", "nearest_airport",
                "dist_zoo_miles",     "nearest_zoo",
                "dist_theme_park_miles", "nearest_theme_park"]:
        if col not in cities.columns:
            cities[col] = None

    # ── fetch all POIs upfront (2 API calls total) ────────────────────────────
    print("\nFetching POI data (2 API calls total)...")
    zoos        = fetch_all_pois("zoo")
    time.sleep(3)
    theme_parks = fetch_all_pois("theme_park")

    # ── process each city (pure math, instant) ────────────────────────────────
    needs_fetch = cities[
        cities["dist_airport_miles"].isna() & cities["lat"].notna()
    ].index.tolist()

    print(f"\nCalculating distances for {len(needs_fetch)} cities...")

    for count, idx in enumerate(needs_fetch, start=1):
        row = cities.loc[idx]
        lat = float(row["lat"])
        lon = float(row["lon"])

        dist_ap, name_ap     = nearest_airport(lat, lon)
        dist_zoo, name_zoo   = nearest_poi(lat, lon, zoos)
        dist_park, name_park = nearest_poi(lat, lon, theme_parks)

        cities.at[idx, "dist_airport_miles"]    = dist_ap
        cities.at[idx, "nearest_airport"]       = name_ap
        cities.at[idx, "dist_zoo_miles"]        = dist_zoo
        cities.at[idx, "nearest_zoo"]           = name_zoo
        cities.at[idx, "dist_theme_park_miles"] = dist_park
        cities.at[idx, "nearest_theme_park"]    = name_park

        if count % 50 == 0:
            print(f"  {count}/{len(needs_fetch)} done...")

    cities.to_csv(MASTER_FILE, index=False)

    print(f"\nDone!")
    print(f"\nSaved -> '{MASTER_FILE}'")
    print("\nSample (first 10 rows):")
    cols = ["city", "state", "dist_airport_miles", "nearest_airport",
            "dist_zoo_miles", "dist_theme_park_miles"]
    print(cities[cols].head(10).to_string(index=False))
    print("\nNext step: run 06_nature.py")

if __name__ == "__main__":
    main()