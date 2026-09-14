---
name: wp-dev
description: Запуск/остановка локального WordPress, WP-CLI, сброс базы, проверка страниц. Использовать при любой работе с локальным сайтом DesignStack.
allowed-tools: Bash Read
---

# Локальная среда WordPress (DesignStack)

Стек: портативный PHP 8.3 (`tools/php/php.exe`) + встроенный сервер `php -S` + SQLite (drop-in `wp-content/db.php`). MySQL и Docker не нужны.

## Команды

| Действие | Команда (из корня проекта) |
|---|---|
| Запустить сервер в фоне | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start.ps1 -Background` |
| Остановить | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/stop.ps1` |
| WP-CLI | `tools/wp.cmd <команда>` (запускать из `wordpress/` или с `--path=wordpress`) |
| Проверить, что сайт жив | `curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/` |
| Сброс базы + переустановка | `python scripts/reset.py` |
| Полная переустановка среды | `python scripts/setup.py` (`--force-core` — перекачать ядро) |
| Лог ошибок PHP/WP | `wordpress/wp-content/debug.log` |

Адреса: сайт `http://localhost:8080`, админка `http://localhost:8080/wp-admin`. Логин/пароль в `.env` (не читать файл без необходимости, попросить пользователя).

## Полезные WP-CLI

```
tools/wp.cmd --path=wordpress theme list
tools/wp.cmd --path=wordpress theme activate designstack
tools/wp.cmd --path=wordpress plugin install <slug> --activate
tools/wp.cmd --path=wordpress post create --post_type=page --post_title="Услуги" --post_status=publish
tools/wp.cmd --path=wordpress option update blogname "Название"
tools/wp.cmd --path=wordpress rewrite flush --hard
tools/wp.cmd --path=wordpress eval 'var_dump( get_option("stylesheet") );'
```

Не работают на SQLite: `wp db *` (export/import/query). Для бэкапа копируй `wordpress/wp-content/database/.ht.sqlite`.

## Проверка результата

1. `curl -s http://localhost:8080/<url>/ | grep -i "<title>"` — страница отдаётся, 200.
2. `tail -20 wordpress/wp-content/debug.log` — нет новых Warning/Fatal.
3. Для визуальной проверки — скриншот через браузер пользователя или Playwright (если установлен).
