"""
debug_wiki.py
Run this first to see exactly what the Wikipedia table looks like.
It prints the first 5 data rows so we can fix the parser.
"""
import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (compatible; CityDataBot/1.0)"}
response = requests.get(
    "https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population",
    headers=headers, timeout=15
)

soup = BeautifulSoup(response.text, "lxml")
tables = soup.find_all("table", {"class": "wikitable"})
print(f"Found {len(tables)} wikitables on the page\n")

for t_idx, table in enumerate(tables[:3]):
    rows = table.find_all("tr")
    print(f"=== Table {t_idx} — {len(rows)} rows ===")
    for row in rows[:6]:
        cells = row.find_all(["th", "td"])
        print(f"  Row has {len(cells)} cells:")
        for i, cell in enumerate(cells[:5]):
            tag = cell.name
            scope = cell.get("scope", "none")
            text = cell.get_text(separator=" ").strip()[:50]
            print(f"    [{i}] <{tag} scope={scope}> '{text}'")
    print()