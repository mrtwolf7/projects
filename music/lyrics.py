import streamlit as st
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import pandas as pd
import time

# Download NLTK tokenizer
nltk.download('punkt_tab')
nltk.download("stopwords")

GENIUS_ID = "4ZVsr3ycdWJ5dldkNft73rCEApzdNjHBL-aSNHxWYSZ2AsSJORMp3HehN6AtoG3z"
GENIUS_API_TOKEN = "Eyz9HkjQUzzcoQ7D118jodnGiZiAW5xrfb9sUMlIBO4E8B0JXG59kFpQhzA1ELDQ"
GENIUS_SECRET = "mnhCvUhPWYtX2gAu9exfDgiLwV_ZsID66Nlj7ak8UxcJHQt7WWVl-z9dX77A1CVMtoxT6ad7Id8ok4T9yoqo9w" 
GENIUS_API_HEADERS = {"Authorization": f"Bearer {GENIUS_API_TOKEN}"}
GENIUS_SEARCH_URL = "https://api.genius.com/search"


# ----------------- Genius API Functions -----------------
def search_artist_songs(artist_name, max_songs=50):
    """Search Genius for songs by artist"""
    base_url = "https://api.genius.com"
    headers = {"Authorization": f"Bearer {GENIUS_API_TOKEN}"}
    search_url = f"{base_url}/search"

    songs = []
    page = 1

    while len(songs) < max_songs:
        params = {"q": artist_name, "per_page": 20, "page": page}
        response = requests.get(search_url, headers=headers, params=params)
        data = response.json()
        hits = data.get("response", {}).get("hits", [])
        if not hits:
            break

        for hit in hits:
            artist_in_hit = hit["result"]["primary_artist"]["name"].lower()
            if artist_name.lower() in artist_in_hit:
                songs.append({
                    "title": hit["result"]["title"],
                    "url": hit["result"]["url"]
                })
                if len(songs) >= max_songs:
                    break
        page += 1
        time.sleep(0.5)  # be gentle on the API

    return songs

def scrape_lyrics(url):
    """Scrape lyrics from Genius page, supports new HTML structure."""
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    lyrics_divs = soup.find_all("div", attrs={"data-lyrics-container": "true"})
    if not lyrics_divs:
        return None
    lyrics = "\n".join(div.get_text(separator="\n") for div in lyrics_divs)
    return lyrics

# ----------------- Lyrics Analysis -----------------
def analyze_lyrics(lyrics_text):
    tokens = word_tokenize(lyrics_text.lower())
    sentences = sent_tokenize(lyrics_text)
    
    num_words = len(tokens)
    num_sentences = len(sentences)
    vocab_size = len(set(tokens))
    avg_word_length = sum(len(w) for w in tokens) / num_words if num_words else 0
    avg_sentence_length = num_words / num_sentences if num_sentences else 0
    lexical_diversity = vocab_size / num_words if num_words else 0
    
    return {
        "num_words": num_words,
        "num_sentences": num_sentences,
        "vocab_size": vocab_size,
        "avg_word_length": round(avg_word_length, 2),
        "avg_sentence_length": round(avg_sentence_length, 2),
        "lexical_diversity": round(lexical_diversity, 3)
    }

# ----------------- Streamlit App -----------------
st.title("🎵 Lyrics Complexity Analyzer")
st.write("Analyze the lexical complexity of all songs from an artist using Genius lyrics.")

artist_name = st.text_input("Artist/Band name:", "")

max_songs = st.slider("Max number of songs to analyze:", 1, 100, 20)

if st.button("Analyze Lyrics") and artist_name:
    st.info(f"Searching for songs by {artist_name}...")
    songs = search_artist_songs(artist_name, max_songs=max_songs)
    
    if not songs:
        st.error("No songs found for this artist.")
    else:
        st.success(f"Found {len(songs)} songs! Scraping lyrics and analyzing complexity...")
        results = []

        for i, song in enumerate(songs, start=1):
            st.write(f"Processing {i}/{len(songs)}: {song['title']}")
            lyrics = scrape_lyrics(song["url"])
            if lyrics:
                stats = analyze_lyrics(lyrics)
                stats["title"] = song["title"]
                results.append(stats)
            else:
                st.warning(f"❌ Could not scrape lyrics for {song['title']}")
            time.sleep(0.5)  # gentle scraping

        if results:
            df = pd.DataFrame(results)
            st.dataframe(df.sort_values("lexical_diversity", ascending=False))

            # Simple visualizations
            st.subheader("Lexical Diversity Distribution")
            st.bar_chart(df.set_index("title")["lexical_diversity"])

            st.subheader("Average Sentence Length Distribution")
            st.bar_chart(df.set_index("title")["avg_sentence_length"])