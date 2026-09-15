# Директива 19: Деплой на российский хостинг

> Этап 19 конвейера (00_pipeline.md). Вход: репозиторий и `PROJECT.md` (18), тема `wordpress/wp-content/themes/designstack/`, плагин `wordpress/wp-content/plugins/designstack-core/`, аудит `15` без критических находок, `docs/brand/naming.md` (домен), `docs/analytics/goals.md` (счётчик, 17). Выход: живой сайт `https://<domain>`, обновлённый `PROJECT.md`. Запуск: `/directive 19`

## Задача

Перенести сайт с локальной среды (SQLite, `php -S`) на российский хостинг с MySQL 8 и HTTPS и получить живой адрес. Первый запуск: выбор хостинга, установка WordPress, перенос контента, заливка темы и плагина, домен, HTTPS, бэкапы, чеклист проверки. Повторные запуски: **обновление темы и плагина**, не переустановка — после запуска источник правды для контента — база на хосте, а не локальная SQLite.

## Когда применять

- Перед запуском: код в репозитории (18), аудит `15` пройден, SEO и трекинг (17) в коде, контент набран (16) хотя бы до стартового объёма из brief §5.3.
- Повторно — после каждой итерации, которую утвердили локально: локалка обновляется мгновенно, живой сайт — по готовности, одной операцией.
- Не запускать, если `debug.log` за последний прогон не пуст или страницы локально отдают ошибки.

## Предусловие

