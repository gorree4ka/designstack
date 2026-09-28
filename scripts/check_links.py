"""Обход сайта глазами робота Яндекса: все адреса карты сайта и все внутренние ссылки с них.

    python scripts/check_links.py                                # живой сайт
    python scripts/check_links.py --base http://localhost:8080   # локальный

Печатает каждый адрес, который ответил не 200 (переадресации не раскрываются), и страницу,
где ссылка найдена. Ссылки из <head> тоже считаются: робот ходит и по ним. Появился после
письма Вебмастера 28.09.2026 — ссылка урока на подборку и ленты разделов отвечали 404.
"""
import argparse
import concurrent.futures as cf
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
parser = argparse.ArgumentParser()
parser.add_argument("--base", default="https://designstack.ru")
BASE = parser.parse_args().base.rstrip("/")
HOST = urllib.parse.urlparse(BASE).netloc
UA = {"User-Agent": "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


opener = urllib.request.build_opener(NoRedirect)


def fetch(url, body=True):
    req = urllib.request.Request(url, headers=UA)
    try:
        with opener.open(req, timeout=60) as r:
            return r.status, (r.read().decode("utf-8", "replace") if body else ""), r.headers.get("Location")
    except urllib.error.HTTPError as e:
        return e.code, "", e.headers.get("Location")
    except Exception as e:  # noqa: BLE001
        return "ERR " + str(e)[:60], "", None


def sitemap():
    out = []
    _, root, _ = fetch(BASE + "/wp-sitemap.xml")
    for sm in re.findall(r"<loc>([^<]+)</loc>", root):
        _, xml, _ = fetch(sm)
        out += re.findall(r"<loc>([^<]+)</loc>", xml)
    return out


pages = sitemap()
print("адресов в карте:", len(pages))
links = {}

with cf.ThreadPoolExecutor(8) as pool:
    for url, (code, html, loc) in zip(pages, pool.map(fetch, pages)):
        if code != 200:
            print("КАРТА", code, url, loc or "")
        for href in re.findall(r'href="([^"#]+)', html):
            full = urllib.parse.urljoin(url, href.replace("&#038;", "&").replace("&amp;", "&"))
            if urllib.parse.urlparse(full).netloc == HOST:
                links.setdefault(full, url)

extra = [u for u in links if u not in set(pages)]
print("внутренних ссылок вне карты:", len(extra))
bad = 0

with cf.ThreadPoolExecutor(8) as pool:
    for u, (code, _, loc) in zip(extra, pool.map(lambda x: fetch(x, False), extra)):
        if code not in (200,):
            bad += 1
            print("ССЫЛКА", code, u, "→", loc or "", "| найдено на", links[u])

print("не 200:", bad)
sys.exit(1 if bad else 0)
