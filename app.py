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

# ── page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="City Suggestor",
    page_icon="🏙️",
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
    st.markdown("# 🏙️ City Suggestor")
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
    if st.button("🔄 Reset all filters", use_container_width=True):
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

# Sort by population descending as default ranking
filtered = filtered.sort_values("metro_population", ascending=False).head(50).reset_index(drop=True)

# ── header ────────────────────────────────────────────────────────────────────

st.markdown(f"## 🏙️ City Suggestor")

city_search = st.text_input("🔍 Search for a specific city", placeholder="e.g. Austin, Denver...", key="city_search")
if city_search.strip():
    search_mask = filtered["city"].str.contains(city_search.strip(), case=False, na=False)
    filtered = filtered[search_mask].reset_index(drop=True)

st.markdown(f"**{len(filtered)}** cities match your filters (showing top 50 by metro population)")
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
            if pd.notna(row.get("avg_temp_f")):
                pills.append(f"🌡️ {row['avg_temp_f']:.0f}°F avg")
            if pd.notna(row.get("median_household_income")):
                pills.append(f"💰 ${row['median_household_income']:,.0f} income")
            if pd.notna(row.get("median_home_price")):
                pills.append(f"🏠 ${row['median_home_price']:,.0f} home")
            if pd.notna(row.get("walkability_score_100")):
                pills.append(f"🚶 {row['walkability_score_100']:.0f} walk")
            if pd.notna(row.get("dist_airport_miles")):
                pills.append(f"✈️ {row['dist_airport_miles']:.0f} mi to airport")
            if pd.notna(row.get("nature_score")):
                pills.append(f"🌲 {row['nature_score']:.0f} nature")
            if pd.notna(row.get("seasons_count")):
                pills.append(f"🍂 {int(row['seasons_count'])} seasons")
            if pd.notna(row.get("total_pro_teams")) and row.get("total_pro_teams", 0) > 0:
                pills.append(f"🏈 {int(row['total_pro_teams'])} pro teams")
            if row.get("coastline_type") in ("ocean", "great_lakes"):
                ct = "🌊 Ocean" if row["coastline_type"] == "ocean" else "🏖️ Great Lakes"
                pills.append(ct)

            pills_html = "".join([f'<span class="stat-pill">{p}</span>' for p in pills])

            pop_str = f"{row['population']:,.0f}" if pd.notna(row.get("population")) else "N/A"
            metro_str = f"{row['metro_population']:,.0f}" if pd.notna(row.get("metro_population")) else "N/A"

            st.markdown(f"""
            <div class="city-card">
                <div class="city-rank">#{rank}</div>
                <div class="city-name">{row['city']}</div>
                <div class="city-state">{row['state']} &nbsp;·&nbsp; Pop: {pop_str} &nbsp;·&nbsp; Metro: {metro_str}</div>
                <div style="margin-top:8px">{pills_html}</div>
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