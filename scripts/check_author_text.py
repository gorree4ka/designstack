"""Авторский текст до показа: ссылки, длина фраз и абзацев, штампы ИИ-текста, «мы» (D199).

Зачем. 06.10.2026 заказчица вернула тексты канала и статьи для vc.ru как машинные, потом нашла
в постах голые адреса, а в статье остались ссылки, у которых текстом стоит сам адрес
(«designstack.ru/lessons»): прежняя проверка искала только `https://` в тексте и их пропустила.
Правило голоса — `docs/VOICE.md` (авторский голос) и `docs/research/voice-channel-2026-10-06.md`.

Что проверяет в каждом файле — текст ниже первой черты `---` (выше — служебная шапка):
- ссылка вшита в слова: текст ссылки не адрес с путём (имя сайта «designstack.ru» можно), голого адреса нет;
- фразы не длиннее 24 слов, абзацы не длиннее 60 слов (около пяти строк на телефоне);
- нет штампов из навыков humanizer и stop-slop и нет «мы»;
- цитата — не длиннее строки: редактор vc.ru при вставке склеивает строки цитаты в одну («оплатуДеньги»),
  пример сообщения из интерфейса идёт картинкой «было — стало» с макета урока (06.10.2026);
- отдельно печатает места для глаз: «просто», «очень», «не …, а …», «не только», «действительно» — бывают
  и по делу: в образце самой заказчицы (статья для vc.ru, версия 4) они стоят намеренно, образец главнее списка.

    python scripts/check_author_text.py docs/content/articles/vc-errors-junior.md
    python scripts/check_author_text.py docs/content/digests/2026-09-30_tg.md --glavred

`--glavred` вставляет текст в glvrd.ru и печатает оценку «Чистота»; ниже 8 — повод перечитать.
Оценку до 9,5 дожимает только сухой справочный стиль: местоимения, вопросы читателю и разговорные
слова Главред подчёркивает, а для авторского голоса они нужны.
"""
import argparse
import html
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LONG_SENTENCE = 24
LONG_PARAGRAPH = 60

STAMPS = {
    "на самом деле": r"на самом деле",
    "давайте / представьте себе / вот что": r"\b(?:давайте|представьте себе|вот что)\b",
    "является / представляет собой": r"\b(?:являет\w*|представля\w* собой)\b",
    "ключевой / важнейший / уникальный": r"\b(?:ключев|важнейш|уникальн|неотъемлем)\w*",
    "хочет одного: / выдаёт одно:": r"\b(?:одного|одно):",
    "в этой статье / эта статья —": r"\bв этой статье\b|\bэта статья —",
    "кроме того": r"\bкроме того\b",
    "по сути / буквально": r"\b(?:по сути|буквально)\b",
    "«мы»": r"\b(?:мы|нам|нас|наш|наша|наше|наши|нашего|нашей|нашему|нашим|наших|нашими|нашу)\b",
}
FOR_EYES = {
    "просто": r"\bпросто\b",
    "очень": r"\bочень\b",
    "не …, а …": r"\bне [^.,:;!?]{1,40}, а\b",
    "не просто / не только": r"\bне (?:просто|только)\b",
    "действительно": r"\bдействительно\b",
    # частота и доля без замера — прикидка: «самый частый тупик», «половину из них» (D202, 06.10.2026)
    "самый частый / чаще всего / половина": r"\bсам\w+ част\w+|\bчаще всего\b|\bполовин\w+|\bбольшинств\w+",
}

parser = argparse.ArgumentParser()
parser.add_argument("files", nargs="+")
parser.add_argument("--glavred", action="store_true")
args = parser.parse_args()

checks = []


def check(name, ok, note=""):
    checks.append((name, bool(ok)))
    if not ok:
        print("  FAIL %s%s" % (name, (" · " + note) if note else ""))


def words(s):
    return re.findall(r"[A-Za-zА-Яа-яЁё0-9]+(?:-[A-Za-zА-Яа-яЁё0-9]+)*", s)