- `PROJECT.md` с репозиторием (18); `git status` чист, локальный `main` = `origin/main`.
- `docs/brand/naming.md` — выбранное название и домен; нет — сначала `09`.
- Локально: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/` → 200, `tools/wp.cmd --path=wordpress core verify-checksums` — OK.
- Инструменты Git Bash: `ssh`, `scp`, `curl` (есть); `rsync` — проверить `rsync --version`, при отсутствии — fallback на `scp`/zip; `tar`/`zip` — есть в Git Bash.
- Доступы к хостингу (панель, SSH/SFTP, БД) — у заказчика; передаются агенту транзиентно, только на время операции.

## Роль

DevOps-инженер для WordPress, который десятки раз переносил сайты с локалки на shared-хостинг и VPS: знает, что `wp db export` не работает на SQLite, почему `search-replace` без `--dry-run` ломает сериализованные опции, и как выглядит письмо формы, ушедшее в спам без SPF.

## Ключевой принцип

**Заливаем только своё** — тему и плагин, ядро ставит хостинг или `wp core download`, dev-файлы (`tools/`, `.env`, `.tmp/`, SQLite) на сервер не едут. **Контент переносится один раз** (WXR), дальше живёт на хосте. **Секреты транзиентны:** пароли панели, SSH, БД, SMTP — только в команде на время операции, не в файлы, не в `PROJECT.md`, не в отчёт, не в историю чата повторно. Любая операция с данными на хосте — сначала бэкап, потом `--dry-run`, потом по-настоящему.

## Граница

Директива НЕ пишет код темы и плагина (ошибки → `13`/`14`), НЕ правит контент (16), НЕ настраивает цели Метрики и Вебмастер (17, туда возвращаемся после деплоя), НЕ покупает домен и хостинг (браузерные шаги и оплата — заказчик), НЕ переводит локальную среду на MySQL (локально остаётся SQLite; прогон на MySQL — на хосте или в staging-папке хостинга).

## Фазы

### Фаза 0. Выбор хостинга и пути — апрув

1. `WebSearch`: актуальные тарифы **Timeweb, Beget, Reg.ru** (плюс 1 запасной, если один из них не подходит) по критериям brief §7: PHP 8.3, MySQL 8, SSH, WP-CLI (или возможность поставить phar), cron, HTTPS Let's Encrypt, цена/мес, оплата картой РФ, лимиты (место, БД, трафик), наличие staging и бэкапов. Результат — таблица в `.tmp/hosting-compare.md` (не в `docs/`, устаревает за месяц).
2. Два пути: **Путь A — shared-хостинг с панелью** (WordPress из панели, SFTP, phpMyAdmin, SSH с WP-CLI если тариф даёт) — рекомендуется для MVP: дешевле, бэкапы и HTTPS «из коробки». **Путь B — VPS** (Ubuntu 24.04, nginx + PHP-FPM 8.3 + MySQL 8, WP-CLI, certbot) — если нужен полный контроль, cron без ограничений или в тарифах shared нет PHP 8.3/SSH.
3. `AskUserQuestion` (≤3): хостинг из таблицы с рекомендацией; путь A/B; домен — подтвердить из `naming.md` (зарегистрирован? DNS у регистратора или хостинга?).
4. Заказчик оплачивает тариф, привязывает домен (браузерные шаги: панель → домены → добавить → NS/A-запись), получает доступы. Агент проверяет: `nslookup <domain>` указывает на хост, `ssh <user>@<host> "php -v; which wp || ls ~/wp-cli.phar; mysql --version"` (пароль — через запрос ssh, не в команде; для пути A SSH может отсутствовать — тогда SFTP + phpMyAdmin).

### Фаза 1. Pre-flight локально

1. `15` — последний аудит без критических находок (`docs/audit/site_audit_<date>.md` ≤ 7 дней); `debug.log` чист после прогона главной, архива, карточки, поиска, 404, формы.
2. `tools/wp.cmd --path=wordpress core verify-checksums`, `core version`, `php -v` → записать версии; на хосте должны быть те же мажорные (WP 7.x, PHP 8.3).
3. Проверка MySQL-совместимости кода: `grep -rniE "sqlite|\bPRAGMA\b|json_extract|\|\|" wordpress/wp-content/plugins/designstack-core wordpress/wp-content/themes/designstack --include=*.php` — не должно быть SQLite-специфики; `meta_query`/`tax_query` только через WP API.
4. Экспорт контента: `tools/wp.cmd --path=wordpress export --dir=.tmp/export --post_type=resource,post,page,nav_menu_item --with_attachments` → WXR-файлы (записи, meta, термины, подборки). `wp db export` **не работает на SQLite** — не пытаться. Медиа: `wordpress/wp-content/uploads/` → архив `.tmp/uploads.zip` (заливается отдельно, в git не входит).
5. Архив кода: `git archive -o .tmp/designstack-<hash>.zip HEAD wordpress/wp-content/themes/designstack wordpress/wp-content/plugins/designstack-core` — только своё, из коммита, а не из рабочей папки.
6. Бэкап «до»: локально `.tmp/backup-<date>/` (экспорт + zip + копия `wp-config.php` без секретов); на хосте — при повторном деплое (фаза 5).

### Фаза 2. WordPress и база на хосте

**Путь A (панель):** установить WordPress из панели (или загрузить `latest-ru_RU.zip` в `public_html`, создать БД в панели, пройти установку по `https://<domain>`) → логин админа заказчику; `wp-config.php` — добавить константы (п. 3) через SFTP.
**Путь B (VPS):** `ssh` → пакеты (`nginx php8.3-fpm php8.3-mysql php8.3-xml php8.3-mbstring php8.3-curl php8.3-gd php8.3-zip php8.3-intl mysql-server certbot python3-certbot-nginx`), `mysql_secure_installation`, БД и пользователь (`CREATE DATABASE … CHARACTER SET utf8mb4`), WP-CLI (`curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar && chmod +x && mv /usr/local/bin/wp`), `wp core download --locale=ru_RU`, `wp config create`, `wp core install --url=https://<domain> …` (пароль админа — из генератора, сразу заказчику, не в чат-историю повторно); nginx-конфиг с `try_files $uri $uri/ /index.php?$args`, `client_max_body_size 64M`; PHP-FPM `memory_limit=256M`.

Общее для обоих путей:
1. Константы в `wp-config.php`: `WP_ENVIRONMENT_TYPE` = `production`, `WP_DEBUG` = false, `WP_DEBUG_LOG` = false, `DISALLOW_FILE_EDIT` = true, `AUTOMATIC_UPDATER_DISABLED` = true (обновления вручную после локальной проверки, brief §7), `WP_MEMORY_LIMIT` = `256M`, `FORCE_SSL_ADMIN` = true. Соли — сгенерировать заново (`wp config shuffle-salts`).
2. Настройки через WP-CLI (или админку, если SSH нет): `blogname` из `naming.md`, `blogdescription` — позиционирующая фраза brief §2, `timezone_string=Europe/Moscow`, `permalink_structure=/%postname%/`, `blog_public=1`, `default_comment_status=closed`, удалить `hello`/`akismet` и демо-контент.
3. Импорт контента: `wp plugin install wordpress-importer --activate`, залить WXR из `.tmp/export/` (`scp`), `wp import .tmp/export/*.xml --authors=create` (кураторов сопоставить по логину), затем `wp plugin deactivate wordpress-importer --uninstall`. Альтернатива для чистого старта без истории — `scripts/seed.py`-подобный импорт (JSON → `wp post create`) по `ssh`.
4. Медиа: распаковать `uploads.zip` в `wp-content/uploads/`, `wp media regenerate --yes` при необходимости.
5. Замена URL: **сначала** `wp search-replace 'http://localhost:8080' 'https://<domain>' --dry-run --report-changed-only`, посмотреть таблицы и число замен, **затем** без `--dry-run` (`--all-tables --precise` для сериализованных данных). Проверить `wp option get siteurl home`.

