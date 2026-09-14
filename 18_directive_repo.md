# Директива 18: Репозиторий GitHub

> Этап 18 конвейера (00_pipeline.md). Вход: тема `wordpress/wp-content/themes/designstack/`, плагин `wordpress/wp-content/plugins/designstack-core/`, `scripts/`, `docs/`, `.gitignore`. Выход: приватный репозиторий на GitHub (ветка `main`), `README.md`, `PROJECT.md`. Запуск: `/directive 18`

## Задача

Положить проект в приватный репозиторий GitHub **одним пушем** и зафиксировать это в `PROJECT.md`, чтобы деплой (19) и повторные итерации знали, откуда брать код. В git попадает только своё: тема, плагин, скрипты, документы, директивы и настройки агента; ядро WordPress, портативный PHP, база SQLite, загрузки и секреты — никогда. Первый запуск создаёт репозиторий и заливает всё; повторные — коммитят и пушат изменения.

## Когда применять

- Перед первым деплоем (19) и после того, как тема с плагином работают локально (14) и прошли аудит (15).
- Повторно — после каждой итерации, которую нужно отправить на хостинг или просто сохранить: законченная работа → `main`, незаконченная — отдельная ветка.
- Не запускать «на всякий случай» посреди правок: коммит должен соответствовать проверенному состоянию (`debug.log` чист, страницы отдают 200).

## Предусловие

- Локальный репозиторий уже инициализирован (`git rev-parse --is-inside-work-tree` → true); ветка `master` без remote — норма для первого запуска.
- `git --version` ≥ 2.40, Git Credential Manager есть (`git config --get credential.helper` → `manager`). `gh` **не установлен** — GitHub API не используем, всё через `git` по HTTPS.
- `.gitignore` в корне (есть; проверяется в фазе 1).
- Аккаунт GitHub у заказчика; браузерные шаги (репозиторий, токен) делает он.
- Если нет темы или плагина — сначала `11`–`14`; директива не заливает пустой каркас.

## Роль

Release-инженер, который уважает время дизайнера: командную строку ведёт агент целиком, заказчик проходит только два браузерных шага и присылает то, что директива попросит. Ты знаешь, чем fine-grained PAT отличается от classic, почему Credential Manager лучше токена в URL и как `git pull --rebase` спасает первый пуш в непустой репозиторий.

## Ключевой принцип

**Пуш — одна операция** (`git add -A` → один коммит → один `git push`), не пофайловая заливка через API. **Секреты транзиентны:** токен живёт в Credential Manager или в одной команде `push` и никогда — в файлах, `.git/config`, `PROJECT.md`, истории коммитов, отчёте. **`PROJECT.md` — якорь среды:** в нём ссылка на репозиторий, ветка, дата и статус этапов; следующие директивы читают его, а не спрашивают заново.

## Граница

Директива НЕ деплоит (19), НЕ создаёт репозиторий и токен сама (браузер заказчика), НЕ переписывает `.gitignore` без апрува, НЕ коммитит контент базы (записи `resource` живут в SQLite локально и в MySQL на хосте — их переносит `19`, экспорт WXR лежит в `.tmp/`), НЕ настраивает CI/Actions (сборки нет — тема и плагин работают без сборки).

## Фазы

### Фаза 0. Проверки и браузерные шаги заказчика

1. `git --version`, `git config --get credential.helper`, `git status --short | head`, `git branch --show-current`, `git remote -v` — записать текущее состояние (ветка, есть ли remote, есть ли коммиты).
2. Локально проверить, что заливаемое состояние рабочее: сервер отвечает 200, `tail -20 wordpress/wp-content/debug.log` без новых ошибок, `tools/wp.cmd --path=wordpress theme list --status=active` показывает `designstack`.
3. Вывести заказчику **два шага** (без них дальше нельзя):
   - **Создать пустой приватный репозиторий:** github.com → «+» → New repository → имя латиницей (рекомендуется `designstack`) → Private → **без** README, `.gitignore`, лицензии → Create. Прислать имя `<user>/<repo>`.
   - **Выпустить fine-grained PAT:** Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token → Repository access: **Only select repositories → этот репозиторий** → Permissions → Repository permissions → **Contents: Read and write** (Metadata подтянется сам) → Expiration: 90 дней (продлить перед деплоем) → Generate → скопировать один раз. **Не присылать токен в чат заранее** — его спросит окно Credential Manager при первом `push`; в чат — только если выбран запасной путь (фаза 3).
