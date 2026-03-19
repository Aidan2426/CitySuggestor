"""
06_nature.py
------------
Computes a nature and outdoor accessibility score for each city.

Factors:
  1. Distance to nearest National Park
  2. Distance to nearest National Forest
  3. Distance to nearest State Park (major ones)
  4. Coastline proximity (ocean or Great Lakes)
  5. Elevation
  6. Total parks within 100 miles

Elevation is fetched in bulk batches (100 cities per API call) for speed.
Everything else is pure math from hardcoded lists — runs in ~30 seconds.

Input:  cities_master.csv
Output: cities_master.csv (updated in place)

Requirements:
    pip install pandas geopy requests
"""

import sys
import time
import requests
import pandas as pd
from geopy.distance import geodesic

MASTER_FILE = "cities_master.csv"

# ── national parks ────────────────────────────────────────────────────────────
NATIONAL_PARKS = [
    ("Acadia NP",                          44.3386,  -68.2733),
    ("Arches NP",                          38.7331, -109.5925),
    ("Badlands NP",                        43.8554, -102.3397),
    ("Big Bend NP",                        29.1275, -103.2425),
    ("Biscayne NP",                        25.4824,  -80.4300),
    ("Bryce Canyon NP",                    37.5930, -112.1871),
    ("Canyonlands NP",                     38.2000, -109.9300),
    ("Capitol Reef NP",                    38.0900, -111.1700),
    ("Carlsbad Caverns NP",                32.1479, -104.5567),
    ("Channel Islands NP",                 34.0069, -119.7785),
    ("Congaree NP",                        33.7948,  -80.7820),
    ("Crater Lake NP",                     42.9446, -122.1090),
    ("Cuyahoga Valley NP",                 41.2808,  -81.5678),
    ("Death Valley NP",                    36.5054, -117.0794),
    ("Denali NP",                          63.3333, -150.5000),
    ("Everglades NP",                      25.2866,  -80.8987),
    ("Glacier NP",                         48.6960, -113.7180),
    ("Grand Canyon NP",                    36.0544, -112.1401),
    ("Grand Teton NP",                     43.7904, -110.6818),
    ("Great Basin NP",                     38.9833, -114.3000),
    ("Great Sand Dunes NP",                37.7279, -105.5116),
    ("Great Smoky Mountains NP",           35.6118,  -83.4895),
    ("Guadalupe Mountains NP",             31.9230, -104.8720),
    ("Hawaii Volcanoes NP",                19.4194, -155.2885),
    ("Hot Springs NP",                     34.5217,  -93.0424),
    ("Indiana Dunes NP",                   41.6531,  -87.0527),
    ("Isle Royale NP",                     48.0000,  -88.8333),
    ("Joshua Tree NP",                     33.8734, -115.9010),
    ("Kings Canyon NP",                    36.8879, -118.5551),
    ("Lassen Volcanic NP",                 40.4977, -121.4208),
    ("Mammoth Cave NP",                    37.1862,  -86.1003),
    ("Mesa Verde NP",                      37.1836, -108.4897),
    ("Mount Rainier NP",                   46.8800, -121.7269),
    ("North Cascades NP",                  48.7718, -121.2985),
    ("Olympic NP",                         47.8021, -123.6044),
    ("Petrified Forest NP",                34.9828, -109.7785),
    ("Pinnacles NP",                       36.4906, -121.1825),
    ("Redwood NP",                         41.3000, -124.0000),
    ("Rocky Mountain NP",                  40.3428, -105.6836),
    ("Saguaro NP",                         32.2967, -110.9890),
    ("Sequoia NP",                         36.4864, -118.5658),
    ("Shenandoah NP",                      38.4755,  -78.4535),
    ("Theodore Roosevelt NP",              46.9790, -103.5387),
    ("White Sands NP",                     32.7872, -106.3256),
    ("Wind Cave NP",                       43.5578, -103.4784),
    ("Yellowstone NP",                     44.4280, -110.5885),
    ("Yosemite NP",                        37.8651, -119.5383),
    ("Zion NP",                            37.2982, -113.0263),
    ("Sleeping Bear Dunes NL",             44.8759,  -86.0569),
    ("Blue Ridge Parkway",                 36.0000,  -80.0000),
    ("Cape Cod NS",                        41.8359,  -70.0388),
    ("Point Reyes NS",                     38.0500, -122.8800),
    ("Padre Island NS",                    27.0300,  -97.3700),
    ("Assateague Island NS",               38.0715,  -75.2040),
    ("Voyageurs NP",                       48.4839,  -92.8277),
    ("Black Canyon Gunnison NP",           38.5754, -107.7416),
    ("Gateway Arch NP",                    38.6247,  -90.1848),
    ("Glacier Bay NP",                     58.6658, -136.9000),
    ("Great Basin NP 2",                   38.9833, -114.3000),
    ("Haleakala NP",                       20.7097, -156.1567),
    ("Kenai Fjords NP",                    59.9195, -149.6484),
    ("Theodore Roosevelt NP 2",            46.9790, -103.5387),
    ("Wrangell St Elias NP",               61.7000, -142.9833),
    ("Fire Island NS",                     40.6329,  -73.1649),
]

