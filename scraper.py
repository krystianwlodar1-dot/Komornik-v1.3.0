import requests
from bs4 import BeautifulSoup
from database import clear, add
from datetime import datetime

BASE_URL = "https://cyleria.pl/?subtopic=houses"

def parse_last_login(owner_page_url):
    try:
        r = requests.get(owner_page_url)
        soup = BeautifulSoup(r.text, "html.parser")
        strong = soup.find("strong")
        if strong:
            return strong.text.strip()
        return None
    except:
        return None

def scrape(progress_callback=None):
    clear()
    page = 0
    total_pages = 1
    total_houses = 0

    while page < total_pages:
        r = requests.get(f"{BASE_URL}&page={page+1}")
        soup = BeautifulSoup(r.text, "html.parser")

        if page == 0:
            # policz wszystkie strony
            pagination = soup.find("ul", class_="pagination")
            if pagination:
                pages = pagination.find_all("li")
                total_pages = int(pages[-2].text.strip())

        tbody = soup.find("tbody", class_="text-start")
        houses = tbody.find_all("tr") if tbody else []

        for tr in houses:
            tds = tr.find_all("td")
            if len(tds) < 4:
                continue
            address_td = tds[0]
            size_td = tds[1]
            owner_td = tds[2]
            status_td = tds[3]

            address = address_td.get_text(strip=True)
            map_span = address_td.find("span", {"data-bs-content": True})
            map_url = None
            if map_span:
                html_content = map_span["data-bs-content"]
                map_soup = BeautifulSoup(html_content, "html.parser")
                img = map_soup.find("img")
                if img:
                    map_url = img.get("src")

            size = int(size_td.get_text(strip=True))
            owner_link = owner_td.find("a")
            owner = owner_link.text.strip() if owner_link else None
            owner_page = "https://cyleria.pl/" + owner_link['href'] if owner_link else None
            last_login = parse_last_login(owner_page) if owner_page else None
            status = status_td.get_text(strip=True)

            add((address, map_url, owner, size, status, last_login))
            total_houses += 1
            if progress_callback:
                progress_callback(total_houses, count_houses())

        page += 1

def count_houses():
    from database import count_houses
    return count_houses()
