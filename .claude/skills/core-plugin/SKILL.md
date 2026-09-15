---
name: "core-plugin"
description: "Плагин designstack-core: тип записи resource, таксономии, мета-поля, панель редактора, динамические блоки, форма «Предложить ресурс», демо-контент. Применять при изменении модели данных, добавлении поля, блока или фильтруемого свойства."
---

# Этап 12 · Плагин designstack-core — модель данных и блоки

> До 15.09.2026 это была директива `12_directive_core_plugin.md`; исходник — `_archive/directives_v2/`.
> Этап 12 конвейера (00_pipeline.md). Вход: `docs/brief.md` §5, `docs/spec.md`, `docs/ds/components.md` (контракт разметки). Выход: `wordpress/wp-content/plugins/designstack-core/`, `scripts/seed.py`. Запуск: /core-plugin

## Задача

Перенести контентную модель из brief §5 в код: плагин `designstack-core` с post type `resource`, таксономиями, meta-полями, редакторской панелью, динамическими блоками (список ресурсов, мета, статус из РФ, форма «предложить ресурс») и демо-контентом через `scripts/seed.py`. Данные живут в плагине и не зависят от темы: смена темы не теряет ни поля, ни URL.

## Когда применять

После 11 (паттерны дают классы для `render.php`) и до 13 (шаблонам нужны блоки и данные). Повторно — при изменении модели в brief §5 через 02/06, добавлении блока или поля. Повторный запуск = синхронизация: читает существующий плагин, добавляет недостающее, ничего не удаляет без явного апрува.

## Предусловие

- `docs/brief.md` §5.1 (поля, таксономии) и §7 (требования к плагину) — есть.
- `docs/spec.md` из 06 — есть (критерии приёмки формы и фильтров). Нет → `/product-spec`; можно идти по brief с пометкой «spec не сверён».
- `docs/ds/components.md` из 11 с разделом «Контракт разметки» (`resource-card`, `badge`, `resource-list`, `empty-state`, `notice`). Нет → `/patterns-library`; блоки временно рендерят разметку по brief §8 с TODO-пометкой.
- `docs/research/competitors.md` — источник реалистичных демо-записей.
- Сервер поднят, `debug.log` доступен.

## Роль

WordPress-разработчик уровня senior, который пишет плагины по Coding Standards без билд-шага: `register_post_type`, `register_post_meta` со схемой REST, PHP-блоки с `render.php`, meta box, `admin_post`-обработчики. Знает, что SQLite под капотом, и не пишет SQL вообще.

## Ключевой принцип

**Имя = якорь.** Ключ поля в brief §5.1 (`ru_open`) = meta-key в БД = поле в REST = атрибут блока = класс бейджа `ds-badge--ru-open`. Значения enum — латиницей ровно как в брифе (`open / vpn_only / blocked`). На общих именах держатся 13, 14, 16 и 17; переименование — только через бриф.

## Граница

- Не верстает: `render.php` воспроизводит классы из `components.md`, CSS остаётся в теме (`patterns.css`).
- Не делает фильтрацию на фронте, поиск по мета, пагинацию архивов (14) — только регистрирует `query_var` и отдаёт данные.
- Не наполняет реальным контентом (16): seed — демо, помеченное `_designstack_seed`.
- Не ставит сторонние плагины (SEO, кеш — 17/19).

## Фазы

### Фаза 0. Модель и допущение A1

Прочитать brief §5 целиком и `docs/spec.md` (разделы про каталог и форму). Один `AskUserQuestion`: «Подтверждаем A1 — единый post type `resource` + таксономия `resource_type` (4 термина), поля по типу показываются условно?» Варианты: «Да, единый тип (Recommended)» / «Четыре отдельных post type» / «Обсудить». Второй вариант — стоп и возврат в 02: меняется бриф, шаблоны и URL. Зафиксировать ответ в README плагина и в `docs/DECISIONS.md`: A1 переезжает из «Предлагаю» в «Решено» новой строкой (`D<N>` · решение · причина · дата), а в «Предлагаю» остаётся пометка о переносе. На месте не переписываем — видно должно быть и что предлагали, и когда решили.