### Фаза 3. Тема и плагин, ЧПУ

1. Заливка (обновление — та же операция): `rsync -az --delete -e ssh wordpress/wp-content/themes/designstack/ <user>@<host>:<path>/wp-content/themes/designstack/` и то же для `plugins/designstack-core/`. Нет `rsync` (Windows) — `scp -r` из `.tmp/designstack-<hash>.zip` + `ssh … "unzip -o"`; путь A без SSH — SFTP-клиент панели или файловый менеджер (zip → распаковать). Заливать из архива коммита, не из рабочей папки.
2. `wp theme activate designstack`, `wp plugin activate designstack-core`, `wp plugin install wordpress-seo --activate` (или выбранный в 17), кеш-плагин по возможностям хостинга (brief §7: встроенный кеш хостинга, иначе WP Super Cache), `redirection`, `updraftplus` (если бэкапы хостинга не покрывают еженедельный внешний экспорт).
3. `wp rewrite structure '/%postname%/' --hard && wp rewrite flush --hard`; путь A — убедиться, что `.htaccess` с правилами WP записан (Apache) или nginx-конфиг панели содержит `try_files`; путь B — nginx из фазы 2.
4. Проверить ЧПУ по факту: `curl -s -o /dev/null -w "%{http_code} %{url_effective}\n"` для `/`, `/tools/`, `/learn/`, `/resource/<slug>/`, `/topic/<slug>/`, `/collections/`, `/suggest/`, `/nonexistent-404/` (ожидаем 200 … и 404 с шаблоном темы).
5. SMTP для форм: плагин `wp-mail-smtp` или SMTP хостинга; адрес отправителя — на домене сайта; у заказчика — SPF/DKIM в DNS (шаги панели). Тест: `wp eval 'wp_mail("<email куратора>","DesignStack: тест SMTP","ok");'` → письмо дошло не в спам.
6. Настройки плагина: ID счётчика Метрики из `goals.md` (`wp option update designstack_metrika_id <ID>`), e-mail куратора для формы «предложить», верификационные теги Вебмастера/GSC (появятся из 17).

### Фаза 4. HTTPS, редиректы, robots, sitemap

1. Сертификат: путь A — Let's Encrypt в панели (галка «SSL»), путь B — `certbot --nginx -d <domain> -d www.<domain>` + `certbot renew --dry-run`.
2. Редиректы: `http → https`, `www → без www` (или наоборот, как в `naming.md`) — на уровне сервера (nginx `return 301` / `.htaccess`), не плагином; `siteurl`/`home` = канонический вариант.
3. `curl -sI http://<domain>/ | head -3`, `curl -sI https://www.<domain>/ | head -3` — 301 на канонический адрес; `curl -sI https://<domain>/ | grep -i strict-transport` — HSTS включён (после проверки, что всё на https).
4. `https://<domain>/robots.txt` и `sitemap_index.xml` (или `wp-sitemap.xml`) отдают 200 и содержат домен, а не `localhost` — правила из 17. `wp option get blog_public` → 1.
5. Счётчик Метрики присутствует в `curl -s https://<domain>/ | grep -c "mc.yandex.ru"` → 1; локально его не было — это и есть проверка `WP_ENVIRONMENT_TYPE`.

### Фаза 5. Бэкапы

1. **До** любого изменения на живом сайте (повторный деплой, импорт, search-replace): бэкап средствами хостинга (панель → бэкапы → создать) или `wp db export ~/backups/<date>.sql.gz` на хосте (там MySQL — работает) + `tar czf ~/backups/wp-content-<date>.tgz wp-content/uploads wp-content/themes/designstack wp-content/plugins/designstack-core`.
2. **После** успешного деплоя — ещё один бэкап «известно хорошее состояние».
3. Расписание: ежедневный бэкап хостинга (проверить, что включён и хранится ≥7 дней); **еженедельно вне хостинга** — cron на хосте: `wp export --dir=~/backups/wxr --post_type=resource,post,page` + архив темы/плагина, скачать `scp` в локальную папку заказчика (не в git). Cron хостинга (не WP-Cron): `0 4 * * 1 cd <path> && wp cron event run --due-now && wp export …`; сюда же — еженедельная проверка ссылок (`scripts/check_links.py` из 16, если на хосте есть Python; иначе WP-CLI-команда плагина).
4. Восстановление проверить один раз: развернуть SQL-дамп в staging-БД (или локально в MySQL-контейнере, если появится) — хотя бы `gunzip -t` и `head` дампа.

