"""
08_sports.py
------------
Counts major professional sports teams per city metro using the
exact Wikipedia team list scraped manually.

Covers: NFL, MLB, NBA, NHL, MLS (US teams only)

Input:  cities_master.csv
Output: cities_master.csv (updated in place)

Adds columns:
  nfl_teams, mlb_teams, nba_teams, nhl_teams, mls_teams
  total_pro_teams
  sports_score (0-100)

Requirements:
    pip install pandas
    No API calls needed.
"""

import sys
import pandas as pd

MASTER_FILE = "cities_master.csv"

# ── exact team data from Wikipedia ───────────────────────────────────────────
# Each entry: (city, state, league)
# City = the metro primary city we map everything to

TEAMS = [
    # NFL
    ("Anaheim",         "CA", "NHL"),   # Ducks — maps to LA metro
    ("Glendale",        "AZ", "NFL"),   # Cardinals
    ("Phoenix",         "AZ", "MLB"),   # Diamondbacks
    ("Atlanta",         "GA", "NFL"),   # Falcons
    ("Atlanta",         "GA", "MLB"),   # Braves (Cumberland = Atlanta metro)
    ("Atlanta",         "GA", "NBA"),   # Hawks
    ("Atlanta",         "GA", "MLS"),   # Atlanta United
    ("Austin",          "TX", "MLS"),   # Austin FC
    ("Baltimore",       "MD", "MLB"),   # Orioles
    ("Baltimore",       "MD", "NFL"),   # Ravens
    ("Boston",          "MA", "NHL"),   # Bruins
    ("Boston",          "MA", "NBA"),   # Celtics
    ("Boston",          "MA", "MLB"),   # Red Sox
    ("New York",        "NY", "NBA"),   # Nets (Brooklyn)
    ("Buffalo",         "NY", "NFL"),   # Bills
    ("Buffalo",         "NY", "NHL"),   # Sabres
    ("Raleigh",         "NC", "NHL"),   # Hurricanes
    ("Charlotte",       "NC", "NFL"),   # Panthers
    ("Charlotte",       "NC", "MLS"),   # Charlotte FC
    ("Charlotte",       "NC", "NBA"),   # Hornets
    ("Chicago",         "IL", "NFL"),   # Bears
    ("Chicago",         "IL", "NHL"),   # Blackhawks
    ("Chicago",         "IL", "NBA"),   # Bulls
    ("Chicago",         "IL", "MLB"),   # Cubs
    ("Chicago",         "IL", "MLS"),   # Fire
    ("Chicago",         "IL", "MLB"),   # White Sox
    ("Cincinnati",      "OH", "NFL"),   # Bengals
    ("Cincinnati",      "OH", "MLS"),   # FC Cincinnati
    ("Cincinnati",      "OH", "MLB"),   # Reds
    ("Cleveland",       "OH", "NFL"),   # Browns
    ("Cleveland",       "OH", "NBA"),   # Cavaliers
    ("Cleveland",       "OH", "MLB"),   # Guardians
    ("Denver",          "CO", "NHL"),   # Avalanche
    ("Denver",          "CO", "MLS"),   # Rapids
    ("Denver",          "CO", "MLB"),   # Rockies
    ("Columbus",        "OH", "NHL"),   # Blue Jackets
    ("Columbus",        "OH", "MLS"),   # Crew
    ("Dallas",          "TX", "NFL"),   # Cowboys (Arlington)
    ("Dallas",          "TX", "MLS"),   # FC Dallas (Frisco)
    ("Dallas",          "TX", "NBA"),   # Mavericks
    ("Dallas",          "TX", "NHL"),   # Stars
    ("Washington",      "DC", "MLS"),   # DC United
    ("Denver",          "CO", "NFL"),   # Broncos
    ("Denver",          "CO", "NBA"),   # Nuggets
    ("Detroit",         "MI", "NFL"),   # Lions
    ("Detroit",         "MI", "NBA"),   # Pistons
    ("Detroit",         "MI", "NHL"),   # Red Wings
    ("Detroit",         "MI", "MLB"),   # Tigers
    ("Miami",           "FL", "NHL"),   # Panthers (Sunrise = Miami metro)
    ("San Francisco",   "CA", "NBA"),   # Warriors
    ("Green Bay",       "WI", "NFL"),   # Packers
    ("Houston",         "TX", "MLB"),   # Astros
    ("Houston",         "TX", "MLS"),   # Dynamo
    ("Houston",         "TX", "NBA"),   # Rockets
    ("Houston",         "TX", "NFL"),   # Texans
    ("Indianapolis",    "IN", "NBA"),   # Pacers
    ("Indianapolis",    "IN", "NFL"),   # Colts
    ("Jacksonville",    "FL", "NFL"),   # Jaguars
    ("Kansas City",     "MO", "NFL"),   # Chiefs
    ("Kansas City",     "MO", "MLB"),   # Royals
    ("Kansas City",     "MO", "MLS"),   # Sporting KC
    ("Los Angeles",     "CA", "MLS"),   # Galaxy
    ("Las Vegas",       "NV", "NFL"),   # Raiders
    ("Los Angeles",     "CA", "MLB"),   # Angels (Anaheim)
    ("Los Angeles",     "CA", "NFL"),   # Chargers (Inglewood)
    ("Los Angeles",     "CA", "NBA"),   # Clippers
    ("Los Angeles",     "CA", "MLB"),   # Dodgers
    ("Los Angeles",     "CA", "MLS"),   # LAFC
    ("Los Angeles",     "CA", "NHL"),   # Kings
    ("Los Angeles",     "CA", "NBA"),   # Lakers
    ("Los Angeles",     "CA", "NFL"),   # Rams (Inglewood)
    ("Memphis",         "TN", "NBA"),   # Grizzlies
    ("Miami",           "FL", "NFL"),   # Dolphins
    ("Miami",           "FL", "NBA"),   # Heat
    ("Miami",           "FL", "MLS"),   # Inter Miami
    ("Miami",           "FL", "MLB"),   # Marlins
    ("Milwaukee",       "WI", "MLB"),   # Brewers
    ("Milwaukee",       "WI", "NBA"),   # Bucks
    ("Minneapolis",     "MN", "NBA"),   # Timberwolves
    ("Minneapolis",     "MN", "MLB"),   # Twins
    ("Minneapolis",     "MN", "MLS"),   # Minnesota United (St Paul)
    ("Minneapolis",     "MN", "NFL"),   # Vikings
    ("Minneapolis",     "MN", "NHL"),   # Wild (St Paul)
    ("Nashville",       "TN", "NHL"),   # Predators
    ("Nashville",       "TN", "MLS"),   # Nashville SC
    ("Boston",          "MA", "NFL"),   # Patriots (Foxborough)
    ("Boston",          "MA", "MLS"),   # Revolution
    ("Newark",          "NJ", "NHL"),   # Devils — NJ = NY metro
    ("New Orleans",     "LA", "NBA"),   # Pelicans
    ("New Orleans",     "LA", "NFL"),   # Saints
    ("New York",        "NY", "MLS"),   # NYCFC
    ("New York",        "NY", "NFL"),   # Giants (East Rutherford)
    ("New York",        "NY", "NHL"),   # Islanders (Elmont)
    ("New York",        "NY", "NFL"),   # Jets (East Rutherford)
    ("New York",        "NY", "NBA"),   # Knicks
    ("New York",        "NY", "MLB"),   # Mets
    ("New York",        "NY", "NHL"),   # Rangers
    ("New York",        "NY", "MLS"),   # Red Bulls (Harrison NJ)
    ("New York",        "NY", "MLB"),   # Yankees
    ("Oklahoma City",   "OK", "NBA"),   # Thunder
    ("Orlando",         "FL", "MLS"),   # Orlando City
    ("Orlando",         "FL", "NBA"),   # Magic
    ("Philadelphia",    "PA", "NBA"),   # 76ers
    ("Philadelphia",    "PA", "NFL"),   # Eagles
    ("Philadelphia",    "PA", "NHL"),   # Flyers
    ("Philadelphia",    "PA", "MLB"),   # Phillies
    ("Philadelphia",    "PA", "MLS"),   # Union (Chester)
    ("Phoenix",         "AZ", "NBA"),   # Suns
    ("Pittsburgh",      "PA", "NHL"),   # Penguins
    ("Pittsburgh",      "PA", "MLB"),   # Pirates
    ("Pittsburgh",      "PA", "NFL"),   # Steelers
    ("Portland",        "OR", "MLS"),   # Timbers
    ("Portland",        "OR", "NBA"),   # Trail Blazers
    ("Sacramento",      "CA", "NBA"),   # Kings
    ("St. Louis",       "MO", "NHL"),   # Blues
    ("St. Louis",       "MO", "MLB"),   # Cardinals
    ("St. Louis",       "MO", "MLS"),   # City SC
    ("Salt Lake City",  "UT", "MLS"),   # Real Salt Lake (Sandy)
    ("San Antonio",     "TX", "NBA"),   # Spurs
    ("San Diego",       "CA", "MLS"),   # San Diego FC
    ("San Diego",       "CA", "MLB"),   # Padres
    ("San Francisco",   "CA", "NFL"),   # 49ers (Santa Clara)
    ("San Francisco",   "CA", "MLB"),   # Giants
    ("San Francisco",   "CA", "MLS"),   # Earthquakes (San Jose)
    ("San Francisco",   "CA", "NHL"),   # Sharks (San Jose)
    ("Seattle",         "WA", "NHL"),   # Kraken
    ("Seattle",         "WA", "MLB"),   # Mariners
    ("Seattle",         "WA", "NFL"),   # Seahawks
    ("Seattle",         "WA", "MLS"),   # Sounders
    ("Tampa",           "FL", "NFL"),   # Buccaneers
    ("Tampa",           "FL", "NHL"),   # Lightning
    ("Tampa",           "FL", "MLB"),   # Rays (St Petersburg)
    ("Nashville",       "TN", "NFL"),   # Titans
    ("Dallas",          "TX", "MLB"),   # Rangers (Arlington)
    ("Salt Lake City",  "UT", "NBA"),   # Jazz
    ("Salt Lake City",  "UT", "NHL"),   # Utah Mammoth
    ("Las Vegas",       "NV", "NHL"),   # Golden Knights
    ("Washington",      "DC", "NHL"),   # Capitals
    ("Washington",      "DC", "NFL"),   # Commanders (Landover MD)
    ("Washington",      "DC", "MLB"),   # Nationals
    ("Washington",      "DC", "NBA"),   # Wizards
]

