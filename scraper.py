import requests
from bs4 import BeautifulSoup
from database import clear, add
import time

BASE_URL = "https://cyleria.pl/?subtopic=houses"

def scrape(progress_callback=None):
    clear()
    session = requests.Session()
    page = 1
    total_houses = 0

    while True:
        r = session.get(BASE_URL + f"&page={page}")
        soup = BeautifulSoup(r.text, "html.parser")

        rows = soup.select("tbody.text-start tr")
        if not rows:
            break

        for i, row in enumerate(rows, start=1):
            name = row.select_one("td.text-center").get_text(strip=True)
            map_url = row.select_one("span[data-bs-content]")["data-bs-content"]
            size = int(row.select_one("td.dt-type-numeric").text.strip())
            owner = row.select_one("td.text-center a").text.strip()
            # Na razie dummy last login, później możesz pobrać ze strony postaci
            last_login = "01.01.2000 (00:00)"  

            add({
                "name": name,
                "map_url": map_url,
                "size": size,
                "owner": owner,
                "last_login": last_login
            })
            total_houses += 1
            if progress_callback:
                progress_callback(total_houses, total_houses + 1)  # ETA dummy

        # sprawdź paginację
        next_button = soup.select_one("ul.pagination li.next")
        if not next_button or "disabled" in next_button.get("class", []):
            break
        page += 1
        time.sleep(1)  # unikamy rate limit