4. `AskUserQuestion` (≤3 вопроса): имя репозитория; способ авторизации — **Credential Manager (Recommended)** / токен в команде push; нужен ли отдельный `README.md` на английском (по умолчанию — русский).

### Фаза 1. Что попадает в git — апрув

1. Сухой прогон: `git add -A --dry-run | sed 's/^add //' | cut -d/ -f1-3 | sort -u` — список верхних путей, которые уйдут в коммит.
2. Сверить с эталоном. **Должны попасть:** `wordpress/wp-content/themes/designstack/`, `wordpress/wp-content/plugins/designstack-*/`, `scripts/`, `docs/`, `.claude/` (кроме `settings.local.json`), `CLAUDE.md`, `00_pipeline.md`, `01_principles.md`, `NN_directive_*.md`, `_archive/`, `.vscode/`, `README.md`, `PROJECT.md`, `.gitignore`. **Не должны:** ядро WordPress (`wordpress/wp-*.php`, `wp-admin/`, `wp-includes/`), `wordpress/wp-content/database/`, `wordpress/wp-content/uploads/`, `wordpress/wp-content/plugins/sqlite-database-integration/`, `wp-content/db.php`, `debug.log`, `tools/`, `.env`, `.tmp/`, `node_modules/`, `__pycache__/`.
3. Известное расхождение: текущий `.gitignore` исключает `tools/php/` и `tools/wp-cli.phar`, но не `tools/router.php`, `tools/wp.cmd`, `tools/php.cmd`. `wp.cmd`/`php.cmd` генерирует `scripts/setup.py`, а `router.php` — нет (его требует `scripts/start.ps1`). `AskUserQuestion` с рекомендацией: заменить правила на `tools/*` + `!tools/router.php` (файл нужен для запуска и воспроизводим только из git). Альтернатива — перенести роутер в `scripts/router.php` и поправить `start.ps1` (это правка кода вне директивы — только с явного согласия).
4. Проверить исполнимость восстановления: в `README.md` описанные команды (`python scripts/setup.py`, `scripts/start.ps1`, `python scripts/seed.py`) существуют в `scripts/`; отсутствующий `seed.py` — пометка «появляется в 12».
5. После правок `.gitignore` — повторить сухой прогон и `git check-ignore -v wordpress/wp-config.php .env tools/php/php.exe` (все три должны быть проигнорированы). Показать итоговый список заказчику — апрув.

### Фаза 2. README и PROJECT.md

1. `README.md` (русский, ≤80 строк): что это (одна фраза из brief §2 + позиционирование), стек (WordPress 7.x, PHP 8.3, блочная тема `designstack`, плагин `designstack-core`, локально SQLite), как поднять локально — `python scripts/setup.py` → `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start.ps1 -Background` → `python scripts/seed.py` → http://localhost:8080 (логин в `.env`), структура папок (тема, плагин, `scripts/`, `docs/`, директивы), конвейер — ссылка на `00_pipeline.md`, как работать с агентом (`/directive NN`). Без секретов, без внутренних адресов хостинга. Скелет:
   ```markdown
   # <Название из naming.md> — каталог проверенных ресурсов для дизайнеров
   Одна фраза о продукте и три обещания (актуальность, доступность из РФ, оценка куратора).
   ## Стек            WordPress 7.x · PHP 8.3 · тема designstack (FSE) · плагин designstack-core · SQLite локально / MySQL 8 на хостинге
   ## Запуск локально python scripts/setup.py → scripts/start.ps1 -Background → python scripts/seed.py → http://localhost:8080
   ## Структура       wordpress/wp-content/themes/designstack/ · plugins/designstack-core/ · scripts/ · docs/ · NN_directive_*.md
   ## Конвейер        00_pipeline.md — этапы 02–19, запуск `/directive NN`; требования — docs/brief.md
   ## Лицензия / контакты   по решению заказчика
   ```
