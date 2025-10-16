import os
import requests
import pandas as pd
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials


# ==========
# SETUP
# ==========
CLIENT_ID = "3f057d6a94ea4c99bcf2cb4b308f81a4"
CLIENT_SECRET = "75f6072f998c46d98603a73216b9d7ea"
REDIRECT_URI = "http://127.0.0.1:8888/callback"



sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-library-read",  # minimal scope is fine
    open_browser=True,
))

# 🎸 Search artist
artist_name = "The Rolling Stones"  # change to Beatles etc.
results = sp.search(q=artist_name, type="artist", limit=1)
artist = results["artists"]["items"][0]
artist_id = artist["id"]
print(f"🎸 Found {artist['name']} with ID: {artist_id}")

# 📀 Collect albums
albums = []
results = sp.artist_albums(artist_id, album_type="album", limit=50)
albums.extend(results["items"])
while results["next"]:
    results = sp.next(results)
    albums.extend(results["items"])

print(f"💿 Found {len(albums)} albums.")

# 🎵 Collect tracks
tracks = []
for album in albums:
    results = sp.album_tracks(album["id"])
    for t in results["items"]:
        tracks.append({
            "track_id": t["id"],
            "track_name": t["name"],
            "album_name": album["name"],
            "release_date": album["release_date"],
        })
print(f"🎵 Collected {len(tracks)} tracks.")

# 🎚 Fetch audio features in proper batches (<=100)
all_features = []
batch_size = 10
for i in range(0, len(tracks), batch_size):
    batch = [t["track_id"] for t in tracks[i:i+batch_size] if t["track_id"]]
    try:
        features = sp.audio_features(batch)
        all_features.extend([f for f in features if f])  # filter None
        print(f"✅ Got features for batch {i//batch_size} ({len(batch)} tracks)")
    except Exception as e:
        print(f"⚠️ Failed batch {i//batch_size}: {e}")
    time.sleep(0.2)

# 🧹 Build DataFrame
df_meta = pd.DataFrame(tracks)
df_feat = pd.DataFrame(all_features)
df = df_meta.merge(df_feat, left_on="track_id", right_on="id", how="left")

print(f"✅ Final dataset: {df.shape[0]} tracks × {df.shape[1]} columns")
df.to_csv("audio_features.csv", index=False)
print("💾 Saved to audio_features.csv")