"""Превращает присланный урок в тело записи для сайта.

Заказчица пишет урок отдельной страницей: своя разметка, свой CSS, свой скрипт.
На сайте урок должен быть на наших классах и токенах, иначе каждый из ста
одиннадцати уроков пришлось бы чинить поодиночке (D153).

Скрипт делает механическую часть и только её:

1. Снимает обвязку страницы — шапку, переключатель темы, свой CSS и скрипт.
   Заголовок и лид уходят в название и анонс записи, метки ступеней рисует
   блок `designstack/lesson-header` из полей, а не разметка урока.
2. Переводит классы по таблице ниже. Класс, которого в таблице нет, остаётся
   как есть и попадает в отчёт: это компонент, для которого ещё нет наших
   стилей, и его надо завести руками.
3. Разворачивает тренажёр из данных скрипта в разметку: без JS вопросы должны
   быть видны списком, иначе страница теряет половину смысла.
4. Приводит обращение к «вы» (D150).

Чего скрипт не делает: не сокращает, не переписывает и не решает за редактора.
Всё, что он изменил в тексте, он перечисляет — это читают глазами.

    python scripts/convert_lesson.py docs/content/sources/<файл>.html
    python scripts/convert_lesson.py <файл> --out docs/content/lessons/<слаг>.body.html
"""
import argparse
import html
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Обвязка страницы: на сайте её рисует тема.
DROP_BLOCKS = ("topbar", "hero", "levels")

# Класс присланного урока → наш класс. Пустая строка — класс снимается, разметка остаётся.
CLASS_MAP = {
    "goals": "ds-lesson__goals",
    "sec-head": "ds-lesson__section-head",
    "sec-sub": "ds-lesson__lead",
    "h2-num": "ds-lesson__num",
    "box": "ds-lesson__box",
    "box-head": "ds-lesson__box-head",
    "box-body": "ds-lesson__box-body",
    "box-foot": "ds-lesson__box-foot",
    "warnbox": "ds-lesson__warn",
    "rule": "ds-lesson__rule",
    "note": "ds-lesson__note",
    "probe": "ds-lesson__probe",
    "aim": "ds-lesson__aim",
    "say": "ds-lesson__say",
    "said": "ds-lesson__said",
    "sheet": "ds-lesson__sheet",
    "spacer": "ds-lesson__spacer",
    "tbl-scroll": "ds-lesson__table",
    "err-list": "ds-lesson__errors",
    "tag": "ds-lesson__tag",
    "tm": "ds-lesson__time",
    "t": "ds-lesson__timing",
    "qpair": "ds-lesson__pair",
    "q-good": "ds-lesson__pair--good",
    "q-bad": "ds-lesson__pair--bad",
    "q-mark": "ds-lesson__mark",
    "q-why": "ds-lesson__why",
    "q-text": "ds-lesson__text",
    "script-block": "ds-lesson__block",
    "dim": "ds-lesson__dim",
    "num": "ds-lesson__num",
    "obs": "ds-lesson__obs",
    "int": "ds-lesson__int",
    # компоненты уроков Middle и Senior — стили для них уже стоят в patterns.css
    "flaw": "ds-lesson__flaw",
    "fix": "ds-lesson__flaw--fix",
    "funnel": "ds-lesson__funnel",
    "tier": "ds-lesson__tier",
    "lab": "ds-lesson__tier-label",
    "arrowdown": "ds-lesson__arrow",
    "trace-row": "ds-lesson__trace-row",
    "step": "ds-lesson__step",
    "k": "ds-lesson__step-key",
    "v": "ds-lesson__step-val",
    "verdict": "ds-lesson__verdict",
    "keep": "ds-lesson__verdict--keep",
    "kill": "ds-lesson__verdict--kill",
    "hold": "ds-lesson__verdict--hold",
    "qline": "ds-lesson__qline",
    "num-c": "ds-lesson__qline-n",
    "why": "ds-lesson__qline-why",
    "who": "ds-lesson__who",
    "meta": "ds-lesson__meta",
    "legend": "ds-lesson__legend",
    "mk": "ds-lesson__mk",
    "cut": "ds-lesson__mk--cut",
    "miss": "ds-lesson__mk--miss",
    "stop": "ds-lesson__mk--stop",
    "think": "ds-lesson__mk--think",
    "ask": "ds-lesson__ask",
    "cmt": "ds-lesson__cmt",
    "ladder": "ds-lesson__ladder",
    "rung": "ds-lesson__rung",
    "st": "ds-lesson__rung-step",
    "doc": "ds-lesson__doc",
    "pagemark": "ds-lesson__pagemark",
    "acc": "ds-lesson__acc",
    "ans": "ds-lesson__ans",
    # компоненты темы «Юзабилити-тесты»
    "drillmark": "ds-lesson__tag",
    "weeks": "ds-lesson__weeks",
    "wk": "ds-lesson__week",
    "big": "ds-lesson__big",
    "cad": "ds-lesson__cadence",
    "cad-out": "ds-lesson__cadence-out",
    "kv": "ds-lesson__kv",
    "calc": "ds-lesson__calc",
    "fld": "ds-lesson__field",
    "out": "ds-lesson__out",
    "cap": "ds-lesson__cap",
    "panel": "ds-lesson__panel",
    "acts": "ds-lesson__acts",
    "vd": "ds-lesson__vd",
    "ok": "is-ok",
    "no": "is-no",
    "done": "is-done",
    "wrap": "",
    "btn": "",
    "lv": "",
    "on": "",
    "kicker": "",
    "lede": "",
    "q": "",
}

