from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup
from icecream import ic


def get_page_content(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)
    html_content = driver.page_source
    driver.quit()
    return html_content


def run():
    url = "https://anilist.co/user/ricardofig016/animelist"

    # Parse html with bs4
    soup = BeautifulSoup(get_page_content(url), "html.parser")

    entries = soup.select("div.entry-card.row")
    # ic(entries)
    data = []
    for entry in entries:
        title_link = entry.find("div", class_="title").find("a")
        id = title_link["href"].split("/")[-3]
        name = title_link.text.strip()
        score = entry.find("div", class_="score").get("score")
        point = [id, name, score]
        data.append(point)

    ic(data)
    ic(len(data))

    with open("ricardo.html", "w", encoding="utf-8") as file:
        [file.write(point.__str__() + "\n") for point in data]
        pass

    return


if __name__ == "__main__":
    run()
