import random, time, os
from playwright.sync_api import sync_playwright
from faker import Faker

def safe_goto(page, url, max_retries=3):
    """Navigate to URL with retry logic"""
    for attempt in range(max_retries):
        try:
            page.goto(url, timeout=30000)
            return
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  ⚠️ Attempt {attempt + 1} failed: {str(e)[:50]}... Retrying...")
                time.sleep(2)  # Wait before retry
            else:
                print(f"  ❌ Failed after {max_retries} attempts. Skipping...")

def run_searches():
    fake = Faker()
    with sync_playwright() as p:
        # 1. Setup Browser
        browser = p.chromium.launch(headless=True)
        
        # --- DESKTOP SEARCHES (approx 30-50 daily) ---
        print("🖥️ Starting Desktop Searches...")
        desktop_context = browser.new_context(
            storage_state="auth_vizz.json",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        desktop_page = desktop_context.new_page()
        
        for i in range(100):
            query = fake.sentence(nb_words=random.randint(2, 3)).replace(".", "")
            safe_goto(desktop_page, f"https://www.bing.com/search?q={query}&PC=U316&FORM=CHROMN")
            print(f"[PC {i+1}/50] {query}")
            time.sleep(random.randint(3, 7)) # Optimized speed
        desktop_context.close()

        # --- MOBILE SEARCHES (approx 20 daily) ---
        print("\n📱 Starting Mobile Searches...")
        mobile_context = browser.new_context(
            storage_state="auth_vizz.json",
            # Mobile User-Agent + Viewport triggers mobile points
            user_agent="Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
            viewport={'width': 375, 'height': 667},
            is_mobile=True
        )
        mobile_page = mobile_context.new_page()

        for i in range(50):
            query = fake.word() + " " + fake.word()
            safe_goto(mobile_page, f"https://www.bing.com/search?q={query}&PC=U316&FORM=CHROMN")
            print(f"[Mobile {i+1}/20] {query}")
            time.sleep(random.randint(3, 7)) # Optimized speed
        mobile_context.close()

        browser.close()

if __name__ == "__main__":
    run_searches()
