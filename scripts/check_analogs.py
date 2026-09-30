"""Блок аналогов на странице ресурса: правило пар и заголовок (D187, лист P28).

Зачем. 30.09.2026 оказалось, что блок «Аналог из России» в 32 парах из 42 вёл на зарубежный сервис,
а в 13 — на ресурс другого назначения или с той же проблемой: у Jitter «аналогом» стоял Rive, который
из России тоже не оплатить, у v0 — закрытый из России Uizard. Правило теперь проверяется здесь.

Что проверяет:
1. Аналог опубликован, не закрыт и открывается из России.
2. Если у ресурса проблема только с оплатой, аналог её не повторяет: он бесплатный или
   оплачивается из России (payable, ru_native). Если ресурс закрыт или не открывается — аналогу
   хватит того, что он открывается (бесплатный тариф или оплату видно на его карточке).
3. На странице каждого ресурса с аналогами заголовок блока совпадает с D187:
   «Аналог, который работает из России» / «Аналоги, которые работают из России» — у ресурса
   с проблемой, «Аналог» / «Аналоги» — у остальных; число — по числу карточек.
4. Прежнее название блока не встречается в коде темы и плагина и в словаре сайта.
5. Поле аналога не ссылается на несуществующую запись: 30.09.2026 на живом сайте у Miro и Figma
   там стоял 0 — блока аналогов не было, а локально всё было на месте.

«То же ли дело делает аналог» скрипт не решает — это суждение куратора на листе решений.

    python scripts/check_analogs.py                      # данные — локальная база, страницы — localhost
    python scripts/check_analogs.py --base https://designstack.ru   # страницы — живой сайт
    python scripts/check_analogs.py --base https://designstack.ru --ssh designstack   # и данные с живого сайта
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent
OLD = "Аналог из России"
DUMP = r"""<?php
$f = function ( $id ) {
	return array(
		'slug' => get_post_field( 'post_name', $id ), 'status' => get_post_meta( $id, 'status', true ),
		'open' => get_post_meta( $id, 'ru_open', true ), 'pay' => get_post_meta( $id, 'ru_payment', true ),
		'pricing' => get_post_meta( $id, 'pricing', true ), 'publish' => 'publish' === get_post_status( $id ),
	);
};
$out = array();
foreach ( get_posts( array( 'post_type' => 'resource', 'post_status' => 'publish', 'numberposts' => -1, 'meta_key' => 'ru_alternative', 'fields' => 'ids' ) ) as $p ) {
	$row = $f( $p ); $row['alts'] = array(); $row['broken'] = array();
	foreach ( (array) get_post_meta( $p, 'ru_alternative' ) as $a ) {
		if ( get_post( (int) $a ) ) { $row['alts'][] = $f( (int) $a ); } else { $row['broken'][] = (string) $a; }
	}
	$out[] = $row;
}
echo wp_json_encode( $out );
"""

parser = argparse.ArgumentParser()
parser.add_argument("--base", default="http://localhost:8080")
parser.add_argument("--ssh", help="SSH-алиас хостинга: данные читаются из живой базы через wp-cli.phar")
args = parser.parse_args()

checks = []


def check(name, ok, note=""):
    checks.append((name, bool(ok), note))


def problem(r):
    if r["status"] == "dead" or r["open"] in ("blocked", "unstable"):
        return "access"
    if r["pricing"] != "free" and r["pay"] in ("no_payment", "intermediary"):
        return "payment"
    return ""


if args.ssh:
    # wp eval-file - читает код из STDIN: на хостинг ничего не копируется.
    raw = subprocess.run(["ssh", args.ssh, "cd ~/designstack/public_html && php8.3 /usr/local/bin/wp-cli.phar eval-file -"],
                         input=DUMP.encode("utf-8"), capture_output=True).stdout.decode("utf-8", "replace")
else:
    tmp = ROOT / ".tmp/check_analogs_dump.php"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_text(DUMP, encoding="utf-8")
    raw = subprocess.run([str(ROOT / "tools/wp.cmd"), "--path=wordpress", "eval-file", str(tmp)],
                         cwd=ROOT, capture_output=True).stdout.decode("utf-8", "replace")
data = json.loads(raw[raw.index("["):])
check("в базе есть ресурсы с аналогами", data, "пусто — значит, не прочиталась база")

for r in data:
    check("аналог ссылается на существующую запись: " + r["slug"], not r["broken"], "значения " + ", ".join(r["broken"]))
    prob = problem(r)
    for a in r["alts"]:
        pair = "%s → %s" % (r["slug"], a["slug"])
        check("аналог опубликован и не закрыт: " + pair, a["publish"] and a["status"] != "dead")
        check("аналог открывается из России: " + pair, a["open"] == "open", a["open"])
        if prob == "payment":
            check("аналог оплатить можно или он бесплатный: " + pair,
                  a["pricing"] == "free" or a["pay"] in ("payable", "ru_native"), "%s · %s" % (a["pricing"], a["pay"]))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "DesignStack-check"})
    return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")


for r in data:
    alive = [a for a in r["alts"] if a["publish"]]
    if not alive:
        continue
    html = fetch("%s/resource/%s/" % (args.base.rstrip("/"), r["slug"]))
    m = re.search(r'<section class="ds-section" id="analogs">.*?<h2 class="ds-section__title">(.*?)</h2>', html, re.S)
    cards = len(re.findall(r'<article class="ds-card', html[m.start():] if m else ""))
    one = len(alive) == 1
    want = (("Аналог, который работает из России" if one else "Аналоги, которые работают из России")
            if problem(r) else ("Аналог" if one else "Аналоги"))
    got = m.group(1).strip() if m else "(нет блока)"
    check("заголовок блока: " + r["slug"], got == want, "%s, а нужно %s" % (got, want))
    check("карточек в блоке столько же, сколько пар: " + r["slug"], cards == len(alive), "%d из %d" % (cards, len(alive)))

code = [p for d in ("wordpress/wp-content/themes/designstack", "wordpress/wp-content/plugins/designstack-core")
        for p in (ROOT / d).rglob("*") if p.suffix in (".php", ".js", ".json", ".html", ".md")]
hits = [str(p.relative_to(ROOT)) for p in code + [ROOT / "docs/VOICE.md"] if OLD in p.read_text(encoding="utf-8", errors="replace")]
check("прежнее название блока нигде не пишется", not hits, ", ".join(hits))

fails = [c for c in checks if not c[1]]
for name, ok, note in checks:
    if not ok:
        print("  ПРОВАЛ  %s — %s" % (name, note))
print("проверок: %d, провалов: %d" % (len(checks), len(fails)))
sys.exit(1 if fails else 0)
