"""Прогон живых кусков уроков в браузере: темы «Юзабилити-тесты», «Анализ конкурентов», «Сценарии и структура» и «Опросы».

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

    # ─── тема «Сценарии и структура» ─────────────────────────────────────────
    plain = browser.new_context(java_script_enabled=False)

    for slug, must in (
        ("flows-structure-junior", ["Приходит из корзины", "Регистрируется по номеру телефона", "Откуда человек сюда попадает?", "Пятнадцать блоков", "С входами и выходами"]),
        ("flows-structure-middle", ["Отменить заказ", "кандидат на два входа", "Активные заказы", "Человек 1", "Система не смогла"]),
        ("flows-structure-senior", ["Подписка на регулярную доставку", "Куда встаёт", "Как выросло за три года"]),
    ):
        page = plain.new_page()
        page.goto(BASE + slug + "/")
        head(slug + " · без скрипта")
        text = page.inner_text("#ds-main")

        for phrase in must:
            fails += 0 if say(phrase.lower() in text.lower(), "видно: " + phrase) else 1

        buttons = page.eval_on_selector_all(
            "#ds-main button",
            "els => els.filter(e => e.offsetParent !== null).map(e => e.textContent.trim())",
        )
        fails += 0 if say(not buttons, "мёртвых кнопок нет" + (": " + str(buttons[:4]) if buttons else "")) else 1
        page.close()

    plain.close()

    page = ctx.new_page()
    page.goto(BASE + "flows-structure-junior/")
    page.wait_for_timeout(500)
    head("flows-structure-junior · со скриптом")

    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1

    # схемы: заливка фигур пришла из токенов, а не осталась чёрной
    fills = page.evaluate("""() => [...document.querySelectorAll('.ds-lesson svg [style*="fill"]')]
        .map(el => getComputedStyle(el).fill).filter(v => v === 'rgb(0, 0, 0)').length""")
    shapes = page.evaluate("""document.querySelectorAll('.ds-lesson svg [style*="fill"]').length""")
    fails += 0 if say(shapes > 0 and fills == 0, "фигур со своей заливкой: %d, чёрных среди них: %d" % (shapes, fills)) else 1

    # вкладки
    panes = page.eval_on_selector_all("[data-switch-pane]", "els => els.filter(e => e.offsetParent !== null).length")
    fails += 0 if say(panes == 1, "из трёх вкладок открыта одна") else 1
    page.click('[data-switch-btn="tp3"]')
    page.wait_for_timeout(100)
    fails += 0 if say(page.is_visible('[data-switch-pane="tp3"]'), "третья вкладка открывается") else 1

    # сборка сценария: сначала ошибка, потом лишний, потом всё по порядку
    cards = page.query_selector_all("[data-seq-pool] button")
    fails += 0 if say(len(cards) == 8, "в стопке восемь карточек: семь шагов и лишняя") else 1
    order = page.get_attribute("[data-seq]", "data-seq-order").split(",")
    page.click("[data-seq-pool] button >> nth=%d" % order.index("3"))
    page.wait_for_timeout(80)
    fails += 0 if say("Пока рано" in page.inner_text("[data-seq-fb]"), "шаг не по порядку: «пока рано»") else 1
    page.click("[data-seq-pool] button >> nth=%d" % order.index("x"))
    page.wait_for_timeout(80)
    fails += 0 if say("лишний" in page.inner_text("[data-seq-fb]"), "лишний вариант распознан") else 1

    for k in range(7):
        page.click("[data-seq-pool] button >> nth=%d" % order.index(str(k)))
        page.wait_for_timeout(60)

    fails += 0 if say("Собрано целиком" in page.inner_text("[data-seq-fb]"), "цепочка собрана целиком") else 1
    fails += 0 if say(page.inner_text("[data-seq-count-out]").startswith("7 "), "счёт: " + page.inner_text("[data-seq-count-out]")) else 1

    # поиск дыр
    pins = page.query_selector_all("[data-hunt] button")
    fails += 0 if say(len(pins) == 5, "точек-кнопок на схеме: " + str(len(pins))) else 1

    for pin in pins:
        pin.click()
        page.wait_for_timeout(50)

    fails += 0 if say("5 из 5" in page.inner_text("[data-hunt-count-out]").lower(), "все пять найдены: " + page.inner_text("[data-hunt-count-out]")) else 1
    fails += 0 if say(page.is_visible("[data-hunt-all]"), "итог поиска показан") else 1
    spot = page.evaluate("""() => { const b = document.querySelector('[data-hunt] button').getBoundingClientRect();
        const h = document.querySelector('[data-hunt]').getBoundingClientRect();
        return b.left >= h.left && b.right <= h.right && b.top >= h.top && b.bottom <= h.bottom; }""")
    fails += 0 if say(spot, "точка стоит внутри схемы") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "flows-structure-middle/")
    page.wait_for_timeout(500)
    head("flows-structure-middle · со скриптом")

    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1

    cards = page.query_selector_all("details.ds-lesson__pcard")
    fails += 0 if say(len(cards) == 12, "карточек-аккордеонов: " + str(len(cards))) else 1

    # сортировка: все карточки в первый раздел
    fails += 0 if say(not page.is_visible("[data-sort-result]"), "итог сортировки скрыт до раскладки") else 1

    for _ in range(10):
        page.click("[data-sort-pool] button >> nth=0")
        page.click("[data-sort-groups] .ds-lesson__sort-name >> nth=0")
        page.wait_for_timeout(40)

    fails += 0 if say("10 из 10" in page.inner_text("[data-sort-count-out]").lower(), "разложено: " + page.inner_text("[data-sort-count-out]")) else 1
    page.click("[data-sort-actions] button >> nth=0")
    page.wait_for_timeout(120)
    mine = page.eval_on_selector_all("td[data-sort-mine]", "els => els.filter(e => e.offsetParent !== null).map(e => e.textContent)")
    differs = page.eval_on_selector_all("[data-sort-differs]", "els => els.filter(e => e.offsetParent !== null).length")
    fails += 0 if say(len(mine) == 10 and mine[0] == "Мои заказы", "колонка «ваш вариант» заполнена: " + str(mine[:2])) else 1
    fails += 0 if say(differs > 0, "отмечено, где вы разошлись с большинством: " + str(differs)) else 1

    # проверка дерева: верный прямой путь
    page.click("[data-tree-list] button >> text=Мои заказы")
    page.wait_for_timeout(60)
    page.click("[data-tree-list] button >> text=Активные заказы")
    page.wait_for_timeout(120)
    verdict = page.eval_on_selector_all("[data-tree-verdict]", "els => els.filter(e => !e.hidden).map(e => e.getAttribute('data-tree-verdict'))")
    fails += 0 if say(verdict == ["direct"], "прямой верный путь: " + str(verdict)) else 1
    fails += 0 if say("кликов: 2" in page.inner_text("[data-tree-count-out]").lower(), page.inner_text("[data-tree-count-out]")) else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "flows-structure-senior/")
    page.wait_for_timeout(500)
    head("flows-structure-senior · со скриптом")

    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1

    cases = page.query_selector_all("[data-wiz-cases] button")
    fails += 0 if say(len(cases) == 6, "случаев стресс-теста: " + str(len(cases))) else 1
    cases[0].click()
    page.wait_for_timeout(80)
    answers = page.get_attribute('[data-wiz-case="sub"]', "data-wiz-answers").split(",")

    for n in range(len(answers)):
        # жмём первый вариант в текущем вопросе: он не обязан быть верным
        page.click(".ds-lesson__wiz-step >> nth=%d >> .ds-quiz__option >> nth=0" % n)
        page.wait_for_timeout(60)

    fails += 0 if say(page.is_visible("[data-wiz-body] [data-wiz-verdict]"), "после трёх вопросов показан вердикт") else 1
    fails += 0 if say("1 из 6" in page.inner_text("[data-wiz-count-out]").lower(), "счёт: " + page.inner_text("[data-wiz-count-out]")) else 1
    notes = page.eval_on_selector_all("[data-wiz-body] .ds-lesson__wiz-fb", "els => els.map(e => e.textContent.slice(0, 24))")
    fails += 0 if say(len(notes) == len(answers), "объяснение под каждым ответом: " + str(notes)) else 1
    # случай «блог» обрывается на первом вопросе
    cases[4].click()
    page.wait_for_timeout(60)
    page.click(".ds-lesson__wiz-step >> nth=0 >> .ds-quiz__option >> nth=1")
    page.wait_for_timeout(80)
    steps = page.query_selector_all(".ds-lesson__wiz-step")
    fails += 0 if say(len(steps) == 1 and page.is_visible("[data-wiz-body] [data-wiz-verdict]"), "короткий случай закрывается одним вопросом") else 1
    page.close()

    # ─── тема «Опросы» ───────────────────────────────────────────────────────
    plain = browser.new_context(java_script_enabled=False)

    for slug, must in (
        ("surveys-data-junior", ["Все пользователи: 500 человек", "Только те, кто ответил: 62 человека", "20 из 62", "Телефон — 21 из 34 (62 %)", "21 из 34 · 62 %"]),
        ("surveys-data-middle", ["Границы пересекаются с предыдущим вариантом", "Шкала согласия 1–5", "Что потом сможете сделать", "78 из 214 · 36 %"]),
        ("surveys-data-senior", ["От 14 % до 70 % по всей базе", "42 человека — это 70 % ответивших", "Не держится", "94 из 112 · 84 %"]),
    ):
        page = plain.new_page()
        page.goto(BASE + slug + "/")
        head(slug + " · без скрипта")
        text = page.inner_text("#ds-main")

        for phrase in must:
            fails += 0 if say(phrase.lower() in text.lower(), "видно: " + phrase) else 1

        buttons = page.eval_on_selector_all(
            "#ds-main button",
            "els => els.filter(e => e.offsetParent !== null).map(e => e.textContent.trim())",
        )
        fails += 0 if say(not buttons, "мёртвых кнопок нет" + (": " + str(buttons[:4]) if buttons else "")) else 1
        bars = page.evaluate("""() => [...document.querySelectorAll('.ds-lesson__bar-fill')]
            .filter(el => el.getBoundingClientRect().width === 0 && parseFloat(el.style.width) > 0).length""")
        fails += 0 if say(bars == 0, "столбики нарисованы без скрипта") else 1
        page.close()

    plain.close()

    page = ctx.new_page()
    page.goto(BASE + "surveys-data-junior/")
    page.wait_for_timeout(500)
    head("surveys-data-junior · со скриптом")

    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1

    # симулятор: пятьсот точек, переключение картин, числа сходятся с разметкой
    dots = page.eval_on_selector_all("[data-bias] i", "els => els.length")
    fails += 0 if say(dots == 500, "точек в сетке: " + str(dots)) else 1
    angry = page.eval_on_selector_all("[data-bias] i.is-angry", "els => els.length")
    fails += 0 if say(angry == 73, "недовольных среди всех: %d (в разметке 73)" % angry) else 1
    page.click("[data-bias-actions] button >> nth=1")
    page.wait_for_timeout(100)
    shown = page.eval_on_selector_all("[data-bias-view]", "els => els.filter(e => !e.hidden).map(e => e.getAttribute('data-bias-view'))")
    angry = page.eval_on_selector_all("[data-bias] i.is-angry", "els => els.length")
    silent = page.eval_on_selector_all("[data-bias] i.is-silent", "els => els.length")
    fails += 0 if say(shown == ["ans"], "открыта картина «кто ответил»") else 1
    fails += 0 if say(angry == 20 and silent == 438, "ответивших недовольных %d, промолчавших %d" % (angry, silent)) else 1

    # калькулятор долей
    page.fill("[data-share-row] >> nth=0 >> [data-share-count]", "42")
    page.wait_for_timeout(100)
    total = page.inner_text("#calcTotal")
    lines = page.inner_text("[data-share-lines]")
    fails += 0 if say(total == "55", "сумма пересчитана: " + total) else 1
    fails += 0 if say("Телефон — 42 из 55 (76 %)" in lines, "готовая строка: " + lines.split("\n")[0]) else 1
    fails += 0 if say("Всего ответили на вопрос: 55 человек" in lines, "итоговая строка на месте") else 1
    page.click("[data-share-actions] button")
    page.wait_for_timeout(100)
    fails += 0 if say(page.inner_text("#calcTotal") == "34", "сброс возвращает пример") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "surveys-data-middle/")
    page.wait_for_timeout(500)
    head("surveys-data-middle · со скриптом")

    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1

    # разметка вариантов: отмечаем два поломанных из трёх и один лишний
    marked = page.eval_on_selector_all("[data-optmark] li.is-bad", "els => els.length")
    fails += 0 if say(marked == 0, "пометки поломок сняты до проверки") else 1
    for n in (1, 2, 0):
        page.click("[data-optmark] li >> nth=%d >> button" % n)
    page.click("[data-opt-actions] button")
    page.wait_for_timeout(120)
    meta = page.inner_text("[data-opt-meta]")
    fails += 0 if say("Нашли поломок: 2 из 3" in meta and "Лишних отмечено: 1" in meta, "итог разметки: " + meta) else 1
    fails += 0 if say(page.is_visible("[data-opt-fix]"), "разбор «чего не хватает» открыт") else 1
    states = page.eval_on_selector_all("[data-optmark] li", "els => els.map(e => e.className)")
    fails += 0 if say(states == ["is-extra", "is-hit", "is-hit", "", "is-missed"], "состояния вариантов: " + str(states)) else 1

    # справочник шкал — семь карточек, открыта одна
    panes = page.eval_on_selector_all(".ds-lesson__scale", "els => els.filter(e => e.offsetParent !== null).length")
    fails += 0 if say(panes == 1, "из семи шкал открыта одна") else 1
    page.click('[data-switch-btn="likert"]')
    page.wait_for_timeout(80)
    fails += 0 if say(page.is_visible('[data-switch-pane="likert"]'), "шкала согласия открывается") else 1

    # чек-лист пилота
    boxes = page.query_selector_all("[data-checklist] input")
    for box in boxes:
        box.check()
    page.wait_for_timeout(100)
    state = page.inner_text("[data-checklist-state]")
    fails += 0 if say("можно рассылать" in state, "чек-лист пилота: " + state) else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "surveys-data-senior/")
    page.wait_for_timeout(500)
    head("surveys-data-senior · со скриптом")

    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1

    big = page.inner_text("#bcBig")
    fails += 0 if say(big == "От 14 % до 70 % по всей базе", "вилка по умолчанию: " + big) else 1
    page.fill("#bcResp", "600")
    page.wait_for_timeout(120)
    big = page.inner_text("#bcBig")
    text = page.inner_text("#bcSay")
    fails += 0 if say(big == "От 46 % до 70 % по всей базе", "вилка при 600 ответах: " + big) else 1
    fails += 0 if say("Вилка умеренная" in text and "{" not in text, "вердикт сменился: " + text[-90:]) else 1
    label = page.inner_text("#bcYesLab")
    fails += 0 if say(label == "420 человек — это 70 % ответивших", "склонение: " + label) else 1

    # разбор отчёта
    notes = page.eval_on_selector_all(".ds-lesson__claim-note", "els => els.filter(e => e.offsetParent !== null).length")
    fails += 0 if say(notes == 0, "разбор скрыт, пока читатель не составил мнение") else 1
    page.click("[data-reveal-button] button")
    page.wait_for_timeout(100)
    notes = page.eval_on_selector_all(".ds-lesson__claim-note", "els => els.filter(e => e.offsetParent !== null).length")
    label = page.inner_text("[data-reveal-button] button")
    fails += 0 if say(notes == 5 and label == "Скрыть разбор", "разбор открыт: пояснений %d, кнопка «%s»" % (notes, label)) else 1
    page.close()

    browser.close()

print("\nнеудач:", fails)
sys.exit(1 if fails else 0)
