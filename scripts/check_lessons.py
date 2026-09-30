"""Ширина на 375, тренажёр, копирование, атрибут hidden, ритм отступов, якоря, внутренние ссылки и «Что почитать дальше» во всех уроках — в браузере.

    python scripts/check_lessons.py                               # локальный сайт
    python scripts/check_lessons.py --base https://designstack.ru  # живой

Список уроков берётся из папки `docs/content/lessons`: что лежит там телом, то и проверяем.

Тренажёр: нажимаем первый вариант первого вопроса и смотрим, что счёт изменился
верно. В опубликованном уроке про интервью он был сломан — разметка отдавала
`data-good`, а скрипт с 17.09.2026 ждёт `data-answer`, и любой ответ считался
неверным. Копирование: кнопку рисует скрипт, значит она обязана появиться.
"""
import argparse
import pathlib
import sys

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument("--base", default="http://localhost:8080")
args = parser.parse_args()

LESSONS = sorted(p.name.replace(".body.html", "") for p in (ROOT / "docs/content/lessons").glob("*.body.html"))
HIDDEN = """() => [...document.querySelectorAll('#ds-main [hidden]')]
  .filter(el => el.offsetParent !== null || getComputedStyle(el).display !== 'none')
  .map(el => el.tagName + '.' + el.className).slice(0, 6)"""
# Ритм: зазор между соседними блоками урока. Блок без поля — таблица, плашка, коробка —
# слипается с соседом; глазом это видно сразу, а проверками до 17.09.2026 не ловилось:
# 135 слипшихся пар в девяти уроках нашла заказчица на скриншоте.
RHYTHM = """() => {
  const out = [];
  const label = el => el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : '');
  const block = el => ['DIV', 'DETAILS', 'FIGURE', 'TABLE'].includes(el.tagName);
  const flow = (parent, need) => {
    const kids = [...parent.children].filter(el => el.offsetParent !== null);
    for (let i = 1; i < kids.length; i++) {
      const a = kids[i - 1], b = kids[i];
      const gap = Math.round(b.getBoundingClientRect().top - a.getBoundingClientRect().bottom);
      // Подпись жмётся к своему блоку, а подзаголовок — к тому, что под ним: это близость по смыслу.
      const close = b.classList.contains('ds-lesson__dim') || b.classList.contains('ds-lesson__lead')
        || /^H[3-6]$/.test(a.tagName);
      const want = need || (close ? 8 : (block(a) || block(b) ? 16 : 8));
      if (gap < want) { out.push(label(a) + ' → ' + label(b) + ': ' + gap + 'px при норме ' + want); }
    }
  };
  const root = document.querySelector('.ds-lesson > div:not([class])') || document.querySelector('.ds-lesson');
  if (!root) { return ['нет корня урока .ds-lesson']; }
  flow(root, 32);
  root.querySelectorAll(':scope > section').forEach(s => flow(s, 0));
  return out;
}"""
# Контраст по WCAG: цвет текста, рамки или заливки против первого непрозрачного фона под ним.
# Прозрачность (неактивная кнопка) сводится к цвету поверх того, что под ней. Число в подписи
# округлено вниз до сотых, как в самом уроке: 4,499 не превращается в 4,5.
CONTRAST = """() => {
  const rgb = c => { const m = c.match(/rgba?\\(([^)]+)\\)/); if (!m) return null;
    const p = m[1].split(',').map(parseFloat); return {c: p.slice(0, 3), a: p.length > 3 ? p[3] : 1}; };
  const lum = p => { const f = v => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(p[0]) + 0.7152 * f(p[1]) + 0.0722 * f(p[2]); };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const mix = (a, b, t) => a.map((v, i) => t * v + (1 - t) * b[i]);
  const under = el => { for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const b = rgb(getComputedStyle(n).backgroundColor); if (b && b.a >= 1) return b.c; } return [255, 255, 255]; };
  const faded = el => { let a = 1, top = null; for (let n = el; n && !n.hasAttribute('data-contrast-demo'); n = n.parentElement) {
      const o = parseFloat(getComputedStyle(n).opacity); if (o < 1) { a *= o; top = n; } } return {a, top}; };
  const pair = (host, kind) => {
    const s = getComputedStyle(host);
    let fg = kind === 'fill' ? rgb(s.backgroundColor).c : kind === 'border' ? rgb(s.borderTopColor).c : rgb(s.color).c;
    let bg = kind === 'text' ? under(host) : under(host.parentElement);
    const f = faded(host);
    if (f.top) { const back = under(f.top.parentElement);
      fg = mix(fg, back, f.a); if (f.top.contains(host) && (kind === 'text')) { bg = mix(bg, back, f.a); } }
    return Math.floor(ratio(fg, bg) * 100) / 100;
  };
  const read = t => { const m = (t || '').match(/(\\d+),(\\d+)\\s*:\\s*1/); return m ? parseFloat(m[1] + '.' + m[2]) : null; };
  const out = {total: 0, bad: []};
  document.querySelectorAll('[data-contrast-demo] .ds-lesson__cr').forEach(cr => {
    const want = read(cr.textContent.replace(/(\\d),(\\d+)(?!\\s*:)/, '$1,$2 : 1'));
    const host = cr.getAttribute('data-of') === 'prev' ? cr.previousElementSibling : cr.parentElement;
    const got = pair(host, cr.getAttribute('data-pair') || 'text');
    out.total++; if (want !== got) out.bad.push(cr.textContent.trim() + ' → замер ' + got);
  });
  // Образец в таблице сверяется с числом в своей ячейке, а если там числа нет — с числом строки:
  // в строке бывает два образца, светлой и тёмной темы.
  document.querySelectorAll('[data-contrast-demo] tr .ds-lesson__cs-badge').forEach(sample => {
    const cell = sample.closest('td, th');
    const own = cell ? read(cell.textContent) : null;
    const want = own !== null ? own : read(sample.closest('tr').textContent);
    if (want === null) return;
    const got = pair(sample, 'text');
    out.total++; if (want !== got) out.bad.push(sample.textContent.trim() + ': ' + want + ' → замер ' + got);
  });
  return out;
}"""
fails = 0
LINKS = {}  # адрес → код ответа, общий для всех уроков

