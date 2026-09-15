# Директива 11: Библиотека паттернов и витрина

> Этап 11 конвейера (00_pipeline.md). Вход: `docs/ds/foundation.md`, `theme.json`, `docs/ia/wireframes/*.md`. Выход: `docs/ds/components.md`, `patterns/*.php`, `parts/*.html`, `assets/css/patterns.css`, витрина `/styleguide/`. Запуск: /directive 11

## Задача

Собрать библиотеку переиспользуемых элементов темы `designstack`: паттерны блоков, части шаблонов, стили ядра — каждый со всеми вариантами и состояниями, только на токенах из 10. Сначала каталог текстом (`docs/ds/components.md`), после апрува — код, затем витрина `/styleguide/`, где каждый паттерн виден во всех вариантах и состояниях в обеих темах. Из этой библиотеки 13 собирает страницы, 12 рендерит карточки той же разметкой.

## Когда применять

После 10 и до 13. Повторно — когда 13 находит повтор (правило 3+/2/1), 14 добавляет состояние, 15 находит дыру в покрытии. Повторный запуск = синхронизация: читает `components.md` и `patterns/`, добавляет недостающее, не пересоздаёт существующее.

## Предусловие

- `docs/ds/foundation.md`, `theme.json` с семантической палитрой, `assets/css/theme-dark.css` — из 10 (иначе `/directive 10`).
- `docs/ia/wireframes/*.md` — из 08 (список секций и элементов, который надо покрыть).
- `.claude/rules/wp-theme.md` — контракт токенов.
- Сервер поднят, тема активна: `tools/wp.cmd --path=wordpress theme list --status=active`.

## Роль

Дизайн-системный инженер, который строит UI-кит каталога прямо в блочной теме WordPress: паттерны, `register_block_style`, обычный CSS на переменных. Проверяет каталог перед заведением нового, чтобы не плодить дубликаты; знает, что состояния — это `:hover / :focus-visible / [aria-current] / [disabled]`, а не отдельные копии разметки.

## Ключевой принцип

**Сначала текст, потом код; витрина — из реальных паттернов, а не копий.** Описание в `components.md` утверждается до первой строки PHP. Страница `/styleguide/` вставляет те же `patterns/*.php`, что и шаблоны сайта: расхождение витрины и сайта невозможно по построению. Полнота = матрица «варианты × состояния» закрыта, а не только default.

## Граница

- Не собирает страницы и шаблоны (13), кроме `page-styleguide.html`.
- Не пишет логику: фильтры, поиск, отправку формы (14). Форма и панель фильтров здесь — статичная разметка со всеми визуальными состояниями.
- Не создаёт блоки плагина и данные (12): `resource-card` здесь — статичная разметка-эталон, которую 12 воспроизведёт в `render.php`.
- Не заводит новые типостили и токены; нужен новый — строка в `foundation.md` как alias через мини-цикл 10.

## Фазы

### Фаза 1. Чтение и инвентарь

1. Прочитать `foundation.md` (таблицы статусов и состояний), `theme.json` (какие preset-переменные есть), все wireframes (какие элементы встречаются и сколько раз), `patterns/` и `parts/` темы (что уже есть после 08 — grey-box-паттерны переписываются, не дублируются).
2. Составить инвентарь. Стартовый список паттернов (из brief §6/§8 и wireframes):

