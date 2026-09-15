# Директива 10: Дизайн-токены и theme.json

> Этап 10 конвейера (00_pipeline.md). Вход: `docs/brief.md` §8, `docs/brand/brand-direction.md`, grey-box тема из 08. Выход: `docs/ds/foundation.md`, `theme.json`, `assets/css/theme-dark.css`, `assets/fonts/`, обновлённый `.claude/rules/wp-theme.md`, подписи статусов в `docs/VOICE.md`, записи в `docs/DECISIONS.md`. Запуск: /directive 10

## Задача

Поставить фундамент дизайн-системы сайта: двухслойные токены (примитивы → семантика) сначала текстом в `docs/ds/foundation.md`, затем материализовать их в `theme.json` v3 блочной темы `designstack`, добавить тёмную тему с переключателем и закрепить контракт в `.claude/rules/wp-theme.md`. После этой директивы вся вёрстка (11, 13, 14) берёт цвета, шрифты, отступы только из токенов.

## Когда применять

Один раз после 09 (бренд) и до 11 (паттерны). Повторно — при ребрендинге, смене акцента или шрифта, добавлении семантики (новый статус, новая поверхность). Повторный запуск = синхронизация `foundation.md` ↔ `theme.json`: директива читает оба, находит расхождения и правит, а не пересоздаёт.

## Предусловие

