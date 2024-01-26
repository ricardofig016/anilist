import sys
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
    hight_diff = max_scroll_height - current_scroll_position
    ic(hight_diff)
    return hight_diff <= 1000


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


def fetch_data(username, list="anime"):
    url = "https://anilist.co/user/" + username
    if list == "anime":
        url += "/animelist"
    elif list == "manga":
        url += "/mangalist"
    else:
        print(f"Error: Invalid list: {list}")

    soup = BeautifulSoup(get_page_content(url), "html.parser")
    entries = soup.select("div.entry.row") + soup.select("div.entry-card.row")
    data = []
    for entry in entries:
        title_link = entry.find("div", class_="title").find("a")
        id = title_link["href"].split("/")[-3]
        title = title_link.text.strip()
        score = entry.find("div", class_="score").get("score")
        item = [id, title, score]
        if not item in data:
            data.append(item)

    return sorted(data, key=lambda x: x[1].lower())


def store_data(username, data):
    formatted_data = [
        {"id": item[0], "title": item[1], "score": item[2]} for item in data
    ]
    json_data = json.dumps(formatted_data, indent=2)
    path = f"data/{username}.json"
    with open(path, "w", encoding="utf-8") as file:
        file.write(json_data)
    return


def main():
    if len(sys.argv) < 2:
        print("Usage: /bin/python3 main.py <username> <arguments>")
        sys.exit(1)

    username = sys.argv[1]
    list = "anime"

    if "--manga" in sys.argv:
        list = "manga"

    data = fetch_data(username, list)
    ic(data)
    ic(len(data))
    store_data(username, data)


if __name__ == "__main__":
    main()
