import requests
from bs4 import BeautifulSoup
from database import clear, add
import time

BASE_URL = "https://cyleria.pl/?subtopic=houses"

def scrape(progress_callback=None):
    # czyścimy stare dane
    clear()

    session = requests.Session()
    page = 0
    total_houses = 0

    while True:
        url = f"{BASE_URL}&page={page}"
        r = session.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        tbody = soup.find("tbody", class_="text-start")
        if not tbody:
            break

        rows = tbody.find_all("tr")
        if not rows:
            break

        for row in rows:
            cols = row.find_all("td")
            name = cols[0].text.strip()
            map_img = cols[0].find("img")["src"]
            size = cols[1].text.strip()
            owner = cols[2].text.strip()
            last_login = "01.01.1970 (00:00)"  # tymczasowo
            status = cols[3].text.strip()
            add(name, map_img, owner, status, size, owner, last_login)
            total_houses += 1
            if progress_callback:
                progress_callback(total_houses, total_houses)

        page += 1
