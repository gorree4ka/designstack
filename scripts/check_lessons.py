"""Тренажёр, копирование, атрибут hidden и ритм отступов во всех уроках — в браузере.

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
fails = 0

with sync_playwright() as play:
    browser = play.chromium.launch()
    page = browser.new_page()

    for slug in LESSONS:
        page.goto(args.base.rstrip("/") + "/lessons/" + slug + "/")
        page.wait_for_timeout(400)
        print("\n=== " + slug)

        leak = page.evaluate(HIDDEN)
        print(("  ок  " if not leak else "  ПЛОХО ") + "[hidden] скрывает" + (": " + str(leak) if leak else ""))
        fails += 1 if leak else 0

        tight = page.evaluate(RHYTHM)
        more = " и ещё %d" % (len(tight) - 4) if len(tight) > 4 else ""
        print(("  ок  " if not tight else "  ПЛОХО ") + "ритм: соседние блоки не слипаются"
              + ("" if not tight else " — " + "; ".join(tight[:4]) + more))
        fails += 1 if tight else 0

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
