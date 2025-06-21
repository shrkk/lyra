from spotify_client import sp
import random
import os
import requests
import re
import unicodedata
import string

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

def get_known_artists_tracks():
    try:
        top_artists = sp.current_user_top_artists(limit=10, time_range='long_term')
        artist_names = [artist['name'] for artist in top_artists['items']]
        top_tracks = sp.current_user_top_tracks(limit=10, time_range='long_term')
        track_names = [f"{track['name']} by {track['artists'][0]['name']}" for track in top_tracks['items']]
        return artist_names, track_names
    except Exception as e:
        return [], []

def normalize_name(name):
    # Lowercase, remove punctuation, normalize unicode
    name = name.lower()
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    name = name.translate(str.maketrans('', '', string.punctuation))
    return name.strip()

def validate_and_correct_tracks_with_spotify(tracks, user_country=None):
    """
    Validates tracks against Spotify and corrects artist names if necessary.
    Returns a list of tuples: (corrected_track_string, spotify_track_id) for valid tracks.
    """
    corrected_tracks = []
    if not tracks:
        return corrected_tracks

    for track in tracks:
        match = re.match(r"(.+?) by (.+)", track)
        if not match:
            continue
        
        track_name, artist_name = match.groups()
        
        # First, try a precise search.
        query = f"track:{track_name} artist:{artist_name}"
        results = sp.search(q=query, type="track", limit=1)
        
        # If no results, broaden the search to just the track name.
        if not results["tracks"]["items"]:
            query = f"track:{track_name}"
            results = sp.search(q=query, type="track", limit=1)

        if results["tracks"]["items"]:
            item = results["tracks"]["items"][0]
            if (item.get("is_playable", True) and
                (not user_country or user_country in item.get("available_markets", []))):
                
                spotify_track_name = item['name']
                spotify_artist_names = ", ".join([a['name'] for a in item['artists']])
                
                corrected_track_string = f"{spotify_track_name} by {spotify_artist_names}"
                spotify_track_id = item['id']
                
                corrected_tracks.append((corrected_track_string, spotify_track_id))

    return corrected_tracks

def extract_tracks_from_response(response_text):
    # Simple regex to find lines like: 1. Song Name by Artist Name
    pattern = r"\d+\.\s*([^\n]+? by [^\n]+)"
    return re.findall(pattern, response_text)

def fallback_spotify_recs(user_message, known_artists, known_tracks):
    # Use Spotify recommendations API, avoiding known tracks/artists
    taste = get_full_spotify_profile()
    # Use top genre or artist as seed
    top_artists, _ = get_known_artists_tracks()
    seed_artists = top_artists[:2] if top_artists else None
    recs = sp.recommendations(seed_artists=seed_artists, limit=5)
    tracks = []
    for t in recs['tracks']:
        track_str = f"{t['name']} by {t['artists'][0]['name']}"
        if t['name'] not in known_tracks and t['artists'][0]['name'] not in known_artists:
            tracks.append(track_str)
    if not tracks:
        tracks = [f"{t['name']} by {t['artists'][0]['name']}" for t in recs['tracks']]
    return tracks

def extract_target_features_from_message(message):
    """Extracts target tempo (BPM) and energy from the user message using regex. Returns a dict."""
    features = {}
    # Tempo: look for e.g. '120 bpm', 'around 100bpm', 'fast tempo', 'slow tempo'
    bpm_match = re.search(r'(\d{2,3})\s?bpm', message.lower())
    if bpm_match:
        features['tempo'] = float(bpm_match.group(1))
    elif 'fast tempo' in message.lower() or 'upbeat' in message.lower():
        features['tempo'] = 130  # typical fast tempo
    elif 'slow tempo' in message.lower() or 'chill' in message.lower():
        features['tempo'] = 80  # typical slow tempo
    # Energy: look for 'high energy', 'low energy', etc.
    if 'high energy' in message.lower() or 'energetic' in message.lower():
        features['energy'] = 0.8
    elif 'low energy' in message.lower() or 'chill' in message.lower():
        features['energy'] = 0.3
    return features

