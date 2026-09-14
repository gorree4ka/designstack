"""Ищет на сайте протокольный язык — тексты, написанные как отчёт о работе.

Читатель пришёл выбрать инструмент, а не узнать, как устроена наша проверка.
Правило и список запретов — в docs/VOICE.md, раздел «Тон». Скрипт проверяет
то, что реально отдаётся браузеру: страницы каталога, статьи, служебные страницы.

    python scripts/check_voice.py
    python scripts/check_voice.py --base http://localhost:8080

Возвращает код 1, если нашлось хоть одно совпадение: так его можно повесить в хук.
"""
import argparse
import html
import re
import sys
import urllib.error
import urllib.request

# Слово в стоп-листе — это не ошибка сама по себе, а признак: почти всегда рядом
# стоит фраза о том, как мы искали, а не о том, что выбрать читателю.
STOP = [
    # Решение заказчика 14.09.2026: про VPN на сайте не должно быть ни слова.
    # Способы открыть закрытое существуют, но это не наша тема и не наш совет.
    "VPN",
    # «прогонять по очереди» — нормальная речь о работе с инструментом, поэтому
    # ловим не корень, а именно наш служебный оборот.
    "прогон с",
    "прогоне",
    "прогоном",
    "с сервера",
    "российского IP",
    "российского адреса",
    "страна IP",
    "замер",
    "условие выборки",
    "условие группы",
    "репозитор",
    "мы проверяли",
    "куратор проверит",
    "куратор перепроверил",
    "код 4",
    "код 2",
    "отчёт о",
    "по правилу",
    "проверено по таблице",
]

# Вердикт не повторяет то, что уже написано меткой рядом: «Недоступен из РФ» под
# фразой «из России не открывается» — это два раза одно и то же в одной карточке.
# Оговорка, которой метка не передаёт («бесплатно — только личные проекты»), остаётся.
ECHO = {
    "Недоступен из РФ": ["не открывается", "сайт закрыт", "недоступен"],
    "Открывается из РФ": ["открывается из России", "работает из России", "открывается напрямую"],
    "Не оплатить из РФ": ["не оплатить", "картой не"],
    "Российский": ["оплата в рублях", "рубли, карта"],
}

CARD = re.compile(r'<article class="ds-card.*?</article>', re.S)

PAGES = [
    "/",
    "/about/",
    "/suggest/",
    "/tools/",
    "/learn/",
    "/assets/",
    "/community/",
    "/collections/",
    "/digest/",
]

UA = "designstack-voice-check"


def text_of(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})

    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read().decode("utf-8", "replace")

    raw = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", raw)

    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def links(base: str, path: str) -> list:
    """Адреса записей и статей с раздела — чтобы не перечислять их руками."""
    try:
        req = urllib.request.Request(base + path, headers={"User-Agent": UA})

        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8", "replace")
    except urllib.error.URLError:
        return []

    found = re.findall(r'href="' + re.escape(base) + r'(/(?:resource|collections|digest)/[^"#?]+/)"', raw)

    return sorted({f for f in found if not f.endswith("/feed/")})


def echoes(raw):
    """Карточки, где вердикт повторяет соседнюю метку."""
    out = []

    for card in CARD.findall(raw):
        plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", card))
        verdict = re.search(r'class="ds-card__verdict">([^<]*)<', card)
        title = re.search(r'class="ds-card__link"[^>]*>([^<]*)<', card)

        if not verdict:
            continue

        said = verdict.group(1)

        for badge, phrases in ECHO.items():
            if badge not in plain:
                continue

            for phrase in phrases:
                if phrase.lower() in said.lower():
                    out.append((title.group(1) if title else "?", badge, said))

                    break

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8080")
    args = ap.parse_args()
    base = args.base.rstrip("/")

    targets = list(PAGES)

    # Архив разбит на страницы: без обхода пагинации проверятся только первые карточки.
    for path in ("/tools/", "/learn/", "/assets/", "/community/", "/collections/", "/digest/"):
        page = 1

        while True:
            part = path if 1 == page else f"{path}page/{page}/"
            found = links(base, part)

            if not found:
                break

            targets.extend(found)
            page += 1

            if page > 40:
                break

    targets = list(dict.fromkeys(targets))
    hits = 0

    for path in targets:
        try:
            body = text_of(base + path)
        except urllib.error.URLError as exc:
            print(f"  {path}: не открылась ({exc})")

            continue

        for word in STOP:
            at = body.lower().find(word.lower())

            if at < 0:
                continue

            print(f"  {path}\n      «{body[max(0, at - 60):at + 90].strip()}»")
            hits += 1

    # Вторая проверка идёт по разделам: там карточка и метка стоят рядом.
    dupes = 0

    for path in ("/tools/", "/learn/", "/assets/", "/community/"):
        page = 1

        while True:
            part = path if 1 == page else f"{path}page/{page}/"

            try:
                req = urllib.request.Request(base + part, headers={"User-Agent": UA})

                with urllib.request.urlopen(req, timeout=20) as resp:
                    raw = resp.read().decode("utf-8", "replace")
            except urllib.error.URLError:
                break

            found = echoes(raw)

            for title, badge, said in found:
                print("  %s · %s: метка «%s» и вердикт «%s»" % (part, title, badge, said))

            dupes += len(found)
            page += 1

            if page > 40 or "ds-card" not in raw:
                break

    print()
    print("Проверено страниц: %d. Протокольных мест: %d. Повторов метки в вердикте: %d."
          % (len(targets), hits, dupes))

    return 1 if (hits or dupes) else 0


sys.exit(main())
