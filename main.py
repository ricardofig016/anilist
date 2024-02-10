import sys
from icecream import ic

from user import read_user_data, fetch_user_data, store_user_data
from media import read_media_data, fetch_and_store_media_data, display_media
from preference import get_preferences
from recommendation import get_recommendations


def main():
    if len(sys.argv) < 2:
        print("Usage: /bin/python3 main.py <username> <arguments>")
        sys.exit(1)

    sys.argv = [argument.lower() for argument in sys.argv]

    username = sys.argv[1]

    user_data = read_user_data(username)
    media_data = read_media_data()

    if not user_data or "--fetch-user" in sys.argv:
        user_data = fetch_user_data(username)
        store_user_data(username, user_data)

    if "--fetch-media" in sys.argv:
        fetch_and_store_media_data()

    if "--display-media" in sys.argv:
        display_media(media_data)

    preferences = get_preferences(user_data, media_data)
    recommendations = get_recommendations(user_data, media_data, preferences)

    if "--preferences" in sys.argv:
        ic(preferences)

    if "--recommendations" in sys.argv:
        size = int(sys.argv[sys.argv.index("--recommendations") + 1])
        ic(recommendations[:size])


if __name__ == "__main__":
    main()
