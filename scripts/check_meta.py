"""Описание страницы для поиска и превью ссылок — на каждой странице из карты сайта.

До 28.09.2026 обрезка описания в плагине (`designstack_core_trim`) снимала хвостовые знаки
побайтовым `rtrim`, и у текста, который обрывался на «р» или «Д», отрезался байт буквы:
строка переставала быть UTF-8, `esc_attr()` отдавал пустоту, и у карточки не было описания
ни в выдаче, ни в превью. Глазом на странице это не видно — только в разметке `<head>`.

    python scripts/check_meta.py                               # локальный сайт
    python scripts/check_meta.py --base https://designstack.ru  # живой

Проверяем: `description` и `og:description` есть, не пустые, совпадают, не длиннее 160 знаков
и не оборваны посреди буквы. Список адресов — из `/wp-sitemap.xml` и вложенных карт.
"""
import argparse
import html
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

parser = argparse.ArgumentParser()
parser.add_argument("--base", default="http://localhost:8080")
BASE = parser.parse_args().base.rstrip("/")
UA = {"User-Agent": "Mozilla/5.0 (DesignStack check_meta)"}
LIMIT = 160


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def sitemap_urls():
    root = get(BASE + "/wp-sitemap.xml")
    urls = []

    for sub in re.findall(r"<loc>([^<]+)</loc>", root):
        urls += re.findall(r"<loc>([^<]+)</loc>", get(html.unescape(sub)))

    return sorted(set(html.unescape(u) for u in urls))


def check(url):
    try:
        page = get(url)
    except Exception as err:  # noqa: BLE001
        return url, ["не открылась: %s" % err]

    head = page.split("</head>", 1)[0]
    desc = re.findall(r'<meta name="description" content="([^"]*)"', head)
    og = re.findall(r'<meta property="og:description" content="([^"]*)"', head)
    bad = []

    if len(desc) != 1 or len(og) != 1:
        bad.append("тегов description %d, og:description %d" % (len(desc), len(og)))
    else:
        text = html.unescape(desc[0])

        if not text.strip():
            bad.append("пустое описание")
        if desc[0] != og[0]:
            bad.append("description и og:description разные")
        if len(text) > LIMIT:
            bad.append("длина %d" % len(text))
        if "�" in text:
            bad.append("битый символ в описании")

    return url, bad


urls = sitemap_urls()

with ThreadPoolExecutor(max_workers=6) as pool:
    results = list(pool.map(check, urls))

fails = [(u, b) for u, b in results if b]

for url, bad in fails:
    print("  ПЛОХО %s — %s" % (url.replace(BASE, ""), "; ".join(bad)))

print("страниц из карты сайта: %d, с ошибкой описания: %d" % (len(urls), len(fails)))
sys.exit(1 if fails or not urls else 0)