# ── national forests (condensed) ──────────────────────────────────────────────
NATIONAL_FORESTS = [
    ("Tongass NF AK",           57.0,  -134.0), ("Chugach NF AK",          61.0,  -148.0),
    ("Mt Baker NF WA",          48.0,  -121.5), ("Gifford Pinchot NF WA",  46.0,  -121.8),
    ("Olympic NF WA",           47.5,  -123.5), ("Okanogan NF WA",         47.5,  -120.5),
    ("Willamette NF OR",        44.0,  -122.0), ("Mt Hood NF OR",          45.3,  -121.8),
    ("Deschutes NF OR",         43.8,  -121.5), ("Rogue River NF OR",      42.5,  -122.5),
    ("Shasta Trinity NF CA",    40.8,  -122.5), ("Tahoe NF CA",            39.3,  -120.5),
    ("Eldorado NF CA",          38.8,  -120.2), ("Sierra NF CA",           37.2,  -119.3),
    ("Angeles NF CA",           34.3,  -118.0), ("San Bernardino NF CA",   34.2,  -116.8),
    ("Los Padres NF CA",        35.5,  -120.5), ("Cleveland NF CA",        33.3,  -116.7),
    ("Inyo NF CA",              37.6,  -118.5), ("Plumas NF CA",           39.8,  -120.8),
    ("Boise NF ID",             44.0,  -115.5), ("Sawtooth NF ID",         43.5,  -114.5),
    ("Nez Perce NF ID",         46.0,  -115.5), ("Idaho Panhandle NF",     47.5,  -116.0),
    ("Gallatin NF MT",          45.5,  -110.5), ("Flathead NF MT",         48.0,  -114.0),
    ("Lolo NF MT",              47.0,  -114.5), ("Bitterroot NF MT",       46.0,  -114.0),
    ("Humboldt Toiyabe NF NV",  39.5,  -117.0), ("Wasatch Cache NF UT",    40.7,  -111.3),
    ("Uinta NF UT",             40.5,  -110.5), ("Dixie NF UT",            37.5,  -112.0),
    ("White River NF CO",       39.5,  -106.8), ("Arapaho Roosevelt NF CO",40.5,  -105.8),
    ("Pike San Isabel NF CO",   38.5,  -105.5), ("Rio Grande NF CO",       37.5,  -106.5),
    ("San Juan NF CO",          37.5,  -108.0), ("Gunnison NF CO",         38.5,  -107.0),
    ("Grand Mesa NF CO",        39.0,  -108.0), ("Kaibab NF AZ",           36.5,  -112.3),
    ("Coconino NF AZ",          35.0,  -111.5), ("Tonto NF AZ",            33.8,  -111.0),
    ("Apache Sitgreaves NF AZ", 34.0,  -109.5), ("Coronado NF AZ",         31.8,  -110.5),
    ("Prescott NF AZ",          34.5,  -112.5), ("Santa Fe NF NM",         35.8,  -106.0),
    ("Carson NF NM",            36.5,  -105.5), ("Cibola NF NM",           35.0,  -107.0),
    ("Gila NF NM",              33.2,  -108.3), ("Lincoln NF NM",          33.0,  -105.5),
    ("Black Hills NF SD",       44.0,  -103.8), ("Bighorn NF WY",          44.5,  -107.2),
    ("Bridger Teton NF WY",     43.2,  -110.2), ("Shoshone NF WY",         43.8,  -109.5),
    ("Nebraska NF",             42.0,  -101.0), ("Superior NF MN",         47.8,   -91.5),
    ("Chippewa NF MN",          47.2,   -94.0), ("Ottawa NF MI",           46.5,   -89.0),
    ("Hiawatha NF MI",          46.2,   -86.5), ("Huron Manistee NF MI",   44.0,   -85.5),
    ("Nicolet NF WI",           45.8,   -90.0), ("Mark Twain NF MO",       37.2,   -91.5),
    ("Shawnee NF IL",           37.5,   -88.8), ("Hoosier NF IN",          38.3,   -86.4),
    ("Wayne NF OH",             39.3,   -81.5), ("Allegheny NF PA",        41.6,   -79.0),
    ("Monongahela NF WV",       38.5,   -80.0), ("George Washington NF VA",38.5,   -79.3),
    ("Jefferson NF VA",         37.2,   -80.5), ("Pisgah NF NC",           35.5,   -82.8),
    ("Nantahala NF NC",         35.2,   -83.5), ("Cherokee NF TN",         36.2,   -82.2),
    ("Daniel Boone NF KY",      37.5,   -83.8), ("Chattahoochee NF GA",    34.8,   -83.8),
    ("Francis Marion NF SC",    33.2,   -79.7), ("Sumter NF SC",           34.5,   -82.0),
    ("Apalachicola NF FL",      30.2,   -84.8), ("Ocala NF FL",            29.3,   -81.8),
    ("Talladega NF AL",         33.3,   -86.0), ("Ouachita NF AR",         34.5,   -94.0),
    ("Ozark NF AR",             35.8,   -93.0), ("Sam Houston NF TX",      30.7,   -95.5),
    ("Angelina NF TX",          31.2,   -94.2),
]

