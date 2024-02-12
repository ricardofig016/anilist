from flask import Flask, request, jsonify, session, abort
from functools import wraps

from modules.user import read_user_data, fetch_user_data, store_user_data
from modules.media import read_media_data, fetch_and_store_media_data, display_media
from modules.preference import get_preferences
from modules.recommendation import get_recommendations


app = Flask(__name__)


@app.route("/")
def index():
    return "THIS IS THE MAIN PAGE"


@app.route("/preferences", methods=["GET"])
def preferences_route():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "username is required"}), 400

    user_data = read_user_data(username)
    media_data = read_media_data()
    preferences = get_preferences(user_data, media_data)

    return jsonify(preferences), 200


@app.route("/recommendations", methods=["GET"])
def recommendations_route():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "username is required"}), 400

    user_data = read_user_data(username)
    media_data = read_media_data()
    preferences = get_preferences(user_data, media_data)
    recommendations = get_recommendations(user_data, media_data, preferences)

    size = request.args.get("size", "10")  # Default size is 10
    if size.isdigit() and int(size) > 0 and int(size) <= 1000:
        return jsonify(recommendations[: int(size)]), 200
    else:
        return jsonify({"error": "size must be integer and <= 1000"}), 400


if __name__ == "__main__":
    app.run(debug=True)
