"""
05b_fix_distances.py
--------------------
Replaces zoo and theme park distances with hardcoded accurate lists.
Keeps existing airport distance data untouched.

Input:  cities_master.csv
Output: cities_master.csv (updated in place)

Requirements:
    pip install pandas geopy
"""

import pandas as pd
from geopy.distance import geodesic

MASTER_FILE = "cities_master.csv"

# ── major US zoos ─────────────────────────────────────────────────────────────

MAJOR_ZOOS = [
    ("Bronx Zoo",                              40.8506,  -73.8769),
    ("Central Park Zoo",                       40.7678,  -73.9718),
    ("Queens Zoo",                             40.7498,  -73.8510),
    ("Prospect Park Zoo",                      40.6605,  -73.9655),
    ("Staten Island Zoo",                      40.6262,  -74.1159),
    ("Brookfield Zoo Chicago",                 41.8353,  -87.8367),
    ("Lincoln Park Zoo Chicago",               41.9214,  -87.6337),
    ("Los Angeles Zoo",                        34.1483, -118.2879),
    ("San Diego Zoo",                          32.7353, -117.1490),
    ("San Diego Zoo Safari Park",              33.0978, -116.9983),
    ("San Francisco Zoo",                      37.7325, -122.5035),
    ("Oakland Zoo",                            37.7685, -122.1712),
    ("Houston Zoo",                            29.7153,  -95.3903),
    ("Phoenix Zoo",                            33.4501, -111.9470),
    ("Philadelphia Zoo",                       39.9714,  -75.1957),
    ("National Zoo Washington DC",             38.9295,  -77.0499),
    ("Atlanta Zoo",                            33.7991,  -84.3941),
    ("Dallas Zoo",                             32.7422,  -96.8165),
    ("Fort Worth Zoo",                         32.7405,  -97.3467),
    ("Denver Zoo",                             39.7499, -104.9508),
    ("Miami Zoo",                              25.6167,  -80.4020),
    ("Tampa's Lowry Park Zoo",                 28.0117,  -82.4694),
    ("Busch Gardens Tampa",                    28.0375,  -82.4208),
    ("Seattle Woodland Park Zoo",              47.6684, -122.3508),
    ("Minnesota Zoo",                          44.7726,  -93.1930),
    ("Como Park Zoo",                          44.9819,  -93.1527),
    ("Detroit Zoo",                            42.4785,  -83.1489),
    ("Cincinnati Zoo",                         39.1452,  -84.5088),
    ("Cleveland Zoo",                          41.4528,  -81.7607),
    ("Columbus Zoo",                           40.1567,  -83.1196),
    ("St. Louis Zoo",                          38.6349,  -90.2905),
    ("Kansas City Zoo",                        39.0307,  -94.5876),
    ("Indianapolis Zoo",                       39.7653,  -86.1839),
    ("Louisville Zoo",                         38.2217,  -85.7166),
    ("Nashville Zoo",                          36.0518,  -86.7659),
    ("Memphis Zoo",                            35.1497,  -90.0553),
    ("Birmingham Zoo",                         33.4874,  -86.7987),
    ("New Orleans Audubon Zoo",                29.9239,  -90.1303),
    ("Baton Rouge Zoo",                        30.5247,  -91.1533),
    ("Oklahoma City Zoo",                      35.5032,  -97.4788),
    ("Tulsa Zoo",                              36.2079,  -95.8942),
    ("Omaha Henry Doorly Zoo",                 41.2122,  -95.9381),
    ("Salt Lake City Zoo",                     40.7695, -111.8451),
    ("Albuquerque Zoo",                        35.0967, -106.6693),
    ("Tucson Reid Park Zoo",                   32.2101, -110.9308),
    ("El Paso Zoo",                            31.7668, -106.4512),
    ("San Antonio Zoo",                        29.4610,  -98.4696),
    ("Austin Zoo",                             30.2240,  -97.8949),
    ("Raleigh NC Zoo",                         35.5773,  -79.7651),
    ("Charlotte NC Zoo",                       35.2698,  -80.5234),
    ("Pittsburgh Zoo",                         40.4753,  -79.9280),
    ("Baltimore Zoo",                          39.3244,  -76.6464),
    ("Providence Zoo",                         41.8006,  -71.4278),
    ("Buffalo Zoo",                            42.9304,  -78.8714),
    ("Sacramento Zoo",                         38.5511, -121.4692),
    ("Fresno Chaffee Zoo",                     36.7979, -119.7845),
    ("Bakersfield Zoo",                        35.3533, -119.0296),
    ("Portland Oregon Zoo",                    45.5097, -122.7153),
    ("Tacoma Point Defiance Zoo",              47.3190, -122.5304),
    ("Spokane Zoo",                            47.6609, -117.3975),
    ("Boise Zoo",                              43.5971, -116.2088),
    ("Anchorage Alaska Zoo",                   61.1363, -149.8133),
    ("Honolulu Zoo",                           21.2712, -157.8220),
    ("Milwaukee County Zoo",                   43.0334,  -88.0367),
    ("Green Bay NEW Zoo",                      44.5279,  -87.9785),
    ("Little Rock Zoo",                        34.7327,  -92.2971),
    ("Jackson Mississippi Zoo",                32.2998,  -90.2050),
    ("Knoxville Zoo",                          35.9784,  -83.9235),
    ("Chattanooga Zoo",                        35.0454,  -85.2964),
    ("Huntsville Zoo",                         34.6963,  -86.6175),
    ("Montgomery Zoo",                         32.3744,  -86.3088),
    ("Mobile Alabama Zoo",                     30.6640,  -88.1002),
    ("Virginia Beach Zoo",                     36.7936,  -76.0643),
    ("Norfolk Zoo",                            36.8768,  -76.0134),
    ("Richmond Metro Zoo",                     37.3552,  -77.6039),
    ("Greensboro Science Center Zoo",          36.0978,  -79.8144),
    ("Columbia SC Riverbanks Zoo",             34.0226,  -81.0565),
    ("Savannah Zoo",                           32.0094,  -81.1303),
    ("Jacksonville Zoo",                       30.3881,  -81.6568),
    ("Miami Metrozoo",                         25.6167,  -80.4020),
    ("Orlando Central Florida Zoo",            28.7397,  -81.3603),
    ("Brevard Zoo",                            28.1172,  -80.6754),
    ("Palm Beach Zoo",                         26.7024,  -80.0520),
    ("Topeka Zoo",                             39.0724,  -95.6958),
    ("Wichita Zoo",                            37.6868,  -97.3517),
    ("Sioux Falls Great Plains Zoo",           43.5457,  -96.7143),
    ("Fargo Red River Zoo",                    46.8571,  -96.7823),
    ("Cheyenne Mountain Zoo",                  38.7763, -104.8476),
    ("Pueblo Zoo",                             38.2634, -104.6085),
    ("Fort Collins Zoo",                       40.5700, -105.0900),
    ("Reno Animal Ark",                        39.5978, -119.8732),
    ("Las Vegas Springs Preserve",             36.1821, -115.1864),
    ("Tacoma Point Defiance Zoo 2",            47.3190, -122.5304),
    ("Grand Rapids John Ball Zoo",             42.9644,  -85.6925),
    ("Lansing Potter Park Zoo",                42.7133,  -84.5397),
    ("Toledo Zoo",                             41.6392,  -83.6108),
    ("Akron Zoo",                              41.0820,  -81.5144),
    ("Dayton Zoo",                             39.7500,  -84.1800),
    ("Lexington Kentucky Zoo",                 38.0622,  -84.5301),
    ("Evansville Zoo",                         37.9886,  -87.5880),
    ("South Bend Zoo",                         41.6739,  -86.2297),
    ("Fort Wayne Zoo",                         41.0849,  -85.1399),
    ("Des Moines Zoo",                         41.5797,  -93.6631),
    ("Iowa City Zoo",                          41.6485,  -91.5419),
    ("Omaha Zoo 2",                            41.2122,  -95.9381),
    ("Springfield Missouri Zoo",              37.1787,  -93.3038),
    ("Shreveport Zoo",                         32.4735,  -93.7861),
    ("Lubbock Zoo",                            33.5561, -101.8944),
    ("Amarillo Zoo",                           35.2099, -101.8313),
    ("Corpus Christi Zoo",                     27.7220,  -97.4176),
    ("Brownsville Zoo",                        25.9017,  -97.4900),
    ("McAllen Zoo",                            26.2034,  -98.2300),
    ("Laredo Zoo",                             27.5503,  -99.5142),
    ("Midland Zoo",                            31.9804, -102.0779),
    ("Abilene Zoo",                            32.4357,  -99.7175),
    ("Tyler Caldwell Zoo",                     32.3513,  -95.3011),
    ("Waco Cameron Park Zoo",                  31.5554,  -97.1476),
    ("College Station Zoo",                    30.5866,  -96.2953),
    ("Albany NY Zoo",                          42.6907,  -73.8272),
    ("Syracuse Zoo",                           43.0567,  -76.1340),
    ("Rochester Seneca Park Zoo",             43.1900,  -77.6173),
    ("Buffalo Aquarium",                       42.8744,  -78.8728),
    ("Hartford Zoo",                           41.8116,  -72.6995),
    ("Bridgeport Beardsley Zoo",              41.1870,  -73.1993),
    ("New Haven Zoo",                          41.3557,  -72.9267),
    ("Worcester Zoo",                          42.2756,  -71.8157),
    ("Lowell Zoo",                             42.6334,  -71.3162),
    ("Tacoma Zoo 2",                           47.3190, -122.5304),
    ("Albuquerque Biopark Zoo",               35.0967, -106.6693),
    ("Colorado Springs Zoo",                   38.7763, -104.8476),
]

