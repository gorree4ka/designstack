"""Прогон живых кусков уроков в браузере: темы «Юзабилити-тесты», «Анализ конкурентов», «Сценарии и структура», «Опросы», «Вайрфреймы и прототипы» и «Композиция и сетка», «Типографика», «Цвет и контраст» и «Анимация и микровзаимодействия», «Таблицы и списки».

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
        ("layout-grid-junior", ["Как исправить. 14 нет в наборе", "Здесь всё верно", "Слева восемь разных отступов"]),
        ("layout-grid-middle", ["Ячейка A-14", "Что должно было запомниться", "Эфиопия Иргачеффе"]),
        ("layout-grid-senior", ["Сообщение · 8, отступ по 2 колонки", "По пункту такому-то", "--space-6: 24px"]),
        ("typography-junior", ["Межстрочный 1,0 — 16/16", "Межстрочный 2,0 — 16/32", "Слева семь кеглей"]),
        # Ошибки набора в корректуре и тренажёре — намеренные: WordPress исправил бы их сам (wptexturize),
        # поэтому в разметке они записаны кодами `&quot;` и `&#45;`. Здесь проверяем, что до читателя дошли ошибки.
        ("typography-middle", ["Как исправить. «3000", "Здесь всё верно. В составных словах", "Так абзац выглядит на ноутбуке",
                               'нажмите "Оформить заказ"', "Самовывоз - бесплатно", 'Нажмите "Купить в один клик"', "30 сентября - успейте"]),
        ("typography-senior", ["Пропорциональные цифры", "Почти разряд под разрядом", "--text-body-strong: 600"]),
        ("color-contrast-junior", ["Убрать. Дубль #DCE1E6", "Остаётся, но меняет роль", "Справа шесть нейтральных"]),
        ("color-contrast-middle", ["Тёмная, те же акценты", "Акценты тонут", "Справа у неактивного своя пара цветов"]),
        ("color-contrast-senior", ["Текст справа вписан значениями", "--color-on-action: var(--blue-950);", "Система не покрывает"]),
        ("motion-junior", ["Убрать. Каждое открытие начинается с ожидания", "Добавлено в корзину", "Все пять найдены"]),
        ("motion-middle", ["Слева сумма и строка «Колумбия»", "Проявляются на месте, без сдвига и масштаба", "prefers-reduced-motion: reduce"]),
        ("motion-senior", ["Нарушение. Выбор — это отклик на нажатие", '"$type": "cubicBezier"', "Изменения нет в таблице"]),
        # Состояния в переключателе — содержимое урока: без скрипта видны все панели подряд.
        ("patterns-states-junior", ["Не удалось загрузить заказы", "Заказ № 1043 оформлен", "Убрать. Ответ быстрее секунды"]),
        ("patterns-states-middle", ["Ещё 11 товаров", "имя не указано", "Вопрос: «Какой текст и где?»"]),
        ("patterns-states-senior", ["Обманный паттерн. Это стыжение", "Удалить аккаунт «Кофейня на Лесной»?", "ГДЕ ИСПОЛЬЗУЕТСЯ"]),
        # Версии иконки в переключателе и слои холста — содержимое урока: без скрипта видно всё.
        ("icons-illustration-junior", ["Толщина исправлена", "Заливка. Набор линейный", "Круг 20"]),
        ("icons-illustration-middle", ["Белый фон в файле", "heart-filled.svg", "Отдельная отрисовка под размер"]),
        ("icons-illustration-senior", ["Вкус. Что именно грустно", "Официальный знак из материалов самого бренда", "9. КАК ПРИСЛАТЬ ИКОНКУ"]),
        # Носители в переключателе и разборы — содержимое урока: без скрипта видно всё.
        ("brand-language-junior", ["Не та версия. Рыжий знак на тёмном фоне", "негативная — светлым на тёмном", "Довод о характере"]),
        ("brand-language-middle", ["Охранное поле. Заголовок стоит вплотную", "Только знак и цвет", "lockup-negative.svg"]),
        ("brand-language-senior", ["Мода. Причина есть в продукте", "«Оценка куратора важнее названия»", "СУТЬ (3–4 слова о продукте)"]),
        # Три причины пустоты, способы для длинного и узкого, шаги выбора строк — содержимое урока.
        ("tables-lists-junior", ["Возвратов пока не было", "Все заказы на сегодня собраны", "Убрать. Оператор по ней ничего не решает"]),
        ("tables-lists-middle", ["RU4829…544RU", "Выбрать все 42 собранных", "42 заказа переданы курьеру", "Переделать. Числа не обрезают"]),
        ("tables-lists-senior", ["Карандаш и корзина", "Не по правилу 3. Изменение — в карточке", "ЧТО ПРИВЕСТИ К ПРАВИЛУ"]),
        # Пометки, места ошибки, ошибки отправки и черновик — панели переключателя, видны все подряд.
        ("forms-junior", ["Звёздочки у обязательных", "Проверьте два поля", "Убрать. Один промах — и всё введённое пропало"]),
        ("forms-middle", ["Сервер не ответил", "Вы остановились на шаге «Реквизиты»", "Переделать. Проверка на вводе ругает", "Сложнее в разработке"]),
        ("forms-senior", ["Правило 4. «Некорректно» в словаре", "ФАЙЛ НЕ ПОДОШЁЛ", "Посчитана по выбранным товарам"]),
        # Периоды, круг и столбцы, две шкалы, базы, вопросы, способы сказать — панели переключателя, видны все.
        ("dashboards-junior", ["вчера к этому часу — 35 100", "Столбцы по убыванию", "Шкала от 880", "Переделать. Неполный день сравнили с полным"]),
        ("dashboards-middle", ["Отстаём на 50 400", "Что изменилось за неделю — разница от нуля", "Мало: заказать у обжарщика, нужно от 10 дней", "Переделать. Было 2, стало 4"]),
        ("dashboards-senior", ["Договорённость", "СЛЕДУЮЩИЙ ПЕРЕСМОТР", "Убрать. Число только растёт"]),
        # Подписи кнопок, заголовки, тон, загадка и шкалы тона — панели переключателя, видны все;
        # у тренажёра «вычеркните лишнее» без скрипта виден ответ: лишнее зачёркнуто, под фразой — что осталось.
        ("ui-copy-junior", ["Оставить подписку", "Ответы на вопросы", "Изменения вступят в силу со следующей доставки.", "Переписать. Подходит к любому экрану продукта"]),
        ("ui-copy-middle", ["Беспл. дост. в пр. МКАД от 2К", "LESNAYA OBZHARKA PODPISKA", "Заменить. Покупатель оформлял подписку"]),
        ("ui-copy-senior", ["Шкалы и примеры", "ПРАВИЛО: 4.2", "Поправить. Шкала «почтительный — дерзкий»"]),
        # Три текста ошибки, пустоты и тупик — панели переключателя, видны все; у тренажёра «соберите
        # сообщение» без скрипта на экране образцовый текст, а разборы всех вариантов видны.
        ("errors-empty-states-junior", ["Сервер магазина не ответил, до оплаты дело не дошло", "Банк не подтвердил оплату",
                                        "«Транзакция» и код — язык банка", "Переписать. Код для разработчика"]),
        ("errors-empty-states-middle", ["Отменённых заказов в 2026 году нет", "Сервер магазина не отвечает. История на месте",
                                        "Извините, оформление новых заказов недоступно.", "Переписать. Тупик: человек шёл к сорту"]),
        ("errors-empty-states-senior", ["Корзина и адрес доставки сохранены.", "Не по схеме. «Сессия» — слово разработки",
                                        "Вернуть. Без форм множественного числа"]),
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

    # Слои экрана без скрипта: что включено классом на коробке, то и видно. Числа
    # отступов — содержимое урока, их должно быть видно все до одного.
    page = plain.new_page()
    page.goto(BASE + "layout-grid-junior/")
    head("layout-grid-junior · слои без скрипта")
    marks = page.evaluate("""() => {
        const all = [...document.querySelectorAll('.is-marks .ds-lesson__gap-n')];
        return [all.length, all.filter(el => el.offsetParent !== null).length]; }""")
    fails += 0 if say(marks[0] > 0 and marks[0] == marks[1], "числа отступов видны: %d из %d" % (marks[1], marks[0])) else 1
    cols = page.evaluate("[...document.querySelectorAll('.is-cols .ds-lesson__spec-cols')].map(el => getComputedStyle(el).display)")
    fails += 0 if say(cols and all(d == "grid" for d in cols), "сетка в разделе 5 видна: " + str(cols)) else 1
    edges = page.evaluate("[...document.querySelectorAll('.is-edges .ds-lesson__spec-el')].filter(el => getComputedStyle(el, '::before').content !== 'none').length")
    fails += 0 if say(edges > 0, "линии краёв в разделе 4 видны: " + str(edges)) else 1
    page.close()

    # «Типографика, Junior»: таблички кеглей — содержимое урока, без скрипта видны все.
    page = plain.new_page()
    page.goto(BASE + "typography-junior/")
    head("typography-junior · кегли без скрипта")
    badges = page.evaluate("""() => { const all = [...document.querySelectorAll('#seven .ds-lesson__fs-n')];
        return [all.length, all.filter(el => el.offsetParent !== null).length]; }""")
    fails += 0 if say(badges[0] == 14 and badges[0] == badges[1], "таблички кеглей видны: %d из %d" % (badges[1], badges[0])) else 1
    page.close()

    # «Иконки, Junior»: все три слоя холста и все три версии кофемолки видны без скрипта.
    page = plain.new_page()
    page.goto(BASE + "icons-illustration-junior/")
    head("icons-illustration-junior · слои и версии без скрипта")
    layers = page.evaluate("""() => ['grid', 'pad', 'keys'].map(n => getComputedStyle(document.querySelector('.ds-lesson__ic-' + n)).display)""")
    fails += 0 if say(all(d != "none" for d in layers), "сетка, поле и опорные фигуры видны: " + str(layers)) else 1
    new = page.evaluate("[...document.querySelectorAll('#foreign .ds-lesson__ic-new')].filter(el => el.offsetParent !== null).length")
    fails += 0 if say(new == 6, "кофемолка во всех трёх версиях, в двух размерах: %d из 6" % new) else 1
    page.close()

    plain.close()

    # --- со скриптом ---
    ctx = browser.new_context()

    page = ctx.new_page()
    page.goto(BASE + "layout-grid-junior/")
    page.wait_for_timeout(400)
    head("layout-grid-junior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1

    # Слои: кнопки по числу объявленных слоёв, нажатое состояние совпадает с классом коробки.
    state = """() => [...document.querySelectorAll('[data-layer-actions]')].map(place => {
        const box = place.closest('.ds-lesson__box');
        return [...place.querySelectorAll('[data-layer]')].map(h =>
            h.getAttribute('data-layer') + ':' + (h.querySelector('button')?.getAttribute('aria-pressed')) + '/' +
            box.classList.contains('is-' + h.getAttribute('data-layer'))); }).flat()"""
    before = page.evaluate(state)
    fails += 0 if say(
        len(before) == 7 and all(s.split(":")[1].split("/")[0] == s.split("/")[1] for s in before),
        "кнопки слоёв созданы, нажатие совпадает с классом: " + str(before),
    ) else 1
    page.click("#edge [data-layer='edges'] button")
    fails += 0 if say(
        page.evaluate("getComputedStyle(document.querySelector('#edge .ds-lesson__spec-el'), '::before').content") == "none",
        "«Края» выключает линии",
    ) else 1
    page.click("#grid [data-layer='cols'] button")
    fails += 0 if say(
        page.evaluate("getComputedStyle(document.querySelector('#grid .ds-lesson__spec-cols')).display") == "none",
        "«Сетка» прячет колонки",
    ) else 1
    page.click("#near [data-layer='blur'] button")
    blur = page.evaluate("""() => { const b = document.querySelector('#near .ds-lesson__spec-body');
        const n = document.querySelector('#near .ds-lesson__gap-n');
        return [getComputedStyle(b).filter, getComputedStyle(n).display]; }""")
    fails += 0 if say(blur[0].startswith("blur") and blur[1] == "none", "«Прищур» размывает и снимает числа: " + str(blur)) else 1

    # Поиск разнобоя: ловушка не идёт в счёт, четыре находки — «4 из 4» и итог.
    pins = page.query_selector_all("[data-hunt] button")
    fails += 0 if say(len(pins) == 8, "чисел-кнопок на экране: " + str(len(pins))) else 1
    miss = page.evaluate("[...document.querySelectorAll('[data-hunt-item]')].map(el => el.hasAttribute('data-hunt-miss'))")
    pins[miss.index(True)].click()
    page.wait_for_timeout(50)
    fails += 0 if say(
        "0 из 4" in page.inner_text("[data-hunt-count-out]").lower() and "всё верно" in page.inner_text("[data-hunt-fb]"),
        "ловушка разобрана, но не засчитана: " + page.inner_text("[data-hunt-count-out]"),
    ) else 1
    fails += 0 if say("is-miss" in (pins[miss.index(True)].get_attribute("class") or ""), "ловушка отмечена пунктиром") else 1

    for pin, is_miss in zip(pins, miss):
        if not is_miss:
            pin.click()
            page.wait_for_timeout(50)

    fails += 0 if say("4 из 4" in page.inner_text("[data-hunt-count-out]").lower(), "все четыре найдены: " + page.inner_text("[data-hunt-count-out]")) else 1
    fails += 0 if say(page.is_visible("[data-hunt-all]"), "итог поиска показан") else 1
    inside = page.evaluate("""() => [...document.querySelectorAll('[data-hunt] button')].every(b => {
        const r = b.getBoundingClientRect(), s = b.closest('.ds-lesson__spec').getBoundingClientRect();
        return r.left >= s.left && r.right <= s.right; })""")
    fails += 0 if say(inside, "числа стоят внутри экрана") else 1
    page.close()

    # Senior: схемы раскладок со слоем «Сетка».
    page = ctx.new_page()
    page.goto(BASE + "layout-grid-senior/")
    page.wait_for_timeout(400)
    head("layout-grid-senior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    cols = "() => [...document.querySelectorAll('#layouts .ds-lesson__lay-cols')].map(el => getComputedStyle(el).display)"
    fails += 0 if say(set(page.evaluate(cols)) == {"grid"}, "сетка на пяти схемах включена") else 1
    page.click("#layouts [data-layer='cols'] button")
    fails += 0 if say(set(page.evaluate(cols)) == {"none"}, "«Сетка» прячет колонки на всех схемах") else 1
    spans = page.evaluate("() => [...document.querySelectorAll('#layouts .ds-lesson__lay')].map(l => [...l.querySelectorAll('.ds-lesson__lay-b')].reduce((s, b) => s + Math.round(b.getBoundingClientRect().width), 0) > 0)")
    fails += 0 if say(all(spans) and len(spans) == 5, "пять схем нарисованы") else 1
    page.close()

    # Middle: лаборатория иерархии и «три секунды».
    page = ctx.new_page()
    page.goto(BASE + "layout-grid-middle/")
    page.wait_for_timeout(400)
    head("layout-grid-middle · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    size = "() => getComputedStyle(document.querySelector('#hierarchy .ds-lesson__hl-main')).fontSize"
    flat = page.evaluate(size)
    page.click("#hierarchy [data-layer='size'] button")
    fails += 0 if say(page.evaluate(size) != flat, "«Размер» увеличивает главное: %s → %s" % (flat, page.evaluate(size))) else 1
    page.click("#hierarchy [data-layer='weight'] button")
    weight = page.evaluate("getComputedStyle(document.querySelector('#hierarchy .ds-lesson__hl-main')).fontWeight")
    fails += 0 if say(int(weight) >= 700, "«Вес» делает главное жирным: " + weight) else 1
    page.click("#hierarchy [data-layer='gray'] button")
    fails += 0 if say("grayscale" in page.evaluate("getComputedStyle(document.querySelector('#hierarchy .ds-lesson__spec')).filter"), "«Без цвета» переводит в серое") else 1
    shown = "() => [document.querySelector('[data-flash-screen]').offsetParent !== null, document.querySelector('[data-flash-after]').offsetParent !== null, document.querySelector('[data-flash-idle]').offsetParent !== null]"
    fails += 0 if say(page.evaluate(shown) == [False, False, True], "«Три секунды» до нажатия: экран спрятан, заглушка видна") else 1
    page.click("[data-flash-actions] button")
    page.wait_for_timeout(300)
    fails += 0 if say(page.evaluate(shown) == [True, False, False], "после нажатия экран виден") else 1
    page.wait_for_timeout(3200)
    fails += 0 if say(page.evaluate(shown) == [False, True, True], "через три секунды экран спрятан, разбор виден") else 1
    page.close()

    # «Цвет и контраст, Junior»: поиск дублей среди образцов и режим «Без цвета».
    page = ctx.new_page()
    page.goto(BASE + "color-contrast-junior/")
    page.wait_for_timeout(400)
    head("color-contrast-junior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    pins = page.query_selector_all("[data-hunt] button")
    kept = page.evaluate("() => [...document.querySelectorAll('[data-hunt] button')].every(b => b.querySelector('b'))")
    fails += 0 if say(len(pins) == 16 and kept, "образцов-кнопок %d, код и подпись раздельно: %s" % (len(pins), kept)) else 1
    miss = page.evaluate("[...document.querySelectorAll('[data-hunt-item]')].map(el => el.hasAttribute('data-hunt-miss'))")
    pins[miss.index(True)].click()
    page.wait_for_timeout(50)
    fails += 0 if say("0 из 7" in page.inner_text("[data-hunt-count-out]").lower(), "нужный цвет разобран, но не засчитан") else 1

    for pin, is_miss in zip(pins, miss):
        if not is_miss:
            pin.click()
            page.wait_for_timeout(50)

    fails += 0 if say("7 из 7" in page.inner_text("[data-hunt-count-out]").lower() and page.is_visible("[data-hunt-all]"), "все семь дублей найдены, итог показан") else 1
    gray = "() => [...document.querySelectorAll('#status .ds-lesson__spec')].map(el => getComputedStyle(el).filter)"
    before = page.evaluate(gray)
    page.click("#status [data-layer='gray'] button")
    after = page.evaluate(gray)
    fails += 0 if say(set(before) == {"none"} and all(f.startswith("grayscale") for f in after), "«Без цвета» переводит оба экрана в серое") else 1
    page.close()

    # «Цвет и контраст, Middle»: слой замеров и тёмные темы на тех же ролях.
    page = ctx.new_page()
    page.goto(BASE + "color-contrast-middle/")
    page.wait_for_timeout(400)
    head("color-contrast-middle · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    seen = "() => [...document.querySelectorAll('#lab .ds-lesson__cr')].filter(el => el.offsetParent !== null).length"
    fails += 0 if say(page.evaluate(seen) == 12, "замеров на экранах видно: %d" % page.evaluate(seen)) else 1
    page.click("#lab [data-layer='ratios'] button")
    fails += 0 if say(page.evaluate(seen) == 0, "«Контраст» прячет замеры") else 1
    inside = page.evaluate("""() => [...document.querySelectorAll('#dark .ds-lesson__cr, #disabled .ds-lesson__cr')].every(cr => {
        const r = cr.getBoundingClientRect(), s = cr.closest('.ds-lesson__spec').getBoundingClientRect();
        return r.width === 0 || (r.left >= s.left && r.right <= s.right); })""")
    fails += 0 if say(inside, "таблички замеров не вылезают за экран") else 1
    page.click("#dark [data-switch-btn='own']")
    bg = page.evaluate("() => getComputedStyle([...document.querySelectorAll('#dark [data-switch-pane]')].find(p => !p.hidden).querySelector('.ds-lesson__cs')).backgroundColor")
    fails += 0 if say(bg == "rgb(21, 24, 28)", "тёмная тема экрана включена ролями: " + bg) else 1
    page.close()

    # «Цвет и контраст, Senior»: тёмная тема перекрашивает роли и не трогает прибитые цвета.
    page = ctx.new_page()
    page.goto(BASE + "color-contrast-senior/")
    page.wait_for_timeout(400)
    head("color-contrast-senior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    ink = """() => [...document.querySelectorAll('#direct .ds-lesson__wf-col')].map(c =>
        getComputedStyle(c.querySelector('.ds-lesson__cs-row b')).color)"""
    light = page.evaluate(ink)
    page.click("#direct [data-layer='dark'] button")
    dark = page.evaluate(ink)
    fails += 0 if say(light == ["rgb(27, 31, 36)", "rgb(27, 31, 36)"] and dark == ["rgb(232, 235, 238)", "rgb(27, 31, 36)"],
                      "роль перекрасилась, примитив остался: %s → %s" % (light, dark)) else 1
    page.close()

    # «Типографика, Junior»: слой «Кегли», шкала справа, переключатель интервалов.
    page = ctx.new_page()
    page.goto(BASE + "typography-junior/")
    page.wait_for_timeout(400)
    head("typography-junior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    seen = "() => [...document.querySelectorAll('#seven .ds-lesson__fs-n')].filter(el => el.offsetParent !== null).length"
    pressed = page.get_attribute("#seven [data-layer='sizes'] button", "aria-pressed")
    fails += 0 if say(pressed == "true" and page.evaluate(seen) == 14, "«Кегли» нажата, табличек 14") else 1
    page.click("#seven [data-layer='sizes'] button")
    fails += 0 if say(page.evaluate(seen) == 0, "«Кегли» прячет таблички") else 1
    sizes = page.evaluate("""() => { const cols = document.querySelectorAll('#seven .ds-lesson__wf-col');
        return [...cols].map(c => [...new Set([...c.querySelectorAll('.ds-lesson__ts')].map(el => parseFloat(getComputedStyle(el).fontSize)))].sort((a, b) => a - b)); }""")
    fails += 0 if say(sizes == [[13, 14, 15, 17, 18, 22, 24], [12, 14, 16, 20, 24]], "кегли на глаз и по шкале: " + str(sizes)) else 1
    weights = page.evaluate("""() => { const c = document.querySelectorAll('#headings .ds-lesson__wf-col')[0];
        return [getComputedStyle(c.querySelector('.ds-lesson__ts b')).fontWeight, getComputedStyle(c.querySelector('.ds-lesson__ts--semi')).fontWeight]; }""")
    fails += 0 if say(weights == ["700", "600"], "жирный и полужирный различаются: " + str(weights)) else 1
    page.click("#leading [data-switch-btn='lh4']")
    lh = page.evaluate("() => [...document.querySelectorAll('#leading [data-switch-pane]')].filter(p => !p.hidden).map(p => getComputedStyle(p.querySelector('.ds-lesson__measure')).lineHeight)")
    fails += 0 if say(lh == ["32px"], "интервал 2,0 даёт 32 px: " + str(lh)) else 1
    page.close()

    # «Типографика, Middle»: корректура строками текста, длина строки, выравнивание заголовка.
    page = ctx.new_page()
    page.goto(BASE + "typography-middle/")
    page.wait_for_timeout(400)
    head("typography-middle · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    pins = page.query_selector_all("[data-hunt] button")
    fails += 0 if say(len(pins) == 9, "мест-кнопок в тексте: " + str(len(pins))) else 1
    miss = page.evaluate("[...document.querySelectorAll('[data-hunt-item]')].map(el => el.hasAttribute('data-hunt-miss'))")
    pins[miss.index(True)].click()
    page.wait_for_timeout(50)
    fails += 0 if say(
        "0 из 6" in page.inner_text("[data-hunt-count-out]").lower() and "всё верно" in page.inner_text("[data-hunt-fb]"),
        "ловушка разобрана, но не засчитана: " + page.inner_text("[data-hunt-count-out]"),
    ) else 1

    for pin, is_miss in zip(pins, miss):
        if not is_miss:
            pin.click()
            page.wait_for_timeout(50)

    fails += 0 if say("6 из 6" in page.inner_text("[data-hunt-count-out]").lower(), "все шесть найдены: " + page.inner_text("[data-hunt-count-out]")) else 1
    fails += 0 if say(page.is_visible("[data-hunt-all]"), "итог корректуры показан") else 1
    inline = page.evaluate("""() => { const m = document.querySelector('[data-hunt] .ds-lesson__measure').getBoundingClientRect();
        return [...document.querySelectorAll('[data-hunt] button')].every(b => { const r = b.getBoundingClientRect();
            return r.height < 40 && r.left >= m.left && r.right <= m.right; }); }""")
    fails += 0 if say(inline, "места стоят в строке и внутри абзаца") else 1
    widths = []

    for key in ("w30", "w60"):
        page.click("#measure [data-switch-btn='%s']" % key)
        widths.append(page.evaluate("() => [...document.querySelectorAll('#measure [data-switch-pane]')].filter(p => !p.hidden).map(p => Math.round(p.querySelector('.ds-lesson__measure').getBoundingClientRect().width))[0]"))

    # Абзац в 100 знаков шире колонки урока: образец выходит за её края, но не за край окна.
    widths.append(page.evaluate("() => Math.round(document.querySelector('.ds-lesson__measure--bleed').getBoundingClientRect().width)"))
    column = page.evaluate("() => Math.round(document.querySelector('.ds-lesson').getBoundingClientRect().width)")
    over = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    fails += 0 if say(widths[0] < widths[1] < column < widths[2] and over <= 0, "длина строки растёт: %s, колонка %d, вылет за окно %d" % (widths, column, over)) else 1
    wrap = page.evaluate("getComputedStyle(document.querySelector('.ds-lesson__balance')).textWrapStyle")
    fails += 0 if say(wrap == "balance", "заголовок выровнен: " + str(wrap)) else 1
    page.close()

    # «Типографика, Senior»: цифры в таблице и экран коллеги с номерами замечаний.
    page = ctx.new_page()
    page.goto(BASE + "typography-senior/")
    page.wait_for_timeout(400)
    head("typography-senior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    digits = """() => { const pane = [...document.querySelectorAll('#numbers [data-switch-pane]')].find(p => !p.hidden);
        const cells = [...pane.querySelectorAll('tbody tr')].map(r => r.cells[2]).filter(c => c.textContent.trim().length === 5);
        return [getComputedStyle(pane.querySelector('table')).fontVariantNumeric, cells.map(c => { const g = document.createRange();
            g.selectNodeContents(c); return Math.round(g.getBoundingClientRect().width * 10) / 10; })]; }"""
    page.click("#numbers [data-switch-btn='prop']")
    prop = page.evaluate(digits)
    page.click("#numbers [data-switch-btn='tab']")
    tab = page.evaluate(digits)
    fails += 0 if say(prop[0] == "proportional-nums" and len(set(prop[1])) > 1, "пропорциональные: ширины разные " + str(prop)) else 1
    # У Golos Text 2.004 `tnum` доводит до ширины нуля только 1, 4 и 7, остальные цифры своей ширины,
    # поэтому равенства нет: проверяем, что разброс стал в разы меньше и не больше полутора пикселей.
    spread = lambda w: max(w) - min(w)
    fails += 0 if say(tab[0] == "tabular-nums" and spread(tab[1]) <= 1.5 and spread(tab[1]) * 4 < spread(prop[1]), "моноширинные: разброс ширин %.1f против %.1f" % (spread(tab[1]), spread(prop[1]))) else 1
    marks = page.evaluate("""() => { const s = document.querySelector('#review .ds-lesson__spec').getBoundingClientRect();
        const all = [...document.querySelectorAll('#review .ds-lesson__spec-mark')];
        return [all.map(m => m.textContent).sort().join(''), all.every(m => { const r = m.getBoundingClientRect();
            return r.left >= s.left - 1 && r.right <= s.right + 1; })]; }""")
    fails += 0 if say(marks == ["123458", True], "номера замечаний 1–5 и 8 на экране: " + str(marks)) else 1
    page.close()

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


    # ─── тема «Вайрфреймы и прототипы» ───────────────────────────────────────
    plain = browser.new_context(java_script_enabled=False)
    page = plain.new_page()
    page.goto(BASE + "wireframes-prototype-junior/")
    head("wireframes-prototype-junior · без скрипта")
    screens = page.eval_on_selector_all(
        "[data-proto-stage] [data-screen]", "all => all.filter(el => el.offsetParent !== null).length"
    )
    fails += 0 if say(screens == 6, "все экраны сценария видны: " + str(screens)) else 1
    text = page.inner_text("#ds-main")
    fails += 0 if say("Дополнительная ветка" in text, "пояснение к экрану видно") else 1
    fails += 0 if say(not page.is_visible("[data-proto-count-out]"), "счётчик экранов спрятан: без скрипта он врёт") else 1
    page.close()
    plain.close()

    page = ctx.new_page()
    page.goto(BASE + "wireframes-prototype-junior/")
    head("wireframes-prototype-junior")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    shown = page.eval_on_selector_all(
        "[data-proto-stage] [data-screen]",
        "all => all.filter(el => el.offsetParent !== null).map(el => el.dataset.screen)",
    )
    fails += 0 if say(shown == ["cart"], "со скриптом на виду один экран: " + str(shown)) else 1
    fails += 0 if say(
        page.text_content("[data-proto-count-out]") == "Экранов: 1 из 4 · тупиков найдено: 0 из 2",
        "счётчик: " + page.text_content("[data-proto-count-out]"),
    ) else 1

    page.click('[data-proto] button[data-dead="Удалить товар"]')
    fb = page.inner_text("[data-proto-fb]")
    fails += 0 if say("Ничего не произошло" in fb and "нет перехода" in fb, "тупик объяснён: " + fb[:60]) else 1
    fails += 0 if say(
        page.text_content("[data-proto-count-out]").endswith("тупиков найдено: 1 из 2"),
        "тупик засчитан: " + page.text_content("[data-proto-count-out]"),
    ) else 1

    page.click('[data-proto] button[data-go="delivery"]')
    page.click('[data-screen="delivery"] button[data-go="payment"]')
    page.click('[data-screen="payment"] button[data-dead="Другая карта"]')
    page.click('[data-screen="payment"] button[data-go="done"]')
    done = page.inner_text("[data-proto-fb]")
    fails += 0 if say("Сценарий пройден" in done and "Тупиков найдено: 2 из 2" in done, "итог: " + done[:70]) else 1
    fails += 0 if say("Вы нашли оба тупика" in done, "оба тупика найдены") else 1
    fails += 0 if say("{" not in done, "подстановки в итоге закрыты") else 1
    log = page.inner_text("[data-proto-log]")
    fails += 0 if say(log.count("→") == 6 and "тупик: Другая карта" in log, "журнал перехода: " + log.split("\n")[-1]) else 1

    page.click('[data-screen="done"] button[data-out="Мои заказы"]')
    stub = page.inner_text('[data-screen="stub"]')
    fails += 0 if say("«Мои заказы»" in stub, "заглушка названа: " + stub.split("\n")[1][:60]) else 1
    page.click("[data-proto-stub-actions] button")
    fails += 0 if say(
        page.eval_on_selector_all(
            "[data-proto-stage] [data-screen]",
            "all => all.filter(el => el.offsetParent !== null).map(el => el.dataset.screen)",
        ) == ["done"],
        "возврат с заглушки на тот же экран",
    ) else 1

    page.click("[data-proto-actions] button")
    fails += 0 if say(
        page.text_content("[data-proto-count-out]") == "Экранов: 1 из 4 · тупиков найдено: 0 из 2"
        and not page.is_visible("[data-proto-log]"),
        "«начать заново» чистит журнал и счётчик",
    ) else 1

    label = page.inner_text("[data-squint-actions] button")
    page.click("[data-squint-actions] button")
    blur = page.eval_on_selector("[data-squint-row] .ds-lesson__wf", "el => getComputedStyle(el).filter")
    fails += 0 if say(blur.startswith("blur("), "прищур размывает экраны: " + blur) else 1
    fails += 0 if say(
        page.inner_text("[data-squint-actions] button") != label, "подпись кнопки сменилась: " + page.inner_text("[data-squint-actions] button")
    ) else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "wireframes-prototype-middle/")
    head("wireframes-prototype-middle")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    page.click("[data-switch] button >> nth=1")
    skels = page.eval_on_selector_all(".ds-lesson__wf-skel", "all => all.filter(el => el.offsetParent !== null).length")
    fails += 0 if say(skels == 3, "в состоянии загрузки серых мест: " + str(skels)) else 1
    fails += 0 if say(
        page.eval_on_selector_all(
            ".ds-lesson__wf-btn[disabled]", "all => all.filter(el => el.offsetParent !== null).length"
        ) == 1,
        "кнопка перехода выглядит недоступной",
    ) else 1
    cut = page.eval_on_selector_all(
        ".ds-lesson__wf-window",
        "all => all.map(el => el.scrollHeight - el.clientHeight > 4)",
    )
    fails += 0 if say(cut == [False, True], "за границу экрана уходит только длинный заказ: " + str(cut)) else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "wireframes-prototype-senior/")
    head("wireframes-prototype-senior")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    lit = "() => [...document.querySelectorAll('[data-diff-row] [data-diff]')].filter(el => getComputedStyle(el).outlineStyle !== 'none').length"
    fails += 0 if say(page.evaluate(lit) == 0, "до нажатия ничего не подсвечено") else 1
    page.click("[data-diff-actions] button")
    fails += 0 if say(page.evaluate(lit) == 6, "подсвечено различий: " + str(page.evaluate(lit))) else 1
    fails += 0 if say(
        page.inner_text("[data-diff-actions] button") == "Убрать подсветку",
        "подпись кнопки: " + page.inner_text("[data-diff-actions] button"),
    ) else 1
    page.close()

    # «Анимация и микровзаимодействия»: без скрипта виден конечный кадр — уходящее спрятано,
    # пришедшее на месте. Иначе страница без JS показала бы старое число и плашку за краем.
    plain = browser.new_context(java_script_enabled=False)
    page = plain.new_page()
    page.goto(BASE + "motion-junior/")
    head("motion-junior · конечный кадр без скрипта")
    frame = page.evaluate("""() => { const box = document.querySelector('#explain .ds-lesson__box');
        const out = [...box.querySelectorAll('.ds-lesson__mo-el--out')].map(el => getComputedStyle(el).opacity);
        const inn = [...box.querySelectorAll('.ds-lesson__mo-el:not(.ds-lesson__mo-el--out)')].map(el => getComputedStyle(el).transform + ' ' + getComputedStyle(el).opacity);
        return [out, inn]; }""")
    fails += 0 if say(set(frame[0]) == {"0"} and set(frame[1]) == {"none 1"}, "старое число спрятано, новое и плашка на месте: " + str(frame)) else 1
    plain.close()

    # Со скриптом: кнопка на каждый образец, выбор длительности, кривые, поиск.
    page = ctx.new_page()
    page.goto(BASE + "motion-junior/")
    page.wait_for_timeout(400)
    head("motion-junior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    made = page.evaluate("() => [document.querySelectorAll('[data-motion]').length, document.querySelectorAll('[data-motion-actions] button').length]")
    fails += 0 if say(made[0] == made[1] == 6, "кнопок «Проиграть» по образцу: %d на %d" % (made[1], made[0])) else 1
    start = page.evaluate("() => getComputedStyle(document.querySelector('#explain [data-motion]:last-child .ds-lesson__mo-toast')).opacity")
    fails += 0 if say(start == "0", "до нажатия образец стоит в начальном кадре: плашка прозрачна") else 1
    # Начальный кадр встаёт мгновенно: образец не двигается сам при загрузке страницы.
    # 28.09.2026 дорожки кривых секунду ехали назад сразу после открытия урока.
    still = page.evaluate("""() => [...document.querySelectorAll('#easing .ds-lesson__mo-run')].map(el =>
        Math.round(new DOMMatrix(getComputedStyle(el).transform).m41))""")
    fails += 0 if say(len(set(still)) == 1 and still[0] < 0, "при загрузке все точки стоят в начале дорожки: " + str(still)) else 1
    picks = "() => [...document.querySelectorAll('#duration [data-motion-pick] button')].map(b => b.getAttribute('aria-pressed'))"
    fails += 0 if say(page.evaluate(picks).count("true") == 1, "выбрана одна длительность: " + str(page.evaluate(picks))) else 1
    page.click("#duration [data-motion-pick] button:nth-of-type(4)")
    dur = page.evaluate("() => getComputedStyle(document.querySelector('#duration .ds-lesson__mo-sheet')).transitionDuration")
    fails += 0 if say(dur.startswith("0.5s") and page.evaluate(picks)[3] == "true", "«500 мс» даёт шторке 0,5 с: " + dur) else 1
    page.click("#easing .ds-lesson__box[data-motion] [data-motion-actions] button")
    page.wait_for_timeout(300)
    lanes = page.evaluate("""() => [...document.querySelectorAll('#easing .ds-lesson__mo-run')].map(el =>
        Math.round(new DOMMatrix(getComputedStyle(el).transform).m41))""")
    fails += 0 if say(len(lanes) == 4 and lanes[2] > lanes[0] > lanes[1], "на трети пути кривые расходятся — конец > равномерно > начало: " + str(lanes)) else 1
    pins = page.query_selector_all("[data-hunt] button")
    miss = page.evaluate("[...document.querySelectorAll('[data-hunt-item]')].map(el => el.hasAttribute('data-hunt-miss'))")

    for pin, is_miss in zip(pins, miss):
        if not is_miss:
            pin.click()
            page.wait_for_timeout(30)

    fails += 0 if say(len(pins) == 10 and "5 из 5" in page.inner_text("[data-hunt-count-out]").lower(), "поиск лишних: 10 строк, найдено 5 из 5") else 1
    page.close()

    # «Уменьшить движение» в коробке: начальный кадр без сдвига, но прозрачный,
    # и смена режима не запускает переход сама.
    page = ctx.new_page()
    page.goto(BASE + "motion-middle/")
    page.wait_for_timeout(400)
    head("motion-middle · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    sheet = "() => { const s = getComputedStyle(document.querySelector('#reduce .ds-lesson__mo-sheet')); return [new DOMMatrix(s.transform).m42, +s.opacity]; }"
    before = page.evaluate(sheet)
    page.click("#reduce [data-layer='reduce'] button")
    page.wait_for_timeout(30)
    after = page.evaluate(sheet)
    fails += 0 if say(before[0] > 0 and before[1] == 1 and after == [0, 0], "«Уменьшить движение»: шторка не сдвинута, а прозрачна — %s → %s" % (before, after)) else 1
    page.close()

    # Подпись внутри отрезка шкалы времени не обрезается на телефоне: длина отрезка —
    # доля шкалы, и на 375 «данные» за 200 мс превращались в «данн».
    phone = browser.new_context(viewport={"width": 375, "height": 800})
    page = phone.new_page()
    page.goto(BASE + "motion-middle/")
    cut = page.evaluate("() => [...document.querySelectorAll('.ds-lesson__mo-seg')].filter(s => s.scrollWidth > s.clientWidth).map(s => s.textContent)")
    fails += 0 if say(not cut, "подписи шкалы не обрезаны на 375" + (": " + str(cut) if cut else "")) else 1
    phone.close()

    # Образцы урока — его содержимое: при системной настройке они играют по нажатию,
    # а над ними видно пояснение. Общее правило темы их не глушит.
    calm = browser.new_context(reduced_motion="reduce")
    page = calm.new_page()
    page.goto(BASE + "motion-middle/")
    page.wait_for_timeout(400)
    head("motion-middle · при «уменьшить движение»")
    note = page.evaluate("() => getComputedStyle(document.querySelector('.ds-lesson__mo-note')).display")
    dur = page.evaluate("() => getComputedStyle(document.querySelector('#reduce .ds-lesson__mo-sheet')).transitionDuration")
    # До нажатия у шторки длительность ухода, 0,2 с: главное, что не 0,01 мс общего правила темы.
    fails += 0 if say(note == "block" and dur == "0.2s", "пояснение видно, переход шторки не заглушен: %s, %s" % (note, dur)) else 1
    calm.close()

    page = ctx.new_page()
    page.goto(BASE + "motion-senior/")
    page.wait_for_timeout(400)
    head("motion-senior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    pins = page.query_selector_all("[data-hunt] button")
    miss = page.evaluate("[...document.querySelectorAll('[data-hunt-item]')].map(el => el.hasAttribute('data-hunt-miss'))")
    pins[miss.index(True)].click()
    page.wait_for_timeout(30)
    fails += 0 if say("0 из 5" in page.inner_text("[data-hunt-count-out]").lower(), "строка без нарушения разобрана, но не засчитана") else 1

    for pin, is_miss in zip(pins, miss):
        if not is_miss:
            pin.click()
            page.wait_for_timeout(30)

    fails += 0 if say(len(pins) == 8 and "5 из 5" in page.inner_text("[data-hunt-count-out]").lower() and page.is_visible("[data-hunt-all]"),
                      "прогон спецификации: 8 строк, найдено 5 из 5, итог показан") else 1
    page.close()

    # «Паттерны и состояния»: переключатель показывает одно состояние за раз, поиск считает
    # только недоделанное, правило обрезки из урока Middle работает — название в две строки.
    def hunt_all(page, total, found=5):
        pins = page.query_selector_all("[data-hunt] button")
        miss = page.evaluate("[...document.querySelectorAll('[data-hunt-item]')].map(el => el.hasAttribute('data-hunt-miss'))")
        pins[miss.index(True)].click()
        page.wait_for_timeout(30)
        ok = "0 из %d" % found in page.inner_text("[data-hunt-count-out]").lower()
        for pin, is_miss in zip(pins, miss):
            if not is_miss:
                pin.click()
                page.wait_for_timeout(30)
        return ok and len(pins) == total and "%d из %d" % (found, found) in page.inner_text("[data-hunt-count-out]").lower() and page.is_visible("[data-hunt-all]")

    shown = "() => [...document.querySelectorAll('#%s [data-switch-pane]')].filter(el => el.offsetParent !== null).map(el => el.getAttribute('data-switch-pane'))"

    page = ctx.new_page()
    page.goto(BASE + "patterns-states-junior/")
    page.wait_for_timeout(300)
    head("patterns-states-junior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    first = page.evaluate(shown % "five")
    page.click("#five [data-switch-btn=st4]")
    page.wait_for_timeout(30)
    now = page.evaluate(shown % "five")
    fails += 0 if say(first == ["st1"] and now == ["st4"] and page.is_visible("#five >> text=Не удалось загрузить заказы"),
                      "переключатель: сначала «Обычное», по нажатию — «Ошибка», видна одна панель") else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 2, "два тренажёра на странице") else 1
    fails += 0 if say(hunt_all(page, 10), "листы состояний: 10 кусков, лишнее не засчитано, найдено 5 из 5") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "patterns-states-middle/")
    page.wait_for_timeout(300)
    head("patterns-states-middle · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    page.click("#real-data [data-switch-btn=rd2]")
    page.wait_for_timeout(30)
    lines = page.evaluate("""() => { const el = document.querySelector('#real-data .ds-lesson__st-clamp');
        const lh = parseFloat(getComputedStyle(el).lineHeight); return Math.round(el.getBoundingClientRect().height / lh); }""")
    fails += 0 if say(lines == 2, "длинное название с правилом — две строки, сейчас %s" % lines) else 1
    gone = page.evaluate("""() => { const row = document.querySelector('#real-data .ds-lesson__st-nowrap').parentElement;
        const card = row.closest('.ds-lesson__wf').getBoundingClientRect();
        return row.querySelector('.ds-lesson__wf-price').getBoundingClientRect().left >= card.right; }""")
    fails += 0 if say(gone, "без правила цена уехала за край карточки") else 1
    fails += 0 if say(hunt_all(page, 10), "описание промокода: 10 строк, понятные не засчитаны, найдено 5 из 5") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "patterns-states-senior/")
    page.wait_for_timeout(300)
    head("patterns-states-senior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    fails += 0 if say(hunt_all(page, 10), "прогон экрана подписки: 10 строк, совпадения не засчитаны, найдено 5 из 5") else 1
    page.close()

    # «Иконки и иллюстрации»: слой выключается кнопкой, настройка меняет размер и цвет
    # всего образца одним нажатием, три поиска считают только чужое.
    page = ctx.new_page()
    page.goto(BASE + "icons-illustration-junior/")
    page.wait_for_timeout(300)
    head("icons-illustration-junior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    page.click("#grid [data-layer=icgrid] button")
    page.wait_for_timeout(30)
    grid = page.evaluate("getComputedStyle(document.querySelector('.ds-lesson__ic-grid')).display")
    keys = page.evaluate("getComputedStyle(document.querySelector('.ds-lesson__ic-keys')).display")
    fails += 0 if say(grid == "none" and keys != "none", "кнопка «Сетка» прячет сетку, опорные фигуры остаются") else 1
    shown = page.evaluate("[...document.querySelectorAll('#foreign [data-switch-pane]')].filter(el => el.offsetParent !== null).map(el => el.getAttribute('data-switch-pane'))")
    fails += 0 if say(shown == ["fg1"], "переключатель версий: видна одна, «На глаз»") else 1
    fails += 0 if say(hunt_all(page, 10), "ряд из десяти: по правилам не засчитаны, чужих найдено 5 из 5") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "icons-illustration-middle/")
    page.wait_for_timeout(300)
    head("icons-illustration-middle · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    made = page.evaluate("[document.querySelectorAll('[data-tune-pick] button').length, [...document.querySelectorAll('[data-tune-pick] button[aria-pressed=true]')].map(b => b.textContent)]")
    fails += 0 if say(made[0] == 8 and made[1] == ["24", "Основной"], "настройка: 8 кнопок, нажаты 24 и «Основной» — %s" % made) else 1
    page.click("#component [data-tune-pick='--ic-size'] button:nth-of-type(1)")
    page.click("#component [data-tune-pick='--ic-color'] button:nth-of-type(3)")
    page.wait_for_timeout(30)
    tuned = page.evaluate("""() => { const all = [...document.querySelectorAll('.ds-lesson__ic-tuned .ds-lesson__ic')];
        const probe = document.createElement('span'); probe.style.color = 'var(--wp--preset--color--text-action)'; document.body.appendChild(probe);
        const action = getComputedStyle(probe).color; probe.remove();
        return [all.length, all.every(el => Math.round(el.getBoundingClientRect().width) === 16), all.every(el => getComputedStyle(el).color === action)]; }""")
    fails += 0 if say(tuned[0] == 10 and tuned[1] and tuned[2], "одно нажатие — все %d иконок стали 16 и акцентными" % tuned[0]) else 1
    fails += 0 if say(hunt_all(page, 10), "набор на тёмном: без поломок не засчитаны, найдено 5 из 5") else 1
    page.close()

    # Плитка «как в тёмной теме» тёмная при любой теме сайта: на подложке цвета текста
    # в тёмной теме нарочная поломка (чёрная иконка, тёмный акцент) пропала бы.
    tiles = []
    for scheme in ("light", "dark"):
        look = browser.new_context(color_scheme=scheme)
        one = look.new_page()
        one.goto(BASE + "icons-illustration-middle/")
        tiles.append(one.evaluate("getComputedStyle(document.querySelector('.ds-lesson__ic-tile')).backgroundColor"))
        look.close()
    dark = [sum(int(v) for v in t[t.index("(") + 1:t.index(")")].split(",")[:3]) < 90 for t in tiles]
    fails += 0 if say(tiles[0] == tiles[1] and all(dark), "плитка «тёмная тема» тёмная в обеих темах сайта: %s" % tiles) else 1

    page = ctx.new_page()
    page.goto(BASE + "icons-illustration-senior/")
    page.wait_for_timeout(300)
    head("icons-illustration-senior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    fails += 0 if say(hunt_all(page, 10), "ревью: замечания по правилу не засчитаны, вкусовых найдено 5 из 5") else 1
    page.close()

    # «Фирменный стиль»: поиски по носителям и по тексту, переключатель носителей,
    # слой «Охранное поле» и граница поля, которая видна без скрипта.
    page = ctx.new_page()
    page.goto(BASE + "brand-language-junior/")
    page.wait_for_timeout(300)
    head("brand-language-junior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    fails += 0 if say(hunt_all(page, 10), "материалы за месяц: по стилю не засчитаны, нарушений найдено 5 из 5") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "brand-language-middle/")
    page.wait_for_timeout(300)
    head("brand-language-middle · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    shown = page.evaluate("[...document.querySelectorAll('#carriers [data-switch-pane]')].filter(el => el.offsetParent !== null).map(el => el.getAttribute('data-switch-pane'))")
    fails += 0 if say(shown == ["cr1"], "носители: видно одно — «Письмо»") else 1
    edge = "getComputedStyle(document.querySelector('#space .ds-lesson__bm-space')).borderTopColor"
    before = page.evaluate(edge)
    page.click("#space [data-layer=bmspace] button")
    page.wait_for_timeout(30)
    after = page.evaluate(edge)
    fails += 0 if say(before != "rgba(0, 0, 0, 0)" and after == "rgba(0, 0, 0, 0)", "слой «Охранное поле»: граница видна и прячется кнопкой") else 1
    fails += 0 if say(hunt_all(page, 10), "материалы нового дизайнера: по правилам не засчитаны, нарушений 5 из 5") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "brand-language-senior/")
    page.wait_for_timeout(300)
    head("brand-language-senior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    fails += 0 if say(hunt_all(page, 10), "черновик описания: доводы не засчитаны, моды и вкуса найдено 5 из 5") else 1
    page.close()

    # «Таблицы и списки»: живая сортировка переставляет строки и переносит `aria-sort`,
    # настройка плотности меняет высоту строк, три поиска считают только поломки.
    page = ctx.new_page()
    page.goto(BASE + "tables-lists-junior/")
    page.wait_for_timeout(300)
    head("tables-lists-junior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    table = "#sort [data-dt-sort]"
    state = """() => { const box = document.querySelector('#sort [data-dt-sort]');
        return [[...box.querySelectorAll('tbody tr')].map(r => r.cells[0].textContent.trim()),
                [...box.querySelectorAll('th[aria-sort]')].map(th => th.textContent.trim() + ':' + th.getAttribute('aria-sort')),
                box.querySelectorAll('th button').length, box.querySelector('[data-dt-live]').textContent.trim()]; }"""
    first = page.evaluate(state)
    fails += 0 if say(first[2] == 3 and first[0][:2] == ["1051", "1052"] and len(first[1]) == 1,
                      "сортировка: три заголовка-кнопки, сначала по доставке — %s" % first[:3]) else 1
    page.click(table + " thead th:nth-child(5) button")
    page.wait_for_timeout(30)
    big = page.evaluate(state)
    page.click(table + " thead th:nth-child(5) button")
    page.wait_for_timeout(30)
    small = page.evaluate(state)
    fails += 0 if say(big[0][0] == "1049" and big[1] == ["Сумма, ₽↓:descending"] and "сначала крупные" in big[3],
                      "первое нажатие по «Сумме» — крупные сверху, стрелка и строка состояния: %s" % big[1:]) else 1
    fails += 0 if say(small[0][0] == "1052" and small[1] == ["Сумма, ₽↑:ascending"] and "сначала меньшие" in small[3],
                      "второе нажатие — обратный порядок: %s" % small[1:]) else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 2, "два тренажёра на странице") else 1
    fails += 0 if say(hunt_all(page, 10), "макет таблицы: нормальное не засчитано, ошибок найдено 5 из 5") else 1
    page.close()

    # Без скрипта у живой таблицы нет кнопок, а порядок по умолчанию и строка состояния видны.
    plain = browser.new_context(java_script_enabled=False)
    page = plain.new_page()
    page.goto(BASE + "tables-lists-junior/")
    head("tables-lists-junior · таблица без скрипта")
    static = page.evaluate("""() => { const box = document.querySelector('#sort [data-dt-sort]');
        return [box.querySelectorAll('button').length, box.querySelector('th[aria-sort]').textContent.trim(),
                box.querySelector('[data-dt-live]').textContent.trim()]; }""")
    fails += 0 if say(static[0] == 0 and static[1] == "Доставка↑" and "сначала ближайшие" in static[2],
                      "без скрипта: кнопок нет, отсортировано по доставке — %s" % static) else 1
    plain.close()

    page = ctx.new_page()
    page.goto(BASE + "tables-lists-middle/")
    page.wait_for_timeout(300)
    head("tables-lists-middle · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    shown = page.evaluate("[...document.querySelectorAll('#select [data-switch-pane]')].filter(el => el.offsetParent !== null).map(el => el.getAttribute('data-switch-pane'))")
    fails += 0 if say(shown == ["sl1"], "выбор строк по шагам: виден один шаг — «Ничего не выбрано»") else 1
    row = "() => Math.round(document.querySelector('#wide .ds-lesson__dt-table tbody tr').getBoundingClientRect().height)"
    usual = page.evaluate(row)
    page.click("#wide [data-tune-pick] button:nth-of-type(3)")
    page.wait_for_timeout(30)
    dense = page.evaluate(row)
    fails += 0 if say(dense < usual, "плотность: «Плотно» ниже обычной строки — %s → %s" % (usual, dense)) else 1
    fixed = page.evaluate("""() => { const scroll = document.querySelector('#wide .ds-lesson__dt-scroll');
        const cell = scroll.querySelector('tbody .ds-lesson__dt-fix'); const before = cell.getBoundingClientRect().left;
        scroll.scrollLeft = 200; return [scroll.scrollWidth > scroll.clientWidth, Math.round(cell.getBoundingClientRect().left - before)]; }""")
    fails += 0 if say(fixed[0] and fixed[1] == 0, "десять колонок листаются, первая стоит на месте: %s" % fixed) else 1
    fails += 0 if say(hunt_all(page, 10), "прогон на длинных данных: нормальное не засчитано, поломок 5 из 5") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "tables-lists-senior/")
    page.wait_for_timeout(300)
    head("tables-lists-senior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 2, "два тренажёра на странице") else 1
    fails += 0 if say(hunt_all(page, 10), "таблица поставщиков: по правилам не засчитано, отличий 5 из 5") else 1
    page.close()

    # «Формы»: живые поля с подписью и без, тренажёр момента проверки в четырёх режимах,
    # три поиска ошибок. Тренажёр без скрипта скрыт целиком — режимы описаны таблицей.
    page = ctx.new_page()
    page.goto(BASE + "forms-junior/")
    page.wait_for_timeout(300)
    head("forms-junior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    page.get_by_label("Цена за пачку, ₽", exact=True).fill("890")
    labelled = page.evaluate("""() => { const f = document.getElementById('fj-price');
        return [f.labels.length, document.getElementById(f.getAttribute('aria-describedby')).textContent.trim()]; }""")
    fails += 0 if say(labelled[0] == 1 and "например 890" in labelled[1], "живое поле с подписью: подпись связана, подсказка описывает поле") else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 2, "два тренажёра на странице") else 1
    fails += 0 if say(hunt_all(page, 10), "форма «Новый сорт»: нормальное не засчитано, ошибок 5 из 5") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "forms-middle/")
    page.wait_for_timeout(300)
    head("forms-middle · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    fv = "#timing [data-fv]"
    look = """() => { const box = document.querySelector('#timing [data-fv]'); const err = box.querySelector('[data-fv-err]');
        return [err.hidden ? '' : err.textContent.trim(), box.querySelector('[data-fv-log]').textContent.trim(),
                box.querySelector('[data-fv-input]').getAttribute('aria-invalid')]; }"""
    modes = page.evaluate("[...document.querySelectorAll('#timing [data-fv-pick] button')].map(b => b.textContent.trim() + ':' + b.getAttribute('aria-pressed'))")
    fails += 0 if say(page.is_visible(fv) and len(modes) == 4 and modes[0].endswith(":true"),
                      "тренажёр показан, четыре режима, выбран «На вводе»: %s" % modes) else 1
    box = page.locator(fv)
    inn = box.locator("[data-fv-input]")
    inn.type("7")
    one = page.evaluate(look)
    fails += 0 if say(one[0] == "В ИНН компании 10 цифр, а сейчас 1" and "первой же цифре" in one[1] and one[2] == "true",
                      "на вводе: ошибка на первой цифре — %s" % one[:2]) else 1
    inn.type("7a")
    fails += 0 if say(page.evaluate(look)[0].startswith("В ИНН только цифры"), "на вводе: буква — «только цифры»") else 1

    box.locator("[data-fv-pick] button").nth(1).click()
    blank = page.evaluate(look) + [inn.input_value()]
    inn.type("770123456")
    typing = page.evaluate(look)
    box.locator("#fv-kpp").click()
    left = page.evaluate(look)
    inn.click()
    inn.press("End")
    inn.type("7")
    stale = page.evaluate(look)
    box.locator("#fv-kpp").click()
    fixed = page.evaluate(look)
    fails += 0 if say(blank[0] == "" and blank[3] == "" and typing[0] == "", "при уходе: смена режима очищает поле, пока вводят — тихо") else 1
    fails += 0 if say(left[0] == "В ИНН компании 10 цифр, а сейчас 9" and "закончили с полем" in left[1], "при уходе: ошибка после ухода из поля — %s" % left[:2]) else 1
    fails += 0 if say(stale[0] != "" and "пока вы не уйдёте" in stale[1], "при уходе: исправили — ошибка висит до ухода") else 1
    fails += 0 if say(fixed[0] == "" and fixed[2] == "false" and "ошибки нет" in fixed[1], "при уходе: ушли из верного поля — ошибки нет") else 1
    box.locator("#fv-kpp").click()
    inn.click()
    box.locator("[data-fv-pick] button").nth(1).click()
    inn.click()
    box.locator("#fv-kpp").click()
    fails += 0 if say(page.evaluate(look)[0] == "", "при уходе: из пустого поля ушли — не ругают") else 1

    box.locator("[data-fv-pick] button").nth(2).click()
    inn.type("770123456")
    box.locator("#fv-kpp").click()
    quiet = page.evaluate(look)
    box.locator("[data-fv-submit]").click()
    late = page.evaluate(look)
    fails += 0 if say(quiet[0] == "" and late[0].endswith("сейчас 9") and "только после «Сохранить»" in late[1],
                      "при отправке: тихо до кнопки, ошибка после — %s" % late[:2]) else 1
    inn.fill("")
    box.locator("[data-fv-submit]").click()
    fails += 0 if say(page.evaluate(look)[0] == "Введите ИНН поставщика", "при отправке: пустое поле — «Введите ИНН поставщика»") else 1

    box.locator("[data-fv-pick] button").nth(3).click()
    inn.type("770123456")
    box.locator("#fv-kpp").click()
    shown_err = page.evaluate(look)
    inn.click()
    inn.press("End")
    inn.type("7")
    gone = page.evaluate(look)
    fails += 0 if say(shown_err[0].endswith("сейчас 9") and gone[0] == "" and "исчезла" in gone[1],
                      "при уходе, потом на вводе: ошибка после ухода, исчезает на исправлении — %s" % gone[:2]) else 1
    box.locator("[data-fv-submit]").click()
    fails += 0 if say("форма сохранилась" in page.evaluate(look)[1], "верный ИНН — «форма сохранилась»") else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 1, "один тренажёр-викторина на странице") else 1
    fails += 0 if say(hunt_all(page, 10), "шаг «Реквизиты»: нормальное не засчитано, ошибок 5 из 5") else 1
    page.close()

    plain = browser.new_context(java_script_enabled=False)
    page = plain.new_page()
    page.goto(BASE + "forms-middle/")
    head("forms-middle · тренажёр без скрипта")
    fails += 0 if say(not page.is_visible("#timing [data-fv]") and page.is_visible("#timing table"),
                      "без скрипта: коробки тренажёра нет, таблица режимов видна") else 1
    plain.close()

    page = ctx.new_page()
    page.goto(BASE + "forms-senior/")
    page.wait_for_timeout(300)
    head("forms-senior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 1, "один тренажёр-викторина на странице") else 1
    fails += 0 if say(hunt_all(page, 10), "форма «Промокод» на ревью: по правилам не засчитано, нарушений 5 из 5") else 1
    page.close()

    # «Дашборды и графики»: живая шкала двигает начало и пересчитывает «выглядит / на деле»,
    # порог красит дни за полосой, три поиска ошибок. Без скрипта ползунков нет, графики стоят
    # как в разметке: столбцы от нуля, порог ±15 % с двумя выделенными днями.
    def slide(page, sel, value):
        page.evaluate("""([sel, v]) => { const el = document.querySelector(sel); el.value = v;
            el.dispatchEvent(new Event('input', { bubbles: true })); }""", [sel, value])
        page.wait_for_timeout(30)

    def cols(page):
        return page.evaluate("""() => [...document.querySelectorAll('[data-axis] .ds-lesson__col')]
            .map(el => el.getBoundingClientRect().height)""")

    page = ctx.new_page()
    page.goto(BASE + "dashboards-junior/")
    page.wait_for_timeout(300)
    head("dashboards-junior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    out = page.inner_text("[data-axis-out]")
    h = cols(page)
    fails += 0 if say(page.is_visible("[data-axis-pick]") and "Шкала от 0" in out and "в 1,1 раза" in out and "на 10" in out
                      and 1.05 < h[1] / h[0] < 1.15, "шкала от нуля: ползунок виден, «в 1,1 раза», столбцы 1 : %.2f" % (h[1] / h[0])) else 1
    slide(page, "[data-axis-input]", 380)
    out = page.inner_text("[data-axis-out]")
    h = cols(page)
    ticks = page.evaluate("[...document.querySelectorAll('[data-axis] .ds-lesson__tick')].filter(t => t.offsetParent !== null).map(t => t.textContent.trim())")
    fails += 0 if say("в 3 раза" in out and 2.9 < h[1] / h[0] < 3.1 and ticks == ["380", "400"],
                      "шкала от 380: «в 3 раза», столбцы 1 : %.2f, деления %s" % (h[1] / h[0], ticks)) else 1
    slide(page, "[data-axis-input]", 200)
    fails += 0 if say("в 1,2 раза" in page.inner_text("[data-axis-out]"), "шкала от 200: «в 1,2 раза»") else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 2, "два тренажёра на странице") else 1
    fails += 0 if say(hunt_all(page, 10), "экран «Сводка»: нормальное не засчитано, ошибок 5 из 5") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "dashboards-middle/")
    page.wait_for_timeout(300)
    head("dashboards-middle · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    bad = "() => document.querySelectorAll('[data-band] .ds-lesson__dev.is-bad').length"
    out = page.inner_text("[data-band-out]")
    fails += 0 if say(page.is_visible("[data-band-pick]") and "2 из 30" in out and "Выделено то" in out and page.evaluate(bad) == 2,
                      "порог ±15 %: выделено 2 дня из 30") else 1
    slide(page, "[data-band-input]", 5)
    out = page.inner_text("[data-band-out]")
    fails += 0 if say("13 из 30" in out and "Тревога" in out and page.evaluate(bad) == 13, "порог ±5 %: 13 дней и предупреждение о тревоге") else 1
    slide(page, "[data-band-input]", 40)
    fails += 0 if say("1 из 30" in page.inner_text("[data-band-out]") and page.evaluate(bad) == 1, "порог ±40 %: один день") else 1
    slide(page, "[data-band-input]", 50)
    out = page.inner_text("[data-band-out]")
    band = page.evaluate("getComputedStyle(document.querySelector('[data-band-strip]')).getPropertyValue('--t').trim()")
    fails += 0 if say("0 из 30" in out and "Ни одного" in out and band == "50", "порог ±50 %%: ни одного дня, полоса --t: %s" % band) else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 2, "два тренажёра-викторины на странице") else 1
    fails += 0 if say(hunt_all(page, 10), "экран «Продажи и склад»: нормальное не засчитано, ошибок 5 из 5") else 1
    page.close()

    plain = browser.new_context(java_script_enabled=False)
    page = plain.new_page()
    page.goto(BASE + "dashboards-junior/")
    head("dashboards-junior · шкала без скрипта")
    h = cols(page)
    fails += 0 if say(not page.is_visible("[data-axis-pick]") and not page.is_visible("[data-axis-out]") and h and 1.05 < h[1] / h[0] < 1.15,
                      "без скрипта: ползунка нет, столбцы от нуля 1 : %.2f" % (h[1] / h[0] if h else 0)) else 1
    page.close()
    page = plain.new_page()
    page.goto(BASE + "dashboards-middle/")
    head("dashboards-middle · порог без скрипта")
    fails += 0 if say(not page.is_visible("[data-band-pick]") and page.evaluate(bad) == 2 and page.is_visible("[data-band] .ds-lesson__plot"),
                      "без скрипта: ползунка нет, порог ±15 %, выделено 2 дня") else 1
    page.close()
    plain.close()

    page = ctx.new_page()
    page.goto(BASE + "dashboards-senior/")
    page.wait_for_timeout(300)
    head("dashboards-senior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 1, "один тренажёр-викторина на странице") else 1
    fails += 0 if say(hunt_all(page, 10), "набор после запуска подписки: нормальное не засчитано, ошибок 5 из 5") else 1
    page.close()
    # «Формулировки интерфейса»: тренажёр «вычеркните лишнее» — нажатие зачёркивает кусок фразы,
    # под фразой то, что осталось; вычеркнутое условие даёт подсказку, что пропало; «Показать лишнее»
    # вычёркивает за человека и открывает итог. Без скрипта лишнее зачёркнуто стилем, кнопок нет.
    def strike(page, n):
        box = page.locator("[data-strike]").nth(n)
        return {
            "out": box.locator("[data-strike-out]").inner_text().replace("\xa0", " "),
            "meta": box.locator("[data-strike-meta]").inner_text(),
            "note": box.locator("[data-strike-note]").inner_text() if box.locator("[data-strike-note]").is_visible() else "",
            "done": box.locator("[data-strike-done]").is_visible(),
        }

    panes = "() => [...document.querySelectorAll('#%s [data-switch-pane]')].filter(el => el.offsetParent !== null).map(el => el.getAttribute('data-switch-pane'))"

    def press(page, n, word):
        page.locator("[data-strike]").nth(n).locator("button[data-strike-w]", has_text=word).first.click()
        page.wait_for_timeout(30)

    page = ctx.new_page()
    page.goto(BASE + "ui-copy-junior/")
    page.wait_for_timeout(300)
    head("ui-copy-junior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    first = page.evaluate(panes % "button")
    page.click("#button [data-switch-btn=bt3]")
    page.wait_for_timeout(30)
    fails += 0 if say(first == ["bt1"] and page.evaluate(panes % "button") == ["bt3"] and page.is_visible("#button >> text=Оставить подписку"),
                      "окно отмены: сначала «Да и Нет», по нажатию — «Действие на кнопке»") else 1
    s = strike(page, 0)
    fails += 0 if say(len(page.query_selector_all("[data-strike]")) == 3 and s["out"].startswith("Пожалуйста, обратите внимание")
                      and "0 из 4" in s["meta"] and not s["note"] and not s["done"], "три фразы, сначала ничего не вычеркнуто: 0 из 4") else 1
    press(page, 0, "Пожалуйста")
    press(page, 0, "все")
    s = strike(page, 0)
    fails += 0 if say(s["out"].startswith("Изменения в вашей подписке") and "2 из 4" in s["meta"], "вычеркнули два куска: «Изменения в вашей…», 2 из 4") else 1
    press(page, 0, "со следующей доставки")
    s = strike(page, 0)
    fails += 0 if say("Пропало главное" in s["note"] and "доставки" not in s["out"] and not s["done"], "вычеркнули условие: подсказка «Пропало главное»") else 1
    press(page, 0, "со следующей доставки")
    fails += 0 if say(not strike(page, 0)["note"], "вернули условие: подсказка ушла") else 1
    page.locator("[data-strike]").nth(0).locator("[data-strike-actions] button").click()
    page.wait_for_timeout(30)
    s = strike(page, 0)
    fails += 0 if say(s["out"] == "Изменения вступят в силу со следующей доставки." and "4 из 4" in s["meta"] and s["done"],
                      "«Показать лишнее»: «Изменения вступят в силу со следующей доставки.», итог открыт") else 1
    page.locator("[data-strike]").nth(1).locator("[data-strike-actions] button").click()
    page.wait_for_timeout(30)
    fails += 0 if say(strike(page, 1)["out"] == "Адрес доставки сохранён.", "вторая фраза: «Адрес доставки сохранён.»") else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 1, "один тренажёр-викторина на странице") else 1
    fails += 0 if say(hunt_all(page, 10), "экран «Моя подписка»: нормальное не засчитано, ошибок 5 из 5") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "ui-copy-middle/")
    page.wait_for_timeout(300)
    head("ui-copy-middle · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    press(page, 0, "при заказе от")
    s = strike(page, 0)
    fails += 0 if say("Пропало условие" in s["note"] and "690" in s["note"] and "2 000" not in s["out"], "вычеркнули сумму: «Пропало условие… 690 ₽»") else 1
    press(page, 0, "при заказе от")
    page.locator("[data-strike]").nth(0).locator("[data-strike-actions] button").click()
    page.wait_for_timeout(30)
    s = strike(page, 0)
    fails += 0 if say(s["out"] == "Доставка по Москве в пределах МКАД бесплатна при заказе от 2 000 ₽." and s["done"],
                      "сокращено без потери условий: «…бесплатна при заказе от 2 000 ₽.»") else 1
    page.locator("[data-strike]").nth(1).locator("[data-strike-actions] button").click()
    page.wait_for_timeout(30)
    fails += 0 if say(strike(page, 1)["out"] == "Скидка 10 % на первую доставку для новых подписчиков по промокоду ЛЕС10",
                      "баннер: восклицания ушли, четыре условия остались") else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 2, "два тренажёра-викторины на странице") else 1
    fails += 0 if say(hunt_all(page, 10), "кабинет, письмо и чат: нормальное не засчитано, ошибок 5 из 5") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "ui-copy-senior/")
    page.wait_for_timeout(300)
    head("ui-copy-senior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    page.click("#tone [data-switch-btn=tv2]")
    page.wait_for_timeout(30)
    fails += 0 if say(page.evaluate(panes % "tone") == ["tv2"] and page.is_visible("#tone >> text=Самый свежий кофе в мире!!!"),
                      "правила тона: по нажатию — «Шкалы и примеры»") else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 2, "два тренажёра-викторины на странице") else 1
    fails += 0 if say(hunt_all(page, 10), "рассылка по правилам: нормальное не засчитано, нарушений 5 из 5") else 1
    page.close()

    # «Тексты ошибок и пустых состояний»: тренажёр «соберите сообщение» — у каждой части сообщения
    # радиокнопки, экран сверху собирается из выбранного; сначала стоят варианты разработчика,
    # разбор виден только у выбранного, «готово» — когда все части верные. Пустой текст прячет кусок.
    def compose(page, n):
        box = page.locator("[data-compose]").nth(n)
        slots = box.evaluate("""b => Object.fromEntries([...b.querySelectorAll('[data-compose-slot]')]
            .map(s => [s.getAttribute('data-compose-slot'), s.hidden ? null : s.textContent.replace(/\\s+/g, ' ').trim()]))""")
        return {"slots": slots, "meta": box.locator("[data-compose-meta]").inner_text(),
                "done": box.locator("[data-compose-done]").is_visible(),
                "notes": box.locator("[data-compose-note]:visible").count()}

    def pick(page, n, part, i):
        page.locator("[data-compose]").nth(n).locator('[data-compose-part="%s"] label' % part).nth(i).click()
        page.wait_for_timeout(30)

    page = ctx.new_page()
    page.goto(BASE + "errors-empty-states-junior/")
    page.wait_for_timeout(300)
    head("errors-empty-states-junior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    first = page.evaluate(panes % "what")
    page.click("#what [data-switch-btn=er3]")
    page.wait_for_timeout(30)
    fails += 0 if say(first == ["er1"] and page.evaluate(panes % "what") == ["er3"] and page.is_visible("#what >> text=Оформить ещё раз"),
                      "ошибка оформления: сначала код, по нажатию — «Словами человека»") else 1
    c = compose(page, 0)
    fails += 0 if say(c["slots"] == {"what": "Ошибка оплаты", "text": "Пожалуйста, проверьте данные карты и повторите попытку.", "btn": "ОК"}
                      and "0 из 3" in c["meta"] and c["notes"] == 3 and not c["done"],
                      "сообщение об оплате: сначала варианты разработчика, 0 из 3, видно три разбора") else 1
    pick(page, 0, "what", 1)
    pick(page, 0, "text", 1)
    c = compose(page, 0)
    fails += 0 if say(c["slots"]["what"] == "Банк не подтвердил оплату" and "2 из 3" in c["meta"] and not c["done"],
                      "заголовок и текст верные: «Банк не подтвердил оплату», 2 из 3") else 1
    pick(page, 0, "btn", 1)
    c = compose(page, 0)
    fails += 0 if say(c["slots"]["btn"] == "Оплатить другой картой" and "3 из 3" in c["meta"] and c["done"],
                      "кнопка «Оплатить другой картой»: 3 из 3, итог открыт") else 1
    pick(page, 0, "btn", 2)
    fails += 0 if say(not compose(page, 0)["done"], "кнопка «Вернуться на главную»: итог снова закрыт") else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 1, "один тренажёр-викторина на странице") else 1
    fails += 0 if say(hunt_all(page, 10), "приложение магазина: нормальное не засчитано, ошибок 5 из 5") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "errors-empty-states-middle/")
    page.wait_for_timeout(300)
    head("errors-empty-states-middle · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    first = page.evaluate(panes % "four")
    page.click("#four [data-switch-btn=fo4]")
    page.wait_for_timeout(30)
    fails += 0 if say(first == ["fo0"] and page.evaluate(panes % "four") == ["fo4"] and page.is_visible("#four >> text=Заказы не загрузились"),
                      "четыре пустоты: сначала одна заглушка, по нажатию — «Сломалось»") else 1
    press(page, 0, "Извините,")
    s = strike(page, 0)
    fails += 0 if say("единственное извинение" in s["note"] and not s["done"], "вычеркнули «Извините»: подсказка про единственное извинение") else 1
    press(page, 0, "Извините,")
    page.locator("[data-strike]").nth(0).locator("[data-strike-actions] button").click()
    page.wait_for_timeout(30)
    s = strike(page, 0)
    fails += 0 if say(s["out"] == "Извините, оформление новых заказов недоступно. Уже оформленные заказы приедут в срок. Оформить новый можно будет после 15:00."
                      and "5 из 5" in s["meta"] and s["done"], "плашка сбоя: одно извинение и три ответа, 5 из 5") else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 2, "два тренажёра-викторины на странице") else 1
    fails += 0 if say(hunt_all(page, 10), "пять ситуаций: нормальное не засчитано, ошибок 5 из 5") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "errors-empty-states-senior/")
    page.wait_for_timeout(300)
    head("errors-empty-states-senior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    c = compose(page, 0)
    fails += 0 if say(c["slots"]["what"] == "Сессия истекла" and "0 из 4" in c["meta"] and c["notes"] == 4,
                      "вход закончился: сначала «Сессия истекла», 0 из 4") else 1
    pick(page, 0, "why", 2)
    fails += 0 if say(compose(page, 0)["slots"]["why"] is None, "«Без причины»: строка причины спрятана") else 1
    for part in ("what", "why"):
        pick(page, 0, part, 1)
    pick(page, 0, "safe", 2)
    pick(page, 0, "btn", 2)
    c = compose(page, 0)
    fails += 0 if say(c["slots"] == {"what": "Вход закончился", "why": "Прошло 30 минут без действий.", "safe": "Корзина и адрес доставки сохранены.",
                                     "btn": "Войти и продолжить"} and "4 из 4" in c["meta"] and c["done"],
                      "все четыре части по схеме: 4 из 4, итог открыт") else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 2, "два тренажёра-викторины на странице") else 1
    fails += 0 if say(hunt_all(page, 10), "сводка от разработки: нормальное не засчитано, нарушений 5 из 5") else 1
    page.close()

    # «Компоненты и варианты»: панель свойств `data-props` — радиокнопки свойств ставят образцу
    # атрибуты `data-cv-*`, подпись встаёт из `data-props-set`, имя варианта собирается из шаблона,
    # пояснение выбранного состояния — из `data-props-say`.
    def props(page, n):
        return page.locator("[data-props]").nth(n).evaluate("""b => {
            const t = b.querySelector('[data-props-target]');
            const vis = el => !!el && el.offsetParent !== null && getComputedStyle(el).display !== 'none';
            return {name: (b.querySelector('[data-props-out]') || {}).textContent || '',
                    said: (b.querySelector('[data-props-said]') || {}).textContent || '',
                    attrs: Object.fromEntries([...t.attributes].filter(a => a.name.startsWith('data-cv-')).map(a => [a.name.slice(8), a.value])),
                    label: t.textContent.replace(/\\s+/g, ' ').trim(),
                    icon: vis(t.querySelector('.ds-lesson__cv-ic')), spin: vis(t.querySelector('.ds-lesson__cv-spin')),
                    bg: getComputedStyle(t).backgroundColor, outline: getComputedStyle(t).outlineStyle,
                    w: Math.round(t.getBoundingClientRect().width)};
        }""")

    def prop(page, n, key, i):
        page.locator("[data-props]").nth(n).locator('[data-props-prop="%s"] label' % key).nth(i).click()
        page.wait_for_timeout(30)

    LABEL_FIT = """id => { const pane = document.querySelector('[data-switch-pane="' + id + '"]');
        const card = pane.querySelector('.ds-lesson__cv-card').getBoundingClientRect();
        const btns = [...pane.querySelectorAll('.ds-lesson__cv-btn')].map(b => b.getBoundingClientRect());
        return {over: btns[2].right - card.right, tall: btns[2].height - btns[1].height}; }"""

    page = ctx.new_page()
    page.goto(BASE + "components-variants-junior/")
    page.wait_for_timeout(300)
    head("components-variants-junior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    p = props(page, 0)
    fails += 0 if say(p["name"] == "Вид=Основная, Размер=Большая" and p["attrs"] == {"kind": "primary", "size": "l", "icon": "on", "label": "mid"} and p["icon"],
                      "панель свойств: сначала «Вид=Основная, Размер=Большая», иконка видна") else 1
    prop(page, 0, "kind", 1)
    prop(page, 0, "size", 1)
    p = props(page, 0)
    fails += 0 if say(p["name"] == "Вид=Вторичная, Размер=Малая" and p["attrs"]["kind"] == "secondary" and p["attrs"]["size"] == "s",
                      "вид и размер меняют имя слоя: «Вид=Вторичная, Размер=Малая»") else 1
    prop(page, 0, "icon", 1)
    prop(page, 0, "label", 2)
    p = props(page, 0)
    fails += 0 if say(not p["icon"] and p["label"] == "Оформить подписку на три месяца" and p["name"] == "Вид=Вторичная, Размер=Малая",
                      "иконка и подпись меняют образец, но не имя варианта") else 1
    raw = page.evaluate(LABEL_FIT, "lb1")
    page.click("#labels [data-switch-btn=lb2]")
    page.wait_for_timeout(30)
    ok = page.evaluate(LABEL_FIT, "lb2")
    fails += 0 if say(raw["over"] > 4 and ok["over"] <= 0.5 and ok["tall"] > 8,
                      "длинная подпись: без правил вылезает за карточку на %d px, с правилами переносится" % raw["over"]) else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 1, "один тренажёр-викторина на странице") else 1
    fails += 0 if say(hunt_all(page, 9, 4), "каталог и корзина: экземпляры не засчитаны, копий 4 из 4") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "components-variants-middle/")
    page.wait_for_timeout(300)
    head("components-variants-middle · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    spins = page.evaluate("() => [...document.querySelectorAll('#states .ds-lesson__cv-spin')].filter(s => s.offsetParent !== null && getComputedStyle(s).display !== 'none').length")
    fails += 0 if say(spins == 1, "лист состояний: индикатор загрузки виден только у «Загрузки» (%d)" % spins) else 1
    p = props(page, 0)
    fails += 0 if say(p["attrs"].get("state") == "focus" and p["outline"] != "none" and p["said"].startswith("Фокус:") and not p["spin"],
                      "панель состояний: сначала фокус — рамка и пояснение, индикатора нет") else 1
    prop(page, 0, "state", 0)
    rest = props(page, 0)
    prop(page, 0, "state", 5)
    load = props(page, 0)
    fails += 0 if say(load["spin"] and not load["icon"] and load["w"] == rest["w"] and load["name"] == "Вид=Основная, Состояние=Загрузка",
                      "загрузка: индикатор на месте иконки, ширина та же (%d px)" % load["w"]) else 1
    prop(page, 0, "state", 4)
    off = props(page, 0)
    fails += 0 if say(off["bg"] != rest["bg"] and off["said"].startswith("Неактивна:"), "неактивна: своя подложка, пояснение сменилось") else 1
    prop(page, 0, "kind", 1)
    prop(page, 0, "state", 1)
    fails += 0 if say(props(page, 0)["name"] == "Вид=Вторичная, Состояние=Наведение", "вид и состояние: «Вид=Вторичная, Состояние=Наведение»") else 1
    first = page.evaluate(panes % "field")
    page.click("#field [data-switch-btn=fd4]")
    page.wait_for_timeout(30)
    fails += 0 if say(first == ["fd1"] and page.evaluate(panes % "field") == ["fd4"] and page.is_visible("#field >> text=действовал до 30"),
                      "поле промокода: сначала покой, по нажатию — ошибка с текстом") else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 1, "один тренажёр-викторина на странице") else 1
    fails += 0 if say(hunt_all(page, 9, 6), "описание кнопки: нормальное не засчитано, ошибок 6 из 6") else 1
    page.close()

    page = ctx.new_page()
    page.goto(BASE + "components-variants-senior/")
    page.wait_for_timeout(300)
    head("components-variants-senior · со скриптом")
    leak = page.evaluate(HIDDEN)
    fails += 0 if say(not leak, "[hidden] скрывает" + (": " + str(leak) if leak else "")) else 1
    fails += 0 if say(len(page.query_selector_all("[data-quiz]")) == 1, "один тренажёр-викторина на странице") else 1
    fails += 0 if say(hunt_all(page, 8), "сообщение о выпуске: нормальное не засчитано, ошибок 5 из 5") else 1
    page.close()

    plain = browser.new_context(java_script_enabled=False)
    page = plain.new_page()
    page.goto(BASE + "ui-copy-junior/")
    head("ui-copy-junior · вычёркивание без скрипта")
    cut = page.evaluate("""() => [...document.querySelectorAll('[data-strike-w="cut"]')]
        .map(el => getComputedStyle(el).textDecorationLine)""")
    fails += 0 if say(len(cut) == 12 and all("line-through" in c for c in cut) and not page.is_visible("[data-strike-meta]"),
                      "лишнее зачёркнуто стилем: %d кусков, счётчика нет" % len(cut)) else 1
    page.close()
    for slug, notes, what in (("errors-empty-states-junior", 9, "Банк не подтвердил оплату"), ("errors-empty-states-senior", 12, "Вход закончился")):
        page = plain.new_page()
        page.goto(BASE + slug + "/")
        head(slug + " · сборка сообщения без скрипта")
        box = page.locator("[data-compose]").nth(0)
        fails += 0 if say(box.locator("input:visible").count() == 0 and box.locator("[data-compose-note]:visible").count() == notes
                          and box.locator('[data-compose-slot="what"]').inner_text() == what and not page.is_visible("[data-compose-meta]"),
                          "радиокнопок нет, разборов %d, на экране образец «%s»" % (notes, what)) else 1
        page.close()
    for slug, sheet in (("components-variants-junior", 0), ("components-variants-middle", 6)):
        page = plain.new_page()
        page.goto(BASE + slug + "/")
        head(slug + " · панель свойств без скрипта")
        cells = page.locator("#states .ds-lesson__cv-cell:visible").count() if sheet else 0
        fails += 0 if say(not page.is_visible(".ds-lesson__cv-panel") and not page.is_visible("[data-props-out]")
                          and page.is_visible("[data-props-target]") and cells == sheet,
                          "панели и имени нет, образец виден" + (", лист состояний — %d плиток" % cells if sheet else "")) else 1
        page.close()
    plain.close()
    browser.close()

print("\nнеудач:", fails)
sys.exit(1 if fails else 0)
