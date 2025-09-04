import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
from datetime import datetime, timedelta

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
]

HEADERS = {
    "User-Agent": random.choice(USER_AGENTS),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tempo.co/",
    "Connection": "keep-alive"
}

BASE_URL_TEMPLATE = "https://www.tempo.co/indeks?page={page}&category=date&start_date={date}+00:00:00&end_date={date}+23:59:59"
SAVE_FOLDER = "tempo_articles"

# Create folder if it doesn't exist
os.makedirs(SAVE_FOLDER, exist_ok=True)

def get_articles_from_page(url):
    response = requests.get(url, headers=HEADERS)
    
    print(f"Fetching {url} - Status code: {response.status_code}")
    
    if response.status_code == 403:
        print("Request blocked by the site. Switching user-agent and retrying...")
        time.sleep(2)  # Brief pause to avoid immediate retries
        return get_articles_from_page(url)  # Retry with the new header

    if response.status_code != 200:
        print(f"Failed to fetch page: {url} (Status code: {response.status_code})")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []

    for figure in soup.select("figure.flex"):
        a_tag = figure.find("a", class_="hover:opacity-75")
        if not a_tag or not a_tag.get("href"):
            continue

        link = a_tag["href"]
        full_link = "https://www.tempo.co" + link if link.startswith("/") else link

        title_tag = figure.find("figcaption")
        title = title_tag.get_text(strip=True) if title_tag else None

        if title and full_link:
            articles.append({
                "title": title,
                "link": full_link,
                "time": None
            })

    return articles

def get_full_article_text(url):
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        return text
    except Exception as e:
        print(f"Error fetching article {url}: {e}")
        return None

def scrape_tempo_for_date(date_str):
    all_articles = []
    page = 1

    while True:
        print(f"Scraping {date_str} - Page {page}")
        url = BASE_URL_TEMPLATE.format(date=date_str, page=page)
        articles = get_articles_from_page(url)

        if not articles:
            break

        for article in articles:
            print(f"  → Fetching full article: {article['title']}")
            article["content"] = get_full_article_text(article["link"])
            time.sleep(1)

        all_articles.extend(articles)
        page += 1
        time.sleep(1)

    return all_articles

def save_to_json(articles, date_str):
    filename = os.path.join(SAVE_FOLDER, f"tempo_{date_str}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 2)

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"\n Starting scrape for {date_str}")
        articles = scrape_tempo_for_date(date_str)
        save_to_json(articles, date_str)
        print(f" Done with {date_str}: {len(articles)} articles saved.\n")
        current_date += timedelta(days=1)