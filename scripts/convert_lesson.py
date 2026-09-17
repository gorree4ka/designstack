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
    # компоненты темы «Анализ конкурентов»
    "atbl": "ds-lesson__table ds-lesson__table--wide",
    "hintrow": "is-hint",
    "dt": "ds-lesson__table-sub",
    "shots": "ds-lesson__screens",
    "shot": "ds-lesson__screen",
    "ph": "ds-lesson__shot-ph",
    "fn": "ds-lesson__shot-file",
    "desc": "ds-lesson__shot-desc",
    "qs": "ds-lesson__checks",
    "m": "ds-lesson__checks-mark",
    "yes": "is-yes",
    "cb-grid": "ds-lesson__build-grid",
    "rb-grid": "ds-lesson__build-grid",
    "cb-out": "ds-lesson__build-out",
    "rb-out": "ds-lesson__build-out",
    "cb-line": "ds-lesson__build-text ds-lesson__build-text--mono",
    "rb-text": "ds-lesson__build-text",
    "cb-note": "ds-lesson__build-note",
    "rb-note": "ds-lesson__build-note",
    "cb-miss": "ds-lesson__build-miss",
    "rb-miss": "ds-lesson__build-miss",
    "full": "ds-lesson__field--full",
    "three": "ds-lesson__three",
    "c": "ds-lesson__three-item",
    "tt": "",
    "dig": "ds-lesson__dig",
    "dig-step": "ds-lesson__dig-step",
    "lvl": "ds-lesson__tier-label",
    "dig-ask": "ds-lesson__dig-ask",
    "dig-actions": "ds-lesson__dig-actions",
    "dig-final": "ds-lesson__dig-final",
    "uicmp": "ds-lesson__screens",
    "uip": "ds-lesson__screen",
    "dlg": "ds-lesson__dlg",
    "toast": "ds-lesson__toast",
    "txt": "ds-lesson__toast-text",
    "undo": "ds-lesson__toast-undo",
    "restore": "ds-lesson__restore",
    "sub": "ds-quiz__sub",
    "pr": "ds-quiz__lead",
    "pcards": "ds-lesson__pcards",
    "pcard": "ds-lesson__pcard",
    "idx": "ds-lesson__pcard-idx",
    "hintline": "ds-lesson__pcard-hint",
    "body": "ds-lesson__pcard-body",
    "row": "ds-lesson__kv",
    "yn": "ds-lesson__yn",
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
    # компоненты темы «Юзабилити-тесты», ступени Junior и Middle
    "watch": "ds-lesson__watch",
    "time": "ds-lesson__watch-time",
    "log": "ds-lesson__log",
    "ev": "ds-lesson__ev",
    "verdictbox": "ds-lesson__result",
    "wh-fb": "ds-lesson__result",
    "wh-fix": "ds-lesson__note",
    "wh-meta": "ds-lesson__meta",
    "wh-text": "",
    "chk": "ds-lesson__checklist",
    "chkbar": "ds-lesson__checkbar",
    "hint": "ds-lesson__hint",
    "prog": "ds-quiz__track",
    "cards": "ds-lesson__cards",
    "card": "ds-lesson__card",
    "card-ask": "ds-lesson__card-ask",
    "tap": "",
    "hd": "ds-lesson__sheet-head",
    "tc": "ds-lesson__sheet-time",
    "quo": "ds-lesson__sheet-note",
    "sev": "ds-lesson__sev",
    "s3": "ds-lesson__sev--critical",
    "s2": "ds-lesson__sev--high",
    "s1": "ds-lesson__sev--low",
    "s0": "ds-lesson__sev--minor",
    "tl": "ds-lesson__timeline",
    "seg": "ds-lesson__seg",
    "core": "ds-lesson__seg--core",
    "mn": "ds-lesson__seg-time",
    "nm": "ds-lesson__seg-name",
    "ctr": "ds-lesson__ctr",
    "mx": "ds-lesson__mx",
    "hh": "ds-lesson__mx-head",
    "rh": "ds-lesson__mx-row",
    "cell": "ds-lesson__cell",
    "mx-out": "ds-lesson__mx-out",
    "mx-levels": "ds-lesson__mx-levels",
    "mx-rows": "ds-lesson__mx-rows",
    "w": "ds-lesson__word",
    "ch-q": "ds-lesson__pick-q",
    "ch-opts": "ds-lesson__pick-opts",
    "ch-opt": "ds-lesson__pick-opt",
    "ch-res": "ds-lesson__result",
    "ch-score": "ds-lesson__pick-score",
    "ch-side": "ds-lesson__pick-side",
    "pts": "ds-lesson__pick-pts",
    "lbl": "ds-lesson__pick-lbl",
    "screens": "ds-lesson__screens",
    "scr": "ds-lesson__screen",
    "ui": "ds-lesson__ui",
    "ui-top": "ds-lesson__ui-top",
    "back": "ds-lesson__ui-back",
    "ttl": "ds-lesson__ui-title",
    "dots": "ds-lesson__ui-dots",
    "ui-card": "ds-lesson__ui-card",
    "ui-row": "ds-lesson__ui-row",
    "ui-h": "ds-lesson__ui-h",
    "ui-status": "ds-lesson__ui-status",
    "ui-btn": "ds-lesson__ui-btn",
    "pri": "ds-lesson__ui-btn--pri",
    "ui-note": "ds-lesson__ui-note",
    "pin": "ds-lesson__pin",
    "pinlist": "ds-lesson__pinlist",
    "solid": "ds-button--primary",
    "danger": "ds-button--secondary",
    "good": "is-good",
    "bad": "is-bad",
    "sel": "is-selected",
    "picked": "is-picked",
    "missed": "is-missed",
    "wrongpick": "is-extra",
    "stem": "ds-quiz__question",
    "say": "ds-lesson__say",
    "calc-case": "ds-lesson__calc-case",
    "wk-test": "ds-lesson__week--test",
    "q": "",
}


# Короткие имена вроде `st`, `b`, `sec`, `cap` в разных уроках значат разное: в одном
# `st` — ступень лесенки, в другом — подпись под чек-листом. Общая таблица тут врёт,
# поэтому у урока может быть своя поправка. Ключ — имя присланного файла без расширения.
LESSON_MAP = {
    "usability-testing-junior": {
        "st": "ds-lesson__checkbar-state",
        "btn": "ds-button ds-button--secondary ds-button--sm",
    },
    "competitor-analysis-junior": {
        "cap": "ds-lesson__screen-cap",
        "btn": "ds-button ds-button--secondary ds-button--sm",
    },
    "competitor-analysis-middle": {
        "cap": "ds-lesson__screen-cap",
        "a": "",
        "b": "is-good",
        "btn": "ds-button ds-button--secondary ds-button--sm",
    },
    "competitor-analysis-senior": {
        "ttl": "ds-lesson__pcard-title",
        "y": "ds-lesson__yn-yes",
        "n": "ds-lesson__yn-no",
        "btn": "ds-button ds-button--secondary ds-button--sm",
    },
    "usability-testing-middle": {
        "b": "ds-lesson__pin-num",
        "sec": "ds-lesson__ui-btn--sec",
        "link": "ds-lesson__ui-btn--link",
        "cap": "ds-lesson__screen-cap",
        "btn": "ds-button ds-button--secondary ds-button--sm",
    },
}

