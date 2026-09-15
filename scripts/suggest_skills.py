"""Предлагает навыки карты компетенций для записей каталога.

Тема задаёт область, слова в названии и вердикте уточняют навык. Предложение — черновик:
его проверяет человек, а применяет `scripts/apply_skills.php`. Так 140 записей размечаются
за один проход, а не открываются по одной.

    wp eval-file scripts/export_resources.php C:/.../.tmp/resources.json
    python scripts/suggest_skills.py
    python scripts/suggest_skills.py --show   # печатает таблицу для вычитки
"""
import argparse
import io
import json
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

p = argparse.ArgumentParser()
p.add_argument("--src", default=".tmp/resources.json")
p.add_argument("--out", default=".tmp/skills-assign.json")
p.add_argument("--show", action="store_true", help="напечатать таблицу для вычитки")
a = p.parse_args()

# Тема каталога → навыки, которые она обычно закрывает. Первый навык — запасной:
# он ставится, если по словам ничего точнее не нашлось.
BY_TOPIC = {
    "ux-research": ["user-interviews", "usability-testing", "surveys-data", "competitor-analysis"],
    "prototyping": ["wireframes-prototype", "flows-structure"],
    "ui-visual": ["layout-grid", "patterns-states", "color-contrast"],
    "typography": ["typography"],
    "icons-illustrations": ["icons-illustration"],
    "design-systems": ["components-variants", "tokens-themes", "ds-documentation"],
    "mobile-design": ["platform-guidelines", "responsive"],
    "web-landings": ["landings", "responsive"],
    "accessibility": ["keyboard-screenreader", "sizes-zoom", "color-contrast"],
    "analytics-metrics": ["validation-metrics", "task-constraints"],
    "ai-for-designers": ["ai-tools"],
    "career-portfolio": ["portfolio-interview", "planning", "mentoring"],
}

# Слово в названии или вердикте → навык. Слова в нижнем регистре, проверяется вхождение.
BY_WORD = {
    "user-interviews": ["интервью", "jtbd", "кастдев", "custdev"],
    "usability-testing": ["юзабилити", "usability", "тестирован", "эвристик"],
    "surveys-data": ["опрос", "анкет", "статистик", "количествен"],
    "competitor-analysis": ["конкурент", "аналог", "бенчмарк"],
    "flows-structure": ["сценари", "поток", "архитектур", "навигац", "cjm", "путь польз"],
    "wireframes-prototype": ["прототип", "вайрфрейм", "кликабельн"],
    "layout-grid": ["сетк", "композиц", "отступ", "раскладк", "layout", "grid"],
    "typography": ["типографик", "шрифт", "кегл", "гарнитур", "font", "кириллиц"],
    "color-contrast": ["цвет", "контраст", "палитр", "тёмная тема", "темная тема"],
    "patterns-states": ["паттерн", "состояни", "чеклист", "тёмные паттерн"],
    "motion": ["анимац", "движени", "motion", "переход"],
    "icons-illustration": ["иконк", "иллюстрац", "пиктограм", "icon", "illustration"],
    "brand-language": ["бренд", "айдентик", "фирменн", "логотип", "визуальн язык"],
    "tables-lists": ["таблиц", "список данн", "дата-грид"],
    "forms": ["форма", "формы", "форме", "формах", "поле ввод", "валидац"],
    "dashboards": ["дашборд", "визуализац данн", "диаграмм", "инфографик"],
    "ui-copy": ["текст в интерфейс", "тексты интерфейс", "редактур", "копирайт", "формулировк", "пиши, сокращай", "инфостил"],
    "errors-empty-states": ["ошибк", "пустое состояни", "пустых состояни"],
    "components-variants": ["компонент", "библиотек компонент", "атомарн"],
    "tokens-themes": ["токен", "переменн", "variables", "тёмная тема", "светлая тема"],
    "ds-documentation": ["документац", "гайдлайн систем", "storybook"],
    "platform-guidelines": ["ios", "android", "material", "human interface", "гайдлайн"],
    "responsive": ["адаптив", "брейкпоинт", "мобильн верс", "responsive"],
    "landings": ["лендинг", "промо", "посадочн"],
    "sizes-zoom": ["размер цел", "увеличени шрифт", "тап"],
    "keyboard-screenreader": ["клавиатур", "скринридер", "screen reader", "aria", "семантик"],
    "task-constraints": ["бизнес-задач", "ограничени", "постановк задач", "бриф"],
    "validation-metrics": ["метрик", "гипотез", "аналитик", "конверси", "a/b", "эксперимент"],
    "handoff": ["разработчик", "передач", "handoff", "вёрстк", "верстк"],
    "design-review": ["ревью", "разбор работ", "критик"],
    "defending-decisions": ["защит решени", "презентац решени", "аргумент"],
    "facilitation": ["воркшоп", "фасилитац", "дизайн-спринт"],
    "figma": ["figma", "фигм"],
    "ai-tools": ["нейросет", "промпт", "prompt", "искусственн интеллект", "ии-", "генерац"],
    "portfolio-interview": ["портфоли", "собеседован", "резюме", "найм", "ваканс", "работодател"],
    "planning": ["срок", "планирован", "оценк задач"],
    "mentoring": ["ментор", "наставник", "обучени команд"],
}

MAX = 3


def starts(text: str, stem: str) -> bool:
    """Основа ищется с начала слова: иначе «ии» находится внутри «иллюстрации»."""
    return re.search(r"(?<![0-9a-zа-яё-])" + re.escape(stem), text) is not None

rows = json.load(io.open(ROOT / a.src, encoding="utf-8"))
result = []

for row in rows:
    topics = [t for t in row["topics"].split(",") if t]
    haystack = (row["title"] + " " + row["verdict"]).lower()

    # навыки, разрешённые темами записи; если тем нет — разрешены все
    allowed = []

    for topic in topics:
        allowed += BY_TOPIC.get(topic, [])

    hits = []

    for skill, words in BY_WORD.items():
        score = sum(1 for w in words if starts(haystack, w))

        if not score:
            continue

        # слово весит больше, если навык и так разрешён темой записи
        hits.append((score + (2 if skill in allowed else 0), skill))

    hits.sort(reverse=True)
    picked = [s for _, s in hits if s in allowed][:MAX]

    # добрали словами вне темы, если тема дала мало
    for _, skill in hits:
        if len(picked) >= MAX:
            break

        if skill not in picked:
            picked.append(skill)

    # ничего не нашлось — берём запасной навык первой темы
    if not picked and allowed:
        picked = [allowed[0]]

    result.append({
        "slug": row["slug"],
        "title": row["title"],
        "type": row["type"],
        "topics": row["topics"],
        "level": row["level"],
        "skills": picked,
    })

with io.open(ROOT / a.out, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)

empty = [r for r in result if not r["skills"]]

review = ROOT / ".tmp/skills-review.txt"

with io.open(review, "w", encoding="utf-8", newline="\n") as fh:
    for r in result:
        fh.write("%-40s %-9s %-26s %s\n" % (
            r["title"][:40], r["type"], r["topics"][:26], ", ".join(r["skills"]) or "ПУСТО"))

print("записей: %d, без навыка: %d" % (len(result), len(empty)))
print("файл:", ROOT / a.out)
print("вычитка:", review)
