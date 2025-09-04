import requests
from bs4 import BeautifulSoup
import re


class TemplateScraper:
    def scrape(self, data: dict) -> dict:
        """
        Scrape relevant information from the provided data.

        :param data: Dictionary containing information about a news article.
        :return: Dictionary with scraped information (title, URL, source, published date, and cleaned content).
        """
        title = data.get("title", "")
        self.url = data.get("link", "")
        source = data.get("source", "")
        published = data.get("published", "")
        content = self.clean(self.fetch_article_content())
        return {"title": title, "url": self.url, "source": source, "published": published, "content": content} if content else None

    def clean(self, text: str) -> str:
        """
        Clean the given text by removing unnecessary characters and extra whitespaces.

        :param text: Raw text to be cleaned.
        :return: Cleaned text.
        """
        if text:
            text = text.replace("\n", " ").replace("\r", "")
            text = "".join(char for char in text if ord(char) < 128)
            text = re.sub(
                r"[\x00-\x1F\x7F-\x9F\u200B-\u200D\u2028-\u2029\u3000]", "", text)
            text = re.sub(r"\s{2,}", " ", text)
            return text.strip()

    def fetch_article_content(self) -> str:
        """
        Placeholder method for fetching the article content.
        This method needs to be implemented in subclasses.

        :return: Raw content of the article.
        """
        pass


class BBCScraper(TemplateScraper):
    def __init__(self, url):
        self.url = url

    def fetch_article_content(self):
        response = requests.get(self.url)
        try:
            soup = BeautifulSoup(response.content, "html.parser")
            article_ele = soup.find("main")
            unwanted = article_ele.find("figure")
            unwanted.extract()  # Remove media images (optional)
            content = " ".join([p.get_text(strip=True)
                               for p in article_ele.find_all("p")])
            if not content:
                raise Exception("No content found")
            print(f"retrieved content from {self.url}")
            return content
        except Exception as e:
            print(f"failed to retrieve content from {self.url}: {e}")
            return ""


def fetch_bbc_articles_from_2024():
    # Base URL for BBC News Archive (you might want to adjust this URL based on the BBC's structure)
    base_url = "https://www.bbc.com/news"
    
    # Example of URL format; this should be customized or paginated based on the website's URL structure for 2024 articles
    bbc_urls_2024 = [
        # These URLs are examples; you may need to programmatically collect them or use a search endpoint.
        "https://www.bbc.com/news/world-xyz123",  # Example article URL from 2024
        "https://www.bbc.com/news/uk-abc456",    # Another example
        # Add more URLs or implement logic to fetch article links for 2024 from the archive
    ]
    
    articles = []
    
    for url in bbc_urls_2024:
        bbc_scraper = BBCScraper(url)
        article_data = {
            "title": "Example Article Title",  # You could extract this from the page
            "link": url,
            "source": "BBC",
            "published": "2024-01-01",  # Adjust this to extract the real publish date
        }
        article = bbc_scraper.scrape(article_data)
        if article:
            articles.append(article)
    
    return articles


# Example usage
all_articles_2024 = fetch_bbc_articles_from_2024()

# Print all the articles for 2024
for article in all_articles_2024:
    print(article["title"])
    print(article["url"])
    print(article["published"])
    print(article["content"])
    print("\n---\n")
