import requests
from bs4 import BeautifulSoup
from database import clear, add

BASE = "https://cyleria.pl/?subtopic=houses"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_last_login(name):
    url = f"https://cyleria.pl/?subtopic=characters&name={name}"
    html = requests.get(url, headers=HEADERS, timeout=15).text
    soup = BeautifulSoup(html, "html.parser")

    for li in soup.select("li.list-group-item"):
        if "Logowanie" in li.text:
            return li.find("strong").text.strip()

    return "None"

def extract_map_and_city(span):
    if not span:
        return "", ""
    data = span.get("data-bs-content", "")
    map_url = ""
    city = ""

    if "img src='" in data:
        map_url = data.split("img src='")[1].split("'")[0]
    if "fw-bold" in data:
        city = data.split("fw-bold'>")[1].split("<")[0]

    return map_url, city

def get_total_pages(html):
    soup = BeautifulSoup(html, "html.parser")
    pages = []
    for b in soup.select("ul.pagination button.page-link"):
        if b.text.isdigit():
            pages.append(int(b.text))
    return max(pages) if pages else 1

def scrape(progress_callback=None):
    clear()

    # Strona 1 żeby sprawdzić ile jest stron
    html = requests.get(BASE, headers=HEADERS, timeout=20).text
    total_pages = get_total_pages(html)

    all_rows = []

    for page in range(total_pages):
        url = BASE + f"&page={page}"
        html = requests.get(url, headers=HEADERS, timeout=20).text
        soup = BeautifulSoup(html, "html.parser")

        rows = soup.select("tbody.text-start tr")
        all_rows.extend(rows)

    total = len(all_rows)
    done = 0

    for row in all_rows:
        tds = row.find_all("td")
        if len(tds) < 3:
            continue

        addr_td = tds[0]
        address = addr_td.contents[0].strip()

        span = addr_td.find("span")
        map_url, city = extract_map_and_city(span)

        size = int(tds[1].text.strip())

        owner_tag = tds[2].find("a")
        owner = owner_tag.text.strip() if owner_tag else "None"

        last_login = get_last_login(owner) if owner != "None" else "None"

        add(address, city, map_url, size, owner, last_login)

        done += 1
        if progress_callback:
            progress_callback(done, total)