### Фаза 6. Чеклист живого сайта

Проверить и записать результат в `.tmp/deploy-check-<date>.md`; всё, что упало, — задание в `13`/`14`/`16`/`17`:
- Главная, 4 архива, архив с фильтром (URL с параметрами), карточка ресурса каждого типа, тема, подборка, дайджест, `/about/`, `/suggest/`, поиск с результатом и без — 200, без PHP-warning'ов в HTML (`curl -s … | grep -ci "warning\|fatal"` → 0).
- 404 отдаёт шаблон темы (`templates/404.html`), статус 404.
- Форма «предложить» и подписка: письмо куратору доходит, nonce/honeypot/лимит по IP работают (повторная отправка → ошибка).
- Тёмная тема переключается и запоминается; `prefers-color-scheme` уважается.
- Скорость: PageSpeed Insights (`https://pagespeed.web.dev/` — браузерный шаг заказчика или `WebFetch` API) — LCP < 2,5 с, CLS < 0,1 на мобильном (brief §7); кеш хостинга включён, изображения WebP.
- Метрика получает хиты: заказчик открывает Метрика → «Посещаемость» в реальном времени, видит свой визит; цель `resource_outbound` срабатывает при клике по ссылке ресурса.
- Админка: `https://<domain>/wp-admin/` по https, 2FA для куратора включена (плагин Two Factor или средствами хостинга), `DISALLOW_FILE_EDIT` — редактор тем скрыт.
- `wp core verify-checksums` на хосте — OK; `wp plugin list` — только нужное; `debug.log` на хосте не создаётся.

### Фаза 7. Запись в PROJECT.md и повторный деплой

1. `PROJECT.md`: «Хостинг» — провайдер, тариф, путь A/B; «Домен» — домен, где DNS; «Живой URL» — `https://<domain>`; «Путь деплоя» — папка на хосте, способ заливки (rsync/scp/SFTP), наличие SSH/WP-CLI; «Бэкапы» — где, как часто; «Дата деплоя» и версия коммита; статус `19 ✅`. **Без** паролей, логинов БД, IP с учётками. Закоммитить и запушить (18, фаза 5).
2. Повторный запуск = обновление: pre-flight (фаза 1, п. 1–3, 5) → бэкап на хосте (фаза 5, п. 1) → заливка темы/плагина из архива коммита (фаза 3, п. 1) → `wp rewrite flush --hard` если менялись слаги → сброс кеша хостинга/плагина → чеклист (фаза 6, сокращённо: главная, архив, карточка, форма) → запись даты и коммита в `PROJECT.md`. Контент, опции, медиа на хосте **не трогаем** — они источник правды после запуска; локальная SQLite — только для разработки (при необходимости обновить локалку — `wp export` на хосте → `wp import` локально, в обратную сторону — никогда).
3. Вернуться в `17`: регистрация в Вебмастере и Search Console, отправка sitemap, создание целей и воронок в интерфейсе Метрики, первый раунд метрик через неделю.

## Формат результата

- Живой сайт `https://<domain>` с активной темой `designstack` и плагином `designstack-core`, контентом из WXR, HTTPS и редиректами.
- `PROJECT.md` — хостинг, домен, путь деплоя, бэкапы, дата, коммит; без секретов.
- `.tmp/hosting-compare.md`, `.tmp/export/*.xml`, `.tmp/designstack-<hash>.zip`, `.tmp/deploy-check-<date>.md` — промежуточные, не в git.
- Бэкапы «до» и «после» на хосте (`~/backups/` или панель) и еженедельный внешний экспорт по cron.
- Задания в другие директивы — списком в Финале, если чеклист выявил проблемы.

## Self-check

