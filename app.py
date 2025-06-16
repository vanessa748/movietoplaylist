import streamlit as st
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Sets page configuration
st.set_page_config(page_title="Movie Quote Playlist Generator")

# API Keys and AI model
API_KEY = "AIzaSyBw718GgG6iaveThyjrTB3ESQZsrtJZJMc"
DEFAULT_GEMINI_MODEL = "models/gemini-1.5-flash-latest"

# Spotify Authentication
auth_manager = SpotifyOAuth(
    client_id="f553faa1ad24431b8800ec91336f33bc",
    client_secret="652d4ed6d5814108a54c786299a533f7",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="playlist-modify-public",
    cache_path=".spotify_cache",
    show_dialog=True  # Forces re-authentication, shows dialog to change accounts
)

# Spotify Auth errors
try:
    sp = spotipy.Spotify(auth_manager=auth_manager)
except Exception as e:
    st.error(f"Error initializing Spotify: {e}. Please ensure your Spotify API credentials are correct.")
    sp = None

# Gemini processing
def analyze_movie_quote(quote, gemini_model):
    API_VERSION = "v1beta"
    API_URL = f"https://generativelanguage.googleapis.com/{API_VERSION}/{gemini_model}:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY,
    }
    prompt = f"""
    Given the following movie quote, identify:
    1. The movie it’s from (if possible)
    2. Three keywords describing the tone or vibe of the quote

    Quote: "{quote}"

    Format your response like this:
    Movie: <movie name>
    Vibe: <keyword1>, <keyword2>, <keyword3>
    """

    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status() # handles bad responses

        result = response.json()

        # Check for the stucture of Gemini response
        if "candidates" in result and len(result["candidates"]) > 0 and \
           "content" in result["candidates"][0] and \
           "parts" in result["candidates"][0]["content"] and \
           len(result["candidates"][0]["content"]["parts"]) > 0 and \
           "text" in result["candidates"][0]["content"]["parts"][0]:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            st.error(f"Gemini API response format unexpected. Full response: {result}")
            return "Error: Unexpected Gemini API response format."

    except requests.exceptions.HTTPError as errh:
        st.error(f"HTTP Error occurred during Gemini API call: {errh}")
        st.error(f"Response content: {errh.response.text}")
        return f"Error: HTTP Error - {errh}"
    except requests.exceptions.ConnectionError as errc:
        st.error(f"Error Connecting to Gemini API: {errc}. Please check your internet connection or API endpoint.")
        return f"Error: Connection Error - {errc}"
    except requests.exceptions.Timeout as errt:
        st.error(f"Timeout Error during Gemini API call: {errt}. The request took too long to respond.")
        return f"Error: Timeout Error - {errt}"
    except requests.exceptions.RequestException as err:
        st.error(f"An unexpected request error occurred with Gemini API: {err}")
        return f"Error: An unexpected request error occurred - {err}"
    except Exception as e:
        st.error(f"An error occurred during Gemini response processing: {e}")
        return f"Error processing Gemini response: {e}"

# Streamlit app UI
st.title("˖ ִ𐙚 Movie to Playlist 𝜗𝜚 ࣪˖")
st.markdown("Enter a quote from a 2000s movie. The app will identify the movie and create a playlist based on the vibe!")

selected_gemini_model = DEFAULT_GEMINI_MODEL

if not sp:
    st.warning("You need to log in to Spotify first.") # Notifys users to login to Spotify if there is no account 
# Only available after logging into Spotify (incl main functionality)
else:
    quote_input = st.text_area("Enter a quote:", placeholder="e.g., 'Ugh, as if!'") # Instructions and placeholder text

    submit = st.button("⋆˚࿔Submit⋆˚࿔")

    if submit:
        if quote_input.strip():
            with st.spinner(f"Analyzing..."):
                try:
                    result = analyze_movie_quote(quote_input, selected_gemini_model)
                    st.success("🎟 Results below! 🎟")
                    st.write(result)

                    if "Movie:" in result and "Vibe:" in result:
                        try:
                            #Getting vibe and movie from Gemini response
                            movie_line = result.split("Movie:")[1].split("\n")[0].strip()
                            vibe_line = result.split("Vibe:")[1].strip()
                            vibes = [v.strip() for v in vibe_line.split(",")]

                            # Create playlist
                            playlist_name = f"Your Movie Playlist ˚.🎀༘⋆"
                            playlist = sp.user_playlist_create(user=sp.current_user()["id"], name=playlist_name, public=True)

                            query = " ".join(vibes)
                            results = sp.search(q=query, limit=10, type="track")
                            track_uris = [track["uri"] for track in results["tracks"]["items"]]

                            if track_uris:
                                sp.playlist_add_items(playlist["id"], track_uris)
                                playlist_url = playlist["external_urls"]["spotify"] # Creates url for playlist
                                st.markdown(f"⋆.˚ ᡣ𐭩 .𖥔˚Playlist created: [Open in Spotify]({playlist_url})") # Displays a link to the playlist
                            else:
                                st.warning("No tracks found matching the vibe keywords.")

                        except Exception as e:
                            st.error(f"Error parsing Gemini result or creating Spotify playlist: {e}")
                    else:
                        st.warning("Gemini result missing 'Movie' or 'Vibe' fields.") 

                except spotipy.exceptions.SpotifyException as se:
                    st.error(f"Spotify Error: {se}. Ensure your Spotify credentials are correct and app is authorized.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
        else:
            st.warning("Please enter a quote first.")

    # Logs user out of Spotify
    if st.button("Logout of Spotify"):
        try:
            if os.path.exists(".spotify_cache"):
                os.remove(".spotify_cache")
                st.success("You have been logged out of Spotify. Please refresh the app.")
            else:
                st.info("No active Spotify session to log out from.") # Already logged out/no Spotify account
        except Exception as e:
            st.error(f"Error logging out: {e}")