# ── major state parks (representative sample) ─────────────────────────────────
STATE_PARKS = [
    # Northeast
    ("Adirondack State Park NY",           44.0,   -74.0),
    ("Catskill State Park NY",             42.0,   -74.3),
    ("Delaware Water Gap NRA",             41.0,   -75.0),
    ("Harriman State Park NY",             41.2,   -74.1),
    ("Cape Henlopen SP DE",                38.8,   -75.1),
    ("Baxter State Park ME",               46.1,   -68.9),
    ("White Mountain NF NH",               44.1,   -71.5),
    ("Green Mountain NF VT",               43.8,   -73.0),
    ("Mohawk Trail SP MA",                 42.6,   -72.9),
    ("Letchworth SP NY",                   42.6,   -78.0),
    ("Watkins Glen SP NY",                 42.4,   -76.9),
    # Mid-Atlantic / Pennsylvania
    ("Shenandoah SP VA",                   38.9,   -78.2),
    ("Assateague SP MD",                   38.1,   -75.2),
    ("Patuxent River SP MD",               39.1,   -76.8),
    ("Pocono Mountains PA",                41.2,   -75.3),
    ("Delaware State Forest PA",           41.1,   -75.2),
    ("Ohiopyle SP PA",                     39.9,   -79.5),
    ("Laurel Hill SP PA",                  40.1,   -79.3),
    ("Ricketts Glen SP PA",                41.3,   -76.3),
    ("McConnells Mill SP PA",              40.9,   -80.2),
    ("Presque Isle SP PA",                 42.2,   -80.1),
    ("Hickory Run SP PA",                  41.0,   -75.6),
    ("Black Moshannon SP PA",              40.9,   -78.1),
    ("Worlds End SP PA",                   41.5,   -76.6),
    # Southeast
    ("Cheraw SP SC",                       34.7,   -79.9),
    ("Stone Mountain SP GA",               33.8,   -84.2),
    ("Cloudland Canyon SP GA",             34.8,   -85.5),
    ("Fall Creek Falls SP TN",             35.7,   -85.4),
    ("Mammoth Cave Area KY",               37.2,   -86.1),
    ("Cumberland Falls SP KY",             36.8,   -84.3),
    ("DeSoto SP AL",                       34.5,   -85.6),
    ("Gulf State Park AL",                 30.2,   -87.6),
    ("Palo Duro Canyon SP TX",             34.9,  -101.7),
    ("Garner SP TX",                       29.6,   -99.7),
    ("Lost Maples SP TX",                  29.8,   -99.6),
    # Florida
    ("Myakka River SP FL",                 27.2,   -82.3),
    ("Fakahatchee Strand SP FL",           25.9,   -81.4),
    ("Jonathan Dickinson SP FL",           27.0,   -80.1),
    ("Ichetucknee Springs SP FL",          29.9,   -82.8),
    # Midwest
    ("Starved Rock SP IL",                 41.3,   -89.0),
    ("Indiana Dunes SP IN",                41.6,   -87.1),
    ("Sleeping Bear Dunes MI",             44.9,   -86.1),
    ("Pictured Rocks MI",                  46.6,   -86.5),
    ("Porcupine Mountains MI",             46.8,   -89.7),
    ("Itasca SP MN",                       47.2,   -95.2),
    ("Lake of the Falls WI",               45.9,   -90.1),
    ("Devil's Lake SP WI",                 43.4,   -89.7),
    ("Effigy Mounds IA",                   43.1,   -91.2),
    ("Chadron SP NE",                      42.8,  -103.0),
    ("Custer SP SD",                       43.7,  -103.4),
    ("Theodore Roosevelt SP ND",           47.0,  -103.5),
    # Mountain West
    ("Flaming Gorge UT",                   41.0,  -109.5),
    ("Antelope Island SP UT",              41.1,  -112.2),
    ("Garden of the Gods CO",              38.9,  -104.9),
    ("Mueller SP CO",                      38.9,  -105.2),
    ("Lory SP CO",                         40.6,  -105.2),
    ("Red Rocks Park CO",                  39.7,  -105.2),
    ("Palisade SP CO",                     39.1,  -108.4),
    ("Ute Mountain SP CO",                 37.2,  -108.8),
    ("Valley of Fire SP NV",               36.5,  -114.5),
    ("Lake Tahoe NV SP",                   39.1,  -119.9),
    ("Coeur d'Alene Lake ID",              47.7,  -116.8),
    ("Hells Canyon NRA ID",                45.5,  -116.5),
    ("Flathead Lake SP MT",                47.9,  -114.1),
    ("Beartooth Scenic Highway MT",        45.0,  -109.5),
    ("Antelope Island SP UT 2",            41.1,  -112.2),
    # Pacific
    ("Olympic SP WA",                      47.5,  -123.5),
    ("Deception Pass SP WA",               48.4,  -122.6),
    ("Mt Spokane SP WA",                   47.9,  -117.1),
    ("Columbia River Gorge OR",            45.7,  -122.0),
    ("Crater Lake OR area",                42.9,  -122.1),
    ("Samuel H Boardman SP OR",            42.1,  -124.3),
    ("Salt Point SP CA",                   38.6,  -123.3),
    ("Big Sur CA",                         36.3,  -121.8),
    ("Anza Borrego SP CA",                 33.1,  -116.4),
    ("Mount San Jacinto SP CA",            33.8,  -116.7),
    ("Torrey Pines SP CA",                 32.9,  -117.3),
    ("Point Lobos SP CA",                  36.5,  -121.9),
    ("Jedediah Smith SP CA",               41.8,  -124.1),
    # Hawaii/Alaska
    ("Na Pali Coast SP HI",                22.2,  -159.6),
    ("Waimea Canyon SP HI",                22.1,  -159.7),
    ("Chugach SP AK",                      61.1,  -149.5),
    ("Denali SP AK",                       62.5,  -151.0),
]

