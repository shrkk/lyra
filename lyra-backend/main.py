from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from spotipy.oauth2 import SpotifyOAuth

from lyra_agent import summarize_taste, llm_respond_with_gemini, recommend_music, get_profile_visualization, initialize_user_session, debug_user_data, get_comprehensive_user_data

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://lyraai-git-main-shrkks-projects.vercel.app", "http://localhost:3000"])  # Allow only your Vercel frontend

@app.route("/lyra/login", methods=["POST"])
def handle_login():
    """
    Login endpoint that pre-loads and caches all user Spotify data.
    This should be called immediately after successful Spotify authentication.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization token not found"}), 401
    token = auth_header.split(' ')[1]
    
    try:
        # Pre-load all user data into cache
        user_data = get_comprehensive_user_data(token)
        
        if isinstance(user_data, dict) and 'error' in user_data:
            return jsonify({
                "success": False,
                "error": user_data['error'],
                "message": "Failed to load user data during login"
            }), 400
        
        # Return success with user profile info
        return jsonify({
            "success": True,
            "message": "Login successful - user data cached",
            "user_profile": {
                "display_name": user_data.get('profile', {}).get('display_name', 'Unknown'),
                "country": user_data.get('profile', {}).get('country', 'Unknown'),
                "top_genres": user_data.get('genre_analysis', {}).get('top_genres', [])[:3],
                "top_artists_count": len(user_data.get('top_artists', {}).get('medium_term', [])),
                "recent_tracks_count": len(user_data.get('recently_played', []))
            },
            "cache_status": "loaded"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Login failed - could not load user data"
        }), 500

@app.route("/lyra", methods=["GET"])
def handle_lyra():
    # This endpoint needs a token to work properly
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization token required"}), 401
    token = auth_header.split(' ')[1]
    
    result = summarize_taste(token)
    return jsonify(result)

@app.route("/lyra/init", methods=["POST"])
def handle_init():
    """Initialize user session and pre-load Spotify data into cache."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization token not found"}), 401
    token = auth_header.split(' ')[1]
    
    result = initialize_user_session(token)
    return jsonify(result)

@app.route("/lyra/debug", methods=["GET"])
def handle_debug():
    """Debug endpoint to check user data status."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization token not found"}), 401
    token = auth_header.split(' ')[1]
    
    result = debug_user_data(token)
    return jsonify(result)

@app.route("/lyra/chat", methods=["POST"])
def handle_chat():
    data = request.json
    user_message = data.get("message", "")
    history = data.get("history", [])
    
    # Get the token from the request header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization token not found"}), 401
    token = auth_header.split(' ')[1]

    # Chat now uses cached data automatically - no need to pre-load
    response = llm_respond_with_gemini(user_message, history=history, token=token)
    return jsonify(response)

@app.route("/lyra/status", methods=["GET"])
def handle_status():
    """
    Check if user data is cached and ready for chat.
    Returns cache status without loading data.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization token not found"}), 401
    token = auth_header.split(' ')[1]
    
    debug_info = debug_user_data(token)
    return jsonify({
        "cache_ready": debug_info.get("cache_status") == "cached",
        "cache_status": debug_info.get("cache_status", "unknown"),
        "has_user_data": debug_info.get("has_summary", False),
        "top_artists_count": debug_info.get("top_artists_count", 0)
    })

@app.route("/lyra/recommend", methods=["POST"])
def handle_recommend():
    data = request.json
    mood = data.get("mood")
    genre = data.get("genre")
    activity = data.get("activity")
    
    # Get token from header
    auth_header = request.headers.get('Authorization')
    token = None
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    
    response = recommend_music(mood=mood, genre=genre, activity=activity, token=token)
    return jsonify(response)

@app.route("/lyra/profile", methods=["GET"])
def handle_profile():
    # Get token from header
    auth_header = request.headers.get('Authorization')
    token = None
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    
    response = get_profile_visualization(token=token)
    return jsonify(response)

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
