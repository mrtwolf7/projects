import pandas as pd
import glob

files = glob.glob("snapshots/*.parquet")
df_pred = pd.concat([pd.read_parquet(f) for f in files])

df_actual = pd.read_csv("london_actual_weather.csv")
df_actual['observation_time']=df_actual['observation_time'].astype("datetime64[us]")

df_tot = df_pred.merge(df_actual, left_on='forecast_time', right_on='observation_time')
df_tot.to_csv("london_weather_full.csv", index=False)
