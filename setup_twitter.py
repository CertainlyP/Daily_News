"""One-time setup script to authenticate with Twitter and save session."""
import json
from playwright.sync_api import sync_playwright


def setup_twitter_session():
    """Interactive setup to log into Twitter and save session."""
    print("=== Twitter Session Setup ===")
    print("This will open a browser window for you to log into Twitter.")
    print("After logging in, press Enter in this terminal to save the session.\n")

    # Load config to get session file path
    with open('config.json', 'r') as f:
        config = json.load(f)
    session_file = config['settings']['twitter_session_file']

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to Twitter
        page.goto("https://twitter.com/login")

        # Wait for user to log in
        input("\n→ Log into Twitter in the browser window, then press Enter here...")

        # Verify login by checking if we can access home
        try:
            page.goto("https://twitter.com/home", timeout=10000)
            print("✓ Login successful!")
        except Exception as e:
            print(f"✗ Could not verify login: {e}")
            print("  Make sure you're fully logged in before continuing.")
            browser.close()
            return

        # Save session
        context.storage_state(path=session_file)
        print(f"✓ Session saved to {session_file}")
        print("\nYou can now run the main script to fetch Twitter posts.")

        browser.close()


if __name__ == "__main__":
    setup_twitter_session()
