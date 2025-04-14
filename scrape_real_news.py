import feedparser
from newspaper import Article
import pandas as pd
import time

rss_feeds = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.theguardian.com/world/rss",
    "http://rss.cnn.com/rss/edition.rss"
]

real_articles = []

for feed_url in rss_feeds:
    print(f"\n🔍 Parsing feed: {feed_url}")
    feed = feedparser.parse(feed_url)

    for entry in feed.entries:
        url = entry.link
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
            print(f"✔️ Scraped: {article.title}")
            time.sleep(1)
        except Exception as e:
            print(f"❌ Failed to scrape: {url} — {e}")
            continue

# Convert to DataFrame and save
df_real = pd.DataFrame(real_articles)
df_real.to_csv("real_news_auto.csv", index=False)
print(f"\n✅ Done! Scraped {len(df_real)} articles.")