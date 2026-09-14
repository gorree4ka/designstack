# DesignStack — сайт-сборник полезных материалов для UX/UI/продуктовых дизайнеров (WordPress)

Цель: лучший ресурс в своей нише. Бриф утверждён 10.09.2026 — `docs/brief.md` (версия 1.0) является источником требований; изменения требований — через `/briefing`, а не молча в коде.

@01_principles.md

## Стек и среда (локально, без Docker/MySQL)

- WordPress 7.1 в `wordpress/`, PHP 8.3 портативный в `tools/php/`, БД — SQLite (`wordpress/wp-content/database/.ht.sqlite`, drop-in `wp-content/db.php`).
- Сервер: встроенный `php -S` с роутером `tools/router.php` → http://localhost:8080 , админка `/wp-admin` (логин/пароль в `.env`).
- WP-CLI 2.12: `tools/wp.cmd --path=wordpress <cmd>`. Локаль сайта ru_RU, ЧПУ `/%postname%/`.
- Node 24 / npm 11 доступны для `@wordpress/scripts`, Python 3.12 — для скриптов в `scripts/`.

## Команды

```
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start.ps1 -Background   # запустить сервер
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/stop.ps1                # остановить
tools/wp.cmd --path=wordpress theme list                                            # WP-CLI
python scripts/reset.py                                                             # снести БД и переустановить сайт
python scripts/setup.py                                                             # поднять среду с нуля (PHP, WP, WP-CLI)
tail -20 wordpress/wp-content/debug.log                                             # ошибки PHP/WP
```

## Структура

- `wordpress/wp-content/themes/designstack/` — наша тема (единственное место для кода сайта, см. skill `wp-theme`).
- `wordpress/wp-content/plugins/designstack-*/` — наши плагины, если понадобятся. Остальное в `wordpress/` не трогаем и не коммитим.
- `scripts/` — детерминированные скрипты (setup/reset/start/stop, хуки в `scripts/hooks/`).
- `tools/` — PHP, WP-CLI, роутер (в git не попадают, восстанавливаются `scripts/setup.py`).
- Директивы конвейера `NN_directive_<slug>.md` в корне, карта и порядок — `00_pipeline.md`. Запуск: `/directive NN`. Исходные версии — `_archive/directives_v1/`.
- `.claude/skills/` — `directive` (запуск директивы по номеру), `briefing`, `decision-board` (лист решений для заказчика), `wp-dev` (среда, WP-CLI, проверка), `wp-theme` (создание темы). `.claude/rules/wp-theme.md` — стандарты кода темы.
- `docs/` — бриф (`brief.md`), лог брифинга, `research/` — исследование конкурентов.
- `docs/DECISIONS.md` — журнал решений: Решено / Предлагаю / Открыто. `docs/VOICE.md` — словарь интерфейса: одно понятие — одно слово на всех страницах.
- `.tmp/` — временные файлы, `.env` — секреты (не читать без нужды).

## Рабочий процесс

1. Перед правками убедись, что сервер запущен (`curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/` → 200).
2. Код только в своей теме/плагине. Контент и настройки — через WP-CLI, а не руками в админке (воспроизводимо).
3. После каждой правки: хук сам прогонит `php -l`; ты — проверь страницу `curl`-ом и `debug.log`.
4. БД SQLite: `wp db *` не работает; MySQL-специфичный SQL не писать.
5. Перед вёрсткой страницы — лист решений для просмотра и апрув заказчика в чате (навык `decision-board`): нет апрува — нет вёрстки. Тексты интерфейса берутся из `docs/VOICE.md`, решения и предложения записываются в `docs/DECISIONS.md`.
6. Коммитить только по просьбе пользователя. В git попадают: тема, плагины `designstack-*`, `scripts/`, `docs/`, `.claude/`, `CLAUDE.md`, директивы `NN_*.md`.

## Известные особенности

- `winget install PHP.PHP.8.3` ломается (404), поэтому PHP качается напрямую с windows.php.net в `scripts/setup.py`.
- WSL/Docker на машине нет; если понадобится MySQL-совместимость (например, для деплоя), ставить Docker Desktop отдельно.
- Команды хуков в `.claude/settings.json` пишутся только с абсолютным путём: рабочая папка агента и субагентов плавает, относительный путь молча ломает хук.
