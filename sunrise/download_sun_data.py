import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import time

CITIES_FILE = Path("cities.csv")
OUTPUT_FILE = Path("data/sun_data.csv")

YEAR = 2026
API_URL = "https://api.sunrise-sunset.org/json"


# -------------------------
# Helpers
# -------------------------
def seconds_to_hours(seconds):
    return seconds / 3600


def time_str_to_hours(t):
    h, m, s = map(int, t.split(":"))
    return h + m/60 + s/3600


def extract_time_from_iso(iso_string):
    return datetime.fromisoformat(iso_string).strftime("%H:%M:%S")


def get_sun_data(lat, lon, date):
    params = {
        "lat": lat,
        "lng": lon,
        "date": date.strftime("%Y-%m-%d"),
        "formatted": 0
    }

    response = requests.get(API_URL, params=params)
    data = response.json()["results"]

    sunrise = extract_time_from_iso(data["sunrise"])
    sunset = extract_time_from_iso(data["sunset"])
    day_length_seconds = int(data["day_length"])

    return sunrise, sunset, day_length_seconds


# -------------------------
# Main
# -------------------------
def main():
    cities = pd.read_csv(CITIES_FILE)

    start_date = datetime(YEAR, 1, 1)
    end_date = datetime(YEAR, 12, 31)
    all_dates = pd.date_range(start_date, end_date)

    # Load existing data if exists
    if OUTPUT_FILE.exists():
        existing_df = pd.read_csv(OUTPUT_FILE, parse_dates=["date"])
    else:
        existing_df = pd.DataFrame()

    rows = []

    for _, city_row in cities.iterrows():
        city = city_row["city"]
        country = city_row["country"]
        lat = city_row["lat"]
        lon = city_row["lon"]

        print(f"\nProcessing {city}...")

        # Find already downloaded dates for this city
        if not existing_df.empty and city in existing_df["city"].unique():
            existing_dates = existing_df[existing_df["city"] == city]["date"]
            missing_dates = all_dates.difference(existing_dates)
        else:
            missing_dates = all_dates

        print(f"Missing days to download: {len(missing_dates)}")

        for date in missing_dates:
            try:
                sunrise, sunset, day_length_sec = get_sun_data(lat, lon, date)

                rows.append({
                    "date": date,
                    "city": city,
                    "country": country,
                    "lat": lat,
                    "lon": lon,
                    "sunrise": sunrise,
                    "sunset": sunset,
                    "day_length_sec": day_length_sec
                })

                time.sleep(0.15)

            except Exception as e:
                print(f"Error for {city} on {date}: {e}")

    # If no new data, exit
    if not rows:
        print("\nNo new data to download.")
        return

    new_df = pd.DataFrame(rows)

    # -------------------------
    # Feature Engineering
    # -------------------------
    new_df["date"] = pd.to_datetime(new_df["date"])
    new_df["day_of_year"] = new_df["date"].dt.dayofyear

    new_df["sunrise_hours"] = new_df["sunrise"].apply(time_str_to_hours)
    new_df["sunset_hours"] = new_df["sunset"].apply(time_str_to_hours)
    new_df["daylight_hours"] = new_df["day_length_sec"].apply(seconds_to_hours)

    new_df = new_df.sort_values(["city", "date"])
    new_df["daylight_change"] = new_df.groupby("city")["daylight_hours"].diff()
    new_df["solar_midpoint"] = (new_df["sunrise_hours"] + new_df["sunset_hours"]) / 2

    new_df["daylight_category"] = pd.cut(
        new_df["daylight_hours"],
        bins=[0, 8, 10, 12, 14, 16, 24],
        labels=["Very Short", "Short", "Medium", "Long", "Very Long", "Extreme"]
    )

    # Merge with existing data
    if not existing_df.empty:
        final_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        final_df = new_df

    final_df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nAdded {len(new_df)} new rows.")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()