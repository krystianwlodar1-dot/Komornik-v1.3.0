import requests
from bs4 import BeautifulSoup
from database import add  # funkcja do dodawania do bazy

BASE_URL = "https://cyleria.pl/houses"  # zmień na właściwy URL

def get_total_pages():
    """Pobiera liczbę stron z paginacji"""
    r = requests.get(BASE_URL)
    soup = BeautifulSoup(r.text, "html.parser")
    pagination = soup.find("ul", class_="pagination")
    if not pagination:
        return 1
    pages = [int(btn.text) for btn in pagination.find_all("button") if btn.text.isdigit()]
    return max(pages) if pages else 1

def get_houses_from_page(page):
    """Zwraca listę domków na jednej stronie"""
    url = f"{BASE_URL}?page={page}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    tbody = soup.find("tbody", class_="text-start")
    if not tbody:
        return []

    houses = []
    for tr in tbody.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue
        # Wyciągamy dane
        name = tds[0].get_text(strip=True)
        size = int(tds[1].text.strip())
        owner = tds[2].get_text(strip=True)
        status = tds[3].get_text(strip=True)
        map_url = ""
        popover = tds[0].find("span", {"data-bs-toggle": "popover"})
        if popover and "data-bs-content" in popover.attrs:
            content = popover["data-bs-content"]
            # wyciągamy URL obrazka z popover
            if "src='" in content:
                map_url = content.split("src='")[1].split("'")[0]
        # Możesz dodać więcej pól jeśli potrzebujesz
        houses.append([None, name, map_url, owner, size, status])
    return houses

def count_all_houses():
    """Liczy wszystkie domki w serwisie"""
    total = 0
    total_pages = get_total_pages()
    for page in range(1, total_pages + 1):
        total += len(get_houses_from_page(page))
    return total

def scrape(progress_callback=None):
    """Główna funkcja scrapująca wszystkie domki"""
    houses = []
    total_pages = get_total_pages()
    total_houses = count_all_houses()
    done = 0

    for page in range(1, total_pages + 1):
        page_houses = get_houses_from_page(page)
        for h in page_houses:
            houses.append(h)
            add(h)  # zapisujemy od razu do bazy
            done += 1
            if progress_callback:
                progress_callback(done, total_houses)

    return houses