| Раздел | Паттерн | Варианты | Состояния |
|---|---|---|---|
| Действия | `button` (стили `core/button`: primary, secondary, ghost; size sm/md) | 3 × 2 | default, hover, focus-visible, disabled, loading |
| Действия | `link` (стиль ссылок: inline, standalone с chevron) | 2 | default, hover, focus-visible, visited |
| Действия | `theme-toggle` | — | light, dark, focus-visible |
| Ввод | `search-form` (шапка / страница поиска) | 2 | default, focus, filled, empty-result |
| Ввод | `filter-panel` (десктоп-сайдбар) + `filter-chips` (мобильный ряд) | 2 | default, selected, focus-visible, disabled, overflow |
| Контейнеры | `resource-card` | type: tool, learning, asset, community | default, hover, focus-within, dead, changed |
| Контейнеры | `resource-list` (сетка 3 / 2 / 1) | layout: grid, list | данные, empty, loading, overflow (длинные названия) |
| Контейнеры | `collection-item`, `digest-item` | — | default, hover, без обложки |
| Контейнеры | `section-header` (заголовок + ссылка «все») | with-link, plain | — |
| Навигация | `site-header` / `site-footer` (parts) | — | desktop, mobile (меню свёрнуто/раскрыто), active item |
| Навигация | `breadcrumbs`, `pagination` | — | default, current, first/last, focus-visible |
| Фидбэк | `badge` | kind: pricing, ru-open, ru-payment, status, checked-at, level, type | tone: success, warning, error, info, neutral |
| Фидбэк | `notice` (карточка/страница) | dead, changed, info | с ссылкой на аналог / без |
| Фидбэк | `empty-state` | search, filters, archive | с CTA / без |
| Фидбэк | `subscribe-cta` (Telegram + рассылка) | inline, block | telegram (MVP: сервис рассылки не выбран, O4), default, success, error (после выбора сервиса) |

3. Чек на дубликаты: если в wireframes два элемента отличаются только текстом — это один паттерн с вариантом. Один `AskUserQuestion` (≤ 3 вопроса): «Список паттернов принимаем? Что добавить/убрать?» с рекомендацией «принять как есть».

### Фаза 2. Каталог `docs/ds/components.md` — текст

Формат записи одинаков для всех; разделы: Действия, Ввод, Контейнеры, Навигация, Фидбэк, Данные, Прочее.

```markdown
### resource-card
- **Назначение:** карточка ресурса в сетках и подборках; одна высота, без описания вендора.
- **Анатомия:** logo (40 / 80 по правилу изображений из 09; фавикон или лого) → title + type-badge → verdict (1 строка, обрезка) → badges-row (pricing, ru-open, ru-payment, checked-at) → tags (2–3) → link overlay
- **Варианты:** type: tool | learning | asset | community (иконка и вторая строка меты по типу)
- **Состояния:** default | hover (shadow-md, translateY 0) | focus-within (border-focus-ring) | dead (text-muted, notice) | changed (badge warning)
- **Отступы:** padding space-4, gap space-2, radius-md
- **Токены:** surface-raised, border-default, text-default, text-muted, bg-/text-<status>, shadow-sm/md
- **Реализация:** `patterns/resource-card.php` (статичный эталон) → те же классы в `designstack-core/blocks/resource-list/render.php`
- **Классы:** `.ds-card`, `.ds-card--tool`, `.ds-card__title`, `.ds-card__verdict`, `.ds-card__badges`, `.is-dead`
- **Тексты:** только слова из `docs/VOICE.md` («проверено», «Работает из РФ», «предложить ресурс»)
- **Used in:** — (заполняет 13)
- **Status:** planned | built | verified
```

Арифметика матрицы: варианты × состояния, число ячеек в записи; > 24 ячеек — дробить паттерн (например, `badge` по `kind`). Для каждого паттерна перечислить все токены, которых касается; нет токена — сначала alias в `foundation.md` / `theme.json` / `theme-dark.css` (мини-цикл 10), потом паттерн. Раздел «Контракт разметки» — список классов, которые 12 обязан воспроизвести в `render.php` (`resource-card`, `badge`, `resource-list`, `empty-state`, `notice`). Раздел «Иконки»: библиотека одна — Lucide (ISC), спрайт `assets/img/icons.svg`, список имён. Все подписи, кнопки, плашки и пустые состояния берутся из `docs/VOICE.md`: понятия, которого нет в словаре, в паттерне не появляется — сначала строка в словаре, потом разметка.

Апрув: показать `components.md` целиком, `AskUserQuestion` «Каталог утверждаем?» (Да / Правки по паттернам …). Без «да» код не пишем.

### Фаза 3. Реализация