# ── metro map: city_lower → primary metro city ────────────────────────────────
METRO_MAP = {
    # New York
    "newark":"new york","jersey city":"new york","yonkers":"new york",
    "paterson":"new york","elizabeth":"new york","bridgeport":"new york",
    "stamford":"new york","new haven":"new york",
    # Los Angeles
    "long beach":"los angeles","anaheim":"los angeles","santa ana":"los angeles",
    "irvine":"los angeles","huntington beach":"los angeles","fontana":"los angeles",
    "moreno valley":"los angeles","riverside":"los angeles",
    "san bernardino":"los angeles","ontario":"los angeles",
    "rancho cucamonga":"los angeles","garden grove":"los angeles",
    "lancaster":"los angeles","palmdale":"los angeles","pomona":"los angeles",
    "torrance":"los angeles","orange":"los angeles","fullerton":"los angeles",
    "corona":"los angeles","west covina":"los angeles","el monte":"los angeles",
    "inglewood":"los angeles","downey":"los angeles","costa mesa":"los angeles",
    "santa clarita":"los angeles","simi valley":"los angeles",
    "thousand oaks":"los angeles","oxnard":"los angeles","ventura":"los angeles",
    "burbank":"los angeles","jurupa Valley":"los angeles","murrieta":"los angeles",
    "temecula":"los angeles","menifee":"los angeles","oceanside":"los angeles",
    "jurupa valley":"los angeles","glendale":"los angeles",
    # Chicago
    "aurora":"chicago","naperville":"chicago","joliet":"chicago","elgin":"chicago",
    # Dallas-Fort Worth
    "fort worth":"dallas","arlington":"dallas","plano":"dallas","garland":"dallas",
    "irving":"dallas","frisco":"dallas","mckinney":"dallas",
    "grand prairie":"dallas","mesquite":"dallas","denton":"dallas",
    "lewisville":"dallas","carrollton":"dallas","richardson":"dallas","allen":"dallas",
    # Houston
    "pasadena":"houston","league city":"houston","pearland":"houston",
    "sugar land":"houston","conroe":"houston","beaumont":"houston",
    # Washington DC
    "alexandria":"washington","chesapeake":"washington",
    # Miami
    "hialeah":"miami","miami gardens":"miami","fort lauderdale":"miami",
    "pembroke pines":"miami","hollywood":"miami","miramar":"miami",
    "coral springs":"miami","pompano beach":"miami","west palm beach":"miami",
    "boca raton":"miami","davie":"miami","plantation":"miami",
    "sunrise":"miami","deerfield beach":"miami",
    # Philadelphia
    "allentown":"philadelphia",
    # Atlanta
    "sandy springs":"atlanta","south fulton":"atlanta","macon":"atlanta",
    # Phoenix (glendale AZ already mapped above as glendale → LA, handle by state)
    "mesa":"phoenix","chandler":"phoenix","scottsdale":"phoenix",
    "gilbert":"phoenix","tempe":"phoenix","peoria":"phoenix",
    "surprise":"phoenix","goodyear":"phoenix","buckeye":"phoenix",
    # Boston
    "worcester":"boston","cambridge":"boston","lowell":"boston",
    "brockton":"boston","lynn":"boston","quincy":"boston",
    "new bedford":"boston","manchester":"boston","providence":"boston",
    # San Francisco Bay Area
    "san jose":"san francisco","oakland":"san francisco","fremont":"san francisco",
    "santa clara":"san francisco","sunnyvale":"san francisco",
    "hayward":"san francisco","concord":"san francisco","berkeley":"san francisco",
    "richmond":"san francisco","antioch":"san francisco","fairfield":"san francisco",
    "vallejo":"san francisco","daly city":"san francisco",
    "santa rosa":"san francisco","stockton":"san francisco",
    "modesto":"san francisco","tracy":"san francisco",
    "vacaville":"san francisco","san mateo":"san francisco",
    # Seattle
    "tacoma":"seattle","bellevue":"seattle","kent":"seattle","renton":"seattle",
    "everett":"seattle","federal way":"seattle","spokane valley":"seattle",
    # Denver
    "lakewood":"denver","thornton":"denver","arvada":"denver",
    "westminster":"denver","centennial":"denver","boulder":"denver",
    "greeley":"denver","fort collins":"denver","colorado springs":"denver",
    "pueblo":"denver",
    # Minneapolis
    "saint paul":"minneapolis","rochester":"minneapolis",
    # Detroit
    "warren":"detroit","sterling heights":"detroit","ann arbor":"detroit",
    "dearborn":"detroit","lansing":"detroit","clinton":"detroit",
    # Tampa
    "st. petersburg":"tampa","clearwater":"tampa","lakeland":"tampa",
    "palm bay":"tampa","port st. lucie":"tampa","deltona":"tampa",
    # Orlando (separate from Tampa for NBA/MLS)
    "cape coral":"orlando",
    # Nashville
    "murfreesboro":"nashville","clarksville":"nashville",
    # Kansas City
    "overland park":"kansas city","olathe":"kansas city",
    "independence":"kansas city","lee's summit":"kansas city",
    # New Orleans
    "baton rouge":"new orleans","shreveport":"new orleans","lafayette":"new orleans",
    # Salt Lake City
    "west valley city":"salt lake city","west jordan":"salt lake city",
    "provo":"salt lake city","st. george":"salt lake city",
    # Oklahoma City
    "norman":"oklahoma city","broken arrow":"oklahoma city","tulsa":"oklahoma city",
    # Milwaukee
    "madison":"milwaukee",
    # Sacramento
    "elk grove":"sacramento","roseville":"sacramento","fresno":"sacramento",
    "bakersfield":"sacramento",
    # San Antonio
    "new braunfels":"san antonio","laredo":"san antonio",
    # Raleigh
    "durham":"raleigh","cary":"raleigh","greensboro":"raleigh",
    "winston-salem":"raleigh","high point":"raleigh","fayetteville":"raleigh",
    "wilmington":"raleigh",
    # Virginia Beach / Norfolk area (no major teams)
    "norfolk":"virginia beach","newport news":"virginia beach",
    "hampton":"virginia beach","suffolk":"virginia beach",
    # Austin
    "round rock":"austin","georgetown":"austin","killeen":"austin",
    "waco":"austin","college station":"austin",
    # Cleveland
    "akron":"cleveland",
    # Las Vegas
    "henderson":"las vegas","north las vegas":"las vegas",
    # Indianapolis
    "carmel":"indianapolis","fishers":"indianapolis","south bend":"indianapolis",
    # Portland
    "salem":"portland","eugene":"portland","gresham":"portland",
    "hillsboro":"portland","vancouver":"portland","bend":"portland",
    # San Diego
    "chula vista":"san diego","escondido":"san diego","el cajon":"san diego",
    "carlsbad":"san diego",
    # Charlotte
    "concord":"charlotte",
    # Boise
    "meridian":"boise","nampa":"boise",
    # Misc
    "sioux falls":"sioux falls","fargo":"fargo","billings":"billings",
    "reno":"reno","sparks":"reno","des moines":"des moines",
    "cedar rapids":"des moines","davenport":"des moines",
    "anchorage":"anchorage","honolulu":"honolulu",
    "el paso":"el paso","albuquerque":"albuquerque","tucson":"albuquerque",
    "rio rancho":"albuquerque","las cruces":"albuquerque",
    "lubbock":"lubbock","amarillo":"amarillo","midland":"midland","odessa":"midland",
    "abilene":"abilene","wichita falls":"wichita falls","san angelo":"san angelo",
    "corpus christi":"corpus christi","mcallen":"mcallen",
    "brownsville":"mcallen","edinburg":"mcallen",
    "little rock":"little rock","fayetteville ar":"little rock",
    "birmingham":"birmingham","montgomery":"birmingham",
    "mobile":"birmingham","huntsville":"birmingham","tuscaloosa":"birmingham",
    "jackson":"jackson","omaha":"omaha","lincoln":"omaha",
    "toledo":"toledo","dayton":"dayton","akron":"cleveland",
    "spokane":"spokane","green bay":"green bay",
    "lexington":"louisville","evansville":"indianapolis",
    "augusta":"atlanta","columbus ga":"atlanta",
    "charleston":"charleston","north charleston":"charleston",
    "columbia":"columbia sc","savannah":"savannah",
    "knoxville":"knoxville","chattanooga":"chattanooga",
    "wichita":"wichita","sioux falls":"sioux falls",
    "springfield mo":"springfield","springfield il":"springfield il",
    "syracuse":"syracuse","albany":"albany",
    "rochester ny":"buffalo","hartford":"hartford",
    "richmond va":"richmond","norfolk":"norfolk",
}

