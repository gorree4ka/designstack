"""Проверка доступности сайтов из России с замером страны IP.

Сначала скрипт определяет страну исходящего IP. Если она не RU, он останавливается
и ничего не проверяет: прогон через VPN или из другой страны ничего не говорит
о доступности из России (O8 в docs/DECISIONS.md).

Запуск с выключенным VPN:
    python scripts/check_ru_access.py
Отладка с нероссийского IP (отчёт уходит в .tmp/ и помечен как недействительный):
    python scripts/check_ru_access.py --debug-non-ru

Список адресов: scripts/ru_access_urls.txt, строка «адрес | что проверяем | где утверждение».
Отчёт: docs/research/ru-access/<ГГГГ-ММ-ДД_ЧЧ-ММ>.md.
Итог «открывается» значит только ответ 2xx без текста о блокировке;
вход, регистрацию и оплату скрипт не проверяет.
"""
import argparse
import datetime as dt
import json
import pathlib
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL_LIST = ROOT / "scripts" / "ru_access_urls.txt"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
GEO_SERVICES = ["https://ipinfo.io/json", "https://ipapi.co/json/", "https://api.country.is/"]
BLOCK_MARKERS = [
    "not available in your country", "not available in your region",
    "unavailable in your region", "not available in russia", "error 1009",
    "has banned the country", "недоступен в вашем регионе", "недоступно в вашем регионе",
    "недоступен в вашей стране", "недоступно в вашей стране",
]
TIMEOUT = 20


def fetch(url, limit=65536):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ru,en;q=0.8"})
    start = time.monotonic()

    def result(code=0, final=url, body=b"", error=""):
        return {"code": code, "final": final, "body": body, "error": error,
                "sec": time.monotonic() - start}

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return result(r.status, r.geturl(), r.read(limit))
    except urllib.error.HTTPError as e:
        try:
            body = e.read(limit)
        except Exception:
            body = b""
        return result(e.code, e.geturl() or url, body)
    except urllib.error.URLError as e:
        reason = e.reason
        if isinstance(reason, socket.gaierror):
            return result(error="DNS не резолвится")
        if isinstance(reason, (socket.timeout, TimeoutError)):
            return result(error="таймаут")
        if isinstance(reason, ssl.SSLError):
            return result(error="ошибка TLS")
        if isinstance(reason, ConnectionResetError):
            return result(error="соединение сброшено")
        return result(error="ошибка сети: " + str(reason)[:80])
    except (socket.timeout, TimeoutError):
        return result(error="таймаут")
    except ConnectionResetError:
        return result(error="соединение сброшено")
    except Exception as e:  # RemoteDisconnected, IncompleteRead и прочее
        return result(error=type(e).__name__)


def geo():
    for url in GEO_SERVICES:
        r = fetch(url)
        if r["code"] != 200:
            continue
        try:
            data = json.loads(r["body"].decode("utf-8", "ignore"))
        except ValueError:
            continue
        country = str(data.get("country_code") or data.get("country") or "").upper()
        if len(country) == 2:
            return {"country": country, "org": str(data.get("org") or data.get("asn") or "—"),
                    "service": url}
    return None


def verdict(r):
    if r["error"]:
        return "не открывается: " + r["error"]
    text = r["body"].decode("utf-8", "ignore").lower()
    marker = next((m for m in BLOCK_MARKERS if m in text), "")
    if marker:
        return "блок по тексту страницы: «" + marker + "»"
    if 200 <= r["code"] < 300:
        return "открывается"
    if r["code"] in (401, 403, 429):
        return "код %d — проверить в браузере (антибот или гео-блок)" % r["code"]
    if r["code"] == 451:
        return "код 451 — закрыто по юридическим причинам"
    return "код %d" % r["code"]


def read_list(path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")] + ["", ""]
        rows.append((parts[0], parts[1], parts[2]))
    return rows


def cell(value):
    return str(value).replace("|", "/")


def main():
    ap = argparse.ArgumentParser(description="Доступность сайтов из России с замером страны IP")
    ap.add_argument("--debug-non-ru", action="store_true",
                    help="прогнать с нероссийского IP; отчёт уходит в .tmp/ с пометкой")
    ap.add_argument("--urls", default=str(URL_LIST),
                    help="список адресов; по умолчанию scripts/ru_access_urls.txt")
    ap.add_argument("--tag", default="",
                    help="пометка в имени отчёта, чтобы прогоны разных списков не затирали друг друга")
    args = ap.parse_args()

    g = geo()
    if g is None:
        print("Не удалось определить страну IP ни одним сервисом. Проверка не запускалась.")
        return 3
    print("Страна IP: %s, сеть: %s (по %s)" % (g["country"], g["org"], g["service"]))
    valid = g["country"] == "RU"
    if not valid and not args.debug_non_ru:
        print("IP не российский, скорее всего включён VPN. Выключите VPN и запустите снова. "
              "Проверка не запускалась.")
        return 2

    url_list = pathlib.Path(args.urls)

    if not url_list.is_absolute():
        url_list = ROOT / url_list

    if not url_list.exists():
        print("Списка нет: %s" % url_list)
        return 4

    now = dt.datetime.now()
    results = []
    for url, what, where in read_list(url_list):
        r = fetch(url)
        v = verdict(r)
        results.append((url, what, where, v, r))
        print("%-48s %s" % (v, url))

    out_dir = ROOT / ("docs/research/ru-access" if valid else ".tmp/ru-access")
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = ("_" + args.tag) if args.tag else ""
    out = out_dir / (now.strftime("%Y-%m-%d_%H-%M") + tag + ".md")
    head = ("Страна IP: **RU**" if valid else
            "**Недействительно для выводов о России: страна IP %s, отладочный прогон**" % g["country"])
    lines = [
        "# Доступность из России — " + now.strftime("%d.%m.%Y %H:%M"),
        "",
        head + ", сеть: %s, определено через %s. Скрипт `scripts/check_ru_access.py`, "
               "список `%s`." % (cell(g["org"]), g["service"], url_list.name),
        "",
        "Итог «открывается» значит только ответ 2xx без текста о блокировке. "
        "Вход, регистрацию и оплату скрипт не проверяет.",
        "",
        "| Адрес | Что проверяем | Итог | Код | Конечный адрес | Время, с | Где утверждение |",
        "|---|---|---|---|---|---|---|",
    ]
    for url, what, where, v, r in results:
        lines.append("| %s | %s | %s | %s | %s | %.1f | %s |" % (
            cell(url), cell(what), cell(v), r["code"] or "—", cell(r["final"]), r["sec"], cell(where)))
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    opened = sum(1 for x in results if x[3] == "открывается")
    print("\nОткрывается: %d из %d. Отчёт: %s" % (opened, len(results), out.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
