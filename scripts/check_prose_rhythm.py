"""Ритм статей: подзаголовок стоит ближе к своему тексту, чем к предыдущему блоку (D189).

Зачем. 30.09.2026 в выпуске дайджеста у каждой новости появился свой подзаголовок, и он висел
посередине: колонка статьи `.ds-prose` давала один зазор 24 между всеми блоками. В уроках это
правило записано с 17.09.2026 (D168) и проверяется `check_lessons.py`, статьи им не охвачены.

Что проверяет на каждой статье — выпуски, подборки, обзоры из карты сайта и «О проекте»:
у каждого h2 и h3 в колонке текста зазор снизу не больше 16 и меньше зазора сверху.

    python scripts/check_prose_rhythm.py                               # локальный сайт
    python scripts/check_prose_rhythm.py --base https://designstack.ru  # живой
"""
import argparse
import re
import sys
import urllib.request

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
parser = argparse.ArgumentParser()
parser.add_argument("--base", default="http://localhost:8080")
args = parser.parse_args()
base = args.base.rstrip("/")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "DesignStack-check"})
    return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")


# Статьи — записи типа post из карты сайта: у них три раздела, и все идут через single.html.
urls = re.findall(r"<loc>([^<]+)</loc>", fetch(base + "/wp-sitemap-posts-post-1.xml")) + [base + "/about/"]
MEASURE = """() => {
  const root = document.querySelector('.ds-prose');
  if (!root) { return null; }
  const kids = [...root.children].filter(el => el.offsetParent !== null);
  const out = [];
  let heads = 0;
  for (let i = 1; i < kids.length - 1; i++) {
    const h = kids[i];
    if (!/^H[23]$/.test(h.tagName)) { continue; }
    heads++;
    const r = h.getBoundingClientRect();
    const up = Math.round(r.top - kids[i - 1].getBoundingClientRect().bottom);
    const down = Math.round(kids[i + 1].getBoundingClientRect().top - r.bottom);
    if (down > 16 || down >= up) { out.push(h.textContent.trim().slice(0, 40) + ': сверху ' + up + ', снизу ' + down); }
  }
  return {heads, out};
}"""

checks = []
with sync_playwright() as play:
    browser = play.chromium.launch()
    for width in (1440, 375):
        page = browser.new_page(viewport={"width": width, "height": 900})
        for url in urls:
            page.goto(url)
            got = page.evaluate(MEASURE)
            name = "%s @%d" % (url.replace(base, ""), width)
            if got is None:
                checks.append((name, False, "нет колонки .ds-prose"))
                continue
            checks.append((name, not got["out"], "; ".join(got["out"][:3]) + ("" if got["heads"] else " (подзаголовков нет)")))
        page.close()
    browser.close()

fails = [c for c in checks if not c[1]]
for name, ok, note in fails:
    print("  ПРОВАЛ  %s — %s" % (name, note))
print("страниц: %d, проверок: %d, провалов: %d" % (len(urls), len(checks), len(fails)))
sys.exit(1 if fails else 0)
