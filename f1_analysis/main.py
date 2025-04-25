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


def create_race_df(results):
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
    
    return df

def main():
    races = get_season_races(year)
    print(f"Found {len(races)} races in {year}")

    race_gaps = []
    position_changes = []

    for race in races:
        results = get_race_results(year, race['round'])
        df_race = create_race_df(results)
        print(df_race)

        race_gaps.append(df_race['time_interval'].iloc[1:].mean())
        position_changes.append(df_race['position_change'].abs().sum())

    season_average_gaps = sum(race_gaps) / len(race_gaps) if race_gaps else None
    season_average_position_changes = sum(position_changes) / len(position_changes) if position_changes else None
    print(season_average_gaps)
    print(season_average_position_changes)


if __name__ == "__main__":
    main()