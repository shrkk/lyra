from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from spotipy.oauth2 import SpotifyOAuth

from lyra_agent import summarize_taste, llm_respond_with_gemini, recommend_music, get_profile_visualization

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://lyraai-git-main-shrkks-projects.vercel.app", "http://localhost:3000"])  # Allow only your Vercel frontend

@app.route("/lyra", methods=["GET"])
def handle_lyra():
    result = summarize_taste()
    return jsonify(result)

@app.route("/lyra/chat", methods=["POST"])
def handle_chat():
    data = request.json
    user_message = data.get("message", "")
    history = data.get("history", [])
    
    # Get the token from the request header (or however your frontend sends it)
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization token not found"}), 401
    token = auth_header.split(' ')[1]

    response = llm_respond_with_gemini(user_message, history=history, token=token)
    return jsonify(response)

@app.route("/lyra/recommend", methods=["POST"])
def handle_recommend():
    data = request.json
    mood = data.get("mood")
    genre = data.get("genre")
    activity = data.get("activity")
    response = recommend_music(mood=mood, genre=genre, activity=activity)
    return jsonify(response)

@app.route("/lyra/profile", methods=["GET"])
def handle_profile():
    response = get_profile_visualization()
    return jsonify(response)

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
