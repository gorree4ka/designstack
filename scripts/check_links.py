"""Перепроверка ссылок каталога: живость, редиректы, смена заголовка страницы.

Директива 16, фаза 6. Скрипт **ничего не меняет** в WordPress: он собирает факты и
пишет отчёт, статусы проставляет куратор после апрува.

Что проверяется:
- код ответа (`HEAD`, при 403/405/501 — повтор `GET` с первыми килобайтами);
- финальный адрес после редиректов — уход на другой домен виден отдельно;
- `<title>` страницы и сравнение с сохранённым в `docs/content/recheck_state.json`;
- возраст `checked_at` — старше 90 дней уходит в очередь на перепроверку (brief A8).

Чего скрипт НЕ проверяет: доступность и оплату из России. Это три пробы фазы 1.5,
одна из них требует российского IP (`scripts/check_ru_access.py`, O8).

Запуск:
    python scripts/check_links.py
    python scripts/check_links.py --timeout 20 --stale-days 90
"""
import argparse
import datetime as dt
import html
import json
import pathlib
import re
import socket
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE = ROOT / "docs/content/recheck_state.json"
EXPORT = ROOT / "scripts/export_resources.php"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")

# Коды, которые говорят о защите от роботов, а не о состоянии сайта.
BOT_BLOCK = (401, 403, 429, 503)

parser = argparse.ArgumentParser()
parser.add_argument("--timeout", type=int, default=15)
parser.add_argument("--stale-days", type=int, default=90)
parser.add_argument("--today", default=dt.date.today().isoformat(), help="дата прогона, ГГГГ-ММ-ДД")
parser.add_argument("--out", default="", help="куда писать отчёт; по умолчанию docs/content/recheck_<дата>.md")
parser.add_argument("--force", action="store_true",
                    help="перезаписать отчёт этого дня; без флага повторный прогон его не трогает")
args = parser.parse_args()

TODAY = dt.date.fromisoformat(args.today)
OUT = pathlib.Path(args.out) if args.out else ROOT / f"docs/content/recheck_{TODAY.isoformat()}.md"


def catalogue() -> list:
    """Каталог из WordPress одним вызовом WP-CLI."""
    # Аргумент с ведущим «/» ломается в Git Bash, поэтому "/" собирается из кусков.
    run = subprocess.run(
        ["cmd", "/" + "c", str(ROOT / "tools" / "wp.cmd"), "--path=wordpress",
         "eval-file", str(EXPORT).replace("\\", "/")],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    body = run.stdout.strip()
    start = body.find("[")

    if start < 0:
        raise SystemExit(f"WP-CLI не отдал JSON:\n{body[:500]}\n{run.stderr[:500]}")

    return json.loads(body[start:])


def normalise(url: str) -> str:
    """Адрес без www, utm и завершающего слеша — по нему ищем дубли и уход на другой домен."""
    parts = urllib.parse.urlsplit(url.strip())
    host = parts.netloc.lower().removeprefix("www.")
    query = "&".join(q for q in parts.query.split("&") if q and not q.startswith("utm_"))

    return urllib.parse.urlunsplit((parts.scheme or "https", host, parts.path.rstrip("/"), query, ""))


def fetch(url: str, method: str, limit: int = 0) -> dict:
    """Один запрос. Возвращает код, финальный адрес и тело, если просили."""
    headers = {"User-Agent": UA, "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8"}

    if limit:
        headers["Range"] = f"bytes=0-{limit}"

    request = urllib.request.Request(url, method=method, headers=headers)
    context = ssl.create_default_context()

    try:
        with urllib.request.urlopen(request, timeout=args.timeout, context=context) as response:
            body = response.read(limit).decode("utf-8", "replace") if limit else ""

            return {"code": response.status, "final": response.geturl(), "body": body, "error": ""}
    except urllib.error.HTTPError as error:
        return {"code": error.code, "final": error.url, "body": "", "error": ""}
    except (urllib.error.URLError, socket.timeout, ssl.SSLError, ConnectionError) as error:
        reason = getattr(error, "reason", error)

        return {"code": 0, "final": url, "body": "", "error": str(reason)[:80]}


def page_title(body: str) -> str:
    """Заголовок страницы; пусто, если тега нет в первых килобайтах."""
    found = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)

    return re.sub(r"\s+", " ", html.unescape(found.group(1))).strip()[:120] if found else ""


def probe(url: str) -> dict:
    """Проверка адреса: HEAD, при отказе — GET; нестабильный ответ проверяется дважды."""
    result = fetch(url, "HEAD")

    # Часть сайтов отвечает на HEAD отказом, хотя страница живая.
    if result["code"] in (0, 403, 405, 501) or result["code"] >= 500:
        result = fetch(url, "GET", limit=4096)

    # Мёртвым считаем только то, что не ответило дважды: разовый таймаут — не смерть.
    if result["code"] == 0 or result["code"] >= 500:
        second = fetch(url, "GET", limit=4096)

        if second["code"] and second["code"] < 500:
            result = second

    if not result["body"] and 200 <= result["code"] < 300:
        result = {**result, **{k: v for k, v in fetch(result["final"], "GET", limit=4096).items() if k == "body"}}

    return result


