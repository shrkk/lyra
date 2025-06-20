from flask import Flask, request, jsonify
from lyra_agent import summarize_taste, chat_with_lyra, recommend_music, get_profile_visualization

app = Flask(__name__)

@app.route("/lyra", methods=["GET"])
def handle_lyra():
    result = summarize_taste()
    return jsonify(result)

@app.route("/lyra/chat", methods=["POST"])
def handle_chat():
    user_message = request.json.get("message", "")
    response = chat_with_lyra(user_message)
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
    app.run(port=8888)
