import random, time, os, requests
from playwright.sync_api import sync_playwright
from faker import Faker

def run_bing_automation():
    fake = Faker()
    
    with sync_playwright() as p:
        # Launch the browser once
        browser = p.chromium.launch(headless=True)
        
        # --- PHASE 1: DESKTOP SEARCHES ---
        print("🖥️ Starting Desktop Searches (30)...")
        desktop_context = browser.new_context(
            storage_state="auth.json",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        desktop_page = desktop_context.new_page()
        
        for i in range(30):
            query = fake.sentence(nb_words=random.randint(2, 3)).replace(".", "")
            desktop_page.goto(f"https://www.bing.com/search?q={query}&PC=U316&FORM=CHROMN")
            print(f"[PC {i+1}/30] {query}")
            time.sleep(random.randint(3, 6))
        
        # --- PHASE 2: VISUAL SEARCH (Integrated in Desktop Context) ---
        print("\n📷 Starting Visual Search...")
        try:
            # Get a random image
            img_resp = requests.get("https://picsum.photos/300/300", timeout=10)
            with open("temp_image.jpg", "wb") as f:
                f.write(img_resp.content)

            desktop_page.goto("https://www.bing.com")
            # Wait for the camera icon and upload
            desktop_page.set_input_files('input[type="file"]', "temp_image.jpg")
            time.sleep(8) # Wait for processing
            print(f"✅ Visual Search Complete: {desktop_page.url[:50]}...")
            os.remove("temp_image.jpg")
        except Exception as e:
            print(f"⚠️ Visual Search Error: {e}")
            
        desktop_context.close()

        # --- PHASE 3: MOBILE SEARCHES ---
        print("\n📱 Starting Mobile Searches (20)...")
        mobile_context = browser.new_context(
            storage_state="auth.json",
            user_agent="Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
            viewport={'width': 390, 'height': 844},
            is_mobile=True
        )
        mobile_page = mobile_context.new_page()

        for i in range(20):
            query = fake.word() + " " + fake.word()
            mobile_page.goto(f"https://www.bing.com/search?q={query}&PC=U316&FORM=CHROMN")
            print(f"[Mobile {i+1}/20] {query}")
            time.sleep(random.randint(3, 6))
            
        mobile_context.close()
        browser.close()
        print("\n🎉 All tasks finished successfully!")

if __name__ == "__main__":
    run_bing_automation()
