"""Собирает из `docs/skills-map/map.md` два листа: карту для нас и проверку для человека.

Карта живёт в markdown: там её правят и там её читает git. Из одного файла получаются
обе страницы, поэтому тексты вариантов не расходятся между документом и проверкой.

Формат карты:

    ## Группа 1. Ремесло
    <абзац: что это за слой и зачем он дизайнеру>

    ### Исследование и пользователи
    `ux-research`

    <абзац: что это за область и зачем она дизайнеру>

    #### Проблемное интервью
    > Подсказка, что это за навык.

    - `—` Не проводил интервью с пользователями
    - `junior` Был на 3 и более интервью: слушал, вёл заметки
    - `middle` Сам написал сценарий и провёл 5 и более интервью по своей задаче
    - `senior` Разбираю чужие сценарии и выводы

Пометка грейда нужна для подсчёта и в проверке не показывается (P24).

    python scripts/render_skills_map.py
    python scripts/render_skills_map.py --out .tmp/map.html --check .tmp/check.html
"""
import argparse
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

p = argparse.ArgumentParser()
p.add_argument("--src", default="docs/skills-map/map.md")
p.add_argument("--out", default=".tmp/skills-map.html", help="лист карты")
p.add_argument("--check", default=".tmp/grade-check.html", help="лист проверки")
p.add_argument("--terms", default=".tmp/skills-terms.json", help="выгрузка термов для таксономии `skill`")
p.add_argument("--php", default="wordpress/wp-content/plugins/designstack-core/data/skills-map.php",
               help="данные проверки для плагина")
a = p.parse_args()

src = ROOT / a.src
GRADES = {"junior": "Junior", "middle": "Middle", "senior": "Senior"}

# ---------- разбор ----------

with open(src, encoding="utf-8") as fh:
    lines = fh.read().splitlines()

def split_slug(heading: str) -> tuple:
    """«Проблемное интервью `user-interviews`» → название и слаг для таксономии."""
    m = re.fullmatch(r"(.+?)\s+`([a-z0-9-]+)`", heading)

    return (m.group(1), m.group(2)) if m else (heading, "")


groups: list[dict] = []
area = skill = None
inside = False

for raw in lines:
    line = raw.rstrip()

    if line == "## Карта":
        inside = True
        continue

    if line.startswith("## Чем карта обеспечена"):
        break

    if not inside:
        continue

    if line.startswith("## "):
        groups.append({"title": line[3:].strip(), "about": "", "areas": []})
        area = skill = None
        continue

    if line.startswith("#### "):
        title, slug = split_slug(line[5:].strip())
        skill = {"title": title, "slug": slug, "hint": "", "opts": []}
        area["skills"].append(skill)
        continue

    if line.startswith("### "):
        title, slug = split_slug(line[4:].strip())
        area = {"title": title, "slug": slug, "topics": "", "about": "", "skills": []}
        groups[-1]["areas"].append(area)
        skill = None
        continue

    if area is not None and skill is None and line.startswith("`"):
        area["topics"] = line.replace("`", "").strip()
        continue

    if skill is not None and line.startswith("> "):
        skill["hint"] = line[2:].strip()
        continue

    m = re.fullmatch(r"- `([^`]+)` (.+)", line)

    if m and skill is not None:
        grade = m.group(1).strip()
        skill["opts"].append(["" if grade not in GRADES else grade, m.group(2).strip()])
        continue

    if not line:
        continue

    # абзац «что это за сфера и зачем она дизайнеру»
    if skill is None and area is not None and not area["about"]:
        area["about"] = line
    elif area is None and groups and not groups[-1]["about"]:
        groups[-1]["about"] = line

if not groups:
    sys.exit("в файле нет раздела «## Карта» — разбирать нечего")

areas_all = [ar for g in groups for ar in g["areas"]]
skills_all = [sk for ar in areas_all for sk in ar["skills"]]
opts_all = sum(len(sk["opts"]) for sk in skills_all)

broken = [sk["title"] for sk in skills_all if len(sk["opts"]) < 4 or not sk["hint"]]

if broken:
    sys.exit("навыки без подсказки или с неполным набором вариантов: " + ", ".join(broken))

slugs = [x["slug"] for x in areas_all + skills_all]

if "" in slugs:
    sys.exit("есть области или навыки без слага: слаг пишется в заголовке через обратные кавычки")

if len(set(slugs)) != len(slugs):
    sys.exit("слаги повторяются: " + ", ".join(sorted({s for s in slugs if slugs.count(s) > 1})))


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def plural(n: int, one: str, few: str, many: str) -> str:
    """«1 навык», «4 навыка», «5 навыков» — иначе счётчик выглядит машинным."""
    if n % 100 in range(11, 15):
        return many

    if n % 10 == 1:
        return one

    if n % 10 in (2, 3, 4):
        return few

    return many


def fill(template: pathlib.Path, out_path: pathlib.Path, values: dict) -> None:
    page = template.read_text(encoding="utf-8")

    for key, value in values.items():
        page = page.replace("{{%s}}" % key, value)

    left = re.findall(r"\{\{[A-Z]+\}\}", page)

    if left:
        sys.exit("в шаблоне %s остались незаполненные места: %s" % (template.name, set(left)))

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(page)


