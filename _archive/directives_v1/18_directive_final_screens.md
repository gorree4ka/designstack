# Директива: Сборка финальных экранов (final_screens)

## Задача
Собрать финальный экран продукта в Figma, заменив каркасные прямоугольники из wireframe на instance реальных компонентов из UI-кита, с привязками к ДС и проработанными состояниями (включая edge cases — empty / loading / overflow). На входе — wireframe (фрейм Figma из урока 4) и каталог компонентов `ds/components.md`. На выходе — фрейм `Screen/<Name>` в SectionNode «Screens», composition map в `ds/screens/<name>.md`, и записи `used in: screens/<name>` у задействованных компонентов в `ds/components.md`.

Директива работает в двух режимах:
- **Single** — `final_screens <ScreenName>` для одного экрана
- **Bulk** — `final_screens` без аргумента: агент идёт по списку wireframes из урока 4 и собирает экраны по очереди

Один экран = один `use_figma`-вызов. Bulk — это серия single-прогонов под капотом.

## Роль
Дизайнер-сборщик с практикой высадки экранов из wireframe + готовой ДС. Знает разницу между instance и detached-копией, всегда оставляет привязку к Component Set. Заранее закладывает edge cases (empty / loading / overflow), не оставляет это на «потом». Привычка — фиксировать структуру в md (composition map), и только после апрува писать на канвас.

> Адаптируй роль под продукт:
> - B2C веб (магазин, медиа, лендинг) → акцент на hero, секционная вёрстка, состояния product card, корзина, чекаут
> - B2B SaaS (dashboard, CRM, админка) → акцент на data-density, таблицы, фильтры, sidebar-навигация, empty states, скелетоны, разные роли
> - Мобильное приложение → акцент на нижнюю навигацию, sheet/drawer, скролл-листы, состояния офлайна
> - Внутренняя админка → меньше визуального лоска, больше edge cases (длинные значения, многоколоночность, сортировки, bulk-actions)

---

## Концептуальные принципы

Семь инвариантов, без которых экран выходит сырым и пользователь правит руками. Они применяются на каждом прогоне директивы, не как polish-набор после фидбэка.

### 1. Sizing — это смысл, не размер

Auto Layout в Figma имеет три режима по каждой оси: **FIXED** (явное число), **HUG_CONTENTS** (по контенту), **FILL_CONTAINER** (по родителю). Использовать `FIXED × FIXED` как дефолт для секций — главная ошибка: жёсткий каркас, который ломается при изменении контента.

Соответствие смыслу:

| Уровень | Width | Height |
|---------|-------|--------|
| Screen (корневой 1440×) | FIXED | HUG (или FIXED только для design-canvas) |
| Top-section (Header / Body / PageHeader / Toolbar / Banner) | **FILL** | **HUG** (Header может FIXED-height для banner-стиля) |
| Column внутри Body (Form / Sidebar / Summary) | sidebar/summary — FIXED, основной — **FILL grow=1** | FILL или HUG |
| Row (StatsRow, ActionRow, Filters) | **FILL** | HUG |
| Spacer (`sp`) | **FILL grow=1** | FILL или HUG |
| Card в horizontal grid | FIXED по сетке или FILL grow=1 для равных | HUG |
| Button / Badge / Chip / Input | HUG | HUG (или FIXED H для конкретной высоты) |
| Modal | FIXED width по дизайну | **HUG** (растёт под контент) |
| Иконка | FIXED W×H |

**API в плагине:** `node.layoutSizingHorizontal/Vertical = "FILL" / "HUG" / "FIXED"`. Ставится **только после `appendChild`** в parent с auto-layout. Не использовать `primaryAxisSizingMode = "FIXED"` + `resize(w,h)` для секций — это и есть источник жёсткого каркаса.

### 2. Все компоненты — instance, не дубликаты

`.createInstance()` от мастера через `getNodeById`. Никакого `cloneNode`, никаких ручных копий геометрии. Если в результате нашёлся `FRAME` вместо `INSTANCE` — пересборка соответствующего блока. Привязка к Component Set — единственный способ, чтобы правки в ДС автоматически переезжали на экраны.

### 3. Все цвета и размеры — через Variables

`fills`, `strokes`, `cornerRadius`, `padding*`, `itemSpacing`, `fontSize` — биндить к Semantic / Primitive variables через `setBoundVariableForPaint` и `setBoundVariable`. На уровне screen и крупных секций — обязательно. На уровне instance — наследуется из Component Set, проверяй, что override не вернул прибитый hex. Если нашёлся `SOLID hex` без bound variable — пересборка.

### 4. Иконки — реальные SVG из библиотеки, не серые квадраты

Перед сборкой экрана **спроси про библиотеку иконок** (Lucide / Phosphor / Heroicons / Material / собственный набор), если в проекте не зафиксирована (нет `ds/icons.md` или строки в `ds/CONTRACT.md`). Дефолт — Lucide. После — иконки рендерятся через `figma.createNodeFromSvg()` в **первой итерации**, не во второй после фидбэка «выглядит сыро».

```js
const node = figma.createNodeFromSvg(lucideSvgString);
node.resize(size, size);
for (const v of node.findAll(n => n.type === 'VECTOR')) {
  if (v.strokes && v.strokes.length > 0) bindStroke(v, S["text-muted"]);
}
```

Placeholder Rectangle уместен только для: логотипа бренда (заменяется руками), реального изображения, реального QR-кода. В composition map указывать конкретное имя иконки (`Lucide / chevron-down 12px`), не «icon placeholder».