# ── coastlines ────────────────────────────────────────────────────────────────
COASTLINES = {
    "ocean": [
        (47.3,-67.9),(44.5,-68.5),(42.3,-71.0),(41.3,-72.0),(40.7,-74.0),
        (39.9,-74.1),(38.9,-74.9),(38.3,-75.1),(37.0,-76.0),(35.5,-75.5),
        (34.2,-77.8),(32.8,-79.9),(31.1,-81.4),(30.4,-81.4),(29.5,-81.3),
        (28.0,-80.6),(26.7,-80.0),(25.8,-80.1),(25.2,-80.4),(25.7,-81.4),
        (27.8,-82.7),(29.1,-83.1),(29.7,-85.1),(30.2,-87.6),(30.4,-88.9),
        (29.9,-90.1),(29.3,-92.0),(29.8,-93.9),(27.8,-97.4),(26.1,-97.2),
        (48.5,-124.7),(47.0,-124.2),(46.2,-124.1),(45.5,-124.0),(44.6,-124.1),
        (43.4,-124.3),(42.0,-124.2),(40.4,-124.4),(38.3,-123.1),(37.8,-122.5),
        (36.6,-121.9),(35.4,-120.9),(34.4,-120.5),(34.0,-118.5),(33.7,-118.3),
        (33.2,-117.4),(32.7,-117.2),(21.3,-157.8),(19.7,-155.1),
        # Puget Sound / inland sea (WA)
        (47.6,-122.3),(47.5,-122.4),(47.4,-122.4),(47.3,-122.4),(47.2,-122.5),
        (47.8,-122.5),(48.1,-122.8),(48.4,-122.6),(47.9,-122.7),(47.1,-122.6),
        # San Francisco Bay
        (37.8,-122.4),(37.7,-122.4),(37.6,-122.4),(37.5,-122.2),(37.9,-122.5),
        # Chesapeake Bay
        (39.3,-76.5),(38.9,-76.5),(38.5,-76.4),(37.9,-76.3),(37.2,-76.2),
        (38.3,-76.5),(39.0,-76.4),(36.9,-76.3),
        # Tampa Bay / Charlotte Harbor
        (27.9,-82.5),(27.7,-82.6),(27.5,-82.7),(26.9,-82.1),
    ],
    "great_lakes": [
        (42.0,-87.6),(42.5,-87.8),(43.0,-87.9),(43.9,-87.5),(44.5,-86.4),
        (45.5,-85.0),(44.6,-85.6),(43.2,-86.3),(42.7,-86.4),(41.7,-87.5),
        (46.7,-84.5),(47.5,-87.0),(48.0,-89.5),(47.0,-91.5),(46.8,-92.1),
        (44.0,-83.3),(45.0,-83.5),(43.5,-82.5),(43.0,-82.4),
        (42.9,-78.9),(42.8,-79.3),(42.6,-80.0),(41.7,-81.2),(41.5,-82.7),
        (43.4,-79.0),(43.5,-76.5),(43.2,-77.6),(43.3,-78.7),
    ],
}

