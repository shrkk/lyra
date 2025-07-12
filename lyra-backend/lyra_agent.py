import os
import requests
import re
import unicodedata
import string
import json
import google.generativeai as genai
import spotipy
from datetime import datetime, timedelta

# Memory cache for user Spotify data
# Structure: {user_token_hash: {"data": {...}, "timestamp": datetime, "expires": datetime}}
USER_CACHE = {}
CACHE_DURATION = timedelta(hours=1)  # Cache for 1 hour

def get_user_cache_key(token):
    """Generate a cache key from the user's token."""
    return hash(token) % (2**32)  # Simple hash for cache key

def get_cached_user_data(token):
    """Get cached user data if it exists and is still valid."""
    cache_key = get_user_cache_key(token)
    if cache_key in USER_CACHE:
        cache_entry = USER_CACHE[cache_key]
        if datetime.now() < cache_entry["expires"]:
            return cache_entry["data"]
        else:
            # Remove expired cache entry
            del USER_CACHE[cache_key]
    return None

def cache_user_data(token, data):
    """Cache user data with expiration."""
    cache_key = get_user_cache_key(token)
    USER_CACHE[cache_key] = {
        "data": data,
        "timestamp": datetime.now(),
        "expires": datetime.now() + CACHE_DURATION
    }

def clear_user_cache(token=None):
    """Clear cache for specific user or all users."""
    if token:
        cache_key = get_user_cache_key(token)
        if cache_key in USER_CACHE:
            del USER_CACHE[cache_key]
    else:
        USER_CACHE.clear()

def initialize_user_session(token):
    """
    Initialize a user session by pre-loading all Spotify data into cache.
    This should be called once when a user starts a conversation.
    Returns the user data summary for immediate use.
    """
    try:
        user_data = get_comprehensive_user_data(token)
        return {
            "success": True,
            "summary": user_data.get('summary', ''),
            "profile": user_data.get('profile', {}),
            "message": "User data loaded and cached successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to load user data"
        }

def get_spotify_client(token):
    """Creates a Spotipy client for a given user token."""
    return spotipy.Spotify(auth=token)

def summarize_taste(token):
    sp = get_spotify_client(token)
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

def recommend_music(mood=None, genre=None, activity=None, token=None):
    # Use Spotify recommendations endpoint for demo
    seed_genres = []
    if genre:
        seed_genres.append(genre)
    else:
        # fallback to user's top genre
        if token:
            taste = summarize_taste(token)
            seed_genres.append(taste['top_genre'])
        else:
            return {"recommendations": [], "used_genre": "unknown"}
    
    if not token:
        return {"recommendations": [], "used_genre": seed_genres[0] if seed_genres else "unknown"}
    
    sp = get_spotify_client(token)
    recs = sp.recommendations(seed_genres=seed_genres[:1], limit=5)
    tracks = [f"{t['name']} by {t['artists'][0]['name']}" for t in recs['tracks']]
    return {"recommendations": tracks, "used_genre": seed_genres[0]}

def get_profile_visualization(token=None):
    # Return genre and artist breakdowns
    if not token:
        return {"top_artists": [], "genre_breakdown": {}}
    
    sp = get_spotify_client(token)
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

