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

# ── hardcoded zoos ────────────────────────────────────────────────────────────

ZOOS = [
    # Northeast
    ("Bronx Zoo NY",                      40.8506,  -73.8769),
    ("Central Park Zoo NY",               40.7678,  -73.9718),
    ("Philadelphia Zoo PA",               39.9736,  -75.1954),
    ("Pittsburgh Zoo PA",                 40.4773,  -79.9430),
    ("Franklin Park Zoo MA",              42.3022,  -71.0897),
    ("Roger Williams Zoo RI",             41.8100,  -71.4290),
    ("Beardsley Zoo CT",                  41.1940,  -73.2010),
    ("Maryland Zoo MD",                   39.3240,  -76.6490),
    ("Buffalo Zoo NY",                    42.9260,  -78.8710),
    ("Utica Zoo NY",                      43.0870,  -75.2270),
    # Mid-Atlantic / Southeast
    ("Smithsonian National Zoo DC",       38.9303,  -77.0503),
    ("Virginia Zoo VA",                   36.8710,  -76.2990),
    ("Roanoke Zoo VA",                    37.2510,  -79.9370),
    ("Riverbanks Zoo SC",                 34.0010,  -81.0620),
    ("Greenville Zoo SC",                 34.8390,  -82.3600),
    ("North Carolina Zoo NC",             35.5080,  -79.7640),
    ("Asheboro Zoo NC",                   35.5080,  -79.7640),
    ("Chattanooga Zoo TN",                35.0550,  -85.3070),
    ("Zoo Knoxville TN",                  35.9620,  -83.9110),
    ("Nashville Zoo TN",                  36.0560,  -86.7280),
    ("Birmingham Zoo AL",                 33.4880,  -86.7960),
    ("Montgomery Zoo AL",                 32.3970,  -86.2760),
    ("Little Rock Zoo AR",                34.7310,  -92.3330),
    ("Jacksonville Zoo FL",               30.3870,  -81.5480),
    ("Tampa Lowry Park Zoo FL",           28.0140,  -82.4720),
    ("Zoo Miami FL",                      25.6060,  -80.4030),
    ("Central Florida Zoo FL",            28.8140,  -81.3780),
    # Midwest
    ("Lincoln Park Zoo IL",               41.9210,  -87.6340),
    ("Brookfield Zoo IL",                 41.8320,  -87.8400),
    ("Indianapolis Zoo IN",               39.7680,  -86.1840),
    ("Fort Wayne Children's Zoo IN",      41.1010,  -85.1440),
    ("Cincinnati Zoo OH",                 39.1430,  -84.5080),
    ("Cleveland Metroparks Zoo OH",       41.4450,  -81.7120),
    ("Columbus Zoo OH",                   40.1530,  -83.1270),
    ("Toledo Zoo OH",                     41.6530,  -83.5920),
    ("Detroit Zoo MI",                    42.4810,  -83.1490),
    ("Potter Park Zoo MI",                42.7130,  -84.5570),
    ("Milwaukee County Zoo WI",           43.0440,  -88.0370),
    ("Minnesota Zoo MN",                  44.7710,  -93.1870),
    ("Como Zoo MN",                       44.9810,  -93.1530),
    ("Omaha Henry Doorly Zoo NE",         41.2120,  -95.9400),
    ("Kansas City Zoo MO",                38.9610,  -94.5430),
    ("St. Louis Zoo MO",                  38.6350,  -90.2900),
    ("Dickerson Park Zoo MO",             37.2340,  -93.2750),
    ("Sedgwick County Zoo KS",            37.7210,  -97.4000),
    ("Sioux Falls Great Plains Zoo SD",   43.5480,  -96.7290),
    ("Des Moines Blank Park Zoo IA",      41.5480,  -93.6700),
    # South / Southwest
    ("Houston Zoo TX",                    29.7150,  -95.3900),
    ("Dallas Zoo TX",                     32.7410,  -96.8100),
    ("Fort Worth Zoo TX",                 32.7440,  -97.3590),
    ("San Antonio Zoo TX",                29.4610,  -98.4740),
    ("El Paso Zoo TX",                    31.7750,  -106.4450),
    ("Abilene Zoo TX",                    32.4100,  -99.7070),
    ("Oklahoma City Zoo OK",              35.5290,  -97.4700),
    ("Tulsa Zoo OK",                      36.1860,  -95.9010),
    ("New Orleans Audubon Zoo LA",        29.9260,  -90.1370),
    ("Baton Rouge Zoo LA",                30.3900,  -91.1760),
    ("Memphis Zoo TN",                    35.1490,  -90.0370),
    ("Phoenix Zoo AZ",                    33.4500, -111.9460),
    ("Tucson Reid Park Zoo AZ",           32.2110, -110.9230),
    ("Albuquerque BioPark Zoo NM",        35.1100, -106.6860),
    # Mountain West
    ("Denver Zoo CO",                     39.7500, -104.9490),
    ("Cheyenne Mountain Zoo CO",          38.7840, -104.8420),
    ("Hogle Zoo UT",                      40.7650, -111.8180),
    ("Las Vegas Springs Preserve NV",     36.1770, -115.1870),
    ("Zoo Boise ID",                      43.6050, -116.1930),
    ("Billings ZooMontana MT",            45.7800, -108.5490),
    # Pacific
    ("Oregon Zoo OR",                     45.5090, -122.7160),
    ("Woodland Park Zoo WA",              47.6680, -122.3530),
    ("Point Defiance Zoo WA",             47.3180, -122.5350),
    ("Sacramento Zoo CA",                 38.5490, -121.4880),
    ("San Francisco Zoo CA",              37.7330, -122.5040),
    ("Oakland Zoo CA",                    37.7590, -122.1780),
    ("LA Zoo CA",                         34.1500, -118.2990),
    ("San Diego Zoo CA",                  32.7350, -117.1510),
    ("San Diego Safari Park CA",          33.0970, -116.9990),
    ("Fresno Chaffee Zoo CA",             36.7510, -119.7810),
    ("Santa Barbara Zoo CA",              34.4130, -119.6760),
    # Hawaii / Alaska
    ("Honolulu Zoo HI",                   21.2660, -157.8250),
    ("Alaska Zoo AK",                     61.1270, -149.8420),
]

