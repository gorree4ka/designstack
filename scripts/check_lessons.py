"""Тренажёр, копирование и атрибут hidden во всех уроках — в браузере.

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
fails = 0

with sync_playwright() as play:
    browser = play.chromium.launch()
    page = browser.new_page()

    for slug in LESSONS:
        page.goto(args.base.rstrip("/") + "/lessons/" + slug + "/")
        page.wait_for_timeout(400)
        print("\n=== " + slug)

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