# ── bulk elevation fetch ──────────────────────────────────────────────────────

def fetch_elevations_bulk(coords: list) -> list:
    """
    Fetches elevation for up to 100 lat/lon pairs in one API call.
    coords: list of (lat, lon) tuples
    Returns list of elevations in feet (same order as input).
    """
    lats = [str(round(c[0], 4)) for c in coords]
    lons = [str(round(c[1], 4)) for c in coords]

    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/elevation",
            params={"latitude": ",".join(lats), "longitude": ",".join(lons)},
            timeout=20
        )
        resp.raise_for_status()
        data = resp.json()
        elevs_m = data.get("elevation", [])
        return [round(e * 3.28084, 0) for e in elevs_m]
    except Exception as e:
        print(f"  [ERROR] Elevation batch failed: {e}")
        return [None] * len(coords)

# ── distance helpers ──────────────────────────────────────────────────────────

def nearest_from_list(lat, lon, locations):
    best_dist = float("inf")
    best_name = None
    for name, plat, plon in locations:
        dist = geodesic((lat, lon), (plat, plon)).miles
        if dist < best_dist:
            best_dist = dist
            best_name = name
    return round(best_dist, 1), best_name

def count_within_radius(lat, lon, locations, radius_miles):
    return sum(
        1 for _, plat, plon in locations
        if geodesic((lat, lon), (plat, plon)).miles <= radius_miles
    )

COASTAL_THRESHOLD = 50.0  # miles — beyond this, city is not considered coastal

def nearest_coast(lat, lon):
    best_dist = float("inf")
    best_type = "none"
    for coast_type, points in COASTLINES.items():
        for clat, clon in points:
            dist = geodesic((lat, lon), (clat, clon)).miles
            if dist < best_dist:
                best_dist = dist
                best_type = coast_type
    coast_type_result = best_type if best_dist <= COASTAL_THRESHOLD else "none"
    return round(best_dist, 1), coast_type_result


