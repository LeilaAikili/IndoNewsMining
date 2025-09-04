import requests
from bs4 import BeautifulSoup
import time
import json
import os
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

BASE_URL_TEMPLATE = "https://indeks.kompas.com/?site=all&date={date}&page={page}"
SAVE_FOLDER = "/Users/leila/Desktop/UNI/BT/IndoNewsArticles/kompas_articles"

# Create folder if it doesn't exist
os.makedirs(SAVE_FOLDER, exist_ok=True)

def get_articles_from_page(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []

    for item in soup.find_all("div", class_="articleItem"):
        link_tag = item.find("a", class_="article-link")
        link = link_tag["href"] if link_tag else None

        title_tag = item.find("h2", class_="articleTitle")
        title = title_tag.get_text(strip=True) if title_tag else None

        date_tag = item.find("div", class_="articlePost-date")
        published_date = date_tag.get_text(strip=True) if date_tag else None

        if title and link:
            articles.append({
                "title": title,
                "link": link,
                "time": published_date,
            })  

    return articles

def get_full_article_text(url):
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find("div", class_="read__content")
        if not paragraphs:
            return None

        text = " ".join([p.get_text(strip=True) for p in paragraphs.find_all("p")])
        return text
    except Exception as e:
        print(f"Error fetching article {url}: {e}")
        return None

def scrape_kompas_for_date(date_str):
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
    filename = os.path.join(SAVE_FOLDER, f"kompas_{date_str}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    start_date = datetime(2024, 12, 26)
    end_date = datetime(2024, 12, 31)

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"\nStarting scrape for {date_str}")
        articles = scrape_kompas_for_date(date_str)
        save_to_json(articles, date_str)
        print(f" Done with {date_str}: {len(articles)} articles saved.\n")
        current_date += timedelta(days=1)