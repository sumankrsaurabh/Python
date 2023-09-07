from flask import Flask, request, jsonify, render_template
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import aiohttp
import re
import asyncio
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from Ids import *

app = Flask(__name__)

# Spotify API credentials
SPOTIPY_REDIRECT_URI = 'http://localhost:5500/callback'

# Initialize the Spotify client with the necessary scope
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="playlist-read-private"
))


async def extract_playlist_id(url):
    parts = url.split("/")
    return parts[-1]


@retry(
    stop=stop_after_attempt(3),  # Number of retries
    wait=wait_fixed(1),  # Retry every 1 second
    retry=retry_if_exception_type(aiohttp.ClientError)  # Retry on client errors
)
async def get_matching_youtube_url(session, query):
    url = "https://www.youtube.com/results?search_query=" + query
    async with session.get(url) as response:
        if response.status == 200:
            response_text = await response.text()
            video_ids = re.findall(r'watch\?v=(\S{11})', response_text)
            if video_ids:
                youtube_url = "https://www.youtube.com/watch?v=" + video_ids[0]
                return youtube_url
    return None


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/search_spotify_and_get_youtube_links", methods=["GET"])
async def search_spotify_and_get_youtube_links():
    playlist_url = request.args.get("playlist_url")

    playlist_id = await extract_playlist_id(playlist_url)

    if not playlist_id:
        return jsonify({"error": "Invalid Spotify playlist URL"})

    try:
        playlist = await asyncio.to_thread(sp.playlist_tracks, playlist_id)
    except spotipy.exceptions.SpotifyException as e:
        return jsonify({"error": f"Error accessing Spotify playlist: {str(e)}"})

    songs = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for track in playlist['items']:
            song_name = track['track']['name']
            artist_name = track['track']['artists'][0]['name']
            search_query = f'{song_name} {artist_name} '
            task = asyncio.create_task(get_matching_youtube_url(session, search_query))
            tasks.append(task)

        youtube_urls = await asyncio.gather(*tasks)

    for track, youtube_url in zip(playlist['items'], youtube_urls):
        song_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        if youtube_url:
            songs.append({"name": song_name, "artist": artist_name, "youtube_url": youtube_url})

    print(jsonify({"songs": songs}))
    return jsonify({"songs": songs})


if __name__ == "__main__":
    app.run(debug=True)
