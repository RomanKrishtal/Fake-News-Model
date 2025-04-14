import requests
from bs4 import BeautifulSoup
from newspaper import Article
import feedparser
import pandas as pd
import time

fake_articles = []

def scrape_politifact():
    print("\n🔍 Scraping PolitiFact (False claims only)")
    for page in range(1, 21):
        url = f"https://www.politifact.com/factchecks/?page={page}"
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.content, "html.parser")

            quotes = soup.select(".m-statement__quote")
            ratings = soup.select(".m-statement__meter img")
            links = soup.select(".m-statement__quote a")

            for quote, rating, link in zip(quotes, ratings, links):
                verdict = rating['alt'].lower()
                if "false" in verdict:
                    text = quote.get_text(strip=True)
                    article_url = "https://www.politifact.com" + link['href']
                    fake_articles.append({
                        "title": text,
                        "text": text,
                        "url": article_url,
                        "source": "PolitiFact",
                        "label": 0
                    })
                    print(f"    ✔️ PolitiFact: {text[:60]}...")
            time.sleep(1)
        except Exception as e:
            print(f"    ❌ Error scraping PolitiFact page {page}: {e}")
            continue

def scrape_snopes():
    print("🔍 Scraping Snopes (Fact-check pages with real verdicts)")
    base_url = "https://www.snopes.com/fact-check/page/"

    for page in range(1, 11):  # scrape first 10 pages
        url = f"{base_url}{page}/"
        print(f"    📄 Page {page}: {url}")
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.content, "html.parser")
            cards = soup.select("article a.card--title")

            for card in cards:
                article_url = card['href']
                if not article_url.startswith("http"):
                    article_url = "https://www.snopes.com" + article_url
                print(f"    🔗 Checking article: {article_url}")

                try:
                    art_res = requests.get(article_url)
                    art_soup = BeautifulSoup(art_res.content, "html.parser")

                    rating_tag = art_soup.find("span", class_="rating-name")
                    verdict = rating_tag.get_text(strip=True).lower() if rating_tag else ""

                    if "false" in verdict or "miscaptioned" in verdict or "scam" in verdict:
                        article = Article(article_url)
                        article.download()
                        article.parse()

                        if len(article.text.strip()) > 200:
                            fake_articles.append({
                                "title": article.title,
                                "text": article.text,
                                "url": article_url,
                                "source": f"Snopes ({verdict})",
                                "label": 0
                            })
                            print(f"        ✔️ Added: {article.title[:60]}...")
                        else:
                            print("        ⚠️ Skipped: too short")
                    else:
                        print(f"        ⚠️ Skipped: verdict is '{verdict}'")

                    time.sleep(1)

                except Exception as e:
                    print(f"        ❌ Failed to process article: {e}")
                    continue

            time.sleep(1.5)

        except Exception as e:
            print(f"    ❌ Failed to load Snopes page {page}: {e}")
            continue

def scrape_onion():
    print("\n🔍 Scraping The Onion via RSS")
    rss_url = "https://www.theonion.com/rss"
    feed = feedparser.parse(rss_url)

    for entry in feed.entries:
        url = entry.link
        title = entry.title
        print(f"    🔗 Trying Onion article: {url}")
        try:
            article = Article(url)
            article.download()
            article.parse()

            if len(article.text.strip()) > 200:
                fake_articles.append({
                    "title": article.title,
                    "text": article.text,
                    "url": url,
                    "source": "The Onion (Satire)",
                    "label": 0
                })
                print(f"    ✔️ Onion: {article.title[:60]}...")
            time.sleep(1)

        except Exception as e:
            print(f"    ❌ Failed Onion article: {url} — {e}")
            continue

scrape_politifact()
scrape_snopes()
scrape_onion()

# Save to CSV
df_fake = pd.DataFrame(fake_articles)
df_fake.to_csv("verified_fake_news.csv", index=False)
print(f"\n✅ Done! Scraped {len(df_fake)} verified fake news articles.")