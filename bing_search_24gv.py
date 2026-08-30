import random
import time
from urllib.parse import quote

from faker import Faker
from playwright.sync_api import sync_playwright


def safe_goto(page, url, max_retries=3):
    """Navigate to URL with retry logic."""
    for attempt in range(max_retries):
        try:
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  ⚠️ Attempt {attempt + 1} failed: {str(e)[:60]}... Retrying...")
                time.sleep(2)
            else:
                print(f"  ❌ Failed after {max_retries} attempts. Skipping...")
                return False
    return False


def human_like_query(fake):
    """Generate less robotic Bing queries that still look natural."""
    topics = [
        "best coffee beans",
        "digital marketing agency",
        "meal prep ideas",
        "home office setup",
        "travel tips for europe",
        "best running shoes",
        "weather forecast",
        "how to grow basil",
        "local pizza near me",
        "small business ideas",
        "fitness routine for beginners",
        "SEO checklist",
        "budget travel guides",
        "car insurance quotes",
        "hair care tips",
        "best laptops for students",
        "iphone camera settings",
        "online learning platforms",
        "indoor plants care",
        "healthy breakfast recipes",
    ]

    # Mix a natural phrase with a more specific two-word tail
    if random.random() < 0.4:
        return random.choice(topics)

    prefix = random.choice([
        "best",
        "latest",
        "top",
        "how to",
        "cheap",
        "affordable",
        "simple",
        "easy",
    ])
    suffix = fake.word().title()
    tail = fake.word().title()
    return f"{prefix} {suffix} {tail}".strip()


def random_delay(min_sec=4, max_sec=12):
    time.sleep(random.uniform(min_sec, max_sec))


def run_desktop_batch(browser, storage_state_path):
    print("🖥️ Starting desktop Bing searches...")
    context = browser.new_context(
        storage_state=storage_state_path,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        viewport={"width": 1366, "height": 768},
        locale="en-US",
        extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
    )

    fake = Faker()
    for i in range(30):
        query = human_like_query(fake)
        page = context.new_page()
        search_url = f"https://www.bing.com/search?q={quote(query)}&PC=U316&FORM=CHROMN"

        print(f"[Desktop {i+1}/30] {query}")
        if safe_goto(page, search_url):
            page.wait_for_timeout(random.randint(1500, 4500))
            if i % 6 == 0:
                page.mouse.wheel(0, random.randint(400, 900))
                page.wait_for_timeout(random.randint(1000, 2600))
        page.close()
        random_delay(6, 12)

    context.close()


def run_mobile_batch(browser, storage_state_path):
    print("\n📱 Starting mobile Bing searches...")
    context = browser.new_context(
        storage_state=storage_state_path,
        user_agent="Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        viewport={"width": 390, "height": 844},
        is_mobile=True,
        locale="en-US",
        extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
    )

    fake = Faker()
    for i in range(20):
        query = human_like_query(fake)
        page = context.new_page()
        search_url = f"https://www.bing.com/search?q={quote(query)}&PC=U316&FORM=CHROMN"

        print(f"[Mobile {i+1}/20] {query}")
        if safe_goto(page, search_url):
            page.wait_for_timeout(random.randint(1200, 3800))
        page.close()
        random_delay(5, 11)

    context.close()


def run_searches():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        try:
            run_desktop_batch(browser, "auth_24gv.json")
            run_mobile_batch(browser, "auth_24gv.json")
        finally:
            browser.close()


if __name__ == "__main__":
    run_searches()
