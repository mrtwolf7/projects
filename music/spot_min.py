import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "3f057d6a94ea4c99bcf2cb4b308f81a4"
CLIENT_SECRET = "75f6072f998c46d98603a73216b9d7ea"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-read-email",   # any harmless user scope
    open_browser=True
))

print("👤 User profile:")
print(sp.me())  # Should show your Spotify account details

track_id = "3n3Ppam7vgaVa1iaRUc9Lp"  # Mr. Brightside
features = sp.audio_features([track_id])[0]

print("🎵 Audio features:")
print(features)