1. **Иконки:** `assets/img/icons.svg` — спрайт `<symbol id="icon-<name>">` с `stroke="currentColor"`; хелпер `designstack_icon( string $name, string $label = '' ): string` в `functions.php` (`aria-hidden` без подписи, `role="img"` с подписью). Бейджи статусов — всегда иконка плюс слово, цвет — третий канал, а не единственный (brief §8). Кликабельное отличается от просто написанного формой: у ссылки и кнопки подчёркивание, рамка или фон и курсор, у информации — ничего из этого.
2. **CSS:** `assets/css/patterns.css`, подключается в `wp_enqueue_scripts` и `enqueue_block_assets` после `global-styles`. Классы `ds-<pattern>__<element>--<modifier>`, состояния `.is-*`. Только `var(--wp--preset--…)` и `var(--wp--custom--…)`; `px` — лишь в `@media (min-width: 600px|900px|1200px)`. Переходы `transition: color, background-color, border-color, box-shadow var(--wp--custom--duration--fast) var(--wp--custom--ease--standard)`; блок `@media (prefers-reduced-motion: reduce) { * { transition-duration: 0.01ms !important; animation: none !important } }`. Состояния через `:hover`, `:focus-visible`, `:active`, `[aria-current="page"]`, `[disabled]`, `[aria-busy="true"]`, `[aria-pressed]`; для витрины каждое правило дублируется классом-двойником: `.ds-button:hover, .ds-button.is-hover { … }`.
3. **Стили ядра:** `register_block_style( 'core/button', ['name' => 'secondary', …] )`, `ghost`; `core/group` → `card`, `panel`; `core/list` → `badges`; `core/heading` → `section-title`. Регистрация в `init`, категории паттернов `designstack` («DesignStack») и `designstack-styleguide` (скрытая: `inserter => false`).
4. **Паттерны:** `patterns/<slug>.php` с заголовком `Title / Slug: designstack/<slug> / Categories: designstack / Block Types (где уместно) / Inserter`. Внутри — блочная разметка (`core/group`, `core/columns`, `core/paragraph`, `core/buttons`, `core/html` только для спрайт-иконок), тексты по-русски через `esc_html__()`, примеры данных — реалистичные (Figma, Pentagram-подборка, «проверено 3 сен 2026»), не lorem. Один паттерн — один файл; варианты — через классы и атрибуты внутри одного файла или отдельные файлы `resource-card-tool.php`, если разметка отличается структурно.
5. **Parts:** `parts/header.html` (лого, навигация из brief §6, `search-form`, `theme-toggle`, мобильное меню на `<details>`), `parts/footer.html` (подписка, Telegram, принципы, политика). Навигация — `core/navigation` с меню, созданным через WP-CLI (`wp menu create`, `wp menu item add-custom`), не руками.
6. После каждого файла: хук `php -l`; `curl -s http://localhost:8080/styleguide/ | grep ds-<pattern>`; `debug.log`.

### Фаза 4. Витрина `/styleguide/`

1. Страница: `tools/wp.cmd --path=wordpress post create --post_type=page --post_name=styleguide --post_title="Styleguide" --post_status=publish` (если есть — не дублировать: `post list --post_type=page --name=styleguide --field=ID`).
2. Шаблон `templates/page-styleguide.html`: header part → `<!-- wp:pattern {"slug":"designstack/styleguide-foundation"} /-->` → по одному `styleguide-<pattern>` на паттерн → footer part.
3. `patterns/styleguide-foundation.php` (категория `designstack-styleguide`) читает `wp_get_global_settings()` и выводит: палитру семантики (свотч + имя + значение в текущей теме), примитивы, шкалу шрифтов строками, отступы линейкой, радиусы, тени. Ничего не хардкодит — источник `theme.json`.
4. `patterns/styleguide-<pattern>.php` — сетка: строки = варианты, столбцы = состояния; в каждой ячейке — тот же `patterns/<pattern>.php` через `do_blocks( '<!-- wp:pattern {"slug":"designstack/<pattern>"} /-->' )` с добавленным классом состояния (`is-hover`, `is-focus`, `is-disabled`) — не копия разметки. Песочницы композиций: «архив» (section-header + filter-chips + resource-list + pagination), «карточка + notice dead», «форма подписки во всех состояниях».
5. Переключатель «подсветить кликабельное» в шапке витрины: `<button aria-pressed>` вешает класс `is-highlight-interactive` на `<body>`, по нему `patterns.css` обводит контуром всё, что реально кликается (`a[href]`, `button`, `input`, `[tabindex]`, оверлей карточки), а информацию глушит. Работает на всех паттернах сразу: где бейдж выглядит кнопкой или ссылка не отличается от текста, видно за секунду и обсуждается отдельно.
6. `noindex`: в `functions.php` фильтр `wp_robots` → `noindex, nofollow` для `is_page('styleguide')`; страницу исключить из меню и sitemap (позже — в 17).
7. Ссылка на витрину — только в футере админ-бара (`admin_bar_menu`), не на сайте.