# Местоимения второго лица: «ты» → «вы» (D150).
PRONOUNS = {
    "ты": "вы", "тебе": "вам", "тебя": "вас", "тобой": "вами", "тобою": "вами",
    "твой": "ваш", "твоя": "ваша", "твоё": "ваше", "твое": "ваше", "твои": "ваши",
    "твоего": "вашего", "твоей": "вашей", "твоему": "вашему", "твоим": "вашим",
    "твою": "вашу", "твоих": "ваших", "твоими": "вашими", "твоём": "вашем",
    "твоем": "вашем", "твоя́": "ваша",
}


# Глаголы второго лица и словарь сайта. Список снят с уже утверждённого перевода трёх
# уроков: он не выдуман, а извлечён сравнением присланных файлов с тем, что стоит на сайте.
WORDS = {
    # словарь сайта (docs/VOICE.md). Слова «уровень» здесь нет намеренно: в уроках про
    # структуру сайта «верхний уровень» — это уровень навигации, а не ступень обучения.
    # Ступени разбираются отдельно, по сочетаниям — см. STEP_PHRASES.
    "респондент": "собеседник", "респондента": "собеседника", "респонденту": "собеседнику",
    "респонденте": "собеседнике", "респондентом": "собеседником", "респонденты": "собеседники",
    "респондентов": "собеседников", "респондентам": "собеседникам",
    # второе лицо: настоящее время
    "научишься": "научитесь", "хочешь": "хотите", "можешь": "можете", "сможешь": "сможете",
    "будешь": "будете", "попробуешь": "попробуете", "проверяешь": "проверяете",
    "помогаешь": "помогаете", "пишешь": "пишете", "объясняешь": "объясняете",
    "разбираешь": "разбираете", "наблюдаешь": "наблюдаете", "разберёшь": "разберёте",
    "просишь": "просите", "изучаешь": "изучаете", "ищешь": "ищете",
    "формулируешь": "формулируете", "выбираешь": "выбираете", "выясняешь": "выясняете",
    "уточняешь": "уточняете", "предлагаешь": "предлагаете", "получаешь": "получаете",
    "записываешь": "записываете", "используешь": "используете", "работаешь": "работаете",
    "предполагаешь": "предполагаете", "решаешь": "решаете", "помнишь": "помните",
    "сохраняешь": "сохраняете", "отвечаешь": "отвечаете", "проводишь": "проводите",
    "предложишь": "предложите", "переводишь": "переводите", "включишь": "включите",
    "выполнишь": "выполните", "услышишь": "услышите", "идёшь": "идёте", "знаешь": "знаете",
    "делаешь": "делаете", "видишь": "видите", "берёшь": "берёте", "найдёшь": "найдёте",
    "получишь": "получите", "собираешь": "собираете", "пользуешься": "пользуетесь",
    "останавливаешься": "останавливаетесь", "обращаешься": "обращаетесь",
    "собираешься": "собираетесь", "подготовишься": "подготовитесь",
    "сам": "сами", "сама": "сами",
    # второе лицо: повелительное наклонение
    "проведи": "проведите", "сгруппируй": "сгруппируйте", "прогони": "прогоните",
    "разложи": "разложите", "собери": "соберите", "попробуй": "попробуйте",
    "прочитай": "прочитайте", "зафиксируй": "зафиксируйте", "отличи": "отличите",
    "решай": "решайте", "подставь": "подставьте", "замени": "замените", "сравни": "сравните",
    "разбей": "разбейте", "пройди": "пройдите", "выпиши": "выпишите",
    "раскладывай": "раскладывайте", "дай": "дайте", "отбери": "отберите",
    "определи": "определите", "заполни": "заполните", "сформулируй": "сформулируйте",
    "найди": "найдите", "допиши": "допишите", "отметь": "отметьте", "поправь": "поправьте",
    "запиши": "запишите", "послушай": "послушайте", "подставляй": "подставляйте",
    "выбери": "выберите", "напиши": "напишите", "сведи": "сведите",
    "оттрассируй": "оттрассируйте", "внеси": "внесите", "сохраняй": "сохраняйте",
    "держи": "держите", "расспроси": "расспросите", "спроси": "спросите",
    "смотри": "смотрите", "начни": "начните", "нажми": "нажмите", "открой": "откройте",
    "читай": "читайте", "бери": "берите", "проверь": "проверьте", "свяжи": "свяжите",
    "разбери": "разберите", "заходи": "заходите", "жми": "жмите", "оставь": "оставьте",
    "предложи": "предложите", "пришли": "пришлите", "расскажи": "расскажите",
    "посмотри": "посмотрите",
    "уточни": "уточните", "объясни": "объясните", "покажи": "покажите",
    "попроси": "попросите", "укажи": "укажите", "обсуди": "обсудите",
    "добавь": "добавьте", "опиши": "опишите", "сохрани": "сохраните",
    "используй": "используйте", "учитывай": "учитывайте", "возьми": "возьмите",
    "отмечай": "отмечайте", "подготовь": "подготовьте", "выясни": "выясните",
    "выбирай": "выбирайте", "пригласи": "пригласите", "договорись": "договоритесь",
    "адаптируй": "адаптируйте", "вернись": "вернитесь", "узнай": "узнайте",
    "оставляй": "оставляйте", "отделяй": "отделяйте", "проверяй": "проверяйте",
    "записывай": "записывайте", "отдели": "отделите", "сопоставь": "сопоставьте",
    "раздели": "разделите", "согласуй": "согласуйте", "посчитай": "посчитайте",
    "нажимай": "нажимайте", "прими": "примите", "задавай": "задавайте",
    "слушай": "слушайте", "торопись": "торопитесь", "обрати": "обратите",
    "переслушай": "переслушайте", "спеши": "спешите", "приготовь": "приготовьте",
    "сверься": "сверьтесь", "загляни": "загляните", "перечитай": "перечитайте",
    "уменьши": "уменьшите", "убери": "уберите", "поставь": "поставьте",
    "исправь": "исправьте", "покрути": "покрутите", "измерь": "измерьте",
}

