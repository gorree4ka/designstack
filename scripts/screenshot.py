"""Screenshot a page of the local site with Playwright (Chromium).

Usage:  python scripts/screenshot.py <url> [--width 1440] [--out .tmp/shots/<name>.png] [--full]
Default name comes from the URL path and width: tools-1440.png, home-375.png.
Without --full only the first screen is captured: height 900, or 812 below 600 px width.
Prints the path of the written file.
"""
import argparse, pathlib
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

p = argparse.ArgumentParser()
p.add_argument("url")
p.add_argument("--width", type=int, default=1440)
p.add_argument("--out")
p.add_argument("--full", action="store_true")
p.add_argument("--dark", action="store_true", help="emulate prefers-color-scheme: dark; the file name gets a -dark suffix")
a = p.parse_args()

name = (urlparse(a.url).path.strip("/").replace("/", "-") or "home") + ("-dark" if a.dark else "") + f"-{a.width}.png"
out = pathlib.Path(a.out or f".tmp/shots/{name}")
out.parent.mkdir(parents=True, exist_ok=True)
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": a.width, "height": 812 if a.width < 600 else 900},
                            color_scheme="dark" if a.dark else "light")
    page.goto(a.url, wait_until="networkidle", timeout=60000)
    page.screenshot(path=str(out), full_page=a.full)
    browser.close()
print(out)
