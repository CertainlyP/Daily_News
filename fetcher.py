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

        if not accounts:
            print("  No Twitter accounts configured.")
            return posts

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=self.twitter_session)
            page = context.new_page()

            # Verify login first
            try:
                print("  Verifying Twitter session...")
                page.goto("https://twitter.com/home", timeout=30000)
                page.wait_for_timeout(3000)

                # Check if we're actually logged in
                if "login" in page.url:
                    print("    ✗ Twitter cookies expired or invalid")
                    print("    → Get fresh cookies:")
                    print("       1. Open twitter.com in browser (logged in)")
                    print("       2. F12 → Application → Cookies")
                    print("       3. Copy auth_token and ct0 values")
                    print("       4. Update twitter_session.json")
                    browser.close()
                    return posts

                print("    ✓ Session valid")
            except Exception as e:
                print(f"    ✗ Session check failed: {e}")
                browser.close()
                return posts

            for account in accounts:
                try:
                    print(f"  Fetching from @{account}...")
                    page.goto(f"https://twitter.com/{account}", timeout=60000)
                    page.wait_for_timeout(5000)  # Simple wait

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
        """Fetch individual articles from listing pages."""
        articles = []
        listing_urls = self.config['sources']['article_urls']
        max_articles = self.config['settings'].get('max_articles_per_source', 5)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        for listing_url in listing_urls:
            try:
                print(f"  Fetching listing page: {listing_url}")
                response = requests.get(listing_url, headers=headers, timeout=15)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract article links from listing page
                article_links = []

                # For bleepingcomputer and similar sites
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    # Make absolute URL
                    if href.startswith('/'):
                        from urllib.parse import urljoin
                        href = urljoin(listing_url, href)

                    # Filter for article URLs (avoid navigation, tags, etc.)
                    if '/news/' in href or '/article' in href or '/20' in href:
                        if href not in article_links and href != listing_url:
                            article_links.append(href)

                print(f"    Found {len(article_links)} potential articles")

                # Fetch first N articles
                for article_url in article_links[:max_articles]:
                    try:
                        print(f"    Fetching article: {article_url[:60]}...")
                        article_response = requests.get(article_url, headers=headers, timeout=10)
                        article_response.raise_for_status()

                        article_soup = BeautifulSoup(article_response.content, 'html.parser')

                        # Extract article content
                        article_content = (
                            article_soup.find('article') or
                            article_soup.find('div', class_='article_section') or
                            article_soup.find('div', class_='content') or
                            article_soup.find('div', class_='post-content') or
                            article_soup.find('main')
                        )

                        if article_content:
                            # Remove junk
                            for junk in article_content(['script', 'style', 'nav', 'footer', 'aside', 'iframe', 'form']):
                                junk.decompose()

                            text = article_content.get_text(separator='\n', strip=True)
                        else:
                            # Fallback
                            text = article_soup.get_text(separator='\n', strip=True)

                        # Clean whitespace
                        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())

                        if text and len(text) > 200:  # Only keep if substantial content
                            articles.append({
                                'source': article_url,
                                'url': article_url,
                                'content': text[:15000],  # Limit length
                                'type': 'article'
                            })
                            print(f"      ✓ Extracted article ({len(text)} chars)")

                    except Exception as e:
                        print(f"      ✗ Error fetching article: {e}")
                        continue

            except Exception as e:
                print(f"    ✗ Error fetching listing page {listing_url}: {e}")
                continue

        return articles


if __name__ == "__main__":
    # Test the fetcher
    fetcher = ContentFetcher()
    content = fetcher.fetch_all()
    print(f"\n✓ Fetched {len(content)} items total")
    for item in content:
        print(f"  - {item['source']}: {len(item['content'])} chars")
