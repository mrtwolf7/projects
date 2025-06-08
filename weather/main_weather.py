import pandas as pd
from dateutil.easter import easter
from meteostat import Daily, Point
from datetime import datetime, timedelta, date


# Define Rome coordinates
rome = Point(41.9028, 12.4964, 21)


def get_easter_week(year):
    em = easter(year) + timedelta(days=1)
    start_date = datetime.combine(em - timedelta(days=4), datetime.min.time())  # Thursday before
    end_date = datetime.combine(em + timedelta(days=3), datetime.min.time())    # Thursday after
    
    return start_date, end_date, em

def main():
    records = []
    cities_df = pd.read_csv("cities.csv")

    for _, row in cities_df.iterrows():
        city_name = row['city']
        location = Point(row['latitude'], row['longitude'], row['elevation'])

        for year in range(1995, 2025):

            start_date, end_date, em = get_easter_week(year)
            try:
                data = Daily(location, start_date, end_date).fetch()
            except Exception as e:
                print(f"Error fetching data for {city_name}, {year}: {e}")
                continue

            for day, row in data.iterrows():
                records.append({
                    "city": city_name,
                    "year": year,
                    "day": day.date(),
                    "easter_monday": (day.date() == em),
                    "rain_mm": row['prcp'] if not pd.isna(row['prcp']) else 0,
                    "temperature_c": row['tavg'] if not pd.isna(row['tavg']) else None
                })

    df = pd.DataFrame(records)
    df.to_csv('weather.csv')

    # TODO:
    # (overall):
    # - cities with most rainy easter mondays (count)
    # - average temp in cities
    # - easter mondays vs normal days:
    #    - cities with most rainy days compared to normal days (count)
    #    - cities with colder/hotter easter mondays than normal days
    #    - average diff in rain between easter mondays and normal
    #    - average diff in temp between easter mondays and mormal
    # 
    # 

if __name__ == "__main__":
    main()
