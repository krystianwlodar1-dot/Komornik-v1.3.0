import requests
from bs4 import BeautifulSoup
from database import add, clear
from datetime import datetime

BASE_URL = "https://cyleria.pl/?subtopic=houses"

def get_last_login(owner):
    url = f"https://cyleria.pl/?subtopic=characters&name={owner}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    tag = soup.find("strong")
    if tag:
        return tag.text.strip()
    return None

def scrape(progress_callback=None):
    clear()  # czyscimy stare dane

    session = requests.Session()
    page = 1
    done = 0

    while True:
        r = session.get(BASE_URL + f"&page={page}")
        soup = BeautifulSoup(r.text, "html.parser")

        rows = soup.select("tbody.text-start tr")
        if not rows:
            break

        for tr in rows:
            tds = tr.find_all("td")
            name = tds[0].text.strip()
            map_img = tds[0].find("img")["src"]
            size = tds[1].text.strip()
            owner_tag = tds[2].find("a")
            owner = owner_tag.text.strip() if owner_tag else "None"
            status = tds[3].text.strip()
            last_login = get_last_login(owner) if owner != "None" else "None"

            add((name, map_img, status, size, owner, last_login))
            done += 1
            if progress_callback:
                progress_callback(done, done)

        # paginacja
        next_btn = soup.select_one("ul.pagination .next")
        if not next_btn or "disabled" in next_btn.get("class", []):
            break
        page += 1