# Опоры присланного скрипта: его `id` становятся нашими атрибутами. Скрипт сайта
# не должен знать чужих идентификаторов, а разметка — тянуть их за собой.
HOOKS = {
    "prepList": "data-checklist",
    "prepProg": "data-checklist-fill",
    "prepSt": "data-checklist-state",
    "panelScore": "data-panel-score",
    "cUsers": 'data-calc-field="users"',
    "cShare": 'data-calc-field="share"',
    "cUnit": 'data-calc-field="unit"',
    "cOutcome": 'data-calc-field="outcome"',
    "cShareVal": "data-calc-share-out",
    "cUnitLabel": "data-calc-label",
    "cOut": "data-calc-out",
    "cCap": "data-calc-cap",
    "cSay": "data-calc-say",
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
    # повелительное наклонение: прогон по шести урокам 17.09.2026 — «запусти», «понаблюдай»
    "включи": "включите", "выдавай": "выдавайте", "выясняй": "выясняйте", "говори": "говорите",
    "добавляй": "добавляйте", "дождись": "дождитесь", "заведи": "заведите", "заложи": "заложите",
    "заменяй": "заменяйте", "заполняй": "заполняйте", "запусти": "запустите",
    "зарезервируй": "зарезервируйте", "исправляй": "исправляйте", "ищи": "ищите",
    "наблюдай": "наблюдайте", "назначь": "назначьте", "назови": "назовите", "называй": "называйте",
    "обещай": "обещайте", "обобщай": "обобщайте", "обозначь": "обозначьте",
    "объедини": "объедините", "отдай": "отдайте", "откладывай": "откладывайте",
    "отличай": "отличайте", "оцени": "оцените", "передавай": "передавайте",
    "переноси": "переносите", "пересмотри": "пересмотрите", "переспрашивай": "переспрашивайте",
    "пиши": "пишите", "планируй": "планируйте", "повтори": "повторите", "повышай": "повышайте",
    "подсказывай": "подсказывайте", "подстрой": "подстройте", "подумай": "подумайте",
    "помогай": "помогайте", "помоги": "помогите", "пополняй": "пополняйте",
    "предполагай": "предполагайте", "представляй": "представляйте", "представь": "представьте",
    "предупреди": "предупредите", "предусмотри": "предусмотрите", "приведи": "приведите",
    "приглашай": "приглашайте", "признай": "признайте", "приписывай": "приписывайте",
    "продолжай": "продолжайте", "проси": "просите", "разберись": "разберитесь",
    "рассмотри": "рассмотрите", "сверь": "сверьте", "сделай": "сделайте", "следи": "следите",
    "собирай": "собирайте", "сопоставляй": "сопоставляйте", "составь": "составьте",
    "спланируй": "спланируйте", "ставь": "ставьте", "считай": "считайте", "требуй": "требуйте",
    "указывай": "указывайте", "уточняй": "уточняйте", "учти": "учтите", "фиксируй": "фиксируйте",
    "выдвигай": "выдвигайте", "делай": "делайте", "доработай": "доработайте",
    "досчитай": "досчитайте", "запланируй": "запланируйте", "защищай": "защищайте",
    "обоснуй": "обоснуйте", "обсуждай": "обсуждайте", "объясняй": "объясняйте",
    "ограничь": "ограничьте", "останавливай": "останавливайте", "остановись": "остановитесь",
    "переведи": "переведите", "перепиши": "перепишите", "пересматривай": "пересматривайте",
    "переходи": "переходите", "подожди": "подождите", "показывай": "показывайте",
    "получи": "получите", "понаблюдай": "понаблюдайте", "предлагай": "предлагайте",
    "придумывай": "придумывайте", "проследи": "проследите", "разбирай": "разбирайте",
    "скорректируй": "скорректируйте", "соблюдай": "соблюдайте", "создай": "создайте",
    "уложись": "уложитесь", "пытайся": "пытайтесь", "измени": "измените", "наполни": "наполните",
    "пометь": "пометьте", "выдели": "выделите",
    # тема «Анализ конкурентов»
    "выведи": "выведите", "нарисуй": "нарисуйте", "подписывай": "подписывайте",
    "полистай": "полистайте", "раскопай": "раскопайте", "снимай": "снимайте",
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

    # Обёртка таблицы листается вбок (`overflow-x: auto`), а значит обязана брать фокус
    # с клавиатуры: иначе колонки справа недоступны тому, кто работает без мыши.
    # Правило axe `scrollable-region-focusable`; на телефоне листается любая таблица,
    # поэтому атрибуты получают все обёртки, а не только заведомо широкая. Роль — `group`,
    # а не `region`: region — это ориентир страницы, и семь одинаково подписанных ориентиров
    # на один урок валидатор справедливо считает ошибкой (`unique-landmark`).
    text, n = re.subn(
        r'<div class="(ds-lesson__table[^"]*)"(?![^>]*tabindex)',
        r'<div class="\1" tabindex="0" role="group" aria-label="Таблица, листается вбок"',
        text,
    )

    if n:
        notes.append("таблиц с фокусом для прокрутки: " + str(n))

    # Подпись `aria-label` на обычном `div` запрещена: у него нет роли, и чтец
    # атрибут игнорирует, а валидатор считает ошибкой. Роль `group` подпись принимает.
    text, n = re.subn(
        r'<div (?![^>]*\brole=)([^>]*\baria-label=)', r'<div role="group" \1', text
    )

    if n:
        notes.append("роль group для подписанных блоков: " + str(n))

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

    Уровень считается от родителя, а не от предыдущего заголовка. Первая версия
    брала «предыдущий плюс один», и три соседние карточки с h5 получали h3, h4 и h5:
    формально без пропусков, по смыслу — три уровня вложенности у равных соседей.
    Найдено на уроке «Анализ конкурентов» 17.09.2026.
    """
    stack = []  # пары (уровень в присланном файле, уровень на сайте)
    out = []
    last = 0

    for found in re.finditer(r"<(/?)h([1-6])", text):
        closing, level = found.group(1), int(found.group(2))

        if closing:
            continue

        while stack and stack[-1][0] >= level:
            stack.pop()

        want = min(level, (stack[-1][1] if stack else 1) + 1)
        stack.append((level, want))

        if want != level:
            fixed.append("h{0} → h{1}".format(level, want))
            # Закрывающий тег того же заголовка меняется вместе с открывающим.
            close = text.find("</h{0}>".format(level), found.end())
            out.append(text[last:found.start()] + "<h{0}".format(want))
            out.append(text[found.end():close] + "</h{0}>".format(want))
            last = close + 5

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


def map_classes(text: str, unknown: set, lesson: str = "") -> str:
    """Переводит классы по таблице, неизвестные оставляет и складывает в отчёт."""
    table = dict(CLASS_MAP)
    table.update(LESSON_MAP.get(lesson, {}))

    def one(found):
        out = []

        for name in found.group(1).split():
            if name in table:
                if table[name]:
                    out.extend(table[name].split())
            else:
                if not name.startswith(("ds-", "is-")):
                    unknown.add(name)
                out.append(name)

        # «btn solid» — это основная кнопка, а не основная поверх второстепенной.
        if "ds-button--primary" in out and "ds-button--secondary" in out:
            out.remove("ds-button--secondary")

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


SELF_REPORT = []


# «Сам» принадлежит читателю не всегда: «решите сам» — обращение, а «участник нашёл
# решение сам» — про участника теста. Поэтому слово переводится, только если в том же
# предложении есть обращение: «вы», «ваш» или глагол второго лица на «-те». Каждый
# случай печатается в отчёт с предложением целиком — решение проверяется глазами.
SELF_RE = re.compile(r"(?<![А-Яа-яЁё-])([Сс]ам|[Сс]ама)(?![А-Яа-яЁё-])")
# Подлежащее третьего лица отменяет перевод: «найдёт ли человек корзину сам» —
# про человека, даже если в том же предложении есть обращение к читателю.
OTHER_RE = re.compile(
    r"(?<![А-Яа-яЁё-])(?:участник[а-яё]*|человек[а-яё]*|собеседник[а-яё]*|"
    r"пользовател[а-яё]+|он|она|они|ведущ[а-яё]+)(?![А-Яа-яЁё-])",
    re.I,
)
READER_RE = re.compile(
    r"(?<![А-Яа-яЁё-])(?:вы|вам|вас|вами|ваш[а-яё]*)(?![А-Яа-яЁё-])"
    r"|(?<![А-Яа-яЁё-])[а-яё]{3,}(?:йте|ите|ете)(?![а-яё])",
    re.I,
)


def self_word(text: str, report: list) -> str:
    """Переводит «сам» → «сами» только в предложении, обращённом к читателю."""
    out = []
    at = 0

    for found in SELF_RE.finditer(text):
        left = max(text.rfind(sign, 0, found.start()) for sign in ".!?;<>")
        right = min(
            (place for place in (text.find(sign, found.end()) for sign in ".!?;<>") if place >= 0),
            default=len(text),
        )
        around = text[left + 1:right].strip()
        reader = bool(READER_RE.search(around)) and not OTHER_RE.search(around)
        out.append(text[at:found.start()])
        out.append(("сами" if found.group(1)[0] in "Сс" and reader else found.group(1)))

        if reader:
            out[-1] = "Сами" if found.group(1)[0] == "С" else "сами"

        at = found.end()
        report.append(("сам → сами" if reader else "сам оставлено") + ": " + around[:110])

    out.append(text[at:])

    return "".join(out)


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

    out = self_word(out, SELF_REPORT)

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

    # Текст вопроса бывает собран сложением: `t: P1 + '<b>Спор:</b> …'`, где P1 — строковая
    # константа выше по скрипту. Пока разбор ждал только литерал, такой тренажёр
    # молча оставался пустой коробкой (урок «Анализ конкурентов», Senior).
    consts = dict(re.findall(r"var\s+([A-Z][A-Z0-9_]*)\s*=\s*'((?:[^'\\]|\\.)*)';", js))
    whole_re = re.compile(r"t:\s*(.*?),\s*a:\s*'", re.S)

    def text_of(chunk: str):
        found = whole_re.search(chunk)

        if not found:
            return None

        parts = re.findall(r"'((?:[^'\\]|\\.)*)'|\b([A-Z][A-Z0-9_]*)\b", found.group(1))

        return "".join(unquote(lit) if lit or not name else unquote(consts.get(name, "")) for lit, name in parts)

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
            text = text_of(chunk)
            answer = answer_re.search(chunk)
            back = back_re.search(chunk)

            if not text or not answer:
                continue

            items.append(
                {
                    "text": text,
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


# ---------------------------------------------------------------------------
# Живые куски урока, которых нет в других темах: секундомер молчания, разметка
# задания, подбор формата и учебная матрица. Данные для них лежат в присланном
# скрипте, а на сайте должны быть в разметке: страница обязана читаться и без JS,
# и попадать в поиск. Каждая функция срабатывает, только если в уроке есть её
# опора, и молча пропускает урок, где такого куска нет.
# ---------------------------------------------------------------------------


def js_string(expr: str) -> str:
    """Склеивает строковые литералы выражения в один текст.

    В присланном скрипте разбор собран сложением: `'<b>…</b>' + items[i].fb + '…'`.
    Подстановку секунд (` + s + `) заменяем местом, куда скрипт сайта впишет число.
    """
    expr = re.sub(r"'\s*\+\s*s\s*\+\s*'", "@@said@@", expr)
    parts = re.findall(r"'((?:[^'\\]|\\.)*)'", expr, re.S)
    text = "".join(parts).replace("\\'", "'").replace('\\"', '"').replace("\\n", " ")
    text = text.replace("@@said@@", '<span data-sim-said></span>')
    # Инлайновые стили из присланного файла ссылаются на чужие переменные.
    return re.sub(r'\s*style="[^"]*"', "", text)


def sim_markup(js: str, body: str, notes: list) -> str:
    """Секундомер молчания: лента событий сессии и разбор по времени подсказки."""
    events = re.findall(r"\{\s*at:\s*([\d.]+),\s*cls:\s*'(\w+)',\s*v:\s*'((?:[^'\\]|\\.)*)'", js)

    if not events or 'id="simLog"' not in body:
        return body

    rows = []

    for at, kind, text in events:
        text = text.replace("\\'", "'")
        rows.append(
            '<div class="ds-lesson__ev{mod}" data-sim-at="{at}">'
            '<span class="ds-lesson__ev-time">{sec} с</span>'
            "<span>{text}</span></div>".format(
                mod=" ds-lesson__ev--win" if kind == "win" else "",
                at=at,
                sec=int(float(at)),
                text=text,
            )
        )

    finish = re.search(r"function finish\(el, won\)\s*\{(.*?)\n    \}", js, re.S)

    if not finish:
        return body

    texts = [js_string(m.group(1)) for m in re.finditer(r"vb\.innerHTML\s*=\s*(.*?);", finish.group(1), re.S)]
    limits = ["win"] + re.findall(r"el\s*<\s*(\d+)", finish.group(1)) + ["end"]

    if len(texts) != len(limits):
        notes.append("симулятор: разборов {} на {} порогов — оставлен как есть".format(len(texts), len(limits)))

        return body

    verdicts = [
        '<div class="ds-lesson__result" data-sim-verdict="{key}"{hide}>{text}</div>'.format(
            key=key, hide="" if key == "win" else " hidden", text=text
        )
        for key, text in zip(limits, texts)
    ]

    win = events[-1][0]
    body = body.replace(
        '<div class="log" id="simLog"></div>',
        '<div class="log" data-sim-log>\n' + "\n".join(rows) + "\n</div>",
    )
    body = body.replace('<div class="verdictbox" id="simVerdict"></div>', "\n".join(verdicts))
    body = body.replace('<div class="watch">', '<div class="watch" data-sim data-sim-win="%s">' % win)
    body = body.replace('id="simTime"', "data-sim-time")
    # Кнопки рисует скрипт: без него они были бы мёртвыми (правило раздела 10).
    body = re.sub(
        r'<button[^>]*id="simStart"[^>]*>.*?</button>', '<span class="acts" data-sim-controls></span>', body, flags=re.S
    )
    body = re.sub(r'<button[^>]*id="simHelp"[^>]*>.*?</button>', "", body, flags=re.S)
    body = re.sub(
        r'<button[^>]*id="simReset"[^>]*>.*?</button>', '<span data-sim-actions></span>', body, flags=re.S
    )
    notes.append("симулятор молчания: событий " + str(len(rows)) + ", разборов " + str(len(verdicts)))

    return body


def marks_markup(js: str, body: str, notes: list) -> str:
    """Разметка задания: какие слова подсказывают участнику путь."""
    tokens = re.findall(r"\[\s*'((?:[^'\\]|\\.)*)'\s*,\s*([01])\s*\]", js)

    if not tokens or 'id="whHost"' not in body:
        return body

    out = []
    total = 0

    for text, flag in tokens:
        text = text.replace("\\'", "'")

        if re.fullmatch(r"[,.\s]+", text):
            out.append(text if text.strip() else " ")
            continue

        if flag == "1":
            total += 1

        out.append(
            '<span class="ds-lesson__word{mod}" data-word="{flag}">{text}</span>'.format(
                mod=" is-picked" if flag == "1" else "", flag=flag, text=text
            )
        )

    host = (
        '<div class="ds-lesson__marks" data-marks data-marks-total="{total}"><p>{text}</p></div>'.format(
            total=total, text=" ".join(out).replace(" ,", ",").replace(" .", ".")
        )
    )
    back = re.search(r"fbEl\.innerHTML\s*=\s*(.*?);\s*\n", js, re.S)

    if back:
        body = body.replace(
            '<div class="wh-fb" id="whFb"></div>',
            '<div class="wh-fb" data-marks-back>' + js_string(back.group(1)) + "</div>",
        )

    body = body.replace('<div id="whHost"></div>', host)
    body = body.replace('<div class="wh-meta" id="whMeta"></div>', '<div class="wh-meta" data-marks-meta></div>')
    body = re.sub(r'<button[^>]*id="whCheck"[^>]*>.*?</button>', '<span data-marks-actions></span>', body, flags=re.S)
    body = re.sub(r'<span[^>]*id="whCount"[^>]*>\s*</span>', "", body)
    notes.append("разметка задания: слов " + str(len(out)) + ", из них с подсказкой " + str(total))

    return body


def pick_markup(js: str, body: str, notes: list) -> str:
    """Подбор формата: четыре вопроса, два исхода и объяснение на ничью."""
    block = re.search(r"var QS = \[(.*?)\n    \];", js, re.S)

    if not block or 'id="chooser"' not in body:
        return body

    questions = []

    for one in re.finditer(r"\{\s*q:\s*'((?:[^'\\]|\\.)*)',\s*\n?\s*a:\s*\[(.*?)\]\s*\}", block.group(1), re.S):
        answers = re.findall(
            r"\{\s*t:\s*'((?:[^'\\]|\\.)*)',\s*s:\s*'(\w+)',\s*d:\s*'((?:[^'\\]|\\.)*)'\s*\}", one.group(2), re.S
        )

        if answers:
            questions.append((one.group(1).replace("\\'", "'"), answers))

    outcomes = re.search(r"var txt = tie(.*?);\s*\n", js, re.S)

    if not questions or not outcomes:
        return body

    # В тройном условии есть и служебные литералы — сравнение `winner === 'mod'`.
    # Исход — это связный текст, а не ключ в четыре буквы.
    texts = [
        js_string("'" + m + "'")
        for m in re.findall(r"'((?:[^'\\]|\\.)*)'", outcomes.group(1), re.S)
        if len(m) > 20
    ]
    rows = []

    for number, (question, answers) in enumerate(questions, 1):
        opts = "".join(
            '<span class="ds-lesson__pick-opt" data-pick-side="{side}"><b>{title}</b><span>{hint}</span></span>'.format(
                side=side, title=title.replace("\\'", "'"), hint=hint.replace("\\'", "'")
            )
            for title, side, hint in answers
        )
        rows.append(
            '<li data-pick-step="{n}"><p class="ds-lesson__pick-q">{q}</p>'
            '<div class="ds-lesson__pick-opts">{opts}</div></li>'.format(n=number, q=question, opts=opts)
        )

    keys = ["tie", "mod", "un"]
    names = re.findall(r"<h5>([^<]+)</h5>", js)
    result = "".join(
        '<div class="ds-lesson__result" data-pick-out="{key}"{name}>{text}</div>'.format(
            key=key,
            name=' data-pick-name="%s"' % html.escape(names[number - 1], quote=True)
            if key != "tie" and len(names) >= number
            else "",
            text=text,
        )
        for number, (key, text) in enumerate(zip(keys, texts))
    )
    markup = (
        '<div class="box-body" data-pick data-pick-total="{total}">'
        '<ol class="ds-lesson__pick-list">{rows}</ol>'
        '<div class="chkbar"><span class="prog"><i data-pick-fill></i></span>'
        '<span data-pick-step-of></span></div>{result}'
        '<span data-pick-actions></span></div>'
    ).format(total=len(questions), rows="".join(rows), result=result)

    body = re.sub(r'<div class="box-body" id="chooser">.*?\n    </div>', markup, body, flags=re.S)
    body = re.sub(r'<button[^>]*id="chReset"[^>]*>.*?</button>', "", body, flags=re.S)
    notes.append("подбор формата: вопросов " + str(len(questions)) + ", исходов " + str(len(texts)))

    return body


def matrix_markup(js: str, body: str, notes: list) -> str:
    """Учебная матрица важности: клетка, её уровень и пример строки."""
    rows = re.findall(r"\{\s*n:\s*'((?:[^'\\]|\\.)*)',\s*ex:\s*'((?:[^'\\]|\\.)*)'\s*\}", js, re.S)
    levels = re.findall(r"(s[0-3]):\s*\{\s*t:\s*'([^']*)',\s*d:\s*'((?:[^'\\]|\\.)*)'\s*\}", js, re.S)

    if not rows or not levels or 'id="mx"' not in body:
        return body

    names = {"s3": "critical", "s2": "high", "s1": "low", "s0": "minor"}
    legend = "".join(
        "<dt>{title}</dt><dd data-mx-level=\"{key}\">{text}</dd>".format(
            key=names[key], title=title, text=text.replace("\\'", "'")
        )
        for key, title, text in levels
    )
    examples = "".join(
        '<li data-mx-row="{n}"><b>{name}</b> — {example}</li>'.format(
            n=number, name=name.replace("\\'", "'"), example=example.replace("\\'", "'")
        )
        for number, (name, example) in enumerate(rows)
    )
    body = body.replace('<div class="mx" id="mx">', '<div class="mx" data-mx>')
    body = re.sub(r'data-i="(\d+)" data-f="(\d+)"', r'data-mx-row="\1" data-mx-count="\2"', body)
    body = re.sub(
        r'<div class="mx-out" id="mxOut">(.*?)</div>',
        lambda m: '<div class="mx-out" data-mx-out>' + m.group(1) + "</div>"
        + '<dl class="mx-levels" data-mx-levels>' + legend + "</dl>"
        + '<ul class="mx-rows" data-mx-rows>' + examples + "</ul>",
        body,
        flags=re.S,
    )
    notes.append("матрица важности: строк " + str(len(rows)) + ", уровней " + str(len(levels)))

    return body


def panel_markup(js: str, body: str, notes: list) -> str:
    """Разбор заявок: карточки людей, кнопки «звать / не звать» и объяснение."""
    people = re.findall(
        r"\{\s*n:\s*'([^']*)',\s*d:\s*'((?:[^'\\]|\\.)*)',\s*ok:\s*(true|false),\s*\n?\s*why:\s*'((?:[^'\\]|\\.)*)'",
        js,
        re.S,
    )

    if not people or 'id="panelList"' not in body:
        return body

    labels = re.findall(r"data-v=\"(\d)\" type=\"button\">([^<]+)</button>", js)
    yes = next((text for key, text in labels if key == "1"), "Звать")
    no = next((text for key, text in labels if key == "0"), "Не звать")
    rows = "".join(
        '<li data-panel-ok="{ok}"><span class="who"><b>{name}</b><span>{about}</span></span>'
        '<span class="acts" data-panel-acts></span>'
        '<span class="vd">{why}</span></li>'.format(
            ok="1" if ok == "true" else "0",
            name=name,
            about=about.replace("\\'", "'"),
            why=why.replace("\\'", "'"),
        )
        for name, about, ok, why in people
    )
    body = body.replace(
        '<ul class="panel" id="panelList"></ul>',
        '<ul class="panel" data-panel data-panel-yes="{yes}" data-panel-no="{no}" '
        'data-panel-total="{total}">{rows}</ul>'.format(yes=yes, no=no, total=len(people), rows=rows),
    )
    notes.append("разбор заявок: карточек " + str(len(people)))

    return body


def js_number(expr: str, minutes: int) -> float:
    """Считает коэффициент выражения вида `affected * (minutes / 60) * p * 0.5`."""
    plain = expr.replace("affected", "1").replace("minutes", str(minutes)).replace("p", "1")

    if not re.fullmatch(r"[\d\s().*/+-]+", plain):
        return 0.0

    return eval(plain, {"__builtins__": {}}, {})  # noqa: S307 — выражение уже проверено


def calc_markup(js: str, body: str, notes: list) -> str:
    """Прикидка объёма: три последствия, у каждого свои коэффициенты и тексты."""
    block = re.search(r"function calc\(\)\s*\{(.*?)\n    \}\n", js, re.S)

    if not block or 'id="cUsers"' not in body:
        return body

    defaults = dict(re.findall(r"(\w+):\s*(\d+)", re.search(r"var DEFAULTS = \{([^}]*)\}", js).group(1)))
    titles = dict(
        re.findall(r"(\w+):\s*'((?:[^'\\]|\\.)*)'", re.search(r"var LABELS = \{(.*?)\n    \};", js, re.S).group(1))
    )
    order = re.findall(r'<option value="(\w+)"', body)
    parts = re.split(r"\}\s*else(?:\s*if\s*\([^)]*\))?\s*\{", block.group(1))
    cases = []

    for key, chunk in zip(order, parts):
        minutes = re.search(r"var minutes = (\d+)", chunk)
        minutes = int(minutes.group(1)) if minutes else 0
        low = re.search(r"lo\s*=\s*([^;]+);", chunk)
        high = re.search(r"hi\s*=\s*([^;]+);", chunk)
        cap = re.search(r"cap\s*=\s*(.*?);\n", chunk, re.S)
        say = re.search(r"say\s*=\s*(.*?);\n", chunk, re.S)

        if not (low and high and cap and say):
            continue

        def text(found):
            out = found.group(1)
            out = re.sub(r"'\s*\+\s*fmt\((\w+)\)\s*\+\s*'", lambda m: "{" + m.group(1) + "}", out)
            out = re.sub(r"'\s*\+\s*minutes\s*\+\s*'", str(minutes), out)

            return js_string(out)

        cases.append(
            '<div class="ds-lesson__calc-case" data-calc-case="{key}" data-calc-low="{low}" '
            'data-calc-high="{high}" data-calc-unit="{unit}" data-calc-label="{label}" hidden>'
            '<p data-calc-cap-text>{cap}</p><p data-calc-say-text>{say}</p></div>'.format(
                key=key,
                low=round(js_number(low.group(1), minutes), 6),
                high=round(js_number(high.group(1), minutes), 6),
                unit=defaults.get(key, ""),
                label=html.escape(titles.get(key, ""), quote=True),
                cap=text(cap),
                say=text(say),
            )
        )

    if not cases:
        return body

    body = body.replace('<div class="out">', '<div class="out" data-calc>' + "".join(cases), 1)
    notes.append("прикидка объёма: последствий " + str(len(cases)))

    return body


def js_condition(expr: str) -> str:
    """Переводит условие из присланного скрипта в выражение Python.

    Нужно ровно для одного: разметить двенадцать недель в конструкторе ритма.
    Правило каждой раскладки записано у неё выражением (`w % 2 === 0 ? …`), и
    переписывать три таких правила руками — значит держать содержимое урока
    в двух местах. Переводим тернарный оператор, сравнения и союзы; ничего,
    кроме чисел, скобок, `w` и строковых литералов, к вычислению не допускаем.
    """
    expr = expr.strip()

    # Внешние скобки снимаем: иначе первый же `(` уводит глубину, и тернарный
    # оператор внутри них остаётся незамеченным.
    while expr.startswith("(") and expr.endswith(")"):
        depth = 0
        whole = True

        for i, char in enumerate(expr):
            depth += 1 if char == "(" else (-1 if char == ")" else 0)

            # Скобка закрылась не на конце — значит она обнимает не всё выражение,
            # а только его часть: `(a || b) ? x : y`.
            if depth == 0 and i < len(expr) - 1:
                whole = False
                break

        if not whole:
            break

        expr = expr[1:-1].strip()

    depth = 0
    ask = -1

    for i, char in enumerate(expr):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "?" and depth == 0:
            ask = i
            break

    if ask < 0:
        return expr.replace("===", "==").replace("!==", "!=").replace("||", " or ").replace("&&", " and ")

    depth = 0
    nested = 0
    colon = len(expr)

    for j in range(ask + 1, len(expr)):
        char = expr[j]

        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "?" and depth == 0:
            nested += 1
        elif char == ":" and depth == 0:
            if nested:
                nested -= 1
            else:
                colon = j
                break

    return "((%s) if (%s) else (%s))" % (
        js_condition(expr[ask + 1:colon]),
        js_condition(expr[:ask]),
        js_condition(expr[colon + 1:]),
    )


def cadence_markup(js: str, body: str, notes: list) -> str:
    """Конструктор ритма: три раскладки двенадцати недель и разбор каждой.

    Без скрипта видны все три плана подряд — это и есть содержание раздела.
    Со скриптом их переключают кнопки: поведение берёт готовый `data-switch`.
    """
    block = re.search(r"var MODES = \{(.*?)\n    \};", js, re.S)

    if not block or 'id="weeks"' not in body:
        return body

    modes = []

    for one in re.finditer(
        r"(\w+):\s*\{\s*mark:\s*function \(w\) \{ return ([^;]+); \},\s*title:\s*'((?:[^'\\]|\\.)*)',"
        r"\s*rows:\s*\[(.*?)\]\s*\}",
        block.group(1),
        re.S,
    ):
        rule = js_condition(one.group(2))

        if not re.fullmatch(r"[\w\s%='\"()<>!.|&+\-*/]+", rule):
            continue

        weeks = []

        for week in range(1, 13):
            kind = eval(rule, {"__builtins__": {}}, {"w": week})  # noqa: S307 — выражение проверено выше
            weeks.append(
                '<div class="wk{mod}"><span>Н{n}</span> <span>{sign}</span></div>'.format(
                    mod=" big" if kind == "big" else (" wk-test" if kind == "test" else ""),
                    n=week,
                    sign="◆" if kind == "big" else ("●" if kind == "test" else "·"),
                )
            )

        rows = "".join(
            '<div class="kv"><span class="k">{key}</span><span class="v">{value}</span></div>'.format(
                key=key.replace("\\'", "'"), value=value.replace("\\'", "'")
            )
            for key, value in re.findall(
                r"\['((?:[^'\\]|\\.)*)',\s*'((?:[^'\\]|\\.)*)'\]", one.group(4), re.S
            )
        )
        modes.append(
            {
                "key": one.group(1),
                "title": one.group(3).replace("\\'", "'"),
                "weeks": "".join(weeks),
                "rows": rows,
            }
        )

    if not modes:
        return body

    label = dict(re.findall(r'data-c="(\w+)" type="button"[^>]*>([^<]+)</button>', body))
    buttons = "".join(
        '<button class="ds-switch__button" type="button" data-switch-btn="{key}" hidden>{name}</button>'.format(
            key=one["key"], name=label.get(one["key"], one["title"].split(" · ")[0])
        )
        for one in modes
    )
    panes = "".join(
        '<div data-switch-pane="{key}"><div class="weeks">{weeks}</div>'
        '<div class="cad-out"><p><b>{title}</b></p>{rows}</div></div>'.format(**one)
        for one in modes
    )
    body = re.sub(r'<button class="btn cad"[^>]*>[^<]*</button>\s*', "", body)
    body = body.replace('<div class="weeks" id="weeks"></div>', panes, 1)
    body = re.sub(r'<div class="cad-out" id="cadOut"></div>\s*', "", body)
    # Кнопки режимов стоят в шапке коробки, а панели — в её теле; общий предок
    # у них только сама коробка, поэтому `data-switch` вешаем на неё.
    body = re.sub(
        r'<div class="box">(\s*<div class="box-head">Конструктор ритма.*?</span>)',
        lambda m: '<div class="box ds-switch" data-switch>' + m.group(1) + buttons,
        body,
        count=1,
        flags=re.S,
    )
    notes.append("конструктор ритма: раскладок " + str(len(modes)) + ", недель в каждой 12")

    return body


# ---------------------------------------------------------------------------
# Живые куски темы «Анализ конкурентов»: таблица аналогов в двух видах, два
# конструктора текста (подпись к скриншоту и отказ от приёма), лесенка причин
# и карточки принципов.
# ---------------------------------------------------------------------------


def js_strings(chunk: str) -> list:
    """Строковые литералы подряд: `'a', 'b', 'c'` → ['a', 'b', 'c']."""
    return [
        one.replace("\\'", "'").replace('\\"', '"')
        for one in re.findall(r"'((?:[^'\\]|\\.)*)'", chunk, re.S)
    ]


def element_end(text: str, start: int, tag: str = "div") -> int:
    """Конец элемента, который начинается в `start`: считает вложенные теги того же имени."""
    depth = 0

    for step in re.finditer(r"</?" + tag + r"\b[^>]*>", text[start:], re.I):
        depth += -1 if step.group(0).startswith("</") else 1

        if depth == 0:
            return start + step.end()

    return -1


def switch_box(body: str, head_starts: str, buttons: str) -> str:
    """Делает коробку корнем переключателя: кнопки в шапке, панели в теле.

    Общий предок у кнопок и панелей — только сама коробка, поэтому `data-switch`
    вешается на неё, а кнопки встают в шапку сразу за распоркой.
    """
    return re.sub(
        r'<div class="box">(\s*<div class="box-head">' + re.escape(head_starts) + r'.*?<span class="spacer"></span>)',
        lambda m: '<div class="box ds-switch" data-switch>' + m.group(1) + buttons,
        body,
        count=1,
        flags=re.S,
    )


def analog_table_markup(js: str, body: str, notes: list) -> str:
    """Таблица разбора аналогов: заполненный пример и пустой шаблон с подсказками."""
    cols = re.search(r"var COLS = \[(.*?)\];", js, re.S)
    hints = re.search(r"var HINTS = \[(.*?)\];", js, re.S)
    rows = re.search(r"var ROWS = \[(.*?)\n    \];", js, re.S)

    if not (cols and hints and rows) or 'id="atblWrap"' not in body:
        return body

    heads = js_strings(cols.group(1))
    tips = js_strings(hints.group(1))
    lines = [js_strings(one) for one in re.findall(r"\[(.*?)\](?=,\s*\n|\s*$)", rows.group(1), re.S)]
    lines = [one for one in lines if len(one) == len(heads)]

    if not heads or not lines:
        return body

    head = "<thead><tr>" + "".join("<th>" + one + "</th>" for one in heads) + "</tr></thead>"
    full = "".join("<tr>" + "".join("<td>" + cell + "</td>" for cell in one) + "</tr>" for one in lines)
    blank = '<tr class="hintrow">' + "".join("<td>" + one + "</td>" for one in tips) + "</tr>"

    for number in range(1, len(lines) + 1):
        blank += "<tr><td>Аналог " + str(number) + "</td>" + "<td></td>" * (len(heads) - 1) + "</tr>"

    labels = dict(re.findall(r'id="tt(Ex|Tpl)"[^>]*>([^<]+)</button>', body))
    names = {"ex": labels.get("Ex", "Пример"), "tpl": labels.get("Tpl", "Шаблон")}
    panes = "".join(
        '<div data-switch-pane="{key}"><p class="ds-switch__title">{name}</p>'
        '<div class="atbl"><table>{head}<tbody>{rows}</tbody></table></div></div>'.format(
            key=key, name=names[key], head=head, rows=inner
        )
        for key, inner in (("ex", full), ("tpl", blank))
    )
    buttons = "".join(
        '<button class="ds-switch__button" type="button" data-switch-btn="{key}" hidden>{name}</button>'.format(
            key=key, name=names[key]
        )
        for key in ("ex", "tpl")
    )
    body = re.sub(r'<button class="btn tt"[^>]*>[^<]*</button>\s*', "", body)
    body = body.replace('<div class="atbl" id="atblWrap"></div>', '<div id="atblWrap">' + panes + "</div>", 1)
    body = switch_box(body, "Таблица разбора аналогов", buttons)
    notes.append("таблица аналогов: колонок {}, строк примера {}".format(len(heads), len(lines)))

    return body


# Шаблоны конструкторов. Синтаксис один на конвертер и на скрипт сайта:
#   {поле}, {поле|запасное слово}, {поле:фильтр}; {? … ?} — кусок выводится,
#   только если все поля внутри него заполнены. Фильтры: slug, num, ru.
# Шаблон записан здесь, а не вытащен из её скрипта: там он собран сложением строк
# с условиями. Чтобы шаблон не разошёлся с присланным уроком, каждая его фраза
# сверяется со скриптом — не нашлась, значит текст урока поменяли, и конструктор
# остаётся нетронутым с пометкой в отчёте.
BUILDERS = {
    "cb": {
        "out": "cbOut",
        "note": "cbNote",
        "today": ["date"],
        "templates": [
            ("text", "{prod:slug|продукт}_{step:num}_{screen:slug|экран}_{date}.png"),
            (
                "text",
                "Шаг {step|—}. {screen|экран}{? после того, как {before}?}. "
                "{?Снял ради: {why}.?}{? Просмотрено {date:ru}.?}",
            ),
        ],
        "joint": "\n\n",
        "phrases": ["'Шаг '", "' после того, как '", "'Снял ради: '", "' Просмотрено '", "'продукт'", "'экран'"],
    },
    "rb": {
        "out": "rbText",
        "note": "rbNote",
        "today": [],
        "templates": [
            (
                "html",
                "<b>{trick|[приём]}</b> есть {who|[у кого]}."
                "{? Похоже, у них это из-за того, что {why}.?}"
                "{? <b>У нас иначе:</b> {us}.?}"
                "{? Поэтому предлагаю {alt}.?}"
                "{? Для нашей задачи это лучше, потому что {better}.?}",
            ),
        ],
        "joint": "",
        "phrases": [
            "'</b> есть '", "'Похоже, у них это из-за того, что '", "'<b>У нас иначе:</b> '",
            "'Поэтому предлагаю '", "'Для нашей задачи это лучше, потому что '", "'[приём]'", "'[у кого]'",
        ],
    },
}


def build_filter(value: str, name: str) -> str:
    if name == "slug":
        value = re.sub(r"\s+", "-", value.strip().lower())

        return re.sub(r"[^a-zа-яё0-9-]", "", value)

    if name == "num":
        found = re.search(r"(\d+)", value or "")

        return found.group(1).zfill(2) if found else "01"

    if name == "ru":
        parts = value.split("-")

        return ".".join(reversed(parts)) if len(parts) == 3 else value

    return value


def build_render(template: str, values: dict, mode: str) -> str:
    """Собирает текст по шаблону — тем же способом, что и скрипт сайта."""

    def field(found):
        name, _, rest = found.group(1).partition("|")
        name, _, how = name.partition(":")
        value = (values.get(name) or "").strip()

        if how == "num":
            return build_filter(value, how)

        value = build_filter(value, how) if how and value else value
        value = value or rest

        return html.escape(value, quote=False) if mode == "html" else value

    def group(found):
        inner = found.group(1)
        names = [one.partition("|")[0].partition(":")[0] for one in re.findall(r"\{([^{}?]+)\}", inner)]

        if any(not (values.get(name) or "").strip() for name in names):
            return ""

        return re.sub(r"\{([^{}?]+)\}", field, inner)

    out = re.sub(r"\{\?(.*?)\?\}", group, template, flags=re.S)

    return re.sub(r"\{([^{}?]+)\}", field, out)


def builder_markup(js: str, body: str, notes: list) -> str:
    """Конструкторы текста: поля, шаблон, подсказка о том, чего не хватает."""
    for prefix, setup in BUILDERS.items():
        if 'id="' + setup["out"] + '"' not in body:
            continue

        lost = [one for one in setup["phrases"] if one not in js]

        if lost:
            notes.append("конструктор {}: фраз нет в присланном скрипте — {}".format(prefix, ", ".join(lost)))
            continue

        # Поля и их значения по умолчанию — из разметки.
        values = {}

        # Два прохода, а не один с необязательным хвостом: у `<input>` необязательная группа
        # «…</textarea>» дотягивалась до чужого закрывающего тега и съедала соседнее поле.
        for found in re.finditer(r'<input\b[^>]*\bid="' + prefix + r'([A-Z]\w*)"[^>]*>', body):
            name = found.group(1)[0].lower() + found.group(1)[1:]
            value = re.search(r'\bvalue="([^"]*)"', found.group(0))
            values[name] = html.unescape(value.group(1) if value else "")

        for found in re.finditer(
            r'<textarea\b[^>]*\bid="' + prefix + r'([A-Z]\w*)"[^>]*>(.*?)</textarea>', body, re.S
        ):
            name = found.group(1)[0].lower() + found.group(1)[1:]
            values[name] = html.unescape(found.group(2))

        # Чего не хватает: условия из её скрипта, имена — оттуда же.
        needs = {}

        for found in re.finditer(
            r"if \(!(?:f\.(\w+)\.value(?:\.trim\(\))?|v\(f\.(\w+)\))\) miss\.push\('([^']*)'\)", js
        ):
            name = found.group(1) or found.group(2)

            if name in values:
                needs[name] = found.group(3)

        def when_of(condition: str) -> str:
            names = re.findall(r"!\s*(?:v\(f\.(\w+)\)|f\.(\w+)\.value)", condition)

            if names:
                return " ".join("!" + (a or b) for a, b in names)

            return "miss" if "miss.length" in condition else "ok"

        def note_text(expr: str) -> str:
            expr = re.sub(r"'\s*\+\s*miss\.join\([^)]*\)\s*\+\s*'", "@@miss@@", expr)

            return js_string(expr).replace("@@miss@@", "<span data-build-miss></span>")

        place = js.find("getElementById('" + setup["note"] + "')")
        scope = js[place:js.find("})();", place)] if place >= 0 else ""
        rules = []
        ternary = re.search(r"note\.innerHTML = miss\.length\s*\?\s*(.*?)\s*:\s*('(?:[^'\\]|\\.)*');", scope, re.S)

        if ternary:
            rules = [("miss", note_text(ternary.group(1))), ("ok", note_text(ternary.group(2)))]
        else:
            chain = re.findall(
                r"(?:if \(([^;{}\n]*)\)|else)\s*\{\s*note\.innerHTML = (.*?);\s*\}", scope, re.S
            )
            rules = [(when_of(cond) if cond else "ok", note_text(expr)) for cond, expr in chain]

        if not rules:
            notes.append("конструктор {}: подсказки не разобраны".format(prefix))
            continue

        def holds(when: str) -> bool:
            if when == "ok":
                return True

            if when == "miss":
                return any(not (values.get(name) or "").strip() for name in needs)

            return all(not (values.get(one[1:]) or "").strip() for one in when.split())

        first = next((n for n, (when, _) in enumerate(rules) if holds(when)), len(rules) - 1)
        missing = ", ".join(label for name, label in needs.items() if not (values.get(name) or "").strip())
        note_html = "".join(
            '<p class="{p}-note" data-build-note data-when="{when}"{hide}>{text}</p>'.format(
                p=prefix,
                when=when,
                hide="" if n == first else " hidden",
                text=text.replace("<span data-build-miss></span>", "<span data-build-miss>" + missing + "</span>")
                if n == first
                else text,
            )
            for n, (when, text) in enumerate(rules)
        )
        outs = setup["joint"].join(
            '<span data-build-out data-build-mode="{mode}" data-template="{tpl}">{now}</span>'.format(
                mode=mode,
                tpl=html.escape(template, quote=True),
                now=build_render(template, values, mode)
                if mode == "html"
                else html.escape(build_render(template, values, mode), quote=False),
            )
            for mode, template in setup["templates"]
        )

        # Разметка: поля получают имя, выход — шаблон и готовый текст по умолчанию.
        def name_field(found):
            name = found.group(2)[0].lower() + found.group(2)[1:]
            extra = ' data-build-field="' + name + '"'

            if name in needs:
                extra += ' data-build-need="' + html.escape(needs[name], quote=True) + '"'

            if name in setup["today"]:
                extra += " data-build-today"

            return found.group(1) + extra

        body = re.sub(r'(<(?:input|textarea)\b[^>]*\bid="' + prefix + r'([A-Z]\w*)")', name_field, body)
        body = re.sub(
            r'(<div class="' + prefix + r'-(?:line|text)" id="' + setup["out"] + r'")></div>',
            lambda m: m.group(1) + ">" + outs + "</div>",
            body,
            count=1,
        )
        body = re.sub(r'<p class="' + prefix + r'-note" id="' + setup["note"] + r'"></p>', lambda m: note_html, body, count=1)
        body = re.sub(
            r'<div class="' + prefix + r'-grid">', '<div class="' + prefix + '-grid" data-build-fields>', body, count=1
        )
        body = re.sub(
            r'(<div class="box-body")(>\s*<div class="' + prefix + r'-grid")', r"\1 data-build\2", body, count=1
        )
        notes.append(
            "конструктор {}: полей {}, подсказок {}, по умолчанию «{}»".format(
                prefix, len(values), len(rules), rules[first][0]
            )
        )

    return body


def dig_markup(js: str, body: str, notes: list) -> str:
    """Лесенка причин: от приёма до ограничения, которое можно проверить у себя."""
    block = re.search(r"var STEPS = \[(.*?)\n    \];", js, re.S)

    if not block or 'id="digList"' not in body:
        return body

    steps = re.findall(
        r"\{\s*l:\s*'((?:[^'\\]|\\.)*)',\s*h:\s*'((?:[^'\\]|\\.)*)',\s*p:\s*'((?:[^'\\]|\\.)*)',\s*q:\s*'((?:[^'\\]|\\.)*)'\s*\}",
        block.group(1),
        re.S,
    )
    final = re.search(r"final\.innerHTML = (.*?);\n", js, re.S)
    ending = re.search(r"hint\.textContent = '((?:[^'\\]|\\.)*)';\s*\n\s*final\.className = 'dig-final on'", js, re.S)
    locked = re.search(r"\? s\.p : '((?:[^'\\]|\\.)*)'", js)

    if not steps or not final:
        return body

    rows = "".join(
        '<div class="dig-step" data-dig-step><span class="lvl">{level}</span><h5>{title}</h5>'
        '<p data-dig-body>{text}</p><p class="dig-ask" data-dig-ask>{ask}</p></div>'.format(
            level=level.replace("\\'", "'"),
            title=title.replace("\\'", "'"),
            text=text.replace("\\'", "'"),
            ask=ask.replace("\\'", "'"),
        )
        for level, title, text, ask in steps
    )
    next_label = re.search(r'id="digNext"[^>]*>([^<]+)</button>', body)
    reset_label = re.search(r'id="digReset"[^>]*>([^<]+)</button>', body)
    body = body.replace(
        '<div class="dig" id="digList"></div>',
        '<div class="dig" data-dig data-dig-locked="{locked}" data-dig-next="{go}" data-dig-reset="{back}">{rows}</div>'.format(
            locked=html.escape(locked.group(1) if locked else "", quote=True),
            go=html.escape(next_label.group(1).strip() if next_label else "Дальше", quote=True),
            back=html.escape(reset_label.group(1).strip() if reset_label else "Сначала", quote=True),
            rows=rows,
        ),
        1,
    )
    body = re.sub(r'<button[^>]*id="digReset"[^>]*>.*?</button>', "<span data-dig-reset-place></span>", body, flags=re.S)
    body = re.sub(r'<button[^>]*id="digNext"[^>]*>.*?</button>', "<span data-dig-actions></span>", body, flags=re.S)
    # Подсказка «нажимайте…» без кнопки бессмысленна: в разметке она скрыта, показывает её скрипт.
    body = re.sub(
        r'<span class="dim" id="digHint"[^>]*>',
        '<span class="dim" data-dig-hint data-dig-hint-end="{}" hidden>'.format(
            html.escape(ending.group(1) if ending else "", quote=True)
        ),
        body,
        count=1,
    )
    body = body.replace(
        '<div class="dig-final" id="digFinal"></div>',
        '<div class="dig-final" data-dig-final>' + js_string(final.group(1)) + "</div>",
        1,
    )
    notes.append("лесенка причин: ступеней " + str(len(steps)))

    return body


def pcards_to_details(text: str, notes: list) -> str:
    """Карточки принципов: кнопка со скриптом → details.

    Раскрытие работает без JS, а атрибут `name` даёт «открыта только одна» средствами
    браузера. Заодно чинится вложенность: у неё блок «так / не так» (`div`) лежит
    внутри `span`, а это невалидно — ключ и значение строки становятся `div`.
    """
    count = 0
    at = 0

    while True:
        found = re.search(r'<div class="pcard"[^>]*>', text[at:])

        if not found:
            break

        start = at + found.start()
        stop = element_end(text, start)

        if stop < 0:
            break

        card = text[start:stop]
        head = re.search(r"<button[^>]*>(.*?)</button>", card, re.S)
        hint = re.search(r'<p class="hintline">(.*?)</p>', card, re.S)
        inner = re.search(r'<div class="body">', card)

        if not head or not inner:
            at = stop
            continue

        content_start = inner.start()
        content_stop = element_end(card, content_start)
        content = card[content_start:content_stop]

        # span.k / span.v → div: внутри значения бывает блочная разметка.
        content = content.replace('<span class="k">', '<div class="k">')
        content = re.sub(r'(<div class="k">[^<]*)</span>', r"\1</div>", content)
        out = []
        pos = 0

        while True:
            v = content.find('<span class="v">', pos)

            if v < 0:
                out.append(content[pos:])
                break

            end = element_end(content, v, "span")
            out.append(content[pos:v])
            out.append('<div class="v">' + content[v + len('<span class="v">'):end - len("</span>")] + "</div>")
            pos = end

        content = "".join(out)
        summary = head.group(1) + ('<span class="hintline">' + hint.group(1) + "</span>" if hint else "")
        fresh = '<details class="pcard" name="pcards"><summary>' + summary + "</summary>" + content + "</details>"
        text = text[:start] + fresh + text[stop:]
        at = start + len(fresh)
        count += 1

    if count:
        notes.append("карточек принципов переведено в details: " + str(count))

    return text


def copy_holder(text: str, notes: list) -> str:
    """Кнопка копирования → пустое место: кнопку рисует скрипт, и она работает.

    В присланном уроке кнопка сама несёт `data-copy="#id"`. Наш скрипт ждёт пустой
    элемент с голым `id` и создаёт кнопку сам — иначе без JS она была бы мёртвой.
    Селектор с решёткой `getElementById` не понимает, поэтому копирование молча
    не работало во всех уроках сразу. Найдено прогоном в браузере 17.09.2026.
    """
    text, n = re.subn(
        r'<button[^>]*data-copy="#?([A-Za-z0-9_-]+)"[^>]*>.*?</button>',
        lambda m: '<span data-copy="%s"></span>' % m.group(1),
        text,
        flags=re.S,
    )

    if n:
        notes.append("кнопок копирования переведено на место для скрипта: " + str(n))

    return text


def cards_to_details(text: str, notes: list) -> str:
    """Карточка-кнопка «показать ответ» → details: ответ виден и без скрипта."""
    def one(match):
        ask = re.search(r'<span class="ask">(.*?)</span>', match.group(1), re.S)
        answer = re.search(r'<span class="ans">(.*?)</span>', match.group(1), re.S)

        if not ask or not answer:
            return match.group(0)

        return (
            '<details class="card"><summary class="card-ask">{ask}</summary>'
            '<div class="ans">{answer}</div></details>'
        ).format(ask=ask.group(1), answer=answer.group(1))

    text, n = re.subn(r'<button class="card"[^>]*>(.*?)</button>', one, text, flags=re.S)

    if n:
        notes.append("карточек-кнопок переведено в details: " + str(n))

    return text


def drop_inline_styles(text: str, notes: list) -> str:
    """Снимает инлайновые стили присланной страницы.

    Они ссылаются на её переменные (`var(--accent)`, `var(--hairline)`), которых у
    нас нет, и задают размеры в пикселях мимо шкалы. Две вещи остаются: доля куска
    на ленте времени (`flex:5` — это данные, а не оформление) и `display:none`,
    который превращается в атрибут `hidden`.
    """
    kept = []
    dropped = []

    def one(match):
        rules = [r.strip() for r in match.group(1).split(";") if r.strip()]
        flex = [r for r in rules if re.fullmatch(r"flex:\s*\d+", r.replace(" ", " "))]
        hide = any(r.replace(" ", "") == "display:none" for r in rules)

        for rule in rules:
            if rule not in flex and rule.replace(" ", "") != "display:none":
                dropped.append(rule)

        out = ""

        if flex:
            kept.extend(flex)
            out += ' style="' + "; ".join(flex) + '"'

        if hide:
            out += " hidden"

        return out

    text = re.sub(r'\s*style="([^"]*)"', one, text)

    if dropped:
        notes.append("инлайновых объявлений снято: " + str(len(dropped)))

    if kept:
        notes.append("доли ленты времени сохранены: " + str(len(kept)))

    return text


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

widget_notes = []
script = "\n".join(m.group(1) for m in re.finditer(r"<script[^>]*>(.*?)</script>", raw, re.S))
body = sim_markup(script, body, widget_notes)
body = marks_markup(script, body, widget_notes)
body = pick_markup(script, body, widget_notes)
body = matrix_markup(script, body, widget_notes)
body = panel_markup(script, body, widget_notes)
body = calc_markup(script, body, widget_notes)
body = cadence_markup(script, body, widget_notes)
body = analog_table_markup(script, body, widget_notes)
body = builder_markup(script, body, widget_notes)
body = dig_markup(script, body, widget_notes)
body = pcards_to_details(body, widget_notes)
body = re.sub(r'<button[^>]*id="calcReset"[^>]*>.*?</button>', '<span data-calc-actions></span>', body, flags=re.S)
body = copy_holder(body, widget_notes)
body = cards_to_details(body, widget_notes)
body = drop_inline_styles(body, widget_notes)

for hook, attribute in HOOKS.items():
    body = body.replace('id="%s"' % hook, 'id="%s" %s' % (hook, attribute))

body = map_classes(body, unknown, path.stem)
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
print("живые куски:", "; ".join(widget_notes) if widget_notes else "нет")
print("«сам»:", len(SELF_REPORT))
for line in SELF_REPORT:
    print("  ", line)
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
