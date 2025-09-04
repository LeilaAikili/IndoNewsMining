import requests
from bs4 import BeautifulSoup
import time
import json
import os
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

SAVE_FOLDER = "tribunnews_articles"
os.makedirs(SAVE_FOLDER, exist_ok=True)

BASE_URL_TEMPLATE = "https://wartakota.tribunnews.com/index-news?date={date}"

def get_articles_from_wartakota_index(date_str):
    url = BASE_URL_TEMPLATE.format(date=date_str)
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []

    li_tags = soup.find_all("li", class_="ptb15")
    for li in li_tags:
        time_tag = li.find("time")
        title_tag = li.find("h3", class_="f16 fbo")
        link_tag = title_tag.find("a") if title_tag else None

        if not link_tag:
            continue

        title = link_tag.get_text(strip=True)
        link = link_tag.get("href")

        articles.append({
            "title": title,
            "link": link,
            "published": time_tag.get_text(strip=True) if time_tag else ""
        })

    return articles

def get_full_article_content(url):
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find("div", class_="side-article txt-article")  # This may vary per article
        if not content_div:
            content_div = soup.find("div", class_="txt-article")  # fallback

        paragraphs = content_div.find_all("p") if content_div else []
        full_text = " ".join(p.get_text(strip=True) for p in paragraphs)
        return full_text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_wartakota_for_date(date_str):
    articles = get_articles_from_wartakota_index(date_str)
    for article in articles:
        print(f"Fetching: {article['title']}")
        article["content"] = get_full_article_content(article["link"])
        time.sleep(1)
    return articles

def save_to_json(articles, date_str):
    filename = os.path.join(SAVE_FOLDER, f"wartakota_{date_str}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    current_date = start_date

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"\n📅 Scraping WartaKota for {date_str}")
        articles = scrape_wartakota_for_date(date_str)
        save_to_json(articles, date_str)
        print(f"✅ {len(articles)} articles saved for {date_str}")
        current_date += timedelta(days=1)
