"""Design token contract check of the designstack theme (directive 10, phase 4; the contract is .claude/rules/wp-theme.md).

1. theme.json: the palette holds only semantic tokens, each one var(--wp--custom--color--<primitive>) of an existing primitive;
   WordPress defaults are off (palette, gradients, font sizes, spacing sizes, shadows).
2. theme-dark.css: both dark blocks carry the same list, every palette token has a dark value through a primitive,
   no primitive is redefined, no hex or rgb.
3. docs/ds/foundation.md: primitive hexes and the light and dark primitive of every semantic token equal theme.json and theme-dark.css.
4. WCAG 2.2 contrast of the pairs from the foundation.md table «Контраст» plus the directive baseline, in both themes, computed from
   theme.json and theme-dark.css: 4.5:1 for text and icons, 3:1 for rims, focus ring and fills. The ratios written in the doc must match.
5. Hardcode in theme files other than theme.json: hex, rgb()/hsl(), font family names, colour and shadow primitives outside
   theme-dark.css, px outside @media (0 is fine). greybox.css is the stage 08 layout: its px are counted, not failed,
   until the stage 11 patterns replace it.
6. Every var(--wp--preset--*) and var(--wp--custom--*) used in the theme exists. Names come from the rendered page when the
   server answers: WordPress writes the slug 2xl as 2-xl.
7. docs/VOICE.md: status keys, words, icons and colour tokens equal the foundation.md table «Статусы каталога → семантика».

Usage: python scripts/check_tokens.py [--url http://localhost:8080/]
Exit code 1 when anything fails.
"""
import argparse, json, pathlib, re, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
THEME = ROOT / "wordpress/wp-content/themes/designstack"
FOUNDATION = ROOT / "docs/ds/foundation.md"
VOICE = ROOT / "docs/VOICE.md"
DARK_CSS = "assets/css/theme-dark.css"
TRANSITIONAL_PX = {"assets/css/greybox.css"}
VAR_RE = re.compile(r"var\(--wp--custom--color--([a-z0-9-]+)\)")

fails = []
notes = []


def check(section, ok, message):
    if not ok:
        fails.append(f"[{section}] {message}")
    return ok