def build_metro_counts(teams: list) -> dict:
    """
    Aggregates team counts per (city_lower, state) key.
    Returns dict: (city_lower, state) → {nfl, mlb, nba, nhl, mls}
    """
    counts = {}
    for city, state, league in teams:
        key = (city.lower(), state.upper())
        if key not in counts:
            counts[key] = {"nfl":0,"mlb":0,"nba":0,"nhl":0,"mls":0}
        league_key = league.lower()
        if league_key in counts[key]:
            counts[key][league_key] += 1
    return counts

def main():
    print("=" * 55)
    print("  08_sports.py — Professional Sports Teams")
    print("=" * 55)

    try:
        cities = pd.read_csv(MASTER_FILE)
        print(f"Loaded {len(cities)} cities")
    except FileNotFoundError:
        print(f"ERROR: '{MASTER_FILE}' not found.")
        sys.exit(1)

    metro_counts = build_metro_counts(TEAMS)

    nfl_list, mlb_list, nba_list, nhl_list, mls_list, total_list = [], [], [], [], [], []
    unmatched = []

    for _, row in cities.iterrows():
        city  = str(row["city"]).strip()
        state = str(row["state"]).strip().upper()
        city_lower = city.lower()

        # Try direct match first
        key = (city_lower, state)
        counts = metro_counts.get(key)

        # Try metro map
        if not counts:
            metro = METRO_MAP.get(city_lower)
            if metro:
                # Try metro city with same state, then any state
                counts = metro_counts.get((metro, state))
                if not counts:
                    # Search all states for this metro
                    for (mc, ms), c in metro_counts.items():
                        if mc == metro:
                            counts = c
                            break

        if counts:
            nfl_list.append(counts["nfl"])
            mlb_list.append(counts["mlb"])
            nba_list.append(counts["nba"])
            nhl_list.append(counts["nhl"])
            mls_list.append(counts["mls"])
            total = sum(counts.values())
            total_list.append(total)
        else:
            nfl_list.append(0); mlb_list.append(0); nba_list.append(0)
            nhl_list.append(0); mls_list.append(0); total_list.append(0)
            unmatched.append(f"{city}, {state}")

    cities["nfl_teams"]       = nfl_list
    cities["mlb_teams"]       = mlb_list
    cities["nba_teams"]       = nba_list
    cities["nhl_teams"]       = nhl_list
    cities["mls_teams"]       = mls_list
    cities["total_pro_teams"] = total_list

    # New York has the most: 2 NFL + 2 MLB + 2 NBA + 3 NHL + 2 MLS = 11
    max_teams = max(total_list) if total_list else 11
    cities["sports_score"] = (cities["total_pro_teams"] / max_teams * 100).round(1)

    cities.to_csv(MASTER_FILE, index=False)

    print(f"\nUnmatched ({len(unmatched)}) — assigned 0 teams:")
    for c in unmatched[:20]:
        print(f"  {c}")

    print(f"\nSaved -> '{MASTER_FILE}'")
    print("\nTop 20 cities by total pro teams:")
    cols = ["city", "state", "nfl_teams", "mlb_teams", "nba_teams",
            "nhl_teams", "mls_teams", "total_pro_teams", "sports_score"]
    print(cities[cols].sort_values("total_pro_teams", ascending=False)
          .head(20).to_string(index=False))
    print("\nNext step: run 09_normalize.py")

if __name__ == "__main__":
    main()