def main() -> None:
    rows = catalogue()
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    report, fresh = [], {}

    for row in rows:
        url = row["url"]

        if not url:
            report.append({**row, "verdict": "нет адреса", "code": "—", "final": "", "title": "", "note": "поле url пустое"})
            continue

        result = probe(url)
        title = page_title(result["body"])
        was = state.get(row["slug"], {})
        code = result["code"]
        moved = normalise(result["final"]) != normalise(url)
        other_host = urllib.parse.urlsplit(normalise(result["final"])).netloc != urllib.parse.urlsplit(normalise(url)).netloc

        notes = []
        verdict = "жив"

        if code == 0:
            verdict, notes = "не ответил", [result["error"]]
        elif code in (404, 410):
            verdict, notes = "мёртв", [f"код {code}"]
        elif code in BOT_BLOCK:
            # Код ответа — это не живость. 429 — лимит запросов, 403 и 503 у Cloudflare —
            # защита от роботов: сайт открыт для человека, но закрыт для скрипта.
            # Такое проверяется руками, статус записи от этого не меняется.
            verdict, notes = "закрыт от робота", [f"код {code}"]
        elif code >= 400:
            verdict, notes = "проверить", [f"код {code}"]

        if other_host:
            verdict = "мёртв" if verdict == "мёртв" else "сменил адрес"
            notes.append(f"→ {result['final']}")
        elif moved:
            notes.append("редирект внутри домена")

        old_title = was.get("title", "")

        if old_title and title and title != old_title:
            same = len(set(old_title.lower().split()) & set(title.lower().split()))

            if same * 2 < max(len(old_title.split()), 1):
                verdict = "сменил адрес" if verdict == "жив" else verdict
                notes.append(f"заголовок: «{old_title}» → «{title}»")

        age = None

        if row["checked_at"]:
            try:
                age = (TODAY - dt.date.fromisoformat(row["checked_at"])).days
            except ValueError:
                notes.append("дата проверки нечитаема")

        if age is not None and age > args.stale_days:
            notes.append(f"проверено {age} дней назад")

        report.append({**row, "verdict": verdict, "code": code, "final": result["final"],
                       "title": title, "note": "; ".join(n for n in notes if n), "age": age})
        fresh[row["slug"]] = {"url": url, "final": result["final"], "title": title or old_title,
                              "code": code, "seen": TODAY.isoformat()}

        print(f"{row['slug']:34} {code!s:>4}  {verdict:14} {row['title'][:28]}")

    write_report(report)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(fresh, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(f"состояние: {STATE}")


def write_report(report: list) -> None:
    """Отчёт в формате директивы: таблица, счётчики, просроченные."""
    counts = {}

    for row in report:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1

    stale = [r for r in report if r.get("age") is not None and r["age"] > args.stale_days]
    problems = [r for r in report if r["verdict"] not in ("жив", "закрыт от робота")]
    manual = [r for r in report if r["verdict"] == "закрыт от робота"]

    lines = [
        f"# Перепроверка каталога: {TODAY.isoformat()}",
        "",
        f"Записей проверено: {len(report)}. "
        + ", ".join(f"{k} — {v}" for k, v in sorted(counts.items()))
        + f". Старше {args.stale_days} дней: {len(stale)}.",
        "",
        "Скрипт `scripts/check_links.py` ничего не менял в записях: статусы проставляются после апрува.",
        "Доступ и оплата из России здесь не проверяются — это три пробы фазы 1.5 директивы 16.",
        "",
        "## Требуют решения",
        "",
    ]

    if problems:
        lines += ["| slug | было | стало | причина | предложение |", "|---|---|---|---|---|"]

        for row in problems:
            lines.append(
                f"| {row['slug']} | {row['state'] or '—'} · {row['url']} | код {row['code']} | "
                f"{row['note'] or '—'} | {'подобрать аналог' if row['verdict'] == 'мёртв' else 'сверить карточку'} |"
            )
    else:
        lines.append("Ни одной мёртвой или сменившей адрес ссылки.")

    lines += ["", "## Закрыты от робота — проверить руками", ""]

    if manual:
        lines += ["| slug | код | адрес | что это значит |", "|---|---|---|---|"]
        for row in manual:
            lines.append(
                f"| {row['slug']} | {row['code']} | {row['url']} | "
                "защита от роботов, не состояние сайта: открыть браузером |"
            )
    else:
        lines.append("Нет.")

    lines += ["", "## Просроченные (перепроверить по брифу A8)", ""]

    if stale:
        lines += ["| slug | тип | проверено | дней назад |", "|---|---|---|---|"]
        for row in sorted(stale, key=lambda r: -r["age"]):
            lines.append(f"| {row['slug']} | {row['type']} | {row['checked_at']} | {row['age']} |")
    else:
        lines.append("Нет.")

    lines += ["", "## Полный прогон", "", "| slug | тип | код | итог | заголовок страницы | примечание |", "|---|---|---|---|---|---|"]

    for row in sorted(report, key=lambda r: r["slug"]):
        lines.append(
            f"| {row['slug']} | {row['type']} | {row['code']} | {row['verdict']} | "
            f"{row['title'] or '—'} | {row['note'] or '—'} |"
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    # В отчёт после прогона дописываются решения куратора. Повторный прогон того же дня
    # затёр бы их молча, поэтому готовый файл заменяется только по явному --force.
    if OUT.exists() and not args.force:
        spare = OUT.with_name(OUT.stem + "_повтор" + OUT.suffix)
        spare.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\r\n")
        print(f"отчёт за этот день уже есть, он не тронут; новый прогон — рядом: {spare}")

        return

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\r\n")


if __name__ == "__main__":
    sys.exit(main())