def kebab(name):
    return "-".join(re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+", name)).lower()


def luminance(hex_value):
    channels = [int(hex_value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def strip_css_comments(text):
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def line_of(text, index):
    return text.count("\n", 0, index) + 1


args = argparse.ArgumentParser()
args.add_argument("--url", default="http://localhost:8080/")
args = args.parse_args()

# 1. theme.json
theme = json.loads((THEME / "theme.json").read_text(encoding="utf-8"))
settings = theme["settings"]
primitives = settings["custom"]["color"]
palette = {p["slug"]: p["color"] for p in settings["color"]["palette"]}
light = {}
for name, value in primitives.items():
    check("theme.json", re.fullmatch(r"#[0-9A-F]{6}", value), f"primitive {name} = {value}: expected #RRGGBB")
for slug, value in palette.items():
    match = VAR_RE.fullmatch(value)
    if check("theme.json", match and match.group(1) in primitives, f"palette {slug} = {value}: expected var() of a primitive"):
        light[slug] = match.group(1)
    check("theme.json", not re.fullmatch(r"(gray|accent|success|warning|error|info)-\d+", slug), f"palette has primitive {slug}")
for path, expected in (("color.defaultPalette", False), ("color.defaultGradients", False), ("typography.defaultFontSizes", False),
                       ("spacing.defaultSpacingSizes", False), ("shadow.defaultPresets", False)):
    group, key = path.split(".")
    check("theme.json", settings.get(group, {}).get(key) is expected, f"settings.{path} must be {expected}")

# 2. theme-dark.css
dark_text = strip_css_comments((THEME / DARK_CSS).read_text(encoding="utf-8"))
block_attr = re.search(r':root\[data-theme="dark"\]\s*\{(.*?)\}', dark_text, re.S)
block_media = re.search(r'@media\s*\(prefers-color-scheme:\s*dark\)\s*\{\s*:root:not\(\[data-theme="light"\]\)\s*\{(.*?)\}\s*\}', dark_text, re.S)
dark = {}
if check("theme-dark.css", block_attr and block_media, "both blocks must exist: :root[data-theme=dark] and the prefers-color-scheme media query"):
    decl_attr = dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", block_attr.group(1)))
    decl_media = dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", block_media.group(1)))
    check("theme-dark.css", decl_attr == decl_media, "the two blocks list different overrides")
    for block in (block_attr.group(1), block_media.group(1)):
        check("theme-dark.css", re.search(r"color-scheme:\s*dark", block), "color-scheme: dark missing in a dark block")
    for name, value in decl_attr.items():
        value = value.strip()
        if name.startswith("--wp--preset--color--"):
            slug = name.removeprefix("--wp--preset--color--")
            match = VAR_RE.fullmatch(value)
            if check("theme-dark.css", match and match.group(1) in primitives, f"{slug} = {value}: expected var() of a primitive"):
                dark[slug] = match.group(1)
        elif name.startswith("--wp--preset--shadow--"):
            match = re.fullmatch(r"var\(--wp--custom--shadow--([a-z0-9-]+)\)", value)
            check("theme-dark.css", match and match.group(1) in settings["custom"].get("shadow", {}), f"{name} = {value}: expected var() of a shadow primitive")
        else:
            check("theme-dark.css", False, f"{name}: only semantic colours and shadows may be overridden, primitives never")
    check("theme-dark.css", set(dark) == set(palette), f"dark values missing for {sorted(set(palette) - set(dark))}, extra {sorted(set(dark) - set(palette))}")
check("theme-dark.css", re.search(r":root\s*\{\s*color-scheme:\s*light;\s*\}", dark_text), ":root { color-scheme: light; } missing")
check("theme-dark.css", not re.search(r"#[0-9a-fA-F]{3,8}\b|\b(rgba?|hsla?)\(", dark_text), "hex or rgb in theme-dark.css")

# 3. foundation.md <-> theme.json / theme-dark.css
doc = FOUNDATION.read_text(encoding="utf-8")
doc_primitives = dict(re.findall(r"^\| `([a-z]+-\d+)` \| `(#[0-9A-F]{6})` \|\s*$", doc, re.M))
check("foundation.md", doc_primitives == primitives,
      f"primitives differ: doc only {sorted(set(doc_primitives.items()) - set(primitives.items()))}, theme.json only {sorted(set(primitives.items()) - set(doc_primitives.items()))}")
doc_semantic = {}
for token, lp, lhex, dp, dhex in re.findall(r"^\| `([a-z-]+)` \| `([a-z]+-\d+)` `(#[0-9A-F]{6})` \| `([a-z]+-\d+)` `(#[0-9A-F]{6})` \|", doc, re.M):
    doc_semantic[token] = (lp, dp)
    check("foundation.md", primitives.get(lp) == lhex and primitives.get(dp) == dhex, f"{token}: hex in the doc row does not match its primitive")
check("foundation.md", set(doc_semantic) == set(palette), f"semantic tokens differ: doc only {sorted(set(doc_semantic) - set(palette))}, theme only {sorted(set(palette) - set(doc_semantic))}")
for token, (lp, dp) in doc_semantic.items():
    check("foundation.md", light.get(token) == lp, f"{token}: light {lp} in the doc, {light.get(token)} in theme.json")
    check("foundation.md", dark.get(token) == dp, f"{token}: dark {dp} in the doc, {dark.get(token)} in theme-dark.css")

# 4. contrast
THEMES = {"светлая": "light", "тёмная": "dark"}
pairs = {}
for fg, bg, theme_ru, ratio_doc, threshold in re.findall(r"^\| `([a-z-]+)` на `([a-z-]+)` \| (светлая|тёмная) \| ([\d,]+):1 \| ([\d,]+):1 \| (?:да|нет) \|", doc, re.M):
    pairs[(fg, bg, THEMES[theme_ru])] = (float(threshold.replace(",", ".")), float(ratio_doc.replace(",", ".")))
check("contrast", len(pairs) >= 50, f"only {len(pairs)} pairs parsed from foundation.md «Контраст»")
for fg, bg, threshold in (("text-default", "surface-default", 4.5), ("text-muted", "surface-default", 4.5), ("text-muted", "surface-subtle", 4.5),
                          ("text-on-action", "surface-action-primary", 4.5), ("text-link", "surface-default", 4.5),
                          ("border-focus-ring", "surface-default", 3.0)):
    for mode in ("light", "dark"):
        pairs.setdefault((fg, bg, mode), (threshold, None))
def floor2(value):
    # How foundation.md writes ratios: rounded to three decimals, then cut to two (4.7996 -> 4.800 -> 4.80, 6.528 -> 6.52).
    # Pass or fail is always decided on the exact value, never on this text.
    return int(round(value, 3) * 100 + 1e-6) / 100


minimum = {"light": 99.0, "dark": 99.0}
for (fg, bg, mode), (threshold, ratio_doc) in sorted(pairs.items()):
    source = light if mode == "light" else dark
    if not check("contrast", fg in source and bg in source, f"{fg} on {bg} ({mode}): unknown token"):
        continue
    ratio = contrast(primitives[source[fg]], primitives[source[bg]])
    check("contrast", ratio >= threshold, f"{fg} on {bg} ({mode}): {floor2(ratio):.2f}:1 below {threshold}:1")
    if ratio_doc is not None:
        check("contrast", abs(floor2(ratio) - ratio_doc) < 1e-9, f"{fg} on {bg} ({mode}): the doc says {ratio_doc}, computed {floor2(ratio):.2f}")
    if threshold == 4.5:
        minimum[mode] = min(minimum[mode], floor2(ratio))

# 5. hardcode in theme files
files = sorted(p for p in THEME.rglob("*") if p.suffix in {".css", ".html", ".php", ".js"})
transitional_px = 0
for path in files:
    rel = path.relative_to(THEME).as_posix()
    raw = path.read_text(encoding="utf-8")
    text = strip_css_comments(raw) if path.suffix == ".css" else raw
    for match in re.finditer(r"(?<![&\w])#[0-9a-fA-F]{3,8}\b", text):
        check("hardcode", False, f"{rel}:{line_of(text, match.start())} hex {match.group(0)}")
    for match in re.finditer(r"\b(rgba?|hsla?)\(", text):
        check("hardcode", False, f"{rel}:{line_of(text, match.start())} {match.group(0)}")
    for match in re.finditer(r"\bfont(?:-family)?\s*:\s*([^;}\"']+)", text):
        value = match.group(1).strip()
        check("hardcode", value == "inherit" or value.startswith("var(--wp--preset--font-family--"), f"{rel}:{line_of(text, match.start())} font family {value}")
    if rel != DARK_CSS:
        for match in re.finditer(r"--wp--custom--(?:color|shadow)--", text):
            check("hardcode", False, f"{rel}:{line_of(text, match.start())} primitive outside theme-dark.css")
    if path.suffix == ".css":
        no_media = re.sub(r"@(?:media|container)[^{]+\{", "@rule{", text)
        for match in re.finditer(r"(?<![\w.#-])(\d*\.?\d+)px\b", no_media):
            if float(match.group(1)) == 0:
                continue
            if rel in TRANSITIONAL_PX:
                transitional_px += 1
            else:
                check("hardcode", False, f"{rel}:{line_of(no_media, match.start())} {match.group(0)} outside @media")
    else:
        # В JS брейкпоинт живёт в matchMedia: это условие @media, а не размер в правиле.
        scanned = re.sub(r"\((?:min|max)-width:[^)]*\)", "(media)", text) if path.suffix == ".js" else text
        for match in re.finditer(r"(?<![\w.#-])(\d*\.?\d+)px\b", scanned):
            check("hardcode", float(match.group(1)) == 0, f"{rel}:{line_of(scanned, match.start())} {match.group(0)}")
if transitional_px:
    notes.append(f"greybox.css: {transitional_px} px values of the stage 08 layout, left for the stage 11 patterns")

# 6. every used token variable exists
defined = set()
try:
    page = urllib.request.urlopen(args.url, timeout=10).read().decode("utf-8")
    defined = set(re.findall(r"(--wp--(?:preset|custom)--[a-z0-9-]+)\s*:", page))
    notes.append(f"token variables taken from {args.url}: {len(defined)}")
except OSError as error:
    notes.append(f"server not reachable ({error}); token variables derived from theme.json")


def walk_custom(prefix, node):
    for key, value in node.items():
        name = f"{prefix}--{kebab(key)}"
        if isinstance(value, dict):
            walk_custom(name, value)
        else:
            defined.add(name)


if not defined:
    walk_custom("--wp--custom", settings["custom"])
    defined |= {f"--wp--preset--color--{kebab(s)}" for s in palette}
    defined |= {f"--wp--preset--font-size--{kebab(f['slug'])}" for f in settings["typography"]["fontSizes"]}
    defined |= {f"--wp--preset--font-family--{kebab(f['slug'])}" for f in settings["typography"]["fontFamilies"]}
    defined |= {f"--wp--preset--spacing--{kebab(s['slug'])}" for s in settings["spacing"]["spacingSizes"]}
    defined |= {f"--wp--preset--shadow--{kebab(s['slug'])}" for s in settings["shadow"]["presets"]}
used = []
for path in files:
    rel = path.relative_to(THEME).as_posix()
    text = path.read_text(encoding="utf-8")
    used += [(rel, line_of(text, m.start()), m.group(1)) for m in re.finditer(r"var\((--wp--(?:preset|custom)--[a-z0-9-]+)", text)]
    if path.suffix == ".html":
        slugs = {p["slug"] for p in settings["color"]["palette"]}
        for m in re.finditer(r'"(?:textColor|backgroundColor|borderColor)":"([a-z0-9-]+)"', text):
            check("variables", m.group(1) in slugs, f"{rel}:{line_of(text, m.start())} colour slug {m.group(1)} is not in the palette")
styles_text = json.dumps(theme["styles"], ensure_ascii=False)
used += [("theme.json styles", 0, "--wp--" + m.group(1).replace("|", "--")) for m in re.finditer(r"var:((?:preset|custom)\|[a-z0-9-]+\|[a-z0-9-]+)", styles_text)]
used += [("theme.json styles", 0, m.group(1)) for m in re.finditer(r"var\((--wp--(?:preset|custom)--[a-z0-9-]+)", styles_text)]
used += [("theme.json settings", 0, m.group(1)) for m in re.finditer(r"var\((--wp--(?:preset|custom)--[a-z0-9-]+)", json.dumps(settings))]
for rel, line, name in used:
    check("variables", name in defined, f"{rel}{':' + str(line) if line else ''} {name} is not defined")

# 8. sizes: foundation.md «Размеры» == theme.json settings.custom.size
size_count = 0
size_part = doc.split("### Размеры", 1)
if check("sizes", len(size_part) == 2, "foundation.md: section «Размеры» missing"):
    doc_sizes = {n: v.strip() for n, v in re.findall(r"^\| `size-([a-z-]+)` \| ([^|]+) \|", size_part[1].split("\n## ", 1)[0], re.M)}
    theme_sizes = settings["custom"].get("size", {})
    size_count = len(theme_sizes)
    check("sizes", set(doc_sizes) == set(theme_sizes),
          f"size keys differ: foundation only {sorted(set(doc_sizes) - set(theme_sizes))}, theme.json only {sorted(set(theme_sizes) - set(doc_sizes))}")
    for name in sorted(set(doc_sizes) & set(theme_sizes)):
        check("sizes", doc_sizes[name] == theme_sizes[name],
              f"size-{name}: {doc_sizes[name]} in foundation.md, {theme_sizes[name]} in theme.json")

# 7. VOICE.md <-> foundation.md statuses
status_section = doc.split("## Статусы каталога → семантика", 1)[1].split("\n## ", 1)[0]
doc_status = {}
for field, values, token, icon, words in re.findall(r"^\| (ru_open|ru_payment|status|checked_at|pricing|level) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|", status_section, re.M):
    values = [v.strip() for v in values.split(", ")] if field in ("pricing", "level") else [values.strip()]
    words = [w.strip() for w in words.split(", ")] if len(values) > 1 else [words.strip()]
    for value, word in zip(values, words, strict=True):
        if value == "у бесплатного ресурса":
            continue
        doc_status[(field, value)] = (token.strip(), icon.strip(), word)
voice = VOICE.read_text(encoding="utf-8")
voice_status = {}
for heading, field in (("### `ru_open`", "ru_open"), ("### `ru_payment`", "ru_payment"), ("### `status`", "status"),
                       ("### Свежесть проверки (`checked_at`)", "checked_at"), ("### `pricing`", "pricing"), ("### `level`", "level")):
    part = voice.split(heading, 1)
    if not check("VOICE.md", len(part) == 2, f"section {heading} missing"):
        continue
    table = part[1].split("\n###", 1)[0]
    check("VOICE.md", "| Иконка | Цвет |" in table, f"{field}: no «Иконка» and «Цвет» columns")
    for value, badge, icon, token in re.findall(r"^\| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| [^|]+ \|\s*$", table, re.M):
        value = value.strip().strip("`")
        if value in ("Значение", "Условие") or value.startswith("---"):
            continue
        voice_status[(field, value)] = (token.replace("`", "").strip(), icon.replace("`", "").strip(), badge.strip())
check("VOICE.md", set(voice_status) == set(doc_status),
      f"status keys differ: foundation only {sorted(set(doc_status) - set(voice_status))}, VOICE only {sorted(set(voice_status) - set(doc_status))}")
for key in sorted(set(doc_status) & set(voice_status)):
    (d_token, d_icon, d_word), (v_token, v_icon, v_badge) = doc_status[key], voice_status[key]
    check("VOICE.md", d_token == v_token, f"{key}: colour {d_token} in foundation.md, {v_token} in VOICE.md")
    check("VOICE.md", d_icon == v_icon, f"{key}: icon {d_icon} in foundation.md, {v_icon} in VOICE.md")
    check("VOICE.md", d_word == v_badge or d_word in v_badge, f"{key}: word «{d_word}» in foundation.md, «{v_badge}» in VOICE.md")

print(f"theme.json: {len(primitives)} primitives, {len(palette)} semantic tokens; theme-dark.css: {len(dark)} dark values")
print(f"contrast: {len(pairs)} pairs, minimum for text and icons {minimum['light']:.2f}:1 light / {minimum['dark']:.2f}:1 dark")
print(f"sizes: {size_count} component size tokens")
print(f"hardcode: {len(files)} theme files scanned; token variables used: {len(used)}; statuses paired: {len(doc_status)}")
for note in notes:
    print("note:", note)
for fail in fails:
    print("FAIL", fail)
print("failures:", len(fails))
sys.exit(1 if fails else 0)