# ── hardcoded theme parks ─────────────────────────────────────────────────────

THEME_PARKS = [
    # Florida
    ("Walt Disney World FL",              28.3852,  -81.5639),
    ("Universal Orlando FL",              28.4749,  -81.4676),
    ("SeaWorld Orlando FL",               28.4119,  -81.4614),
    ("Busch Gardens Tampa FL",            28.0378,  -82.4208),
    ("LEGOLAND Florida FL",               28.0000,  -81.6900),
    ("Fun Spot America FL",               28.4440,  -81.4590),
    # California
    ("Disneyland CA",                     33.8121, -117.9190),
    ("Universal Studios Hollywood CA",    34.1381, -118.3534),
    ("SeaWorld San Diego CA",             32.7641, -117.2267),
    ("Knott's Berry Farm CA",             33.8442, -117.9988),
    ("Six Flags Magic Mountain CA",       34.4254, -118.5970),
    ("California's Great America CA",     37.3966, -121.9766),
    ("LEGOLAND California CA",            33.1262, -117.3123),
    ("Six Flags Discovery Kingdom CA",    38.1390, -122.2340),
    # Northeast
    ("Six Flags Great Adventure NJ",      40.1376,  -74.4409),
    ("Hersheypark PA",                    40.2874,  -76.6549),
    ("Knoebels PA",                       40.8810,  -76.5050),
    ("Dorney Park PA",                    40.5570,  -75.5890),
    ("Six Flags New England MA",          42.0400,  -72.6110),
    ("Rye Playland NY",                   40.9790,  -73.6780),
    ("Darien Lake NY",                    42.8910,  -78.5040),
    # Mid-Atlantic / Southeast
    ("Busch Gardens Williamsburg VA",     37.2508,  -76.6440),
    ("Kings Dominion VA",                 37.8354,  -77.4448),
    ("Carowinds NC",                      35.1027,  -80.9394),
    ("Dollywood TN",                      35.7950,  -83.5290),
    ("Six Flags Over Georgia GA",         33.7701,  -84.5513),
    ("Six Flags White Water GA",          33.9340,  -84.4950),
    # Midwest
    ("Cedar Point OH",                    41.4806,  -82.6877),
    ("Kings Island OH",                   39.3430,  -84.2700),
    ("Michigan's Adventure MI",           43.3970,  -86.4260),
    ("Six Flags Great America IL",        42.3700,  -87.9360),
    ("Holiday World IN",                  38.1210,  -86.9440),
    ("Indiana Beach IN",                  40.5660,  -86.7700),
    ("Worlds of Fun MO",                  39.1700,  -94.4870),
    ("Silver Dollar City MO",             36.6670,  -93.3380),
    ("Valleyfair MN",                     44.7230,  -93.4700),
    ("Adventureland IA",                  41.6810,  -93.5470),
    ("Lagoon UT",                         41.0820, -111.9000),
    ("Elitch Gardens CO",                 39.7500, -105.0110),
    ("Worlds of Fun KS",                  39.1700,  -94.4870),
    # South / Southwest
    ("Six Flags Fiesta Texas TX",         29.5990,  -98.6110),
    ("Six Flags Over Texas TX",           32.7572,  -97.0714),
    ("SeaWorld San Antonio TX",           29.4560,  -98.7000),
    ("Six Flags New Orleans LA",          29.9310,  -90.1630),
    ("Six Flags St. Louis MO",            38.5070,  -90.6750),
    # Pacific NW / Mountain
    ("Silverwood ID",                     47.8960, -116.7280),
    ("Wild Waves WA",                     47.3150, -122.2860),
    ("Oaks Park OR",                      45.4820, -122.6760),
    # Hawaii
    ("Wet n Wild Hawaii HI",              21.3670, -158.0050),
]