def text_part(raw):
    parts = raw.split("\n---\n", 1)
    body = parts[1] if len(parts) > 1 else raw
    body = re.sub(r"^(?:Кампания|Текст):.*$", "", body, flags=re.M)
    body = re.sub(r"^## Дальше\n.*", "", body, flags=re.S)
    # картинка и карточка ссылки — вставки редактора площадки, а не текст
    return re.sub(r"\[(?:картинка|карточка ссылки)[^\]]*\]", "", body)


def lesson_part(raw):
    """Урок сайта (`*.body.html`): абзацы и пункты списков текстом, без «Что почитать дальше» и шаблонов в `<pre>`.

    Текст тренажёра «вычеркните лишнее» (`data-strike-text`) — нарочно плохой образец, а не голос урока:
    «Наши специалисты делают всё возможное» читатель как раз вычёркивает (06.10.2026).

    Блок, который читатель копирует себе кнопкой (`data-copy="id"`), — его документ, как шаблон в `<pre>`:
    план интервью «О чём мы ещё не поговорили?» и формат «Как мы проводим интервью» пишутся голосом
    читателя и его команды, а не урока (06.10.2026). Образец без кнопки копирования помечают
    `data-sample` на рамке: вопросы скринера, шаблон обоснования выборки."""
    starts = [re.search(r'<(\w+)\b[^>]*\bid="%s"' % re.escape(t), raw) for t in set(re.findall(r'data-copy="([^"]+)"', raw))]
    starts += list(re.finditer(r'<(\w+)\b[^>]*\bdata-sample\b', raw))
    # с конца файла: вырезанный блок не сдвигает позиции тех, что выше
    for m in sorted((m for m in starts if m and m.group(1) != "pre"), key=lambda m: -m.start()):
        tag, depth, pos = m.group(1), 0, m.start()
        for t in re.finditer(r"<(/?)%s\b[^>]*>" % tag, raw[pos:]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                raw = raw[:pos] + raw[pos + t.end():]
                break
    raw = re.sub(r'<section id="further-reading">.*?</section>|<pre.*?</pre>|<p[^>]*data-strike-text[^>]*>.*?</p>',
                 "", raw, flags=re.S)
    # <q> на странице рисует «ёлочки» — для проверки это та же цитата-образец
    raw = re.sub(r"<q\b[^>]*>(.*?)</q>", r"«\1»", raw, flags=re.S)
    out = []
    for tag, inner in re.findall(r"<(p|li)\b[^>]*>(.*?)</\1>", raw, flags=re.S):
        # пункт викторины — вопрос и разбор отдельными абзацами: склеенные, они давали одну «фразу» в 26 слов
        parts = re.findall(r"<p\b[^>]*>(.*?)</p>", inner, flags=re.S) if tag == "li" and "<p" in inner else [inner]
        # пустая строка внутри абзаца (<br><br>) на экране — граница абзацев: разбор «Что сломано… / Что сказать вместо…»
        parts = [c for part in parts for c in re.split(r"<br\s*/?>\s*<br\s*/?>", part)]
        for part in parts:
            t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", part))).strip()
            if t:
                out.append(t)
    return "\n\n".join(out)


GLAVRED_LIMIT = 5000  # 10 700 и 8 900 знаков Главред не досчитал (06.10.2026), 2 000 — да: делим по абзацам


def glavred_chunks(text):
    chunks, cur = [], ""
    for para in re.split(r"\n\s*\n", text):
        if cur and len(cur) + len(para) > GLAVRED_LIMIT:
            chunks.append(cur)
            cur = ""
        cur = (cur + "\n\n" + para) if cur else para
    return chunks + [cur] if cur else chunks


def glavred(text):
    from playwright.sync_api import sync_playwright
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for chunk in glavred_chunks(text):
            pg = b.new_page(viewport={"width": 1440, "height": 1000})
            pg.goto("https://glvrd.ru/", timeout=30000)
            pg.wait_for_timeout(2500)
            ed = pg.locator("[contenteditable=true]").first
            ed.click()
            ed.evaluate("(el, t) => { el.focus(); document.execCommand('insertText', false, t); }", chunk)
            # Сразу после вставки Главред показывает «10 баллов, 0 стоп-слов» и досчитывает позже:
            # ждём, пока счёт стоп-слов (через неразрывный пробел) три секунды подряд не меняется.
            pg.wait_for_timeout(6000)
            last, same = None, 0
            for _ in range(40):
                m = re.search(r"(\d+)\s+стоп-слов", pg.inner_text("body"))
                cur = m.group(1) if m else None
                same = same + 1 if cur is not None and cur == last else 0
                last = cur
                if same >= 3:
                    break
                pg.wait_for_timeout(1000)
            lines = [l.replace("\xa0", " ").strip() for l in pg.inner_text("body").splitlines() if l.strip()]
            pg.close()
            i = next((k for k, l in enumerate(lines) if re.search(r"балл\w* из 10", l)), None)  # «балла» или «баллов»
            ok = i is not None and any(re.search(r"\d+\s+стоп-слов", l) for l in lines)
            out.append(" · ".join(lines[i - 1:i + 5]) if ok else "оценка не найдена (%d знаков)" % len(chunk))
        b.close()
    return "\n  Главред: ".join(out)


for f in args.files:
    path = pathlib.Path(f)
    raw = path.read_text(encoding="utf-8")
    # урок с 06.10.2026 пишется в стиле образца автора (D200, D201) и проверяется теми же мерками
    body = lesson_part(raw) if path.suffix == ".html" else text_part(raw)
    print("== %s" % path.as_posix())
    for url in re.findall(r"\[карточка ссылки (\S+)\]", raw):
        check("адрес карточки без меток — с «?» редактор vc.ru карточку не делает", "?" not in url, url)
    for label, href in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", body):
        check("ссылка вшита в слова, а не в адрес", not re.search(r"https?://|\w\.\w{2,}/", label), "«%s»" % label)
    plain = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    for url in re.findall(r"https?://\S+", plain):
        check("нет голого адреса в тексте", False, url[:80])
    paras = [p.strip() for p in re.split(r"\n\s*\n", plain) if p.strip()]
    for p in paras:
        quote_lines = [l for l in p.split("\n") if l.startswith("> ")]
        check("цитата в одну строку — многострочную редактор vc.ru склеивает", len(quote_lines) <= 1, p[:70])
    prose = [p for p in paras if not re.match(r"^(?:#|- |— |> |---)", p)]
    for p in prose:
        n = len(words(p))
        check("абзац не длиннее %d слов" % LONG_PARAGRAPH, n <= LONG_PARAGRAPH, "%d · %s…" % (n, p[:70]))
        # пункты списка в посте («— …») и строки после двоеточия — отдельные фразы
        for s in re.split(r"\n|(?<=[.!?…])\s+(?=[«А-ЯЁA-Z0-9])", p):
            n = len(words(s))
            check("фраза не длиннее %d слов" % LONG_SENTENCE, n <= LONG_SENTENCE, "%d · %s…" % (n, s[:70]))
    for name, rx in STAMPS.items():
        # цитата в «ёлочках» — пример, а не голос автора: «Вчера мы всё поменяли», реплика
        # интервьюера «Давайте вернёмся к моменту…» (06.10.2026) — штампы в ней не считаются
        hits = re.findall(rx, re.sub(r"«[^»]*»", "", plain), re.I)
        check("нет штампа: " + name, not hits, ", ".join(dict.fromkeys(h.lower() for h in hits)))
    for name, rx in FOR_EYES.items():
        for m in re.finditer(rx, plain, re.I):
            print("  глазами · %s · …%s…" % (name, plain[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")))
    if args.glavred:
        g = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
        g = re.sub(r"^#+ |^> |\*\*", "", g, flags=re.M).replace("\n---\n", "\n")
        print("  Главред: %s" % glavred(g))

fails = [c for c in checks if not c[1]]
print("проверок: %d, провалов: %d" % (len(checks), len(fails)))
sys.exit(1 if fails else 0)
