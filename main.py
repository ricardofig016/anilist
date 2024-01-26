import sys
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import json
from icecream import ic


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


def fetch_data(username, list_="anime"):
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


def store_data(username, data, list_):
    dir = f"data/{username}/"
    if not os.path.exists(dir):
        os.makedirs(dir)
    path = f"{dir}{list_}.json"

    json_data = json.dumps(data, indent=2)
    with open(path, "w", encoding="utf-8") as file:
        file.write(json_data)
    return


def read_data(username, list_):
    path = f"data/{username}/{list_}.json"
    try:
        with open(path, "r") as file:
            data = json.load(file)
        return data
    except:
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: /bin/python3 main.py <username> <arguments>")
        sys.exit(1)

    username = sys.argv[1]
    list_ = "anime"
    fetch = False
    display = False

    if "--manga" in sys.argv:
        list_ = "manga"
    if "--fetch" in sys.argv:
        fetch = True
    if "--display" in sys.argv:
        display = True

    data = read_data(username, list_)
    if not data or fetch:
        data = fetch_data(username, list_)
        store_data(username, data, list_)

    if display:
        ic(data)


if __name__ == "__main__":
    main()
