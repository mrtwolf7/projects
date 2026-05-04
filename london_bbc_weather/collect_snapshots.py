import requests
import pandas as pd
from datetime import datetime
import os

os.makedirs("london_bbc_weather/snapshots", exist_ok=True)

URL = "https://weather-broker-cdn.api.bbci.co.uk/en/forecast/aggregated/2643743"

def fetch_snapshot():
    r = requests.get(URL)
    data = r.json()
    #print(data["forecasts"][0])

    now = datetime.utcnow()
    rows = []
    
    for day in data["forecasts"]:
        for rep in day["detailed"]["reports"]:
            forecast_time = pd.to_datetime(rep["localDate"] + " " + rep["timeslot"])
            
            rows.append({
               "scrape_time": now,
               "forecast_time": forecast_time,
               "temp": rep.get("temperatureC"),
               "temp_perc": rep.get("feelsLikeTemperatureC"),
               "rain_prob": rep.get("precipitationProbabilityInPercent"),
               "condition": rep.get("weatherTypeText"),
               "wind_speed": rep.get("windSpeedKph"),
               "wind_direction": rep.get("windDirectionAbbreviation"),
               "humidity": rep.get("humidity"),
               "pressure": rep.get("pressure")
            })
    
    return pd.DataFrame(rows)

df = fetch_snapshot()
df["horizon_hours"] = (df["forecast_time"] - df["scrape_time"]).dt.total_seconds() / 3600
timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
df.to_parquet(f"london_bbc_weather/snapshots/{timestamp}.parquet")