with sync_playwright() as play:
    browser = play.chromium.launch()
    page = browser.new_page()
    # Узкий экран: урок не шире окна телефона. 30.09.2026 скрытая подпись для диктора
    # (`screen-reader-text`, position: absolute) внутри листающейся таблицы вставала
    # от страницы и растягивала её на 54 пикселя — глазом на компьютере не видно.
    phone = browser.new_page(viewport={"width": 375, "height": 800})

    for slug in LESSONS:
        phone.goto(args.base.rstrip("/") + "/lessons/" + slug + "/")
        phone.wait_for_timeout(250)
        wide = phone.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        page.goto(args.base.rstrip("/") + "/lessons/" + slug + "/")
        page.wait_for_timeout(400)
        print("\n=== " + slug)
        print(("  ок  " if wide <= 0 else "  ПЛОХО ") + "на 375 не шире окна" + ("" if wide <= 0 else ": на %d пикселей" % wide))
        fails += 0 if wide <= 0 else 1

        leak = page.evaluate(HIDDEN)
        print(("  ок  " if not leak else "  ПЛОХО ") + "[hidden] скрывает" + (": " + str(leak) if leak else ""))
        fails += 1 if leak else 0

        tight = page.evaluate(RHYTHM)
        more = " и ещё %d" % (len(tight) - 4) if len(tight) > 4 else ""
        print(("  ок  " if not tight else "  ПЛОХО ") + "ритм: соседние блоки не слипаются"
              + ("" if not tight else " — " + "; ".join(tight[:4]) + more))
        fails += 1 if tight else 0

        # Якорь на странице один: второй `id="read"` увёл бы ссылку оглавления в чужой раздел.
        twins = page.evaluate("""() => { const seen = {}, twice = new Set();
            document.querySelectorAll('[id]').forEach(el => { if (seen[el.id]) twice.add(el.id); seen[el.id] = 1; });
            return [...twice]; }""")
        print(("  ок  " if not twins else "  ПЛОХО ") + "якоря не повторяются" + (": " + str(twins) if twins else ""))
        fails += 1 if twins else 0

        # «Что почитать дальше» — список, а не подвал одним абзацем (замечание заказчицы 27.09.2026).
        reads = page.evaluate("""() => [document.querySelectorAll('#further-reading .ds-lesson__reads li').length,
            document.querySelectorAll('.ds-lesson footer').length]""")
        ok = reads[0] > 0 and reads[1] == 0
        print(("  ок  " if ok else "  ПЛОХО ") + "«Что почитать дальше»: пунктов %d, подвалов %d" % tuple(reads))
        fails += 0 if ok else 1

        # Внутренние ссылки урока отвечают 200 без переадресации. 28.09.2026 в уроке «Типографика,
        # Middle» ушла на сайт ссылка /shrifty-s-kirillicey/ вместо /collections/…: 404, и её нашёл
        # только обход сайта после письма Вебмастера.
        hrefs = page.evaluate("""() => [...new Set([...document.querySelectorAll('#ds-main a[href]')]
            .map(a => a.href.split('#')[0]).filter(h => h.startsWith(location.origin)))]""")
        dead = []

        for href in hrefs:
            if href not in LINKS:
                try:
                    LINKS[href] = page.request.get(href, max_redirects=0).status
                except Exception as error:  # noqa: BLE001
                    LINKS[href] = str(error)[:40]
            if LINKS[href] != 200:
                dead.append("%s %s" % (LINKS[href], href.replace(args.base.rstrip("/"), "")))

        print(("  ок  " if not dead else "  ПЛОХО ") + "внутренние ссылки отвечают 200: %d из %d"
              % (len(hrefs) - len(dead), len(hrefs)) + (" — " + "; ".join(dead[:4]) if dead else ""))
        fails += 1 if dead else 0

        # Образцы контраста (`data-contrast-demo`): axe их пропускает, поэтому каждое число
        # в тексте сверяем с замером того, что нарисовано. Иначе поправка цвета в разметке
        # молча разойдётся с подписью «5,81 : 1».
        demo = page.evaluate(CONTRAST)

        if demo["total"]:
            bad = demo["bad"]
            print(("  ок  " if not bad else "  ПЛОХО ") + "контраст образцов совпадает с подписью: %d из %d"
                  % (demo["total"] - len(bad), demo["total"]) + (" — " + "; ".join(bad[:4]) if bad else ""))
            fails += 1 if bad else 0

        # тренажёр: отвечаем верно на первый вопрос каждого тренажёра
        boxes = page.query_selector_all("[data-quiz]")
        print("  тренажёров:", len(boxes))

        for number, box in enumerate(boxes, 1):
            item = box.query_selector("[data-quiz-q]:not([hidden])")
            key = item.get_attribute("data-answer") if item else None
            option = box.query_selector('[data-quiz-answer="%s"]' % key) if key else None

            if not option:
                print("  ПЛОХО тренажёр %d: ключ ответа %r не совпал ни с одной кнопкой" % (number, key))
                fails += 1
                continue

            option.click()
            page.wait_for_timeout(80)
            score = box.query_selector("[data-quiz-score]").inner_text()
            ok = score.startswith("1")
            print(("  ок  " if ok else "  ПЛОХО ") + "тренажёр %d: верный ответ даёт «%s»" % (number, score))
            fails += 0 if ok else 1

        holders = page.query_selector_all("[data-copy]")

        if holders:
            made = [h for h in holders if h.query_selector("button")]
            ok = len(made) == len(holders)
            print(("  ок  " if ok else "  ПЛОХО ") + "кнопок копирования: %d из %d" % (len(made), len(holders)))
            fails += 0 if ok else 1

    browser.close()

print("\nнеудач:", fails)
sys.exit(1 if fails else 0)
