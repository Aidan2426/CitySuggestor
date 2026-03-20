"""
00_init_cities.py
Converts newdata.csv (tab-separated, "City, ST" format) into a clean
cities_master.csv with separate city / state / population columns.
Run this FIRST before any other pipeline scripts.
"""

import pandas as pd

INPUT  = "newdata.csv"
OUTPUT = "cities_master.csv"

# ── read tab-separated file ────────────────────────────────────────────────
df = pd.read_csv(INPUT, sep="\t")
print(f"Loaded {len(df)} rows from {INPUT}")
print(df.head(3))

# ── split "New York, NY" → city="New York", state="NY" ────────────────────
split = df["City"].str.rsplit(",", n=1, expand=True)
df["city"]  = split[0].str.strip()
df["state"] = split[1].str.strip()

# ── keep only what we need ─────────────────────────────────────────────────
out = pd.DataFrame({
    "city":       df["city"],
    "state":      df["state"],
    "population": df["Population"],
})

out.to_csv(OUTPUT, index=False)
print(f"\nSaved {len(out)} cities to {OUTPUT}")
print(out.head(10).to_string(index=False))
print("\nState sample:", out["state"].value_counts().head(10).to_dict())
