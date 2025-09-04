import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

SAVE_FOLDER = "republic_articles"
os.makedirs(SAVE_FOLDER, exist_ok=True)

BASE_URL_TEMPLATE = "https://republika.co.id/index/{offset}/{date}"


def get_articles_from_republika_page(offset, date_str):
    url = BASE_URL_TEMPLATE.format(offset=offset, date=date_str)
    print(f"🔍 Trying URL: {url}")
    response = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    })
    if response.status_code != 200:
        print(f"❌ Failed to fetch page. Status: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    
    # DEBUG: print number of <li> elements found
    li_tags = soup.find_all("li", class_="list-group-item")
    print(f"✅ Found {len(li_tags)} <li> tags (all types)")
    
    article_tags = soup.find_all("li", class_="list-group-item list-border conten1")
    print(f"✅ Found {len(article_tags)} article tags with class 'conten1'")
    
    articles = []
    for li in article_tags:
        a_tag = li.find("a")
        if not a_tag or not a_tag.get("href"):
            continue

        link = a_tag["href"]
        title_tag = li.find("h3")
        title = title_tag.get_text(strip=True) if title_tag else ""

        date_tag = li.find("div", class_="date")
        timestamp = date_tag.get_text(strip=True) if date_tag else ""

        articles.append({
            "title": title,
            "link": link,
            "published": timestamp
        })

    return articles



def get_full_article_content_republika(url):
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        content_div = soup.find("div", class_="detail-artikel")  # main article text
        paragraphs = content_div.find_all("p") if content_div else []
        return " ".join(p.get_text(strip=True) for p in paragraphs)
    except Exception as e:
        print(f"Error fetching article at {url}: {e}")
        return None


def scrape_republika_for_date(date_str):
    all_articles = []
    for offset in [0, 50, 100, 150]:
        print(f"  🔹 Scraping offset {offset}")
        articles = get_articles_from_republika_page(offset, date_str)
        if not articles:
            break  # Stop if current offset yields no articles
        for article in articles:
            print(f"    - Fetching: {article['title']}")
            article["content"] = get_full_article_content_republika(article["link"])
            time.sleep(1)
        all_articles.extend(articles)
    return all_articles


def save_to_json(articles, date_str):
    filename = os.path.join(SAVE_FOLDER, f"republika_{date_str}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 1)
    current_date = start_date

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"\n Republika: Scraping for {date_str}")
        articles = scrape_republika_for_date(date_str)
        save_to_json(articles, date_str)
        print(f"Saved {len(articles)} articles for {date_str}")
        current_date += timedelta(days=1)