### 5. Тени из foundation — это база, не polish

Если в `ds/foundation.md` есть `shadow-sm/md/lg` — применяй с первого прогона. Без теней Card / Modal / Toast / Dropdown-panel визуально плоские и сливаются с фоном. Стандартный маппинг:

- Card (interactive / hover): `shadow-sm` или `shadow-md`
- Modal: `shadow-lg`
- Toast: `shadow-sm`
- Dropdown / Select panel: `shadow-md`
- Sticky sidebar / summary: `shadow-sm`

Если Effect Styles в foundation нет — сообщи пользователю, не пропускай тихо.

### 6. Информативность — Dashboard не может быть пустым

Если первый проход даёт экран с контентом только в верхних 30-40% высоты — composition map неполный. Минимум **60% площади** dashboard / overview-экрана должно быть занято осмысленным контентом. Стандартные секции для дашборда продукта:

- Топ-метрика (баланс / основная цифра / KPI) с visual hierarchy
- Mini-graph активности (sparkline / progress bar / trend chart)
- Список основных сущностей с богатой мета-информацией
- Quick actions / shortcuts row
- Recent activity / feed
- Recommendations / upgrade-prompts (если уместно)

Адаптировать под продукт, но пустой dashboard — это баг, не feature.

### 7. Структурированная мета — не plain text через точки

Антипаттерн: `Ubuntu 22.04 · Амстердам · 2 CPU / 4 GB · uptime 12 дней` одной строкой в карточке. Выглядит дёшево, плохо сканируется. Правильно — каждое поле отдельным визуальным элементом:

- ОС → иконка дистрибутива + текст
- Регион → флаг-эмодзи + текст
- Specs → chip-badges (CPU / RAM / Disk) с иконками
- Uptime → muted-блок с иконкой clock

В composition map для каждой карточки списка явно расписывать какие поля и в каких визуальных формах. То же для FAQ / help-links — это **clickable** (chevron-right, underline или accordion), не голый текст.

### 8. Повторяющиеся блоки — это компонент в UI-ките, не локальная сборка