# Названия книг и цитаты, которые словарь принял бы за обращение: «Спроси маму» —
# это название, а не повелительное наклонение. Такие места защищаются до перевода.
PROTECT = [
    "Спроси маму",
]

# Ссылки на карточки каталога: в присланном файле их нет, а на сайте книга должна вести
# на свою карточку с ценой и доступом из РФ (D156). Ключ — как книга названа в тексте.
CATALOG = {
    "«Спроси маму»": "/resource/sprosi-mamu/",
    "«Как создать продукт, который купят»": "/resource/lean-customer-development/",
    "«Practical Empathy»": "/resource/practical-empathy/",
    "«Just Enough Research»": "/resource/just-enough-research/",
    "«Continuous Discovery Habits»": "/resource/continuous-discovery-habits/",
    "«Интервью по пользовательскому опыту»": "/resource/interviewing-users/",
    "Nielsen Norman Group": "/resource/nngroup-articles/",
}


def tidy_markup(text: str, notes: list) -> str:
    """Мелкие правки разметки, которых требует сайт, а не присланная страница."""
    # Заголовок колонки без scope чтец не связывает со столбцом (правило аудита 16.09.2026).
    text, n = re.subn(r"<th(?![^>]*scope=)(?![a-z])", '<th scope="col"', text)

    if n:
        notes.append("scope у заголовков таблиц: " + str(n))

    # Жирная строка в начале блока целей — это заголовок блока, а не просто жирный текст.
    # Без своего тега WordPress оборачивает её абзацем и ломает вложенность.
    text, n = re.subn(
        r'(<div class="ds-lesson__goals">\s*)<b>(.*?)</b>',
        lambda m: m.group(1) + '<p class="ds-lesson__goals-title">' + m.group(2) + "</p>",
        text,
        flags=re.S,
    )

    if n:
        notes.append("заголовок блока целей: " + str(n))

    return text


