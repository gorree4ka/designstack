"""Результат проверки грейда: кнопка карты на первом экране и подписи круга профиля (D192).

Зачем: круг подписан названиями областей и ступенями, а раскладку подписей считает браузер по
размеру текста. Ошибку в ней глазами на одном профиле не поймать: подписи слипаются только
у некоторых сочетаний «длинное название + соседняя ось», а кегль на телефоне зависит от ширины.
Скрипт проходит проверку с четырьмя профилями (как у живого человека, всё на нуле, всё Senior,
вперемешку) на 1440×900, 1280×800, 375×667 и 375×812, в светлой и тёмной теме, и смотрит:

- кнопка «Открыть карту развития» стоит в карточке ориентира и видна без прокрутки;
- на круге 13 подписей, рамки подписей не пересекаются друг с другом и не заходят на круг;
- подписи целиком внутри рисунка, у рисунка есть viewBox по подписям;
- на телефоне название и ступень не мельче 12 пикселей;
- у страницы нет прокрутки вбок;
- в списке под кругом 13 строк с полными названиями и без номеров;
- контраст названия и ступени к фону страницы не ниже 4,5 : 1 (axe круг пропускает: он скрыт от диктора);
- axe на показанном результате, 1440 и 375, обе темы — без нарушений;
- «заново» доходит до первого вопроса: ссылки «Пройти проверку заново» на главной и на карте ведут
  на проверку с #again и открывают первый вопрос; на вступлении пройденной проверки есть «Пройти заново»;
  кнопка внизу результата тоже работает; старые ответы живы, пока не отмечен первый новый.

axe ставится один раз: `npm install axe-core --prefix .tmp/audit --no-save`; без него проверка падает.

    python scripts/check_grade_result.py
    python scripts/check_grade_result.py --base https://designstack.ru
"""
import argparse
import pathlib
import re
import sys

from playwright.sync_api import sync_playwright

p = argparse.ArgumentParser()
p.add_argument("--base", default="http://localhost:8080")
a = p.parse_args()
base = a.base.rstrip("/")
AXE = pathlib.Path(__file__).resolve().parent.parent / ".tmp/audit/node_modules/axe-core/axe.min.js"


