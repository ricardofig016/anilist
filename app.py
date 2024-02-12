from flask import Flask, request, jsonify, g, abort
from functools import wraps

from modules.user import read_user_data, fetch_user_data, store_user_data
from modules.media import read_media_data, fetch_and_store_media_data, display_media
from modules.preference import get_preferences
from modules.recommendation import get_recommendations


app = Flask(__name__)


def user_data_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(g, "user_data"):
            username = request.args.get("username")
            print(username)
            if not username:
                abort(400, "username is required")
            g.user_data = read_user_data(username)
        return func(*args, **kwargs)

    return wrapper


def media_data_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(g, "media_data"):
            g.media_data = read_media_data()
        return func(*args, **kwargs)

    return wrapper


def preferences_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(g, "preferences"):
            g.preferences = get_preferences(g.user_data, g.media_data)
        return func(*args, **kwargs)

    return wrapper


def recommendations_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(g, "recommendations"):
            g.recommendations = get_recommendations(
                g.user_data, g.media_data, g.preferences
            )
        return func(*args, **kwargs)

    return wrapper


@app.route("/")
def index():
    return "THIS IS THE MAIN PAGE"


@app.route("/preferences", methods=["GET"])
@user_data_decorator
@media_data_decorator
@preferences_decorator
def preferences_route():
    return jsonify(g.preferences), 200


@app.route("/recommendations", methods=["GET"])
@user_data_decorator
@media_data_decorator
@preferences_decorator
@recommendations_decorator
def recommendations_route():
    size = request.args.get("size", "10")  # Default size is 10
    if size.isdigit() and int(size) > 0 and int(size) <= 1000:
        return jsonify(g.recommendations[: int(size)]), 200
    else:
        return jsonify({"error": "size must be integer and <= 1000"}), 400


if __name__ == "__main__":
    app.run(debug=True)