def classify_environment(lat, lon, elev_ft, dist_coast, coast_type, state):
    """Classify a city's natural environment into a descriptive category."""
    elev = elev_ft or 0
    dist_c = dist_coast if dist_coast is not None else 999

    # Coastal ocean
    if coast_type == "ocean":
        return "coastal"

    # Great Lakes shoreline
    if coast_type == "great_lakes":
        return "great_lakes"

    # Desert Southwest
    if state in ("AZ", "NM"):
        return "desert"
    if state == "NV" and not (lat and lat > 39.5 and elev > 4000):
        return "desert"
    if state == "CA" and lat and lat < 35.5 and lon and lon > -117.5:
        return "desert"
    if state == "TX" and lon and lon < -103:
        return "desert"
    if state == "UT" and lat and lat < 38.5 and elev < 4500:
        return "desert"

    # High mountains (Rockies, Cascades, Sierra)
    mountain_west = ("CO", "WY", "MT", "ID")
    if state in mountain_west and elev > 4500:
        return "mountains"
    if state == "UT" and elev > 4000:
        return "mountains"
    if state in ("WA", "OR") and elev > 900 and dist_c > 40:
        return "mountains"
    if state == "CA" and elev > 1500 and lon and lon > -121:
        return "mountains"
    if state == "NV" and lat and lat > 39.5 and elev > 4000:
        return "mountains"

    # Rocky Mountain foothills
    if state in mountain_west and 2000 < elev <= 4500:
        return "foothills"
    if state == "CO" and elev > 1500:
        return "foothills"
    if state in ("NM", "AZ") and elev > 5000:
        return "foothills"

    # Appalachian hills / Ozarks
    appalachian = ("WV", "KY", "TN", "VA", "PA", "MD", "NC", "AL")
    if state in appalachian and elev > 500:
        return "hills"
    if state == "NY" and lon and lon < -74.5 and elev > 500:
        return "hills"
    if state in ("AR", "MO") and elev > 500:
        return "hills"
    if state == "GA" and elev > 800:
        return "hills"
    if state in ("OH", "IN") and elev > 900:
        return "hills"

    # Pacific NW / California valleys
    if state in ("WA", "OR") and elev < 500:
        return "valley"
    if state == "CA" and lat and lat > 35.5 and elev < 500:
        return "valley"

    # Great Plains / Midwest
    plains = ("KS", "NE", "ND", "SD", "OK", "IA", "IL", "IN", "MI", "WI", "MN")
    if state in plains:
        return "plains"
    if state == "TX":
        return "plains"
    if state in ("OH", "MO", "MI") and elev < 900:
        return "plains"

    # Southeast lowlands
    southeast = ("FL", "LA", "MS", "SC", "GA", "AL")
    if state in southeast and elev < 300:
        return "lowlands"

    return "plains"

# ── scoring ───────────────────────────────────────────────────────────────────