### Фаза 1. Каркас плагина

```
wordpress/wp-content/plugins/designstack-core/
  designstack-core.php      заголовок (Plugin Name, Text Domain: designstack-core, Requires PHP 8.3), константы, require includes
  includes/post-types.php  register_post_type
  includes/taxonomies.php  register_taxonomy × 3
  includes/meta.php        register_post_meta, enum-справочники, санитизация
  includes/rewrite.php     короткие URL типов, term_link
  includes/form.php        обработчик «предложить ресурс»
  admin/meta-box.php       панель полей в редакторе
  admin/meta-box.js        показ полей по типу (без сборки)
  admin/columns.php        колонки списка в админке: тип, ru_open, ru_payment, checked_at
  blocks/<name>/block.json, render.php, editor.js
  uninstall.php            удаление опций; записи не трогает
  README.md
```

Активация: `register_activation_hook` → регистрация типов + `flush_rewrite_rules()`; деактивация → `flush_rewrite_rules()`. Всё остальное — на `init`. Префикс функций `designstack_core_`, text-domain `designstack-core`. Проверка: `tools/wp.cmd --path=wordpress plugin activate designstack-core` → `debug.log` пуст.

### Фаза 2. Пробы возможностей

Каркас стоит — до основной реализации проверяем прогоном каждую нетривиальную вещь, на которую потом завяжется логика. Не проверил — значит не знаешь: документация и статьи врут, а SQLite, REST и блочный редактор ведут себя не как в примерах. Проба — маленький файл в `.tmp/probes/<name>.php`, запуск на локальном сервере (`curl` или `tools/wp.cmd --path=wordpress eval-file`), вывод в консоль, строка результата в `docs/DECISIONS.md`, после этого проба удаляется. Остаётся знание, а не код.

| Проба | Что проверяем | Пройдена, когда видно |
|---|---|---|
| `rewrite-short-url` | `add_rewrite_rule( '^tools/?$', … )` плюс фильтр `term_link` | `/tools/` реально отдаёт архив типа: 200 и карточки в теле, а не 404, не главная и не редирект в `/type/tool/` |
| `meta-array-schema` | `register_post_meta` с `type => array` и `schema.items` | поле есть в `/wp-json/wp/v2/resource`, запись через REST и `post meta update --format=json` сохраняется и читается обратно массивом |
| `meta-query-sqlite` | `meta_query` из четырёх-пяти условий с `relation => AND` и датой | запрос не падает, отдаёт ожидаемые ID, число запросов `$wpdb->queries` записано цифрой |
| `meta-box-block-editor` | классический `add_meta_box` в блочном редакторе | поля уходят в БД вместе с записью по обычному «Обновить», без второго сохранения и без потери при автосейве |
| `dynamic-block-no-build` | блок с `render_callback` и `editor.js` без сборки | рендерится и на фронте, и превью в редакторе (`wp.serverSideRender`), консоль редактора чиста |
| `wp-mail-local` | `wp_mail` на `php -S` без SMTP | что происходит на самом деле: `false`, исключение или тихий успех — с этим потом живёт форма |

Проба не прошла — решение меняется здесь, пока на нём ничего не построено: строка в `docs/DECISIONS.md` («Открыто» с тем, что мешает, или «Предлагаю» с обходным путём) и вопрос заказчику, если меняется поведение сайта.

### Фаза 3. Post type и таксономии

