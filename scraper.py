import requests
from bs4 import BeautifulSoup
from database import clear, add
import time
from datetime import datetime

BASE_URL = "https://cyleria.pl/?subtopic=houses"

def scrape(progress_callback=None):
    clear()
    session = requests.Session()
    page = 0
    done_houses = 0

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
            map_img = cols[0].find("img")["src"] if cols[0].find("img") else ""
            size = cols[1].text.strip()
            owner = cols[2].text.strip()
            status = cols[3].text.strip()

            # Pobieramy rzeczywiste ostatnie logowanie z linku gracza
            last_login = "01.01.1970 (00:00)"
            try:
                profile_url = cols[2].find("a")["href"]
                profile_r = session.get("https://cyleria.pl/" + profile_url)
                profile_soup = BeautifulSoup(profile_r.text, "html.parser")
                login_info = profile_soup.find("td", text="Ostatnie logowanie")
                if login_info:
                    last_login = login_info.find_next_sibling("td").text.strip()
            except:
                pass

            add(name, map_img, owner, status, size, owner, last_login)
            done_houses += 1
            if progress_callback:
                progress_callback(done_houses, done_houses)

        page += 1
        time.sleep(0.1)
