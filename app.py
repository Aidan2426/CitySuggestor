"""
app.py
------
City Suggestor — Streamlit app

Run with:
    pip install streamlit pandas plotly folium streamlit-folium
    streamlit run app.py
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# ── pro sports team lookup ────────────────────────────────────────────────────
# Keyed by metro name; cities map to a metro below.

_METRO_TEAMS = {
    "new_york":        {"NFL": ["NY Giants", "NY Jets"], "MLB": ["NY Yankees", "NY Mets"], "NBA": ["NY Knicks", "Brooklyn Nets"], "NHL": ["NY Rangers", "NY Islanders", "NJ Devils"], "MLS": ["NY Red Bulls", "NYCFC"]},
    "los_angeles":     {"NFL": ["LA Rams", "LA Chargers"], "MLB": ["LA Dodgers", "LA Angels"], "NBA": ["LA Lakers", "LA Clippers"], "NHL": ["LA Kings", "Anaheim Ducks"], "MLS": ["LA Galaxy", "LAFC"]},
    "chicago":         {"NFL": ["Chicago Bears"], "MLB": ["Cubs", "White Sox"], "NBA": ["Chicago Bulls"], "NHL": ["Blackhawks"], "MLS": ["Chicago Fire"]},
    "dallas":          {"NFL": ["Dallas Cowboys"], "MLB": ["Texas Rangers"], "NBA": ["Dallas Mavericks"], "NHL": ["Dallas Stars"], "MLS": ["FC Dallas"]},
    "houston":         {"NFL": ["Houston Texans"], "MLB": ["Houston Astros"], "NBA": ["Houston Rockets"], "MLS": ["Houston Dynamo"]},
    "phoenix":         {"MLB": ["Arizona Diamondbacks"], "NBA": ["Phoenix Suns"]},
    "philadelphia":    {"NFL": ["Philadelphia Eagles"], "MLB": ["Philadelphia Phillies"], "NBA": ["Philadelphia 76ers"], "NHL": ["Philadelphia Flyers"], "MLS": ["Philadelphia Union"]},
    "san_antonio":     {"NBA": ["San Antonio Spurs"]},
    "san_diego":       {"MLB": ["San Diego Padres"], "MLS": ["San Diego FC"]},
    "san_jose":        {"NFL": ["SF 49ers"], "MLB": ["SF Giants", "Oakland Athletics"], "NBA": ["Golden State Warriors"], "NHL": ["San Jose Sharks"], "MLS": ["San Jose Earthquakes"]},
    "san_francisco":   {"NFL": ["SF 49ers"], "MLB": ["SF Giants", "Oakland Athletics"], "NBA": ["Golden State Warriors"], "NHL": ["San Jose Sharks"], "MLS": ["San Jose Earthquakes"]},
    "oakland":         {"NFL": ["SF 49ers"], "MLB": ["SF Giants", "Oakland Athletics"], "NBA": ["Golden State Warriors"], "NHL": ["San Jose Sharks"], "MLS": ["San Jose Earthquakes"]},
    "austin":          {"MLS": ["Austin FC"]},
    "jacksonville":    {"NFL": ["Jacksonville Jaguars"]},
    "charlotte":       {"NFL": ["Carolina Panthers"], "NBA": ["Charlotte Hornets"], "MLS": ["Charlotte FC"]},
    "columbus":        {"NHL": ["Columbus Blue Jackets"], "MLS": ["Columbus Crew"]},
    "indianapolis":    {"NFL": ["Indianapolis Colts"], "NBA": ["Indiana Pacers"]},
    "washington_dc":   {"NFL": ["Washington Commanders"], "MLB": ["Washington Nationals"], "NBA": ["Washington Wizards"], "NHL": ["Washington Capitals"], "MLS": ["DC United"]},
    "seattle":         {"NFL": ["Seattle Seahawks"], "MLB": ["Seattle Mariners"], "NHL": ["Seattle Kraken"], "MLS": ["Seattle Sounders"]},
    "denver":          {"NFL": ["Denver Broncos"], "MLB": ["Colorado Rockies"], "NBA": ["Denver Nuggets"], "NHL": ["Colorado Avalanche"], "MLS": ["Colorado Rapids"]},
    "nashville":       {"NFL": ["Tennessee Titans"], "NHL": ["Nashville Predators"], "MLS": ["Nashville SC"]},
    "las_vegas":       {"NFL": ["Las Vegas Raiders"], "NHL": ["Vegas Golden Knights"]},
    "boston":          {"NFL": ["New England Patriots"], "MLB": ["Boston Red Sox"], "NBA": ["Boston Celtics"], "NHL": ["Boston Bruins"], "MLS": ["New England Revolution"]},
    "detroit":         {"NFL": ["Detroit Lions"], "MLB": ["Detroit Tigers"], "NBA": ["Detroit Pistons"], "NHL": ["Detroit Red Wings"]},
    "portland":        {"NBA": ["Portland Trail Blazers"], "MLS": ["Portland Timbers"]},
    "memphis":         {"NBA": ["Memphis Grizzlies"]},
    "baltimore":       {"NFL": ["Baltimore Ravens"], "MLB": ["Baltimore Orioles"]},
    "milwaukee":       {"MLB": ["Milwaukee Brewers"], "NBA": ["Milwaukee Bucks"]},
    "sacramento":      {"NBA": ["Sacramento Kings"]},
    "atlanta":         {"NFL": ["Atlanta Falcons"], "MLB": ["Atlanta Braves"], "NBA": ["Atlanta Hawks"], "MLS": ["Atlanta United"]},
    "kansas_city":     {"NFL": ["Kansas City Chiefs"], "MLB": ["Kansas City Royals"], "MLS": ["Sporting KC"]},
    "raleigh":         {"NHL": ["Carolina Hurricanes"]},
    "miami":           {"NFL": ["Miami Dolphins"], "MLB": ["Miami Marlins"], "NBA": ["Miami Heat"], "NHL": ["Florida Panthers"], "MLS": ["Inter Miami"]},
    "oklahoma_city":   {"NBA": ["Oklahoma City Thunder"]},
    "minneapolis":     {"NFL": ["Minnesota Vikings"], "MLB": ["Minnesota Twins"], "NBA": ["Minnesota Timberwolves"], "NHL": ["Minnesota Wild"], "MLS": ["Minnesota United"]},
    "cleveland":       {"NFL": ["Cleveland Browns"], "MLB": ["Cleveland Guardians"], "NBA": ["Cleveland Cavaliers"]},
    "pittsburgh":      {"NFL": ["Pittsburgh Steelers"], "MLB": ["Pittsburgh Pirates"], "NHL": ["Pittsburgh Penguins"]},
    "new_orleans":     {"NFL": ["New Orleans Saints"], "NBA": ["New Orleans Pelicans"]},
    "st_louis":        {"MLB": ["St. Louis Cardinals"], "NHL": ["St. Louis Blues"], "MLS": ["St. Louis City SC"]},
    "tampa":           {"NFL": ["Tampa Bay Buccaneers"], "MLB": ["Tampa Bay Rays"], "NHL": ["Tampa Bay Lightning"]},
    "salt_lake_city":  {"NBA": ["Utah Jazz"], "NHL": ["Utah Hockey Club"], "MLS": ["Real Salt Lake"]},
    "buffalo":         {"NFL": ["Buffalo Bills"], "NHL": ["Buffalo Sabres"]},
    "cincinnati":      {"NFL": ["Cincinnati Bengals"], "MLB": ["Cincinnati Reds"], "MLS": ["FC Cincinnati"]},
    "orlando":         {"NBA": ["Orlando Magic"], "MLS": ["Orlando City SC"]},
    "green_bay":       {"NFL": ["Green Bay Packers"]},
    "baton_rouge":     {"NFL": ["New Orleans Saints"], "NBA": ["New Orleans Pelicans"]},
    "fresno":          {"NBA": ["Fresno Grizzlies (G-League)"]},
    "tulsa":           {"NBA": ["Tulsa Thunder (G-League)"]},
    "laredo":          {"NBA": ["Laredo Lemurs"]},
    "spokane":         {},
    "colorado_springs":{"NFL": ["Denver Broncos"], "MLB": ["Colorado Rockies"], "NBA": ["Denver Nuggets"], "NHL": ["Colorado Avalanche"], "MLS": ["Colorado Rapids"]},
}

# City name → metro key
_CITY_METRO = {
    # New York metro
    "New York": "new_york", "Jersey City": "new_york", "Newark": "new_york",
    "Yonkers": "new_york", "Paterson": "new_york", "Elizabeth": "new_york",
    "Stamford": "new_york", "Bridgeport": "new_york", "New Haven": "new_york",
    # Los Angeles metro
    "Los Angeles": "los_angeles", "Long Beach": "los_angeles", "Anaheim": "los_angeles",
    "Santa Ana": "los_angeles", "Irvine": "los_angeles", "Glendale": "los_angeles",
    "Santa Clarita": "los_angeles", "Fontana": "los_angeles", "San Bernardino": "los_angeles",
    "Moreno Valley": "los_angeles", "Oxnard": "los_angeles", "Thousand Oaks": "los_angeles",
    "Simi Valley": "los_angeles", "Torrance": "los_angeles", "Fullerton": "los_angeles",
    "Pomona": "los_angeles", "Orange": "los_angeles", "Rancho Cucamonga": "los_angeles",
    "Inglewood": "los_angeles", "Burbank": "los_angeles", "El Monte": "los_angeles",
    "Pasadena": "los_angeles", "Downey": "los_angeles", "Costa Mesa": "los_angeles",
    "Huntington Beach": "los_angeles", "Garden Grove": "los_angeles", "West Covina": "los_angeles",
    "Lancaster": "los_angeles", "Palmdale": "los_angeles", "Corona": "los_angeles",
    "Menifee": "los_angeles", "Murrieta": "los_angeles", "Temecula": "los_angeles",
    "Jurupa Valley": "los_angeles", "Ontario": "los_angeles",
    # Chicago metro
    "Chicago": "chicago", "Aurora": "chicago", "Naperville": "chicago",
    "Joliet": "chicago", "Elgin": "chicago",
    # Dallas metro
    "Dallas": "dallas", "Fort Worth": "dallas", "Arlington": "dallas",
    "Plano": "dallas", "Garland": "dallas", "Irving": "dallas",
    "Mesquite": "dallas", "McKinney": "dallas", "Lewisville": "dallas",
    "Denton": "dallas", "Richardson": "dallas", "Carrollton": "dallas",
    "Grand Prairie": "dallas", "Frisco": "dallas", "Allen": "dallas",
    # Houston metro
    "Houston": "houston", "Pasadena": "houston", "Pearland": "houston",
    "Sugar Land": "houston", "Conroe": "houston", "League City": "houston",
    "Beaumont": "houston",
    # Phoenix metro
    "Phoenix": "phoenix", "Mesa": "phoenix", "Scottsdale": "phoenix",
    "Chandler": "phoenix", "Gilbert": "phoenix", "Glendale": "phoenix",
    "Goodyear": "phoenix", "Surprise": "phoenix", "Peoria": "phoenix",
    "Tempe": "phoenix", "Buckeye": "phoenix",
    # Philadelphia
    "Philadelphia": "philadelphia", "Allentown": "philadelphia",
    # San Diego
    "San Diego": "san_diego", "Escondido": "san_diego",
    "El Cajon": "san_diego", "Chula Vista": "san_diego", "Carlsbad": "san_diego",
    "Oceanside": "san_diego",
    # SF Bay Area
    "San Francisco": "san_francisco", "San Jose": "san_jose", "Oakland": "oakland",
    "Fremont": "san_jose", "Santa Clara": "san_jose", "Berkeley": "oakland",
    "Richmond": "oakland", "Fairfield": "san_jose", "Vallejo": "san_jose",
    "Antioch": "san_jose", "Concord": "san_jose", "Hayward": "oakland",
    "Sunnyvale": "san_jose", "San Mateo": "san_francisco", "Daly City": "san_francisco",
    "Stockton": "san_jose",
    # Seattle metro
    "Seattle": "seattle", "Tacoma": "seattle", "Bellevue": "seattle",
    "Kent": "seattle", "Renton": "seattle", "Everett": "seattle",
    "Federal Way": "seattle", "Spokane Valley": "spokane",
    # Denver metro
    "Denver": "denver", "Lakewood": "denver", "Thornton": "denver",
    "Arvada": "denver", "Westminster": "denver", "Centennial": "denver",
    "Greeley": "denver", "Boulder": "denver", "Colorado Springs": "colorado_springs",
    # Miami metro
    "Miami": "miami", "Fort Lauderdale": "miami", "Hialeah": "miami",
    "Miramar": "miami", "Pompano Beach": "miami", "West Palm Beach": "miami",
    "Pembroke Pines": "miami", "Coral Springs": "miami", "Boca Raton": "miami",
    "Miami Gardens": "miami", "Hollywood": "miami", "Davie": "miami",
    "Plantation": "miami", "Sunrise": "miami", "Port St. Lucie": "miami",
    # Boston metro
    "Boston": "boston", "Worcester": "boston", "Cambridge": "boston",
    "Lowell": "boston", "Brockton": "boston", "Lynn": "boston",
    "Quincy": "boston", "New Bedford": "boston", "Providence": "boston",
    "Manchester": "boston",
    # DC metro
    "Washington": "washington_dc", "Alexandria": "washington_dc",
    "Chesapeake": "washington_dc",
    # Other major cities (standalone)
    "Chicago": "chicago", "Nashville": "nashville", "Las Vegas": "las_vegas",
    "North Las Vegas": "las_vegas", "Henderson": "las_vegas",
    "Detroit": "detroit", "Warren": "detroit", "Sterling Heights": "detroit",
    "Dearborn": "detroit", "Ann Arbor": "detroit", "Clinton": "detroit",
    "Portland": "portland", "Gresham": "portland", "Hillsboro": "portland",
    "Vancouver": "portland", "Salem": "portland", "Eugene": "portland",
    "Memphis": "memphis", "Baltimore": "baltimore",
    "Milwaukee": "milwaukee", "Madison": "milwaukee",
    "Sacramento": "sacramento", "Elk Grove": "sacramento",
    "Roseville": "sacramento", "Vacaville": "sacramento",
    "Atlanta": "atlanta", "Sandy Springs": "atlanta", "South Fulton": "atlanta",
    "Kansas City": "kansas_city", "Overland Park": "kansas_city",
    "Olathe": "kansas_city", "Independence": "kansas_city", "Lee's Summit": "kansas_city",
    "Raleigh": "raleigh", "Durham": "raleigh", "Cary": "raleigh",
    "Greensboro": "raleigh", "Winston-Salem": "raleigh", "High Point": "raleigh",
    "Concord": "charlotte",
    "Tampa": "tampa", "St. Petersburg": "tampa", "Clearwater": "tampa",
    "Lakeland": "tampa",
    "Salt Lake City": "salt_lake_city", "West Valley City": "salt_lake_city",
    "West Jordan": "salt_lake_city", "Provo": "salt_lake_city",
    "St. George": "salt_lake_city",
    "Buffalo": "buffalo", "Cincinnati": "cincinnati",
    "Columbus": "columbus", "Orlando": "orlando", "Deltona": "orlando",
    "Cape Coral": "orlando",
    "Green Bay": "green_bay", "Indianapolis": "indianapolis",
    "Fishers": "indianapolis", "Carmel": "indianapolis", "South Bend": "indianapolis",
    "Oklahoma City": "oklahoma_city", "Norman": "oklahoma_city",
    "Broken Arrow": "oklahoma_city", "Tulsa": "tulsa",
    "Minneapolis": "minneapolis", "Saint Paul": "minneapolis",
    "Rochester": "minneapolis",
    "Cleveland": "cleveland", "Akron": "cleveland",
    "Pittsburgh": "pittsburgh", "New Orleans": "new_orleans",
    "Baton Rouge": "baton_rouge", "Shreveport": "baton_rouge",
    "St. Louis": "st_louis", "Jacksonville": "jacksonville",
    "Charlotte": "charlotte", "San Antonio": "san_antonio",
    "Austin": "austin", "Round Rock": "austin", "Georgetown": "austin",
    "Miami": "miami", "Richmond": "washington_dc",
    "Fresno": "fresno", "Bakersfield": "fresno",
    "Laredo": "laredo", "Stockton": "san_jose",
    "Modesto": "san_jose",
}


def get_teams(city: str, row) -> dict:
    """Return {league: [team names]} for a city, or empty dict if no teams."""
    metro = _CITY_METRO.get(city)
    if not metro:
        return {}
    teams = _METRO_TEAMS.get(metro, {})
    # Filter to only leagues where this city's count > 0
    result = {}
    for league, col in [("NFL", "nfl_teams"), ("MLB", "mlb_teams"),
                        ("NBA", "nba_teams"), ("NHL", "nhl_teams"), ("MLS", "mls_teams")]:
        if pd.notna(row.get(col)) and row.get(col, 0) >= 1 and league in teams:
            result[league] = teams[league]
    return result

# ── page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="City Suggestor",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .stApp { background-color: #0f1117; }
    section[data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2d3048;
    }
    .city-card {
        background: #1e2130;
        border: 1px solid #2d3048;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 8px;
    }
    /* Sports pill — inline <details> element styled like a stat-pill */
    details.sports-pill {
        display: inline-block;
        position: relative;
        vertical-align: middle;
        margin: 2px 3px 2px 0;
    }
    details.sports-pill summary {
        background: #2d3048;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 11px;
        color: #a5b4fc;
        cursor: pointer;
        list-style: none;
        user-select: none;
        outline: none;
    }
    details.sports-pill summary::-webkit-details-marker { display: none; }
    details.sports-pill summary::marker { display: none; }
    details.sports-pill summary:hover { background: #3d4060; color: #c4b5fd; }
    details.sports-pill[open] summary { border-radius: 10px 10px 0 0; }
    details.sports-pill .sports-dropdown {
        position: absolute;
        top: 100%;
        left: 0;
        background: #1e2130;
        border: 1px solid #4f46e5;
        border-radius: 0 8px 8px 8px;
        padding: 8px 12px;
        z-index: 999;
        min-width: 220px;
        font-size: 12px;
        color: #d1d5db;
        line-height: 1.8;
        white-space: nowrap;
    }
    .city-rank {
        font-size: 12px;
        color: #6b7280;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .city-name {
        font-size: 20px;
        font-weight: 700;
        color: #f9fafb;
        margin: 2px 0;
    }
    .city-state {
        font-size: 13px;
        color: #9ca3af;
    }
    .city-stat {
        font-size: 12px;
        color: #d1d5db;
        margin-top: 6px;
    }
    .stat-pill {
        display: inline-block;
        background: #2d3048;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 11px;
        color: #a5b4fc;
        margin: 2px 3px 2px 0;
    }
    .match-score {
        font-size: 22px;
        font-weight: 800;
        color: #818cf8;
    }
    .section-header {
        font-size: 11px;
        font-weight: 700;
        color: #6366f1;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin: 16px 0 6px 0;
    }
    div[data-testid="stSlider"] label {
        font-size: 12px !important;
        color: #9ca3af !important;
    }
    h1 { color: #f9fafb !important; }
    h2, h3 { color: #e5e7eb !important; }
    .stSelectbox label, .stMultiSelect label, .stCheckbox label {
        color: #9ca3af !important;
        font-size: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# ── load data ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("cities_master.csv")
    except FileNotFoundError:
        st.error("cities_master.csv not found. Make sure it's in the same folder as app.py")
        st.stop()

    # Clean up
    numeric_cols = [
        "population", "metro_population", "median_household_income",
        "median_home_price", "avg_temp_f", "avg_summer_high_f",
        "avg_winter_low_f", "walkability_score_100", "dist_airport_miles",
        "dist_zoo_miles", "dist_theme_park_miles", "nature_score",
        "dist_natl_park_miles", "dist_coast_miles", "elevation_ft",
        "seasons_count", "total_pro_teams", "lat", "lon",
        "nfl_teams", "mlb_teams", "nba_teams", "nhl_teams", "mls_teams",
        "temp_range_f", "transit_score",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "coastline_type" not in df.columns:
        df["coastline_type"] = "none"
    df["coastline_type"] = df["coastline_type"].fillna("none")

    return df

df = load_data()

# ── helper: safe min/max ──────────────────────────────────────────────────────

def safe_range(col, default_min=0, default_max=100):
    if col not in df.columns or df[col].isna().all():
        return default_min, default_max
    return float(df[col].min()), float(df[col].max())

# ── sidebar filters ───────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("# City Suggestor")
    st.markdown("Filter cities by what matters to you.")
    st.markdown("---")

    # ── Population
    st.markdown('<div class="section-header">Population</div>', unsafe_allow_html=True)
    pop_min, pop_max = safe_range("population", 100_000, 10_000_000)
    pop_range = st.slider(
        "City population",
        min_value=int(pop_min), max_value=int(pop_max),
        value=(int(pop_min), int(pop_max)),
        format="%,d", key="pop"
    )

    metro_min, metro_max = safe_range("metro_population", 100_000, 20_000_000)
    metro_range = st.slider(
        "Metro population",
        min_value=int(metro_min), max_value=int(metro_max),
        value=(int(metro_min), int(metro_max)),
        format="%,d", key="metro"
    )

    # ── Income & Housing
    st.markdown('<div class="section-header">Income & Housing</div>', unsafe_allow_html=True)
    inc_min, inc_max = safe_range("median_household_income", 30_000, 200_000)
    inc_range = st.slider(
        "Median household income ($)",
        min_value=int(inc_min), max_value=int(inc_max),
        value=(int(inc_min), int(inc_max)),
        format="$%,d", key="income"
    )

    home_min, home_max = safe_range("median_home_price", 50_000, 2_000_000)
    home_range = st.slider(
        "Median home price ($)",
        min_value=int(home_min), max_value=int(home_max),
        value=(int(home_min), int(home_max)),
        format="$%,d", key="home"
    )

    # ── Temperature
    st.markdown('<div class="section-header">Temperature</div>', unsafe_allow_html=True)
    temp_min, temp_max = safe_range("avg_temp_f", 20.0, 90.0)
    temp_range = st.slider(
        "Avg annual temp (°F)",
        min_value=float(temp_min), max_value=float(temp_max),
        value=(float(temp_min), float(temp_max)),
        step=1.0, format="%.0f°F", key="temp"
    )

    sum_min, sum_max = safe_range("avg_summer_high_f", 60.0, 115.0)
    summer_range = st.slider(
        "Avg summer high (°F)",
        min_value=float(sum_min), max_value=float(sum_max),
        value=(float(sum_min), float(sum_max)),
        step=1.0, format="%.0f°F", key="summer"
    )

    win_min, win_max = safe_range("avg_winter_low_f", -10.0, 65.0)
    winter_range = st.slider(
        "Avg winter low (°F)",
        min_value=float(win_min), max_value=float(win_max),
        value=(float(win_min), float(win_max)),
        step=1.0, format="%.0f°F", key="winter"
    )

    # ── Seasons
    st.markdown('<div class="section-header">Seasons</div>', unsafe_allow_html=True)
    seasons_range = st.slider(
        "Number of seasons (1-4)",
        min_value=1, max_value=4,
        value=(1, 4), key="seasons"
    )

    # ── Walkability
    st.markdown('<div class="section-header">Walkability</div>', unsafe_allow_html=True)
    walk_min, walk_max = safe_range("walkability_score_100", 0.0, 100.0)
    walk_range = st.slider(
        "Walkability score (0-100)",
        min_value=float(walk_min), max_value=float(walk_max),
        value=(float(walk_min), float(walk_max)),
        step=1.0, format="%.0f", key="walk"
    )

    # ── Distances
    st.markdown('<div class="section-header">Distances</div>', unsafe_allow_html=True)
    ap_min, ap_max = safe_range("dist_airport_miles", 0.0, 200.0)
    airport_range = st.slider(
        "Distance to major airport (miles)",
        min_value=float(ap_min), max_value=float(ap_max),
        value=(float(ap_min), float(ap_max)),
        step=1.0, format="%.0f mi", key="airport"
    )

    zoo_min, zoo_max = safe_range("dist_zoo_miles", 0.0, 300.0)
    zoo_range = st.slider(
        "Distance to zoo (miles)",
        min_value=float(zoo_min), max_value=float(zoo_max),
        value=(float(zoo_min), float(zoo_max)),
        step=1.0, format="%.0f mi", key="zoo"
    )

    park_min, park_max = safe_range("dist_theme_park_miles", 0.0, 300.0)
    park_range = st.slider(
        "Distance to theme park (miles)",
        min_value=float(park_min), max_value=float(park_max),
        value=(float(park_min), float(park_max)),
        step=1.0, format="%.0f mi", key="park"
    )

    np_min, np_max = safe_range("dist_natl_park_miles", 0.0, 500.0)
    natl_park_range = st.slider(
        "Distance to national park (miles)",
        min_value=float(np_min), max_value=float(np_max),
        value=(float(np_min), float(np_max)),
        step=1.0, format="%.0f mi", key="natl_park"
    )

    # ── Nature
    st.markdown('<div class="section-header">Nature & Outdoors</div>', unsafe_allow_html=True)
    nature_min, nature_max = safe_range("nature_score", 0.0, 100.0)
    nature_range = st.slider(
        "Nature & outdoor score (0-100)",
        min_value=float(nature_min), max_value=float(nature_max),
        value=(float(nature_min), float(nature_max)),
        step=1.0, format="%.0f", key="nature"
    )

    # ── Coastline
    st.markdown('<div class="section-header">Coastline</div>', unsafe_allow_html=True)
    coastline_options = ["Any", "ocean", "great_lakes", "none"]
    # coastline_type is now "none" for inland cities (fixed threshold)
    coastline_filter = st.selectbox(
        "Coastline type",
        options=coastline_options,
        index=0, key="coast"
    )

    # ── Sports
    st.markdown('<div class="section-header">Pro Sports Teams</div>', unsafe_allow_html=True)
    total_sports_range = st.slider(
        "Total pro sports teams",
        min_value=0, max_value=12,
        value=(0, 12), key="sports_total"
    )

    st.markdown("**Require specific leagues:**")
    need_nfl = st.checkbox("NFL team", value=False, key="nfl")
    need_mlb = st.checkbox("MLB team", value=False, key="mlb")
    need_nba = st.checkbox("NBA team", value=False, key="nba")
    need_nhl = st.checkbox("NHL team", value=False, key="nhl")
    need_mls = st.checkbox("MLS team", value=False, key="mls")

    # ── Reset
    st.markdown("---")
    if st.button("Reset all filters", use_container_width=True):
        for key in ["pop", "metro", "income", "home", "temp", "summer", "winter",
                    "seasons", "walk", "airport", "zoo", "park", "natl_park",
                    "nature", "coast", "sports_total", "nfl", "mlb", "nba", "nhl",
                    "mls", "city_search"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ── apply filters ─────────────────────────────────────────────────────────────

filtered = df.copy()

def apply_range(df, col, range_tuple):
    if col not in df.columns:
        return df
    lo, hi = range_tuple
    return df[df[col].between(lo, hi, inclusive="both") | df[col].isna()]

filtered = apply_range(filtered, "population",              pop_range)
filtered = apply_range(filtered, "metro_population",        metro_range)
filtered = apply_range(filtered, "median_household_income", inc_range)
filtered = apply_range(filtered, "median_home_price",       home_range)
filtered = apply_range(filtered, "avg_temp_f",              temp_range)
filtered = apply_range(filtered, "avg_summer_high_f",       summer_range)
filtered = apply_range(filtered, "avg_winter_low_f",        winter_range)
filtered = apply_range(filtered, "walkability_score_100",   walk_range)
filtered = apply_range(filtered, "dist_airport_miles",      airport_range)
filtered = apply_range(filtered, "dist_zoo_miles",          zoo_range)
filtered = apply_range(filtered, "dist_theme_park_miles",   park_range)
filtered = apply_range(filtered, "dist_natl_park_miles",    natl_park_range)
filtered = apply_range(filtered, "nature_score",            nature_range)
filtered = apply_range(filtered, "total_pro_teams",         total_sports_range)

if "seasons_count" in filtered.columns:
    filtered = filtered[
        filtered["seasons_count"].between(seasons_range[0], seasons_range[1]) |
        filtered["seasons_count"].isna()
    ]

if coastline_filter != "Any":
    filtered = filtered[filtered["coastline_type"] == coastline_filter]

if need_nfl: filtered = filtered[filtered.get("nfl_teams", pd.Series(0, index=filtered.index)) >= 1]
if need_mlb: filtered = filtered[filtered.get("mlb_teams", pd.Series(0, index=filtered.index)) >= 1]
if need_nba: filtered = filtered[filtered.get("nba_teams", pd.Series(0, index=filtered.index)) >= 1]
if need_nhl: filtered = filtered[filtered.get("nhl_teams", pd.Series(0, index=filtered.index)) >= 1]
if need_mls: filtered = filtered[filtered.get("mls_teams", pd.Series(0, index=filtered.index)) >= 1]

# Sort by city population descending
filtered = filtered.sort_values("population", ascending=False).reset_index(drop=True)

# ── header ────────────────────────────────────────────────────────────────────

st.markdown(f"## City Suggestor")

city_search = st.text_input("Search for a specific city", placeholder="e.g. Austin, Denver...", key="city_search")
if city_search.strip():
    search_mask = filtered["city"].str.contains(city_search.strip(), case=False, na=False)
    filtered = filtered[search_mask].reset_index(drop=True)

st.markdown(f"**{len(filtered)}** cities match your filters")
st.markdown("---")

# ── main layout: list + map ───────────────────────────────────────────────────

col_list, col_map = st.columns([1, 1.4], gap="large")

# ── city list ─────────────────────────────────────────────────────────────────

with col_list:
    st.markdown("### Matching Cities")

    if filtered.empty:
        st.warning("No cities match your current filters. Try widening your ranges.")
    else:
        for i, row in filtered.iterrows():
            rank = i + 1

            # Build stat pills
            pills = []
            temp_parts = []
            if pd.notna(row.get("avg_temp_f")):
                temp_parts.append(f"{row['avg_temp_f']:.0f}°F avg")
            if pd.notna(row.get("avg_summer_high_f")):
                temp_parts.append(f"{row['avg_summer_high_f']:.0f}°F summer")
            if pd.notna(row.get("avg_winter_low_f")):
                temp_parts.append(f"{row['avg_winter_low_f']:.0f}°F winter")
            if temp_parts:
                pills.append("  |  ".join(temp_parts))
            if pd.notna(row.get("median_household_income")):
                pills.append(f"${row['median_household_income']:,.0f} income")
            if pd.notna(row.get("median_home_price")):
                pills.append(f"${row['median_home_price']:,.0f} home")
            if pd.notna(row.get("walkability_score_100")):
                pills.append(f"{row['walkability_score_100']:.0f} walk score")
            if pd.notna(row.get("dist_airport_miles")):
                pills.append(f"{row['dist_airport_miles']:.0f} mi to airport")
            if pd.notna(row.get("nature_score")):
                pills.append(f"{row['nature_score']:.0f} nature")
            if pd.notna(row.get("seasons_count")):
                pills.append(f"{int(row['seasons_count'])} seasons")

            # Sports pill — built separately as a clickable <details> element
            total_teams = int(row.get("total_pro_teams", 0) or 0)
            teams_by_league = get_teams(row["city"], row) if total_teams > 0 else {}
            if total_teams > 0:
                teams_rows = "".join(
                    f'<div><strong style="color:#c4b5fd">{lg}:</strong> {", ".join(names)}</div>'
                    for lg, names in teams_by_league.items()
                ) or f"<div>{total_teams} pro team(s) in metro area</div>"
                sports_pill = f"""
                <details class="sports-pill">
                  <summary>{total_teams} pro team{'s' if total_teams != 1 else ''}</summary>
                  <div class="sports-dropdown">{teams_rows}</div>
                </details>"""
            else:
                sports_pill = ""

            if pd.notna(row.get("environment_type")):
                pills.append(str(row["environment_type"]).replace("_", " ").title())
            elif row.get("coastline_type") in ("ocean", "great_lakes"):
                pills.append("Ocean" if row["coastline_type"] == "ocean" else "Great Lakes")

            pills_html = "".join([f'<span class="stat-pill">{p}</span>' for p in pills])

            pop_str = f"{row['population']:,.0f}" if pd.notna(row.get("population")) else "N/A"
            metro_str = f"{row['metro_population']:,.0f}" if pd.notna(row.get("metro_population")) else "N/A"

            st.markdown(f"""
            <div class="city-card">
                <div class="city-rank">#{rank}</div>
                <div class="city-name">{row['city']}</div>
                <div class="city-state">{row['state']} &nbsp;·&nbsp; Pop: {pop_str} &nbsp;·&nbsp; Metro: {metro_str}</div>
                <div style="margin-top:8px">{pills_html}{sports_pill}</div>
            </div>
            """, unsafe_allow_html=True)

# ── map ───────────────────────────────────────────────────────────────────────

with col_map:
    st.markdown("### Map")

    map_df = filtered.dropna(subset=["lat", "lon"]).copy()

    if map_df.empty:
        st.info("No cities with coordinates to display on map.")
    else:
        # Build hover text
        map_df["hover"] = map_df.apply(lambda r: (
            f"{r['city']}, {r['state']}<br>"
            f"Pop: {r['population']:,.0f}<br>" if pd.notna(r.get('population')) else f"{r['city']}, {r['state']}<br>"
        ) + (
            f"Avg Temp: {r['avg_temp_f']:.0f}°F<br>" if pd.notna(r.get('avg_temp_f')) else ""
        ) + (
            f"Income: ${r['median_household_income']:,.0f}<br>" if pd.notna(r.get('median_household_income')) else ""
        ) + (
            f"Home Price: ${r['median_home_price']:,.0f}<br>" if pd.notna(r.get('median_home_price')) else ""
        ) + (
            f"Walk Score: {r['walkability_score_100']:.0f}<br>" if pd.notna(r.get('walkability_score_100')) else ""
        ) + (
            f"Nature: {r['nature_score']:.0f}<br>" if pd.notna(r.get('nature_score')) else ""
        ) + (
            f"Pro Teams: {int(r['total_pro_teams'])}" if pd.notna(r.get('total_pro_teams')) else ""
        ), axis=1)

        fig = px.scatter_mapbox(
            map_df,
            lat="lat",
            lon="lon",
            hover_name="city",
            hover_data={
                "lat": False,
                "lon": False,
                "state": True,
                "population": ":,.0f",
                "avg_temp_f": ":.1f",
                "median_household_income": ":,.0f",
                "walkability_score_100": ":.0f",
            },
            color="metro_population",
            color_continuous_scale="Viridis",
            size_max=18,
            zoom=3,
            height=680,
            mapbox_style="carto-darkmatter",
        )

        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            coloraxis_colorbar=dict(
                title="Metro Pop",
                thickness=12,
                len=0.5,
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        fig.update_traces(
            marker=dict(size=10, opacity=0.85)
        )

        st.plotly_chart(fig, use_container_width=True)

# ── data table at bottom ──────────────────────────────────────────────────────

st.markdown("---")
st.markdown("### Full Data Table")

display_cols = [c for c in [
    "city", "state", "population", "metro_population",
    "median_household_income", "median_home_price",
    "avg_temp_f", "avg_summer_high_f", "avg_winter_low_f",
    "walkability_score_100", "dist_airport_miles",
    "dist_zoo_miles", "dist_theme_park_miles",
    "nature_score", "dist_natl_park_miles",
    "coastline_type", "dist_coast_miles", "elevation_ft",
    "seasons_count", "total_pro_teams",
    "nfl_teams", "mlb_teams", "nba_teams", "nhl_teams", "mls_teams",
] if c in filtered.columns]

st.dataframe(
    filtered[display_cols].style.format({
        "population":               "{:,.0f}",
        "metro_population":         "{:,.0f}",
        "median_household_income":  "${:,.0f}",
        "median_home_price":        "${:,.0f}",
        "avg_temp_f":               "{:.1f}°F",
        "avg_summer_high_f":        "{:.1f}°F",
        "avg_winter_low_f":         "{:.1f}°F",
        "walkability_score_100":    "{:.0f}",
        "dist_airport_miles":       "{:.1f} mi",
        "dist_zoo_miles":           "{:.1f} mi",
        "dist_theme_park_miles":    "{:.1f} mi",
        "nature_score":             "{:.0f}",
        "dist_natl_park_miles":     "{:.1f} mi",
        "dist_coast_miles":         "{:.1f} mi",
        "elevation_ft":             "{:.0f} ft",
    }, na_rep="N/A"),
    use_container_width=True,
    height=400,
)