`register_post_type( 'resource', [...] )`: `public`, `show_in_rest`, `has_archive` — по решению P10 в `docs/DECISIONS.md` (общего архива нет в brief §6); до ответа `false`, архивы — по `resource_type` (архив «все ресурсы» на `/resource/` — используется поиском и фильтрами в 14), `rewrite => ['slug' => 'resource', 'with_front' => false]`, `supports => ['title','editor','thumbnail','excerpt','author','revisions','custom-fields']`, `menu_icon => 'dashicons-screenoptions'`, `taxonomies => ['resource_type','topic','level','post_tag']`, labels по-русски («Ресурсы», «Добавить ресурс»). Все видимые слова — названия типов, терминов таксономий, подписи полей и кнопок в админке — берутся из `docs/VOICE.md`; мимо словаря новых слов не заводим.

Таксономии:
- `resource_type` — плоская, `show_in_rest`, `rewrite => ['slug' => 'type']`. Четыре термина с фиксированными слагами `tool / learning / asset / community` создаются при активации (`wp_insert_term`, если нет). Требование 07: архивы открываются как `/tools/`, `/learn/`, `/assets/`, `/community/`. Механизм: `rewrite` даёт `/type/tool/`; короткие URL — `add_rewrite_rule( '^tools/?$', 'index.php?resource_type=tool', 'top' )` + правило с `page/([0-9]+)`, и фильтр `term_link`, возвращающий `home_url('/tools/')` для терминов этой таксономии. Карта `tool→tools, learning→learn, asset→assets, community→community` — одна константа в `rewrite.php`. Старый `/type/tool/` — 301 на короткий (`template_redirect`).
- `topic` — иерархическая, `show_in_rest`, `rewrite => ['slug' => 'topic']` → `/topic/{slug}/`. Термины из brief §5 (12 тем) с латинскими слагами: `ux-research, prototyping, ui-visual, typography, icons-illustrations, design-systems, ai-for-designers, analytics-metrics, career-portfolio, accessibility, mobile-design, web-landings`.
- `level` — плоская, `show_in_rest`, `rewrite => false`, `query_var => 'level'`; термины `junior / middle / senior`.

Единственность типа: на `save_post_resource` оставлять первый термин `resource_type`, если выбрано несколько; в панели — подсказка «один тип».

### Фаза 4. Meta-поля и панель редактора

Все поля brief §5.1 через `register_post_meta( 'resource', $key, [...] )` с `single => true`, `show_in_rest => true` (для массивов — `['schema' => ['type' => 'array', 'items' => ['type' => 'integer']]]`), `sanitize_callback`, `auth_callback => fn() => current_user_can('edit_posts')`.

| Поле | type | sanitize |
|---|---|---|
| `url`, `affiliate_url` | string | `esc_url_raw` |
| `verdict` | string | `sanitize_text_field` + обрезка 120 |
| `review`, `price_note`, `duration` | string | `sanitize_textarea_field` / `sanitize_text_field` |
| `pricing`, `ru_open`, `ru_payment`, `language`, `status`, `format`, `license`, `platform`, `activity`, `cyrillic` | string | whitelist из справочника `designstack_core_enums()`; чужое значение → default |
| `ru_alternative` | array of integer | `array_map('absint')`, только существующие `resource` |
| `checked_at` | string `Y-m-d` | `DateTime::createFromFormat` или пусто |
| `platforms`, `file_format` | array of string | whitelist / `sanitize_text_field` |
| `has_free_tier`, `ai_features`, `certificate`, `is_jobs` | boolean | `rest_sanitize_boolean` |
| `assets_count` | integer | `absint` |
| `audience_size` | string | «≈ 12 000, 09.2026» |

`curator` — не meta, а `post_author`; выводится именем и ролью (`get_the_author_meta`). Поле `level` из brief для learning — это таксономия `level`, не meta.