def filter_tracks_by_features(corrected_tracks_with_ids, target_features=None):
    """
    corrected_tracks_with_ids: list of (track_string, track_id) tuples
    target_features: dict of {feature_name: value}
    Returns: list of (track_string, track_id) tuples sorted by similarity
    """
    if not corrected_tracks_with_ids or not target_features:
        return corrected_tracks_with_ids
    
    track_ids = [track_id for _, track_id in corrected_tracks_with_ids]
    
    if not track_ids:
        return []

    features_list = sp.audio_features(track_ids)
    
    filtered = []
    for i, feat in enumerate(features_list):
        if not feat:
            continue
        score = 0
        for k, v in target_features.items():
            if k in feat and feat[k] is not None:
                if k == 'tempo':
                    score -= abs(feat[k] - v)
                else:
                    score -= (feat[k] - v) ** 2
        
        track_info = corrected_tracks_with_ids[i] # (track_string, track_id)
        filtered.append((score, track_info))
        
    filtered.sort(reverse=True)
    return [t_info for _, t_info in filtered]

def llm_respond_with_groq(message, history=None):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"response": "Groq API key not set in .env."}
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # Fetch full Spotify profile and known artists/tracks for context
    spotify_context = get_full_spotify_profile()
    known_artists, known_tracks = get_known_artists_tracks()
    system_prompt = (
        "You are Lyra, a deeply insightful, emotionally intelligent music companion. "
        "You always mirror the user's tone and personality, responding in a personable, natural, and reflective way. "
        "You have access to the user's Spotify profile, including their top artists and tracks, which are considered 'already known' to the user: "
        f"Artists: {', '.join(known_artists)}. Tracks: {', '.join(known_tracks)}. "
        "When recommending music or building playlists, focus on discovery: suggest fresh, streamable Spotify tracks and artists that the user is less likely to have heard, based on their taste. "
        "Only suggest real tracks that are currently streamable on Spotify. If unsure, skip it."
        "Avoid repeating artists or tracks from their top lists unless specifically asked. "
        "When building playlists, make sure the selections are either sonically similar to what the user likes or fit the requested niche/mood. "
        "Use mood vocabulary, musical descriptors (like 'dreamy texture', 'bass-forward', 'cinematic strings'), and the occasional emoji. "
        "Keep explanations concise, but make your recommendations feel personal and emotionally resonant. "
        "Include the emotional tone of the music, and always sound like a thoughtful, music-loving friend. "
        "If the user asks for a playlist, build it with variety and freshness in mind. "
        "If you don't know something, say so honestly. "
        f"Here is the user's Spotify profile and listening context: {spotify_context} "
    )
    # Build conversation history for Groq
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})
    data = {
        "model": "llama3-8b-8192",  # or another Groq-supported model
        "messages": messages
    }
    # Try up to 2 times to get valid tracks from LLM
    for attempt in range(2):
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            llm_response = result["choices"][0]["message"]["content"]
            
            tracks_to_validate = extract_tracks_from_response(llm_response)
            
            if tracks_to_validate:
                corrected_tracks = validate_and_correct_tracks_with_spotify(tracks_to_validate)
                
                if len(corrected_tracks) == len(tracks_to_validate):
                    final_tracks_with_ids = corrected_tracks
                    target_features = extract_target_features_from_message(message)
                    
                    if target_features:
                        final_tracks_with_ids = filter_tracks_by_features(corrected_tracks, target_features)

                    response_text = "Based on your request, I've found these tracks for you:"
                    tracks_for_embed = [{"name": name, "id": id} for name, id in final_tracks_with_ids]
                    
                    return {"response": response_text, "tracks": tracks_for_embed}
                else:
                    # Some tracks failed validation/correction, ask LLM to try again
                    data["messages"].append({"role": "assistant", "content": llm_response})
                    data["messages"].append({"role": "system", "content": "Some of your suggestions were not found on Spotify. Please suggest only real, streamable Spotify tracks."})
                    continue
            else:
                return {"response": llm_response}
        except Exception as e:
            return {"response": f"Error calling Groq API: {e}"}
            
    # Fallback to Spotify recs if LLM fails
    fallback_tracks = fallback_spotify_recs(message, known_artists, known_tracks)
    fallback_text = "Here are some fresh Spotify recommendations for you:\n" + "\n".join(f"{t}" for t in fallback_tracks)
    return {"response": fallback_text}
