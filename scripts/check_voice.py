"""Ищет обращение на «ты» в текстах сайта: интерфейс на «вы» (решение заказчика 15.09.2026).

Правило живёт в `docs/VOICE.md`, раздел «Тон». Проверка нужна потому, что обращение
задаётся в трёх разных местах — строки плагина, паттерны темы и содержимое страниц, —
и правка одного места молча оставляет «ты» в двух других.

    python scripts/check_voice.py            # тема, плагин, исходники контента
    python scripts/check_voice.py --db        # плюс выгрузка базы, если она снята

Выгрузка базы: `.tmp/db-text.txt` (её пишет разовый скрипт выгрузки, в git не входит).
Комментарии кода пропускаются: обращение в комментарии читателю не показывается.
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

TARGETS = [
    ROOT / "wordpress/wp-content/themes/designstack",
    ROOT / "wordpress/wp-content/plugins/designstack-core",
    ROOT / "docs/content/pages",
    ROOT / "docs/content/digests",
    ROOT / "docs/content/collections",
    ROOT / "docs/content/lessons",
]
EXT = {".php", ".js", ".html"}

# Местоимения и глаголы второго лица единственного числа.
WORDS = (
    r"ты|тебе|тебя|тобой|тво[йяёе]|твои[а-яё]*|"
    r"знаешь|собираешь|пользуешься|делаешь|хочешь|можешь|видишь|найдёшь|получишь|ищешь|берёшь|"
    r"пришли|напиши|расскажи|посмотри|отметь|начни|выбери|попробуй|нажми|смотри|бери|проверь|"
    r"открой|найди|читай|заходи|жми|сравни|подпишись|оставь|предложи|прочитай"
)
RE = re.compile(r"(?<![А-Яа-яЁё])(" + WORDS + r")(?![А-Яа-яЁё])", re.IGNORECASE)

# Повелительное наклонение единственного числа по окончанию: «-ай», «-яй», «-уй», «-юй»
# и возвратное «-ись». Существительных с такими концами мало, и они перечислены.
# Случай: 17.09.2026 — «Запусти симулятор и понаблюдай» дожило до сайта, потому что
# словарь выше знал только слова из первых трёх уроков.
IMPERATIVE = re.compile(r"(?<![А-Яа-яЁё-])([а-яё]{3,}(?:ай|яй|уй|юй|ись))(?![А-Яа-яЁё-])", re.IGNORECASE)
NOT_VERB = {
    "случай", "край", "чай", "сарай", "обычай", "трамвай", "урожай", "запись", "надпись",
    "подпись", "опись", "роспись", "летопись", "рукопись", "живопись", "аудиозапись",
    "видеозапись", "перепись", "пропись", "май", "рай", "лай", "буй", "струй", "статуй",
    "вайфай", "трамвай", "малай", "самурай", "попугай", "валуй",
}
COMMENT = re.compile(r"^\s*(\*|//|#|/\*|<!--\s*(wp:|/wp:))")

# Прямая речь — данные, а не обращение к читателю: в уроке в кавычках лежат реплики
# собеседника и образцы замечаний коллеги — там «ты» законно. Тег <q> — та же прямая речь.
QUOTED = re.compile(r"«[^»]{0,400}»|<q>.*?</q>")

# «пришли» — и повелительное («пришли ссылку»), и прошедшее («вы пришли»). Второе не ошибка.
PAST = re.compile(r"(?:вы|мы|они|люди|все|этому|сюда|туда)\s+$", re.IGNORECASE)


def scan(path: pathlib.Path):
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return
    for n, line in enumerate(text.splitlines(), 1):
        if COMMENT.match(line):
            continue
        # Кавычки гасим пробелами, чтобы номера столбцов не съехали.
        clean = QUOTED.sub(lambda q: " " * len(q.group(0)), line)
        for m in RE.finditer(clean):
            if PAST.search(clean[:m.start()]):
                continue
            yield n, m.group(1), line.strip()[:120]
        for m in IMPERATIVE.finditer(clean):
            # «-лись» — прошедшее время («вернулись»), «-тись» — инфинитив («пройтись»),
            # «-вшись» — деепричастие («испугавшись»); повелительное среди них не встречается.
            if m.group(1).lower() not in NOT_VERB and not m.group(1).lower().endswith(("лись", "тись", "вшись")):
                yield n, m.group(1), line.strip()[:120]


p = argparse.ArgumentParser()
p.add_argument("--db", action="store_true", help="проверить и выгрузку базы .tmp/db-text.txt")
a = p.parse_args()

hits = []

for target in TARGETS:
    if not target.exists():
        continue
    for f in sorted(target.rglob("*")):
        # В папке уроков лежат и присланные исходники, и наши тела: на сайт идут только `*.body.html`.
        if f.parent.name == "lessons" and not f.name.endswith(".body.html"):
            continue
        if f.is_file() and f.suffix in EXT:
            for n, word, line in scan(f):
                hits.append((f.relative_to(ROOT).as_posix(), n, word, line))

if a.db:
    dump = ROOT / ".tmp/db-text.txt"
    if dump.exists():
        for n, word, line in scan(dump):
            hits.append((".tmp/db-text.txt", n, word, line))
    else:
        print("выгрузки базы нет, проверены только файлы")

for path, n, word, line in hits:
    print(f"{path}:{n}\t{word}\t{line}")

print(f"\nнайдено обращений на «ты»: {len(hits)}")
sys.exit(1 if hits else 0)
