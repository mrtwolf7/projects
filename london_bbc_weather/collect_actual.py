import requests
import pandas as pd

LATITUDE = 51.5074
LONGITUDE = -0.1278

START_DATE = "2026-05-04"
END_DATE = "2026-06-29"

URL = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "start_date": START_DATE,
    "end_date": END_DATE,
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "surface_pressure",
        "wind_speed_10m",
        "wind_direction_10m"
    ],
    "timezone": "Europe/London"
}

response = requests.get(URL, params=params)
response.raise_for_status()

data = response.json()["hourly"]

df = pd.DataFrame(data)

df.rename(columns={
    "time": "observation_time",
    "temperature_2m": "actual_temp",
    "relative_humidity_2m": "actual_humidity",
    "precipitation": "actual_precipitation",
    "surface_pressure": "actual_pressure",
    "wind_speed_10m": "actual_wind_speed",
    "wind_direction_10m": "actual_wind_direction"
}, inplace=True)

df["observation_time"] = pd.to_datetime(df["observation_time"])

df.to_csv("london_actual_weather.csv", index=False)

print(df.head())
print(f"\nDownloaded {len(df)} hourly observations.")