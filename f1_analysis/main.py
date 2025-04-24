from f1_client.ergast_client import (
    get_available_seasons,
    get_season_races,
    get_race_results,
    get_driver_standings,
    get_constructor_standings
)
from metrics.race_metrics import (
    get_position_changes,
    get_position_interval,
    convert_to_timedelta_column
)
import pandas as pd

year = 2024
seasons = get_available_seasons()


def convert_to_timedelta(time_str):
    if time_str.startswith('+'):
        return pd.Timedelta(seconds=float(time_str[1:]))
    else:
        return pd.to_timedelta(time_str)


def main():
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
    } for r in results]).head()

    df['grid'] = df['grid'].astype(int)
    df['position'] = df['position'].astype(int)
    df['time'] = convert_to_timedelta_column(df['time'])
    df['position_change'] = get_position_changes(df['position'],df['grid'])
    df['time_interval'] = get_position_interval(df['time'])

    print(df)

if __name__ == "__main__":
    main()