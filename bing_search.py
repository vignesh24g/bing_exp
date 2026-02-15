import random, time, os
from playwright.sync_api import sync_playwright
from faker import Faker

def run_searches():
    fake = Faker()
    with sync_playwright() as p:
        # Load the saved session from auth.json
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        for i in range(50):
            query = fake.sentence(nb_words=random.randint(2, 4)).replace(".", "")
            page.goto(f"https://www.bing.com/search?q={query}&PC=U316&FORM=CHROMN")
            
            print(f"[{i+1}/50] Searched: {query}")
            # Random wait to mimic human behavior
            time.sleep(random.randint(15, 35))
            
        browser.close()

if __name__ == "__main__":
    run_searches()