### Фаза 5. Проверка и аудит

1. Скриншоты: `python scripts/screenshot.py http://localhost:8080/styleguide/ --width 1440`, `--width 375`, оба — в светлой и тёмной (`--dark`); файлы в `.tmp/patterns/`.
2. Аудит по трём осям, построчно по каталогу: **типографика** — все размеры из шкалы, нет новых типостилей; **цвета** — `grep -rnE "#[0-9a-fA-F]{3,6}\b|rgb\(" themes/designstack --include=*.css --include=*.php --include=*.html` пуст, нет `--wp--custom--color--*` в `patterns.css`; **отступы** — `grep -nE "[0-9]+px" assets/css/patterns.css` показывает только `@media`. Плюс `python scripts/check_tokens.py`.
3. Покрытие состояний: для каждого паттерна сверить ячейки на скриншоте с матрицей в `components.md`; пустая ячейка = не сделано. Клавиатура: `Tab` по витрине — фокус виден на каждом интерактивном элементе (проверить скриншотом с `:focus-visible`-двойником).
4. Кликабельность — отдельная строка чеклиста витрины: включи «подсветить кликабельное» и пройди паттерны глазами. Обведено ровно то, что ведёт куда-то или что-то делает; ни бейдж, ни вердикт, ни мета-строка не выглядят контролом. Расхождение — правка паттерна, а не «и так понятно».
5. Длинный контент: карточка с названием в 80 символов и вердиктом в 200 — обрезка, не разъезд сетки; чип с длинной темой — перенос.
6. `tail -20 wordpress/wp-content/debug.log` — чисто. `curl` главной и одного архива — parts подхватились без ошибок.
7. Апрув заказчика по 4 скриншотам: `AskUserQuestion` «Библиотеку принимаем?» (Да / Правки: …). После «да» — `Status: verified` в каталоге.

Предлагать, не делать молча: микро-анимации появления, скелетоны, дополнительные размеры — отдельным вопросом после базовой матрицы.

## Формат результата

```
docs/ds/components.md                                          каталог: разделы, матрицы, токены, классы, Used in, Status
wordpress/wp-content/themes/designstack/patterns/<slug>.php      по паттерну на файл (категория designstack)
wordpress/wp-content/themes/designstack/patterns/styleguide-*.php  витринные обёртки (категория designstack-styleguide, скрыта)
wordpress/wp-content/themes/designstack/parts/header.html, footer.html
wordpress/wp-content/themes/designstack/templates/page-styleguide.html
wordpress/wp-content/themes/designstack/assets/css/patterns.css
wordpress/wp-content/themes/designstack/assets/img/icons.svg
wordpress/wp-content/themes/designstack/functions.php            block styles, категории, иконка-хелпер, noindex, enqueue
.tmp/patterns/*.png                                             4 скриншота витрины
```

## Self-check

- На каждый паттерн из инвентаря есть запись в `components.md` со всеми полями (включая «Тексты») и файл в `patterns/`? Перечислить отсутствующие — список пуст.
- Матрица каждого паттерна на витрине заполнена целиком (варианты × состояния), состояния — CSS-селекторами, а не копиями разметки?
- Витрина вставляет реальные `patterns/*.php`, Foundation читает `theme.json`?
- Ни одного hex/rgb/px вне `@media`, ни одного примитива в `patterns.css`, ни одного нового размера шрифта?
- `prefers-reduced-motion` учтён, переходы 150–200 мс, фокус виден везде, статусы — иконка плюс слово, цвет третий канал?
- Каждый текст паттерна есть в `docs/VOICE.md` тем же словом; слов, заведённых мимо словаря, — ноль?
- Подсветка кликабельного обводит ровно то, что кликается, и контролы отличимы от информации не только цветом?
- `/styleguide/` отдаёт `noindex`, не в меню; `debug.log` чист; `php -l` по всем файлам.
- Раздел «Контракт разметки» в каталоге заполнен для паттернов, которые будет рендерить 12?

