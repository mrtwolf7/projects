import requests
import pandas as pd
from pathlib import Path

CITIES_FILE = Path("cities.csv")

def get_lat_lon(city):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "sunrise-app"}

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    if not data:
        raise ValueError("City not found")

    return float(data[0]["lat"]), float(data[0]["lon"]), data[0]["display_name"]

def add_city(city_name):
    lat, lon, display_name = get_lat_lon(city_name)

    if CITIES_FILE.exists():
        df = pd.read_csv(CITIES_FILE)
    else:
        df = pd.DataFrame(columns=["city", "country", "lat", "lon"])

    if city_name in df["city"].values:
        print("City already exists")
        return

    country = display_name.split(",")[-1].strip()

    new_row = pd.DataFrame([{
        "city": city_name,
        "country": country,
        "lat": lat,
        "lon": lon
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CITIES_FILE, index=False)

    print(f"Added {city_name}: {lat}, {lon}")

if __name__ == "__main__":
    city = input("Enter city name: ")
    add_city(city)