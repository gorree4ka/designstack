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
    # словарь сайта (docs/VOICE.md)
    "уровень": "ступень", "уровня": "ступени", "уровню": "ступени", "уровне": "ступени",
    "уровнем": "ступенью", "уровни": "ступени", "уровней": "ступеней", "уровням": "ступеням",
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
    text = PAST_AFTER_VY.sub(lambda m: m.group(1) + m.group(2) + "и", text)

    # Второй и третий глагол в ряду: правило крутится, пока цепочка не кончится.
    while True:
        after = PAST_CHAIN.sub(lambda m: m.group(1) + m.group(2) + "и", text)

        if after == text:
            return text

        text = after


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


def quiz_markup(items: list, labels: tuple) -> str:
    """Тренажёр разметкой, а не данными в скрипте: без JS вопросы видны списком."""
    yes, no = labels
    rows = []

    for one in items:
        rows.append(
            '<li data-quiz-q data-good="{good}"><p class="ds-quiz__question">{text}</p>'
            '<p class="ds-quiz__feedback" data-quiz-feedback><b>{word}</b>{back}</p></li>'.format(
                good="1" if one["good"] else "0",
                text=one["text"],
                word=yes if one["good"] else no,
                back=one["feedback"],
            )
        )

    return (
        '<div class="ds-lesson__box ds-quiz" data-quiz>\n'
        '<div class="ds-lesson__box-head">Тренажёр · вопрос <span data-quiz-idx>1</span> из '
        + str(len(items))
        + '<span class="ds-lesson__spacer"></span><span data-quiz-score>0 верно</span></div>\n'
        '<div class="ds-lesson__box-body">\n<ol class="ds-quiz__list">\n'
        + "\n".join(rows)
        + '\n</ol>\n<div class="ds-quiz__actions" data-quiz-actions hidden>'
        '<button class="ds-quiz__option" type="button" data-quiz-answer="1">' + yes + "</button>"
        '<button class="ds-quiz__option" type="button" data-quiz-answer="0">' + no + "</button></div>\n"
        '<div class="ds-quiz__bar"><span class="ds-quiz__track"><i data-quiz-fill></i></span>'
        '<button class="ds-button ds-button--secondary ds-button--sm" type="button" data-quiz-next hidden>'
        "Дальше</button></div>\n</div>\n</div>"
    )


def put_quiz(text: str, markup: str) -> bool:
    """Меняет её пустую коробку тренажёра на нашу разметку. Возвращает, получилось ли."""
    box = re.search(r'<div class="[^"]*" id="quiz">', text) or re.search(r'<div id="quiz"[^>]*>', text)

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
head = {k: to_vy(v, head_changes, head_guessed) for k, v in head.items()}
items = quiz_data(raw)
unknown = set()
changes = []
guessed = set()

body = strip_page(raw)
body, quiz_ok = put_quiz(body, quiz_markup(items, quiz_labels(raw)) if items else "")
body = map_classes(body, unknown)
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
print("тренажёр:", f"{len(items)} вопросов развёрнуто в разметку" if quiz_ok else "нет или не подставился")
print("строк с «ты» → «вы»:", len(changes))
print("форм переведено по правилу, не по словарю:", len(guessed))
if guessed:
    print(" ", "; ".join(sorted(guessed)))
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