# ── major US theme parks ──────────────────────────────────────────────────────

MAJOR_THEME_PARKS = [
    # Florida
    ("Walt Disney World Magic Kingdom",        28.4177,  -81.5812),
    ("Walt Disney World EPCOT",                28.3747,  -81.5494),
    ("Walt Disney World Hollywood Studios",    28.3573,  -81.5584),
    ("Walt Disney World Animal Kingdom",       28.3553,  -81.5900),
    ("Universal Studios Florida",              28.4750,  -81.4668),
    ("Universal Islands of Adventure",         28.4720,  -81.4681),
    ("SeaWorld Orlando",                       28.4120,  -81.4617),
    ("Busch Gardens Tampa",                    28.0375,  -82.4208),
    ("LEGOLAND Florida",                       28.0090,  -81.6924),
    ("Kennedy Space Center",                   28.5235,  -80.6827),
    # California
    ("Disneyland",                             33.8121, -117.9190),
    ("Disney California Adventure",            33.8091, -117.9186),
    ("Universal Studios Hollywood",            34.1381, -118.3534),
    ("Knott's Berry Farm",                     33.8442, -117.9986),
    ("Six Flags Magic Mountain",               34.4248, -118.5979),
    ("SeaWorld San Diego",                     32.7648, -117.2267),
    ("LEGOLAND California",                    33.1261, -117.3122),
    ("California's Great America",             37.3978, -121.9742),
    ("Six Flags Discovery Kingdom",            38.1393, -122.2325),
    # New York/New Jersey
    ("Six Flags Great Adventure NJ",           40.1378,  -74.4412),
    ("Hersheypark PA",                         40.2877,  -76.6567),
    ("Dorney Park PA",                         40.5735,  -75.5927),
    ("Knoebels PA",                            40.8759,  -76.4979),
    ("Nickelodeon Universe NJ",                40.8871,  -74.0573),
    ("Rye Playland NY",                        40.9793,  -73.6818),
    # Texas
    ("Six Flags Over Texas",                   32.7574,  -97.0706),
    ("Six Flags Fiesta Texas",                 29.6022,  -98.6192),
    ("SeaWorld San Antonio",                   29.4563,  -98.7003),
    ("Schlitterbahn New Braunfels",            29.6988,  -98.1278),
    ("Moody Gardens Galveston",                29.2698,  -94.8560),
    ("NASA Space Center Houston",              29.5519,  -95.0977),
    ("LEGOLAND Discovery Dallas",              32.9272,  -96.9854),
    ("Universal Kids Resort Frisco",           33.1560,  -96.8244),
    # Illinois/Midwest
    ("Six Flags Great America IL",             42.3706,  -87.9351),
    ("Cedar Point Ohio",                       41.4812,  -82.6838),
    ("Kings Island Ohio",                      39.3444,  -84.2680),
    ("Worlds of Fun Kansas City",              39.1760,  -94.5193),
    ("Valleyfair Minnesota",                   44.7859,  -93.4735),
    ("Michigan's Adventure",                   43.3793,  -86.2698),
    ("Holiday World Indiana",                  38.1197,  -86.8013),
    ("Indiana Beach",                          40.5637,  -86.4981),
    # Southeast
    ("Six Flags Over Georgia",                 33.7714,  -84.5513),
    ("Dollywood Tennessee",                    35.7951,  -83.5307),
    ("Silver Dollar City Missouri",            36.6602,  -93.3392),
    ("Busch Gardens Williamsburg VA",          37.2354,  -76.6398),
    ("Kings Dominion VA",                      37.8362,  -77.4455),
    ("Carowinds NC",                           35.1024,  -80.9394),
    ("Wild Adventures Georgia",                30.8526,  -83.3247),
    ("Fun Spot America",                       28.4389,  -81.4652),
    # Mountain/West
    ("Elitch Gardens Denver",                  39.7509, -105.0090),
    ("Lagoon Utah",                            40.9887, -111.8863),
    ("Enchanted Forest Oregon",                44.7990, -122.5420),
    ("Oaks Amusement Park Portland",           45.4850, -122.6517),
    ("Wild Waves Washington",                  47.3184, -122.3170),
    ("Silverwood Theme Park Idaho",            47.8936, -116.7132),
    ("Castles N Coasters Phoenix",             33.5782, -112.0630),
    ("Golfland Sunsplash AZ",                  33.3785, -111.9079),
    ("Wet N Wild Las Vegas",                   36.1967, -115.2761),
    ("Gilroy Gardens CA",                      36.9895, -121.5728),
    ("Scandia Fun Center CA",                  34.0983, -117.5827),
    # Northeast
    ("Six Flags New England",                  42.0373,  -72.6131),
    ("Lake Compounce CT",                      41.6620,  -72.9590),
    ("Quassy Amusement Park CT",               41.5048,  -73.0630),
    ("Canobie Lake Park NH",                   42.8002,  -71.2123),
    ("Funtown Splashtown Maine",               43.4801,  -70.4526),
    ("Story Land NH",                          44.0565,  -71.1573),
    ("Seabreeze Amusement Park NY",            43.1843,  -77.5213),
    ("Darien Lake NY",                         42.8921,  -78.4940),
    ("Waldameer PA",                           42.1048,  -80.1317),
    ("Idlewild Park PA",                       40.2183,  -79.1042),
    # Louisiana/South
    ("Zephyr Field New Orleans",               29.9490,  -90.2060),
    ("Dixie Landin LA",                        30.3877,  -91.1399),
    # Hawaii
    ("Sea Life Park Hawaii",                   21.3103, -157.6602),
    ("Wet N Wild Hawaii",                      21.3955, -158.0046),
]

