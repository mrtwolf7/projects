import pandas as pd
from pathlib import Path

DATA_FILE = Path("data/sun_data.csv")


def load_data():
    df = pd.read_csv(DATA_FILE)
    df["date"] = pd.to_datetime(df["date"])
    return df


def filter_city(df, city):
    return df[df["city"] == city].copy()


def hours_to_hhmm(x):
    if pd.isna(x):
        return None
    h = int(x)
    m = int(round((x - h) * 60))
    return f"{h:02d}:{m:02d}"


def add_time_strings(df):
    df = df.copy()
    df["sunrise_str"] = df["sunrise_hours"].apply(hours_to_hhmm)
    df["sunset_str"] = df["sunset_hours"].apply(hours_to_hhmm)
    df["daylight_str"] = df["daylight_hours"].apply(hours_to_hhmm)
    return df


def aggregate_data(df, granularity):
    df = df.copy()

    if granularity == "day":
        return df

    if granularity == "week":
        df["period"] = df["date"].dt.to_period("W").apply(lambda r: r.start_time)

    if granularity == "month":
        df["period"] = df["date"].dt.to_period("M").apply(lambda r: r.start_time)

    agg = (
        df.groupby("period")
        .agg({
            "sunrise_hours": "mean",
            "sunset_hours": "mean",
            "daylight_hours": "mean"
        })
        .reset_index()
        .rename(columns={"period": "date"})
    )

    return agg