Панель: `add_meta_box( 'designstack_resource_fields', 'Поля ресурса', ..., 'resource', 'normal', 'high' )` — классический meta box работает в блочном редакторе. Fieldset «Общие» + четыре fieldset по типу; `admin/meta-box.js` (plain JS, `wp.data.subscribe`) скрывает fieldset'ы, не соответствующие выбранному `resource_type`; без JS видны все. `wp_nonce_field( 'designstack_core_meta', 'designstack_core_nonce' )`; сохранение на `save_post_resource` с проверкой nonce, `DOING_AUTOSAVE`, `current_user_can`, через те же `sanitize_callback`. `ru_alternative` — мультиселект из опубликованных `resource` (`get_posts`, `numberposts => 200`, `fields => 'ids'`). `checked_at` — `<input type="date">`; кнопка «Сегодня». Колонки списка в админке: тип, `ru_open`, `ru_payment`, `status`, `checked_at` с сортировкой (`orderby => 'meta_value'`).

### Фаза 5. Динамические блоки (PHP, без сборки)

Каждый блок — папка в `blocks/`, `block.json` с `"apiVersion": 3`, `"render": "file:./render.php"`, `"editorScript": "file:./editor.js"`, регистрация `register_block_type( __DIR__ . '/blocks/<name>' )` на `init`. `editor.js` — plain JS на `wp.blocks.registerBlockType` + `wp.element.createElement` + `wp.components` (`SelectControl`, `RangeControl`) в `InspectorControls`, превью через `wp.serverSideRender`. Никакого JSX и `@wordpress/scripts`: это единственный JS редактора в проекте, и его хватает. Разметка `render.php` — классы из «Контракта разметки» `components.md`, вывод только через `esc_*`, тексты через `esc_html__( '…', 'designstack-core' )`.

- `designstack/resource-list` — атрибуты `ids[]`, `resource_type`, `topic`, `level`, `pricing`, `ru_open`, `ru_payment`, `limit` (6–24), `layout` (grid | list), `orderby` (checked_at | date | title). Внутри `WP_Query` с `tax_query`/`meta_query`; при `ids` — `post__in` + `orderby => 'post__in'`. Пусто → разметка `empty-state`. Каждая карточка — `designstack_core_render_card( $post_id )` (общая функция, её же использует шаблон `single`/`archive` через блок).
- `designstack/resource-meta` — поля карточки текущего `resource`: вердикт, бейджи (pricing, ru_open, ru_payment, status, checked_at, level), поля по типу списком «термин — значение», аналоги (`ru_alternative` → мини-карточки), куратор. Атрибут `fields[]` для выбора.
- `designstack/ru-status` — бейджи `ru_open` и `ru_payment` (у бесплатных ресурсов без бейджа оплаты, D28) + `status` + дата проверки; иконка + текст; атрибут `size`.
- `designstack/suggest-form` — форма без регистрации: поля url (required), название, комментарий, email (опц.), согласие; `wp_nonce_field`, honeypot `website` (скрыт CSS, заполнен → молча «успех»), лимит 3 отправки/час на IP (`transient` по `wp_hash( ip )`). Обработчик `admin_post_nopriv_designstack_suggest` и `admin_post_designstack_suggest` в `includes/form.php`: валидация → `wp_insert_post( post_type resource, post_status pending )` с `url` и комментарием в `review`, `_designstack_suggested_by` → `wp_mail` куратору (`get_option('admin_email')`) → редирект на `?suggest=ok|error|limit` с якорем формы. `render.php` показывает состояние по query var: по умолчанию / ошибки полей / успех / ошибка отправки / лимит.

### Фаза 6. Демо-контент — `scripts/seed.py`

Python 3.12, только `subprocess` к `tools/wp.cmd --path=wordpress`, данные в `scripts/seed_data.json` (редактируется без Python). Создаёт: 12 терминов `topic`, 3 `level`, категории записей `collections / digest / reviews` (слаги = URL из brief §6); 24–32 записи `resource` по 6–8 на тип из `docs/research/competitors.md` и известных инструментов (Figma, Penpot, Maze, Mobbin, Refero, NN/g, Laws of UX, Golos Text, Дизайн-кабак…), с разными `pricing`, `ru_open` и `ru_payment` (все значения обоих полей и бесплатный ресурс без поля оплаты), `status` (минимум одна `dead`, одна `changed`), `checked_at` (свежие и старше 90 дней), одна с названием в 80 символов; `ru_alternative` перекрёстно; одна тема (`accessibility`) остаётся пустой — для проверки empty-state в 13. Плюс 2 подборки (`post` в `collections` с блоком `resource-list` по `ids`), 1 дайджест.

