from spotify_client import sp
import random
import os
import requests

def summarize_taste():
    top_artists = sp.current_user_top_artists(limit=5, time_range='medium_term')
    names = [artist['name'] for artist in top_artists['items']]
    genres = [genre for artist in top_artists['items'] for genre in artist['genres']]
    genre_freq = {}
    for g in genres:
        genre_freq[g] = genre_freq.get(g, 0) + 1
    top_genre = max(genre_freq, key=genre_freq.get)
    return {
        "summary": f"You're into artists like {', '.join(names)}. Your dominant genre is {top_genre}.",
        "top_artists": names,
        "top_genre": top_genre
    }

def chat_with_lyra(message):
    # Simple rule-based responses for demo
    if "recommend" in message.lower():
        return {"response": "What mood or genre are you in the mood for?"}
    elif "favorite" in message.lower():
        taste = summarize_taste()
        return {"response": f"Your favorite artists are: {', '.join(taste['top_artists'])}."}
    else:
        return {"response": "I'm Lyra! Ask me about your music taste or for recommendations."}

def recommend_music(mood=None, genre=None, activity=None):
    # Use Spotify recommendations endpoint for demo
    seed_genres = []
    if genre:
        seed_genres.append(genre)
    else:
        # fallback to user's top genre
        taste = summarize_taste()
        seed_genres.append(taste['top_genre'])
    recs = sp.recommendations(seed_genres=seed_genres[:1], limit=5)
    tracks = [f"{t['name']} by {t['artists'][0]['name']}" for t in recs['tracks']]
    return {"recommendations": tracks, "used_genre": seed_genres[0]}

def get_profile_visualization():
    # Return genre and artist breakdowns
    top_artists = sp.current_user_top_artists(limit=10, time_range='medium_term')
    artist_names = [artist['name'] for artist in top_artists['items']]
    genres = [genre for artist in top_artists['items'] for genre in artist['genres']]
    genre_freq = {}
    for g in genres:
        genre_freq[g] = genre_freq.get(g, 0) + 1
    return {
        "top_artists": artist_names,
        "genre_breakdown": genre_freq
    }

def get_full_spotify_profile():
    try:
        profile = sp.current_user()
        display_name = profile.get('display_name', 'Unknown')
        country = profile.get('country', 'Unknown')
        # Top artists
        top_artists = sp.current_user_top_artists(limit=5, time_range='long_term')
        artist_names = [artist['name'] for artist in top_artists['items']]
        artist_genres = [genre for artist in top_artists['items'] for genre in artist['genres']]
        # Top tracks
        top_tracks = sp.current_user_top_tracks(limit=5, time_range='long_term')
        track_names = [f"{track['name']} by {track['artists'][0]['name']}" for track in top_tracks['items']]
        # Recently played
        recent = sp.current_user_recently_played(limit=5)
        recent_tracks = [f"{item['track']['name']} by {item['track']['artists'][0]['name']}" for item in recent['items']]
        # Playlists
        playlists = sp.current_user_playlists(limit=5)
        playlist_names = [pl['name'] for pl in playlists['items']]
        # Genre frequency
        genre_freq = {}
        for g in artist_genres:
            genre_freq[g] = genre_freq.get(g, 0) + 1
        top_genres = sorted(genre_freq, key=genre_freq.get, reverse=True)[:3]
        # Compose summary
        summary = (
            f"Spotify profile for {display_name} (Country: {country}).\n"
            f"Top artists: {', '.join(artist_names)}.\n"
            f"Top genres: {', '.join(top_genres)}.\n"
            f"Top tracks: {', '.join(track_names)}.\n"
            f"Recently played: {', '.join(recent_tracks)}.\n"
            f"Playlists: {', '.join(playlist_names)}."
        )
        return summary
    except Exception as e:
        return f"(Could not fetch full Spotify profile: {e})"

def llm_respond_with_groq(message):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"response": "Groq API key not set in .env."}
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # Fetch full Spotify profile for context
    spotify_context = get_full_spotify_profile()
    system_prompt = (
        "You are Lyra, a friendly music insight assistant. "
        "The user has authorized access to their Spotify data. "
        f"Here is a summary of their Spotify profile and listening habits: {spotify_context} "
        "Answer user questions about their music taste, Spotify data, and give recommendations. "
        "If you don't know, say so."
    )
    data = {
        "model": "llama3-8b-8192",  # or another Groq-supported model
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        return {"response": result["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"response": f"Error calling Groq API: {e}"}
