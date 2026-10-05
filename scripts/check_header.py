"""Шапка на граничных ширинах: пункты меню не наезжают на поиск, кнопки и логотип.

    python scripts/check_header.py                               # локальный сайт
    python scripts/check_header.py --base https://designstack.ru  # живой

Прежняя проверка раскладки сравнивала ширину страницы с окном — и не видела, что пункт
меню целиком ушёл под поле поиска: шапка от этого не становится шире. 05.10.2026 так
«О проекте» был спрятан под поиском на 1200–1300 и упирался в кнопку на 900 (лист P30, D197).
Здесь меряются прямоугольники видимых элементов ряда шапки: пункты меню между собой и с
логотипом, полем поиска, его кнопкой, значками меню, поиска и темы. Пересечение или зазор
меньше 4 px — провал; пункт, вылезший за правый край окна, — тоже.
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

parser = argparse.ArgumentParser()
parser.add_argument("--base", default="http://localhost:8080")
args = parser.parse_args()
BASE = args.base.rstrip("/")

PAGES = ["/", "/lessons/", "/map/", "/tools/"]
WIDTHS = [1920, 1440, 1439, 1300, 1200, 1199, 1000, 900, 899, 600, 375]
GAP = 4

MEASURE = """(gap) => {
  const bar = document.querySelector('.ds-header__bar');
  if (!bar) return {error: 'нет .ds-header__bar'};
  const top = bar.getBoundingClientRect().bottom;
  // Закрытый <details> в Chrome прячет содержимое через content-visibility: у скрытых пунктов
  // остаются размеры и offsetParent. Поэтому содержимое закрытой панели не считается видимым.
  const hidden = el => { const d = el.closest('details'); return d && !d.open && !el.closest('summary'); };
  const visible = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return !hidden(el) && r.width > 0 && r.height > 0 && r.top < top && s.visibility !== 'hidden' && el.offsetParent !== null; };
  const box = (el, name) => { const r = el.getBoundingClientRect(); return {name, l: r.left, r: r.right, t: r.top, b: r.bottom}; };
  const links = [...bar.querySelectorAll('.ds-header__nav a')].filter(visible).map(a => box(a, 'пункт «' + a.textContent.trim() + '»'));
  const ctrls = [];
  const add = (sel, name) => bar.querySelectorAll(sel).forEach(el => { if (visible(el)) ctrls.push(box(el, name)); });
  add('.ds-header__logo', 'логотип');
  add('.ds-search__field', 'поле поиска');
  add('.ds-search--header button', 'кнопка «Найти»');
  add('.ds-header__search-toggle', 'значок поиска');
  add('.ds-header__menu-toggle', 'значок меню');
  add('.ds-theme-toggle', 'кнопка темы');
  const bad = [];
  const hit = (a, b) => a.l < b.r + gap && b.l < a.r + gap && a.t < b.b && b.t < a.b;
  links.forEach((a, i) => {
    if (a.r > innerWidth) bad.push(a.name + ' за правым краем окна');
    links.slice(i + 1).forEach(b => { if (hit(a, b)) bad.push(a.name + ' и ' + b.name); });
    ctrls.forEach(c => { if (hit(a, c)) bad.push(a.name + ' и ' + c.name + ' (зазор ' + Math.round(Math.max(c.l - a.r, a.l - c.r)) + ')'); });
  });
  return {links: links.length, ctrls: ctrls.map(c => c.name), bad};
}"""

fails = 0
with sync_playwright() as play:
    browser = play.chromium.launch()
    for path in PAGES:
        print("\n=== " + path)
        for width in WIDTHS:
            page = browser.new_page(viewport={"width": width, "height": 800})
            page.goto(BASE + path, wait_until="networkidle")
            page.wait_for_timeout(200)
            out = page.evaluate(MEASURE, GAP)
            page.close()
            if out.get("error"):
                print("  ПЛОХО %d: %s" % (width, out["error"]))
                fails += 1
                continue
            ok = not out["bad"]
            print(("  ок  " if ok else "  ПЛОХО ") + "%d: пунктов меню в ряду %d" % (width, out["links"])
                  + ("" if ok else " — " + "; ".join(out["bad"][:3])))
            fails += 0 if ok else 1
    browser.close()

print("\nнеудач:", fails)
sys.exit(1 if fails else 0)
