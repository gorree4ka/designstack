"""Прогон живых кусков уроков в браузере: темы «Юзабилити-тесты» и «Анализ конкурентов».

    python scripts/check_lesson_widgets.py [--base https://designstack.ru]

Проверяем три вещи по каждому уроку:
1. Что атрибут `hidden` действительно скрывает — правило раздела 10 про `[hidden]`
   против `display`. Меряем по `offsetParent`, а не по разметке.
2. Что без скрипта страница читается: всё содержимое видно.
3. Что со скриптом упражнение работает — нажимаем и смотрим на результат.
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

parser = argparse.ArgumentParser()
parser.add_argument("--base", default="http://localhost:8080")
BASE = parser.parse_args().base.rstrip("/") + "/lessons/"
HIDDEN = """() => {
  const all = [...document.querySelectorAll('#ds-main [hidden]')];
  return all.filter(el => el.offsetParent !== null || getComputedStyle(el).display !== 'none')
            .map(el => el.tagName + '.' + el.className).slice(0, 8);
}"""


def head(title):
    print("\n=== " + title)


def say(ok, text):
    print(("  ок  " if ok else "  ПЛОХО ") + text)

    return ok


fails = 0

with sync_playwright() as play:
    browser = play.chromium.launch()

    # --- без скрипта: страница должна читаться целиком ---
    plain = browser.new_context(java_script_enabled=False)

    for slug, must in (
        ("usability-testing-junior", ["Нажал «⋯» → «Отменить заказ»", "Показать ответ" ]),
        ("usability-testing-middle", ["личный кабинет", "Модерируемый"]),
        ("usability-testing-senior", ["П-018"]),
    ):
        page = plain.new_page()
        page.goto(BASE + slug + "/")
        head(slug + " · без скрипта")
        text = page.inner_text("#ds-main")

        for phrase in must:
            if phrase == "Показать ответ":
                continue
            fails += 0 if say(phrase in text, "видно: " + phrase) else 1

        buttons = page.eval_on_selector_all(
            "#ds-main button",
            "els => els.filter(e => e.offsetParent !== null).map(e => e.textContent.trim())",
        )
        fails += 0 if say(not buttons, "мёртвых кнопок нет" + (": " + str(buttons) if buttons else "")) else 1
        page.close()

    plain.close()

    # --- со скриптом ---
    ctx = browser.new_context()

    page = ctx.new_page()
    page.goto(BASE + "usability-testing-junior/")
    page.wait_for_timeout(400)
    head("usability-testing-junior · со скриптом")

    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1

    # чек-лист
    page.check("[data-checklist] input >> nth=0")
    page.wait_for_timeout(100)
    state = page.inner_text("[data-checklist-state]")
    fails += 0 if say(state.startswith("1 из"), "чек-лист считает: " + state) else 1

    # секундомер: запускаем, ждём, бьём по подсказке
    fails += 0 if say(
        page.is_visible("[data-sim-controls] button"), "кнопки секундомера созданы скриптом"
    ) else 1
    page.click("[data-sim-controls] button >> nth=0")
    page.wait_for_timeout(1200)
    page.click("[data-sim-controls] button >> nth=1")
    page.wait_for_timeout(200)
    shown = page.eval_on_selector_all(
        "[data-sim-verdict]", "els => els.filter(e => !e.hidden).map(e => e.getAttribute('data-sim-verdict'))"
    )
    said = page.eval_on_selector_all(
        "[data-sim-said]", "els => els.map(e => e.textContent).filter(Boolean)"
    )
    fails += 0 if say(shown == ["11"], "разбор подсказки на первой секунде: " + str(shown)) else 1
    fails += 0 if say(bool(said), "секунды подставлены: " + str(said)) else 1

    # карточки-ответы
    page.click(".ds-lesson__card summary >> nth=0")
    fails += 0 if say(page.is_visible(".ds-lesson__card .ds-lesson__ans >> nth=0"), "карточка раскрывается") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "usability-testing-middle/")
    page.wait_for_timeout(400)
    head("usability-testing-middle · со скриптом")

    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1

    marked = page.eval_on_selector_all(".ds-lesson__word.is-picked", "els => els.length")
    fails += 0 if say(marked == 0, "отметки сняты, слова чистые") else 1
    page.click('[data-word="1"] >> nth=0')
    page.click("[data-marks-actions] button")
    page.wait_for_timeout(150)
    meta = page.inner_text("[data-marks-meta]")
    back = page.is_visible("[data-marks-back]")
    fails += 0 if say("Нашли: 1 из 5" in meta, "проверка разметки считает: " + meta) else 1
    fails += 0 if say(back, "разбор открылся после проверки") else 1

    # подбор формата: четыре раза жмём первый вариант → модерируемый
    for _ in range(4):
        page.click("[data-pick-step]:not([hidden]) .ds-lesson__pick-opt >> nth=0")
        page.wait_for_timeout(80)

    out = page.eval_on_selector_all(
        "[data-pick-out]", "els => els.filter(e => !e.hidden).map(e => e.getAttribute('data-pick-out'))"
    )
    score = page.inner_text("[data-pick-score]")
    fails += 0 if say(out == ["mod"], "исход подбора: " + str(out)) else 1
    fails += 0 if say("4" in score and "Модерируемый" in score, "счёт: " + score.replace("\n", " ")) else 1

    # матрица
    page.click('[data-mx] button[data-mx-row="1"][data-mx-count="3"]')
    page.wait_for_timeout(120)
    out = page.inner_text("[data-mx-out]")
    fails += 0 if say("3 из 5" in out and "Критично" in out, "матрица объясняет клетку: " + out[:80]) else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "usability-testing-senior/")
    page.wait_for_timeout(400)
    head("usability-testing-senior · со скриптом")

    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1

    hidden_vd = page.eval_on_selector_all(
        ".ds-lesson__panel .ds-lesson__vd", "els => els.filter(e => e.offsetParent !== null).length"
    )
    fails += 0 if say(hidden_vd == 0, "разборы заявок спрятаны до ответа") else 1
    page.click("[data-panel-acts] button >> nth=0")
    page.wait_for_timeout(120)
    score = page.inner_text("[data-panel-score]")
    opened = page.eval_on_selector_all(
        ".ds-lesson__panel .ds-lesson__vd", "els => els.filter(e => e.offsetParent !== null).length"
    )
    fails += 0 if say(score.lower().startswith("1 из"), "счёт заявок: " + score) else 1
    fails += 0 if say(opened == 1, "разбор открылся у одной карточки") else 1

    # калькулятор
    out = page.inner_text("[data-calc-out]")
    fails += 0 if say("₽" in out and out != "—", "калькулятор посчитал: " + out) else 1
    page.select_option('[data-calc-field="outcome"]', "churn")
    page.wait_for_timeout(120)
    after = page.inner_text("[data-calc-out]")
    label = page.inner_text("[data-calc-label]")
    say_text = page.inner_text("[data-calc-say]")
    fails += 0 if say(after != out, "смена последствия меняет ответ: " + after) else 1
    fails += 0 if say("Маржинальный" in label, "подпись поля: " + label) else 1
    fails += 0 if say("{" not in say_text and len(say_text) > 40, "формулировка собрана: " + say_text[:70]) else 1
    page.close()

    # ─── тема «Анализ конкурентов» ───────────────────────────────────────────
    plain = browser.new_context(java_script_enabled=False)

    for slug, must in (
        ("competitor-analysis-junior", ["Магазин А", "Аналог 1", "ozon_02_карточка-заказа_.png", "Шаг 2 из 3"]),
        ("competitor-analysis-middle", ["Уровень 4 · ограничение", "Проверяем у себя", "есть у всех пяти аналогов"]),
        ("competitor-analysis-senior", ["Обратимость вместо подтверждения"]),
    ):
        page = plain.new_page()
        page.goto(BASE + slug + "/")
        head(slug + " · без скрипта")
        text = page.inner_text("#ds-main")

        for phrase in must:
            # Подписи с `text-transform: uppercase` приходят в innerText заглавными.
            fails += 0 if say(phrase.lower() in text.lower(), "видно: " + phrase) else 1

        buttons = page.eval_on_selector_all(
            "#ds-main button",
            "els => els.filter(e => e.offsetParent !== null).map(e => e.textContent.trim())",
        )
        fails += 0 if say(not buttons, "мёртвых кнопок нет" + (": " + str(buttons) if buttons else "")) else 1
        page.close()

    plain.close()

    page = ctx.new_page()
    page.goto(BASE + "competitor-analysis-junior/")
    page.wait_for_timeout(400)
    head("competitor-analysis-junior · со скриптом")

    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1

    # таблица: пример → шаблон
    fails += 0 if say(page.is_visible('[data-switch-pane="ex"]'), "по умолчанию открыт пример") else 1
    page.click('[data-switch-btn="tpl"]')
    page.wait_for_timeout(100)
    fails += 0 if say(
        page.is_visible('[data-switch-pane="tpl"]') and not page.is_visible('[data-switch-pane="ex"]'),
        "кнопка «Шаблон» переключает таблицу",
    ) else 1
    wide = page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    fails += 0 if say(wide, "широкая таблица не раздвигает страницу") else 1

    # конструктор подписи
    today = page.evaluate("new Date().toISOString().slice(0, 4)")
    out = page.inner_text("#cbOut")
    fails += 0 if say("_" + today in out and "Просмотрено" in out, "дата подставлена сегодняшняя: " + out.split("\n")[0]) else 1
    page.fill('[data-build-field="why"]', "")
    page.wait_for_timeout(100)
    note = page.eval_on_selector_all("[data-build-note]", "els => els.filter(e => !e.hidden).map(e => e.textContent)")
    fails += 0 if say(len(note) == 1 and "зачем сняли" in note[0], "без «зачем» конструктор говорит: " + (note[0][:60] if note else "—")) else 1
    out = page.inner_text("#cbOut")
    fails += 0 if say("Снял ради" not in out, "кусок «Снял ради» ушёл из подписи") else 1
    page.fill('[data-build-field="prod"]', "Яндекс Лавка")
    page.wait_for_timeout(100)
    out = page.inner_text("#cbOut")
    fails += 0 if say(out.startswith("яндекс-лавка_02_"), "имя файла собрано: " + out.split("\n")[0]) else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "competitor-analysis-middle/")
    page.wait_for_timeout(400)
    head("competitor-analysis-middle · со скриптом")

    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1

    # лесенка
    open_now = page.eval_on_selector_all("[data-dig-body]", "els => els.filter(e => !e.hidden).length")
    final = page.is_visible("[data-dig-final]")
    fails += 0 if say(open_now == 1 and not final, "лесенка начинается с первой ступени, вывод скрыт") else 1
    stubs = page.eval_on_selector_all("[data-dig-stub]", "els => els.filter(e => !e.hidden).map(e => e.textContent)")
    fails += 0 if say(len(stubs) == 3 and "Копайте" in stubs[0], "закрытые ступени подписаны: " + (stubs[0] if stubs else "—")) else 1

    for _ in range(3):
        page.click("[data-dig-actions] button")
        page.wait_for_timeout(80)

    fails += 0 if say(page.is_visible("[data-dig-final]"), "после четвёртой ступени открыт вывод") else 1
    fails += 0 if say(not page.is_visible("[data-dig-actions] button"), "кнопка «копать» ушла") else 1
    hint = page.inner_text("[data-dig-hint]")
    fails += 0 if say("Дошли" in hint, "подсказка сменилась: " + hint[:50]) else 1

    # конструктор отказа
    page.fill('[data-build-field="us"]', "")
    page.wait_for_timeout(100)
    note = page.eval_on_selector_all("[data-build-note]", "els => els.filter(e => !e.hidden).map(e => e.textContent)")
    fails += 0 if say(len(note) == 1 and "Нет главного" in note[0], "без факта о нас: " + (note[0][:50] if note else "—")) else 1
    page.fill('[data-build-field="alt"]', "")
    page.wait_for_timeout(100)
    note = page.eval_on_selector_all("[data-build-note]", "els => els.filter(e => !e.hidden).map(e => e.textContent)")
    fails += 0 if say(len(note) == 1 and "мне не нравится" in note[0], "без причины и замены: " + (note[0][:50] if note else "—")) else 1
    page.fill('[data-build-field="trick"]', "<b>x</b>")
    page.wait_for_timeout(100)
    raw = page.inner_html("#rbText")
    fails += 0 if say("&lt;b&gt;x" in raw, "ввод экранируется, разметка не подставляется") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "competitor-analysis-senior/")
    page.wait_for_timeout(400)
    head("competitor-analysis-senior · со скриптом")

    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1

    cards = page.query_selector_all("details.ds-lesson__pcard")
    fails += 0 if say(len(cards) == 4, "карточек принципов: " + str(len(cards))) else 1
    page.click("details.ds-lesson__pcard >> nth=0 >> summary")
    page.click("details.ds-lesson__pcard >> nth=1 >> summary")
    page.wait_for_timeout(100)
    opened = page.eval_on_selector_all("details.ds-lesson__pcard", "els => els.map(e => e.open)")
    fails += 0 if say(opened == [False, True, False, False], "открыта только одна карточка: " + str(opened)) else 1
    lead = page.query_selector_all(".ds-quiz__lead")
    fails += 0 if say(len(lead) >= 3, "в тренажёре принцип стоит перед спором: " + str(len(lead))) else 1

    # копирование забирает и закрытые карточки
    ctx.grant_permissions(["clipboard-read", "clipboard-write"])
    page.click('[data-copy="pcards"] button')
    page.wait_for_timeout(300)
    copied = page.evaluate("navigator.clipboard.readText()")
    fails += 0 if say(
        "пересмотр" in copied.lower() and copied.lower().count("формулировка") == 4,
        "скопированы все четыре карточки, знаков: " + str(len(copied)),
    ) else 1
    opened = page.eval_on_selector_all("details.ds-lesson__pcard", "els => els.map(e => e.open)")
    fails += 0 if say(opened == [False, True, False, False], "после копирования карточки как были") else 1
    page.close()

    browser.close()

print("\nнеудач:", fails)
sys.exit(1 if fails else 0)
