import os
import requests
import re
import unicodedata
import string
import json
import google.generativeai as genai
import spotipy

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

def get_full_spotify_profile(token):
    sp = get_spotify_client(token)
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

def fallback_spotify_recs(user_message, known_artists, known_tracks):
    # Use Spotify recommendations API, avoiding known tracks/artists
    # Use top artist as a reliable seed
    top_artists, _ = get_known_artists_tracks()
    if not top_artists:
        # Fallback if there are no top artists for some reason
        return ["Sorry, I couldn't get any recommendations right now. Try listening to some more music!"]

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
    spotify_context = get_full_spotify_profile(token)
    
    system_prompt = (
    "You are Lyra, a deeply insightful music companion that helps users discover music on Spotify.\n\n"
    "When a user asks for **song recommendations or playlist creation**, you MUST respond with a warm, conversational summary **followed by a valid JSON block** containing real Spotify tracks.\n\n"
    "If you do not include the JSON block, the user will not receive any music recommendations.\n"
    "Here is the required JSON format:\n"
    "```json\n"
    "{\n"
    '  "recommendations": [\n'
    '    {"track": "Song Name 1", "artist": "Artist Name 1"},\n'
    '    {"track": "Song Name 2", "artist": "Artist Name 2"}\n'
    "  ]\n"
    "}\n"
    "```\n"
    "Do NOT respond with only text. Always include the JSON block after your summary.\n\n"
    "If the user asks general questions about their **music taste**, preferences, or habits, base your analysis on their **most recent listening activity from the last 1–2 months**, unless the user clearly asks about 'long-term' or 'all-time' history.\n\n"
    "For example, summarize top genres, favorite artists, and listening patterns using medium_term or short_term Spotify data (NOT long_term).\n\n"
    "For all NON-music related questions, respond with regular conversational text and DO NOT include any JSON.\n\n"
    f"Here is the user's Spotify profile for context: {spotify_context}"
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
            fallback_tracks = fallback_spotify_recs(message, [], [])
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
