import pandas as pd
import requests
from datetime import datetime, timedelta
from pathlib import Path
import time

CITIES_FILE = Path("cities.csv")
OUTPUT_FILE = Path("data/sun_data.csv")
YEAR = 2026


def utc_to_local(utc_time_str, lon):
    offset_hours = lon / 15

    t = datetime.strptime(utc_time_str, "%H:%M:%S")
    total_seconds = t.hour * 3600 + t.minute * 60 + t.second
    total_seconds += offset_hours * 3600
    total_seconds = total_seconds % (24 * 3600)

    h = int(total_seconds // 3600)
    m = int((total_seconds % 3600) // 60)
    s = int(total_seconds % 60)

    return h, m, s


def hms_to_decimal(h, m, s):
    return h + m/60 + s/3600


def get_sun_data(lat, lon, year=YEAR):
    url = "https://api.sunrise-sunset.org/json"

    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)

    rows = []

    date = start_date
    while date <= end_date:
        params = {
            "lat": lat,
            "lng": lon,
            "date": date.strftime("%Y-%m-%d"),
            "formatted": 0
        }

        r = requests.get(url, params=params)
        data = r.json()["results"]

        sunrise_utc = data["sunrise"][11:19]
        sunset_utc = data["sunset"][11:19]

        sr_h, sr_m, sr_s = utc_to_local(sunrise_utc, lon)
        ss_h, ss_m, ss_s = utc_to_local(sunset_utc, lon)

        sunrise_hours = hms_to_decimal(sr_h, sr_m, sr_s)
        sunset_hours = hms_to_decimal(ss_h, ss_m, ss_s)

        daylight_hours = sunset_hours - sunrise_hours
        if daylight_hours < 0:
            daylight_hours += 24

        rows.append([
            date.strftime("%Y-%m-%d"),
            sunrise_hours,
            sunset_hours,
            daylight_hours
        ])

        date += timedelta(days=1)
        time.sleep(0.2)

    df = pd.DataFrame(rows, columns=[
        "date",
        "sunrise_hours",
        "sunset_hours",
        "daylight_hours"
    ])

    return df


def main():
    cities = pd.read_csv(CITIES_FILE)

    if OUTPUT_FILE.exists():
        existing = pd.read_csv(OUTPUT_FILE)
    else:
        existing = pd.DataFrame()

    all_data = []

    for _, row in cities.iterrows():
        city = row["city"]

        if not existing.empty and city in existing["city"].unique():
            print(f"Skipping {city} (already downloaded)")
            continue

        print(f"Downloading data for {city}...")

        df = get_sun_data(row["lat"], row["lon"])
        df["city"] = city

        all_data.append(df)

    if all_data:
        new_data = pd.concat(all_data)

        if not existing.empty:
            combined = pd.concat([existing, new_data])
        else:
            combined = new_data

        combined.to_csv(OUTPUT_FILE, index=False)
        print("Saved to data/sun_data.csv")
    else:
        print("No new cities to download.")


if __name__ == "__main__":
    main()