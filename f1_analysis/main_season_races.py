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
    convert_to_timedelta_column,
    compute_gini_coefficient
)
import pandas as pd
from collections import Counter

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


def create_race_metrics_df(df_race, year, track_id, track_name):
    average_gaps = df_race['time_interval'].iloc[1:].mean()
    pos_changes = df_race['position_change'].abs().sum()
    win_driver = df_race['driver'][0]
    win_constructor = df_race['constructor'][0]

    df_race_metrics = pd.DataFrame([{
        'year': year,
        'track_id': track_id,
        'track_name': track_name,
        'average_gap': average_gaps,
        'position_change': pos_changes,
        'winner': win_driver,
        'constructor': win_constructor
    }])

    return df_race_metrics


def create_season_metrics_df(year, df_races_metrics):
    df_season = df_races_metrics.loc[df_races_metrics['year']==year]
    average_gaps = sum(df_season['average_gap']) / len(df_season)
    average_position_changes = sum(df_season['position_change']) / len(df_season)
    winner_drivers_gini = compute_gini_coefficient(list(Counter(df_season['winner']).values()))
    winner_constructors_gini = compute_gini_coefficient(list(Counter(df_season['constructor']).values()))    

    df_season_metrics = pd.DataFrame([{
        'year': year,
        'average_gaps': average_gaps,
        'average_position_change': average_position_changes,
        'winner_drivers_gini': winner_drivers_gini,
        'winner_constructors_gini': winner_constructors_gini
    }])

    return df_season_metrics


def main():
    races = get_season_races(year)
    print(f"Found {len(races)} races in {year}")

    race_gaps = []
    position_changes = []
    winner_drivers = []
    winner_constructors = []

    df_races_metrics = pd.DataFrame()

    for race in races:
        track_id = race['Circuit']['circuitId']
        track_name = race['Circuit']['circuitName']

        results = get_race_results(year, race['round'])
        df_race = create_race_df(results)
        df_race_metrics = create_race_metrics_df(df_race, year, track_id, track_name)    
        df_races_metrics = pd.concat([df_races_metrics, df_race_metrics], ignore_index=True)

    print(df_races_metrics)
    df_races_metrics.to_csv('df_races_metrics.csv')

    df_season_metrics = create_season_metrics_df(year, df_races_metrics)
    print(df_season_metrics)

    # TODO diversity of top 5
    # TODO add qualifying winner and constructors
    # TODO % point drivers season
    # TODO % point constructors season
    # TODO collect and iterate over seasons
    # TODO create dashboard for season metrics:
    #      - (season and overall) gini index over time (both)
    #      - (season) distribution of average gaps
    #      - (season) distribution of position changes
    #      - (season) pie chart of points for drivers, constructors
    #      - (overall) average season gaps over time
    #      - (overall) average season position changes over time
    #      - (overall) plot bar of % winner and constructor


if __name__ == "__main__":
    main()