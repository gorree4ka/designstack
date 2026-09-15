"""Сбор адресов каталога для проверки доступа из России.

Навык `catalog-content`, фаза 1.5. Главная страница пробой не считается: «открывается» проверяется
на странице входа или регистрации, «оплачивается» — на странице тарифов или оплаты.
Эти адреса не выдумываются, а находятся на самом сайте: скрипт открывает главную
браузером и берёт ссылки, подписанные «Log in», «Pricing», «Войти», «Тарифы».

Результат — `scripts/ru_access_catalog.txt` в формате списка для `check_ru_access.py`:
«адрес | что проверяем | где утверждение». Файл потом уезжает на сервер в РФ.

Запуск: python scripts/collect_ru_urls.py
"""
import io
import json
import pathlib
import re
import subprocess
import urllib.parse

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts" / "ru_access_catalog.txt"

# Подписи ссылок, по которым узнаём вход и оплату. Ищем по видимому тексту, а не по пути:
# у части сайтов вход лежит на /auth, у части — на поддомене.
WANTED = (
    ("вход", ("log in", "login", "sign in", "sign up", "get started", "войти", "вход", "регистрация")),
    ("оплата", ("pricing", "plans", "upgrade", "pro", "тарифы", "цены", "подписка", "купить")),
)


def catalogue() -> list:
    run = subprocess.run(
        ["cmd", "/" + "c", str(ROOT / "tools" / "wp.cmd"), "--path=wordpress",
         "eval-file", str(ROOT / "scripts" / "export_resources.php").replace("\\", "/")],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    body = run.stdout

    return json.loads(body[body.find("["):])


def same_site(a: str, b: str) -> bool:
    """Ссылка считается своей, если совпадает корневой домен: вход часто живёт на поддомене."""
    host_a = urllib.parse.urlsplit(a).netloc.lower().removeprefix("www.")
    host_b = urllib.parse.urlsplit(b).netloc.lower().removeprefix("www.")

    return host_a.split(".")[-2:] == host_b.split(".")[-2:]


def main() -> None:
    rows = [r for r in catalogue() if r["url"] and r["state"] != "dead"]
    lines = [
        "# Адреса каталога для scripts/check_ru_access.py, собраны scripts/collect_ru_urls.py.",
        "# Формат: «адрес | что проверяем | где утверждение». Вход и оплата найдены на самих сайтах.",
    ]

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 1000}, locale="en-US")

        for row in rows:
            url, slug = row["url"], row["slug"]
            found = {}

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(2500)
                links = page.evaluate(
                    """() => [...document.querySelectorAll('a[href]')]
                        .map(a => ({text: (a.innerText || a.getAttribute('aria-label') || '').trim().toLowerCase(),
                                    href: a.href}))
                        .filter(l => l.text && l.text.length < 24 && l.href.startsWith('http'))"""
                )
            except Exception as error:
                print(f"{slug:24} не открылся отсюда: {str(error)[:60]}")
                links = []

            for kind, words in WANTED:
                for link in links:
                    if kind in found:
                        break
                    if any(re.fullmatch(rf"{re.escape(w)}\s*→?", link["text"]) or link["text"] == w for w in words):
                        if same_site(url, link["href"]):
                            found[kind] = link["href"].split("?")[0]

            lines.append(f"{url} | главная, {row['type']} | каталог: {slug}")

            for kind, address in found.items():
                lines.append(f"{address} | {kind}, {row['type']} | каталог: {slug}")

            print(f"{slug:24} {'вход ✓' if 'вход' in found else 'вход —':10} {'оплата ✓' if 'оплата' in found else 'оплата —'}")

        browser.close()

    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print(f"\nадресов: {len(lines) - 2}, файл: {OUT}")


if __name__ == "__main__":
    main()
