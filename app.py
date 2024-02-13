from flask import Flask, request, jsonify, render_template
from icecream import ic

from modules.user import read_user_data
from modules.media import read_media_data
from modules.preference import get_preferences
from modules.recommendation import get_recommendations


app = Flask(__name__)


@app.route("/")
def index_route():
    return render_template("index.html")


@app.route("/preferences", methods=["GET"])
def preferences_route():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "username is required"}), 400

    force_fetch_user = request.args.get("force_fetch_user")
    user_data = read_user_data(username, force_fetch_user)
    media_data = read_media_data()
    preferences = get_preferences(user_data, media_data)

    return jsonify(preferences)


@app.route("/recommendations", methods=["GET"])
def recommendations_route():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "username is required"}), 400

    force_fetch_user = request.args.get("force_fetch_user")
    user_data = read_user_data(username, force_fetch_user)
    media_data = read_media_data()
    preferences = get_preferences(user_data, media_data)
    recommendations = get_recommendations(user_data, media_data, preferences)

    size = request.args.get("size", "10")  # Default size is 10
    if not size.isdigit() or int(size) < 1 or int(size) > 1000:
        return jsonify({"error": "size must be an integer between 1 and 1000"}), 400

    recommendations = recommendations[: int(size)]
    return render_template("recommendations.html", recommendations=recommendations)


@app.route("/statistics", methods=["GET"])
def statistics_route():
    return render_template("statistics.html")


if __name__ == "__main__":
    app.run(debug=True)