def get_comprehensive_user_data(token):
    """
    Fetch comprehensive user data from Spotify and cache it.
    This function should be called once at the start of a conversation.
    """
    # Check cache first
    cached_data = get_cached_user_data(token)
    if cached_data:
        return cached_data
    
    sp = get_spotify_client(token)
    try:
        # Basic profile
        profile = sp.current_user()
        display_name = profile.get('display_name', 'Unknown')
        country = profile.get('country', 'Unknown')
        
        # Top artists (long term)
        top_artists_long = sp.current_user_top_artists(limit=10, time_range='long_term')
        top_artists_medium = sp.current_user_top_artists(limit=10, time_range='medium_term')
        top_artists_short = sp.current_user_top_artists(limit=10, time_range='short_term')
        
        # Top tracks (long term)
        top_tracks_long = sp.current_user_top_tracks(limit=10, time_range='long_term')
        top_tracks_medium = sp.current_user_top_tracks(limit=10, time_range='medium_term')
        top_tracks_short = sp.current_user_top_tracks(limit=10, time_range='short_term')
        
        # Recently played
        recent = sp.current_user_recently_played(limit=20)
        
        # Playlists
        playlists = sp.current_user_playlists(limit=10)
        
        # Process and structure the data
        user_data = {
            "profile": {
                "display_name": display_name,
                "country": country
            },
            "top_artists": {
                "long_term": [{"name": artist['name'], "genres": artist['genres']} for artist in top_artists_long['items']],
                "medium_term": [{"name": artist['name'], "genres": artist['genres']} for artist in top_artists_medium['items']],
                "short_term": [{"name": artist['name'], "genres": artist['genres']} for artist in top_artists_short['items']]
            },
            "top_tracks": {
                "long_term": [{"name": track['name'], "artist": track['artists'][0]['name']} for track in top_tracks_long['items']],
                "medium_term": [{"name": track['name'], "artist": track['artists'][0]['name']} for track in top_tracks_medium['items']],
                "short_term": [{"name": track['name'], "artist": track['artists'][0]['name']} for track in top_tracks_short['items']]
            },
            "recently_played": [{"name": item['track']['name'], "artist": item['track']['artists'][0]['name']} for item in recent['items']],
            "playlists": [{"name": pl['name'], "id": pl['id']} for pl in playlists['items']],
            "genre_analysis": {},
            "summary": ""
        }
        
        # Analyze genres across all time periods
        all_genres = []
        for time_period in ['long_term', 'medium_term', 'short_term']:
            for artist in user_data['top_artists'][time_period]:
                all_genres.extend(artist['genres'])
        
        genre_freq = {}
        for genre in all_genres:
            genre_freq[genre] = genre_freq.get(genre, 0) + 1
        
        user_data['genre_analysis'] = {
            'frequency': genre_freq,
            'top_genres': sorted(genre_freq.keys(), key=lambda x: genre_freq[x], reverse=True)[:5]
        }
        
        # Create summary for LLM
        top_artists_names = [artist['name'] for artist in user_data['top_artists']['medium_term'][:5]]
        top_tracks_names = [f"{track['name']} by {track['artist']}" for track in user_data['top_tracks']['medium_term'][:5]]
        recent_tracks_names = [f"{track['name']} by {track['artist']}" for track in user_data['recently_played'][:5]]
        playlist_names = [pl['name'] for pl in user_data['playlists'][:5]]
        
        user_data['summary'] = (
            f"Spotify profile for {display_name} (Country: {country}).\n"
            f"Top artists: {', '.join(top_artists_names)}.\n"
            f"Top genres: {', '.join(user_data['genre_analysis']['top_genres'][:3])}.\n"
            f"Top tracks: {', '.join(top_tracks_names)}.\n"
            f"Recently played: {', '.join(recent_tracks_names)}.\n"
            f"Playlists: {', '.join(playlist_names)}."
        )
        
        # Cache the data
        cache_user_data(token, user_data)
        return user_data
        
    except Exception as e:
        return {
            "error": f"Could not fetch Spotify profile: {e}",
            "summary": f"(Could not fetch full Spotify profile: {e})"
        }

def get_full_spotify_profile(token):
    """
    Legacy function for backward compatibility.
    Now uses cached data if available.
    """
    user_data = get_comprehensive_user_data(token)
    return user_data.get('summary', user_data.get('error', 'Unknown error'))

def get_known_artists_tracks(token):
    """
    Get known artists and tracks from cached user data.
    """
    try:
        user_data = get_comprehensive_user_data(token)
        if isinstance(user_data, dict) and 'error' in user_data:
            return [], []
        
        # Extract artist names and track names safely
        artist_names = []
        track_names = []
        
        # Handle artist data
        if isinstance(user_data, dict) and 'top_artists' in user_data:
            top_artists_data = user_data['top_artists']
            if isinstance(top_artists_data, dict) and 'medium_term' in top_artists_data:
                top_artists = top_artists_data['medium_term']
                if isinstance(top_artists, list):
                    artist_names = [artist['name'] for artist in top_artists if isinstance(artist, dict) and 'name' in artist]
        
        # Handle track data
        if isinstance(user_data, dict) and 'top_tracks' in user_data:
            top_tracks_data = user_data['top_tracks']
            if isinstance(top_tracks_data, dict) and 'medium_term' in top_tracks_data:
                top_tracks = top_tracks_data['medium_term']
                if isinstance(top_tracks, list):
                    track_names = [f"{track['name']} by {track['artist']}" for track in top_tracks if isinstance(track, dict) and 'name' in track and 'artist' in track]
        
        return artist_names, track_names
    except Exception as e:
        return [], []