def get_zoos():
    print(f"  Using hardcoded list: {len(ZOOS)} zoos")
    return [(lat, lon, name) for name, lat, lon in ZOOS]


def get_theme_parks():
    print(f"  Using hardcoded list: {len(THEME_PARKS)} theme parks")
    return [(lat, lon, name) for name, lat, lon in THEME_PARKS]

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
    zoos        = get_zoos()
    theme_parks = get_theme_parks()

    # ── process each city (pure math, instant) ────────────────────────────────
    # Separate passes: airport (if missing), zoo/theme park (if missing)
    needs_airport = cities[
        cities["dist_airport_miles"].isna() & cities["lat"].notna()
    ].index.tolist()

    needs_poi = cities[
        (cities["dist_zoo_miles"].isna() | cities["dist_theme_park_miles"].isna()) &
        cities["lat"].notna()
    ].index.tolist()

    all_needs = sorted(set(needs_airport) | set(needs_poi))
    print(f"\nCalculating distances for {len(all_needs)} cities "
          f"({len(needs_airport)} missing airport, {len(needs_poi)} missing zoo/theme park)...")

    for count, idx in enumerate(all_needs, start=1):
        row = cities.loc[idx]
        lat = float(row["lat"])
        lon = float(row["lon"])

        if idx in needs_airport:
            dist_ap, name_ap = nearest_airport(lat, lon)
            cities.at[idx, "dist_airport_miles"] = dist_ap
            cities.at[idx, "nearest_airport"]    = name_ap

        if idx in needs_poi:
            dist_zoo, name_zoo   = nearest_poi(lat, lon, zoos)
            dist_park, name_park = nearest_poi(lat, lon, theme_parks)
            cities.at[idx, "dist_zoo_miles"]        = dist_zoo
            cities.at[idx, "nearest_zoo"]           = name_zoo
            cities.at[idx, "dist_theme_park_miles"] = dist_park
            cities.at[idx, "nearest_theme_park"]    = name_park

        if count % 50 == 0:
            print(f"  {count}/{len(all_needs)} done...")

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