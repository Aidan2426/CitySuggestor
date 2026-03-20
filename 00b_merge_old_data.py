"""
00b_merge_old_data.py
---------------------
Copies pre-computed columns from cities_master_old.csv (349 cities)
into cities_master.csv (1000 cities) for matching city+state pairs.

Run this AFTER 03_temperature.py finishes.
Only copies columns that are missing/null in the new file.
"""

import pandas as pd

OLD_FILE = "cities_master_old.csv"
NEW_FILE = "cities_master.csv"

# Columns to copy from old → new (everything except basic identity columns)
COPY_COLS = [
    "lat", "lon",
    "avg_temp_f", "avg_temp_c", "avg_high_f", "avg_low_f",
    "avg_summer_high_f", "avg_winter_low_f",
    "walkability_score", "walkability_score_100",
    "dist_airport_miles", "nearest_airport",
    "dist_zoo_miles", "nearest_zoo",
    "dist_theme_park_miles", "nearest_theme_park",
    "dist_natl_park_miles", "nearest_natl_park",
    "dist_natl_forest_miles", "nearest_natl_forest",
    "coastline_type", "dist_coast_miles", "elevation_ft",
    "parks_within_100mi", "nature_score",
    "dist_state_park_miles", "nearest_state_park",
    "temp_range_f", "has_winter", "has_summer", "has_spring_fall",
    "seasons_count", "seasons_score",
    "nfl_teams", "mlb_teams", "nba_teams", "nhl_teams", "mls_teams",
    "total_pro_teams", "sports_score",
    "environment_type",
]

old = pd.read_csv(OLD_FILE)
new = pd.read_csv(NEW_FILE)

print(f"Old: {len(old)} cities with {len(old.columns)} columns")
print(f"New: {len(new)} cities with {len(new.columns)} columns")

# Ensure all destination columns exist in new
for col in COPY_COLS:
    if col not in new.columns:
        new[col] = None

# Build lookup from old: (city_lower, state_upper) → row
old["_key"] = old["city"].str.strip().str.lower() + "|" + old["state"].str.strip().str.upper()
old = old.drop_duplicates(subset="_key", keep="first")
old_lookup = old.set_index("_key")

filled = 0
for idx, row in new.iterrows():
    key = str(row["city"]).strip().lower() + "|" + str(row["state"]).strip().upper()
    if key not in old_lookup.index:
        continue
    old_row = old_lookup.loc[key]
    for col in COPY_COLS:
        if col in old_lookup.columns:
            # Only fill if currently null in new
            if pd.isna(new.at[idx, col]):
                new.at[idx, col] = old_row[col]
    filled += 1

print(f"\nCopied data for {filled} matching cities")
print(f"Cities still needing data: {len(new) - filled}")

# Show coverage after merge
print("\nColumn coverage after merge:")
for col in COPY_COLS:
    if col in new.columns:
        have = new[col].notna().sum()
        print(f"  {col}: {have}/1000")

new.drop(columns=["_key"], errors="ignore", inplace=True)
new.to_csv(NEW_FILE, index=False)
print(f"\nSaved → {NEW_FILE}")
