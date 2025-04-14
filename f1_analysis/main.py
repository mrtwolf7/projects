from f1_client.ergast_client import (
    get_available_seasons,
    get_season_races,
    get_race_results,
    get_driver_standings,
    get_constructor_standings
)
import pandas as pd

year = 2024
seasons = get_available_seasons()

# Get race list
races = get_season_races(year)
print(f"Found {len(races)} races in {year}")

# Grab and display one race result
results = get_race_results(year, 1)
df = pd.DataFrame([{
    'position': r['position'],
    'driver': f"{r['Driver']['givenName']} {r['Driver']['familyName']}",
    'constructor': r['Constructor']['name'],
    'grid': r['grid'],
    'time': r['Time']['time'] if 'Time' in r else None
} for r in results])

print(df.head())