def fix_headings(text: str, fixed: list) -> str:
    """Убирает пропуски уровней заголовков: после h2 идёт h3, а не h4.

    Пропуск рвёт структуру страницы для экранного чтеца и поисковика — правило
    этапа 15. В присланных файлах внутри образцов документов встречаются h4 и h5
    прямо под h2: относительная вложенность сохраняется, абсолютный уровень падает.
    """
    previous = 2
    out = []
    last = 0

    for found in re.finditer(r"<(/?)h([1-6])", text):
        closing, level = found.group(1), int(found.group(2))

        if closing:
            continue

        want = min(level, previous + 1)

        if want != level:
            fixed.append("h{0} → h{1}".format(level, want))
            # Закрывающий тег того же заголовка меняется вместе с открывающим.
            close = text.find("</h{0}>".format(level), found.end())
            out.append(text[last:found.start()] + "<h{0}".format(want))
            out.append(text[found.end():close] + "</h{0}>".format(want))
            last = close + 5
        previous = want

    out.append(text[last:])

    return "".join(out)


def link_catalog(text: str, linked: list) -> str:
    """Ставит ссылку на карточку там, где книга названа в тексте."""
    for name, url in CATALOG.items():
        # Только первое упоминание и только вне уже существующей ссылки.
        pattern = re.compile(r"(?<!>)" + re.escape(name) + r"(?![^<]*</a>)")
        found = pattern.search(text)

        if not found:
            continue

        text = text[: found.start()] + '<a href="' + url + '">' + name + "</a>" + text[found.end():]
        linked.append(name)

    return text


# «Уровень» в значении ступени обучения — только в этих сочетаниях. Всё остальное
# («верхний уровень» в структуре сайта) остаётся как написано и попадает в отчёт.
STEP_PHRASES = {
    "этом уровне": "этой ступени", "этого уровня": "этой ступени",
    "этому уровню": "этой ступени", "этот уровень": "эта ступень",
    "этим уровнем": "этой ступенью", "прошлом уровне": "прошлой ступени",
    "прошлого уровня": "прошлой ступени", "прошлым уровнем": "прошлой ступенью",
    "предыдущего уровня": "предыдущей ступени", "предыдущих уровнях": "предыдущих ступенях",
    "следующего уровня": "следующей ступени", "следующие уровни": "следующие ступени",
    "следующим уровням": "следующим ступеням", "ошибки уровня": "ошибки ступени",
    "ловушки уровня": "ловушки ступени", "ловушка уровня": "ловушка ступени",
    "ловушку уровня": "ловушку ступени", "граница уровней": "граница ступеней",
    "границы уровней": "границы ступеней", "критерий уровня": "критерий ступени",
    "сердце уровня": "сердце ступени", "три уровня": "три ступени",
    "навык уровня": "навык ступени", "раздел уровня": "раздел ступени",
    "чек-лист уровня": "чек-лист ступени", "про уровни": "про ступени",
    "уровне junior": "ступени Junior", "уровне middle": "ступени Middle",
    "уровне senior": "ступени Senior", "уровень junior": "ступень Junior",
    "уровень middle": "ступень Middle", "уровень senior": "ступень Senior",
    "уровня junior": "ступени Junior", "уровня middle": "ступени Middle",
    "уровня senior": "ступени Senior",
}

# Прошедшее время с чередованием: «вёл» во множественном — «вели», а не «вёли».
PAST_ODD = {
    "вёл": "вели", "шёл": "шли", "нашёл": "нашли", "провёл": "провели",
    "привёл": "привели", "пришёл": "пришли", "подошёл": "подошли",
    "нёс": "несли", "принёс": "принесли", "мог": "могли", "смог": "смогли",
}

