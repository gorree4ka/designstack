"""Доступность: axe-core по списку адресов в обеих темах, плюс ручные проверки.

Использование: python scripts/audit_a11y.py [--urls .tmp/audit/urls.txt] [--out .tmp/audit/a11y.json]

axe ставится один раз: `npm install axe-core --prefix .tmp/audit --no-save`.
Скрипт печатает сводку и сохраняет находки в JSON. Ноль замечаний axe не значит,
что страница доступна: клавиатуру, порядок заголовков и контраст смотрим глазами.
"""
import argparse
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

# Консоль Windows живёт в cp1251 и падает на «×» и русских буквах: вывод переключаем на UTF-8.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
AXE = ROOT / ".tmp/audit/node_modules/axe-core/axe.min.js"
BASE = "http://localhost:8080"

parser = argparse.ArgumentParser()
parser.add_argument("--urls", default=str(ROOT / ".tmp/audit/urls.txt"))
parser.add_argument("--out", default=str(ROOT / ".tmp/audit/a11y.json"))
args = parser.parse_args()

if not AXE.exists():
    raise SystemExit("Нет axe-core: npm install axe-core --prefix .tmp/audit --no-save")

paths = []

for line in pathlib.Path(args.urls).read_text(encoding="utf-8").splitlines():
    if line.strip():
        paths.append(line.split("\t")[0])

axe_source = AXE.read_text(encoding="utf-8")
report = []

# Кроме нарушений собираем `incomplete` — то, что axe проверить не смог. Контраст поверх
# картинки или слоя с `z-index: -1` попадает именно сюда, и проверка «ноль нарушений» молчала
# при контрасте 1,12:1 на всех 140 карточках каталога (16.09.2026).
RUN = """() => axe.run(document, {
    runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']}
}).then(r => ({
    violations: r.violations.map(v => ({
        id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.length,
        target: v.nodes.slice(0, 2).map(n => n.target.join(' ')),
    })),
    incomplete: r.incomplete.map(v => ({
        id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.length,
        target: v.nodes.slice(0, 2).map(n => n.target.join(' ')),
    })),
}))"""

with sync_playwright() as pw:
    browser = pw.chromium.launch()

    for theme in ("light", "dark"):
        page = browser.new_page(viewport={"width": 1440, "height": 900}, color_scheme=theme)

        for path in paths:
            page.goto(BASE + path, wait_until="load", timeout=60000)
            page.add_script_tag(content=axe_source)
            found = page.evaluate(RUN)
            violations = found["violations"]
            unchecked = found["incomplete"]

            # Ручные проверки, которые axe не делает.
            manual = page.evaluate("""() => {
                const h1 = document.querySelectorAll('#ds-main h1, main h1').length;
                const levels = [...document.querySelectorAll('#ds-main h1, #ds-main h2, #ds-main h3, #ds-main h4')]
                    .map(h => Number(h.tagName[1]));
                let jumps = 0;
                for (let i = 1; i < levels.length; i++) {
                    if (levels[i] - levels[i - 1] > 1) { jumps++; }
                }
                const iconOnly = [...document.querySelectorAll('button, a')].filter(el => {
                    const text = (el.textContent || '').replace(/\\s/g, '');
                    const hidden = el.querySelector('.screen-reader-text');
                    return !text && !hidden && !el.getAttribute('aria-label') && el.querySelector('svg');
                }).length;
                const imgNoAlt = [...document.querySelectorAll('img')].filter(i => !i.hasAttribute('alt')).length;
                return {h1, jumps, iconOnly, imgNoAlt};
            }""")

            if violations or unchecked or manual["h1"] != 1 or manual["jumps"] or manual["iconOnly"] or manual["imgNoAlt"]:
                report.append({"path": path, "theme": theme, "violations": violations,
                               "incomplete": unchecked, "manual": manual})

        page.close()

    browser.close()

pathlib.Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

total = sum(len(r["violations"]) for r in report)
unknown = sum(len(r.get("incomplete", [])) for r in report)
print(f"страниц проверено: {len(paths)} × 2 темы")
print(f"страниц с замечаниями: {len(report)}; нарушений axe всего: {total}")
print(f"axe не смог проверить (меряем руками): {unknown}")

seen = {}

for row in report:
    for violation in row["violations"]:
        key = (violation["id"], violation["impact"])
        seen.setdefault(key, []).append(f"{row['path']} [{row['theme']}]")

for (rule, impact), where in sorted(seen.items(), key=lambda x: -len(x[1])):
    print(f"  — {rule} ({impact}): {len(where)} страниц, например {where[0]}")

for row in report:
    m = row["manual"]
    if m["h1"] != 1 or m["jumps"] or m["iconOnly"] or m["imgNoAlt"]:
        print(f"  ручное · {row['path']} [{row['theme']}]: h1={m['h1']}, пропуски уровней={m['jumps']}, "
              f"кнопок-иконок без подписи={m['iconOnly']}, img без alt={m['imgNoAlt']}")

print("отчёт:", args.out)