Если на экране оказалось **3+ копий** одного блока (карточки серверов, строки активности, шаги explainer'а, stat-cards, quick-actions) — это компонент. Не «домен-композиция с пометкой кандидат на вынос потом», а:

- Обнаружили в Phase 1.5
- Согласовали с пользователем
- Создали в UI-ките через short-cycle `grow_ui_kit` (Phase 2.5) **в том же прогоне `final_screens`**
- Записали в `ds/components.md` (новая строка с матрицей вариантов и Used-in)
- Использовали как `createInstance()` в финальном экране, а не frame-копии

Пороги:
- **3+ копий** → выносим (almost always)
- **2 копии** → спорно, спрашиваем пользователя (часто это знак что будет третий случай)
- **1 копия** → не выносим, локальная композиция

Если попутно понадобились новые семантические токены (например, `surface-activity-income` / `surface-activity-outcome`) — добавить в `ds/foundation.md` Slой 2 как alias к существующим Primitive, синхронизировать в Variables через тот же short-cycle `ds_baseline`-расширение. Это инвариант: **новые токены добавляются как alias, не как прибитые значения**.

**Why:** копии локально — бомба замедленного действия. Когда дизайнер потом захочет поменять hover-фон на ServerCard — придётся править в трёх местах вручную, а ещё чаще — в одном поправят, в других забудут. Компонент в UI-ките делает правку в одной точке.

---

## Выбор режима

### Single-режим: `final_screens <ScreenName>`

Используется когда:
- Собираешь один конкретный экран, на котором сейчас работаешь
- Хочешь полный контроль над composition map
- Демо или обучение
- Экран нестандартный — нужно самому расписать секции, без bulk-автомата

### Bulk-режим: `final_screens` (без аргумента)

Используется когда:
- Все wireframes уже на месте, ДС готова, нужно собрать сразу несколько экранов
- Экраны типовые (Dashboard / List / Settings / Profile / Form)
- Готов потратить время на ручную доводку каждого после прогона

В bulk агент:
1. Находит SectionNode «Wireframes» в Figma, читает список фреймов
2. Сверяет с уже собранными экранами в SectionNode «Screens» (если есть) — пропускает уже собранное, спрашивает подтверждение если хочется пересобрать
3. По каждому несобранному фрейму запускает короткий бриф: «Wireframe Dashboard содержит 4 секции — Header / Sidebar / Stats Row / Files Table. Собираем? Если да — какие edge cases закладываем (empty/loading)?»
4. На «да» — single-прогон через все фазы
5. На «нет» или «пропустить» — переходит к следующему

В bulk пользователь не теряет контроль над скопом — каждый экран проходит через явный апрув брифа и composition map.

---

## Фаза 0. Pre-flight — спросить про ресурсы

### Фаза 0.1: Библиотека иконок

Если в проекте нет фиксированного стандарта (нет `ds/icons.md` или явной строки в `ds/CONTRACT.md`) — спроси:

> Какая библиотека иконок? Lucide / Phosphor / Heroicons / Material / собственный набор?

Дефолт-рекомендация — **Lucide** (де-факто стандарт для tech-продуктов, MIT, кириллицу не ломает, легко рендерится через `figma.createNodeFromSvg()`). Если пользователь подтверждает — зафиксируй в `ds/CONTRACT.md` строкой «Icon library: Lucide» или «Icon library: <выбор>».

После ответа — иконки **обязательно ищутся и внедряются с первой итерации**, не оставляются как placeholder Rectangle. Серый Rectangle уместен только для специфичного контента (логотип бренда, реальный QR-код, реальное изображение под замену вручную).

### Фаза 0.2: Effect Styles / Shadows

Проверь `ds/foundation.md` Effects/Shadows — там должны быть `shadow-sm/md/lg`. Они применяются при сборке, не во второй итерации после фидбэка. Маппинг по умолчанию:

- Card (interactive / hover): `shadow-sm` или `shadow-md`
- Modal: `shadow-lg`
- Toast: `shadow-sm`
- Dropdown / Select panel: `shadow-md`
- Sticky sidebar / summary: `shadow-sm`

Если Effects в foundation нет — пред-этап `ds_baseline` должен был их положить. Если их там реально нет (legacy-проект) — сообщи пользователю и предложи добавить.

---

## Фаза 1. Read — что есть на входе

### Фаза 1.1: Чтение wireframe в Figma

Найди фрейм по имени в SectionNode «Wireframes». Через `get_metadata`:
- Структура секций (имена дочерних фреймов, иерархия)
- Auto Layout-параметры на каждой секции (если уже стоят)
- Подписи / placeholder-тексты, которые проставил агент в уроке 4

Если фрейма нет — переспроси: «wireframe `<ScreenName>` не найден. Создавать его сейчас? Это задача урока 4, не текущей директивы. Запустить `wireframes`?»

### Фаза 1.2: Чтение `ds/components.md`

Прочти весь каталог компонентов. Сохрани в `componentsCatalog`:
- По каждому компоненту: имя, Node ID, доступные variants / states / sizes, краткое назначение
- Если у компонента есть строка `used in:` — её тоже сохрани, понадобится для аудита в уроке 10

### Фаза 1.3: Сверка покрытия

Пройдись по секциям wireframe. На каждой подписи (например, «Карточка статистики», «Таблица файлов») попытайся подобрать компонент из `componentsCatalog`. Веди черновой список:

```
Wireframe секция     → Кандидат из ДС
Header (logo+nav)    → NavMenu/Primary + Logo (нет в ДС, плейсхолдер)
Sidebar              → NavMenu/Vertical
Stats card           → Card/Default + Badge
Files table          → Table/Default + Pagination
Empty state plate    → Card/Default (используем как контейнер)
```

Если для секции в ДС нет компонента-кандидата — пометь и выведи в чат:

```
Не нашёл компонента под секцию "<имя>". Варианты:
1. Сначала добавить компонент в ДС через grow_ui_kit (рекомендую)
2. Использовать ближайший — <имя кандидата>, потерять часть смысла
3. Пропустить эту секцию, оставить wireframe-плейсхолдер

Что выбираем?
```

Без явного решения дальше не идёшь.

### Фаза 1.4: Анализ достаточности wireframe

Wireframe из стадии low-fi (директива `wireframes`) часто схематичен — секции в виде серых прямоугольников и одной строки текста. На переходе в final-screen агент **обязан** не просто переложить wireframe 1:1, а провести **анализ информационной достаточности** и предложить пользователю доработки. Без этого экран на выходе будет таким же сырым, как wireframe, только с компонентами вместо плейсхолдеров.

Пройдись по каждой секции wireframe и проверь:

1. **Семантическая ёмкость секции.** Wireframe-секция «Карточка сервера» содержит только Title + 1 строку метаданных? Это сыро — на финальном экране сущность должна быть раскрыта (status, IP, specs, region, uptime, actions). См. Принцип 7 — структурированная мета.

2. **Пустые зоны экрана.** В wireframe нижние 60% — пусто? Это не feature, это пробел в композиции. Дашборд / overview-экран должны быть заполнены минимум на 60% (Принцип 6). Предложи дополнительные секции (StatsRow, QuickActions, RecentActivity, Tips, Onboarding-prompts) в зависимости от типа продукта.

3. **Edge cases.** В wireframe только default-state? Empty / loading / error / overflow обычно не закладываются на стадии low-fi. На final-screen они нужны — закладываются как `visible:false` соседи (Phase 4 правило 9).

4. **Скучный CTA-уровень.** Один primary-кнопкой не закрыть продукт. Spotting: где быстрые действия пользователя кроме главного потока? На дашборде в норме 3-5 quick-actions, не один.

5. **Голый текст там, где нужен интерактив.** FAQ / help-links / breadcrumbs / footer-links — в wireframe могут быть как plain текст. На final — это chevron / underline / accordion (Принцип 7 второй половиной).

6. **Списочные блоки с одним элементом.** В wireframe «список серверов» содержит 1 фейковую строку? На final — минимум 3 для иллюстрации realistic state, разные статусы (running / stopped / deploying), разные размеры мета.

Сформируй сводку для пользователя и **спроси решение по каждому пункту**:

```
Анализ wireframe Dashboard:

[1] СЫРАЯ СУЩНОСТЬ: «карточка сервера» в wireframe содержит только имя + IP. На final раскрываем до:
    icon + name + status-badge + kebab → IP + copy → 3 chips (OS / Region / Specs) → footer (uptime + Детали).
    Принять? (да / убрать что-то / оставить как в wireframe)

[2] ПУСТАЯ ЗОНА: wireframe заполнен на ~30%. Предлагаю добавить:
    - StatsRow из 3 metric cards (баланс / активные серверы / прогноз)
    - QuickActions row из 4 кнопок (Создать / Пополнить / Reboot all / Status)
    - RecentActivity card из 4 строк операций
    Принять весь блок / выбрать часть / оставить пустым?

[3] EDGE CASES не заложены в wireframe. Предлагаю:
    - EmptyState (нет серверов) с illustration + CTA
    - ZeroBalanceBanner (баланс ≤ 0) с red-fill warning
    Заложить? (да / нет / только N)

[4] МАЛО CTA-уровней. Предлагаю QuickActions row.
    Принять? (см. [2])

[5] LIST с 1 элементом → расширяю до 3 серверов с разными статусами для реалистичности.
    Принять?
```

На «да» / «принять» — учитывается в composition map в Phase 2. На «нет» / «оставь как есть» — не лезешь, идёшь дальше.

> Это **обязательная** фаза, не опция. Без неё final-экран будет таким же сырым как wireframe.

### Фаза 1.5: Идентификация повторяющихся паттернов

После анализа достаточности — пройдись по предполагаемой композиции и найди **повторяющиеся блоки** (см. Принцип 8). Кандидаты:

- Списочные карточки (3+ ServerCard, 3+ ProjectCard, 3+ FileRow)
- Метрические карточки (StatCard, KpiTile)
- Шаги explainer'а / onboarding (StepItem, OnboardStep)
- Action-chips (QuickActionChip, FilterChip)
- Activity / log rows (ActivityRow, LogEntry)
- Notification / Toast / Alert
- Comment / Reply (если соц. компонент)

По каждому повторяющемуся блоку — спроси пользователя:

```
Обнаружены повторяющиеся блоки:

[A] ServerCard — 3 копии в Dashboard. Кандидат на вынос в UI-кит?
    + Variants: status (running / stopped / deploying / error)
    + Используется потом и в Servers list page
    Выносим? (да / нет / отложить)

[B] StatCard — 3 копии в Dashboard. Кандидат?
    + Generic metric card, переиспользуется в Reports / Analytics
    Выносим?

[C] ActivityRow — 4 копии в RecentActivity. Кандидат?
    + Variants: type (income / outcome / system / warning)
    Выносим?

[D] StepItem — 4 копии в BillingTopup explainer. Кандидат?
    + Не уверен в переиспользовании, есть только тут
    Выносим? (рекомендую: оставить локально пока)
```

На «да, выносим» — добавляется в очередь Phase 2.5 (inline grow_ui_kit). На «оставить локально» — собирается как domain-composition в финальном экране, помечается в md-карте «при появлении 2-го экрана с этим блоком — вынести через grow_ui_kit».

Если для нового компонента нужны новые семантические токены — пометить также. Они уйдут в Phase 2.5 вместе с компонентом.

---

## Фаза 2. Composition map — md-карта экрана

### Фаза 2.0: Принципы информативности

Composition map описывает не только «какие компоненты», но и **визуальную детализацию данных**. Без этого экраны выходят сырыми и пустыми. Три правила:

**1. Dashboard / Overview не может быть пустым.** Если первый проход даёт экран с контентом только в верхних 30-40% высоты — composition map неполный, добавляй секции. Минимум 60% площади должно быть занято осмысленным контентом. Стандартные секции дашборда:
- Топ-метрика (баланс / основная цифра / KPI) с visual hierarchy
- Mini-graph активности (sparkline / progress bar / trend chart)
- Список основных сущностей с богатой мета-информацией (icons, badges, chips, не plain text)
- Quick actions / shortcuts row
- Recent activity / feed
- Recommendations / upgrade-prompts (если уместно для продукта)

**2. Структурированная мета — не plain text через точки.** Антипаттерн: «Ubuntu 22.04 · Амстердам · 2 CPU / 4 GB · uptime 12 дней» одной строкой. Правильно — каждое поле отдельным визуальным элементом:
- ОС → иконка дистрибутива + текст
- Регион → флаг-эмодзи + текст
- Specs → chip-badges (CPU / RAM / Disk) с иконками
- Uptime → muted-блок с иконкой clock

В composition map для каждой карточки списка явно расписывать какие поля и в каких визуальных формах (icon-text-row / chip-row / badge / muted-meta).

**3. FAQ / справочные ссылки — не голый текст.** Если на экране есть FAQ, help-links, change-log, learn-more — это **clickable**: ссылка с chevron-right или underline-стилем, либо expandable accordion. В composition map указывать: «FAQ link — text + chevron-right icon» или «FAQ accordion — title click expand».

### Фаза 2.1: Структура файла

Создай (если нет) папку `ds/screens/`. Внутри — файл `<screen-name>.md` (kebab-case от имени экрана: `dashboard.md`, `file-detail.md`).

Структура файла:

```markdown
# Screen: Dashboard

**Wireframe Node ID:** `1:111`
**Final Screen Node ID:** (заполнится после фазы 4)

## Composition

### Header
- Auto Layout: horizontal, space-between, padding 16/24, gap 24
- Background: surface-default
- Содержимое (слева направо):
  - Logo (плейсхолдер 120×32, заменяется руками)
  - NavMenu/Primary, Node ID `1:222`, items: Files / Shared / Recent / Trash
  - Spacer (flex)
  - Avatar/Md, Node ID `1:333` (default state)
  - Dropdown trigger (IconButton/Ghost/Md, Node ID `1:444`)

### Sidebar
- Auto Layout: vertical, gap 8, padding 16
- Background: surface-subtle
- Width: 240
- Содержимое:
  - NavMenu/Vertical, Node ID `1:555`, 6 items
  - Divider (border-default, height 1)
  - Button/Ghost/Md, Node ID `1:666`, label "Upgrade plan"

### Stats Row
- Auto Layout: horizontal, gap 16
- 3 × Card/Default, Node ID `1:777`
  - Каждая Card содержит: Title (text-md), Value (text-2xl), Badge/Success или Badge/Warning
- Текст-плейсхолдеры: "Total files / 1,247 / +12%", "Shared / 89 / +3%", "Storage used / 67% / Warning"

### Files Table
- Auto Layout: vertical, gap 0
- Содержимое:
  - Table header, Node ID `1:888`, columns: Name / Owner / Modified / Size
  - 8 × Table/Row/Default, Node ID `1:999`
  - Pagination/Default, Node ID `1:aaa` снизу

## Edge cases

### Empty state (Files Table)
- Расположение: внутри Files Table, заменяет 8 строк + Pagination
- Card/Default по центру, padding 48
- Text-md "Файлов пока нет", Button/Primary/Md "Загрузить файл"
- Visibility: false по умолчанию (показывается через override)

### Loading skeleton (Files Table)
- 8 × Table/Row/Loading (если в ДС есть; иначе — 8 строк с opacity 0.4 на тексте)
- Visibility: false по умолчанию

## Tokens used
- Цвета: surface-default, surface-subtle, border-default, text-default, text-muted
- Отступы: space-2, space-4, space-6
- Размеры: size-md (тексты)

## Иконки
- Поиск, колокольчик, шестерёнка — плейсхолдеры. Подменить руками после прогона (Lucide / собственный набор).
```

### Фаза 2.2: Апрув

Покажи пользователю готовый md-файл целиком. Жди апрув.

Без «да» дальше не идёшь. Если пользователь правит детали («Sidebar убери», «вместо Card возьми Tile, у нас он есть») — перепиши md, покажи снова, жди апрув.

> Если пользователь начинает уточнять отдельные мелочи (точные цвета, размер шрифта в Stats) — скажи: «это уровень компонентов в ДС, на экране подцепится автоматически. Если хочешь — после прогона поправим инстансом-override». Не давай уйти в детализацию ниже уровня экрана.

---

## Фаза 2.5. Inline вынос в UI-кит (если решено в Phase 1.5)

Если в Phase 1.5 пользователь подтвердил вынос N компонентов — эта фаза происходит **до** Phase 4 (canvas-write финального экрана). Логика — провернуть mini-цикл `grow_ui_kit` внутри текущего прогона, чтобы потом в Phase 4 ставить `createInstance()` от только что созданных мастеров, а не frame-копии.

### Фаза 2.5.1: Бриф каждого нового компонента

Для каждого подтверждённого компонента — короткий бриф (см. формат в `directive_grow_ui_kit.md` Phase 2):

```markdown
### ServerCard

**Назначение:** карточка сервера в списочных видах (Dashboard, Servers list)
**Анатомия:** TopRow (icon-badge + name + status-badge + kebab) → IpRow (ip + copy) → Chips (OS / Region / Specs) → Footer (uptime + details-link)
**Варианты:** Status: running | stopped | deploying | error
**Состояния:** default / hover (на interactive)
**Привязки:** fill `surface-default`, border `border-default`, radius `radius-md`, shadow-sm + shadow-lg-soft. Текст — DS TextStyles.
```

Сохрани в `ds/.tmp/final_screens_extract_<screen>.md`. Покажи пользователю весь пакет одним блоком, жди апрув.

### Фаза 2.5.2: Новые семантические токены (если требуются)

Если бриф какого-либо компонента вводит новый смысловой цвет (например, `surface-activity-income` для зелёного фона activity-row, или `surface-card-elevated` для карточки с тенью и offset) — собери список новых Semantic-токенов одним блоком. Каждый — alias к существующему Primitive:

```
Новые Semantic для расширения foundation:
- surface-card-elevated → surface-default (с эффектом shadow на компоненте)
- text-trend-positive → success-500 (для +X% индикаторов)
- text-trend-negative → error-500
```

Покажи пользователю, дождись апрув. **Прибитые значения в Semantic запрещены — только alias.** Это инвариант (`ds/CONTRACT.md`).

### Фаза 2.5.3: use_figma — создание компонентов и токенов

Один или несколько вызовов `use_figma` (по правилу из `directive_grow_ui_kit.md`: ≤3 компонента на вызов). В каждом:

1. Если есть новые токены — `figma.variables.createVariable()` с alias-привязкой к Primitive
2. Создание ComponentNode через `figma.createComponentFromNode(frame)` для каждого variant
3. `figma.combineAsVariants([...], page)` для ComponentSet
4. Размещение в SectionNode «Components» / на странице Components, по соглашению проекта
5. Все привязки fills / strokes / cornerRadius / itemSpacing / fontSize — через Variables и TextStyles, как в `grow_ui_kit` Phase 3 правилах 1-7

После создания — короткий audit (как `grow_ui_kit` Phase 3.3): нет ли unbound fills, нет ли FRAME-вместо-COMPONENT, все ли тексты с `textStyleId`.

### Фаза 2.5.4: Запись в каталог

Обнови:
- **`ds/components.md`** — новая строка для каждого вынесенного компонента в соответствующей секции (Действия / Ввод / Контейнеры / Навигация / Фидбэк / Данные / Особенные). Поля: имя, тип (ComponentSet / Component), Node ID, матрица (variants × states), Used in (`screens/<name>` для текущего экрана).
- **`ds/foundation.md`** — если добавлены новые Semantic-токены, записать их в соответствующий слой 2 раздел (Поверхности / Текст / Обводки / Состояния) с alias-привязкой.
- **`ds/screens/<name>.md`** — обновить composition map: на местах компонентов, которые мы только что вынесли, заменить «локальная композиция» на «`ServerCard` instance (`<NewID>`)».

После Phase 2.5 — у нас в UI-ките есть N новых ComponentSets с правильными матрицами и токенами, готовых к `createInstance()` в Phase 4.

> Если пользователь в Phase 1.5 решил «оставить локально» — Phase 2.5 пропускается полностью. Composition map просто содержит «domain-композиция, кандидат на вынос при появлении 2-го экрана».

---

## Фаза 3. Pre-canvas check

Перед `use_figma` пройдись по чеклисту:

1. **Все компоненты в composition map существуют в `ds/components.md`?** Если есть призрак — стоп, либо в Phase 1.3 (берём из ДС), либо в Phase 1.5 / 2.5 (выносим новый компонент сейчас), либо в директиву `grow_ui_kit` отдельным прогоном.
2. **Phase 1.4 пройдена (анализ wireframe-достаточности)?** Все вопросы по сырым сущностям / пустым зонам / edge cases / голому тексту получили решение от пользователя?
3. **Phase 1.5 пройдена (повторяющиеся блоки)?** Все 3+ копии получили решение «выносим / оставим локально»? Если выносим — Phase 2.5 завершилась с обновлёнными `ds/components.md` и `ds/foundation.md`?
4. **Auto Layout-параметры внятные?** Если на секции нет gap / padding — додумай дефолты (gap space-4, padding space-4) и покажи пользователю в виде вопроса: «на Stats Row не указан gap, ставлю space-4. Ок?»
5. **Sizing-карта применена?** Все секции должны быть FILL × HUG (или соответствующее по таблице из Phase 4 правила 3). Не FIXED × FIXED по умолчанию.
6. **Иконки прописаны конкретно?** Не «icon placeholder» в map, а «Lucide / chevron-down 12px» или эквивалент. Если хоть одна иконка указана как placeholder — стоп, возвращайся к Phase 0.1.
7. **Shadows запланированы?** Card / Modal / Toast / Dropdown-panel — у каждого должна быть строчка про тень. Если нет — добавить по дефолту из Phase 0.2.
8. **Информативность экрана достаточна?** Dashboard / Overview занят минимум на 60% контентом, мета карточек структурирована (не plain text через `·`), FAQ/help-ссылки имеют визуальный cue.
9. **Edge cases прописаны?** Если в фазе 2 не оказалось ни одного edge case — переспроси: «empty/loading закладываем? Если нет — окей, но в продакшне это придётся доделывать». На «не нужно» — двигайся дальше, на «закладываем» — допиши в md.
10. **fileKey известен?** Если нет — переспроси.

---

## Фаза 4. Canvas — отрисовка

### Фаза 4.1: SectionNode «Screens»

Если в Figma нет SectionNode «Screens» — создай его рядом с SectionNode «Wireframes». Все собранные экраны идут туда.

### Фаза 4.2: Один `use_figma`-вызов

Один вызов на экран. JS делает следующее:

```js
const screensSection = figma.currentPage.findOne(
  n => n.type === "SECTION" && n.name === "Screens"
);
const componentsCatalog = {
  "NavMenu/Primary": "1:222",
  "Avatar/Md": "1:333",
  "IconButton/Ghost/Md": "1:444",
  "NavMenu/Vertical": "1:555",
  "Button/Ghost/Md": "1:666",
  "Card/Default": "1:777",
  "Table/Header": "1:888",
  "Table/Row/Default": "1:999",
  "Pagination/Default": "1:aaa",
  // ...
};

// Шрифты
await figma.loadFontAsync({family: "Inter", style: "Regular"});
await figma.loadFontAsync({family: "Inter", style: "Medium"});

// Главный фрейм экрана
const screen = figma.createFrame();
screen.name = "Screen/Dashboard";
screen.layoutMode = "VERTICAL";
screen.primaryAxisSizingMode = "AUTO";
screen.counterAxisSizingMode = "FIXED";
screen.resize(1440, screen.height);
screen.itemSpacing = 0;
// background через setBoundVariable("fills", surfaceDefault)

// Header
const header = figma.createFrame();
header.name = "Header";
header.layoutMode = "HORIZONTAL";
header.primaryAxisAlignItems = "SPACE_BETWEEN";
// padding 16/24, через Variables (space-4 / space-6)
header.paddingTop = 16; header.paddingBottom = 16;
header.paddingLeft = 24; header.paddingRight = 24;
// addChild instance компонентов из componentsCatalog
const navPrimary = figma.getNodeById(componentsCatalog["NavMenu/Primary"])
  .createInstance();
header.appendChild(navPrimary);
// ... остальные дочерние

screen.appendChild(header);

// Body (sidebar + main)
const body = figma.createFrame();
body.layoutMode = "HORIZONTAL";
// ... sidebar, main с Stats Row + Files Table

// Empty state как отдельный фрагмент рядом, не внутри (агент часто ошибается на вложенных override)
// Лучше: создать как visible:false внутри Files Table сразу

screen.appendChild(body);

// Размещение в SectionNode "Screens"
screensSection.appendChild(screen);
```

**Правила отрисовки:**

1. **Все компоненты — instance, не дубликаты.** Используй `.createInstance()` от ноды по `getNodeById`. Никаких `figma.cloneNode` или ручного копирования геометрии.

2. **Auto Layout на каждой секции и на самом screen.** Без AL раскладка ломается при изменении контента.

3. **Sizing — по таблице FILL / HUG / FIXED.** Это инвариант, нарушение которого пользователь правит руками после прогона:

   | Уровень | Width | Height |
   |---------|-------|--------|
   | Screen (корневой 1440×) | FIXED | HUG (или FIXED для design-canvas-фиксации) |
   | Top-section: Header / Body / PageHeader / Toolbar / Banner | **FILL** | **HUG** (Header может FIXED-height) |
   | Column внутри Body (Form / Sidebar / Summary) | sidebar/summary — FIXED, основной — **FILL grow=1** | **FILL** или HUG |
   | Row (StatsRow, ActionRow, Filters) | **FILL** | HUG |
   | Spacer (`sp`) | **FILL grow=1** | FILL или HUG |
   | Card в horizontal grid | FIXED по сетке или FILL grow=1 для равных | HUG |
   | Button / Badge / Chip / Input | HUG | HUG (или FIXED H) |
   | Modal | FIXED width по дизайну | **HUG** |
   | Иконка | FIXED W×H |

   В коде: после `appendChild` явно ставить `node.layoutSizingHorizontal/Vertical = "FILL"/"HUG"`. **НЕ использовать** `primaryAxisSizingMode = "FIXED"` + `resize(w, h)` как дефолт для секций — это даёт жёсткий каркас, ломается на любых правках.

4. **Цвета фона / текста — через `setBoundVariable` к Semantic.** На уровне screen и крупных секций — обязательно. На уровне instance — наследуется из Component Set, проверяй, что не появился override с прибитым hex.

5. **Размеры (padding / itemSpacing / fontSize) — через Primitive Variables** (`space-*`, `size-*`).

6. **Тени применяются по умолчанию из foundation:**
   - Card-instances в списках / гридах: `shadow-sm` или `shadow-md` через effects-override
   - Modal-фреймы: `shadow-lg`
   - Toast-инстансы: уже встроено в master, проверять
   - Dropdown / Select panels: `shadow-md`
   - Sticky sidebar / summary: `shadow-sm`

7. **Иконки — реальные SVG из выбранной библиотеки (см. Фаза 0.1).** Lucide-style рендерятся так:
   ```js
   const node = figma.createNodeFromSvg(svgString);
   node.resize(size, size);
   for (const v of node.findAll(n => n.type === 'VECTOR')) {
     if (v.strokes && v.strokes.length > 0) bindStroke(v, S["text-muted"]);
   }
   ```
   Placeholder-rectangle оставлять только для: логотипа бренда (заменяется руками), реального изображения, специфичного арта. В composition map указывать имя иконки из библиотеки, не «icon-placeholder».

8. **Главный фрейм называется `Screen/<Name>`.** Слэш — стандарт навигации в Figma. Sub-фреймы — простыми именами секций (`Header`, `Sidebar`, `Main`, `Stats Row`, `Files Table`).

9. **Edge cases — в том же фрейме, через `visible: false`.** Empty state кладётся рядом с основным содержимым в той же секции, флаг видимости ставится false. Чтобы переключить — пользователь руками меняет visible на нужном.

### Фаза 4.3: Проверка после write

1. `get_screenshot` на собранный screen, покажи пользователю.
2. Точечно проверь:
   - На одном instance в правой панели — фиолетовый ромб (instance), не серый квадрат (frame). Если квадрат — где-то агент создал детачнутую копию, пересборка нужного блока.
   - На главном frame `Screen/<Name>` — fill через Variable, не SOLID hex.
   - Auto Layout стоит везде — проверка: попробуй в правой панели «Resize to hug» на секции, если ломается — AL не выставлен.
3. Запиши Final Screen Node ID в md-файл `ds/screens/<name>.md` в строку «Final Screen Node ID».

---

## Фаза 5. Запись в каталог

### Фаза 5.1: Обновление `ds/components.md`

По каждому компоненту, который оказался задействован на экране — добавь / обнови строку `used in:`:

```markdown
### Card

- **Назначение:** контейнер контента
- **Варианты:** type: default | interactive; state: default | hover | selected (на interactive)
- **Node ID:** `1:777`
- **Used in:** screens/dashboard, screens/file-detail
```

Если строки `used in` не было — добавь. Если была и в ней не указан текущий экран — допиши через запятую.

### Фаза 5.2: Композиционный индекс

В `ds/screens/_index.md` (создай если нет) — короткая строка:

```markdown
# Screens index

- `dashboard.md` — главный экран после входа, Files / Stats / Sidebar
- `file-detail.md` — карточка файла с превью и историей версий
- `settings.md` — настройки профиля и команды
```

Это помогает на следующих этапах (аудит, хендофф) быстро находить, какие экраны вообще есть.

---

## Фаза 6. Финальный отчёт

### Single-режим:

```
Экран <ScreenName> собран:
- Final Screen Node ID: 1:bbb
- Использовано компонентов из ДС: 9 (NavMenu/Primary, Avatar/Md, IconButton/Ghost/Md, NavMenu/Vertical, Button/Ghost/Md, Card/Default, Table/Header, Table/Row/Default, Pagination/Default)
- Новые компоненты, вынесенные в UI-кит в этом прогоне (Phase 2.5):
  - ServerCard — ComponentSet 5:101, variants Status (4 значения)
  - StatCard — Component 5:120
  - ActivityRow — ComponentSet 5:135, variants Type (4 значения)
- Новые Semantic-токены, добавленные в Foundation (Phase 2.5.2):
  - text-trend-positive → success-500
  - text-trend-negative → error-500
- Edge cases: empty (visible: false), loading skeleton (visible: false)
- Плейсхолдеры под замену руками: 1 (логотип бренда — Logo placeholder в Header)
- ds/screens/<name>.md создан
- ds/components.md обновлён (новые компоненты + used in)
- ds/foundation.md обновлён (новые Semantic-алиасы)
- ds/screens/_index.md обновлён

Точечная проверка: все компоненты — instance, фон через Variable, иконки реальные SVG из библиотеки, повторяющиеся блоки 3+ копий вынесены в UI-кит.
```

### Bulk-режим:

```
Прогон по wireframes завершён.

Собрано:
- Dashboard — 9 компонентов, 2 edge cases, 1 плейсхолдер
  + 3 новых компонента в UI-кит (ServerCard, StatCard, ActivityRow)
  + 2 новых Semantic-токена (text-trend-positive, text-trend-negative)
- File Detail — 7 компонентов (включая ServerCard из вынесенного), 1 edge case
- Settings — 6 компонентов, 0 edge cases

Пропущено:
- Onboarding — пользователь сказал «соберу позже руками, сложная композиция»

UI-кит вырос на 3 новых компонента, foundation — на 2 новых токена. Всё через alias к Primitive, инвариант ds/CONTRACT.md соблюдён.

ds/screens/_index.md обновлён, ds/components.md обновлён, ds/foundation.md обновлён.
```

---

## Формат результата

В папке проекта после прогона:

```
ds/
  components.md              — у задействованных компонентов добавлено `used in: screens/<name>`
  screens/
    _index.md                — список собранных экранов
    dashboard.md             — composition map одного экрана
    file-detail.md           — ...
```

В Figma:
- SectionNode «Screens» с фреймами `Screen/Dashboard`, `Screen/FileDetail`, ...
- Все компоненты внутри — instance (привязка к Component Set из SectionNode «Foundation» работает)
- Edge cases (empty / loading) лежат внутри секций с `visible: false`
- Плейсхолдеры иконок и логотипов помечены — Rectangle с fill `border-default`

---

## Правила работы

- **Никаких MCP-вызовов до апрува composition map.** Главное правило. Структурную ошибку дешевле поймать в md, чем перерисовывать экран.
- **Один экран за один `use_figma`-вызов.** Даже на bulk — каждый экран это отдельная транзакция. Write-tools плывут, если пытаться в одном вызове собрать два-три экрана.
- **Wireframe — это исходник, не финальный layout.** Phase 1.4 (анализ достаточности) обязательна. Сырые сущности, пустые зоны, отсутствие edge-cases в wireframe — нормально для low-fi. Финальный экран эти пробелы закрывает на этапе брифа, согласовав с пользователем, а не оставляет «как было».
- **3+ копий одного блока = новый компонент в UI-ките.** Phase 1.5 + Phase 2.5 — обязательная связка. Локальные frame-копии повторяющихся блоков — антипаттерн. Если пользователь решил «оставить локально» — composition map помечает это как кандидата на вынос.
- **Новые semantic-токены добавляются как alias к Primitive.** Phase 2.5.2 — никаких прибитых значений в Semantic. Это инвариант `ds/CONTRACT.md`.
- **Все компоненты — instance, не дубликаты.** Если в результате нашёлся frame вместо instance — пересборка соответствующего блока, не «допишу руками».
- **Auto Layout везде, sizing по таблице FILL/HUG/FIXED.** Не использовать FIXED × FIXED как дефолт для секций — это даёт жёсткий каркас, ломается на правках. Top-секции = FILL × HUG. См. таблицу в Phase 4 правило 3.
- **Иконки — реальные SVG из выбранной библиотеки, не placeholder.** При первом запуске — спросить про библиотеку (Phase 0.1). Затем рендерить через `figma.createNodeFromSvg()` сразу в первой итерации, не во второй. Placeholder Rectangle только для логотипа бренда / реального изображения.
- **Shadows из foundation применяются по умолчанию.** Card, Modal, Toast, Dropdown-panel — все получают тень при первом прогоне, не во второй итерации после фидбэка «выглядит плоско».
- **Dashboard / overview не может быть пустым.** Минимум 60% площади занято контентом. Если меньше — composition map неполный, расширить через Phase 1.4.
- **Метаданные структурированы.** Списочные карточки не plain text через `·`, а chips/icons/badges по полям.
- **FAQ / справочные ссылки — visible interactive.** Не голый текст. Chevron / underline / accordion-pattern.
- **Edge cases закладываются сразу.** Empty / loading / overflow — в том же canvas-вызове, как `visible: false` соседи. Не на потом.
- **Прибитых hex быть не должно.** Все цвета — через Variables. Если нашёлся прибитый цвет на screen / секции — пересборка.
- **Главный фрейм через слэш — `Screen/<Name>`.** Это стандарт навигации в Figma. Без слэша — будет один длинный список фреймов, потеряешь структуру.
- **Bulk не пересобирает уже собранные экраны без явного запроса.** Если в SectionNode «Screens» уже есть `Screen/Dashboard` — пропуск, не перерисовка.
- **Структурные правки на экране — через директиву или через md.** Если меняешь раскладку секции руками в Figma и хочешь, чтобы это переехало в composition map — обнови `ds/screens/<name>.md` руками или прогони директиву ещё раз с правкой.
- **Артефакты прогона — комплексные.** За один прогон `final_screens` обновляется: `ds/screens/<name>.md` (composition map), `ds/screens/_index.md`, `ds/components.md` (used-in + новые компоненты из Phase 2.5), `ds/foundation.md` (новые Semantic из Phase 2.5.2 если были). Не оставлять что-то «на потом» — это и есть «локально».
