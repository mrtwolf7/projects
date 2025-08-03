import requests
import time
import pandas as pd
from bs4 import BeautifulSoup


API_KEY = '8a70b208'
BASE_URL = 'http://www.omdbapi.com/'
imdb_top250 = 'IMDB_top250.csv'


def get_imdb_top250(imdb_top250):
    df_imdb_top250 = pd.read_csv(imdb_top250)
    movies = list(set(df_imdb_top250['name']))
    return movies


def get_movie_data(title):
    params = {'apikey': API_KEY, 't': title}
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    return None


def main():
    results = []
    movie_titles = get_imdb_top250(imdb_top250)
    print(f"Collected {len(movie_titles)} movie titles.")

    for title in movie_titles:
        data = get_movie_data(title)
        if data and data.get('Response') == 'True' and 'BoxOffice' in data:
            results.append(data)
        else:
            print(f"Skipped: {title}")
        time.sleep(0.25)  # Avoid rate limiting

    # Save to DataFrame
    df = pd.DataFrame(results)
    df.to_csv("omdb_movie_data.csv", index=False)


if __name__ == "__main__":
    main()
