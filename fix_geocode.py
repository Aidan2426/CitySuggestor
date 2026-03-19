"""
fix_geocode.py
--------------
Adds lat/lon to cities_master.csv without overwriting any other columns.
Run this once — takes ~6-8 minutes for 346 cities.

Requirements:
    pip install geopy
"""

import time
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

MASTER_FILE   = "cities_master.csv"
GEOCODE_DELAY = 1.1

def main():
    cities = pd.read_csv(MASTER_FILE)
    print(f"Loaded {len(cities)} cities")
    print(f"Geocoding all cities — this takes ~6-8 minutes...\n")

    geolocator = Nominatim(user_agent="city_suggestor_geocode_fix_v1")

    lats, lons = [], []

    for idx, row in enumerate(cities.itertuples(), start=1):
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
            print(f"  {idx}/{len(cities)} geocoded...")

        time.sleep(GEOCODE_DELAY)

    cities["lat"] = lats
    cities["lon"] = lons

    failed = cities["lat"].isna().sum()
    print(f"\nGeocoding complete!")
    print(f"  Success: {len(cities) - failed}/{len(cities)}")
    print(f"  Failed:  {failed}")

    if failed > 0:
        print("\n  Cities missing coordinates:")
        print(cities[cities["lat"].isna()][["city", "state"]].to_string(index=False))

    cities.to_csv(MASTER_FILE, index=False)
    print(f"\nSaved → '{MASTER_FILE}'")
    print("\nSample:")
    print(cities[["city", "state", "lat", "lon"]].head(10).to_string(index=False))
    print("\nNow re-run: python 03_temperature.py")

if __name__ == "__main__":
    main()