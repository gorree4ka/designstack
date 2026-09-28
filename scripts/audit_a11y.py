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
parser = argparse.ArgumentParser()
parser.add_argument("--urls", default=str(ROOT / ".tmp/audit/urls.txt"))
parser.add_argument("--out", default=str(ROOT / ".tmp/audit/a11y.json"))
# Живой сайт проверяется тем же прогоном: после выката важно, что до страницы доехали
# и разметка, и стили, а не только то, что они собрались локально.
parser.add_argument("--base", default="http://localhost:8080")
args = parser.parse_args()
BASE = args.base.rstrip("/")

if not AXE.exists():
    raise SystemExit("Нет axe-core: npm install axe-core --prefix .tmp/audit --no-save")

paths = []

for line in pathlib.Path(args.urls).read_text(encoding="utf-8").splitlines():
    if line.strip():
        paths.append(line.split("\t")[0])

axe_source = AXE.read_text(encoding="utf-8")
report = []
demo_blocks = 0

# Кроме нарушений собираем `incomplete` — то, что axe проверить не смог. Контраст поверх
# картинки или слоя с `z-index: -1` попадает именно сюда, и проверка «ноль нарушений» молчала
# при контрасте 1,12:1 на всех 140 карточках каталога (16.09.2026).
#
# Образец с намеренно плохим контрастом (`data-contrast-demo`, уроки «Цвет и контраст») — содержимое
# урока: серая дата 2,53:1 нужна, чтобы показать провал. Такие блоки проверяются всеми правилами,
# кроме контраста, а их числа сверяет с замером `scripts/check_lessons.py`.
RUN = """async () => {
const opts = {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']}};
const demo = document.querySelectorAll('[data-contrast-demo]').length;
const pack = r => ({
    violations: r.violations.map(v => ({
        id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.length,
        target: v.nodes.slice(0, 2).map(n => n.target.join(' ')),
    })),
    incomplete: r.incomplete.map(v => ({
        id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.length,
        target: v.nodes.slice(0, 2).map(n => n.target.join(' ')),
        measured: v.id === 'color-contrast' ? v.nodes.map(n => measure(n.target.join(' '))) : [],
    })),
});
const main = pack(await axe.run(demo ? {exclude: [['[data-contrast-demo]']]} : document, opts));
if (demo) {
    const inside = pack(await axe.run({include: [['[data-contrast-demo]']]},
        Object.assign({}, opts, {rules: {'color-contrast': {enabled: false}}})));
    main.violations = main.violations.concat(inside.violations);
    main.incomplete = main.incomplete.concat(inside.incomplete);
}
main.demo = demo;
return main;

// Контраст узла, который axe оставил без ответа: цвет текста против первого непрозрачного
// фона вверх по дереву. Картинка или полупрозрачный слой под текстом — честное «не измерить».
function measure(selector) {
    let el = null;
    try { el = document.querySelector(selector); } catch (e) { el = null; }
    if (!el) { return {selector, skip: 'узел не найден'}; }
    const parse = c => { const m = c.match(/rgba?\\(([^)]+)\\)/); return m ? m[1].split(',').map(parseFloat) : null; };
    const lum = p => { const f = v => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
        return 0.2126 * f(p[0]) + 0.7152 * f(p[1]) + 0.0722 * f(p[2]); };
    const style = getComputedStyle(el);
    const fg = parse(style.color);
    let node = el, bg = null;
    while (node && node.nodeType === 1) {
        const s = getComputedStyle(node);
        if (s.backgroundImage && s.backgroundImage !== 'none') { return {selector, skip: 'под текстом картинка'}; }
        const c = parse(s.backgroundColor);
        if (c) {
            const alpha = c.length > 3 ? c[3] : 1;
            if (alpha >= 1) { bg = c; break; }
            if (alpha > 0) { return {selector, skip: 'полупрозрачный слой'}; }
        }
        node = node.parentElement;
    }
    if (!fg || !bg) { bg = bg || [255, 255, 255]; }
    if (!fg) { return {selector, skip: 'цвет текста не разобран'}; }
    const hi = Math.max(lum(fg), lum(bg)), lo = Math.min(lum(fg), lum(bg));
    const size = parseFloat(style.fontSize), bold = parseInt(style.fontWeight, 10) >= 700;
    const need = size >= 24 || (size >= 18.66 && bold) ? 3 : 4.5;
    return {selector, ratio: Math.round(((hi + 0.05) / (lo + 0.05)) * 100) / 100, need,
            text: (el.textContent || '').trim().slice(0, 30)};
}
}"""

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
            demo_blocks += found.get("demo", 0)

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
if demo_blocks:
    print(f"образцов с намеренно плохим контрастом: {demo_blocks} — контраст в них не мерит axe, числа сверяет check_lessons.py")
# Что из «не смог проверить» удалось измерить самим, и что осталось глазам.
measured = [m for r in report for one in r.get("incomplete", []) for m in one.get("measured", [])]
ratios = [m for m in measured if "ratio" in m]
low = [m for m in ratios if m["ratio"] < m["need"]]
blind = [m for m in measured if "skip" in m]
print(f"axe не смог проверить: {unknown}; из них контраст измерен самим аудитом: {len(ratios)} узлов"
      + (f", худший {min(m['ratio'] for m in ratios)}:1" if ratios else ""))

for m in low:
    print(f"  НЕ ДОБИРАЕТ {m['ratio']}:1 при норме {m['need']}: {m['selector']} «{m['text']}»")

if blind:
    print(f"  остаётся глазам: {len(blind)} — " + "; ".join(sorted({m['skip'] for m in blind})))

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
