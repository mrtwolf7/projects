import asyncio
import aiohttp
import pandas as pd
import sqlite3
import json
import re
import time
from rapidfuzz import fuzz
import numpy as np

# =========================
# CONFIG
# =========================
API_KEY = "68df11add6e029abce7aad3633323158"
INPUT_CSV = "movie-budgets.csv"
OUTPUT_CSV = "movie-budgets-enriched.csv"
CACHE_DB = "movie_cache.db"

CONCURRENCY = 8
BATCH_SIZE = 200
SCORE_THRESHOLD = 60

# =========================
# DB CACHE
# =========================
conn = sqlite3.connect(CACHE_DB)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")
conn.commit()


def cache_get(key):
    cur.execute("SELECT value FROM cache WHERE key=?", (key,))
    row = cur.fetchone()
    return json.loads(row[0]) if row else None


def cache_set(key, value):
    cur.execute(
        "INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?)",
        (key, json.dumps(value))
    )
    conn.commit()


# =========================
# CLEANING
# =========================
def clean_title(t):
    if pd.isna(t):
        return ""
    t = t.lower()
    t = re.sub(r"\(.*?\)", "", t)
    t = re.sub(r"[^a-z0-9 ]", "", t)
    return t.strip()


# =========================
# SCORING
# =========================
def score(row, candidate):
    s = 0

    # title similarity
    s += fuzz.token_set_ratio(
        row['title_clean'],
        candidate['title'].lower()
    ) * 0.5

    # year
    if candidate.get("release_date"):
        try:
            cand_year = int(candidate["release_date"][:4])
            diff = abs(row['year'] - cand_year)
            s += max(0, 20 - diff * 5)
        except:
            pass

    return s


# =========================
# API CALLS
# =========================
BASE_URL = "https://api.themoviedb.org/3"


async def search_movie(session, title, year):
    key = f"search::{title}::{year}"
    cached = cache_get(key)
    if cached:
        return cached

    url = f"{BASE_URL}/search/movie"
    params = {"api_key": API_KEY, "query": title, "year": year}

    for _ in range(3):
        try:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                cache_set(key, data)
                return data
        except:
            await asyncio.sleep(1)

    return {}


async def get_details(session, movie_id):
    key = f"details::{movie_id}"
    cached = cache_get(key)
    if cached:
        return cached

    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": API_KEY,
        "append_to_response": "credits"
    }

    for _ in range(3):
        try:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                cache_set(key, data)
                return data
        except:
            await asyncio.sleep(1)

    return {}


# =========================
# PROCESS ROW
# =========================


async def process_row(session, row, semaphore):    
    if (
        pd.notna(row.get("runtime")) and
        pd.notna(row.get("directors")) and
        pd.notna(row.get("actors")) and
        pd.notna(row.get("production_company"))
    ):
        return None  # skip already complete

    async with semaphore:
        results = await search_movie(session, row['title'], row['year'])

    candidates = results.get("results", [])[:5]

    if not candidates:
        return {"match": False}

    best = max(candidates, key=lambda c: score(row, c))
    best_score = score(row, best)

    if best_score < SCORE_THRESHOLD:
        return {"match": False}

    async with semaphore:
        details = await get_details(session, best['id'])

    if not details:
        return {"match": False}

    return {
        "match": True,
        "runtime": details.get("runtime"),
        "directors": [
            c['name'] for c in details.get('credits', {}).get('crew', [])
            if c.get('job') == 'Director'
        ],
        "actors": [
            a['name'] for a in details.get('credits', {}).get('cast', [])[:5]
        ],
        "production_company": [
            c['name'] for c in details.get('production_companies', [])
        ]
    }


# =========================
# PIPELINE
# =========================
async def run_batch(df_chunk):
    semaphore = asyncio.Semaphore(CONCURRENCY)

    async with aiohttp.ClientSession() as session:
        tasks = [
            process_row(session, row, semaphore)
            for _, row in df_chunk.iterrows()
        ]

        return await asyncio.gather(*tasks)


# =========================
# MAIN
# =========================
def main():
    df = pd.read_csv(INPUT_CSV)
    #df = df.head(500)

    # normalize columns (adjust if needed)
    df['title_clean'] = df['title'].apply(clean_title)
    df['year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year
    df['month'] = pd.to_datetime(df['release_date'], errors='coerce').dt.month
    df['runtime'] = df['runtime'].str.replace(' minutes', '', regex=False)
    df['production_budget'] = pd.to_numeric(
        df['production_budget']
            .str.replace('$', '', regex=False)
            .str.replace(',', '', regex=False),
        errors='coerce')
    df['domestic_gross'] = pd.to_numeric(
        df['domestic_gross']
            .str.replace('$', '', regex=False)
            .str.replace(',', '', regex=False),
        errors='coerce')
    df['worldwide_gross'] = pd.to_numeric(
        df['worldwide_gross']
            .str.replace('$', '', regex=False)
            .str.replace(',', '', regex=False),
        errors='coerce')
    df['opening_theater_count'] = pd.to_numeric(
        df['opening_theater_count']
            .str.replace(',', '', regex=False),
        errors='coerce')
    df['max_theater_count'] = pd.to_numeric(
        df['max_theater_count']
            .str.replace(',', '', regex=False),
        errors='coerce')
    df['avg_run_per_theater'] = pd.to_numeric(
        df['avg_run_per_theater']
            .str.replace(' weeks', '', regex=False),
        errors='coerce')
    df['genre'] = df['genre'].str.replace(
        r'All Time (Domestic|International) Box Office for Comedy Movies.*',
        'Comedy',
        regex=True
    )
    df['story_source'] = df['story_source'].str.replace(
        r'All Time (Domestic|International) Box Office for Remake Movies.*',
        'Remake',
        regex=True
    )
    df['production_method'] = df['production_method'].str.replace(
        r'All Time (Domestic|International) Box Office for Digital Animation Movies.*',
        'Digital Animation',
        regex=True
    )
    df['creative_type'] = df['creative_type'].str.replace(
        r'All Time (Domestic|International) Box Office for Super Hero Movies.*',
        'Super Hero',
        regex=True
    )


    df = df.rename(columns={"avg_run_per_theater": "avg_run_per_theater_weeks"})

    results_all = []

    chunks = [
    df.iloc[i:i+BATCH_SIZE]
    for i in range(0, len(df), BATCH_SIZE)
]

    for i, chunk in enumerate(chunks):

        print(f"\nProcessing batch {i+1}")

        results = asyncio.run(run_batch(chunk))

        for idx, res in zip(chunk.index, results):
            if not res or not res.get("match"):
                continue

            if pd.isna(df.at[idx, 'runtime']):
                df.at[idx, 'runtime'] = res['runtime']

            if pd.isna(df.at[idx, 'directors']):
                df.at[idx, 'directors'] = ", ".join(res['directors'])

            if pd.isna(df.at[idx, 'actors']):
                df.at[idx, 'actors'] = ", ".join(res['actors'])

            if pd.isna(df.at[idx, 'production_company']):
                df.at[idx, 'production_company'] = ", ".join(res['production_company'])

        df.to_csv(OUTPUT_CSV, index=False)
        print(f"Saved progress after batch {i+1}")

    print("\nDone!")


if __name__ == "__main__":
    main()