Команды: `post create --post_type=resource --post_name=<slug> --porcelain`, `post meta update <id> <key> <value>` (массивы — `--format=json`), `post term set <id> resource_type tool`, `post meta update <id> _designstack_seed 1`. Идемпотентность: перед созданием `post list --post_type=resource --name=<slug> --field=ID`; есть — обновить meta, не создавать. `python scripts/seed.py --reset` удаляет только записи с `_designstack_seed=1` (`post delete --force`) и созданные категории, если пусты. Вывод: «создано N / обновлено M / удалено K».

### Фаза 7. Проверка по факту

```
tools/wp.cmd --path=wordpress plugin list --status=active
tools/wp.cmd --path=wordpress post list --post_type=resource --format=count           # 24–32
tools/wp.cmd --path=wordpress term list resource_type --fields=slug,count
tools/wp.cmd --path=wordpress post meta list <id>                                      # все ключи, значения enum
curl -s http://localhost:8080/wp-json/wp/v2/resource?per_page=1 | python -m json.tool  # meta.* видны
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/tools/                  # 200
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/type/tool/              # 301
curl -s http://localhost:8080/resource/<slug>/ | grep -c "ds-badge--ru-open"
curl -s -X POST http://localhost:8080/wp-admin/admin-post.php -d "action=designstack_suggest&website=bot" # honeypot → редирект без записи
tail -30 wordpress/wp-content/debug.log
```
Плюс `php -l` (хук) по каждому файлу, `python scripts/seed.py` дважды подряд — второй прогон ничего не создаёт. Отчёт «что не перенеслось»: поля брифа без реализации, блоки без превью, URL без 200 — список должен быть пуст или объяснён.

### Фаза 8. README плагина

`README.md` в папке плагина: назначение, структура, таблица полей (ключ, тип, enum, REST), таксономии и URL-карта, блоки и атрибуты, форма (лимиты, письмо), seed, ограничения (SQLite локально, MySQL на проде), подтверждённое A1. Отдельный `docs/ds/data-model.md` не нужен: модель — brief §5, детали — README рядом с кодом.

## Формат результата

```
wordpress/wp-content/plugins/designstack-core/   структура из фазы 1, все файлы
scripts/seed.py, scripts/seed_data.json         демо-контент, идемпотентно, --reset
.tmp/probes/<name>.php                          пробы фазы 2: живут до записи результата в docs/DECISIONS.md, потом удаляются
.tmp/plugin/report.md                           вывод команд проверки (можно удалять)
```

## Self-check

- Каждое поле brief §5.1 (общие + 4 группы по типу) есть в `register_post_meta` с `show_in_rest`, `sanitize_callback`, `auth_callback`? Список отсутствующих пуст.
- `curator` = автор, `level` = таксономия — не продублированы как meta?
- `/tools/`, `/learn/`, `/assets/`, `/community/`, `/topic/<slug>/`, `/resource/<slug>/` отдают 200; `/type/tool/` → 301?
- Массивы (`ru_alternative`, `platforms`, `file_format`) в REST — массивы, не строки?
- Блоки регистрируются, превью в редакторе работает, `render.php` использует классы из `components.md`?
- Форма: nonce, honeypot, лимит по IP, pending-запись, письмо, пять состояний вывода?
- Seed идемпотентен, `--reset` удаляет только своё, покрыты все значения `ru_open` / `ru_payment` / `status` / `pricing`, есть пустая тема?
- Ворота этапа: каждая проба из фазы 2 прогнана, результат записан строкой в `docs/DECISIONS.md`, файл пробы удалён? Проба без записанного результата — этап не закрыт.
- Решение по A1 лежит в `docs/DECISIONS.md` в разделе «Решено» с датой, а не только в README плагина?
- Ни одной строки SQL, ни одного `flush_rewrite_rules` вне активации; `debug.log` чист.

