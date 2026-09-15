"""Собирает иконки сайтов каталога, чтобы поставить их в плитку карточки.

Плитка логотипа нарисована ещё на этапе паттернов, но до сих пор показывала букву:
картинок у записей не было. Скрипт берёт с самого сайта ресурса его иконку —
`apple-touch-icon`, затем `icon`, затем `/favicon.ico`, — приводит к 128×128 на
прозрачном холсте и кладёт в `docs/content/logos/<слаг>.png`.

Ничего не публикует: в WordPress картинки заносит `scripts/import_logos.php` после
того, как иконки просмотрены глазами. Мелкие (меньше 48 px) и нераспознанные файлы
пропускаются — в карточке останется буквенная плитка, это нормальный исход.

Сайты обходятся в несколько потоков с коротким таймаутом: один медленный вендор
иначе держит очередь минутами (прогон 15.09.2026 встал на пятой записи из ста сорока).

    python scripts/fetch_logos.py .tmp/voice/current.json
    python scripts/fetch_logos.py .tmp/voice/current.json --only figma,miro --workers 12
"""
import argparse
import concurrent.futures
import io
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request

from PIL import Image

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
SIDE = 128
MIN_SIDE = 32
LINK = re.compile(r"<link\b[^>]*>", re.I)
ATTR = re.compile(r'(\w[\w-]*)\s*=\s*"([^"]*)"|(\w[\w-]*)\s*=\s*\'([^\']*)\'')

p = argparse.ArgumentParser()
p.add_argument("catalog", help="JSON с полями slug и url (выгрузка каталога)")
p.add_argument("--out", default="docs/content/logos", help="куда класть иконки")
p.add_argument("--only", default="", help="слаги через запятую — обработать только их")
p.add_argument("--timeout", type=int, default=8)
p.add_argument("--workers", type=int, default=10)
a = p.parse_args()

out_dir = pathlib.Path(a.out)
out_dir.mkdir(parents=True, exist_ok=True)
only = {s.strip() for s in a.only.split(",") if s.strip()}


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})

    with urllib.request.urlopen(req, timeout=a.timeout) as resp:
        return resp.read(3_000_000)


def attrs(tag: str) -> dict:
    out = {}

    for m in ATTR.finditer(tag):
        key = (m.group(1) or m.group(3) or "").lower()
        out[key] = m.group(2) if m.group(2) is not None else (m.group(4) or "")

    return out


def biggest(value: str) -> int:
    """Число из sizes="180x180"; «any» и пустое считаем нулём."""
    found = [int(x) for x in re.findall(r"(\d+)x\d+", value or "", re.I)]

    return max(found) if found else 0


def candidates(page: str, base: str) -> list:
    """Адреса иконок со страницы, от самой крупной к мелкой, плюс /favicon.ico."""
    found = []

    for tag in LINK.findall(page):
        at = attrs(tag)
        rel = (at.get("rel") or "").lower()

        if "icon" not in rel or "mask-icon" in rel:
            continue

        href = at.get("href") or ""

        if not href or href.startswith("data:") or href.endswith(".svg"):
            continue

        weight = biggest(at.get("sizes", ""))

        if "apple-touch-icon" in rel:
            weight = max(weight, 180)

        found.append((weight, urllib.parse.urljoin(base, href)))

    found.sort(key=lambda x: -x[0])
    parts = urllib.parse.urlsplit(base)
    found.append((0, urllib.parse.urlunsplit((parts.scheme, parts.netloc, "/favicon.ico", "", ""))))
    seen, out = set(), []

    for _, url in found:
        if url not in seen:
            seen.add(url)
            out.append(url)

    return out


