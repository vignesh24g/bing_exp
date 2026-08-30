import argparse
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def load_storage_state(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_cookie_expiry(storage_state):
    cookies = storage_state.get("cookies", [])
    now = time.time()
    valid = []
    expired = []

    for cookie in cookies:
        exp = cookie.get("expires")
        if exp is None:
            continue
        name = cookie.get("name", "UNKNOWN")
        try:
            exp_val = float(exp)
        except (TypeError, ValueError):
            continue

        if exp_val <= now:
            expired.append((name, exp_val))
        else:
            valid.append((name, exp_val))

    return valid, expired


def print_cookie_summary(path):
    state = load_storage_state(path)
    valid, expired = check_cookie_expiry(state)

    print(f"\n=== {path} ===")
    print(f"Total cookies: {len(state.get('cookies', []))}")
    print(f"Valid cookies: {len(valid)}")
    print(f"Expired cookies: {len(expired)}")

    if expired:
        for name, exp in expired[:10]:
            print(f"  EXPIRED: {name} -> {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(exp))}")
    if valid:
        for name, exp in valid[:10]:
            print(f"  VALID:   {name} -> {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(exp))}")


def test_search_on_bing(path, headless=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(storage_state=path)
        page = context.new_page()

        print(f"\n--- Loading Bing with {path} ---")
        page.goto("https://www.bing.com/search?q=session+health+test", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        url = page.url
        body_text = page.locator("body").inner_text()
        lower_text = body_text.lower()

        sign_in_signals = [
            "sign in",
            "sign in to save",
            "welcome back",
            "microsoft account",
            "continue with microsoft",
            "log in",
        ]

        results_signals = [
            "results for",
            "search results",
            "about",
            "people also ask",
        ]

        print(f"Final URL: {url}")

        if "login.live.com" in url or "login.microsoftonline.com" in url:
            print("STATUS: AUTH EXPIRED or NOT LOGGED IN")
        elif any(s in lower_text for s in sign_in_signals):
            print("STATUS: AUTH EXPIRED or NOT LOGGED IN")
        elif any(s in lower_text for s in results_signals):
            print("STATUS: SEARCH PAGE WORKING")
        else:
            print("STATUS: UNKNOWN - page loaded but login/search state is unclear")

        browser.close()


def main():
    parser = argparse.ArgumentParser(description="Check Bing storage state expiration and if Bing searches work")
    parser.add_argument("path", nargs="?", default="auth_24gv.json", help="Path to the storage_state JSON file")
    parser.add_argument("--headed", action="store_true", help="Open browser visibly instead of headless")
    parser.add_argument("--all", action="store_true", help="Check both auth_24gv.json and auth_vizz.json")
    args = parser.parse_args()

    headless = not args.headed

    if args.all:
        for file_name in ["auth_24gv.json", "auth_vizz.json"]:
            print_cookie_summary(file_name)
            test_search_on_bing(file_name, headless=headless)
    else:
        path = Path(args.path)
        print_cookie_summary(str(path))
        test_search_on_bing(str(path), headless=headless)


if __name__ == "__main__":
    main()
