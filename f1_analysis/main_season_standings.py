from f1_client.ergast_client import (
    get_available_seasons,
    get_season_races,
    get_race_results,
    get_driver_standings,
    get_constructor_standings
)

import pandas as pd


def create_driver_standings(year, standings):
    df = pd.json_normalize(
        standings,
        sep='_',
        record_prefix='',
        meta=[
            'position', 'points',
            ['Driver', 'driverId'],
            ['Driver', 'dateOfBirth'],
            ['Driver', 'nationality']
        ]
    )

    df = df.rename(columns={
        'Driver_driverId': 'driver_id',
        'Driver_dateOfBirth': 'dateOfBirth',
        'Driver_nationality': 'nationality'
    })

    df = df[['position', 'points', 'driver_id', 'dateOfBirth', 'nationality']]
    df['year']= year

    return df


def create_constructor_standings(year, standings):
    df = pd.json_normalize(
        standings,
        sep='_',
        record_prefix='',
        meta=[
            'position', 'points',
            ['Constructor', 'constructorId'],
            ['Constructor', 'nationality']
        ]
    )

    df = df.rename(columns={
        'Constructor_constructorId': 'constructor_id',
        'Constructor_nationality': 'nationality'
    })

    df = df[['position', 'points', 'constructor_id', 'nationality']]
    df['year']= year

    return df


def main():
    df_drivers_standings = pd.DataFrame()
    df_constructors_standings = pd.DataFrame()

    years = get_available_seasons()

    for year in years:
        print(year)
        driver_standings = get_driver_standings(year)
        df_driver_standings = create_driver_standings(year, driver_standings)
        df_drivers_standings = pd.concat([df_drivers_standings, df_driver_standings], ignore_index=True)

        constructor_standings = get_constructor_standings(year)      
        if constructor_standings:
            df_constructor_standings = create_constructor_standings(year, constructor_standings)
            df_constructors_standings = pd.concat([df_constructors_standings, df_constructor_standings], ignore_index=True)
        else:
            print(f"Constructor standings not available for {year}, skipping.")

    df_drivers_standings.to_csv('df_drivers_standings.csv')
    df_constructors_standings.to_csv('df_constructors_standings.csv')

if __name__ == "__main__":
    main()