# Общее правило «+и» даёт «вёли» и «шёли» — чередование чинится после него.
PAST_AFTER = {"вёли": "вели", "шёли": "шли", "нёсли": "несли", "моги": "могли"}


def steps_and_odd(text: str, notes: list) -> str:
    """Сочетания про ступень и неправильное прошедшее время."""
    for phrase, repl in STEP_PHRASES.items():
        pattern = re.compile(r"(?<![А-Яа-яЁё])" + re.escape(phrase) + r"(?![А-Яа-яЁё])", re.I)
        text, n = pattern.subn(lambda m: same_case(m.group(0), repl), text)

        if n:
            notes.append(phrase + " → " + repl)

    return text


# Форма на -шь, которой нет в словаре: правило работает для подавляющего большинства
# глаголов, но каждое такое слово всё равно попадает в отчёт — их читают глазами.
SKIP_SH = {"лишь", "вишь", "бишь"}


def by_rule(word: str):
    """Догадка для формы второго лица, которой нет в словаре.

    Правило простое и потому надёжное: окончание «шь» меняется на «те»,
    «шься» — на «тесь». Читаешь → читаете, научишься → научитесь.
    Неправильные глаголы (хочешь → хотите) живут в словаре выше.
    """
    low = word.lower()

    if low in SKIP_SH:
        return None

    if low.endswith("шься"):
        return low[:-4] + "тесь"

    if low.endswith("шь"):
        return low[:-2] + "те"

    return None


def same_case(source: str, target: str) -> str:
    return target.capitalize() if source[:1].isupper() else target


def drop_block(text: str, klass: str) -> str:
    """Убирает элемент с этим классом целиком, считая вложенность тегов."""
    pattern = re.compile(r'<(\w+)[^>]*\bclass="[^"]*\b' + re.escape(klass) + r'\b[^"]*"[^>]*>')

    while True:
        found = pattern.search(text)

        if not found:
            return text

        tag = found.group(1)
        depth = 0
        stop = None

        for step in re.finditer(r"</?" + tag + r"\b[^>]*>", text[found.start():], re.I):
            depth += -1 if step.group(0).startswith("</") else 1

            if depth == 0:
                stop = found.start() + step.end()
                break

        if stop is None:
            return text

        text = text[: found.start()] + text[stop:]


def strip_page(source: str) -> str:
    """Оставляет содержимое урока без обвязки страницы."""
    body = re.search(r"<body[^>]*>(.*)</body>", source, re.S)
    text = body.group(1) if body else source
    text = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", text, flags=re.S)

    for name in DROP_BLOCKS:
        text = drop_block(text, name)

    return text


def head_of(source: str) -> dict:
    """Название и анонс записи: в присланной странице это H1 и лид."""
    def plain(chunk: str) -> str:
        return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", chunk))).strip()

    title = re.search(r"<h1[^>]*>(.*?)</h1>", source, re.S)
    lede = re.search(r'<p class="lede"[^>]*>(.*?)</p>', source, re.S)

    return {
        "title": plain(title.group(1)) if title else "",
        "excerpt": plain(lede.group(1)) if lede else "",
    }


def map_classes(text: str, unknown: set) -> str:
    """Переводит классы по таблице, неизвестные оставляет и складывает в отчёт."""

    def one(found):
        out = []

        for name in found.group(1).split():
            if name in CLASS_MAP:
                if CLASS_MAP[name]:
                    out.append(CLASS_MAP[name])
            else:
                if not name.startswith("ds-"):
                    unknown.add(name)
                out.append(name)

        return 'class="' + " ".join(out) + '"' if out else ""

    # Пробел перед атрибутом съедается вместе с ним: иначе остаётся «<div >».
    return re.sub(r'\s*class="([^"]+)"', lambda m: (" " + one(m)) if one(m) else "", text)


