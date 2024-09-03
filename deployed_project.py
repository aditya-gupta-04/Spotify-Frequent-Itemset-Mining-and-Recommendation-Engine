import streamlit as st
import pandas as pd
import pinecone
import time
import spotipy
import spotipy.oauth2 as oauth2
from spotipy.oauth2 import SpotifyOAuth,SpotifyClientCredentials
from streamlit_searchbox import st_searchbox

spotify_details = {
    'Client_id': '16d7d284a7734668ae40098fc56881e8',
    'client_secret': '25f9c87708aa441cb46d1a273a7840fd'
}

auth_manager = SpotifyClientCredentials(client_id=spotify_details['Client_id'], client_secret=spotify_details['client_secret'])
sp = spotipy.client.Spotify(auth_manager=auth_manager)

st.set_page_config(layout="wide")
st.title("Spotify Song Search")

PINECONE_API_KEY = 'd5018bce-8fb3-4c62-8527-18621cd84f7e'
PINECONE_ENV = 'gcp-starter'

pinecone.init(api_key=PINECONE_API_KEY,environment=PINECONE_ENV)
INDEX_NAME = 'vector-similarity-search-spotify'
pinecone_index = pinecone.Index(INDEX_NAME)

def display_track_info(track, audio_features1, st):
    
    st.image(track['album']['images'][0]['url'], caption="Album Cover", width=270)
    # st.image(track['album']['images'][0]['url'], caption="Album Cover", use_column_width=False)
    st.write(f"Song Name: {track['name']}")
    st.write(f"Track ID: {track['id']}")
    
    # st.write("Artists:")
    # for artist1 in track['artists']:
    #     st.write(f"{artist1['name']}")
    artist_names = ", ".join([artist1['name'] for artist1 in track['artists']])
    st.write(f"Artists: {artist_names}")
        
    st.write(f"Popularity: {track['popularity']}")
    st.write("Audio Features:")
    # audio_features1 = sp.audio_features([track['id']])[0]
    st.write(f"Danceability: {audio_features1['danceability']}")
    st.write(f"Energy: {audio_features1['energy']}")
    st.write(f"Release date: {track['album']['release_date']}")
    st.write("------")

def search_fn(search_term):
    ls = sp.search(search_term)['tracks']['items']
    return [(track['name'] + " - " + track['artists'][0]['name']+ " - " + track['album']['release_date'][:4], track['uri'].split(':')[-1]) for track in ls]


track_id = st_searchbox(search_fn)
search_button = st.button("Search")

def show_trending(trending_tracks):

    one = st.columns(4,gap="large")

    tracks = sp.tracks(trending_tracks)['tracks']
    audio_fts = sp.audio_features(trending_tracks)

    for track_id in range(0, len(trending_tracks),4):
        try:
            
            for i in range(4):
                track = tracks[track_id+i]
                # print(track)
                display_track_info(track, audio_fts[track_id+i], one[i])
            

            st.markdown("<div style='clear: both;'></div>", unsafe_allow_html=True)  # Start a new row
        except spotipy.exceptions.SpotifyException as e:
            st.error(f"Spotify API Error: {e}")
        
trending_tracks = list(pd.read_csv('trending.csv')['id'])


if search_button:

    start = time.time()
    # Query Pinecone for similar track IDs
    similar_tracks = pinecone_index.query(id=track_id, top_k=20)
    similar_tracks_ids = [match['id'] for match in similar_tracks['matches']]
    one = st.columns(4,gap="large")

    print(track_id) 
    print(len(similar_tracks_ids)) 

    tracks = sp.tracks(similar_tracks_ids)['tracks']
    audio_fts = sp.audio_features(similar_tracks_ids)

    print(f"Retrieved songs in {time.time() - start}")

    for track_id in range(0, len(similar_tracks_ids),4):
        try:
            
            for i in range(4):
                track = tracks[track_id+i]
                # print(track)
                display_track_info(track, audio_fts[track_id+i], one[i])
            

            st.markdown("<div style='clear: both;'></div>", unsafe_allow_html=True)  # Start a new row
        except spotipy.exceptions.SpotifyException as e:
            st.error(f"Spotify API Error: {e}")

else:
    st.title("Trending Today")
    show_trending(trending_tracks)
    



