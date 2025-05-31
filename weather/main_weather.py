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

    for year in range(1995, 2025):

        start_date, end_date, em = get_easter_week(year)
        data = Daily(rome, start_date, end_date).fetch()

        for day, row in data.iterrows():
            records.append({
                "city": "Rome",
                "year": year,
                "day": day.date(),
                "easter_monday": (day.date() == em),
                "rain_mm": row['prcp'] if not pd.isna(row['prcp']) else 0,
                "temperature_c": row['tavg'] if not pd.isna(row['tavg']) else None
            })

    df = pd.DataFrame(records)
    df.to_csv('weather.csv')
    df.head(20)

if __name__ == "__main__":
    main()
