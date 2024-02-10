import os
import time
import json
from icecream import ic
import requests
import traceback


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
            time.sleep(1.8)
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
        print("\n*******************\n\n1-minute timeout\n\n*******************\n")
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
    path = "data/media.json"
    with open(path, "r") as file:
        data = json.load(file)
    return data


def display_media(data):
    sort_keys = input("[display_media] Sort by: ").split(".")

    example_value = data[0]
    try:
        for key in sort_keys:
            example_value = example_value[key]
    except:
        print(f"[display_media] Error: {sort_keys} is not a valid key combination.")
        return

    if type(example_value) == dict:
        print(
            "[display_media] Error: Key cannot be a dictionary.",
            "Use <dict>.<key> to access keys inside dictionaries.",
        )
        return

    is_reverse = input("[display_media] Reverse (y/n): ").lower() == "y"

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
        print(f"[display_media] Error: {len(sort_keys)} is not a valid number of keys")

    filter_keys = []
    key_combination = input("[display_media] Filter by (-1 to finish): ").split(".")
    while key_combination[0] != "-1":
        filter_keys.append(key_combination)
        key_combination = input("[display_media] Filter by (-1 to finish): ").split(".")

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

        file_path = os.path.join("results", "display_media.json")
        with open(file_path, "w") as file:
            json.dump(filtered_data, file, indent=2)
        print(f"[display_media] See results at '{file_path}'")
    except Exception as e:
        print("[display_media] Error: ", e)
    return