def compute_nature_score(dist_np, dist_nf, dist_sp, dist_coast, elev_ft, parks_100,
                         lat=None, lon=None):
    score = 0.0

    # National park proximity (0-25 pts)
    if dist_np is not None:
        if dist_np < 10:    score += 25
        elif dist_np < 50:  score += 18
        elif dist_np < 100: score += 10
        elif dist_np < 200: score += 4

    # Bonus for multiple national parks within 150 miles (0-10 pts)
    if lat is not None and lon is not None:
        nps_nearby = count_within_radius(lat, lon, NATIONAL_PARKS, 150)
        if nps_nearby >= 4:   score += 10
        elif nps_nearby == 3: score += 7
        elif nps_nearby == 2: score += 4

    # National forest proximity (0-20 pts)
    if dist_nf is not None:
        if dist_nf < 15:    score += 20
        elif dist_nf < 50:  score += 13
        elif dist_nf < 100: score += 7
        elif dist_nf < 200: score += 2

    # State park proximity (0-15 pts)
    if dist_sp is not None:
        if dist_sp < 10:    score += 15
        elif dist_sp < 30:  score += 10
        elif dist_sp < 75:  score += 5
        elif dist_sp < 150: score += 2

    # Coastline proximity (0-20 pts)
    if dist_coast is not None:
        if dist_coast < 5:    score += 20
        elif dist_coast < 20: score += 15
        elif dist_coast < 50: score += 9
        elif dist_coast < 100: score += 4

    # Elevation bonus (0-10 pts) — only meaningful if near mountains/forests,
    # so halve the bonus if the city is far from both national parks and forests
    if elev_ft is not None:
        if elev_ft > 5000:   elev_pts = 10
        elif elev_ft > 3000: elev_pts = 7
        elif elev_ft > 1500: elev_pts = 4
        elif elev_ft > 500:  elev_pts = 1
        else:                elev_pts = 0
        near_terrain = (
            (dist_np is not None and dist_np < 200) or
            (dist_nf is not None and dist_nf < 100)
        )
        score += elev_pts if near_terrain else elev_pts // 2

    # Parks density within 100 miles (0-10 pts)
    if parks_100 is not None:
        score += min(parks_100 * 1.5, 10)

    return round(min(score, 100), 1)

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  06_nature.py — Nature & Outdoor Accessibility")
    print("=" * 55)

    try:
        cities = pd.read_csv(MASTER_FILE)
        print(f"Loaded {len(cities)} cities")
    except FileNotFoundError:
        print(f"ERROR: '{MASTER_FILE}' not found.")
        sys.exit(1)

    new_cols = ["dist_natl_park_miles", "nearest_natl_park",
                "dist_natl_forest_miles", "nearest_natl_forest",
                "dist_state_park_miles", "nearest_state_park",
                "coastline_type", "dist_coast_miles",
                "elevation_ft", "parks_within_100mi", "nature_score",
                "environment_type"]
    for col in new_cols:
        if col not in cities.columns:
            cities[col] = None

    # Clear ALL scores so every city is recalculated with updated thresholds/rules
    cities["nature_score"] = None
    cities["environment_type"] = None

    needs_fetch = cities[cities["lat"].notna()].index.tolist()

    total = len(needs_fetch)
    all_parks = NATIONAL_PARKS + NATIONAL_FORESTS + STATE_PARKS

    print(f"\nProcessing {total} cities...")
    print(f"  National parks:   {len(NATIONAL_PARKS)}")
    print(f"  National forests: {len(NATIONAL_FORESTS)}")
    print(f"  State parks:      {len(STATE_PARKS)}")
    print(f"  Fetching elevations in batches of 100...\n")

    # ── fetch all elevations in bulk batches ──────────────────────────────────
    coords = [
        (float(cities.loc[idx, "lat"]), float(cities.loc[idx, "lon"]))
        for idx in needs_fetch
    ]

    elevations = []
    batch_size = 100
    for i in range(0, len(coords), batch_size):
        batch = coords[i:i+batch_size]
        print(f"  Fetching elevation batch {i//batch_size + 1}/{(len(coords)-1)//batch_size + 1}...")
        elevs = fetch_elevations_bulk(batch)
        elevations.extend(elevs)
        time.sleep(0.5)

    print(f"  Elevations fetched for {len(elevations)} cities\n")
    print("  Calculating distances (pure math, fast)...")

    # ── calculate all distances ───────────────────────────────────────────────
    for i, idx in enumerate(needs_fetch):
        row  = cities.loc[idx]
        lat  = float(row["lat"])
        lon  = float(row["lon"])
        elev = elevations[i] if i < len(elevations) else None

        dist_np, name_np = nearest_from_list(lat, lon, NATIONAL_PARKS)
        dist_nf, name_nf = nearest_from_list(lat, lon, NATIONAL_FORESTS)
        dist_sp, name_sp = nearest_from_list(lat, lon, STATE_PARKS)
        dist_coast, c_type = nearest_coast(lat, lon)
        parks_100 = count_within_radius(lat, lon, all_parks, 100)

        score = compute_nature_score(
            dist_np, dist_nf, dist_sp, dist_coast, elev, parks_100,
            lat=lat, lon=lon
        )

        env_type = classify_environment(
            lat, lon, elev, dist_coast, c_type, str(row.get("state", ""))
        )

        cities.at[idx, "dist_natl_park_miles"]   = dist_np
        cities.at[idx, "nearest_natl_park"]       = name_np
        cities.at[idx, "dist_natl_forest_miles"]  = dist_nf
        cities.at[idx, "nearest_natl_forest"]     = name_nf
        cities.at[idx, "dist_state_park_miles"]   = dist_sp
        cities.at[idx, "nearest_state_park"]      = name_sp
        cities.at[idx, "coastline_type"]          = c_type
        cities.at[idx, "dist_coast_miles"]        = dist_coast
        cities.at[idx, "elevation_ft"]            = elev
        cities.at[idx, "parks_within_100mi"]      = parks_100
        cities.at[idx, "nature_score"]            = score
        cities.at[idx, "environment_type"]        = env_type

    cities.to_csv(MASTER_FILE, index=False)

    print(f"\nDone!")
    print(f"Saved -> '{MASTER_FILE}'")
    print("\nTop 15 cities by nature score:")
    cols = ["city", "state", "nature_score", "nearest_natl_park",
            "dist_natl_park_miles", "coastline_type", "elevation_ft"]
    print(cities[cols].sort_values("nature_score", ascending=False)
          .head(15).to_string(index=False))
    print("\nNext step: run 07_seasons.py")

if __name__ == "__main__":
    main()