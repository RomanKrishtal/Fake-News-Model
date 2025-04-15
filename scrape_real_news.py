import feedparser
from newspaper import Article
import pandas as pd
import time
import os

rss_feeds = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.theguardian.com/uk/rss",
    "http://rss.cnn.com/rss/edition.rss",
    "http://rss.cnn.com/rss/edition_world.rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://feeds.npr.org/1004/rss.xml"
]

real_articles = []
existing_urls = set()

# Load existing articles if the file exists
if os.path.exists("real_news_auto.csv"):
    existing_df = pd.read_csv("real_news_auto.csv")
    existing_urls = set(existing_df["url"].tolist())
    print(f"🔁 Loaded {len(existing_urls)} existing articles")
else:
    existing_df = pd.DataFrame()

# Start scraping
for feed_url in rss_feeds:
    print(f"\n🔍 Parsing feed: {feed_url}")
    feed = feedparser.parse(feed_url)

    for entry in feed.entries:
        url = entry.link
        if url in existing_urls:
            continue
        try:
            article = Article(url)
            article.download()
            article.parse()
            real_articles.append({
                "title": article.title,
                "text": article.text,
                "url": url,
                "label": 1
            })
            existing_urls.add(url)
            print(f"✔️ Scraped: {article.title}")
            time.sleep(1)
        except Exception as e:
            print(f"❌ Failed to scrape: {url} — {e}")
            continue

# Combine and save
new_df = pd.DataFrame(real_articles)
combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset="url")
combined_df.to_csv("real_news_auto.csv", index=False)
print(f"\n✅ Done! Total unique articles saved: {len(combined_df)}")