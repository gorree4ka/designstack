"""Инфографика и «Коротко» в выпусках дайджеста (D190): масштаб, источник, ссылки, ширина.

Зачем. С 30.09.2026 у новостей выпуска есть инфографика — вёрстка на токенах, числа лежат
в разметке пользовательскими свойствами. Глазом не видно, что столбец нарисован не в масштабе,
что у схемы потерялся источник или что ссылка из «Коротко» ведёт в пустоту, — это ловит скрипт.

Что проверяет на каждом выпуске из карты сайта, на ширине 1440 и 375:
1. у каждой инфографики есть подпись и источник;
2. длина столбца, доли и отметки пропорциональна числу от нуля — расхождение не больше 1,5 %;
3. число, написанное у столбца, совпадает с его значением в разметке;
4. каждая ссылка «Коротко» ведёт на единственный элемент с этим id, и id на странице не повторяются;
5. страница и каждая инфографика не шире окна.

    python scripts/check_infographics.py                               # локальный сайт
    python scripts/check_infographics.py --base https://designstack.ru  # живой
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


urls = [u for u in re.findall(r"<loc>([^<]+)</loc>", fetch(base + "/wp-sitemap-posts-post-1.xml")) if "/digest/" in u]
MEASURE = """() => {
  const num = (el, name) => parseFloat(getComputedStyle(el).getPropertyValue(name));
  const w = el => el.getBoundingClientRect().width;
  const out = {figs: 0, bad: [], brief: 0};
  document.querySelectorAll('.ds-infographic').forEach((f, n) => {
    out.figs++;
    const name = '#' + (n + 1) + ' ' + (f.querySelector('.ds-infographic__title') || {textContent: '?'}).textContent.trim().slice(0, 30);
    if (!f.querySelector('.ds-infographic__title')) out.bad.push(name + ': нет подписи');
    const src = f.querySelector('.ds-infographic__source');
    if (!src || !src.textContent.trim()) out.bad.push(name + ': нет источника');
    if (f.scrollWidth > f.clientWidth + 1) out.bad.push(name + ': шире своей колонки на ' + (f.scrollWidth - f.clientWidth));
    f.querySelectorAll('.ds-infographic__bar').forEach(bar => {
      const track = bar.querySelector('.ds-infographic__bar-track');
      const fill = bar.querySelector('.ds-infographic__bar-fill');
      const mark = bar.querySelector('.ds-infographic__bar-mark');
      const v = num(bar, '--v'), max = num(bar, '--max'), m = num(bar, '--m');
      const got = w(fill) / w(track), want = v / max;
      if (Math.abs(got - want) > 0.015) out.bad.push(name + ': столбец ' + v + ' нарисован как ' + Math.round(got * max));
      if (mark) { const at = (mark.getBoundingClientRect().left - track.getBoundingClientRect().left) / w(track);
        if (Math.abs(at - m / max) > 0.015) out.bad.push(name + ': отметка ' + m + ' стоит на ' + Math.round(at * max)); }
      const txt = (bar.querySelector('.ds-infographic__bar-value') || {textContent: ''}).textContent.replace(/\\s/g, '');
      if (!txt.includes(String(v))) out.bad.push(name + ': у столбца написано «' + txt + '», в разметке ' + v);
    });
    const parts = [...f.querySelectorAll('.ds-infographic__share-part')];
    if (parts.length) {
      const sum = parts.reduce((s, p) => s + num(p, '--v'), 0);
      const total = parts.reduce((s, p) => s + w(p), 0);
      parts.forEach(p => { const want = num(p, '--v') / sum, got = w(p) / total;
        if (Math.abs(got - want) > 0.015) out.bad.push(name + ': доля ' + num(p, '--v') + ' нарисована как ' + Math.round(got * sum)); });
    }
    f.querySelectorAll('.ds-infographic__meter').forEach(mt => {
      const fill = mt.querySelector('.ds-infographic__meter-fill'), track = mt.querySelector('.ds-infographic__meter-track');
      const got = w(fill) / w(track), want = num(fill, '--v') / 100;
      if (Math.abs(got - want) > 0.015) out.bad.push(name + ': шкала ' + num(fill, '--v') + ' % нарисована как ' + Math.round(got * 100));
    });
  });
  const ids = {};
  document.querySelectorAll('[id]').forEach(el => { ids[el.id] = (ids[el.id] || 0) + 1; });
  Object.keys(ids).filter(k => ids[k] > 1).forEach(k => out.bad.push('id повторяется: ' + k));
  document.querySelectorAll('.ds-brief a').forEach(a => {
    out.brief++;
    const id = decodeURIComponent((a.getAttribute('href') || '').replace(/^#/, ''));
    if (!a.getAttribute('href').startsWith('#') || ids[id] !== 1) out.bad.push('«Коротко» ведёт в пустоту: ' + a.getAttribute('href'));
  });
  if (document.documentElement.scrollWidth > innerWidth) out.bad.push('страница шире окна на ' + (document.documentElement.scrollWidth - innerWidth));
  return out;
}"""

checks = []
with sync_playwright() as play:
    browser = play.chromium.launch()
    for width in (1440, 375):
        page = browser.new_page(viewport={"width": width, "height": 900})
        for url in urls:
            page.goto(url)
            got = page.evaluate(MEASURE)
            name = "%s @%d (инфографик %d, ссылок «Коротко» %d)" % (url.replace(base, ""), width, got["figs"], got["brief"])
            checks.append((name, not got["bad"], "; ".join(got["bad"][:4])))
        page.close()
    browser.close()

fails = [c for c in checks if not c[1]]
for name, ok, note in checks:
    print(("  ок      " if ok else "  ПРОВАЛ  ") + name + ("" if ok else " — " + note))
print("выпусков: %d, проверок: %d, провалов: %d" % (len(urls), len(checks), len(fails)))
sys.exit(1 if fails else 0)