- На хост ушли только тема и плагин (из архива коммита), а не ядро/`tools/`/`.env`/SQLite; `wp theme list`/`plugin list` на хосте подтверждают активные версии.
- `wp option get siteurl home` = `https://<domain>`; `search-replace` выполнен после `--dry-run`, число замен совпало.
- Все URL чеклиста отдают ожидаемые коды; 404 — шаблон темы; ЧПУ `/tools/`, `/resource/<slug>/` работают без `index.php`.
- `WP_ENVIRONMENT_TYPE=production`, `WP_DEBUG=false`, `DISALLOW_FILE_EDIT=true`, `blog_public=1`, счётчик Метрики на странице есть, локально — нет.
- HTTPS с автопродлением, http/www редиректят 301 на канонический адрес.
- Письмо из формы дошло не в спам; SPF/DKIM настроены.
- Бэкап «до» и «после» существуют, cron еженедельного экспорта установлен и отработал вручную один раз.
- В `PROJECT.md`, отчёте и файлах нет паролей, токенов, строк подключения к БД.

## Финал

```
Сайт опубликован.
- Хостинг: <провайдер, тариф> · путь: <A shared с панелью | B VPS> · домен: https://<domain>
- WordPress <версия>, PHP 8.3, MySQL 8; тема designstack + плагин designstack-core (коммит <hash>)
- Контент: импортировано <N> resource, <N> подборок, <N> дайджестов, медиа <N> файлов; search-replace ✓
- HTTPS + редиректы ✓ · robots/sitemap ✓ · Метрика <ID> получает хиты ✓ · SMTP ✓
- Бэкапы: до/после ✓, хостинг ежедневно, внешний экспорт еженедельно (cron <день>)
- Чеклист: <пройдено N из M>; задания → <13/14/16/17: …>
- PROJECT.md обновлён (без секретов)
Следующий шаг: /directive 17 — Вебмастер, Search Console, цели в Метрике; первый раунд метрик через 7 дней.
Повторный деплой: /directive 19 — обновление темы/плагина, контент на хосте не трогается.
```

## Грабли

- **`wp db export` на SQLite** — не работает; экспорт только `wp export` (WXR). На хосте (MySQL) `wp db export` работает и используется для бэкапов.
- **`search-replace` без `--dry-run`** — сериализованные опции и виджеты ломаются молча; сначала dry-run, затем `--precise --all-tables`, потом проверка `siteurl`/`home`.
- **`uploads/` в git или в архиве темы** — гигабайты в репозитории; медиа едут отдельным zip один раз, дальше живут на хосте.
- **Кеш хостинга после обновления** — старые шаблоны и CSS показываются часами; сбрасывать кеш панели и плагина после каждой заливки, проверять с `?nocache=1` и в приватном окне.
- **ЧПУ 404 на всём, кроме главной** — нет `.htaccess`/`try_files`; `wp rewrite flush --hard` пишет `.htaccess` только если файл доступен для записи.
- **Права на файлы** — залито от root или другого пользователя; WP не пишет `uploads/`, обновления падают. `chown -R <user>:<group>`, папки 755, файлы 644, `wp-config.php` 640.
- **Письма из формы — в спам** без SMTP/SPF/DKIM; `wp_mail` через `mail()` хостинга почти всегда в спам.
- **Импорт WXR без авторов** — записи у пользователя «admin», подпись куратора теряется; `--authors=create` или маппинг.
- **`blog_public=0` приехал с локалки** — сайт закрыт от индексации; проверять в чеклисте.
- **Переустановка вместо обновления** — при повторном деплое затирается контент на хосте. После запуска контент только там; локальная SQLite не источник.
- **Секреты в чате и файлах** — пароль SSH/БД/SMTP только в момент операции; `ssh` спрашивает пароль сам, ключи предпочтительнее пароля (`ssh-keygen`, `ssh-copy-id`).
- **`rsync` отсутствует в Git Bash** — заранее проверить и держать fallback `scp` + `unzip` на хосте.

## Правила

- Заливаем только тему и плагин из архива коммита; ядро и плагины ставятся на хосте штатно.
- Контент переносится один раз WXR-экспортом; после запуска хост — источник правды, направление синхронизации только хост → локалка.
- Каждая операция с данными на хосте: бэкап → `--dry-run` → выполнение → проверка `curl`.
- Секреты транзиентны; в `PROJECT.md` — только хостинг, домен, путь и даты.
- Локалка обновляется мгновенно, живой сайт — по готовности, одной операцией, с чеклистом после.
- Путь A/B и хостинг выбирает заказчик по таблице сравнения; браузерные шаги (оплата, домен, DNS, панель) — заказчик, командная строка — агент.
- Повторный запуск = обновление темы/плагина + чеклист, не переустановка.