# ── distance helpers ──────────────────────────────────────────────────────────

def nearest_from_list(lat: float, lon: float, locations: list) -> tuple:
    best_dist = float("inf")
    best_name = None
    for name, plat, plon in locations:
        dist = geodesic((lat, lon), (plat, plon)).miles
        if dist < best_dist:
            best_dist = dist
            best_name = name
    return round(best_dist, 1), best_name

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  05b_fix_distances.py — Fix Zoo & Theme Park")
    print("=" * 55)

    cities = pd.read_csv(MASTER_FILE)
    print(f"Loaded {len(cities)} cities")
    print(f"Recalculating zoo and theme park distances from hardcoded lists...")
    print(f"  Zoos: {len(MAJOR_ZOOS)}")
    print(f"  Theme parks: {len(MAJOR_THEME_PARKS)}\n")

    zoo_dists, zoo_names     = [], []
    park_dists, park_names   = [], []

    for _, row in cities.iterrows():
        if pd.isna(row.get("lat")):
            zoo_dists.append(None);  zoo_names.append(None)
            park_dists.append(None); park_names.append(None)
            continue

        lat, lon = float(row["lat"]), float(row["lon"])

        d_zoo,  n_zoo  = nearest_from_list(lat, lon, MAJOR_ZOOS)
        d_park, n_park = nearest_from_list(lat, lon, MAJOR_THEME_PARKS)

        zoo_dists.append(d_zoo);   zoo_names.append(n_zoo)
        park_dists.append(d_park); park_names.append(n_park)

    cities["dist_zoo_miles"]        = zoo_dists
    cities["nearest_zoo"]           = zoo_names
    cities["dist_theme_park_miles"] = park_dists
    cities["nearest_theme_park"]    = park_names

    cities.to_csv(MASTER_FILE, index=False)

    print("Done!")
    print(f"Saved -> '{MASTER_FILE}'")
    print("\nSample (first 15 rows):")
    cols = ["city", "state", "dist_airport_miles",
            "dist_zoo_miles", "nearest_zoo",
            "dist_theme_park_miles", "nearest_theme_park"]
    print(cities[cols].head(15).to_string(index=False))
    print("\nNext step: run 06_nature.py")

if __name__ == "__main__":
    main()