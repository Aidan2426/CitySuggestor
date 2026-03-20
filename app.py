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
import requests

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Base ── */
    html, body, [class*="css"], * { font-family: 'Inter', sans-serif !important; }
    .stApp { background-color: #F4F6F9; }
    .main  { background-color: #F4F6F9; }

    /* ── Top header / toolbar ── */
    header[data-testid="stHeader"] {
        background-color: #FFFFFF !important;
        border-bottom: 1px solid #E2E8F0;
    }
    [data-testid="stToolbar"] { background: transparent !important; }
    [data-testid="stDecoration"] { background: #1D4ED8 !important; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    /* ── City card ── */
    .city-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 14px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .card-photo {
        width: 100%; height: 180px;
        object-fit: cover; display: block;
        background-color: #E2E8F0;
    }
    .card-photo-placeholder {
        width: 100%; height: 180px;
        background: linear-gradient(135deg, #DBEAFE 0%, #EFF6FF 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 32px; color: #93C5FD;
    }
    .card-body { padding: 14px 16px 12px; }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
    }
    .card-rank {
        font-size: 11px; font-weight: 700;
        color: #1D4ED8; letter-spacing: 0.08em;
    }
    .card-city-name {
        font-size: 20px; font-weight: 700;
        color: #111827; line-height: 1.2;
    }
    .card-subtitle {
        font-size: 12px; color: #6B7280; margin-top: 2px;
    }

    /* ── 2×2 stat grid ── */
    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-bottom: 12px;
    }
    .stat-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 8px 10px;
    }
    .stat-label {
        font-size: 9px; font-weight: 700;
        color: #9CA3AF; letter-spacing: 0.1em;
        text-transform: uppercase; margin-bottom: 3px;
    }
    .stat-val {
        font-size: 16px; font-weight: 700; color: #111827;
    }
    .stat-val.accent { color: #EA580C; }

    /* ── Tags row ── */
    .card-tags { display: flex; flex-wrap: wrap; gap: 5px; }
    .ctag {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 10px; font-weight: 600;
        color: #1D4ED8; letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .ctag-lakes {
        background: #F0F9FF;
        border: 1px solid #7DD3FC;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 10px; font-weight: 600;
        color: #0284C7; letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    /* ── Sports pill ── */
    details.sports-pill {
        display: inline-block; position: relative;
        vertical-align: middle;
    }
    details.sports-pill summary {
        background: #FFF7ED; border: 1px solid #FED7AA;
        border-radius: 4px; padding: 2px 8px;
        font-size: 10px; font-weight: 600;
        color: #C2410C; letter-spacing: 0.06em;
        text-transform: uppercase;
        cursor: pointer; list-style: none; user-select: none; outline: none;
    }
    details.sports-pill summary::-webkit-details-marker { display: none; }
    details.sports-pill summary::marker { display: none; }
    details.sports-pill summary:hover { background: #FFEDD5; border-color: #FB923C; }
    details.sports-pill[open] summary { border-radius: 4px 4px 0 0; }
    details.sports-pill .sports-dropdown {
        position: absolute; top: 100%; left: 0;
        background: #FFFFFF; border: 1px solid #1D4ED8;
        border-radius: 0 6px 6px 6px;
        padding: 8px 12px; z-index: 999;
        min-width: 200px; font-size: 12px;
        color: #374151; line-height: 1.9; white-space: nowrap;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* ── Search bar ── */
    div[data-testid="stTextInput"] {
        max-width: 520px;
        margin: 0 auto 4px;
    }
    div[data-testid="stTextInput"] > div {
        position: relative;
    }
    div[data-testid="stTextInput"] > div::before {
        content: "";
        position: absolute;
        left: 14px; top: 50%; transform: translateY(-50%);
        width: 16px; height: 16px; z-index: 1; pointer-events: none;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%239CA3AF' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'/%3E%3C/svg%3E");
        background-repeat: no-repeat; background-size: contain;
    }
    div[data-testid="stTextInput"] input {
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 24px !important;
        padding-left: 40px !important;
        color: #111827 !important;
        font-size: 14px !important;
        height: 42px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #1D4ED8 !important;
        box-shadow: 0 0 0 3px rgba(29,78,216,0.15) !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #9CA3AF !important;
    }

    /* ── Sidebar labels & sliders ── */
    .section-header {
        font-size: 10px; font-weight: 700;
        color: #9CA3AF; letter-spacing: 0.12em;
        text-transform: uppercase; margin: 16px 0 6px 0;
    }
    div[data-testid="stSlider"] label { font-size: 12px !important; color: #6B7280 !important; }
    .stSelectbox label, .stMultiSelect label, .stCheckbox label {
        color: #6B7280 !important; font-size: 12px !important;
    }

    /* ── Headings & body text ── */
    h1, h2, h3 { color: #111827 !important; }
    p, li, span { color: #374151; }
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


_STATE_NAMES = {
    "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California",
    "CO":"Colorado","CT":"Connecticut","DE":"Delaware","FL":"Florida","GA":"Georgia",
    "HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa",
    "KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland",
    "MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi",
    "MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire",
    "NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
    "ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania",
    "RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee",
    "TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington",
    "WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming","DC":"District of Columbia",
}

@st.cache_data(show_spinner=False, ttl=86400)
def get_city_photo(city: str, state: str) -> str:
    """Fetch a single Wikipedia thumbnail. Fast — one API call, cached."""
    state_name = _STATE_NAMES.get(state, state)
    for slug in [
        f"{city}_skyline".replace(" ", "_"),
        f"{city},_{state_name}".replace(" ", "_"),
        city.replace(" ", "_"),
    ]:
        try:
            resp = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}",
                timeout=4, headers={"User-Agent": "CitySuggestor/1.0"},
            )
            if resp.status_code == 200:
                url = resp.json().get("thumbnail", {}).get("source", "")
                if url:
                    return url
        except Exception:
            pass
    return ""


def fmt_pop(n):
    if pd.isna(n): return "N/A"
    n = int(n)
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.0f}k"
    return str(n)

def fmt_money(n, short=True):
    if pd.isna(n): return "N/A"
    if short:
        if n >= 1_000_000: return f"${n/1_000_000:.1f}M"
        if n >= 1_000: return f"${n/1_000:.0f}k"
    return f"${int(n):,}"

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

_, search_col, _ = st.columns([1, 2, 1])
with search_col:
    city_search = st.text_input(
        "search",
        placeholder="Search cities, regions, or climates...",
        key="city_search",
        label_visibility="collapsed",
    )
if city_search.strip():
    search_mask = filtered["city"].str.contains(city_search.strip(), case=False, na=False)
    filtered = filtered[search_mask].reset_index(drop=True)

st.markdown(f"**{len(filtered)}** cities match your filters")
display_df = filtered

st.markdown("---")

# ── map (full width, between search and list) ─────────────────────────────────

map_df = display_df.dropna(subset=["lat", "lon"]).copy()

if map_df.empty:
    st.info("No cities with coordinates to display on map.")
else:
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
            "nature_score": ":.0f",
        },
        color="metro_population",
        color_continuous_scale="Viridis",
        size_max=18,
        zoom=3,
        height=430,
        mapbox_style="carto-positron",
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title="Metro Pop",
            thickness=12,
            len=0.5,
            title_font=dict(color="#374151", size=11),
            tickfont=dict(color="#374151", size=10),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="#E2E8F0",
            borderwidth=1,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#374151"),
    )
    fig.update_traces(marker=dict(size=10, opacity=0.85))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── city list ─────────────────────────────────────────────────────────────────

heading_col, toggle_col = st.columns([5, 1])
with heading_col:
    st.markdown("### Matching Cities")
with toggle_col:
    card_view = st.radio(
        "display",
        ["Cards", "Table"],
        horizontal=True,
        label_visibility="collapsed",
        key="card_view",
    )

if display_df.empty:
    st.warning("No cities match your current filters. Try widening your ranges.")
elif card_view == "Table":
    data_cols = [c for c in [
        "state", "population", "metro_population",
        "median_household_income", "median_home_price",
        "avg_temp_f", "avg_summer_high_f", "avg_winter_low_f",
        "walkability_score_100", "dist_airport_miles",
        "dist_zoo_miles", "dist_theme_park_miles",
        "nature_score", "dist_natl_park_miles",
        "coastline_type", "dist_coast_miles", "elevation_ft",
        "seasons_count", "total_pro_teams",
        "nfl_teams", "mlb_teams", "nba_teams", "nhl_teams", "mls_teams",
    ] if c in display_df.columns]
    tbl = display_df[["city"] + data_cols].copy().reset_index(drop=True)
    tbl.insert(0, "#", range(1, len(tbl) + 1))
    tbl = tbl.set_index(["#", "city"])
    st.dataframe(
        tbl.style.format({
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
        height=600,
    )
else:
    def render_card(rank, row):
        photo_url = get_city_photo(row["city"], row["state"])
        if photo_url:
            photo_html = f'<img class="card-photo" src="{photo_url}" alt="{row["city"]}" onerror="this.parentNode.innerHTML=\'<div class=&quot;card-photo-placeholder&quot;></div>\'">'
        else:
            photo_html = '<div class="card-photo-placeholder"></div>'

        env = str(row.get("environment_type") or "").replace("_", " ").title()
        subtitle = f"{row['state']}"
        if env:
            subtitle += f" &nbsp;·&nbsp; {env}"

        temp_str = f"{row['avg_temp_f']:.0f}°F" if pd.notna(row.get("avg_temp_f")) else "N/A"
        summer_str = f"{row['avg_summer_high_f']:.0f}°" if pd.notna(row.get("avg_summer_high_f")) else ""
        winter_str = f"{row['avg_winter_low_f']:.0f}°" if pd.notna(row.get("avg_winter_low_f")) else ""
        temp_detail = f"<br><span style='font-size:11px;color:#7c8db5'>{summer_str} hi / {winter_str} lo</span>" if summer_str else ""

        stats_html = f"""
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-label">Population</div>
                <div class="stat-val">{fmt_pop(row.get('population'))}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Avg Temp</div>
                <div class="stat-val accent">{temp_str}{temp_detail}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Median Income</div>
                <div class="stat-val">{fmt_money(row.get('median_household_income'))}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Home Price</div>
                <div class="stat-val">{fmt_money(row.get('median_home_price'))}</div>
            </div>
        </div>"""

        tags_html = ""
        if pd.notna(row.get("seasons_count")):
            tags_html += f'<span class="ctag">{int(row["seasons_count"])} Seasons</span>'
        if pd.notna(row.get("metro_population")) and row.get("metro_population", 0) > 0:
            tags_html += f'<span class="ctag">Metro {fmt_pop(row["metro_population"])}</span>'
        if pd.notna(row.get("walkability_score_100")):
            tags_html += f'<span class="ctag">Walk {int(row["walkability_score_100"])}</span>'
        if pd.notna(row.get("nature_score")):
            tags_html += f'<span class="ctag">Outdoors {int(row["nature_score"])}</span>'
        if pd.notna(row.get("dist_airport_miles")):
            tags_html += f'<span class="ctag">Airport {row["dist_airport_miles"]:.0f} mi</span>'
        if pd.notna(row.get("dist_zoo_miles")):
            tags_html += f'<span class="ctag">Zoo {row["dist_zoo_miles"]:.0f} mi</span>'
        if pd.notna(row.get("dist_theme_park_miles")):
            tags_html += f'<span class="ctag">Theme Park {row["dist_theme_park_miles"]:.0f} mi</span>'
        if pd.notna(row.get("dist_natl_park_miles")):
            tags_html += f'<span class="ctag">Natl Park {row["dist_natl_park_miles"]:.0f} mi</span>'
        coast = row.get("coastline_type", "none")
        if coast == "ocean":
            tags_html += '<span class="ctag">Ocean</span>'
        elif coast == "great_lakes":
            tags_html += '<span class="ctag-lakes">Great Lakes</span>'

        total_teams = int(row.get("total_pro_teams", 0) or 0)
        if total_teams > 0:
            teams_by_league = get_teams(row["city"], row)
            teams_rows = "".join(
                f'<div><strong style="color:#c4b5fd">{lg}:</strong> {", ".join(names)}</div>'
                for lg, names in teams_by_league.items()
            ) or f"<div>{total_teams} pro team(s)</div>"
            tags_html += f"""<details class="sports-pill">
              <summary>{total_teams} Pro Team{'s' if total_teams != 1 else ''}</summary>
              <div class="sports-dropdown">{teams_rows}</div>
            </details>"""

        st.markdown(f"""
        <div class="city-card">
            {photo_html}
            <div class="card-body">
                <div class="card-header">
                    <div>
                        <div class="card-rank">#{rank}</div>
                        <div class="card-city-name">{row['city']}</div>
                        <div class="card-subtitle">{subtitle}</div>
                    </div>
                </div>
                {stats_html}
                <div class="card-tags">{tags_html}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    rows = list(display_df.iterrows())
    for row_start in range(0, len(rows), 3):
        cols = st.columns(3, gap="medium")
        for col_idx, (i, row) in enumerate(rows[row_start:row_start + 3]):
            with cols[col_idx]:
                render_card(i + 1, row)