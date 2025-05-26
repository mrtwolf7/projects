import requests
import pandas as pd

BASE_URL = "https://ergast.com/api/f1"


def get_available_seasons():
    url = "https://ergast.com/api/f1/seasons.json?limit=1000"
    response = requests.get(url)
    data = response.json()
    seasons = [int(s['season']) for s in data['MRData']['SeasonTable']['Seasons']]
    return seasons

def get_season_races(year):
    url = f"{BASE_URL}/{year}.json"
    response = requests.get(url)
    data = response.json()
    races = data['MRData']['RaceTable']['Races']
    return races

def get_race_results(year, round_number):
    url = f"{BASE_URL}/{year}/{round_number}/results.json"
    response = requests.get(url)
    data = response.json()
    results = data['MRData']['RaceTable']['Races'][0]['Results']
    return results

def get_driver_standings(year):
    url = f"{BASE_URL}/{year}/driverStandings.json"
    response = requests.get(url)
    data = response.json()
    standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
    return standings

def get_constructor_standings(year):
    url = f"{BASE_URL}/{year}/constructorStandings.json"
    response = requests.get(url)
    data = response.json()

    standings_lists = data['MRData']['StandingsTable']['StandingsLists']
    if not standings_lists:
        print(f"No constructor standings for year {year}")
        return []

    return standings_lists[0]['ConstructorStandings']

    url = f"{BASE_URL}/{year}/constructorStandings.json"
    response = requests.get(url)
    data = response.json()
    standings = data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
    return standings