# После «вы» глагол прошедшего времени идёт во множественном числе: «вы работали»,
# а не «вы работал». Однородные сказуемые тянутся следом: «вы готовили и проводили».
PAST = r"[а-яё]+(?:ал|ял|ил|ел|ул|ыл|ёл)"
# Между «вы» и глаголом может стоять отрицание или наречие: «вы не спросили», «вы уже провели».
PAST_AFTER_VY = re.compile(
    r"((?<![А-Яа-яЁё])[Вв]ы\s+(?:(?:не|уже|ещё|только|сами|тогда|там|потом)\s+)?)(" + PAST + r")(?![а-яё])"
)
PAST_CHAIN = re.compile(
    r"(ли(?:сь)?[^.!?;:]{0,70}?(?:,\s+|\s+и\s+|\s+а\s+|\s+но\s+))(" + PAST + r")(?![а-яё])"
)


def past_plural(text: str) -> str:
    for odd, repl in PAST_ODD.items():
        text = re.sub(
            r"((?<![А-Яа-яЁё])(?:[Вв]ы|ли)\s+(?:[а-яё]+\s+){0,3}?)" + odd + r"(?![а-яё])",
            lambda m, r=repl: m.group(1) + r,
            text,
        )

    text = PAST_AFTER_VY.sub(lambda m: m.group(1) + m.group(2) + "и", text)

    # Второй и третий глагол в ряду: правило крутится, пока цепочка не кончится.
    while True:
        after = PAST_CHAIN.sub(lambda m: m.group(1) + m.group(2) + "и", text)

        if after == text:
            break

        text = after

    # Общее правило «+и» даёт «вёли» вместо «вели»: чередование чинится следом.
    for wrong, right in PAST_AFTER.items():
        text = re.sub(
            r"(?<![А-Яа-яЁё])" + wrong + r"(?![а-яё])",
            lambda m, r=right: same_case(m.group(0), r),
            text,
            flags=re.I,
        )

    return text


def to_vy(text: str, changes: list, guessed: set) -> str:
    """Переводит обращение на «вы» в тексте, не трогая теги, атрибуты и названия."""
    for n, phrase in enumerate(PROTECT):
        text = text.replace(phrase, "@@keep" + str(n) + "@@")

    known = {}
    known.update(PRONOUNS)
    known.update(WORDS)
    word_re = re.compile(r"(?<![А-Яа-яЁё-])([А-Яа-яЁё]+)(?![А-Яа-яЁё-])")

    def swap(found):
        raw = found.group(1)
        low = raw.lower()

        if low in known:
            return same_case(raw, known[low])

        guess = by_rule(raw)

        if guess:
            guessed.add(low + " → " + guess)
            return same_case(raw, guess)

        return raw

    def fix(chunk: str) -> str:
        after = past_plural(word_re.sub(swap, chunk))

        if after != chunk and chunk.strip():
            changes.append((chunk.strip()[:170], after.strip()[:170]))

        return after

    out = "".join(
        part if part.startswith("<") else fix(part)
        for part in re.split(r"(<[^>]+>)", text)
    )

    for n, phrase in enumerate(PROTECT):
        out = out.replace("@@keep" + str(n) + "@@", phrase)

    return out


def quiz_data(source: str) -> list:
    """Достаёт вопросы тренажёра из её скрипта: в разметке лежит пустая коробка."""
    block = re.search(r"var\s+QS\s*=\s*\[(.*?)\];", source, re.S)

    if not block:
        return []

    out = []

    for item in re.finditer(r"\{(.*?)\}", block.group(1), re.S):
        chunk = item.group(1)
        text = re.search(r"t:\s*'((?:[^'\\]|\\.)*)'", chunk)
        good = re.search(r"good:\s*(true|false)", chunk)
        back = re.search(r"fb:\s*'((?:[^'\\]|\\.)*)'", chunk)

        if not text or not good:
            continue

        out.append(
            {
                "text": text.group(1).replace("\\'", "'"),
                "good": good.group(1) == "true",
                "feedback": back.group(1).replace("\\'", "'") if back else "",
            }
        )

    return out


def quiz_labels(source: str) -> tuple:
    """Подписи кнопок: они же слова вердикта в разборе."""
    good = re.search(r'id="btnGood"[^>]*>(.*?)<', source, re.S)
    bad = re.search(r'id="btnBad"[^>]*>(.*?)<', source, re.S)

    return (
        html.unescape(good.group(1)).strip() if good else "Годится",
        html.unescape(bad.group(1)).strip() if bad else "Переделать",
    )