2. `PROJECT.md` (создать или обновить, секции фиксированы): «Репозиторий» — `https://github.com/<user>/<repo>`, ветка `main`, дата последнего пуша; «Статус этапов» — таблица директив 02–19 со статусом (✅ / ⏳ / —) и датой; «Хостинг», «Домен», «Живой URL», «Метрика» — заполняют `19` и `17`, здесь оставить `—`. Ни паролей, ни токенов, ни IP с логинами.
3. Прогнать проверку по факту: оба файла в списке `git add -A --dry-run`, в них нет строк, похожих на токены (`grep -nE "ghp_|github_pat_|AKIA|password" README.md PROJECT.md` пусто).

### Фаза 3. Подготовить и запушить одной операцией

1. Ветка: `git branch -M main` (переименовать `master`). Автор: `git config user.name`/`user.email` заданы; e-mail — тот, что привязан к аккаунту GitHub (или `<id>+<user>@users.noreply.github.com`).
2. Коммит: `git add -A && git commit -m "DesignStack: тема, плагин, скрипты, документы (этап 18)" -m "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"`. Один коммит на весь объём; если история уже есть — обычный инкрементальный коммит с той же атрибуцией.
3. Remote — чистый URL без токена: `git remote add origin https://github.com/<user>/<repo>.git` (или `git remote set-url origin …`, если уже был).
4. Пуш (основной путь, Credential Manager): `git push -u origin main`. GCM откроет окно входа — заказчик выбирает «Token» и вставляет PAT (или входит через браузер). Токен сохраняется в Windows Credential Store, в репозиторий не попадает; при следующих пушах вопросов не будет.
   Запасной путь (если окно GCM недоступно, например в неинтерактивном терминале): заказчик присылает токен, агент выполняет **одной командой** `git push -u https://<TOKEN>@github.com/<user>/<repo>.git main`, затем сразу `git remote set-url origin https://github.com/<user>/<repo>.git` и `git remote -v` — в конфиге токена нет. Команду с токеном в отчёт и в файлы не копировать.
5. Если репозиторий оказался непустым (заказчик добавил README) — `git pull --rebase origin main`, разрешить конфликт в пользу локального README, повторить пуш. Force-push не делать.

### Фаза 4. Проверить и отдать

1. `git status` чист, `git log --oneline -3` показывает коммит, `git ls-files | grep -cE "^wordpress/wp-(admin|includes)/|^tools/php/|^\.env$"` → 0, `git ls-files | wc -l` — разумное число (сотни, не десятки тысяч).
2. `git remote -v` — URL без токена; `git config --list | grep -i token` пусто.
3. Заказчик открывает страницу репозитория: файлы на месте, README отображается, ветка `main`, видимость Private. Агент даёт HTTPS-ссылку.
4. Записать в `PROJECT.md` дату пуша и статус `18 ✅`, закоммитить и запушить тем же способом (второй коммит — нормально).

### Фаза 5. Повторный запуск = обновление

1. Прочитать `PROJECT.md` (репозиторий, ветка), `git status`, `git fetch origin && git status -sb` — есть ли расхождение с `origin/main`.
2. Законченная итерация → в `main`: `git add -A` → коммит с атрибуцией → `git pull --rebase origin main` (если remote ушёл вперёд) → `git push`.
3. Незаконченная итерация → отдельная ветка `feat/<slug>` (`git switch -c feat/<slug>`), пуш `git push -u origin feat/<slug>`; в `main` не трогать. Слияние — обычным `git merge --no-ff` локально после проверки, не через веб-интерфейс (нет `gh`, PR не обязателен).
4. Обновить `PROJECT.md`: дата, ветка, статус этапов. В финале перечислить, что и куда ушло.

## Формат результата

- Репозиторий `https://github.com/<user>/<repo>` (Private), ветка `main`, remote `origin` с чистым URL.
- `README.md` в корне проекта — описание, запуск, структура, конвейер.
- `PROJECT.md` в корне проекта — репозиторий, ветка, дата, статус этапов; поля хостинга/домена/Метрики для `19` и `17`.
- Обновлённый `.gitignore` (только по апруву фазы 1).
- Отчёт в чат — Финал ниже; токен в отчёте не фигурирует.

## Self-check

