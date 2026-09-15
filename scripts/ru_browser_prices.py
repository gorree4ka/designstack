"""Снимает цены браузером, но глазами из России.

Зачем нужен отдельно от `ru_prices.py`. Тот читает разметку и справляется, пока
цена лежит в HTML. Но часть каталога живёт на страницах, где цену привозит скрипт
уже после загрузки: роботу достаётся пустой документ, и цены нет ни в разметке,
ни в данных страницы. Нужен настоящий браузер.

Но браузер на рабочей машине смотрит из Казахстана, а цена зависит от страны
посетителя: 15.09.2026 IxDF показал Казахстану $12, а России — $22. Поэтому
браузер запускается здесь, а трафик уходит через сервер в России.

Перед запуском поднять туннель (окно не закрывать, либо запустить с -f):

    ssh -f -N -D 1081 -o ExitOnForwardFailure=yes designstack

Запуск:

    python scripts/ru_browser_prices.py .tmp/список.txt [--port 1081] [--out docs/content/sources]

Строка списка: «адрес | слаг записи». Скрипт сам проверяет, что выход в сеть
российский, и без этого не работает: иначе он молча собрал бы казахстанские цены,
а отличить их по кадру невозможно.
"""
import argparse
import json
import pathlib
import re
import sys

from playwright.sync_api import sync_playwright

MONEY = re.compile(
    r"[^\n]{0,70}(?:\d[\d\s ]{2,}\s?(?:₽|руб)|[$€£]\s?\d[\d\s.,]*|\d+\s?(?:USD|EUR|RUB))[^\n]{0,70}"
)

p = argparse.ArgumentParser()
p.add_argument("list", help="файл со строками «адрес | слаг»")
p.add_argument("--port", type=int, default=1081, help="локальный порт SOCKS-туннеля")
p.add_argument("--out", default="docs/content/sources", help="куда класть кадры")
p.add_argument("--date", default="2026-09-15", help="дата в имени кадра")
a = p.parse_args()

out_dir = pathlib.Path(a.out)
out_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as pw:
    browser = pw.chromium.launch(proxy={"server": f"socks5://127.0.0.1:{a.port}"})
    page = browser.new_page(
        viewport={"width": 1440, "height": 900},
        locale="ru-RU",
        extra_http_headers={"Accept-Language": "ru-RU,ru;q=0.9"},
    )

    # Замер страны — до всего остального. Кадр из неправильной страны хуже, чем его отсутствие.
    page.goto("https://ipinfo.io/json", wait_until="domcontentloaded", timeout=60000)
    where = json.loads(page.inner_text("body"))
    print("Страна выхода:", where.get("country"), "|", where.get("org"), "|", where.get("city"))

    if where.get("country") != "RU":
        print("ОСТАНОВЛЕНО: туннель не в Россию. Подними его и повтори:")
        print("    ssh -f -N -D", a.port, "-o ExitOnForwardFailure=yes designstack")
        browser.close()
        sys.exit(1)

    for line in open(a.list, encoding="utf-8"):
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        url, _, slug = [x.strip() for x in line.partition("|")]
        slug = slug or re.sub(r"\W+", "-", url)[:40]
        print("=" * 14, slug)

        try:
            page.goto(url, wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(2500)

            shot = out_dir / f"{a.date}_{slug}-pricing.png"
            page.screenshot(path=str(shot), full_page=True)

            text = re.sub(r"[ \t ]+", " ", page.inner_text("body"))
            seen, found = set(), 0

            for m in MONEY.finditer(text):
                s = m.group(0).strip()
                key = s.lower()

                if key in seen:
                    continue

                seen.add(key)
                print("    ", s[:150])
                found += 1

                if found >= 14:
                    break

            if not found:
                print("     цен на странице не видно")

            print("     кадр:", shot)
        except Exception as exc:
            print("     ОШИБКА:", exc)

    browser.close()