def quiz_markup(items: list, options: list, title: str = "Тренажёр") -> str:
    """Тренажёр разметкой, а не данными в скрипте: без JS вопросы видны списком.

    Вариантов ответа бывает от двух до пяти, поэтому ключ ответа — строка, а не
    «верно / неверно»: в разных уроках это «годится / переделать», «низкая / средняя
    / высокая» и так далее.
    """
    rows = []
    labels = {one["key"]: one["label"] for one in options}

    for one in items:
        rows.append(
            '<li data-quiz-q data-answer="{key}"><p class="ds-quiz__question">{text}</p>'
            '<p class="ds-quiz__feedback" data-quiz-feedback><b>{word}</b>{back}</p></li>'.format(
                key=html.escape(one["answer"], quote=True),
                text=one["text"],
                word=labels.get(one["answer"], "Разбор"),
                back=one["feedback"],
            )
        )

    buttons = "".join(
        '<button class="ds-quiz__option" type="button" data-quiz-answer="{key}">{label}</button>'.format(
            key=html.escape(one["key"], quote=True), label=one["label"]
        )
        for one in options
    )

    head = (
        '<div class="ds-lesson__box ds-quiz" data-quiz>\n'
        '<div class="ds-lesson__box-head">'
        + title
        + " · вопрос <span data-quiz-idx>1</span> из "
        + str(len(items))
        + '<span class="ds-lesson__spacer"></span><span data-quiz-score>0 верно</span></div>\n'
    )
    body = (
        '<div class="ds-lesson__box-body">\n<ol class="ds-quiz__list">\n'
        + "\n".join(rows)
        + '\n</ol>\n<div class="ds-quiz__actions" data-quiz-actions hidden>'
        + buttons
        + "</div>\n"
        '<div class="ds-quiz__bar"><span class="ds-quiz__track"><i data-quiz-fill></i></span>'
        '<button class="ds-button ds-button--secondary ds-button--sm" type="button" data-quiz-next hidden>'
        "Дальше</button></div>\n</div>\n</div>"
    )

    return head + body


def js_arrays(js: str, start: int) -> list:
    """Два первых массива в аргументах вызова, со счётом скобок.

    Поиском по регулярке их не взять: внутри текста вопросов встречаются и скобки,
    и апострофы, а у вызова есть четвёртый аргумент — функция разбора.
    """
    out = []
    depth = 0
    begin = None
    quote = None
    i = start

    while i < len(js) and len(out) < 2:
        char = js[i]

        if quote:
            if char == "\\":
                i += 2
                continue
            if char == quote:
                quote = None
        elif char in "'\"":
            quote = char
        elif char == "[":
            depth += 1
            if depth == 1:
                begin = i + 1
        elif char == "]":
            depth -= 1
            if depth == 0 and begin is not None:
                out.append(js[begin:i])
                begin = None
        elif char == ")" and depth == 0:
            break

        i += 1

    return out


def drills_of(source: str) -> list:
    """Тренажёры, собранные вызовом makeDrill('#id', [варианты], [вопросы], …)."""
    js = "\n".join(m.group(1) for m in re.finditer(r"<script[^>]*>(.*?)</script>", source, re.S))
    out = []
    opt_re = re.compile(r"key:\s*'([^']*)'\s*,\s*label:\s*'((?:[^'\\]|\\.)*)'")
    text_re = re.compile(r"t:\s*'((?:[^'\\]|\\.)*)'")
    answer_re = re.compile(r"a:\s*'([^']*)'")
    back_re = re.compile(r"fb:\s*'((?:[^'\\]|\\.)*)'")

    def unquote(value: str) -> str:
        return value.replace("\\'", "'").replace('\\"', '"')

    for call in re.finditer(r"makeDrill\(\s*'#(\w+)'\s*,", js):
        arrays = js_arrays(js, call.end())

        if len(arrays) < 2:
            continue

        options = [
            {"key": m.group(1), "label": unquote(m.group(2))} for m in opt_re.finditer(arrays[0])
        ]
        items = []

        for one in re.finditer(r"\{(.*?)\}", arrays[1], re.S):
            chunk = one.group(1)
            text = text_re.search(chunk)
            answer = answer_re.search(chunk)
            back = back_re.search(chunk)

            if not text or not answer:
                continue

            items.append(
                {
                    "text": unquote(text.group(1)),
                    "answer": answer.group(1),
                    "feedback": unquote(back.group(1)) if back else "",
                }
            )

        if options and items:
            out.append({"node": call.group(1), "options": options, "items": items})

    return out


