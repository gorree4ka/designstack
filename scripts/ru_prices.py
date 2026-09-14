"""Снимает цены со страниц тарифов с российского IP.

Нужен, потому что страницы тарифов локализуются по адресу посетителя: Tilda
показала нероссийскому IP доллары, а российскому — рубли (находка 14.09.2026).
Цена, снятая не из России, — это не та цена, которую увидит наш читатель.

Запуск только на сервере в РФ:  python3 scripts/ru_prices.py scripts/<список>.txt
Строка списка: «адрес | слаг записи».
"""
import json
import re
import sys
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
PRICE = re.compile(r"[^<>\n]{0,60}(?:\d[\d\s ]{2,}\s?(?:₽|руб)|[$€£]\s?\d+)[^<>\n]{0,60}")
TAG = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.S | re.I)


def country():
    req = urllib.request.Request("https://ipinfo.io/json", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r).get("country", "??")


def text(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ru-RU,ru;q=0.9"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")
    raw = TAG.sub(" ", raw)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw))


def main():
    c = country()
    print("Страна IP:", c)
    if c != "RU":
        print("ОСТАНОВЛЕНО: цены имеет смысл снимать только с российского адреса")
        return 1
    for line in open(sys.argv[1], encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        url, _, slug = [p.strip() for p in line.partition("|")]
        print("=" * 12, slug or url)
        try:
            found, seen = 0, set()
            for m in PRICE.finditer(text(url)):
                s = m.group(0).strip()
                if s in seen:
                    continue
                seen.add(s)
                print("   ", s[:150])
                found += 1
                if found >= 12:
                    break
            if not found:
                print("    цен на странице не видно")
        except Exception as exc:
            print("    ОШИБКА:", str(exc)[:120])
    return 0


sys.exit(main())
