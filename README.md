# movietoplaylist desc
This is a Streamlit web application that turns iconic 2000s movie quotes into Spotify playlists. By combining Google's Gemini language model with the Spotify API, the app identifies the movie and captures the "vibe" of a quote and then generates music to match the emotional tone. The app uses Google's Gemini model to analyze any 2000s movie quote and identify the film it came from (if possible), along with three keywords that describe the tone or vibe. It then automatically creates a Spotify playlist inspired by the vibes using Spotify's search and recommendation systems. It also allows users to securely log in and out of Spotify.

# requirements
Streamlit: Used for creating the web application interface.
```bash
pip install streamlit
```
Spotipy: Used for user authentication and creating playlists.
```bash
pip install spotipy
```
Requests: Used to make requests to Gemini
```bash
pip install requests
```