def put_quiz(text: str, markup: str, node: str = "quiz"):
    """Меняет её пустую коробку тренажёра на нашу разметку. Возвращает текст и успех."""
    box = re.search(r'<div[^>]*\bid="' + re.escape(node) + r'"[^>]*>', text)

    if not box or not markup:
        return text, False

    depth = 0
    stop = None

    for step in re.finditer(r"</?div\b[^>]*>", text[box.start():], re.I):
        depth += -1 if step.group(0).startswith("</") else 1

        if depth == 0:
            stop = box.start() + step.end()
            break

    if stop is None:
        return text, False

    return text[: box.start()] + markup + text[stop:], True


parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("--out", help="куда положить тело; без него только отчёт")
args = parser.parse_args()

path = pathlib.Path(args.source)
raw = path.read_text(encoding="utf-8")

head = head_of(raw)
head_changes = []
head_guessed = set()
head = {k: to_vy(steps_and_odd(v, []), head_changes, head_guessed) for k, v in head.items()}
items = quiz_data(raw)
unknown = set()
changes = []
guessed = set()

body = strip_page(raw)

# Тренажёр в уроках собран двумя способами: массивом QS (первая тема) и вызовами
# makeDrill (все остальные). Оба разворачиваются в одну и ту же нашу разметку.
quizzes = 0
yes, no = quiz_labels(raw)
pairs = [{"key": "1", "label": yes}, {"key": "0", "label": no}]
keyed = [
    {"text": one["text"], "answer": "1" if one["good"] else "0", "feedback": one["feedback"]}
    for one in items
]

body, quiz_ok = put_quiz(body, quiz_markup(keyed, pairs) if keyed else "", "quiz")
quizzes += 1 if quiz_ok else 0

for drill in drills_of(raw):
    body, ok = put_quiz(
        body, quiz_markup(drill["items"], drill["options"]), drill["node"]
    )
    quizzes += 1 if ok else 0

body = map_classes(body, unknown)
steps = []
body = steps_and_odd(body, steps)
body = to_vy(body, changes, guessed)

notes = []
body = tidy_markup(body, notes)

fixed = []
body = fix_headings(body, fixed)

linked = []
body = link_catalog(body, linked)
body = re.sub(r"\n{3,}", "\n\n", body).strip()
# Блок `wp:html` обязателен: без него WordPress прогоняет содержимое через wpautop,
# сам расставляет абзацы вокруг строчных элементов и рвёт вложенность — валидатор
# ловит это как «лишний </p>». Проверено прогоном 17.09.2026.
body = '<!-- wp:html -->\n<div class="ds-lesson">\n' + body + "\n</div>\n<!-- /wp:html -->"

print("название:", head["title"])
print("анонс:", head["excerpt"][:160])
print("тело:", len(body), "байт")
print("тренажёров развёрнуто в разметку:", quizzes)
print("строк с «ты» → «вы»:", len(changes))
print("форм переведено по правилу, не по словарю:", len(guessed))
if guessed:
    print(" ", "; ".join(sorted(guessed)))
print("ступень вместо уровня:", len(steps), "; ".join(steps) if steps else "нет")
print("правки разметки:", "; ".join(notes) if notes else "нет")
print("пропусков уровня заголовка поправлено:", len(fixed), ", ".join(fixed) if fixed else "")
print("ссылок на каталог поставлено:", len(linked), ", ".join(linked) if linked else "")
print("классов без нашей пары:", len(unknown), " ".join(sorted(unknown)) if unknown else "")

if changes:
    print("\n--- обращение: что изменилось ---")
    for was, now in changes:
        print("  −", was)
        print("  +", now)

if args.out:
    out = pathlib.Path(args.out)
    out.write_text(body, encoding="utf-8", newline="")
    out.with_suffix(".json").write_text(
        json.dumps(head, ensure_ascii=False, indent=1), encoding="utf-8", newline=""
    )
    print("\nзаписано:", out.name, "и", out.with_suffix(".json").name)
