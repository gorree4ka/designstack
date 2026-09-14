"""Демо-контент каталога: ресурсы, подборки и дайджест из scripts/seed_data.json.

    python scripts/seed.py           наполнить или обновить
    python scripts/seed.py --reset   удалить только записи с меткой _designstack_seed
    python scripts/seed.py --check   проверить данные, ничего не записывая

Идемпотентно: запись ищется по слагу, существующая обновляется, а не создаётся заново.
Перед записью данные проверяются на покрытие значений — этап 13 собирает по ним страницы,
и если в демо не окажется, скажем, закрытого ресурса, состояние «Закрыт» будет негде посмотреть.

Тяжёлую часть делает scripts/seed.php одним вызовом WP-CLI: на Windows каждый вызов
стоит около полусекунды, а полей здесь под четыре сотни — отдельными командами
наполнение шло бы минуты. Запись идёт функциями плагина, то есть через ту же
санитизацию, что и правки в редакторе.
"""
import argparse
import json
import pathlib
import subprocess
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "scripts" / "seed_data.json"
SEED_PHP = ROOT / "scripts" / "seed.php"
WP = ["cmd", "/" + "c", str(ROOT / "tools" / "wp.cmd"), "--path=wordpress"]

# Что обязано быть в демо, чтобы этапу 13 было на чём проверять состояния.
REQUIRED = {
    "pricing": {"free", "freemium", "paid", "trial"},
    "ru_open": {"open", "vpn_only", "blocked"},
    # payable — зарубежный сервис, который оплачивается российской картой напрямую.
    # Среди проверенных ресурсов таких не нашлось, и это факт рынка, а не пропуск в данных:
    # метка у payable и ru_native одна и та же (зелёная галочка), так что вёрстке есть что показать.
    "ru_payment": {"intermediary", "no_payment", "ru_native"},
    "status": {"active", "changed", "dead"},
}
EMPTY_TOPIC = "accessibility"
TODAY = "2026-09-12"


def wp(*args: str) -> str:
    done = subprocess.run(WP + list(args), cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if done.returncode != 0:
        sys.exit(f"WP-CLI упал: {' '.join(args)}\n{done.stdout}\n{done.stderr}")
    return (done.stdout or "").strip()


def check(data: dict) -> list[str]:
    """Возвращает список замечаний к данным. Пустой список — данные годятся."""
    problems: list[str] = []
    resources = data["resources"]

    slugs = [item["slug"] for item in resources]
    doubles = [slug for slug, count in Counter(slugs).items() if count > 1]
    if doubles:
        problems.append(f"слаги повторяются: {', '.join(doubles)}")

    by_type = Counter(item["type"] for item in resources)
    for kind in ("tool", "learning", "asset", "community"):
        if not 6 <= by_type[kind] <= 8:
            problems.append(f"тип {kind}: {by_type[kind]} записей, нужно 6–8")

    if not 24 <= len(resources) <= 32:
        problems.append(f"всего {len(resources)} ресурсов, нужно 24–32")

    for key, needed in REQUIRED.items():
        seen = {item["fields"].get(key) for item in resources}
        missing = needed - seen
        if missing:
            problems.append(f"поле {key}: не покрыты значения {', '.join(sorted(missing))}")

    free_without_payment = [
        item["slug"] for item in resources
        if item["fields"].get("pricing") == "free" and "ru_payment" not in item["fields"]
    ]
    if not free_without_payment:
        problems.append("нет бесплатного ресурса без поля оплаты (D28)")

    if not any(item["fields"].get("checked_at", "") < "2026-06-14" for item in resources):
        problems.append("нет ресурса с проверкой старше 90 дней")

    if not any(item["fields"].get("checked_at", "") >= "2026-09-01" for item in resources):
        problems.append("нет ресурса со свежей проверкой")

    longest = max(len(item["title"]) for item in resources)
    if longest < 70:
        problems.append(f"самое длинное название {longest} знаков, нужно около 80 для проверки вёрстки")

    used_topics = {topic for item in resources for topic in item["topics"]}
    if EMPTY_TOPIC in used_topics:
        problems.append(f"тема {EMPTY_TOPIC} должна остаться пустой — на ней проверяется пустое состояние")

    without_analogs = [item["slug"] for item in resources if item["fields"].get("status") == "dead"
                       and not item.get("analogs")]
    if without_analogs:
        problems.append(f"у закрытого ресурса нет аналога: {', '.join(without_analogs)}")

    for item in resources:
        for part in ("review_for", "review_why", "review_not"):
            if not item["fields"].get(part):
                problems.append(f"{item['slug']}: пустая часть оценки {part} — такая запись не публикуется (D32)")
        if item["fields"].get("checked_at", "") > TODAY:
            problems.append(f"{item['slug']}: дата проверки в будущем")

    known = set(slugs)
    for item in resources:
        for analog in item.get("analogs", []):
            if analog not in known:
                problems.append(f"{item['slug']}: аналог {analog} не найден в данных")

    for post in data["posts"]:
        for slug in post["resources"]:
            if slug not in known:
                problems.append(f"{post['slug']}: ресурс {slug} не найден в данных")

    return problems


def prepare_site() -> list[str]:
    """Приводит сайт к карте URL этапа 07: имя, страница политики, демо-записи установки."""
    done: list[str] = []

    if wp("option", "get", "blogname") != "DesignStack":
        wp("option", "update", "blogname", "DesignStack")
        done.append("имя сайта → DesignStack (D38)")

    privacy = wp("post", "list", "--post_type=page", "--name=privacy-policy", "--field=ID")
    if privacy:
        wp("post", "update", privacy, "--post_name=privacy")
        done.append("страница политики получила слаг privacy")

    for slug in ("hello-world", "sample-page"):
        found = wp("post", "list", "--post_type=any", "--post_status=any", f"--name={slug}", "--field=ID")
        if found:
            wp("post", "delete", found, "--force")
            done.append(f"удалена демо-запись установки {slug}")

    return done


def main() -> None:
    parser = argparse.ArgumentParser(description="Демо-контент каталога DesignStack")
    parser.add_argument("--reset", action="store_true", help="удалить записи с меткой _designstack_seed")
    parser.add_argument("--check", action="store_true", help="только проверить данные")
    args = parser.parse_args()

    data = json.loads(DATA.read_text(encoding="utf-8"))
    problems = check(data)

    for line in problems:
        print(f"данные: {line}")

    if problems and not args.reset:
        sys.exit("наполнение остановлено: сначала поправь scripts/seed_data.json")

    if args.check:
        print("данные в порядке")
        return

    if not args.reset:
        for line in prepare_site():
            print(f"сайт: {line}")

    mode = "reset" if args.reset else "apply"
    out = wp("eval-file", str(SEED_PHP).replace("\\", "/"), mode)

    numbers = {"created": 0, "updated": 0, "removed": 0}
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("created="):
            for pair in line.split():
                key, _, value = pair.partition("=")
                numbers[key] = int(value)
        elif line:
            print(line)

    print(f"создано {numbers['created']} / обновлено {numbers['updated']} / удалено {numbers['removed']}")


if __name__ == "__main__":
    main()