## Финал

```
Библиотека паттернов собрана.
- docs/ds/components.md: <N> паттернов в <K> разделах, матрицы и токены заполнены
- Код: patterns/ <N> файлов, parts/ header + footer, block styles <список>, patterns.css <строк>, icons.svg <M> иконок
- Витрина: http://localhost:8080/styleguide/ (noindex) — Foundation + все паттерны × состояния + 3 песочницы
Проверено: hex/px вне токенов — 0, check_tokens — ок, состояния покрыты <N/N>, debug.log чист
Скриншоты: .tmp/patterns/{light,dark}-{1440,375}.png
Предложено, не сделано: <анимации / скелетоны / … или «нет»>
Дальше: /directive 12 (плагин и данные), затем /directive 13 (сборка страниц)
```

## Грабли

- **Копия вместо паттерна.** Витрина, собранная из «похожей» разметки, разъедется с сайтом через неделю. Только `wp:pattern` / `do_blocks()` реальных файлов.
- **Состояние как отдельная копия.** `resource-card-hover.php` — антипаттерн; hover живёт в CSS, витрина включает его классом-двойником.
- **Кэш паттернов.** WP кэширует зарегистрированные паттерны из `patterns/`; после правки заголовка файла — `tools/wp.cmd --path=wordpress cache flush` и перезагрузка страницы.
- **`core/html` в паттернах** отдаёт разметку как есть — допустим только для спрайт-иконок; текст и структура — блоками, иначе куратор не сможет править.
- **Навигация в part** без созданного меню рендерит пустоту: меню создавать WP-CLI до скриншота.
- **Мобильные фильтры.** Выезжающая панель — `<details>`/`popover` без JS на этом этапе; логика применения — в 14.
- **Высота карточек.** «Одинаковая по высоте» — через `grid` + `align-items: stretch` и обрезку вердикта `-webkit-line-clamp`, а не через фиксированную высоту в px.
- **Тёмная тема на витрине.** Проверять оба режима; чаще всего ломаются тени и бейджи с подложкой `-100`.
- **Слишком большая матрица.** `badge` 6 kinds × 5 tones = 30 ячеек: на витрине показывать по kind, в CSS — tone как единственная ось.
- **Паттерн без строки в `docs/ds/components.md`.** Файл есть, записи нет: 13 его не найдёт, 15 посчитает самодеятельностью, состояния никто не закроет. Сначала строка, потом файл.
- **Текст на кнопке, которого нет в словаре.** «Отправить» рядом с «Предложить» читается как два разных продукта. Новое слово — сначала в `docs/VOICE.md`, потом в паттерн.
- **Статус одним цветом.** Зелёная точка без слова не читается в ч/б, при дальтонизме и в тёмной теме. Иконка плюс слово, цвет — третий канал.

## Правила

- Никакого кода до апрува `components.md`; правки — сначала в каталоге, потом в файле.
- Один паттерн — один файл, имя латиницей kebab-case, slug `designstack/<slug>`; тексты по-русски с «ёлочками» и ё.
- Тексты паттернов — из `docs/VOICE.md`. Новое понятие заводится сначала строкой в словаре, потом попадает в разметку; своё слово в кнопке — баг.
- Статус показывается иконкой плюс словом, цвет — третий канал; кликабельное отличается от написанного формой, а не только цветом.
- Только семантические токены; примитивы — запрещены вне `theme-dark.css`.
- Состояния обязательны: default / hover / focus-visible / active / disabled + специфичные; списки — данные / пусто / загрузка / переполнение.
- Чек на дубликаты перед каждым новым паттерном; правило 3+/2/1 — при выносе из 13.
- Новые токены и типостили здесь не заводятся; нужен — мини-цикл 10 с записью в `foundation.md`.
- Проверка по факту: `php -l`, `curl`, `debug.log`, скриншоты в обеих темах. «Я написал файл» — не результат.
- Предлагать, не делать молча: всё сверх матрицы — вопросом заказчику.