- `docs/brief.md` §8 — есть (утверждён).
- `docs/brand/brand-direction.md` (акцент, шрифт, характер) — из 09. Нет → `/directive 09`; если заказчик хочет идти без бренда — взять значения из brief §8 и допущения A7, записать в `foundation.md` как «A-10.x, пересмотреть после 09».
- Тема `wordpress/wp-content/themes/designstack/` существует (grey-box из 08: `style.css`, `theme.json`, `functions.php`, `templates/index.html`). Нет → `/directive 08`.
- Сервер поднят: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/` → 200.

## Роль

Дизайн-системный архитектор с опытом постановки ДС для контентных каталогов (B2C-веб, плотные карточки, тёмная тема, кириллица). Знает, как WordPress превращает `theme.json` в CSS-переменные `--wp--preset--*` и `--wp--custom--*`, и не пишет CSS там, где хватает `theme.json`.

## Ключевой принцип

**Два слоя, один источник.** Примитивы (`gray-500`, `accent-500`, `space-4`) в вёрстке не используются; всё ссылается на семантику (`text-muted`, `surface-action-primary`, `border-error`), а семантика — alias на примитив. Критерий готовности: смена одного значения акцента в `theme.json` перекрашивает все кнопки, ссылки и фокус-кольца; переключение темы не требует править ни один паттерн.

## Граница

- Не рисует паттерны (11), не собирает страницы (13), не трогает плагин (12).
- Не выбирает бренд и название (09): акцент и шрифт — данность.
- Не пишет `assets/css/patterns.css`; единственный CSS здесь — `theme-dark.css`, единственный JS — переключатель темы.
- Не расширяет шкалы сверх зашитого минимума без запроса заказчика.

## Фазы

### Фаза 1. Бриф: пять вопросов, ответы уже есть

Ответы на классический ds-бриф собрать из документов, не задавать заново:

```
1. Отрасль:    медиа-каталог для дизайнеров (brief §1)
2. Аудитория:  b2c, junior + middle (brief §3)
3. Тон:        <два прилагательных из brand-direction.md; по умолчанию «утилитарный, спокойный»>
4. Платформа:  web, mobile-first, брейкпоинты 600 / 900 / 1200 (brief §8)
5. Локаль:     ru — кириллица обязательна, названия продуктов латиницей
+ Акцент:      <hex из brand-direction.md>   + Шрифты: <sans / mono из brand-direction.md>
```

Один `AskUserQuestion`: «Зафиксировал так — верно?» с вариантами «Всё верно (Recommended)» / «Есть правки». Если `brand-direction.md` нет — в вопросе показать допущения (акцент, шрифт Inter + JetBrains Mono) с пометкой «A-10.1». Блок «Бриф» записать в шапку `docs/ds/foundation.md`.

### Фаза 2. `docs/ds/foundation.md` — текст до кода

Зашитый минимум (состав фиксирован, значения — под бриф):

**Слой 1 — примитивы**
- Палитра: акцент `accent-100/300/500/700/900`; 9 нейтралов `gray-00, 50, 100, 200, 300, 500, 700, 900, 950`; функциональные `success/warning/error/info` по два тона: `-500` (цвет) и `-100` (подложка бейджа). Для тёмной темы подложки `-900`.
- Типографика: `font-sans` (кириллица: Inter, Golos Text, Onest, IBM Plex Sans), `font-mono` (JetBrains Mono — ценники, даты); 9 ступеней `xs 12, sm 14, base 16, lg 18, xl 20, 2xl 24, 3xl 30, 4xl 36, 5xl 48`, от `2xl` — fluid; веса 400/500/600/700; `line-height-tight 1.2`, `line-height-base 1.55` (+5 % под кириллицу); `letter-spacing-tight −0.01em` на `3xl+`.
- Радиусы: `radius-none 0, sm 4, md 8, lg 16, full 999`.
- Отступы: `space-1 4, 2 8, 3 12, 4 16, 6 24, 8 32, 12 48, 16 64`.
- Тени: `shadow-sm/md/lg` — мягкие, нейтральные, без бренд-цвета; для тёмной темы отдельные значения (на тёмном тень не видна — выше непрозрачность плюс `border-default`).
- Прочее: `duration-fast 150ms`, `duration-base 200ms`, `ease-standard`, `border-width-hairline 1px`, `z-header/z-dropdown/z-modal`, `content-width 720px`, `wide-width 1200px`, брейкпоинты 600/900/1200 (только для `@media`).

**Слой 2 — семантика** — каждая строка обязана быть alias, две колонки значений:

```markdown
| Токен | Светлая | Тёмная | Где |
|---|---|---|---|
| surface-default | gray-00 | gray-950 | фон страницы |
| surface-subtle | gray-50 | gray-900 | подложки секций, фильтров |
| surface-raised | gray-00 | gray-900 | карточки |
| surface-action-primary | accent-500 | accent-500 | кнопка, активный чип |
| surface-action-primary-hover | accent-700 | accent-300 | |
| surface-selected | accent-100 | accent-900 | выбранный чип, aria-current |
| text-default | gray-900 | gray-50 | |
| text-muted | gray-500 | gray-300 | мета, даты |
| text-on-action | gray-00 | gray-950 | текст на акценте |
| text-link | accent-700 | accent-300 | |
| border-default | gray-200 | gray-700 | |
| border-strong | gray-300 | gray-500 | |
| border-focus-ring | accent-500 | accent-300 | outline 2px |
| border-error | error-500 | error-500 | |
| bg-success / text-success | success-100 / success-500 | success-900 / success-100 | |
| bg-warning / text-warning | warning-100 / warning-500 | warning-900 / warning-100 | |
| bg-error / text-error | error-100 / error-500 | error-900 / error-100 | |
| bg-info / text-info | info-100 / info-500 | info-900 / info-100 | |
```

**Статусы каталога → семантика** (для 11 и 12, чтобы бейджи не изобретали цвета):

```
ru_open:    open → success · vpn_only → warning · blocked → error
ru_payment: payable, ru_native → success · no_payment → warning · у бесплатных ресурсов бейджа нет (D28)
status:    active → без бейджа · changed → warning · dead → error (+ карточка text-muted)
checked_at: ≤ 90 дней → text-muted · > 90 дней → warning («Давно не проверяли»)
pricing:   free → success · freemium → info · trial → info · paid → нейтральный (border-default)
```

**Состояния → что меняется → токен** (обязательная таблица; новые токены только как alias):

| Состояние | Что меняется | Токен |
|---|---|---|
| hover | фон action темнее/светлее, ссылка — underline | `surface-action-*-hover` |
| focus-visible | outline 2px, offset 2px, не убирать | `border-focus-ring` |
| active (pressed) | фон как hover, без transform | `surface-action-*-hover` |
| disabled | `opacity .5`, `cursor: not-allowed`, отдельного токена нет | — |
| loading | тот же фон, контент под спиннером, `aria-busy` | — |
| selected / aria-current | фон подложки + обводка акцента | `surface-selected`, `border-focus-ring` |
| error | обводка и подпись | `border-error`, `text-error` |

Апрув: `AskUserQuestion` — «foundation.md утверждаем?» (Всё верно / Поменять акцент или шрифт / Поменять шкалы). Без «да» в `theme.json` не идём. Утверждённое записывается решением в `docs/DECISIONS.md` («Решено»: палитра, шрифт, механика тёмной темы — решение · причина · дата); что предложено, но не подтверждено, живёт в разделе «Предлагаю» и переезжает в «Решено» с датой, а не переписывается на месте.

### Фаза 3. Материализация

3.1 **Шрифты локально.** Скачать woff2 (Inter — github.com/rsms/inter releases; Golos Text, JetBrains Mono — их GitHub) в `assets/fonts/` вместе с лицензией (`OFL.txt`). Никаких Google Fonts по сети: закон о персональных данных и скорость. В `theme.json`: `settings.typography.fontFamilies[].fontFace` с `src: ["file:./assets/fonts/inter-variable.woff2"]`, `fontWeight: "400 700"`, `fontDisplay: "swap"`.

3.2 **Карта foundation → theme.json → CSS-переменная:**

| foundation | theme.json | CSS |
|---|---|---|
| примитивы цвета | `settings.custom.color.gray-500` | `--wp--custom--color--gray-500` |
| семантика цвета (светлая) | `settings.color.palette[{slug:"text-muted", color:"var(--wp--custom--color--gray-500)"}]` | `--wp--preset--color--text-muted` |
| шкала шрифта | `settings.typography.fontSizes` + `fluid: {min,max}` | `--wp--preset--font-size--lg` |
| шрифты | `settings.typography.fontFamilies` | `--wp--preset--font-family--sans` |
| отступы | `settings.spacing.spacingSizes` (`spacingScale.steps: 0`) | `--wp--preset--spacing--4` |
| тени | `settings.shadow.presets` | `--wp--preset--shadow--md` |
| радиусы, длительности, z-index, hairline | `settings.custom.radius.md` и т. п. | `--wp--custom--radius--md` |
| ширины | `settings.layout.contentSize / wideSize` | — |

Palette хранит только семантику (примитивов в палитре редактора быть не должно — куратор выбирает «text-muted», а не «gray-500»). Значение палитры — `var()` на примитив: одна точка изменения. Отключить дефолты WP: `color.defaultPalette: false`, `defaultGradients: false`, `typography.defaultFontSizes: false`, `spacing.defaultSpacingSizes: false`, `shadow.defaultPresets: false`.

3.3 **`styles`:** `styles.color` (body = `surface-default` / `text-default`), `styles.typography` (font-sans, base, line-height-base), `styles.elements.link` (`text-link`, `:hover` underline, `:focus` outline), `styles.elements.button` (`surface-action-primary`, `:hover`, `:focus`), `styles.elements.h1…h6` (шкала, `line-height-tight`, вес 600), `styles.spacing.blockGap` = `space-4`, `styles.blocks.core/separator` = `border-default`. Ничего блочно-специфичного сверх этого — остальное в 11.

3.4 **Тёмная тема — `assets/css/theme-dark.css`.** Сначала проба: возможности проверяются прогоном, а не по документации. До того как завязывать тёмную тему на переключатель во всех шаблонах, собери маленькую пробу — один семантический токен в `theme.json`, его переопределение в `theme-dark.css`, три строки на `localStorage` — и открой реальную страницу локального сервера: порядок стилей, специфичность `:root`, реакция на `prefers-color-scheme` и мигание при загрузке видны только там. Проба прошла — раскатывай на весь набор семантики.

Переопределение только preset-переменных семантики через примитивы:

```css
:root[data-theme="dark"] { --wp--preset--color--surface-default: var(--wp--custom--color--gray-950); … }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { /* тот же набор */ } }
```
Оба блока — один и тот же список, вторая колонка таблицы из фазы 2. Плюс `color-scheme: light dark` на `:root`, иначе нативные контролы и скроллбары останутся светлыми.

**Переключатель:** `assets/js/theme-toggle.js` (≤ 40 строк, без зависимостей): читает `localStorage.designstack-theme`, ставит `data-theme` на `<html>`, кнопка `.ds-theme-toggle` с `aria-pressed` и подписью «Тёмная тема» / «Светлая тема». Чтобы не мигало при загрузке — крошечный инлайн-скрипт в `wp_head` с приоритетом 0, который выставляет атрибут до отрисовки. Сама кнопка ставится в шапку в 11.

3.5 **Почему не `styles/dark.json` как единственный механизм.** Вариации стилей (`styles/*.json`) переключает редактор сайта, а не посетитель: активной может быть одна, и она одна для всех. Переключатель темы посетителя по брифу §8 — это CSS-переменные + атрибут. `styles/dark.json` допустимо добавить позже как превью тёмной темы в редакторе, но это не выход директивы.

3.6 **`functions.php`:** `wp_enqueue_style('designstack-theme-dark', …, array('global-styles'), filemtime())` в `wp_enqueue_scripts` и в `enqueue_block_assets` (чтобы редактор тоже видел), `wp_enqueue_script` переключателя с `strategy => 'defer'`. Порядок важен: тёмный CSS должен идти после инлайновых global styles, иначе переопределение проиграет.

3.7 **Словарь и статусы — парой.** Одновременно с токенами заводится словарь интерфейса `docs/VOICE.md`. Этап 10 отвечает за то, чтобы подписи статусов (`ru_open`, `ru_payment`, `status`, `pricing`, `level`) в словаре и цвета статусов в токенах были заведены парой: у каждого статуса есть цвет, иконка (набор Lucide выбран в 09) и слово. Одно понятие называется одним словом на всех страницах: «Работает из РФ» и на карточке, и в фильтре, и в подсказке. Статус не показывается одним цветом: иконка плюс слово обязательны, цвет — третий канал (brief §8). Список ключей в таблице «Статусы каталога → семантика» (`foundation.md`) и в `docs/VOICE.md` — один и тот же; расхождение — баг этапа 10, а не 11.

### Фаза 4. Проверка по факту

Дампа `theme.json` в WP-CLI нет — проверяем рендером.
1. `python -m json.tool wordpress/wp-content/themes/designstack/theme.json` и `tools/wp.cmd --path=wordpress eval 'print_r( wp_get_theme("designstack")->errors() );'` → пусто.
2. `curl -s http://localhost:8080/ | grep -o -- "--wp--preset--color--surface-default:[^;]*"` — переменная присутствует и равна `var(--wp--custom--color--gray-00)`.
3. Витрина: если `/styleguide/` из 11 ещё нет — создать заглушку через WP-CLI (`wp post create --post_type=page --post_name=styleguide --post_title=Styleguide` с core-блоками: заголовки h1–h4, абзац с ссылкой, кнопки, список, разделитель). Скриншоты: `python scripts/screenshot.py http://localhost:8080/styleguide/ --width 1440` и `--width 375`; для тёмной — скрипт с `--dark` (эмулирует `prefers-color-scheme`; если флага нет — добавить в `scripts/screenshot.py`). Четыре файла в `.tmp/tokens/`.
4. Хардкод: `grep -rnE "#[0-9a-fA-F]{3,6}\b" wordpress/wp-content/themes/designstack --include=*.css --include=*.html --include=*.php` → только `theme.json` (в grep не попадает) — то есть вывод пуст. Аналогично `grep -rnE "[0-9]+px"` — допустимы только `@media` и `theme.json`.
5. «Смени акцент — всё перекрасилось»: временно заменить `accent-500` в `settings.custom`, скриншот главной — кнопки, ссылки, фокус, активный чип поменялись все; вернуть значение. Если что-то не перекрасилось — это hardcode, чинить сейчас.
6. Контраст: `python scripts/check_tokens.py` — читает `theme.json` и `theme-dark.css`, считает WCAG-контраст пар `text-default/surface-default`, `text-muted/surface-default`, `text-muted/surface-subtle`, `text-on-action/surface-action-primary`, `text-link/surface-default`, `text-<status>/bg-<status>` в обеих темах; порог 4.5:1 (3:1 для `border-focus-ring` на фоне). Скрипт также ловит палитру без `var()` и hex вне `theme.json`. Пишется в этой директиве, если его ещё нет (Python 3.12, без зависимостей). Не прошло — двигать примитив, не семантику.
7. `tail -20 wordpress/wp-content/debug.log` — без новых ошибок.

Показать заказчику 4 скриншота одним сообщением, `AskUserQuestion`: «Принимаем фундамент?» (Да / Поправить тёмную / Поправить светлую).

**Ворота этапа 10** — проверяемое состояние, а не «агент разрешил». Каждый пункт показывается файлом, выводом команды или скриншотом; что показать нечем — не пройдено.
- [ ] Смена одного значения акцента перекрашивает все страницы — два скриншота «было и стало» (п. 5).
- [ ] `grep` не находит hex вне `theme.json` — пустой вывод команды из п. 4.
- [ ] Контраст в обеих темах не ниже 4,5:1 — вывод `check_tokens.py` с минимумом по светлой и по тёмной (п. 6).
- [ ] У каждого статуса есть цвет, иконка и слово из `docs/VOICE.md` — строка таблицы плюс бейдж на скриншоте витрины.

### Фаза 5. Контракт — `.claude/rules/wp-theme.md`

Переписать файл (front-matter `paths:` для темы и плагинов `designstack-*` сохранить). Новое содержимое, разделы:
1. **Кодстайл WP** — прежние пункты (WPCS, префикс `designstack_`, экранирование, i18n `designstack`, enqueue, никакого SQL, SQLite).
2. **Токены — единственный источник.** Цвета только `var(--wp--preset--color--<семантика>)`; размеры шрифта — `--wp--preset--font-size--*`; отступы — `--wp--preset--spacing--*`; радиусы/тени/длительности — `--wp--custom--*` / `--wp--preset--shadow--*`. Примитивы (`--wp--custom--color--*`) в CSS паттернов запрещены — только в `theme-dark.css`.
3. **Запрет hardcode:** hex, rgb, px (кроме `@media` и `0`), имена шрифтов вне `theme.json` — баг; проверка `python scripts/check_tokens.py`.
4. **Нейминг:** `surface-* / text-* / border-* / bg-*`, суффиксы `-hover / -selected / -error`, kebab-case, латиница.
5. **Новый токен:** сначала строка в `docs/ds/foundation.md` (обе колонки), затем `theme.json` как alias, затем `theme-dark.css`; прибитое значение в семантике не принимается.
6. **Тёмная тема:** новая семантика обязана получить тёмное значение в тот же коммит; примитивы не переопределяются.
7. **Чеклист перед коммитом:** `php -l` (хук), `python -m json.tool theme.json`, `python scripts/check_tokens.py`, `curl` страницы, `debug.log`, скриншот в обеих темах при визуальных изменениях.

Отдельный `docs/ds/CONTRACT.md` не нужен: правила в `.claude/rules/*.md` с `paths:` подгружаются автоматически при работе с файлами темы, а документ в `docs/` агент читать не обязан. Контракт живёт там, где срабатывает.

## Формат результата

```
docs/ds/foundation.md                                   бриф, слой 1, слой 2 (светлая/тёмная), статусы, состояния
docs/VOICE.md                                           подписи статусов: ключ → слово (файл уже есть, дописываем)
docs/DECISIONS.md                                       «Решено»: палитра, шрифт, механика тёмной темы (дописываем)
wordpress/wp-content/themes/designstack/theme.json       v3: custom (примитивы), palette (семантика), fonts, sizes, spacing, shadows, styles
wordpress/wp-content/themes/designstack/assets/fonts/    woff2 + OFL.txt
wordpress/wp-content/themes/designstack/assets/css/theme-dark.css
wordpress/wp-content/themes/designstack/assets/js/theme-toggle.js
wordpress/wp-content/themes/designstack/functions.php    enqueue (дополнен)
scripts/check_tokens.py                                 контраст, alias, hardcode
.claude/rules/wp-theme.md                               контракт (переписан)
.tmp/tokens/*.png                                       скриншоты проверки
```

## Self-check

- Каждая строка слоя 2 в `foundation.md` имеет светлое и тёмное значение и оба — имена примитивов, не hex?
- Каждый семантический токен из `foundation.md` есть в `palette` (как `var()` на примитив) и в `theme-dark.css`? Перечислить расхождения — список пуст.
- В `palette` нет примитивов; дефолтные палитра/размеры/отступы WP отключены?
- `grep` hex/px по теме пуст; `check_tokens.py` — все пары ≥ 4.5:1 в обеих темах?
- Тест «смени акцент» пройден и значение возвращено?
- Шрифты локальные, с кириллицей, лицензия лежит рядом; `font-display: swap`?
- `.claude/rules/wp-theme.md` переписан, front-matter `paths:` на месте?
- У каждого статуса (`ru_open`, `ru_payment`, `status`, `pricing`, `level`) есть цвет, иконка и слово из `docs/VOICE.md`; список ключей в `foundation.md` и в словаре совпадает?
- Ворота этапа пройдены, и каждый пункт показан файлом, выводом команды или скриншотом?
- Решения по палитре, шрифту и механике тёмной темы записаны в `docs/DECISIONS.md` («Решено», с датой)?
- `debug.log` чист, скриншоты 4 шт. показаны заказчику.

## Финал

```
Фундамент ДС поставлен.
- docs/ds/foundation.md: примитивы <N>, семантика <M> (светлая + тёмная), статусы каталога, таблица состояний
- theme.json v3: palette = семантика через var(), custom = примитивы, шрифты локально (<имена>), 9 размеров (fluid), 8 отступов, 3 тени
- Тёмная тема: assets/css/theme-dark.css + переключатель (localStorage, prefers-color-scheme)
- Контракт: .claude/rules/wp-theme.md переписан
- Словарь и журнал: docs/VOICE.md — у каждого статуса цвет, иконка и слово; docs/DECISIONS.md — решения по палитре, шрифту, тёмной теме
Проверено: json валиден, ошибок темы нет, hex вне theme.json — 0, контраст ≥ 4.5:1 в обеих темах (<min light> / <min dark>), тест «смени акцент» — ок, debug.log чист
Скриншоты: .tmp/tokens/{light,dark}-{1440,375}.png
Допущения: <A-10.x или «нет»>
Дальше: /directive 11 — паттерны и витрина /styleguide/
```

## Грабли

- **`var()` в палитре и редактор.** На фронте WP выводит значение как есть, и alias работает. Если в редакторе свотчи палитры окажутся пустыми — запасной путь: hex в палитре, а `check_tokens.py` проверяет, что каждый hex совпадает с одним из примитивов. Не молчать, зафиксировать выбор в `foundation.md`.
- **Порядок стилей.** Global styles выводятся инлайном; `theme-dark.css` без зависимости `global-styles` может встать раньше и проиграть. Проверять `curl`-ом порядок `<style id="global-styles-inline-css">` и `<link id="designstack-theme-dark-css">`.
- **Где WP выводит preset-переменные.** С WP 6.6 — на `:root`; переопределять на `:root[data-theme="dark"]` (специфичность выше), не на `body`.
- **Тени на тёмном.** Скопированные из светлой темы тени исчезают; давать тёмной теме свои `shadow-*` через переопределение `--wp--preset--shadow--*` и добавлять `border-default` карточкам.
- **Мигание темы.** Без инлайн-скрипта в `<head>` страница сначала рисуется светлой. Скрипт — до любого CSS, приоритет `wp_head` 0.
- **Кириллица.** Проверить Щ, Ъ, Ы, ё и «ёлочки» на скриншоте; subset-файл woff2 «latin only» — частая ошибка при скачивании.
- **Контраст `text-muted`.** `gray-500` на белом обычно 4.6:1 — на `surface-subtle` уже может не пройти; считать обе пары.
- **`fluid` без `min/max`** масштабирует по своим правилам; для `xs`–`xl` fluid выключать явно (`"fluid": false`), иначе мелкий текст на мобильном станет ещё мельче.
- **SQLite.** Никаких `wp db`; проверять только через `wp eval`, `curl`, скриншоты.

## Правила

- Сначала `foundation.md` и апрув, потом `theme.json`. Правка текста дешевле правки JSON и CSS.
- Семантика — только alias. Прибитое значение в слое 2 или в `theme-dark.css` — баг.
- Имена — ровно как в `foundation.md`: `surface-action-primary`, не `surfaceActionPrimary` и не `surface_action_primary`.
- Никаких сетевых шрифтов, никаких CDN.
- Шкалы — зашитый минимум; расширение только по запросу и с записью в `foundation.md`.
- Без фазы 5 директива не завершена: без контракта фундамент — декорация.
- Статус не показывается одним цветом: цвет, иконка и слово заводятся парой с записью в `docs/VOICE.md`.
- Возможности проверяются прогоном: связка `theme.json` + CSS-переменные + `localStorage` сначала маленькой пробой на живой странице, потом на всех шаблонах.
- Повторный запуск синхронизирует, а не пересоздаёт; удалять токен можно только после `grep` по теме и плагину, что он нигде не используется.