# ---------- лист карты ----------

blocks = []
n_area = 0

for group in groups:
    blocks.append('<h2 class="grp">%s</h2>' % esc(group["title"]))

    if group["about"]:
        blocks.append('<p class="grp-about">%s</p>' % esc(group["about"]))

    for ar in group["areas"]:
        n_area += 1
        skills_html = []

        for sk in ar["skills"]:
            rows = []

            for grade, text in sk["opts"]:
                rows.append(
                    '<div class="opt"><span class="opt-tx">{tx}</span>'
                    '<span class="opt-gr{cls}">{gr}</span></div>'.format(
                        tx=esc(text),
                        cls="" if grade else " none",
                        gr=GRADES.get(grade, "—"),
                    )
                )

            skills_html.append(
                '<div class="skill"><div class="skill-top"><strong>{title}</strong></div>'
                '<p class="skill-hint">{hint}</p>{rows}</div>'.format(
                    title=esc(sk["title"]), hint=esc(sk["hint"]), rows="".join(rows)
                )
            )

        blocks.append(
            '<details class="area{gap}"{open}>'
            '<summary><span class="area-head"><span class="area-name">{name}</span>'
            '<span class="area-meta"><span class="area-src">{src}</span>'
            '<span class="area-state">{n} {word}</span></span></span>'
            '<span class="area-about">{about}</span></summary>'
            '<div class="area-body">{skills}</div></details>'.format(
                gap=" gap" if ar["topics"] == "темы нет" else "",
                open=" open" if n_area == 1 else "",
                name=esc(ar["title"]),
                src=esc(ar["topics"] or "—"),
                about=esc(ar["about"]),
                n=len(ar["skills"]),
                word=plural(len(ar["skills"]), "навык", "навыка", "навыков"),
                skills="".join(skills_html),
            )
        )

fill(
    ROOT / "scripts/templates/skills-map.html",
    ROOT / a.out,
    {
        "MAP": "\n".join(blocks),
        "AREAS": str(len(areas_all)),
        "SKILLS": str(len(skills_all)),
        "OPTIONS": str(opts_all),
    },
)

# ---------- лист проверки ----------

questions = []

for group in groups:
    for ar in group["areas"]:
        for sk in ar["skills"]:
            questions.append({
                "area": ar["title"],
                "name": sk["title"],
                "hint": sk["hint"],
                "opts": sk["opts"],
            })

fill(
    ROOT / "scripts/templates/grade-check.html",
    ROOT / a.check,
    {
        "DATA": json.dumps(questions, ensure_ascii=False),
        "AREAS": str(len(areas_all)),
        "SKILLS": str(len(skills_all)),
    },
)

# ---------- выгрузка термов ----------

terms = []

for ar in areas_all:
    terms.append({
        "slug": ar["slug"],
        "name": ar["title"],
        "parent": "",
        "description": ar["about"],
    })

    for sk in ar["skills"]:
        terms.append({
            "slug": sk["slug"],
            "name": sk["title"],
            "parent": ar["slug"],
            "description": sk["hint"],
        })

terms_path = ROOT / a.terms
terms_path.parent.mkdir(parents=True, exist_ok=True)

with open(terms_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(terms, fh, ensure_ascii=False, indent=2)

# ---------- данные для плагина ----------


def php(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


php_lines = [
    "<?php",
    "/**",
    " * Данные проверки грейда: области, навыки и варианты ответа.",
    " *",
    " * Файл собран скриптом `scripts/render_skills_map.py` из `docs/skills-map/map.md`.",
    " * Руками не править: правки перетрутся при следующей сборке карты.",
    " *",
    " * @package designstack-core",
    " */",
    "",
    "defined( 'ABSPATH' ) || exit;",
    "",
    "return array(",
]

for ar in areas_all:
    php_lines += [
        "\tarray(",
        "\t\t'slug'   => %s," % php(ar["slug"]),
        "\t\t'name'   => %s," % php(ar["title"]),
        "\t\t'about'  => %s," % php(ar["about"]),
        "\t\t'skills' => array(",
    ]

    for sk in ar["skills"]:
        php_lines += [
            "\t\t\tarray(",
            "\t\t\t\t'slug' => %s," % php(sk["slug"]),
            "\t\t\t\t'name' => %s," % php(sk["title"]),
            "\t\t\t\t'hint' => %s," % php(sk["hint"]),
            "\t\t\t\t'opts' => array(",
        ]

        for grade, text in sk["opts"]:
            php_lines.append("\t\t\t\t\tarray( 'grade' => %s, 'text' => %s )," % (php(grade), php(text)))

        php_lines += ["\t\t\t\t),", "\t\t\t),"]

    php_lines += ["\t\t),", "\t),"]

php_lines += [");", ""]

php_path = ROOT / a.php
php_path.parent.mkdir(parents=True, exist_ok=True)

with open(php_path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(php_lines))

print("групп %d · областей %d · навыков %d · вариантов %d" % (
    len(groups), len(areas_all), len(skills_all), opts_all))
print("карта:   ", ROOT / a.out)
print("проверка:", ROOT / a.check)
