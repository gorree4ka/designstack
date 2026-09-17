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
    # компоненты темы «Опросы»
    "bars": "ds-lesson__bars",
    "brow": "ds-lesson__bar",
    "blab": "ds-lesson__bar-label",
    "btrack": "ds-lesson__bar-track",
    "bfill": "ds-lesson__bar-fill",
    "rt": "is-num",
    "ppl": "ds-lesson__ppl",
    "legend2": "ds-lesson__dots-legend",
    "bias-view": "ds-lesson__bias-view",
    "bias-title": "ds-lesson__bias-title",
    "share-rows": "ds-lesson__share-rows",
    "calcrow": "ds-lesson__share-row",
    "calchd": "ds-lesson__share-head",
    "calcout": "ds-lesson__build-out",
    "lines": "ds-lesson__build-text ds-lesson__build-text--mono",
    "res": "ds-lesson__share-part",
    "pager": "ds-lesson__doc",
    "rep": "ds-lesson__doc",
    "opt-q": "ds-lesson__pick-q",
    "opt-list": "ds-lesson__optlist",
    "opt-name": "ds-lesson__opt-name",
    "opt-why": "ds-lesson__opt-why",
    "opt-meta": "ds-lesson__meta",
    "opt-fix": "ds-lesson__result",
    "sc-body": "",
    "sc-card": "ds-lesson__scale",
    "sc-ex": "ds-lesson__scale-ex",
    "opts2": "ds-lesson__dim",
    "sc-warn": "ds-lesson__scale-warn",
    "cmp": "",
    "cmp-row": "ds-lesson__cmp-row",
    "cmp-two": "ds-lesson__cmp-two",
    "cmp-v": "ds-lesson__cmp-verdict",
    "bc-grid": "ds-lesson__build-grid",
    "bc-out": "ds-lesson__out",
    "bc-big": "ds-lesson__big",
    "bc-say": "ds-lesson__say",
    "rng": "ds-lesson__range",
    "axis": "ds-lesson__range-axis",
    "span": "ds-lesson__range-span",
    "pt": "ds-lesson__range-point",
    "ptlab": "ds-lesson__range-label",
    "tick": "ds-lesson__range-tick",
    "claim": "ds-lesson__claim",
    # компоненты темы «Сценарии и структура»
    "fig-scroll": "ds-lesson__figure",
    "btn-ghost": "",
    "hunt": "ds-lesson__hunt",
    "hunt-count": "ds-lesson__count",
    "hunt-fb": "ds-lesson__result",
    "hunt-list": "ds-lesson__hunt-list",
    "hunt-all": "ds-lesson__dim",
    "it": "ds-lesson__shape",
    "ok-list": "ds-lesson__oklist",
    "seq": "",
    "seq-pool": "ds-lesson__seq-pool",
    "seq-chain": "ds-lesson__seq-chain",
    "seq-note": "ds-lesson__seq-note",
    "seq-decoy": "ds-lesson__seq-decoy",
    "seq-empty": "ds-lesson__dim",
    "seq-fb": "ds-lesson__result",
    "tabnote": "ds-lesson__result",
    "cs-pool": "ds-lesson__sort-pool",
    "cs-groups": "ds-lesson__sort-groups",
    "cs-res": "ds-lesson__sort-result",
    "mini": "ds-lesson__mini",
    "top": "is-top",
    "flag": "ds-lesson__flag",
    "tt-task": "ds-lesson__tree-task",
    "tt-crumb": "ds-lesson__tree-crumb",
    "tt-list": "ds-lesson__tree-list",
    "tt-tree": "ds-lesson__tree-source",
    "tt-bar": "ds-lesson__acts",
    "tt-res": "ds-lesson__result",
    "path": "ds-lesson__path",
    "h": "",
    "metrics": "ds-lesson__metrics",
    "metric": "ds-lesson__metric",
    "cases": "ds-lesson__cases",
    "wiz": "ds-lesson__wiz",
    "wiz-list": "ds-lesson__pcards",
    "wiz-case": "ds-lesson__pcard ds-lesson__wiz-case",
    "qt": "ds-lesson__wiz-q",
    "qfb": "ds-lesson__wiz-fb",
    "rules": "ds-lesson__rules",
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
    "surveys-junior": {
        "q": "ds-lesson__qcard",
        "typ": "ds-lesson__qcard-type",
        "t": "ds-lesson__bar-name",
        "v": "ds-lesson__bar-value",
        "btn": "ds-button ds-button--secondary ds-button--sm",
    },
    "surveys-middle": {
        "t": "ds-lesson__bar-name",
        "v": "ds-lesson__bar-value",
        "vd": "ds-lesson__verdict",
        "same": "ds-lesson__verdict--keep",
        "clash": "ds-lesson__verdict--kill",
        "other": "ds-lesson__verdict--hold",
        "st": "ds-lesson__checkbar-state",
        "btn": "ds-button ds-button--secondary ds-button--sm",
    },
    "surveys-senior": {
        "t": "ds-lesson__bar-name",
        "v": "ds-lesson__bar-value",
        "vd": "ds-lesson__verdict",
        "hold": "ds-lesson__verdict--keep",
        "soft": "ds-lesson__verdict--hold",
        "drop": "ds-lesson__verdict--kill",
        "n": "ds-lesson__tier-label",
        "pts": "ds-lesson__three",
        "pt-card": "ds-lesson__three-item",
        "txt": "ds-lesson__claim-text",
        "note": "ds-lesson__claim-note",
        "btn": "ds-button ds-button--secondary ds-button--sm",
    },
    "flows-structure-junior": {
        "legend": "ds-lesson__shapes",
        "pin": "ds-lesson__hunt-pin",
        "q": "ds-lesson__hunt-q",
        "fix": "ds-lesson__hunt-fix",
        "txt": "ds-lesson__seq-text",
        "btn": "ds-button ds-button--secondary ds-button--sm",
    },
    "flows-structure-middle": {
        "btn": "ds-button ds-button--secondary ds-button--sm",
    },
    "flows-structure-senior": {
        "verdict": "ds-lesson__wiz-verdict",
        "vr": "ds-lesson__kv",
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
    # подсказки под тренажёрами, которые вернулись в уроки 17.09.2026
    "сравнивай": "сравнивайте",
    # тема «Опросы»
    "убедись": "убедитесь", "описывай": "описывайте", "оценивай": "оценивайте",
    "подменяй": "подменяйте", "переключай": "переключайте", "переформулируй": "переформулируйте",
    "выгрузи": "выгрузите", "напомни": "напомните", "продумай": "продумайте", "реши": "решите",
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
    text, figures = re.subn(
        r'<div class="(ds-lesson__figure[^"]*)"(?![^>]*tabindex)',
        r'<div class="\1" tabindex="0" role="group" aria-label="Схема, листается вбок"',
        text,
    )
    n += figures

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
    "ошибка уровня": "ошибка ступени",
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


# После этих слов «уровень» — про устройство продукта, а не про ступень обучения:
# «про уровни структуры продукта» — это книга Гарретта, а не Junior, Middle и Senior.
# Найдено глазами в теме «Сценарии и структура» 17.09.2026: сочетание «про уровни»
# было в списке ступеней и переводилось вслепую.
NOT_A_STEP = r"(?!\s+(?:структур|навигац|меню|дерева|вложенност|иерарх|продукта|сайта|интерфейс|абстракц))"


def steps_and_odd(text: str, notes: list) -> str:
    """Сочетания про ступень и неправильное прошедшее время."""
    for phrase, repl in STEP_PHRASES.items():
        pattern = re.compile(r"(?<![А-Яа-яЁё])" + re.escape(phrase) + r"(?![А-Яа-яЁё])" + NOT_A_STEP, re.I)
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
    r"пользовател[а-яё]+|он|она|они|ведущ[а-яё]+|кто-то|кому-то|разработчик[а-яё]*|"
    r"нович[а-яё]+|автор[а-яё]*)(?![А-Яа-яЁё-])",
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
        # Подлежащее третьего лица ищется только до слова «сам»: «найдёт ли человек корзину сам» —
        # про человека, а «пройдите по нему сам или вместе с коллегой» — про читателя, хотя
        # коллега в предложении тоже есть.
        ahead = text[left + 1:found.start()]
        reader = bool(READER_RE.search(around)) and not OTHER_RE.search(ahead)

        # «Сам» перед существительным или прилагательным — это «сам по себе», а не обращение:
        # «не работает сам проверяемый сценарий». К читателю слово относится, когда после него
        # конец фразы, союз, предлог или глагол: «решаете сам и…», «сам определите».
        # Случай: 17.09.2026 — на сайт уехало «не работает сами проверяемый сценарий».
        after = re.match(r"\s+([А-Яа-яЁё-]+)(\s+[а-яё]+)?", text[found.end():right])

        if after:
            word = after.group(1).lower()
            idiom = word == "по" and (after.group(2) or "").strip() == "себе"
            link = word in {"и", "или", "а", "но", "либо", "из", "без", "от", "с", "со", "в", "на", "за", "для", "до", "при", "по"}
            verb = re.search(r"(?:те|тесь|ть|ться|чь)$", word)

            if idiom or not (link or verb):
                reader = False

        # «Сама» к читателю не относится никогда: у неё читатель — «ты … сам», а женский род
        # согласуется с существительным рядом («схема должна работать сама»). И «сам» сразу
        # после глагола в единственном числе — «пришёл сам» — тоже не про читателя: с «вы»
        # глагол стоял бы во множественном. Оба случая найдены глазами 17.09.2026.
        before = re.search(r"([А-Яа-яЁё]+)\s+$", text[max(0, found.start() - 40):found.start()])

        if found.group(1).lower() == "сама" or (before and re.search(r"(?:л|лся|ёл|шёл)$", before.group(1).lower())):
            reader = False

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


def quiz_markup(items: list, options: list, title: str = "Тренажёр", foot: str = "") -> str:
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

    # Счётчик вопроса и счёт имеют смысл только в пошаговом режиме: без скрипта вопросы
    # идут списком, и «вопрос 1 из 10» над ним был бы неправдой. Показывает их lesson.js.
    head = (
        '<div class="ds-lesson__box ds-quiz" data-quiz>\n'
        '<div class="ds-lesson__box-head">'
        + title
        + '<span class="ds-lesson__spacer"></span><span data-quiz-meta hidden>вопрос <span data-quiz-idx>1</span> из '
        + str(len(items))
        + " · <span data-quiz-score>0 верно</span></span></div>\n"
    )
    body = (
        '<div class="ds-lesson__box-body">\n<ol class="ds-quiz__list">\n'
        + "\n".join(rows)
        + '\n</ol>\n<div class="ds-quiz__actions" data-quiz-actions hidden>'
        + buttons
        + "</div>\n"
        '<div class="ds-quiz__bar"><span class="ds-quiz__track"><i data-quiz-fill></i></span>'
        '<button class="ds-button ds-button--secondary ds-button--sm" type="button" data-quiz-next hidden>'
        "Дальше</button></div>\n</div>\n"
        + ('<div class="ds-lesson__box-foot">' + foot + "</div>\n" if foot else "")
        + "</div>"
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


def put_quiz(text: str, items: list, options: list, node: str = "quiz"):
    """Меняет её коробку тренажёра на нашу разметку. Возвращает текст и успех.

    Заменяется коробка целиком, но её слова остаются: заголовок («Тренажёр 2 · разложи
    запись по колонкам») и подсказка в подвале. Первая версия выбрасывала и то и другое —
    текст заказчицы молча пропадал из каждого тренажёра (найдено 17.09.2026). В новых
    уроках `id` стоит на внутреннем блоке, а не на коробке: тогда заменяется охватывающая
    коробка, иначе выходит коробка в коробке с двумя шапками.
    """
    inner = re.search(r'<div[^>]*\bid="' + re.escape(node) + r'"[^>]*>', text)

    if not inner or not items:
        return text, False

    start = inner.start()

    # Класс `box` ищется как отдельное слово: `box-body` и `box-head` — это не коробка,
    # а дефис для `\b` — граница слова, и первая версия принимала тело коробки за коробку.
    is_box = r'class="(?:[^"]*\s)?box(?:\s[^"]*)?"'

    if not re.search(is_box, inner.group(0)):
        outer = [m for m in re.finditer(r"<div " + is_box + r"[^>]*>", text[:start])]

        for candidate in reversed(outer):
            if element_end(text, candidate.start()) > start:
                start = candidate.start()
                break

    stop = element_end(text, start)

    if stop < 0:
        return text, False

    box = text[start:stop]
    head = re.search(r'<div class="box-head">(.*?)</div>', box, re.S)
    title = "Тренажёр"

    if head:
        plain = re.sub(r'<span class="spacer">.*', "", head.group(1), flags=re.S)
        plain = re.sub(r"<[^>]+>", "", plain).strip()
        title = plain or title

    foot = re.search(r'<div class="box-foot">(.*?)</div>\s*</div>\s*$', box, re.S)

    return text[:start] + quiz_markup(items, options, title, foot.group(1).strip() if foot else "") + text[stop:], True


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
        group = re.search(r'data-group="(\w+)"', found.group(0))
        fresh = (
            '<details class="pcard" name="' + (group.group(1) if group else "pcards") + '"><summary>'
            + summary + "</summary>" + content + "</details>"
        )
        text = text[:start] + fresh + text[stop:]
        at = start + len(fresh)
        count += 1

    if count:
        notes.append("карточек принципов переведено в details: " + str(count))

    return text


# ---------------------------------------------------------------------------
# Живые куски темы «Сценарии и структура»: вкладки со схемами, сборка цепочки
# шагов, поиск дыр на схеме, сортировка карточек, проверка дерева и стресс-тест.
# Данных в её скриптах здесь много и они вложенные, поэтому вместо регулярки на
# каждый массив — общий разбор JS-литерала в обычные списки и словари.
# ---------------------------------------------------------------------------


def js_literal(source: str):
    """JS-литерал (объект или массив) → данные Python.

    Строки в одинарных кавычках становятся JSON-строками, голые ключи берутся
    в кавычки, висячие запятые снимаются. Функций и выражений внутри не ждём:
    на них json.loads упадёт, и это правильнее, чем молча прочитать мусор.
    """
    out = []
    i = 0

    while i < len(source):
        char = source[i]

        if char in "'\"":
            j = i + 1
            buf = []

            while j < len(source) and source[j] != char:
                if source[j] == "\\" and j + 1 < len(source):
                    nxt = source[j + 1]
                    buf.append({"n": "\n", "t": "\t"}.get(nxt, nxt))
                    j += 2
                    continue

                buf.append(source[j])
                j += 1

            out.append(json.dumps("".join(buf), ensure_ascii=False))
            i = j + 1
            continue

        out.append(char)
        i += 1

    text = "".join(out)
    text = re.sub(r"([{,]\s*)([A-Za-z_]\w*)(\s*:)", r'\1"\2"\3', text)
    text = re.sub(r",(\s*[}\]])", r"\1", text)

    return json.loads(text)


def js_var(js: str, name: str):
    """Значение `var NAME = <литерал>` — со счётом скобок и с учётом строк."""
    found = re.search(r"\bvar\s+" + re.escape(name) + r"\s*=\s*", js)

    if not found:
        return None

    start = found.end()

    if start >= len(js) or js[start] not in "[{":
        return None

    depth = 0
    quote = None
    i = start

    while i < len(js):
        char = js[i]

        if quote:
            if char == "\\":
                i += 2
                continue
            if char == quote:
                quote = None
        elif char in "'\"":
            quote = char
        elif char in "[{":
            depth += 1
        elif char in "]}":
            depth -= 1

            if depth == 0:
                try:
                    return js_literal(js[start:i + 1])
                except ValueError:
                    return None

        i += 1

    return None


# Слова языка, а не урока. Если такое приехало в подпись кнопки, регулярка зацепилась
# не за то место: у `next ? 'true' : 'false'` и у подписи кнопки одинаковое начало.
# Случай: 17.09.2026 — кнопка разбора в уроке «Опросы, Senior» называлась «true».
JS_WORDS = {"true", "false", "null", "undefined", "on", "off", "block", "none", "flex", "0", "1"}
PHRASE_REPORT = []


def js_phrase(js: str, pattern: str, default: str = "") -> str:
    """Одна фраза из кода скрипта по регулярке с одной группой."""
    found = re.search(pattern, js, re.S)

    if not found:
        return default

    out = found.group(1).replace("\\'", "'")

    # Слово языка или обломок кода в подписи — верный признак, что регулярка
    # зацепилась не за то место: `'` и `+` в тексте урока не встречаются.
    if out.strip().lower() in JS_WORDS or re.search(r"'\s*\+|\+\s*'|\"\s*>", out):
        PHRASE_REPORT.append(out.strip()[:60] + " ← " + pattern[:60])

        return default

    return out


# Её переменные цвета → наши токены. Нужны только внутри SVG: там цвет задан прямо
# на фигурах, и без перевода схема осталась бы чёрной (переменных у нас нет).
SVG_VARS = {
    "--raised": "surface-raised",
    "--surface": "surface-subtle",
    "--demo-bg": "surface-subtle",
    "--page": "surface-default",
    "--ink": "text-default",
    "--ink-2": "text-muted",
    "--muted": "text-muted",
    "--svg-dim": "text-muted",
    "--accent": "text-action",
    "--accent-deep": "text-action",
    "--chip": "surface-selected",
    "--svg-chip": "surface-selected",
    "--hairline": "border-default",
    "--border": "border-default",
    "--bad": "icon-error",
    "--bad-soft": "bg-error",
    "--good": "icon-success",
    "--warn": "icon-warning",
    "--warn-soft": "bg-warning",
}


def svg_tokens(svg: str, lost: set) -> str:
    """Цвета схемы — на токены сайта; шрифт — наследуется от страницы."""

    def swap(found):
        name = found.group(1)

        if name in SVG_VARS:
            return "var(--wp--preset--color--" + SVG_VARS[name] + ")"

        lost.add(name)

        return found.group(0)

    svg = re.sub(r"var\((--[a-z0-9-]+)\)", swap, svg)

    return re.sub(r'\s+font-family="[^"]*"', "", svg)


def tabs_to_switch(body: str, notes: list) -> str:
    """Вкладки `role="tab"` → готовый переключатель `data-switch`.

    Без скрипта у неё видна только первая вкладка, остальные закрыты наглухо.
    У переключателя без скрипта видны все панели подряд, каждая со своим заголовком.
    """
    labels = dict(re.findall(r'<button[^>]*role="tab"[^>]*aria-controls="(\w+)"[^>]*>(.*?)</button>', body, re.S))

    if not labels:
        return body

    def bar(found):
        return '<div class="ds-switch__bar">' + "".join(
            '<button class="ds-switch__button" type="button" data-switch-btn="{key}" hidden>{name}</button>'.format(
                key=key, name=name.strip()
            )
            for key, name in re.findall(
                r'<button[^>]*role="tab"[^>]*aria-controls="(\w+)"[^>]*>(.*?)</button>', found.group(0), re.S
            )
        ) + "</div>"

    body = re.sub(r'<div class="tabs"[^>]*>.*?</div>', bar, body, flags=re.S)
    body = re.sub(
        r'<div class="tabpanel(?: on)?" id="(\w+)"[^>]*>',
        lambda m: '<div data-switch-pane="{key}"><p class="ds-switch__title">{name}</p>'.format(
            key=m.group(1), name=labels.get(m.group(1), "").strip()
        ),
        body,
    )
    body = re.sub(
        r'<div class="box-body">(\s*<div class="ds-switch__bar">)', r'<div class="box-body ds-switch" data-switch>\1', body
    )
    notes.append("вкладок переведено в переключатель: " + str(len(labels)))

    return body


def accs_to_details(text: str, notes: list) -> str:
    """Карточки-аккордеоны (`.acc[data-acc]`) — в ту же разметку, что карточки принципов."""
    groups = 0

    # Каждая группа получает своё имя: «открыта только одна» действует внутри группы.
    parts = re.split(r'(<div class="accs"[^>]*>)', text)
    out = [parts[0]]

    for n in range(1, len(parts), 2):
        groups += 1
        chunk = parts[n + 1].replace('<div class="acc" data-acc>', '<div class="pcard" data-group="accs%d">' % groups)
        out.append(parts[n].replace('class="accs"', 'class="pcards"'))
        out.append(chunk)

    if groups:
        notes.append("групп аккордеонов переведено в карточки: " + str(groups))

    return "".join(out)


def seq_markup(js: str, body: str, notes: list) -> str:
    """Сборка сценария по порядку: шаги, один лишний вариант и разбор каждого."""
    steps = js_var(js, "SEQ")
    decoy = js_var(js, "DECOY")
    order = js_var(js, "ORDER")

    if not steps or not order or 'id="seqPool"' not in body:
        return body

    rows = "".join(
        '<li data-seq-step{io}><span class="txt">{text}{tag}</span> <span class="seq-note" data-seq-note>{note}</span></li>'.format(
            io=' data-seq-io="%s"' % html.escape(one["io"], quote=True) if one.get("io") else "",
            text=one["t"],
            tag='<span class="tag">%s</span>' % one["io"] if one.get("io") else "",
            note=one.get("n", ""),
        )
        for one in steps
    )
    extra = ""

    if decoy:
        extra = (
            '<p class="seq-decoy" data-seq-decoy data-seq-decoy-text="{text}"><b>{title}: «{text}».</b> '
            "<span data-seq-decoy-note>{note}</span></p>"
        ).format(
            title=js_phrase(js, r"'<b>(Это лишний вариант)</b>'", "Это лишний вариант"),
            text=html.escape(decoy["t"], quote=True),
            note=decoy["n"],
        )

    words = {
        "right": js_phrase(js, r"'<b>(Верно)</b>'", "Верно"),
        "early": js_phrase(js, r"'<b>(Пока рано)</b>'", "Пока рано"),
        "extra": js_phrase(js, r"'<b>(Это лишний вариант)</b>'", "Это лишний вариант"),
        "first": js_phrase(js, r"expect === 0\s*\?\s*'((?:[^'\\]|\\.)*)'"),
        "next": js_phrase(js, r":\s*'(Сейчас на очереди[^']*)'") + "{prev}" + js_phrase(js, r"toLowerCase\(\) \+ '([^']*)'"),
        "done-title": js_phrase(js, r"'<b>(Собрано целиком)</b>", "Собрано целиком"),
        "done": js_phrase(js, r"<b>Собрано целиком</b>((?:[^'\\]|\\.)*)'"),
        "count": "{n} из {total}",
    }
    attrs = "".join(' data-seq-%s="%s"' % (key, html.escape(value, quote=True)) for key, value in words.items())
    markup = (
        '<div class="seq" data-seq data-seq-order="{order}"{attrs}>'
        '<div class="seq-pool" data-seq-pool></div>'
        '<ol class="seq-chain" data-seq-steps>{rows}</ol>{extra}</div>'
    ).format(order=",".join(str(one) for one in order), attrs=attrs, rows=rows, extra=extra)

    body = body.replace('<div class="seq-pool" id="seqPool"></div>', markup, 1)
    body = re.sub(r'\s*<div class="seq-chain" id="seqChain"></div>', "", body)
    body = re.sub(r'<p class="seq-empty" id="seqEmpty">', '<p class="seq-empty" data-seq-empty hidden>', body)
    body = body.replace('<div class="seq-fb" id="seqFb"></div>', '<div class="seq-fb" data-seq-fb hidden></div>', 1)
    body = re.sub(r'<span class="hunt-count" id="seqCount">[^<]*</span>', '<span class="hunt-count" data-seq-count-out></span>', body)
    body = re.sub(
        r'<div[^>]*>\s*<button[^>]*id="seqReset"[^>]*>(.*?)</button>\s*</div>',
        lambda m: '<span data-seq-actions data-seq-reset="%s"></span>' % html.escape(m.group(1).strip(), quote=True),
        body,
        flags=re.S,
    )
    notes.append("сборка сценария: шагов {}, лишних вариантов {}".format(len(steps), 1 if decoy else 0))

    return body


def hunt_markup(js: str, body: str, notes: list) -> str:
    """Поиск дыр на схеме: точки на рисунке и разбор каждой."""
    spots = js_var(js, "HUNT")

    if not spots or 'id="hunt"' not in body:
        return body

    fix = js_phrase(js, r"'<span class=\"fix\"><b>((?:[^<])*)</b>'", "Как чинить. ")
    rows = "".join(
        '<li data-hunt-item><span class="q">{q}</span><span class="fix"><b>{fix}</b>{text}</span></li>'.format(
            q=one["q"], fix=fix, text=one["fix"]
        )
        for one in spots
    )
    done = re.search(r"<span class=\"fix\" style=\"[^\"]*\">(<b>.*?)</span>' : ''", js, re.S)
    # Точка без скрипта — не кнопка: нажать её нечем, зато номер на схеме остаётся.
    body = re.sub(
        r'<button class="pin" type="button" data-hunt="(\d+)" (style="[^"]*") aria-label="([^"]*)">(\d+)</button>',
        r'<span class="pin" data-hunt-pin="\1" data-hunt-label="\3" \2>\4</span>',
        body,
    )
    body = body.replace('<div class="hunt" id="hunt">', '<div class="hunt" data-hunt data-hunt-count="Найдено {n} из {total}">', 1)
    body = re.sub(
        r'<div class="hunt-fb" id="huntFb">(.*?)</div>',
        lambda m: '<ol class="hunt-list" data-hunt-list>' + rows + "</ol>"
        + '<div class="hunt-fb" data-hunt-fb hidden>' + m.group(1) + "</div>"
        + ('<p class="hunt-all" data-hunt-all>' + done.group(1).replace("\\'", "'") + "</p>" if done else ""),
        body,
        count=1,
        flags=re.S,
    )
    body = re.sub(r'<span class="hunt-count" id="huntCount">[^<]*</span>', '<span class="hunt-count" data-hunt-count-out></span>', body)
    notes.append("поиск дыр: точек " + str(len(spots)))

    return body


def sort_markup(js: str, body: str, notes: list) -> str:
    """Сортировка карточек: как разложили пятеро и что из этого следует."""
    groups = js_var(js, "GROUPS")
    cards = js_var(js, "CARDS")

    if not groups or not cards or 'id="csPool"' not in body:
        return body

    spread_text = js_phrase(js, r"verdict = '(Разброс[^']*)'")
    move_text = js_phrase(js, r"verdict = '(Люди кладут в «)'") + "{group}" + js_phrase(js, r"t\.g \+ '([^']*)'; flag = '<span class=\"flag\">менять")
    agree_text = js_phrase(js, r"verdict = '(Согласие[^']*)'")
    split_text = js_phrase(js, r"verdict = '(Делится[^']*)'")
    flags = re.findall(r"flag = '<span class=\"flag\">([^<]*)</span>'", js)
    differs = js_phrase(js, r"<span class=\"dim\"[^>]*>((?:[^<])*)</span>' : ''")
    # Здесь из скрипта берётся не фраза, а кусок разметки таблицы: проверка на обломки
    # кода к нему не применима, поэтому читаем напрямую.
    table_head = re.search(r"csRes\.innerHTML = '(.*?)</thead>", js, re.S)
    heads = re.findall(r"<th>([^<]*)</th>", table_head.group(1) if table_head else "")
    conclusion = re.search(r"'<div class=\"rule\"[^>]*>(.*?)</div>';", js, re.S)
    rows = []

    for one in cards:
        spread = one["p"]
        top = max(spread, key=lambda key: spread[key])
        chips = "".join(
            '<span class="mini{top}">{name} · {n}</span>'.format(top=" top" if name == top else "", name=name, n=n)
            for name, n in sorted(spread.items(), key=lambda kv: -kv[1])
        )

        if len(spread) >= 3:
            verdict, flag = spread_text, flags[0] if flags else ""
        elif top != one["ours"]:
            verdict, flag = move_text.replace("{group}", top), flags[1] if len(flags) > 1 else ""
        elif spread[top] >= 4:
            verdict, flag = agree_text, ""
        else:
            verdict, flag = split_text, flags[2] if len(flags) > 2 else ""

        rows.append(
            '<tr data-sort-card data-sort-top="{top}"><td><b>{text}</b></td><td data-sort-mine hidden></td>'
            "<td>{chips}</td><td>{verdict}{flag}"
            '<span class="dim" data-sort-differs hidden><br>{differs}</span></td></tr>'.format(
                top=html.escape(top, quote=True),
                text=one["t"],
                chips=chips,
                verdict=verdict,
                flag=' <span class="flag">%s</span>' % flag if flag else "",
                differs=differs,
            )
        )

    if len(heads) < 4:
        heads = ["Карточка", "Ваш вариант", "Как разложили пятеро", "Итог"]

    table = (
        '<div class="tbl-scroll"><table><thead><tr><th>{h0}</th><th data-sort-mine hidden>{h1}</th>'
        "<th>{h2}</th><th>{h3}</th></tr></thead><tbody>{rows}</tbody></table></div>"
    ).format(h0=heads[0], h1=heads[1], h2=heads[2], h3=heads[3], rows="".join(rows))
    rule = '<div class="rule">' + conclusion.group(1).replace("\\'", "'") + "</div>" if conclusion else ""
    words = {
        "count": "Разложено {n} из {total}",
        "empty": js_phrase(js, r"d\.textContent = '([^']*)'", "Все карточки разложены."),
        "none": js_phrase(js, r"e\.textContent = '([^']*)'", "пусто"),
        "back": js_phrase(js, r"pb\.title = '([^']*)'", "Вернуть в стопку"),
        "show": js_phrase(body, r'id="csShow"[^>]*>([^<]*)</button>', "Показать"),
        "reset": js_phrase(body, r'id="csReset"[^>]*>([^<]*)</button>', "Заново"),
        "groups": "|".join(groups),
    }
    attrs = "".join(' data-sort-%s="%s"' % (key, html.escape(value, quote=True)) for key, value in words.items())
    body = body.replace(
        '<div class="cs-pool" id="csPool"></div>',
        '<div data-sort' + attrs + '><div class="cs-pool" data-sort-pool hidden></div>',
        1,
    )
    body = body.replace('<div class="cs-groups" id="csGroups"></div>', '<div class="cs-groups" data-sort-groups hidden></div>', 1)
    body = re.sub(
        r'<div class="tt-bar">\s*<button[^>]*id="csShow"[^>]*>.*?</button>\s*<button[^>]*id="csReset"[^>]*>.*?</button>\s*</div>',
        '<div class="tt-bar" data-sort-actions></div>',
        body,
        count=1,
        flags=re.S,
    )
    body = body.replace(
        '<div class="cs-res" id="csRes"></div>', '<div class="cs-res" data-sort-result>' + table + rule + "</div></div>", 1
    )
    body = re.sub(r'<span class="hunt-count" id="csCount">[^<]*</span>', '<span class="hunt-count" data-sort-count-out></span>', body)
    notes.append("сортировка карточек: карточек {}, разделов {}".format(len(cards), len(groups)))

    return body


def tree_markup(js: str, body: str, notes: list) -> str:
    """Проверка дерева: разделы, верный путь и что сделали пятеро."""
    tree = js_var(js, "TREE")
    right = js_var(js, "RIGHT")
    people = js_var(js, "PEOPLE")

    if not tree or not right or not people or 'id="ttList"' not in body:
        return body

    nested = "".join(
        "<li><b>{name}</b><ul>{kids}</ul></li>".format(name=name, kids="".join("<li>" + kid + "</li>" for kid in kids))
        for name, kids in tree.items()
    )
    verdicts = re.search(
        r"\(ok \? \(direct \? '((?:[^'\\]|\\.)*)' : '((?:[^'\\]|\\.)*)'\)\s*:\s*'((?:[^'\\]|\\.)*)'\)", js, re.S
    )
    metrics = re.search(r"'(<div class=\"metrics\">'.*?'</div>') \+\s*\n\s*'<div class=\"tbl-scroll\"", js, re.S)
    conclusion = re.search(r"'(<p style=\"margin-bottom:0\"><b>Вывод\.</b>.*?</p>)';", js, re.S)
    heads = re.findall(r"<th>([^<]*)</th>", js_phrase(js, r"(<table><thead><tr><th>Кто.*?</thead>)"))
    done_word = js_phrase(js, r"\(p\.ok \? '([^']*)'", "дошёл")
    miss_word = js_phrase(js, r"\(p\.ok \? '[^']*' : '([^']*)'\)", "не дошёл")
    person = js_phrase(js, r"'<tr><td><b>(Человек )'", "Человек ")
    rows = "".join(
        '<tr><td><b>{who}{n}</b></td><td class="path">{path}</td><td>{end} — {note}</td></tr>'.format(
            who=person, n=one["n"], path=one["path"], end=done_word if one["ok"] else miss_word, note=one["note"]
        )
        for one in people
    )

    if len(heads) < 3:
        heads = ["Кто", "Путь", "Чем кончилось"]

    mine = ""

    if verdicts:
        mine = (
            '<p data-tree-mine hidden><b class="h">{title}<span class="path" data-tree-path></span></b> '
            '<span data-tree-verdict="direct" hidden>{a}</span><span data-tree-verdict="back" hidden>{b}</span>'
            '<span data-tree-verdict="miss" hidden>{c}</span></p>'
        ).format(
            title=js_phrase(js, r"'<b class=\"h\">(Ваш путь: )<span", "Ваш путь: "),
            a=verdicts.group(1).replace("\\'", "'"),
            b=verdicts.group(2).replace("\\'", "'"),
            c=verdicts.group(3).replace("\\'", "'"),
        )

    result = (
        mine
        + (js_string(metrics.group(1)) if metrics else "")
        + '<div class="tbl-scroll"><table><thead><tr><th>{0}</th><th>{1}</th><th>{2}</th></tr></thead>'.format(*heads)
        + "<tbody>" + rows + "</tbody></table></div>"
        + (conclusion.group(1).replace("\\'", "'") if conclusion else "")
    )
    words = {
        "right": "|".join(right),
        "root": js_phrase(body, r'id="ttCrumb">([^<]*)<', "Вы в корне: выберите раздел"),
        "in": js_phrase(js, r"\? '(Вы в разделе: )'", "Вы в разделе: "),
        "done": js_phrase(js, r"ttCrumb\.textContent = '(Ответ записан)'", "Ответ записан"),
        "clicks": js_phrase(js, r"ttCount\.textContent = '(Кликов: )'", "Кликов: "),
        "leaf": js_phrase(js, r"\(leaf \? '([^']*)'", "искать здесь"),
        "kids": js_phrase(js, r"\.length \+ '([^']*)'\)", " раздела"),
        "back": js_phrase(body, r'id="ttBack"[^>]*>([^<]*)</button>', "На уровень выше"),
        "reset": js_phrase(body, r'id="ttReset"[^>]*>([^<]*)</button>', "Начать заново"),
    }
    attrs = "".join(' data-tree-%s="%s"' % (key, html.escape(value, quote=True)) for key, value in words.items())
    body = re.sub(r'<div class="tt-crumb" id="ttCrumb">[^<]*</div>', '<div class="tt-crumb" data-tree-crumb hidden></div>', body)
    body = body.replace(
        '<div class="tt-list" id="ttList"></div>',
        '<div data-tree' + attrs + '><ul class="tt-tree" data-tree-source>' + nested + '</ul><div class="tt-list" data-tree-list hidden></div>',
        1,
    )
    body = re.sub(
        r'<div class="tt-bar">\s*<button[^>]*id="ttBack"[^>]*>.*?</button>\s*<button[^>]*id="ttReset"[^>]*>.*?</button>\s*</div>',
        '<div class="tt-bar" data-tree-actions></div>',
        body,
        count=1,
        flags=re.S,
    )
    body = body.replace('<div class="tt-res" id="ttRes"></div>', '<div class="tt-res" data-tree-result>' + result + "</div></div>", 1)
    body = re.sub(r'<span class="hunt-count" id="ttCount">[^<]*</span>', '<span class="hunt-count" data-tree-count-out></span>', body)
    notes.append("проверка дерева: разделов {}, участников {}".format(len(tree), len(people)))

    return body


def wiz_markup(js: str, body: str, notes: list) -> str:
    """Стресс-тест: шесть будущих разделов, три вопроса правила и вердикт по каждому."""
    questions = js_var(js, "WQ")
    cases = js_var(js, "CASES")

    if not questions or not cases or 'id="wizCases"' not in body:
        return body

    keys = re.findall(r"<span class=\"k\">([^<]*)</span><span class=\"v\">(?:<b>)?' \+ cur\.(\w+)", js)
    labels = {field: label for label, field in keys} or {"where": "Куда встаёт", "breaks": "Что ломается", "todo": "Решить заранее"}
    asks = "".join(
        '<li data-wiz-q="{q}">{opts}</li>'.format(
            q=html.escape(one["q"], quote=True),
            opts="".join('<span data-wiz-opt="%s">%s</span>' % (opt["k"], opt["l"]) for opt in one["opts"]),
        )
        for one in questions
    )
    blocks = []

    for one in cases:
        steps = []

        for n, answer in enumerate(one["a"]):
            option = next((opt["l"] for opt in questions[n]["opts"] if opt["k"] == answer), answer)
            steps.append(
                '<li data-wiz-step><p class="qt">{q}</p><p class="qfb"><b>{option}.</b> '
                "<span data-wiz-fb>{fb}</span></p></li>".format(q=questions[n]["q"], option=option.rstrip("."), fb=one["fb"][n])
            )

        verdict = "".join(
            '<div class="vr"><span class="k">{label}</span><span class="v">{text}</span></div>'.format(
                label=labels.get(field, field), text=("<b>" + one[field] + "</b>") if field == "where" else one[field]
            )
            for field in ("where", "breaks", "todo")
            if one.get(field)
        )
        blocks.append(
            '<details class="wiz-case" name="wiz" data-wiz-case="{id}" data-wiz-answers="{answers}">'
            "<summary>{title}</summary><ol>{steps}</ol>"
            '<div class="verdict" data-wiz-verdict>{verdict}</div></details>'.format(
                id=one["id"], answers=",".join(one["a"]), title=one["t"], steps="".join(steps), verdict=verdict
            )
        )

    words = {
        "count": "Разобрано {n} из {total}",
        "right": js_phrase(js, r"\? '(Так и есть\. )'", "Так и есть. "),
        "wrong": js_phrase(js, r": '(По правилам[^']*)'\)", "По правилам — другой ответ. "),
        "again": js_phrase(js, r"btn\.textContent = '([^']*)'", "Пройти этот случай заново"),
    }
    attrs = "".join(' data-wiz-%s="%s"' % (key, html.escape(value, quote=True)) for key, value in words.items())
    body = body.replace(
        '<div class="cases" id="wizCases"></div>',
        '<div data-wiz' + attrs + '><ol data-wiz-questions hidden>' + asks + '</ol><div class="cases" data-wiz-cases hidden></div>',
        1,
    )
    body = re.sub(
        r'<div class="wiz" id="wizBody">(.*?)</div>',
        lambda m: '<div class="wiz" data-wiz-body hidden>' + m.group(1) + "</div>"
        + '<div class="wiz-list" data-wiz-list>' + "".join(blocks) + "</div></div>",
        body,
        count=1,
        flags=re.S,
    )
    body = re.sub(r'<span class="hunt-count" id="wizCount">[^<]*</span>', '<span class="hunt-count" data-wiz-count-out></span>', body)
    notes.append("стресс-тест: случаев {}, вопросов {}".format(len(cases), len(questions)))

    return body


# ---------------------------------------------------------------------------
# Живые куски темы «Опросы»: столбики результатов, симулятор смещения отклика,
# калькулятор долей, разметка вариантов ответа, справочник шкал, калькулятор
# «вилки» и разбор чужого отчёта.
# ---------------------------------------------------------------------------


def vy_text(phrase: str) -> str:
    """Фраза из её скрипта с обращением на «вы».

    Текст внутри атрибутов `data-*` общая замена обращения не видит: она идёт по тексту
    между тегами. Поэтому всё, что переезжает из скрипта в атрибут, переводится здесь.
    """
    kept = len(SELF_REPORT)
    out = to_vy(steps_and_odd(phrase, []), [], set())
    del SELF_REPORT[kept:]

    return out


def vy_attr(phrase: str) -> str:
    return html.escape(vy_text(phrase), quote=True)


def bar_row(name: str, count: int, total: int, width: int = None, of: str = "из") -> str:
    share = round(count / total * 100) if total else 0

    return (
        '<div class="brow"><div class="blab"><span class="t">{name}</span>'
        '<span class="v">{count} {of} {total} · {share} %</span></div>'
        '<div class="btrack"><span class="bfill" style="width:{width}%"></span></div></div>'
    ).format(name=name, count=count, of=of, total=total, share=share, width=share if width is None else width)


def bars_markup(body: str, notes: list) -> str:
    """Столбики, заданные данными (`data-bars`), рисуются сразу разметкой: скрипт им не нужен."""
    count = 0

    def one(found):
        nonlocal count
        tag = found.group(0)
        data = re.search(r"data-bars='([^']*)'", tag)
        total = re.search(r'data-total="(\d+)"', tag)

        if not data or not total:
            return tag

        rows = json.loads(html.unescape(data.group(1)))
        whole = int(total.group(1))
        # При множественном выборе ширина считается от самого частого варианта, доля — от числа ответивших.
        top = max(n for _, n in rows) if "data-multi" in tag else whole
        count += 1

        return '<div class="bars">' + "".join(
            bar_row(name, n, whole, round(n / top * 100) if top else 0) for name, n in rows
        ) + "</div>"

    body = re.sub(r'<div class="bars" data-bars=[^>]*></div>', one, body)

    if count:
        notes.append("диаграмм из данных нарисовано разметкой: " + str(count))

    return body


def plural_people(n: int) -> str:
    a, b = n % 10, n % 100

    if a == 1 and b != 11:
        return "человек"

    if 2 <= a <= 4 and not 12 <= b <= 14:
        return "человека"

    return "человек"


def bias_sim_markup(js: str, body: str, notes: list) -> str:
    """Симулятор смещения отклика: вся аудитория и те, кто ответил.

    Модель у неё детерминированная — свой генератор с фиксированным зерном. Конвертер
    повторяет его и кладёт в разметку обе картины с готовыми числами; скрипт сайта по тем
    же параметрам рисует только сетку точек.
    """
    if 'id="pplGrid"' not in body:
        return body

    size = re.search(r"var N = (\d+), ANS = (\d+);", js)
    seed0 = re.search(r"var seed = (\d+);", js)
    moods = re.search(r"r < ([\d.]+) \? 'angry' : \(r < ([\d.]+) \? 'happy'", js)
    chance = re.search(r"chance = \{ angry: ([\d.]+), happy: ([\d.]+), neutral: ([\d.]+) \}", js)

    if not (size and seed0 and moods and chance):
        notes.append("симулятор отклика: параметры модели не найдены — оставлен как есть")

        return body

    total, quota = int(size.group(1)), int(size.group(2))
    state = int(seed0.group(1))
    edge_angry, edge_happy = float(moods.group(1)), float(moods.group(2))
    odds = {"angry": float(chance.group(1)), "happy": float(chance.group(2)), "neutral": float(chance.group(3))}

    def rnd():
        nonlocal state
        state = (state * 9301 + 49297) % 233280

        return state / 233280

    people = []

    for _ in range(total):
        roll = rnd()
        people.append(["angry" if roll < edge_angry else ("happy" if roll < edge_happy else "neutral"), False])

    answered = 0

    for one in people:
        if answered >= quota:
            break

        if rnd() < odds[one[0]]:
            one[1] = True
            answered += 1

    def counts(group):
        return {mood: sum(1 for one in group if one[0] == mood) for mood in ("angry", "happy", "neutral")}

    everyone = counts(people)
    replied = counts([one for one in people if one[1]])
    labels = re.search(r"\[\['([^']*)', c\.angry[^\]]*\], \['([^']*)', c\.happy[^\]]*\], \['([^']*)', c\.neutral", js)
    names = labels.groups() if labels else ("Недовольны", "Довольны", "Всё нормально")
    legend = re.findall(r"</i> ([^<]+)</span>", js)
    titles = (
        js_phrase(js, r": '(Все пользователи: )'", "Все пользователи: "),
        js_phrase(js, r"\? '(Только те, кто ответил: )'", "Только те, кто ответил: "),
    )
    text_all = js_phrase(js, r": '(Так устроена аудитория[^']*)'\)")
    share_replied = round(replied["angry"] / answered * 100) if answered else 0
    share_all = round(everyone["angry"] / total * 100)
    ratio = share_replied / share_all if share_all else 0
    word = "втрое" if ratio >= 2.6 else ("вдвое" if ratio >= 1.7 else "заметно")
    tail = js_phrase(js, r"' \+ word \+ '([^']*)'")
    text_replied = (
        "Среди ответивших недовольных — {a} %. Среди всех пользователей их {b} %. "
        "В этой учебной модели доля недовольных среди ответивших {word}{tail}"
    ).format(a=share_replied, b=share_all, word=word, tail=tail)

    for phrase in ("'Среди ответивших недовольных — '", "' %. Среди всех пользователей их '", "' %. В этой учебной модели доля недовольных среди ответивших '"):
        if phrase not in js:
            notes.append("симулятор отклика: текст вывода в скрипте изменился — " + phrase)

            return body

    def view(key, title, group, whole, text, extra_legend):
        marks = [("is-angry", legend[0] if legend else "недовольны"), ("is-happy", legend[1] if len(legend) > 1 else "довольны"),
                 ("is-answered" if key == "ans" else "is-plain", legend[2] if len(legend) > 2 else "всё нормально")]

        if extra_legend:
            marks.append(("is-silent", legend[3] if len(legend) > 3 else "не ответили"))

        return (
            '<div class="bias-view" data-bias-view="{key}"><p class="bias-title"><b>{title}{n} {people}</b></p>'
            '<div class="legend2">{legend}</div><div class="bars">{bars}</div><p class="dim">{text}</p></div>'
        ).format(
            key=key,
            title=title,
            n=whole,
            people=plural_people(whole),
            legend="".join('<span><i class="%s"></i> %s</span>' % pair for pair in marks),
            bars="".join(bar_row(names[i], group[mood], whole) for i, mood in enumerate(("angry", "happy", "neutral"))),
            text=text,
        )

    views = view("all", titles[0], everyone, total, text_all, False) + view("ans", titles[1], replied, answered, text_replied, True)
    buttons = dict(re.findall(r'id="sim(All|Ans)"[^>]*>([^<]+)</button>', body))
    params = (
        ' data-bias data-bias-n="{n}" data-bias-quota="{q}" data-bias-seed="{s}" data-bias-angry="{a}" data-bias-happy="{h}"'
        ' data-bias-odds="{oa},{oh},{on}" data-bias-all="{ball}" data-bias-ans="{bans}"'
    ).format(
        n=total, q=quota, s=seed0.group(1), a=edge_angry, h=edge_happy, oa=odds["angry"], oh=odds["happy"], on=odds["neutral"],
        ball=vy_attr(buttons.get("All", "Все пользователи")), bans=vy_attr(buttons.get("Ans", "Кто ответил")),
    )
    body = re.sub(r'<button[^>]*id="simAll"[^>]*>.*?</button>\s*', "<span data-bias-actions></span>", body, flags=re.S)
    body = re.sub(r'<button[^>]*id="simAns"[^>]*>.*?</button>\s*', "", body, flags=re.S)
    body = body.replace('<div class="ppl" id="pplGrid"></div>', '<div class="ppl"' + params + ' aria-hidden="true" hidden></div>', 1)
    body = re.sub(r'\s*<div class="legend2" id="pplLegend"></div>', "", body)
    body = re.sub(r'<div id="pplOut"[^>]*></div>', '<div data-bias-views>' + views + "</div>", body, count=1)
    notes.append(
        "симулятор отклика: всего {}, ответили {}, недовольных {} % против {} %".format(total, answered, share_replied, share_all)
    )

    return body


def share_calc_markup(js: str, body: str, notes: list) -> str:
    """Калькулятор долей: варианты, количества, столбики и готовые строки для отчёта."""
    rows = js_var(js, "DEF")

    if not rows or 'id="calcRows"' not in body:
        return body

    total = sum(n for _, n in rows)
    placeholder = js_phrase(js, r'placeholder="(Вариант )\' \+', "Вариант ")
    fields = "".join(
        '<div class="calcrow" data-share-row><input type="text" value="{name}" placeholder="{ph}{i}" aria-label="{ph}{i}" data-share-name>'
        '<input type="number" min="0" step="1" value="{n}" aria-label="{count} {i}" data-share-count>'
        '<span class="res" data-share-part>{part}</span></div>'.format(
            name=html.escape(name, quote=True), ph=placeholder, i=index, n=n or "", count="Человек, вариант",
            part=(str(round(n / total * 100)) + " %") if name and total else "",
        )
        for index, (name, n) in enumerate(rows, 1)
    )
    filled = [(name, n) for name, n in rows if name]
    lines = "\n".join("{} — {} из {} ({} %)".format(name, n, total, round(n / total * 100)) for name, n in filled)
    total_line = js_phrase(js, r"'\\n\\n(Всего ответили на вопрос: )' \+ total \+ '([^']*)'", "Всего ответили на вопрос: ")
    total_tail = re.search(r"Всего ответили на вопрос: ' \+ total \+ '([^']*)'", js)
    empty = js_phrase(js, r": '(Впиши варианты[^']*)'")
    attrs = (
        ' data-share data-share-line="{{name}} — {{n}} из {{total}} ({{p}} %)" data-share-total="{total}{{total}}{tail}"'
        ' data-share-empty="{empty}" data-share-of="из"'
    ).format(total=vy_attr(total_line), tail=vy_attr(total_tail.group(1) if total_tail else " человек"), empty=vy_attr(empty))
    body = body.replace('<div id="calcRows"></div>', '<div class="share-rows" data-share-rows>' + fields + "</div>", 1)
    body = re.sub(
        r'(<div class="box-body")(>\s*<div class="calcrow"><span class="calchd">)', lambda m: m.group(1) + attrs + m.group(2), body, count=1
    )
    body = re.sub(r'(<span class="res" id="calcTotal"[^>]*>)0(</span>)', lambda m: m.group(1) + str(total) + m.group(2), body, count=1)
    body = body.replace(
        '<div class="bars" id="calcBars"></div>',
        '<div class="bars" id="calcBars" data-share-bars>' + "".join(bar_row(name, n, total) for name, n in filled) + "</div>",
        1,
    )
    body = body.replace(
        '<div class="lines" id="calcLines"></div>',
        '<div class="lines" id="calcLines" data-share-lines>' + lines + "\n\n"
        + vy_text(total_line) + str(total) + vy_text(total_tail.group(1) if total_tail else " человек") + "</div>",
        1,
    )
    body = re.sub(r'<button[^>]*id="calcReset"[^>]*>(.*?)</button>', lambda m: '<span data-share-actions data-share-reset="%s"></span>' % vy_attr(m.group(1).strip()), body, count=1, flags=re.S)
    notes.append("калькулятор долей: строк {}, всего {}".format(len(rows), total))

    return body


def optmark_markup(js: str, body: str, notes: list) -> str:
    """Разметка вариантов ответа: какие поломаны и чего в списке не хватает."""
    options = js_var(js, "OPTS")

    if not options or 'id="optList"' not in body:
        return body

    fine = js_phrase(js, r"checked \? '(С этим вариантом всё в порядке[^']*)'")
    rows = "".join(
        '<li data-opt="{bad}"{cls}><span class="opt-name" data-opt-name>{text}</span>'
        '<span class="opt-why" data-opt-why>{why}</span></li>'.format(
            bad="1" if one["bad"] else "0", cls=' class="is-bad"' if one["bad"] else "", text=one["t"], why=one["why"]
        )
        for one in options
    )
    fix = re.search(r"fix\.innerHTML = (.*?);\n", js, re.S)
    total = sum(1 for one in options if one["bad"])
    words = {
        "count": js_phrase(js, r"\? '' : '(отмечено: )' \+ n", "отмечено: ") + "{n}",
        "hint": js_phrase(js, r"meta\.innerHTML = '<span>([^<]*)</span>';"),
        "found": js_phrase(js, r"<span style=\"color:var\(--bad\)\">([^']*)' \+ hit", "Нашёл поломок: ") + "{hit}" + js_phrase(js, r"\+ hit \+ '([^<]*)</span>'", " из 3"),
        "extra": js_phrase(js, r"<span style=\"color:var\(--muted\)\">([^']*)' \+ wrong", "Лишних отмечено: ") + "{wrong}",
        "missing": js_phrase(js, r"<span style=\"color:var\(--warn\)\">([^<]*)</span>'"),
        "fine": fine,
        "check": js_phrase(body, r'id="optCheck"[^>]*>([^<]*)</button>', "Проверить"),
        "again": js_phrase(js, r"checkB\.textContent = '(Ещё раз)'", "Ещё раз"),
    }
    # «Нашёл поломок» — это про читателя: с «вы» глагол стоит во множественном числе.
    words["found"] = words["found"].replace("Нашёл", "Нашли")
    attrs = "".join(' data-opt-%s="%s"' % (key, vy_attr(value)) for key, value in words.items())
    body = body.replace('<ul class="opt-list" id="optList"></ul>', '<ul class="opt-list" data-optmark data-opt-total="%d"%s>%s</ul>' % (total, attrs, rows), 1)
    body = re.sub(r'<div class="opt-meta" id="optMeta"></div>', '<div class="opt-meta" data-opt-meta hidden></div>', body, count=1)
    body = body.replace('<div class="opt-fix" id="optFix"></div>', '<div class="opt-fix" data-opt-fix>' + (js_string(fix.group(1)) if fix else "") + "</div>", 1)
    body = re.sub(r'<span[^>]*id="optCount"[^>]*></span>', "<span class=\"hunt-count\" data-opt-count-out></span>", body, count=1)
    body = re.sub(r'<button[^>]*id="optCheck"[^>]*>.*?</button>', "<span data-opt-actions></span>", body, count=1, flags=re.S)
    notes.append("разметка вариантов: вариантов {}, поломанных {}".format(len(options), total))

    return body


def scales_markup(js: str, body: str, notes: list) -> str:
    """Справочник шкал: семь типов вопроса, что каждый даёт и чего не даёт."""
    scales = js_var(js, "SCALES")

    if not scales or 'id="scTabs"' not in body:
        return body

    heads = re.findall(r"<h6>([^<]*)</h6>", js)
    can_title = heads[0] if heads else "Что потом сможете сделать"
    cant_title = heads[1] if len(heads) > 1 else "Чего не сможете"
    example = js_phrase(js, r"<b>(Пример:)</b>", "Пример:")
    watch = js_phrase(js, r"<p class=\"sc-warn\"><b>([^<]*)</b>", "На что смотреть:")
    buttons = "".join(
        '<button class="ds-switch__button" type="button" data-switch-btn="{k}" hidden>{n}</button>'.format(k=one["k"], n=one["n"])
        for one in scales
    )
    panes = "".join(
        '<div data-switch-pane="{k}" class="sc-card"><h5>{n}</h5>'
        '<div class="sc-ex"><b>{example}</b> {q}<div class="opts2">{o}</div></div>'
        '<div class="cmp-two"><div><h6>{can_title}</h6><ul>{can}</ul></div><div><h6>{cant_title}</h6><ul>{cant}</ul></div></div>'
        '<p class="sc-warn"><b>{watch}</b> {warn}</p></div>'.format(
            k=one["k"], n=one["n"], example=example, q=one["q"], o=one["o"], can_title=can_title, cant_title=cant_title,
            can="".join("<li>" + item + "</li>" for item in one["can"]),
            cant="".join("<li>" + item + "</li>" for item in one["cant"]),
            watch=watch, warn=one["warn"],
        )
        for one in scales
    )
    body = body.replace('<div class="sc-tabs" id="scTabs"></div>', '<div class="ds-switch__bar">' + buttons + "</div>", 1)
    body = body.replace('<div class="sc-body" id="scBody"></div>', '<div class="sc-body">' + panes + "</div>", 1)
    body = re.sub(r'<div class="box-body">(\s*<div class="ds-switch__bar">)', r'<div class="box-body ds-switch" data-switch>\1', body)
    notes.append("справочник шкал: типов вопроса " + str(len(scales)))

    return body


def fork_calc_markup(js: str, body: str, notes: list) -> str:
    """Калькулятор «вилки»: в каких пределах гуляет ответ, если неответившие думают иначе."""
    if 'id="bcBase"' not in body:
        return body

    start = {}

    for name in ("bcBase", "bcResp", "bcYes", "bcOther"):
        found = re.search(r'id="' + name + r'"[^>]*\bvalue="(\d+)"', body)

        if not found:
            return body

        start[name] = int(found.group(1))

    verdicts = re.search(
        r"\(width >= (\d+)\s*\?\s*'((?:[^'\\]|\\.)*)'\s*:\s*width >= (\d+)\s*\?\s*'((?:[^'\\]|\\.)*)'\s*:\s*'((?:[^'\\]|\\.)*)'\)", js, re.S
    )
    lead = re.search(r"say\.innerHTML = (.*?) \+\s*\n\s*\(width >= ", js, re.S)

    if not verdicts or not lead:
        notes.append("калькулятор вилки: тексты не разобраны — оставлен как есть")

        return body

    template = lead.group(1)

    for source, target in (
        ("R", "{R}"), ("N", "{N}"), ("respShare", "{share}"), ("asP", "{as}"), ("nonResp", "{non}"),
        ("Math.round(pO * 100)", "{po}"), ("lowP", "{low}"),
    ):
        template = re.sub(r"'\s*\+\s*" + re.escape(source) + r"\s*\+\s*'", target, template)

    template = js_string(template)
    words = {
        # В её разметке стоит «42 человека», а шаблон скрипта дал бы «42 человек»: слово склоняется
        # по числу, формы приезжают атрибутом. Поймано сверкой текста 17.09.2026.
        "yes": "{yes} {people}" + js_phrase(js, r"yesCount \+ ' человек([^']*)' \+ Math", " — это ") + "{p}" + js_phrase(js, r"pY \* 100\) \+ '([^']*)';", " % ответивших"),
        "people": "человек|человека|человек",
        "other": js_phrase(js, r"otherLab\.textContent = '([^']*)'", "сейчас: ") + "{p} %",
        "big": js_phrase(js, r"big\.textContent = '([^']*)' \+ lo", "От ") + "{lo}" + js_phrase(js, r"\+ lo \+ '([^']*)' \+ up", " % до ") + "{up}" + js_phrase(js, r"\+ up \+ '([^']*)';", " % по всей базе"),
        # Якорь — класс подписи: то же `asP + '` встречается выше, у самой отметки,
        # и без якоря в подпись уезжал кусок её разметки (`%">`).
        "point": "{p}" + js_phrase(js, r"class=\"ptlab\".*?asP \+ '([^'<]*)</span>'", " % в опросе"),
        "say": template,
        "wide": verdicts.group(2).replace("\\'", "'"),
        "mid": verdicts.group(4).replace("\\'", "'"),
        "narrow": verdicts.group(5).replace("\\'", "'"),
        "wide-from": verdicts.group(1),
        "mid-from": verdicts.group(3),
    }
    # Расчёт по значениям по умолчанию — та же формула, что в её скрипте.
    base, resp = max(1, start["bcBase"]), max(1, min(start["bcResp"], start["bcBase"]))
    p_yes, p_other = start["bcYes"] / 100, start["bcOther"] / 100
    yes_count = round(resp * p_yes)
    silent = base - resp
    low = round((yes_count + silent * p_other) / base * 100)
    high = round((yes_count + silent * p_yes) / base * 100)
    as_is = round(p_yes * 100)
    lo, up = min(low, high), max(low, high)
    width = up - lo
    verdict = words["wide"] if width >= int(words["wide-from"]) else (words["mid"] if width >= int(words["mid-from"]) else words["narrow"])
    filled = vy_text(words["say"])

    for key, value in (("{R}", resp), ("{N}", base), ("{share}", round(resp / base * 100)), ("{as}", as_is), ("{non}", silent), ("{po}", round(p_other * 100)), ("{low}", low)):
        filled = filled.replace(key, str(value))

    scale = (
        '<span class="axis"></span><span class="span" style="left:{lo}%;width:{w}%"></span><span class="pt" style="left:{a}%"></span>'
        '<span class="ptlab" style="left:{a}%">{point}</span><span class="tick" style="left:{lo}%">{lo} %</span>'
        '<span class="tick" style="left:{up}%">{up} %</span>'
    ).format(lo=lo, up=up, w=max(1, width), a=as_is, point=words["point"].replace("{p}", str(as_is)))
    attrs = "".join(' data-fork-%s="%s"' % (key, vy_attr(value)) for key, value in words.items())
    body = re.sub(r'<div class="bc-grid">', '<div class="bc-grid" data-fork' + attrs + ">", body, count=1)
    body = re.sub(r'(<span id="bcYesLab">)[^<]*(</span>)', lambda m: m.group(1) + words["yes"].replace("{yes}", str(yes_count)).replace("{people}", plural_people(yes_count)).replace("{p}", str(as_is)) + m.group(2), body, count=1)
    body = re.sub(r'(<span id="bcOtherLab">)[^<]*(</span>)', lambda m: m.group(1) + words["other"].replace("{p}", str(round(p_other * 100))) + m.group(2), body, count=1)
    body = re.sub(r'(<div class="bc-big" id="bcBig">)[^<]*(</div>)', lambda m: m.group(1) + words["big"].replace("{lo}", str(lo)).replace("{up}", str(up)) + m.group(2), body, count=1)
    body = body.replace('<div class="rng" id="bcRng"></div>', '<div class="rng" id="bcRng" aria-hidden="true">' + scale + "</div>", 1)
    body = body.replace('<div class="bc-say" id="bcSay"></div>', '<div class="bc-say" id="bcSay">' + filled + vy_text(verdict) + "</div>", 1)
    body = re.sub(r'<button[^>]*id="bcReset"[^>]*>(.*?)</button>', lambda m: '<span data-fork-actions data-fork-reset="%s"></span>' % vy_attr(m.group(1).strip()), body, count=1, flags=re.S)
    notes.append("калькулятор вилки: по умолчанию от {} % до {} %".format(lo, up))

    return body


def review_markup(js: str, body: str, notes: list) -> str:
    """Разбор чужого отчёта: вердикты и пояснения открываются кнопкой (готовый `data-reveal`)."""
    if 'id="revBtn"' not in body or 'id="repDoc"' not in body:
        return body

    show = js_phrase(body, r'id="revBtn"[^>]*>([^<]*)</button>', "Показать разбор")
    # Якорь — именно `textContent`: строкой выше стоит `next ? 'true' : 'false'`
    # для `aria-pressed`, и без якоря подписью кнопки становилось слово «true».
    hide = js_phrase(js, r"textContent = next \? '([^']*)'", "Скрыть разбор")
    box = [m for m in re.finditer(r'<div class="box">', body[:body.index('id="revBtn"')])]

    if not box:
        return body

    at = box[-1].start()
    body = body[:at] + '<div class="box" data-reveal data-reveal-show="%s" data-reveal-hide="%s">' % (vy_attr(show), vy_attr(hide)) + body[at + len('<div class="box">'):]
    body = re.sub(r'<button[^>]*id="revBtn"[^>]*>.*?</button>', "<span data-reveal-button></span>", body, count=1, flags=re.S)
    body, verdicts = re.subn(r'(<span class="vd [a-z]+")>', r"\1 data-reveal-item>", body)
    body, texts = re.subn(r'(<(?:p|div) class="note")', r"\1 data-reveal-item", body)
    notes.append("разбор отчёта: вердиктов {}, пояснений {}".format(verdicts, texts))

    return body


def checklist_markup(js: str, body: str, notes: list) -> str:
    """Чек-лист со счётчиком: опоры для скрипта и фразы итога — из её урока.

    Фразы у каждого урока свои («можно проводить», «можно рассылать»), поэтому они
    приезжают атрибутами, а не лежат в скрипте темы.
    """
    for prefix in ("prep", "pil"):
        if 'id="' + prefix + 'List"' not in body:
            continue

        words = re.search(r"\(n === boxes\.length \? '([^']*)' : '([^']*)'\)", js)
        done, going = (words.group(1), words.group(2)) if words else ("", "")
        body = body.replace('id="' + prefix + 'List"', "data-checklist", 1)
        body = body.replace('id="' + prefix + 'Prog"', "data-checklist-fill", 1)
        body = body.replace(
            'id="' + prefix + 'St"',
            'data-checklist-state data-checklist-done="%s" data-checklist-going="%s"' % (vy_attr(done), vy_attr(going)),
            1,
        )
        notes.append("чек-лист: итог «" + done.strip(" —") + "»")

    return body


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
    нас нет, и задают размеры в пикселях мимо шкалы. Остаются данные, а не оформление:
    доля куска на ленте времени (`flex:5`), место точки на схеме (`left:4.1%; top:33%`)
    и `display:none`, который превращается в атрибут `hidden`. Внутри SVG стиль не
    снимается, а переводится на токены сайта: там он задаёт цвет самих фигур.
    """
    kept = []
    dropped = []
    lost = set()
    data_rule = re.compile(r"(?:flex:\s*\d+|(?:left|top|width):\s*[\d.]+%)")

    def one(match):
        rules = [r.strip() for r in match.group(1).split(";") if r.strip()]
        keep = [r for r in rules if data_rule.fullmatch(r)]
        hide = any(r.replace(" ", "") == "display:none" for r in rules)

        for rule in rules:
            if rule not in keep and rule.replace(" ", "") != "display:none":
                dropped.append(rule)

        out = ""

        if keep:
            kept.extend(keep)
            out += ' style="' + "; ".join(keep) + '"'

        if hide:
            out += " hidden"

        return out

    parts = re.split(r"(<svg\b.*?</svg>)", text, flags=re.S)
    svgs = 0

    for n, part in enumerate(parts):
        if part.startswith("<svg"):
            parts[n] = svg_tokens(part, lost)
            svgs += 1
        else:
            parts[n] = re.sub(r'\s*style="([^"]*)"', one, part)

    if dropped:
        notes.append("инлайновых объявлений снято: " + str(len(dropped)))

    if kept:
        notes.append("данных в стиле сохранено (доли и точки): " + str(len(kept)))

    if svgs:
        notes.append("схем SVG переведено на токены: " + str(svgs))

    if lost:
        notes.append("в SVG остались неизвестные переменные: " + ", ".join(sorted(lost)))

    return "".join(parts)


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
source_body = body

# Тренажёр в уроках собран двумя способами: массивом QS (первая тема) и вызовами
# makeDrill (все остальные). Оба разворачиваются в одну и ту же нашу разметку.
quizzes = 0
yes, no = quiz_labels(raw)
pairs = [{"key": "1", "label": yes}, {"key": "0", "label": no}]
keyed = [
    {"text": one["text"], "answer": "1" if one["good"] else "0", "feedback": one["feedback"]}
    for one in items
]

body, quiz_ok = put_quiz(body, keyed, pairs, "quiz")
quizzes += 1 if quiz_ok else 0

for drill in drills_of(raw):
    body, ok = put_quiz(body, drill["items"], drill["options"], drill["node"])
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
body = bars_markup(body, widget_notes)
body = bias_sim_markup(script, body, widget_notes)
body = share_calc_markup(script, body, widget_notes)
body = optmark_markup(script, body, widget_notes)
body = scales_markup(script, body, widget_notes)
body = fork_calc_markup(script, body, widget_notes)
body = review_markup(script, body, widget_notes)
body = checklist_markup(script, body, widget_notes)
body = tabs_to_switch(body, widget_notes)
body = seq_markup(script, body, widget_notes)
body = hunt_markup(script, body, widget_notes)
body = sort_markup(script, body, widget_notes)
body = tree_markup(script, body, widget_notes)
body = wiz_markup(script, body, widget_notes)
body = accs_to_details(body, widget_notes)
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

# Сверка: её текст не должен пропадать. Каждый кусок текста из присланной разметки
# прогоняется через те же замены, что и тело, и ищется в готовом теле. Не нашёлся —
# значит, конвертер его выбросил. До 17.09.2026 так молча пропадали заголовок и
# подсказка каждого тренажёра: коробка заменялась целиком, а сверки не было.
def squash(text: str) -> str:
    """Текст для сравнения: без тегов, с одним пробелом и без пробелов у знаков препинания.

    Ссылка на каталог ставит тег посреди фразы, и на его месте после снятия тегов
    остаётся пробел перед точкой с запятой — сравнивать надо без таких пробелов.
    """
    text = " ".join(re.sub(r"<[^>]+>", " ", html.unescape(text)).split())
    text = re.sub(r"\s+([,.;:!?»)])", r"\1", text)

    return re.sub(r"([«(])\s+", r"\1", text)


kept_report = len(SELF_REPORT)
final_text = squash(body)
# Подписи кнопок и подсказки упражнений переезжают в атрибуты `data-*`: это не потеря.
final_attrs = html.unescape(" ".join(re.findall(r'="([^"]*)"', body)))
lost = []

for piece in re.split(r"<[^>]+>", re.sub(r"<(script|style|svg)\b.*?</\1>", " ", source_body, flags=re.S)):
    piece = " ".join(html.unescape(piece).split())

    if len(piece) < 25:
        continue

    same = squash(to_vy(steps_and_odd(piece, []), [], set()))

    if same not in final_text and same not in final_attrs:
        lost.append(piece)

del SELF_REPORT[kept_report:]
if PHRASE_REPORT:
    print("фраз из скрипта взято не то (использован запасной текст):", len(PHRASE_REPORT))
    for line in PHRASE_REPORT:
        print("  ✕", line)

print("её текст, не дошедший до тела:", len(lost))
for piece in lost:
    print("  ✕", piece[:150])

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
