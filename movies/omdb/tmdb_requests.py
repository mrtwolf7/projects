import requests
import pandas as pd

TMDB_API_KEY = "68df11add6e029abce7aad3633323158"

def discover_movies(page):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "sort_by": "popularity.desc",
        "vote_count.gte": 400,
        "page": page
    }
    response = requests.get(url, params=params)
    data = response.json()
    return [m["id"] for m in data.get("results", [])]


def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY}
    r = requests.get(url, params=params)
    return r.json()


def main():
    movies = []
    for p in range(1, 2):
        movies += discover_movies(p)
    print(movies)
    print(f"Fetched {len(movies)} movies from TMDb")
    for movie in movies:
        movie_details = get_movie_details(movie)
        print(movie_details)      



if __name__ == "__main__":
    main()
