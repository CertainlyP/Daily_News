"""Content fetcher for Twitter and web articles."""
import json
import os
from typing import List, Dict
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup


class ContentFetcher:
    """Fetches content from various sources (Twitter, articles, etc.)."""

    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.twitter_session = self.config['settings']['twitter_session_file']
        self.max_tweets = self.config['settings']['max_tweets_per_account']

    def fetch_all(self) -> List[Dict]:
        """Fetch content from all configured sources."""
        all_content = []

        # Fetch Twitter posts
        if os.path.exists(self.twitter_session):
            print("Fetching Twitter posts...")
            twitter_content = self.fetch_twitter_posts()
            all_content.extend(twitter_content)
        else:
            print(f"⚠️  Twitter session file not found. Run setup_twitter.py first.")

        # Fetch articles
        print("Fetching articles...")
        article_content = self.fetch_articles()
        all_content.extend(article_content)

        return all_content

    def fetch_twitter_posts(self) -> List[Dict]:
        """Fetch posts from configured Twitter accounts using Playwright."""
        posts = []
        accounts = self.config['sources']['twitter_accounts']

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=self.twitter_session)
            page = context.new_page()

            for account in accounts:
                try:
                    print(f"  Fetching from @{account}...")
                    page.goto(f"https://twitter.com/{account}", timeout=30000)
                    page.wait_for_load_state("networkidle", timeout=20000)

                    # Wait for tweets to load
                    page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)

                    # Extract tweets
                    tweets = page.query_selector_all('article[data-testid="tweet"]')

                    for i, tweet in enumerate(tweets[:self.max_tweets]):
                        try:
                            # Extract tweet text
                            text_element = tweet.query_selector('[data-testid="tweetText"]')
                            text = text_element.inner_text() if text_element else ""

                            # Try to get tweet URL
                            time_element = tweet.query_selector('time')
                            tweet_url = f"https://twitter.com/{account}"
                            if time_element:
                                link = time_element.evaluate('el => el.parentElement.href')
                                if link:
                                    tweet_url = link

                            if text.strip():
                                posts.append({
                                    'source': f'@{account}',
                                    'url': tweet_url,
                                    'content': text,
                                    'type': 'twitter'
                                })
                        except Exception as e:
                            print(f"    Error extracting tweet {i}: {e}")
                            continue

                    print(f"    ✓ Fetched {min(len(tweets), self.max_tweets)} tweets")

                except Exception as e:
                    print(f"    ✗ Error fetching from @{account}: {e}")
                    continue

            browser.close()

        return posts

    def fetch_articles(self) -> List[Dict]:
        """Fetch articles from configured URLs using requests."""
        articles = []
        urls = self.config['sources']['article_urls']

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        for url in urls:
            try:
                print(f"  Fetching {url}...")
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Try to extract main content
                # Common article containers
                article = (
                    soup.find('article') or
                    soup.find('div', class_='content') or
                    soup.find('div', class_='post-content') or
                    soup.find('main')
                )

                if article:
                    # Remove script and style elements
                    for script in article(['script', 'style', 'nav', 'footer', 'aside']):
                        script.decompose()

                    text = article.get_text(separator='\n', strip=True)
                else:
                    text = soup.get_text(separator='\n', strip=True)

                # Clean up excessive whitespace
                text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())

                if text:
                    articles.append({
                        'source': url,
                        'url': url,
                        'content': text[:10000],  # Limit content length
                        'type': 'article'
                    })
                    print(f"    ✓ Fetched article ({len(text)} chars)")

            except Exception as e:
                print(f"    ✗ Error fetching {url}: {e}")
                continue

        return articles


if __name__ == "__main__":
    # Test the fetcher
    fetcher = ContentFetcher()
    content = fetcher.fetch_all()
    print(f"\n✓ Fetched {len(content)} items total")
    for item in content:
        print(f"  - {item['source']}: {len(item['content'])} chars")