## Финал

```
Плагин designstack-core собран и активирован.
- Post type resource, таксономии resource_type (4) / topic (12) / level (3), meta-полей <N> (все в REST)
- URL: /tools/ /learn/ /assets/ /community/ /topic/<slug>/ /resource/<slug>/ — 200
- Блоки: resource-list, resource-meta, ru-status, suggest-form (PHP-рендер, editor.js без сборки)
- Форма: nonce + honeypot + лимит 3/час, pending-черновик + письмо куратору
- Демо: scripts/seed.py — <N> ресурсов, 2 подборки, 1 дайджест; повторный прогон — 0 созданий
- Пробы: короткий URL, meta-массив в REST, meta_query на SQLite, meta box, динамический блок, wp_mail — <N/6> пройдено, результаты в docs/DECISIONS.md
Не перенеслось / требует внимания: <список или «нет»>
README: wordpress/wp-content/plugins/designstack-core/README.md
Дальше: /page-templates — сборка страниц из паттернов и блоков
```

## Грабли

- **SQLite.** Никакого raw SQL, `$wpdb->prepare` с MySQL-функциями, `wp db *`; `meta_query` по дате — строки `Y-m-d`, сравнение `type => 'DATE'` работает, `CHAR` — надёжнее.
- **`flush_rewrite_rules` на каждом `init`** — убивает производительность и ломает SQLite-кэш; только активация/деактивация. После правки правил вручную — `tools/wp.cmd --path=wordpress rewrite flush`.
- **Meta без `show_in_rest` не видна в REST и в редакторе** — блочный редактор не сохранит поле; для массивов обязательна `schema` с `items`, иначе `register_post_meta` вернёт `false` молча.
- **Meta box и автосохранение.** Без проверки `DOING_AUTOSAVE` и nonce поля затираются пустыми при автосейве.
- **Порядок регистрации.** Таксономии регистрировать после post type (или через `taxonomies` в аргументах), иначе `/tools/` даёт 404 после активации.
- **`add_rewrite_rule` без `page/`** — вторая страница архива уходит на 404; правила пагинации добавлять сразу, хотя пагинацию включает 14.
- **`term_link` фильтр** должен проверять таксономию, иначе перепишет ссылки категорий.
- **`wp_mail` локально** без SMTP молча возвращает `false` — в `debug.log` писать факт отправки, не считать ошибкой.
- **Honeypot** не скрывать через `display:none` в инлайн-стиле с hex — только класс из `patterns.css`.
- **Seed и slug'и** — `post_name` задавать явно, иначе WP транслитерирует кириллицу по-своему, и идемпотентность ломается.
- **`orderby => 'post__in'`** работает только вместе с `post__in`; при пустом `ids` не передавать.

## Правила

- Имя = якорь: ключи, enum и классы — ровно из brief §5.1 и `components.md`.
- Не проверил — значит не знаешь: нетривиальное сначала пробой в `.tmp/probes/`, потом реализация; результат пробы — строкой в `docs/DECISIONS.md`.
- Видимые слова админки — названия терминов таксономий, подписи полей и кнопок — из `docs/VOICE.md`.
- Код по WPCS, префикс `designstack_core_`, text-domain `designstack-core`, экранирование на выводе, санитизация на входе.
- Данные — в плагине, вид — в теме: `render.php` не содержит CSS и hex.
- Никакого SQL, никаких сторонних плагинов, никакой сборки JS кроме plain `editor.js`.
- Контент — через WP-CLI и seed, не руками в админке.
- Проверка по факту после каждой фазы: `php -l`, `wp`, `curl`, `debug.log`.
- Повторный запуск синхронизирует; удаление поля или термина — только с апрувом и после `grep` по теме.
