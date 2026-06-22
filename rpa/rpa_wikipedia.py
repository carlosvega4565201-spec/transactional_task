import os
import sys

import requests
from playwright.sync_api import sync_playwright

API_URL = os.getenv("API_URL", "http://localhost:8000")


def extract_first_paragraph(term: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Drive the real search box to demonstrate browser automation.
        page.goto("https://en.wikipedia.org/wiki/Main_Page", wait_until="domcontentloaded")
        page.fill("input[name='search']", term)
        page.press("input[name='search']", "Enter")
        page.wait_for_load_state("domcontentloaded")

        # The search may land on a results page; if so, open the first result.
        if "Special:Search" in page.url:
            first = page.locator("ul.mw-search-results li a").first
            if first.count():
                first.click()
                page.wait_for_load_state("domcontentloaded")

        title = page.locator("h1#firstHeading").inner_text()

        # Find the first substantive paragraph in the article body.
        paragraphs = page.locator("div.mw-parser-output > p")
        text = ""
        for i in range(paragraphs.count()):
            candidate = paragraphs.nth(i).inner_text().strip()
            if len(candidate) > 60:
                text = candidate
                break

        browser.close()

    print(f"[rpa] article: {title}")
    print(f"[rpa] first paragraph ({len(text)} chars):\n{text}\n")
    return text


def summarize(text: str) -> dict:
    res = requests.post(
        f"{API_URL}/assistant/summarize",
        json={"text": text},
        timeout=30,
    )
    res.raise_for_status()
    return res.json()


def main() -> None:
    term = sys.argv[1] if len(sys.argv) > 1 else "Artificial intelligence"
    print(f"[rpa] searching Wikipedia for: {term!r}")

    paragraph = extract_first_paragraph(term)
    if not paragraph:
        print("[rpa] could not extract a paragraph; aborting.")
        sys.exit(1)

    result = summarize(paragraph)
    print("[rpa] summary from API:")
    print(result["summary"])
    print(f"[rpa] logged as assistant_log id={result['log_id']}")


if __name__ == "__main__":
    main()
