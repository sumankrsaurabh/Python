from Ids import *
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import re
import webbrowser  # Import the webbrowser module

# Spotify API credentials
SPOTIPY_REDIRECT_URI = 'http://localhost:5500/callback'

# Initialize the Spotify client with the necessary scope
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="playlist-read-private"
))


# Function to extract the playlist ID from the URL
def extract_playlist_id(url):
    parts = url.split("/")
    return parts[-1]


# Function to search for songs in the Spotify playlist and open the matching YouTube link in the browser
def search_spotify_and_play_matching_youtube_song():
    playlist_url = input('Enter Spotify Playlist URL: ')
    print(f'Entered Spotify Playlist URL: {playlist_url}')  # Print the entered URL
    playlist_id = extract_playlist_id(playlist_url)

    if not playlist_id:
        print('Invalid Spotify playlist URL. Please provide a valid URL.')
        return

    try:
        playlist = sp.playlist_tracks(playlist_id)
        print(f'Fetched {len(playlist["items"])} tracks from Spotify playlist.')  # Print the number of tracks fetched
    except spotipy.exceptions.SpotifyException as e:
        print(f'Error accessing Spotify playlist: {str(e)}')
        return

    for track in playlist['items']:
        song_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        search_query = f'{song_name} {artist_name} official music video'

        # Use pytube to search for the matching YouTube video based on the query
        youtube_url = get_matching_youtube_url(search_query)

        if youtube_url:
            print(f'Spotify Song: {song_name} - {artist_name}')
            print(f'Matching YouTube URL: {youtube_url}')  # Print song details and matching YouTube URL
            print('\n')

            # Open the matching YouTube URL in the default web browser to play the song
            webbrowser.open(youtube_url)


# Function to get the matching YouTube URL based on the search query using pytube
def get_matching_youtube_url(query):
    url = "https://www.youtube.com/results?search_query=" + query
    response = requests.get(url)
    if response.status_code == 200:
        video_ids = re.findall(r'watch\?v=(\S{11})', response.text)
        if video_ids:
            # Check if the first video is an official video (you can add more checks if needed)
            youtube_url = "https://www.youtube.com/watch?v=" + video_ids[0]
            return youtube_url
    return None


# Run the function to search for Spotify songs and open the matching YouTube video to play it
search_spotify_and_play_matching_youtube_song()
