import requests
import pandas as pd
from datetime import datetime, timedelta

def get_sun_data(lat, lon, date):
    url = "https://api.sunrise-sunset.org/json"
    params = {
        "lat": lat,
        "lng": lon,
        "date": date.strftime("%Y-%m-%d"),
        "formatted": 0
    }

    r = requests.get(url, params=params)
    data = r.json()["results"]

    return {
        "sunrise": data["sunrise"],
        "sunset": data["sunset"],
        "day_length": data["day_length"]
    }

cities = pd.read_csv("cities.csv")

start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 12, 31)

rows = []

for _, row in cities.iterrows():
    city = row["city"]
    lat = row["lat"]
    lon = row["lon"]

    date = start_date
    while date <= end_date:
        sun = get_sun_data(lat, lon, date)

        rows.append({
            "date": date,
            "city": city,
            "sunrise": sun["sunrise"],
            "sunset": sun["sunset"],
            "day_length": sun["day_length"]
        })

        date += timedelta(days=1)

df = pd.DataFrame(rows)
df.to_csv("output_data/sun_data.csv", index=False)