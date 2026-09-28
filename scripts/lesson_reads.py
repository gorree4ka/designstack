"""Раздел «Что почитать дальше» в конце урока — из одного файла данных.

До 28.09.2026 рекомендации стояли в подвале урока одним абзацем: служебная подпись
(тема, ступень, пример, что копируется), а за ней книги через точку с запятой.
Заказчица не узнала в этом рекомендацию (27.09.2026), и подвал стал списком: у каждой
книги или статьи своя строка — что это, кто и на каком языке, зачем читать.

Данные — `docs/content/lessons/reads.json`: источники отдельно, уроки отдельно, поэтому
книга, которую завели в каталог, получает ссылку во всех уроках правкой одной строки.
Скрипт заменяет в теле урока `<footer>…</footer>` или прежний `<section id="further-reading">…</section>`.

    python scripts/lesson_reads.py            # переписать тела уроков
    python scripts/lesson_reads.py --check    # только сверить, ничего не писать
"""
import argparse
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
LESSONS = ROOT / "docs/content/lessons"
DATA = json.loads((LESSONS / "reads.json").read_text(encoding="utf-8"))
# Якорь `read` уже занят разделом «Как прочитать результат» в уроке «Структура и потоки, Middle»,
# поэтому у списка своё имя — два одинаковых id на странице уводят ссылку оглавления не туда.
OLD = re.compile(r"<footer>.*?</footer>|<section id=\"further-reading\">.*?</section>", re.S)

parser = argparse.ArgumentParser()
parser.add_argument("--check", action="store_true")
args = parser.parse_args()


def glue(meta):
    # Разделитель держится за предыдущее слово: иначе при переносе строка начнётся с «·».
    return meta.replace(" · ", " · ")


def render(items):
    rows = []

    for item in items:
        res = DATA["resources"][item["res"]]
        parts = ['<span class="ds-lesson__reads-title">%s</span>' % res["title"]]

        if res["meta"]:
            parts.append('<span class="ds-lesson__reads-meta">%s</span>' % glue(res["meta"]))

        if item["why"]:
            parts.append("<span>%s</span>" % item["why"])

        rows.append("    <li>" + "".join(parts) + "</li>")

    return (
        '<section id="further-reading">\n'
        '  <div class="ds-lesson__section-head"><h2>Что почитать дальше</h2></div>\n'
        '  <ul class="ds-lesson__reads">\n' + "\n".join(rows) + "\n  </ul>\n</section>"
    )


problems = []
bodies = sorted(p.name.replace(".body.html", "") for p in LESSONS.glob("*.body.html"))

for slug in sorted(set(bodies) - set(DATA["lessons"])):
    problems.append("урок без списка в reads.json: " + slug)

for slug, items in DATA["lessons"].items():
    missing = [i["res"] for i in items if i["res"] not in DATA["resources"]]

    if missing:
        problems.append("%s: нет источника %s" % (slug, missing))
        continue

    path = LESSONS / (slug + ".body.html")
    body = path.read_text(encoding="utf-8")
    found = OLD.findall(body)

    if len(found) != 1:
        problems.append("%s: подвалов или разделов «Что почитать» %d, нужен один" % (slug, len(found)))
        continue

    new = OLD.sub(lambda m: render(items), body)
    bare = sum(1 for i in items if "<a " not in DATA["resources"][i["res"]]["title"])
    state = "без изменений" if new == body else ("было: подвал" if found[0].startswith("<footer>") else "обновлён")
    print("%-30s пунктов %d, без ссылки %d · %s" % (slug, len(items), bare, state))

    if not args.check and new != body:
        if not new.strip():
            problems.append(slug + ": пустой результат, не пишу")
            continue
        path.write_text(new, encoding="utf-8", newline="\n")

used = {i["res"] for items in DATA["lessons"].values() for i in items}

for key in sorted(set(DATA["resources"]) - used):
    problems.append("источник нигде не используется: " + key)

print("\nпроблем: %d" % len(problems))

for line in problems:
    print("  " + line)

sys.exit(1 if problems else 0)