def normalize_name(name):
    # Lowercase, remove punctuation, normalize unicode
    name = name.lower()
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    name = name.translate(str.maketrans('', '', string.punctuation))
    return name.strip()

def validate_and_correct_tracks_with_spotify(tracks, token, user_country=None):
    """
    Validates tracks against Spotify and corrects artist names if necessary.
    Returns a list of tuples: (corrected_track_string, spotify_track_id) for valid tracks.

    This version STRICTLY validates artist matches, only accepting results
    where the artist from Spotify matches the requested artist.
    """
    sp = get_spotify_client(token)
    corrected_tracks = []
    if not tracks:
        return corrected_tracks

    for track in tracks:
        match = re.match(r"(.+?) by (.+)", track)
        if not match:
            continue
        
        track_name, artist_name = match.groups()
        artist_name_norm = normalize_name(artist_name)

        # First try precise search: track + artist
        query = f'track:"{track_name}" artist:"{artist_name}"'
        results = sp.search(q=query, type="track", limit=5)

        # If no precise results, fallback to just track name search
        if not results["tracks"]["items"]:
            query = f'track:"{track_name}"'
            results = sp.search(q=query, type="track", limit=5)

        # Find best matching track where artist matches normalized artist name
        best_match = None
        for item in results["tracks"]["items"]:
            if not item.get("is_playable", True):
                continue
            if user_country and user_country not in item.get("available_markets", []):
                continue
            
            artists = item["artists"]
            artist_names = [normalize_name(a['name']) for a in artists]
            if artist_name_norm in artist_names:
                best_match = item
                break
        
        if best_match:
            spotify_track_name = best_match['name']
            spotify_artist_names = ", ".join([a['name'] for a in best_match['artists']])
            corrected_track_string = f"{spotify_track_name} by {spotify_artist_names}"
            spotify_track_id = best_match['id']
            corrected_tracks.append((corrected_track_string, spotify_track_id))
        # else: no good match, skip this track

    return corrected_tracks

def extract_json_from_response(response_text):
    """
    Finds and parses a JSON object from the end of a string.
    Returns the parsed JSON and the text before the JSON object.
    """
    json_start_index = response_text.rfind('```json')
    if json_start_index == -1:
        return None, response_text

    json_str_with_ticks = response_text[json_start_index + 7:]
    json_end_index = json_str_with_ticks.rfind('```')
    if json_end_index == -1:
        return None, response_text
    
    json_str = json_str_with_ticks[:json_end_index].strip()
    
    try:
        data = json.loads(json_str)
        conversation_part = response_text[:json_start_index].strip()
        return data, conversation_part
    except json.JSONDecodeError:
        return None, response_text

def fallback_spotify_recs(user_message, known_artists, known_tracks, token):
    # Use Spotify recommendations API, avoiding known tracks/artists
    # Use top artist as a reliable seed
    top_artists, _ = get_known_artists_tracks(token)
    if not top_artists:
        # Fallback if there are no top artists for some reason
        return ["Sorry, I couldn't get any recommendations right now. Try listening to some more music!"]

    sp = get_spotify_client(token)
    seed_artists = top_artists[:2]
    recs = sp.recommendations(seed_artists=seed_artists, limit=5)

    tracks = []
    if recs and recs['tracks']:
        for t in recs['tracks']:
            track_str = f"{t['name']} by {t['artists'][0]['name']}"
            if t['name'] not in known_tracks and t['artists'][0]['name'] not in known_artists:
                tracks.append(track_str)
    
    # If filtering results in an empty list, return the original recommendations
    if not tracks:
        tracks = [f"{t['name']} by {t['artists'][0]['name']}" for t in recs['tracks']] if recs and recs['tracks'] else []

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
def is_similarity_request(message):
    """Returns True if user is asking for songs like a specific track or artist."""
    keywords = [
        "like", "similar to", "reminds me of", "same vibe as", "same energy as", "same feel as"
    ]
    return any(kw in message.lower() for kw in keywords)


