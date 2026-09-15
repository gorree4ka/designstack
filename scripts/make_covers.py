"""Рисует обложки статей 1200×630 в оформлении сайта: заголовок, подпись, логотип.

Обложка нужна дважды: как изображение записи и как превью ссылки в мессенджере.
Раньше превью было одно на весь раздел («Подборка. Отобрано и проверено вручную»),
поэтому все статьи в ленте выглядели одинаково.

Рисуется браузером по шаблону на наших токенах и шрифтах темы — никаких чужих
картинок и стоков. Вход — JSON со списком записей:

    [{"slug": "...", "kind": "Подборка", "title": "...", "note": "..."}]

    python scripts/make_covers.py docs/content/covers/covers.json
    python scripts/make_covers.py covers.json --out docs/content/covers
"""
import argparse
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = (ROOT / "wordpress/wp-content/themes/designstack/assets/fonts").as_uri()

p = argparse.ArgumentParser()
p.add_argument("list", help="JSON со списком обложек")
p.add_argument("--out", default="docs/content/covers", help="куда класть PNG")
a = p.parse_args()

out_dir = pathlib.Path(a.out)
out_dir.mkdir(parents=True, exist_ok=True)

TEMPLATE = """<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>
@font-face { font-family: "Golos Text"; src: url("FONTS/golos-text-variable.woff2") format("woff2");
             font-weight: 400 900; font-display: block; }
* { margin: 0; box-sizing: border-box; }
body { width: 1200px; height: 630px; padding: 72px 80px; background: #f7f8f9; color: #14181b;
       font-family: "Golos Text", system-ui, sans-serif; display: flex; flex-direction: column;
       justify-content: space-between; }
.rule { width: 96px; height: 8px; border-radius: 4px; background: #037a8f; }
.kind { margin-top: 28px; font-size: 24px; font-weight: 500; color: #5b6770; letter-spacing: 0.02em; }
h1 { margin-top: 18px; font-size: SIZEpx; font-weight: 700; line-height: 1.12; letter-spacing: -0.02em;
     max-width: 20ch; text-wrap: balance; }
.note { margin-top: 20px; font-size: 26px; line-height: 1.35; color: #5b6770; max-width: 34ch; }
.brand { display: flex; align-items: center; gap: 14px; font-size: 26px; font-weight: 700; }
.mark { width: 46px; height: 46px; color: #037a8f; flex: none; }
</style></head><body>
<div><div class="rule"></div><div class="kind">KIND</div><h1>TITLE</h1><div class="note">NOTE</div></div>
<div class="brand"><svg class="mark" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" fill="currentColor"><polygon points="32,5 56,17 32,29 8,17"/><polygon points="32,20 56,32 32,44 8,32" opacity=".72"/><polygon points="32,35 56,47 32,59 8,47" opacity=".45"/></svg>DesignStack</div>
</body></html>"""


def size_for(title: str) -> int:
    """Кегль под длину заголовка: длинный заголовок иначе выходит за поле."""
    if len(title) <= 40:
        return 72

    if len(title) <= 60:
        return 62

    return 54


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


rows = json.load(open(a.list, encoding="utf-8"))

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": 1200, "height": 630})

    for row in rows:
        html = (TEMPLATE
                .replace("FONTS", FONTS)
                .replace("SIZE", str(size_for(row["title"])))
                .replace("KIND", escape(row.get("kind", "")))
                .replace("TITLE", escape(row["title"]))
                .replace("NOTE", escape(row.get("note", ""))))
        page.set_content(html)
        page.wait_for_timeout(300)
        path = out_dir / ("%s.png" % row["slug"])
        page.screenshot(path=str(path))
        print("  %-34s %s" % (row["slug"], path))

    browser.close()

print("обложек нарисовано:", len(rows))
sys.exit(0)