def lum(rgb):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def ratio(fg, bg):
    x, y = sorted((lum(fg), lum(bg)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def rgb(css):
    return tuple(int(v) for v in re.findall(r"\d+", css)[:3])

# ступень ответа по областям: 0 — нет ступени, 1 — Junior, 2 — Middle, 3 — Senior
PROFILES = {
    "как у человека": [[1, 2, 1, 1], [2, 1, 1], [2, 1, 2, 1], [1, 2, 1], [1, 1, 2], [1, 2, 1], [1, 2, 1], [0, 1, 0],
                       [0, 0, 1], [0, 0, 0], [0, 1, 0, 0], [0, 0, 0], [0, 0, 1, 0]],
    "всё на нуле": [[0]] * 13,
    "всё Senior": [[3]] * 13,
    "вперемешку": [[3], [0], [3], [0], [2], [1], [3], [0], [2], [3], [0], [1], [3]],
}

FILL = """(plan) => {
  const order = ['junior', 'middle', 'senior'];
  const items = [...document.querySelectorAll('[data-check-q]')];
  const areas = [];
  items.forEach(it => { const a = it.querySelector('.ds-check__area').textContent; if (!areas.includes(a)) areas.push(a); });
  const seen = {};
  const kept = {};
  items.forEach(it => {
    const a = areas.indexOf(it.querySelector('.ds-check__area').textContent);
    const k = seen[a] = (seen[a] || 0);
    seen[a]++;
    const row = plan[a] || [0];
    const want = row[k % row.length];
    const inputs = [...it.querySelectorAll('input')];
    let idx = inputs.findIndex(i => want === 0 ? !i.getAttribute('data-grade') : i.getAttribute('data-grade') === order[want - 1]);
    if (idx < 0) idx = 0;
    kept[it.getAttribute('data-skill')] = idx;
  });
  localStorage.setItem('designstack-grade-check', JSON.stringify(kept));
}"""

MEASURE = """() => {
  const svg = document.querySelector('.ds-check__radar');
  const labels = [...svg.querySelectorAll('.ds-check__radar-label')];
  const box = svg.getBoundingClientRect();
  const rings = svg.querySelectorAll('.ds-check__radar-ring');
  const outer = rings[rings.length - 1].getBoundingClientRect();
  const cx = outer.left + outer.width / 2, cy = outer.top + outer.height / 2;
  const radius = Math.max(outer.width, outer.height) / 2;
  const rects = labels.map(l => l.getBoundingClientRect());
  const overlaps = [];
  for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) {
    const A = rects[i], B = rects[j];
    if (A.left < B.right - 0.5 && B.left < A.right - 0.5 && A.top < B.bottom - 0.5 && B.top < A.bottom - 0.5)
      overlaps.push(labels[i].textContent + ' × ' + labels[j].textContent);
  }
  // ближайшая к центру точка рамки подписи должна лежать снаружи внешнего кольца
  const onRing = [];
  rects.forEach((r, i) => {
    const nx = Math.max(r.left, Math.min(cx, r.right)), ny = Math.max(r.top, Math.min(cy, r.bottom));
    if (Math.hypot(nx - cx, ny - cy) < radius * 0.97) onRing.push(labels[i].textContent);
  });
  const outside = rects.filter(r => r.left < box.left - 0.5 || r.right > box.right + 0.5 || r.top < box.top - 0.5 || r.bottom > box.bottom + 0.5).length;
  const name = svg.querySelector('.ds-check__radar-name'), grade = svg.querySelector('.ds-check__radar-grade');
  const scale = box.width / svg.viewBox.baseVal.width;
  const card = document.querySelector('.ds-check__verdict');
  const btn = card && card.querySelector('a.ds-button');
  const rows = [...document.querySelectorAll('.ds-check__row-name')];
  return {
    labels: labels.length, overlaps, onRing, outside,
    namePx: parseFloat(getComputedStyle(name).fontSize) * scale,
    gradePx: parseFloat(getComputedStyle(grade).fontSize) * scale,
    btn: btn ? { text: btn.textContent, bottom: btn.getBoundingClientRect().bottom, href: btn.getAttribute('href') } : null,
    bottomMap: !!document.querySelector('.ds-check__map a.ds-button'),
    vh: innerHeight,
    wide: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    rows: rows.length, rowNums: document.querySelectorAll('.ds-check__row-num').length,
    rowNamesFull: rows.every(r => r.textContent.length > 0 && !/^\\d/.test(r.textContent)),
    radarW: Math.round(box.width), circle: Math.round(radius * 2),
    fill: getComputedStyle(svg.querySelector('.ds-check__radar-shape')).fill,
    colors: [...svg.querySelectorAll('.ds-check__radar-name, .ds-check__radar-grade')].map(t => getComputedStyle(t).fill),
    bg: getComputedStyle(document.body).backgroundColor,
  };
}"""

checks = []


def check(name, ok, note=""):
    checks.append((name, bool(ok), note))
    if not ok:
        print("  ✘", name, note)


with sync_playwright() as pw:
    browser = pw.chromium.launch()
    for (w, h) in ((1440, 900), (1280, 800), (375, 667), (375, 812)):
        for scheme in ("light", "dark"):
            for pname, plan in PROFILES.items():
                if scheme == "dark" and pname not in ("как у человека", "всё Senior"):
                    continue
                page = browser.new_page(viewport={"width": w, "height": h}, color_scheme=scheme)
                page.goto(base + "/grade-check/", wait_until="networkidle", timeout=60000)
                page.evaluate(FILL, plan)
                page.reload(wait_until="networkidle")
                page.click("[data-check-start]")
                page.wait_for_selector(".ds-check__radar-label")
                page.evaluate("document.fonts.ready")
                page.wait_for_timeout(300)
                page.evaluate("window.scrollTo(0, 0)")
                m = page.evaluate(MEASURE)
                tag = "%d×%d %s · %s" % (w, h, scheme, pname)
                check(tag + ": 13 подписей", m["labels"] == 13, str(m["labels"]))
                check(tag + ": подписи не пересекаются", not m["overlaps"], "; ".join(m["overlaps"]))
                check(tag + ": подписи не заходят на круг", not m["onRing"], ", ".join(m["onRing"]))
                check(tag + ": подписи внутри рисунка", m["outside"] == 0, str(m["outside"]))
                if w < 600:
                    check(tag + ": название не мельче 12 px", m["namePx"] >= 12, "%.1f" % m["namePx"])
                    check(tag + ": ступень не мельче 12 px", m["gradePx"] >= 11.95, "%.1f" % m["gradePx"])
                check(tag + ": кнопка карты в карточке ориентира", m["btn"] and m["btn"]["text"] == "Открыть карту развития" and m["btn"]["href"], str(m["btn"]))
                check(tag + ": кнопка видна без прокрутки", m["btn"] and m["btn"]["bottom"] <= m["vh"], str(m["btn"] and round(m["btn"]["bottom"])))
                check(tag + ": кнопка карты и внизу", m["bottomMap"])
                check(tag + ": нет прокрутки вбок", m["wide"] <= 0, str(m["wide"]))
                check(tag + ": 13 строк списка без номеров", m["rows"] == 13 and m["rowNums"] == 0 and m["rowNamesFull"], "%d/%d" % (m["rows"], m["rowNums"]))
                check(tag + ": заливка — градиент", "url(" in m["fill"], m["fill"])
                worst = min(ratio(rgb(c), rgb(m["bg"])) for c in set(m["colors"]))
                check(tag + ": контраст подписей не ниже 4,5", worst >= 4.5, "%.2f" % worst)
                if pname == "как у человека" and h in (900, 667):
                    if not AXE.exists():
                        check(tag + ": axe установлен", False, str(AXE))
                    else:
                        page.add_script_tag(path=str(AXE))
                        found = page.evaluate("async () => (await axe.run(document, {resultTypes: ['violations']})).violations.map(v => v.id + ' ×' + v.nodes.length)")
                        check(tag + ": axe без нарушений", not found, ", ".join(found))
                        print("%s: axe нарушений %d, худший контраст подписей %.2f" % (tag, len(found), worst))
                if pname == "как у человека" and scheme == "light":
                    print("%s: рисунок %d, круг %d, подписи %.1f/%.1f px, низ кнопки %d из %d" % (
                        tag, m["radarW"], m["circle"], m["namePx"], m["gradePx"], m["btn"]["bottom"], m["vh"]))
                page.close()
    # ---------- «заново» ----------
    plan = PROFILES["как у человека"]
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    def fresh(url):
        page.goto(base + "/grade-check/", wait_until="networkidle")
        page.evaluate(FILL, plan)
        page.goto(base + url, wait_until="networkidle")
        page.wait_for_timeout(200)

    def stored():
        return page.evaluate("Object.keys(JSON.parse(localStorage.getItem('designstack-grade-check') || '{}')).length")

    def first_question():
        return page.evaluate("""() => { const q = [...document.querySelectorAll('[data-check-q]')].filter(i => !i.hidden);
          return q.length === 1 && q[0] === document.querySelector('[data-check-q]')
            && document.querySelector('[data-check-intro]').hidden && document.querySelector('[data-check-result]').hidden; }""")

    fresh("/grade-check/")
    total = stored()
    check("заново: ответы сохранены", total == 37, str(total))
    check("заново: на вступлении «Посмотреть результат» и «Пройти заново»",
          page.evaluate("document.querySelector('[data-check-start]').textContent") == "Посмотреть результат"
          and page.is_visible("[data-check-restart]"))
    page.click("[data-check-restart]")
    check("заново: кнопка на вступлении открывает первый вопрос", first_question())
    check("заново: ответы целы, пока не отмечен новый", stored() == total, str(stored()))
    page.locator("[data-check-q]").first.locator("input").first.check()
    check("заново: первый новый ответ заменяет старые", stored() == 1, str(stored()))

    fresh("/grade-check/#again")
    check("заново: #again без перезагрузки открывает первый вопрос", first_question())
    page.goto(base + "/about/", wait_until="networkidle")
    page.goto(base + "/grade-check/#again", wait_until="networkidle")
    page.wait_for_timeout(200)
    check("заново: #again с другой страницы открывает первый вопрос", first_question())
    check("заново: #again убран из адреса", "#" not in page.url, page.url)
    check("заново: после #again ответы целы", stored() == total, str(stored()))

    fresh("/grade-check/")
    page.click("[data-check-start]")
    page.wait_for_selector(".ds-check__radar")
    page.locator(".ds-check__result .ds-check__actions button", has_text="Пройти заново").click()
    check("заново: кнопка внизу результата открывает первый вопрос", first_question())

    for path, sel in (("/", "[data-banner-again] a"), ("/map/", "[data-map-check]")):
        fresh(path)
        href = page.get_attribute(sel, "href") if page.query_selector(sel) else None
        check("заново: «Пройти проверку заново» на %s ведёт с #again" % path, href and href.endswith("#again"), str(href))
        if href:
            page.click(sel)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(200)
            check("заново: переход с %s открывает первый вопрос" % path, first_question())
    page.close()
    browser.close()

fails = [c for c in checks if not c[1]]
print("проверок: %d, провалов: %d" % (len(checks), len(fails)))
sys.exit(1 if fails else 0)
