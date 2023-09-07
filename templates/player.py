import tkinter as tk
from tkinter import ttk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import webbrowser
from Ids import *

# Spotify API credentials
SPOTIPY_REDIRECT_URI = 'http://localhost:5500/callback'

# Initialize the Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-library-read user-library-modify user-read-playback-state user-modify-playback-state"
))

# Function to play a Spotify track
def play_spotify_track():
    track_uri = track_uri_entry.get()
    try:
        sp.start_playback(device_id=device_id, uris=[track_uri])
        status_label.config(text="Playing")
    except SpotifyException as e:
        status_label.config(text="Error: " + str(e))

# Function to open a Spotify track in the user's default web browser
def open_spotify_track():
    track_uri = track_uri_entry.get()
    webbrowser.open(track_uri)

# Function to retrieve the active Spotify playback device and set device_id
def get_active_device():
    global device_id
    devices = sp.devices()
    active_device = next((device for device in devices['devices'] if device['is_active']), None)
    if active_device:
        device_id = active_device['id']
        print(f"Active Device ID: {device_id}")
    else:
        device_id = None

# Get the active Spotify playback device on startup
device_id = None
get_active_device()

# Create the main GUI window
root = tk.Tk()
root.title("Spotify Player")

# Create and pack a frame for input elements
input_frame = ttk.Frame(root)
input_frame.pack(padx=20, pady=20)

# Create and pack input label and entry for Spotify track URI
track_uri_label = ttk.Label(input_frame, text="Spotify Track URI:")
track_uri_label.grid(row=0, column=0, padx=5, pady=5)
track_uri_entry = ttk.Entry(input_frame, width=40)
track_uri_entry.grid(row=0, column=1, padx=5, pady=5)

# Create and pack buttons for playing and opening the track
play_button = ttk.Button(input_frame, text="Play", command=play_spotify_track)
play_button.grid(row=1, column=0, padx=5, pady=5)
open_button = ttk.Button(input_frame, text="Open in Spotify", command=open_spotify_track)
open_button.grid(row=1, column=1, padx=5, pady=5)

# Create and pack a label for status messages
status_label = ttk.Label(root, text="")
status_label.pack(pady=10)

# Button to refresh the active device
refresh_device_button = ttk.Button(root, text="Refresh Device", command=get_active_device)
refresh_device_button.pack(pady=10)

# Run the GUI main loop
root.mainloop()
