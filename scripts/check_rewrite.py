"""Переписанный урок против прежней версии: что из фактов ушло и что пришло (D202).

  python scripts/check_rewrite.py docs/content/lessons/<урок>.body.html [ещё уроки] [--base HEAD]

Старые уроки переписываются в стиле образца автора (D200) вместе с содержанием. Факты в них уже
сверены (D185, D186), поэтому каждое расхождение с прежней версией должно быть нарочным: ушедшее —
убрано по решению, пришедшее — сверено с первоисточником. Скрипт сравнивает файл с его версией
в git и печатает списками «ушло» и «пришло»:

- ссылки (внешние и внутренние);
- числа из текста;
- цитаты и примеры в «ёлочках»;
- названия латиницей: компании, руководства, стандарты.

Тренажёры обязаны совпасть по устройству — число вопросов, меток поиска, частей сборки, панелей,
кусков для вычёркивания, шаблонов и пунктов «Что почитать дальше». Расхождение — провал: тренажёр
переделывают нарочно, с флагом `--widgets-changed`, и тогда проверяют его прогоном
`scripts/check_lesson_widgets.py`.
"""
import argparse
import collections
import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent

WIDGETS = {
    "вопросов викторины": r"data-quiz-q\b",
    "меток поиска": r'data-hunt-pin="',
    "ловушек поиска": r"data-hunt-miss\b",
    "частей сборки": r'data-compose-part="',
    "верных вариантов сборки": r"data-compose-ok\b",
    "панелей переключателя": r'data-switch-pane="',
    "кусков вычёркивания": r'data-strike-w="',
    "свойств панели": r"data-props-prop\b",
    "шаблонов для копирования": r'data-copy="',
    "пунктов «Что почитать дальше»": r'<li><span class="ds-lesson__reads-title">',
    "разделов": r'<section id="',
}

parser = argparse.ArgumentParser()
parser.add_argument("files", nargs="+")
parser.add_argument("--base", default="HEAD")
parser.add_argument("--widgets-changed", action="store_true")
args = parser.parse_args()


def text_of(html):
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    html = re.sub(r"<[^>]+>", " ", html)
    for ent, ch in (("&nbsp;", " "), ("&quot;", '"'), ("&#45;", "-"), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">")):
        html = html.replace(ent, ch)
    return re.sub(r"\s+", " ", html.replace(" ", " "))


def facts(html):
    text = text_of(html)
    return {
        "ссылки": collections.Counter(re.findall(r'href="([^"#][^"]*)"', html)),
        "числа": collections.Counter(re.findall(r"\d+(?:[ ,.:–-]\d+)*", text)),
        "цитаты": collections.Counter(q.strip() for q in re.findall(r"«([^«»]{2,160})»", text)),
        # точка в конце — знак препинания, а не часть названия: «Wix.» и «Wix» — одно и то же
        "названия латиницей": collections.Counter(
            n.rstrip(".") for n in re.findall(r"\b[A-Z][A-Za-z0-9.]*(?:[ -][A-Z0-9][A-Za-z0-9.]*)*", text)),
    }


fails = 0
for name in args.files:
    path = pathlib.Path(name)
    rel = path.resolve().relative_to(ROOT).as_posix()
    new = path.read_text(encoding="utf-8")
    try:
        old = subprocess.run(["git", "show", "%s:%s" % (args.base, rel)], cwd=ROOT, capture_output=True,
                             check=True).stdout.decode("utf-8")
    except subprocess.CalledProcessError:
        print("== %s\n  ПЛОХО нет версии в %s" % (rel, args.base))
        fails += 1
        continue

    print("== %s  (против %s)" % (rel, args.base))
    words = [len(re.findall(r"\w+", text_of(h))) for h in (old, new)]
    h3 = [h.count("<h3") for h in (old, new)]
    print("  слов %d → %d · подзаголовков h3 %d → %d" % (words[0], words[1], h3[0], h3[1]))

    for label, rx in WIDGETS.items():
        a, b = len(re.findall(rx, old)), len(re.findall(rx, new))
        if a != b:
            ok = args.widgets_changed
            fails += 0 if ok else 1
            print("  %s %s: %d → %d" % ("внимание" if ok else "ПЛОХО", label, a, b))

    fo, fn = facts(old), facts(new)
    for kind in fo:
        gone = sorted((fo[kind] - fn[kind]).elements())
        came = sorted((fn[kind] - fo[kind]).elements())
        if gone:
            print("  ушло · %s (%d): %s" % (kind, len(gone), " | ".join(gone)))
        if came:
            print("  пришло · %s (%d): %s" % (kind, len(came), " | ".join(came)))

print("\nпровалов: %d" % fails)
sys.exit(1 if fails else 0)
