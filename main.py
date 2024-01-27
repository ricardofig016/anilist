import sys
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import json
from icecream import ic
import requests
import traceback
import functools


def is_scroll_at_bottom(driver):
    current_scroll_position = driver.execute_script("return window.scrollY;")
    max_scroll_height = driver.execute_script(
        "return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );"
    )
    height_diff = max_scroll_height - current_scroll_position
    # ic(height_diff)
    return height_diff <= 1000


def get_page_content(url):
    driver = webdriver.Chrome()
    driver.get(url)
    body = driver.find_element("tag name", "body")
    time.sleep(3)
    while not is_scroll_at_bottom(driver):
        body.send_keys(Keys.END)
        time.sleep(0.5)
    html_content = driver.page_source
    driver.quit()
    return html_content


def fetch_user_data(username, list_="anime"):
    url = "https://anilist.co/user/" + username
    if list_ == "anime":
        url += "/animelist"
    elif list_ == "manga":
        url += "/mangalist"
    else:
        print(f"Error: Invalid list: {list_}")

    soup = BeautifulSoup(get_page_content(url), "html.parser")
    entries = soup.select("div.entry.row") + soup.select("div.entry-card.row")
    data = []
    for entry in entries:
        title_link = entry.find("div", class_="title").find("a")
        id_ = title_link["href"].split("/")[-3]
        title = title_link.text.strip()
        score = entry.find("div", class_="score").get("score")
        item = {"id": id_, "title": title, "score": score}
        if not item in data:
            data.append(item)

    return sorted(data, key=lambda x: x["title"].lower())


def store_user_data(username, data, list_):
    dir = f"data/users/{username}/"
    if not os.path.exists(dir):
        os.makedirs(dir)
    path = f"{dir}{list_}.json"

    json_data = json.dumps(data, indent=2)
    with open(path, "w", encoding="utf-8") as file:
        file.write(json_data)
    return


def read_user_data(username, list_):
    path = f"data/users/{username}/{list_}.json"
    try:
        with open(path, "r") as file:
            data = json.load(file)
        return data
    except:
        return False


def fetch_and_store_media_data():
    media_data = read_media_data()
    try:
        index = 0
        if len(media_data) > 0:
            index = media_data[-1]["id"] + 1
        while True:
            ic(index)
            item_ = fetch_media_item(index)
            if item_:
                media_data.append(item_)
            index += 1
            time.sleep(1.7)
    except Exception as e:
        ic(e)
        traceback.print_exc()
    finally:
        store_media_data(media_data)


def fetch_media_item(id_):
    query = """
    query ($id: Int) {
    Media (id: $id) {
        id
        idMal
        title {
            romaji
            english
        }
        type
        format
        status
        description
        startDate {
            year
        }
        episodes
        chapters
        countryOfOrigin
        source
        coverImage {
            extraLarge
        }
        genres
        averageScore
        popularity
        tags {
            name
            rank
        }
        studios {
            edges {
                node {
                    name
                }
                isMain
            }
        }
        siteUrl
        
    }
    }
    """

    variables = {"id": id_}

    url = "https://graphql.anilist.co"
    response = requests.post(url, json={"query": query, "variables": variables})

    if response.status_code == 429:
        ic("1-minute timeout")
        time.sleep(61)
        return fetch_media_item(id_)

    if response.status_code != 200:
        print(f"Error: Status code: {response.status_code}")
        return

    query_data = response.json()

    if "errors" in query_data:
        print(f"Error: {query_data['errors']}")
        return

    media_data = query_data["data"]["Media"]
    return organize_title_media(media_data)


def organize_title_media(media_data):
    tags = media_data["tags"]

    studios = []
    for studio in media_data["studios"]["edges"]:
        if studio["isMain"]:
            studios.append(studio["node"]["name"])

    item = {
        "id": media_data["id"],
        "idMal": media_data["idMal"],
        "title": media_data["title"],
        "type": media_data["type"],
        "format": media_data["format"],
        "status": media_data["status"],
        "description": media_data["description"],
        "year": media_data["startDate"]["year"],
        "episodes": media_data["episodes"],
        "chapters": media_data["chapters"],
        "country": media_data["countryOfOrigin"],
        "source": media_data["source"],
        "coverImage": media_data["coverImage"]["extraLarge"],
        "genres": media_data["genres"],
        "averageScore": media_data["averageScore"],
        "popularity": media_data["popularity"],
        "tags": tags,
        "studios": studios,
        "siteUrl": media_data["siteUrl"],
    }
    return item


def store_media_data(data):
    path = f"data/media.json"

    json_data = json.dumps(data, indent=2)
    with open(path, "w", encoding="utf-8") as file:
        file.write(json_data)
    return


def read_media_data():
    path = f"data/media.json"
    with open(path, "r") as file:
        data = json.load(file)
    return data


def display(data, file_name):
    sort_keys = input("[display] Sort by: ").split(".")

    example_value = data[0]
    try:
        for key in sort_keys:
            example_value = example_value[key]
    except:
        print(f"[display] Error: {sort_keys} is not a valid key combination.")
        return

    if type(example_value) == dict:
        print(
            "[display] Error: Key cannot be a dictionary.",
            "Use <dict>.<key> to access keys inside dictionaries.",
        )
        return

    is_reverse = input("[display] Reverse (y/n): ").lower() == "y"

    default_value = 0
    if type(example_value) == str:
        default_value = ""

    sorted_data = []
    if len(sort_keys) == 1:
        sorted_data = sorted(
            data,
            key=lambda x: x.get(sort_keys[0], default_value)
            if x.get(sort_keys[0]) is not None
            else default_value,
            reverse=is_reverse,
        )
    elif len(sort_keys) == 2:
        sorted_data = sorted(
            data,
            key=lambda x: x.get(sort_keys[0]).get(sort_keys[1], default_value)
            if x.get(sort_keys[0]).get(sort_keys[1]) is not None
            else default_value,
            reverse=is_reverse,
        )
    else:
        print(f"[display] Error: {len(sort_keys)} is not a valid number of keys")

    filter_keys = []
    key_combination = input("[display] Filter by (-1 to finish): ").split(".")
    while key_combination[0] != "-1":
        filter_keys.append(key_combination)
        key_combination = input("[display] Filter by (-1 to finish): ").split(".")

    try:
        filtered_data = []
        for entry in sorted_data:
            filtered_entry = {}
            for key_comb in filter_keys:
                value = entry
                for key in key_comb:
                    value = value[key]
                filtered_entry["_".join(key_comb)] = value
            filtered_data.append(filtered_entry)

        file_path = os.path.join("results", file_name)
        with open(file_path, "w") as file:
            json.dump(filtered_data, file, indent=2)
        print(f"[display] See results at '{file_path}'")
    except Exception as e:
        print("[display] Error: ", e)
    return


def main():
    if len(sys.argv) < 2:
        print("Usage: /bin/python3 main.py <username> <arguments>")
        sys.exit(1)

    sys.argv = [argument.lower() for argument in sys.argv]

    username = sys.argv[1]

    list_ = "anime"
    if "--manga" in sys.argv:
        list_ = "manga"

    user_data = read_user_data(username, list_)
    media_data = read_media_data()

    if not user_data or "--fetch-user" in sys.argv:
        user_data = fetch_user_data(username, list_)
        store_user_data(username, user_data, list_)

    if "--fetch-media" in sys.argv:
        fetch_and_store_media_data()

    if "--display-user" in sys.argv:
        display(user_data, "display_user.json")

    if "--display-media" in sys.argv:
        display(media_data, "display_media.json")


if __name__ == "__main__":
    main()