def filter_tracks_by_features(corrected_tracks_with_ids, token, target_features=None):
    """
    corrected_tracks_with_ids: list of (track_string, track_id) tuples
    target_features: dict of {feature_name: value}
    Returns: list of (track_string, track_id) tuples sorted by similarity
    """
    sp = get_spotify_client(token)
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

def llm_respond_with_gemini(message, history, token):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"response": "Google API key not set in .env."}
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Get cached user data (this will fetch from cache if available, or fetch and cache if not)
    user_data = get_comprehensive_user_data(token)
    spotify_context = user_data.get('summary', user_data.get('error', 'Unknown error'))
    
    system_prompt = (
        "You are Lyra, an emotionally intelligent music companion who curates deeply personal, handpicked Spotify recommendations.\n\n"

        "🧭 YOUR MISSION:\n"
        "- Help users discover truly *new* and *underappreciated* music.\n"
        "- Avoid anything popular or trending unless explicitly requested.\n"
        "- Capture the **ambiance, tonality, emotional undercurrent, and texture** of the user's recent (1–3 month) listening patterns.\n\n"

        "🎧 BEHAVIOR GUIDELINES:\n"
        "- DO NOT recommend artists or tracks found in the user's top artists, top tracks, or recent plays.\n"
        "- Focus instead on lesser-known tracks that *feel* like the user's taste — e.g., similar tempo, instrumentation, mood, or vocal style.\n"
        "- Choose songs with **emotional alignment**, not just genre or popularity overlap.\n"
        "- Prioritize **non-mainstream**, emerging, international, or overlooked artists — ideally those with under-the-radar followings.\n\n"

        "🎨 TONE OF VOICE:\n"
        "- Write as a warm, thoughtful, perceptive curator — like a close friend sharing a hidden gem.\n"
        "- Use vivid, emotionally intelligent language that speaks to the *feel* of a song: melancholic piano, glitched-out vocals, dreamlike synths, hushed intimacy, lush orchestration.\n"
        "- Do not sound robotic or algorithmic — always write like a human with taste.\n\n"

        "📦 RESPONSE FORMAT:\n"
        "1. Start with a brief, conversational recommendation message (~2–3 sentences).\n"
        "2. Follow with a valid JSON block like this:\n"
        "```json\n"
        "{\n"
        '  "recommendations": [\n'
        '    {"track": "Song Name 1", "artist": "Artist Name 1"},\n'
        '    {"track": "Song Name 2", "artist": "Artist Name 2"}\n'
        "  ]\n"
        "}\n"
        "```\n"
        "⚠️ If no good matches are found, explain gently and ask the user to adjust input — but still provide an empty JSON block.\n\n"

        "🛑 DO NOT:\n"
        "- Recommend charting artists (Top 100 or editorial playlist regulars)\n"
        "- Repeat artists already known to the user\n"
        "- Generate fake song or artist names\n\n"

        "🎵 TEMPO & MOOD GUIDANCE:\n"
        "- Match terms like 'chill', 'slow tempo', 'sad', etc. to songs with ~80 BPM and low energy (~0.3)\n"
        "- Match 'upbeat', 'dancey', etc. to ~130 BPM, energy > 0.7\n"
        "- Consider instrumentation (e.g., lo-fi textures, ambient layers, acoustic tones) over genre labels\n\n"

        "📊 USER PROFILE INTERPRETATION:\n"
        "- Use recent 1–3 month Spotify data to infer emotional trends, genre leanings, tempo/energy averages\n"
        "- Only reference user history **briefly** and **sparingly** — 1–2 times per session unless asked\n"

        "💬 VOICE EXAMPLES:\n"
        '- “You’ve been vibing with moody, synth-washed ballads lately — here’s something in that spirit but a little off the radar.”\n'
        '- “This one has a similar hush and warmth to what you’ve been spinning at night — think vintage keys and foggy vocals.”\n'

        "🌐 For non-music questions, respond conversationally — skip JSON.\n\n"

        f"Here is the user's Spotify profile: {spotify_context}"
    )


    full_history = [{"role": "system", "content": system_prompt}]
    if history:
        full_history.extend(history)
    full_history.append({"role": "user", "content": message})

    gemini_history = []
    for msg in full_history:
        role = 'model' if msg['role'] == 'assistant' else msg['role']
        if role == 'system': continue
        gemini_history.append({'role': role, 'parts': [msg['content']]})

    chat = model.start_chat(history=gemini_history)

    try:
        prompt_with_context = f"{system_prompt}\\n\\nUser message: {message}"
        resp = chat.send_message(prompt_with_context)
        llm_response_full = resp.text
        
        parsed_json, conversational_response = extract_json_from_response(llm_response_full)
        
        tracks_to_validate = []
        # Check if the AI intended to send recommendations
        if parsed_json and isinstance(parsed_json.get("recommendations"), list):
            recs = parsed_json["recommendations"]
            for rec in recs:
                if isinstance(rec, dict) and "track" in rec and "artist" in rec:
                    tracks_to_validate.append(f"{rec['track']} by {rec['artist']}")

            # If we have tracks to validate, proceed
            if tracks_to_validate:
                # Pass the token to the validation function
                final_tracks_with_ids = validate_and_correct_tracks_with_spotify(tracks_to_validate, token)
                
                if final_tracks_with_ids:
                    # Success case: return embeds
                    target_features = extract_target_features_from_message(message)
                    if target_features:
                        final_tracks_with_ids = filter_tracks_by_features(final_tracks_with_ids, token, target_features)
                    # Extract features if not already done and it's a similarity-style prompt
                    if not target_features and is_similarity_request(message):
                        target_features = extract_target_features_from_message(message)

                    tracks_for_embed = []
                    for name, id in final_tracks_with_ids:
                        # Fetch track details from Spotify to get preview_url and external_urls
                        try:
                            track_info = get_spotify_client(token).track(id)
                            preview_url = track_info.get('preview_url')
                            spotify_url = track_info.get('external_urls', {}).get('spotify')
                        except Exception:
                            preview_url = None
                            spotify_url = None
                        tracks_for_embed.append({
                            "name": name,
                            "id": id,
                            "preview_url": preview_url,
                            "spotify_url": spotify_url
                        })
                    return {"response": conversational_response, "tracks": tracks_for_embed}
                else:
                    # Failure case: AI tried but tracks were invalid
                    return {"response": "I found some potential recommendations, but couldn't confirm them on Spotify. Could you try asking in a different way?"}

        # If we are here, the AI did not intend to send music. Return its text response.
        # BACKEND FALLBACK: If the user message is about music, try to generate recommendations anyway
        music_keywords = ["recommend", "playlist", "song", "music", "track", "suggest"]
        if any(kw in message.lower() for kw in music_keywords):
            # Use fallback_spotify_recs to get track strings
            fallback_tracks = fallback_spotify_recs(message, [], [], token)
            if fallback_tracks:
                # Validate and enrich tracks
                final_tracks_with_ids = validate_and_correct_tracks_with_spotify(fallback_tracks, token)
                if final_tracks_with_ids:
                    tracks_for_embed = []
                    for name, id in final_tracks_with_ids:
                        try:
                            track_info = get_spotify_client(token).track(id)
                            preview_url = track_info.get('preview_url')
                            spotify_url = track_info.get('external_urls', {}).get('spotify')
                        except Exception:
                            preview_url = None
                            spotify_url = None
                        tracks_for_embed.append({
                            "name": name,
                            "id": id,
                            "preview_url": preview_url,
                            "spotify_url": spotify_url
                        })
                    return {"response": conversational_response, "tracks": tracks_for_embed}
        return {"response": conversational_response}
            
    except Exception as e:
        return {"response": f"Error calling Gemini API: {e}"}