def square(raw: bytes) -> Image.Image:
    """Картинка на прозрачном квадрате 128×128 без растягивания."""
    img = Image.open(io.BytesIO(raw))
    img.load()

    if img.mode not in ("RGBA", "LA"):
        img = img.convert("RGBA")

    if min(img.size) < MIN_SIDE:
        raise ValueError("мелкая: %dx%d" % img.size)

    img.thumbnail((SIDE, SIDE), Image.LANCZOS)
    canvas = Image.new("RGBA", (SIDE, SIDE), (0, 0, 0, 0))
    canvas.paste(img, ((SIDE - img.width) // 2, (SIDE - img.height) // 2), img)

    return canvas


def telegram_avatar(url: str) -> list:
    """Аватарка канала со страницы-превью t.me: иначе все каналы получают общий значок Telegram."""
    parts = urllib.parse.urlsplit(url)
    name = parts.path.strip("/").split("/")[0]

    if not name:
        return []

    preview = "https://t.me/s/" + name

    try:
        page = get(preview).decode("utf-8", "replace")
    except Exception:
        return []

    found = re.search(r'<meta property="og:image" content="([^"]+)"', page)

    return [found.group(1)] if found else []


# Имена, под которыми иконка лежит у сайтов без ссылки в разметке.
GUESSES = (
    "/apple-touch-icon.png", "/apple-touch-icon-precomposed.png", "/favicon.png",
    "/favicon-192x192.png", "/favicon-96x96.png", "/icon.png", "/logo.png", "/favicon.ico",
)


def grab(row: dict) -> tuple:
    slug, url = row.get("slug", ""), row.get("url", "")

    if not url:
        return slug, "", "адреса нет"

    parts = urllib.parse.urlsplit(url)

    if parts.netloc.endswith("t.me"):
        urls = telegram_avatar(url)
    else:
        urls = []

        try:
            urls = candidates(get(url).decode("utf-8", "replace"), url)
        except Exception:
            pass

        root = urllib.parse.urlunsplit((parts.scheme, parts.netloc, "", "", ""))
        urls += [root + guess for guess in GUESSES]

    for icon in urls[:10]:
        try:
            square(get(icon)).save(out_dir / ("%s.png" % slug))

            return slug, icon, "ок"
        except Exception:
            continue

    return slug, "", "иконки нет или она мелкая"


def svg_icons(url: str) -> list:
    """Адреса иконок в SVG: их много у документационных сайтов, растрового значка там нет."""
    try:
        page = get(url).decode("utf-8", "replace")
    except Exception:
        return []

    found = []

    for tag in LINK.findall(page):
        at = attrs(tag)
        rel = (at.get("rel") or "").lower()
        href = at.get("href") or ""

        if "icon" in rel and href and (href.endswith(".svg") or "svg" in (at.get("type") or "")):
            found.append(urllib.parse.urljoin(url, href))

    parts = urllib.parse.urlsplit(url)
    root = urllib.parse.urlunsplit((parts.scheme, parts.netloc, "", "", ""))

    return found + [root + "/favicon.svg", root + "/icon.svg"]


def rasterize(rows_left: list) -> list:
    """Снимает SVG-иконку браузером: Pillow векторы не открывает, а Playwright уже стоит."""
    from playwright.sync_api import sync_playwright

    out = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": SIDE, "height": SIDE})

        for row in rows_left:
            slug, url = row.get("slug", ""), row.get("url", "")
            saved = ""

            for icon in svg_icons(url)[:4]:
                try:
                    raw = get(icon)
                except Exception:
                    continue

                if b"<svg" not in raw[:4000]:
                    continue

                data = urllib.parse.quote(raw.decode("utf-8", "replace"))
                page.set_content(
                    '<body style="margin:0;background:transparent">'
                    '<img src="data:image/svg+xml;utf8,%s" width="%d" height="%d" '
                    'style="object-fit:contain">' % (data, SIDE, SIDE)
                )
                page.wait_for_timeout(200)
                page.screenshot(path=str(out_dir / ("%s.png" % slug)), omit_background=True)
                saved = icon

                break

            out.append((slug, saved, "ок (svg)" if saved else "иконки нет или она мелкая"))

        browser.close()

    return out


rows = [r for r in json.load(open(a.catalog, encoding="utf-8")) if not only or r.get("slug") in only]

with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
    report = list(pool.map(grab, rows))

failed = {slug for slug, _, note in report if note != "ок"}

if failed:
    print("SVG-проход для %d записей…" % len(failed))
    fixed = {slug: (slug, src, note) for slug, src, note in rasterize([r for r in rows if r["slug"] in failed])}
    report = [fixed.get(slug, (slug, src, note)) for slug, src, note in report]

done = sum(1 for _, _, note in report if note.startswith("ок"))

for slug, src, note in sorted(report, key=lambda r: (r[2] == "ок", r[0])):
    print("  %-26s %-24s %s" % (slug, note, src[:70]))

print("иконок собрано: %d из %d, папка: %s" % (done, len(rows), out_dir))
sys.exit(0)