- Пуш прошёл одной операцией (один `git push` на весь объём), не пофайлово и не через API.
- В `git ls-files` нет ядра WordPress, `tools/php/`, `wp-cli.phar`, `.env`, `.tmp/`, `database/`, `uploads/`, `debug.log`, `settings.local.json`.
- Есть тема, плагин, `scripts/`, `docs/`, `.claude/`, директивы, `README.md`, `PROJECT.md`.
- Токен **нигде не сохранён**: `git remote -v` без `@`, `git config --list` без токена, `grep -rE "ghp_|github_pat_" README.md PROJECT.md .claude docs` пусто, в истории чата команда с токеном не повторена.
- Ветка `main` (не `master`), коммит с `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
- README на GitHub отображается; ссылки на команды запуска соответствуют реальным файлам в `scripts/`.
- `PROJECT.md` обновлён и запушен.

## Финал

```
Проект в репозитории GitHub.
- Репозиторий: https://github.com/<user>/<repo> (Private) · ветка: main · коммит: <hash>
- Залито одним пушем: тема designstack, плагин designstack-core, scripts/, docs/, .claude/, директивы, README, PROJECT.md (<N> файлов)
- Исключено: ядро WP, tools/, .env, .tmp/, база SQLite, uploads/, debug.log
- Авторизация: <Credential Manager | токен в разовой команде>, remote без токена ✓
- PROJECT.md: статус этапов обновлён, поля хостинга/домена/Метрики ждут 19 и 17
Следующий шаг: /directive 19 — деплой на хостинг (или /directive 17 для раунда метрик).
```

## Грабли

- **Пофайловая заливка через API** — полчаса ожидания и обрывы. Только один `git push`.
- **Токен в URL остаётся в `.git/config`.** После разового `push https://<TOKEN>@…` обязательно `git remote set-url` на чистый URL и проверка `git remote -v`. Основной путь — Credential Manager, там этой проблемы нет.
- **Classic PAT «на всё и без срока»** — избыточные права. Fine-grained на один репозиторий с `Contents: Read and write`; срок 90 дней, продление — браузерный шаг заказчика.
- **`tools/router.php` не воспроизводим.** `setup.py` его не создаёт; без исключения в `.gitignore` свежий клон не запустится. Решить в фазе 1, не молча.
- **Ядро WordPress в репозитории** — тысячи файлов и обновления через git. `wordpress/*` остаётся в `.gitignore` с точечными `!`-исключениями для темы и плагинов `designstack-*`.
- **Репозиторий создан с README** → первый пуш отклонён. Просим пустой; иначе `git pull --rebase`, не `--force`.
- **`.env` в коммите** — пароль админки локалки уходит в историю навсегда. Проверять `git check-ignore .env` до `git add`; если попал — `git rm --cached .env`, сменить пароль (`wp user update admin --user_pass=…`), переписать историю до пуша.
- **E-mail коммита не привязан к GitHub** — коммиты без аватара и вклада; проверять `git config user.email`.
- **Контент базы «в git»** — записей `resource` в репозитории нет и не должно быть; экспорт WXR — артефакт `19`, живёт в `.tmp/` или в бэкапах хостинга.
- **`.vscode/` и `.claude/` с личными настройками.** В git идут только общие файлы (`settings.json`, `extensions.json`, skills, rules); `settings.local.json` и `*.local` уже в `.gitignore` — не снимать эти правила ради «полноты».
- **CRLF-шум.** Windows может переписать окончания строк и раздуть diff; `git config core.autocrlf false` + `.gitattributes` с `* text=auto eol=lf` для `.php/.json/.md` (добавить по апруву, если diff «весь красный»).

## Правила

- Один пуш всего объёма; остальные операции — стандартные `git`-команды, без `gh` и API.
- Репозиторий и токен создаёт заказчик по шагам директивы; агент ведёт командную строку.
- Токен транзиентный: Credential Manager или одна команда; не в файлы, не в конфиг, не в отчёт.
- В git — только своё: тема, плагин, скрипты, документы, директивы, настройки агента. Ядро, инструменты, база, загрузки, секреты — нет.
- Коммиты с атрибуцией `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`; коммитить только по запросу заказчика или в рамках этой директивы.
- Повторный запуск — обновление того же репозитория: `main` для законченного, ветка для незаконченного; `PROJECT.md` всегда актуален.
