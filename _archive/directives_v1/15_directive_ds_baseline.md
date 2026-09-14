# Директива: Стартовая дизайн-система с нуля (ds_baseline)

## Задача
Поставить стартовую дизайн-систему на пустой проект: бриф из пяти вопросов → `ds/foundation.md` с двумя слоями токенов → две коллекции Figma Variables («Primitive» и «Semantic») → SectionNode «Foundation» рядом с Wireframes плюс 5–7 базовых компонентов, ссылающихся на смысловые Variables. Один прогон, один файл, один артефакт на выходе.

## Роль
Дизайн-системный архитектор. 5+ лет в продуктовом дизайне, опыт постановки ДС с нуля. Знает разницу между примитивными, смысловыми и компонентными токенами. Умеет писать Variables через Figma API, не только мышкой в панели.

> Адаптируй роль под продукт:
> - B2C веб → дизайнер с фокусом на конверсию и доверие, шкала отступов под плотные карточки
> - B2B SaaS → дизайнер дашбордов, плотная типографическая шкала, четыре уровня нейтралов
> - Мобильное приложение → дизайнер с фокусом на тач-таргеты (минимум 44pt), мобильная типографическая шкала
> - Лендинг → дизайнер маркетинговых страниц, крупная типографическая шкала, акцентный цвет работает на CTA

## Как устроена директива

Три фазы. Первая — бриф в пять вопросов. Вторая — `ds/foundation.md` с двумя слоями токенов. Третья — два вызова `use_figma`: создание Variables и отрисовка фундамента плюс базовых компонентов в одном Figma-файле, где уже лежат wireframes.

Жёсткое правило: **никаких MCP-вызовов до апрува текста**. Сначала бриф и foundation в md согласованы, только потом Figma.

**Важно про инструмент:** только `use_figma`. Пишем Variables через Figma Plugin API (`figma.variables.createVariableCollection`, `figma.variables.createVariable`) и рисуем фундамент-секцию обычными `createFrame` / `createRectangle` / `createText`.

**Важно про файл:** работаем в том же Figma Design-файле, где лежат wireframes (если они уже стоят) или планируются финальные экраны. Не плодим файлы — ДС живёт рядом с экранами.

---

## Фаза 1. Бриф

Задай пять вопросов одним блоком. Никаких уточнений и философии — короткие ответы.

```
1. Отрасль продукта. Одно слово: финтех / e-com / edtech / SaaS / медиа / госуслуги / другое.
2. Аудитория. b2b / b2c / внутренний продукт.
3. Тон. Два прилагательных через запятую: например «строгий, надёжный» или «дружелюбный, простой».
4. Платформа. web / mobile / web+mobile.
5. Локаль. ru / en / ru+en.
```

Сохрани ответы в `ds/brand-brief.md`. Это якорь решений по тону палитры и типографики на следующих фазах.

> Если пользователь вместо короткого ответа пишет полстраницы — выдели из текста ключевое и переспроси: «зафиксировал X, верно?» Не разворачивай бриф в интервью.

---

## Фаза 2. Foundation в Markdown

Собери `ds/foundation.md` со структурой ниже. Используй привязку к ответам брифа: тон палитры, шкалу типографики, плотность отступов.

**Зашитый минимум** (адаптируется под бриф, но состав фиксирован):
- Палитра: один акцентный цвет (под бриф), 9 нейтралов (00, 50, 100, 200, 300, 500, 700, 900, 950), 4 функциональных (success, warning, error, info)
- Типографика: Inter (или альтернатива из RU-набора при `локаль = ru`), шкала на 9 размеров (xs 12 — 4xl 48), межстрочный +5% при кириллице
- Радиусы: 0, 4, 8, 16
- Отступы: 4, 8, 12, 16, 24, 32, 48, 64
- Тени: 3 уровня (sm, md, lg), мягкие, без бренд-цвета

**Шаблон файла:**

```markdown
# Foundation

**Бриф:** <одной строкой из brand-brief.md>

## Слой 1 — примитивные токены

### Палитра
- accent-500 = #2563EB  ← основной акцент
- accent-100, accent-300, accent-700, accent-900  ← оттенки акцента
- gray-00 ... gray-950  ← 9 нейтралов
- success-500, warning-500, error-500, info-500  ← функциональные

### Типографика
- font-sans = Inter
- size-xs = 12, size-sm = 14, size-base = 16, size-lg = 18, size-xl = 20, size-2xl = 24, size-3xl = 32, size-4xl = 48
- weight-regular = 400, weight-medium = 500, weight-semibold = 600, weight-bold = 700
- line-height-base = 1.5  ← +5% от 1.43 под кириллицу

### Радиусы
- radius-none = 0, radius-sm = 4, radius-md = 8, radius-lg = 16

### Отступы
- space-1 = 4, space-2 = 8, space-3 = 12, space-4 = 16, space-6 = 24, space-8 = 32, space-12 = 48, space-16 = 64

## Слой 2 — смысловые токены

### Поверхности
- surface-default → gray-00
- surface-subtle → gray-50
- surface-action-primary → accent-500
- surface-action-primary-hover → accent-700

### Текст
- text-default → gray-900
- text-muted → gray-500
- text-on-action → gray-00
- text-error → error-500

### Обводки
- border-default → gray-200
- border-strong → gray-300
- border-error → error-500

### Состояния
- bg-success → success-500
- bg-warning → warning-500
- bg-error → error-500
- bg-info → info-500

## Слой 3 — компонентные токены
*На стартовом наборе не нужен. Добавляется отдельной директивой при расширении компонентов вариантами и состояниями (button-padding-y, input-height и т.д.).*
```

Покажи файл пользователю. Дождись апрува. Если бриф изменил что-то существенное (например, локаль `ru+en` → нужен резервный шрифт) — внеси правки и переспроси.

---

## Фаза 3. Перенос в Figma

### Фаза 3.0: Получение файла

> Пришли ссылку на Figma Design-файл, в котором собирается продукт (если есть wireframes — тот же файл). Variables и фундамент-секцию ставим в тот же файл — не плодим проекты.

Извлеки `fileKey` из ссылки.

### Фаза 3.1: Первый вызов `use_figma` — Variables

Один вызов. Создаёт две коллекции и заливает в них значения по `ds/foundation.md`.

```js
// Коллекция 1: Primitive
const primitive = figma.variables.createVariableCollection("Primitive");

// Цвета
const accent500 = figma.variables.createVariable("accent-500", primitive, "COLOR");
accent500.setValueForMode(primitive.defaultModeId, {r: 0.145, g: 0.388, b: 0.922});
// ... остальные цвета по слою 1

// Числовые токены: радиусы, отступы, размеры
const radiusMd = figma.variables.createVariable("radius-md", primitive, "FLOAT");
radiusMd.setValueForMode(primitive.defaultModeId, 8);
// ... остальные числа

// Строковые: имена шрифтов
const fontSans = figma.variables.createVariable("font-sans", primitive, "STRING");
fontSans.setValueForMode(primitive.defaultModeId, "Inter");

// Коллекция 2: Semantic
const semantic = figma.variables.createVariableCollection("Semantic");

const surfaceActionPrimary = figma.variables.createVariable("surface-action-primary", semantic, "COLOR");
surfaceActionPrimary.setValueForMode(
  semantic.defaultModeId,
  {type: "VARIABLE_ALIAS", id: accent500.id}  // ← привязка к примитиву
);
// ... остальные смысловые с привязками
```

**Правила:**
- Variables создаются именно в этом порядке: примитивы → смыслы. Смыслы ссылаются на примитивы через `VARIABLE_ALIAS`. Прибитые значения в смысловой коллекции запрещены — сломается ребрендинг.
- Имена точно как в `ds/foundation.md`. Без переименований по ходу.
- На канвасе ничего не появляется — Variables живут в панели Local Variables.

После вызова попроси пользователя открыть панель Local Variables и убедиться, что обе коллекции на месте, привязки работают (наводишь на значение в Semantic — показывает имя примитива).

### Фаза 3.2: Второй вызов `use_figma` — фундамент и базовые компоненты

Один вызов. Создаёт SectionNode «Foundation» рядом с «Wireframes — low-fi» и наполняет его.

**Структура SectionNode:**

```
Foundation (SectionNode)
├── Palette (FrameNode, Auto Layout)
│   ├── PrimitiveColors (плитки 9 нейтралов + 5 акцент-оттенков + 4 функциональных)
│   └── SemanticColors (плитки smantic-имён, привязанных к примитивам)
├── Typography (FrameNode)
│   └── 9 строк типографической шкалы с подписями: «xs 12», «sm 14» ... «4xl 48»
├── Radii (FrameNode)
│   └── 4 квадрата с разными радиусами
├── Spacing (FrameNode)
│   └── Линейка 8 значений отступов
└── Components (FrameNode, Auto Layout, расположен ниже)
    ├── Button — primary / secondary / ghost (3 варианта)
    ├── Input — default / error
    ├── Card — карточка с заголовком и текстом
    ├── Modal — модалка с шапкой и кнопками
    ├── Navbar — горизонтальная панель навигации
    ├── IconButton — квадратная кнопка под иконку
    └── Badge — статус
```

**Правила отрисовки:**

1. **Компоненты — это настоящие `ComponentNode`, не `FrameNode`.** Это главное. Базовые UI-элементы (Button, Input, Card, Modal, Navbar, IconButton, Badge) создаются через `figma.createComponent()` или `figma.createComponentFromNode(frame)` — должны быть видны в Assets-панели Figma и пригодны для `createInstance()`. Создавать их как обычные `figma.createFrame()` запрещено: тогда это просто фреймы-картинки, на экранах их нельзя переиспользовать как инстансы.

   Варианты — через `figma.combineAsVariants([...components], parent)`. Имена variants до объединения задаются в формате `Property=value`:
   ```js
   const primary   = figma.createComponentFromNode(primaryFrame);   primary.name   = "State=primary";
   const secondary = figma.createComponentFromNode(secondaryFrame); secondary.name = "State=secondary";
   const ghost     = figma.createComponentFromNode(ghostFrame);     ghost.name     = "State=ghost";
   const buttonSet = figma.combineAsVariants([primary, secondary, ghost], page);
   buttonSet.name = "Button";
   ```
   После `combineAsVariants` ComponentSet можно перемещать в Components-row (фрейм-контейнер внутри Foundation).

2. **Типографика — через TextStyles, не прибитые числа в text-узлах.** Создаётся отдельный `TextStyle` на каждую ступень шкалы. `fontSize` стиля привязывается к Primitive Variable, line-height и letter-spacing задаются на самом стиле (PERCENT, не PIXELS — устойчиво при смене размера).
   ```js
   const style = figma.createTextStyle();
   style.name = "DS/Heading/lg";
   style.fontName = {family: "Inter", style: "Medium"};
   style.setBoundVariable("fontSize", P["size-lg"]);
   style.lineHeight = {value: 150, unit: "PERCENT"};
   await text.setTextStyleIdAsync(style.id);
   ```
   Минимальный набор стилей под `foundation.md` слой 1 (sizes × weights): `Heading/4xl`, `Heading/3xl`, `Heading/2xl`, `Heading/xl`, `Heading/lg`, `Body/base`, `Body/sm`, `Body/sm Medium`, `Body/xs`, `Label/xs` (с letter-spacing 5%). Все text-узлы внутри Foundation **и** все text-узлы внутри созданных компонентов должны быть привязаны к одному из этих стилей через `setTextStyleIdAsync`. Прибивать `fontSize` напрямую в text-узлах запрещено.

   **Цвет текста — отдельно.** TextStyle хранит только typography (font, size, line-height, letter-spacing). Цвет применяется через `text.fills` с биндингом к Semantic-переменной (`text-default`, `text-muted`, `text-on-action`, `text-error`, ...).

   **Gotcha: имена стилей со слэшами.** Figma при сохранении имени `"DS / Heading / lg"` иногда нормализует пробелы вокруг `/` (часть стилей становится `"DS/Heading/lg"`, часть остаётся как есть — поведение зависит от рендеринга). При поиске стилей в коде нормализуй: `name.replace(/\s*\/\s*/g, '/')`.

3. **Все заливки и обводки — через Variables.**
   ```js
   const paint = figma.variables.setBoundVariableForPaint(
     {type: "SOLID", color: {r:0,g:0,b:0}}, "color", semVar
   );
   node.fills = [paint];
   ```
   Прибитых hex-значений в компонентах быть не должно. Если поле не поддерживает Variable — используй EffectStyle.

4. **Auto Layout везде.** Любая секция, любой компонент — Auto Layout. Без него UI-кит ломается на расширении.

5. **Радиусы — через Variables.** Биндить надо четыре угла отдельно:
   ```js
   node.setBoundVariable("topLeftRadius",     P["radius-md"]);
   node.setBoundVariable("topRightRadius",    P["radius-md"]);
   node.setBoundVariable("bottomLeftRadius",  P["radius-md"]);
   node.setBoundVariable("bottomRightRadius", P["radius-md"]);
   ```

6. **Имена компонентов — латиницей по смыслу:** `Button`, `Input`, `Card`, `Modal`, `Navbar`, `IconButton`, `Badge`. Имена variants — `State=primary` / `State=secondary` или `Variant=success` / `Variant=error`. Это даёт правильную property-схему в Properties-панели после `combineAsVariants`.

7. **Раскладка в SectionNode:** Foundation-блоки сверху (Palette, Typography, Radii, Spacing — горизонтально), компоненты ниже в одном Components-фрейме с `layoutWrap = "WRAP"` (плитка переносится автоматически). Между блоками — `itemSpacing = 32`.

8. **Цвет фона SectionNode:** `surface-subtle` через привязку — чтобы белые карточки компонентов читались.

9. **Проверка по факту, не по интенту.** После создания обязательно `findOne(n => n.type === 'COMPONENT_SET' && n.name === 'Button')` — если возвращает null или type='FRAME', значит компонент не создан, фикси перед тем как идти к компонентному токену. Аналогично для TextStyles: `getLocalTextStylesAsync()` должен вернуть N стилей с префиксом `DS/`. Для applied стилей — `text.textStyleId` должен быть непустым на каждом узле внутри Foundation.

10. **Никакого `throw` в конце мутирующего вызова.** `use_figma` исполняет каждый вызов как транзакцию: `throw` в конце откатывает **все** мутации того же вызова (`createComponent`, `setBoundVariable`, `setTextStyleIdAsync` — всё). Хочется отчёта — делай два вызова: первый мутирует (заканчивается естественно), второй читает результат и кидает throw с метрикой. Альтернатива — клади статус в `node.name` или `setSharedPluginData`. Симптом нарушения: «лог говорит applied=N, в файле visually ничего не изменилось».

### Фаза 3.3: Проверка после write

После каждого мутирующего вызова `use_figma` — **отдельным** вызовом (read-only):
1. `findOne` на ключевые узлы (ComponentSet `Button`, ComponentSet `Input`, и т.д.) — все должны возвращаться с правильным type и name.
2. `getLocalTextStylesAsync()` — N стилей с префиксом `DS/`. Если меньше — значит `createTextStyle` откатился (см. правило 10 выше).
3. Пройдись по всем text-узлам внутри Foundation: у каждого `t.textStyleId` должен быть непустым. Если есть пустые — `setTextStyleIdAsync` откатился.
4. `get_screenshot` на созданной структуре, покажи пользователю.
5. Проверь визуально, что в компонентах не осталось прибитых цветов: открой один Button в Inspect-панели, fill должен быть `Variable`, не `SOLID hex`.
6. Проверь, что переключение значения акцентного цвета в коллекции Semantic перекрашивает все компоненты на канвасе. Если нет — какой-то fill не привязан, нужна доводка.

### Фаза 3.4: Краткий показ

```
Стартовая ДС в Figma поставлена:
- Variables: Primitive (N токенов) + Semantic (M токенов с привязками)
- SectionNode «Foundation» — палитра, типографика, радиусы, отступы
- 7 базовых компонентов: Button, Input, Card, Modal, Navbar, IconButton, Badge
- Все fills и обводки привязаны к Semantic.
```

Не закрываемся здесь. Без следующей фазы ДС остаётся декорацией: при сборке экранов агент не обязан её использовать.

---

## Фаза 4. Контракт ДС в проекте

Цель — закрепить правила работы с ДС на весь дальнейший модуль. После этой фазы при любой команде вида «собери экран X», «добавь форму», «дорисуй карточку» агент опирается на эти правила и не отступает от них без явного «забудь про ДС».

### Фаза 4.1: Создать `ds/CONTRACT.md`

Один файл с правилами проекта. Содержимое:

```markdown
# DS Contract — правила работы с дизайн-системой в этом проекте

**Источник ДС:** ds_baseline (стартовая, поставлена с нуля)
**Figma-файл:** <ссылка на тот же файл, где wireframes>
**Дата постановки:** <ISO-дата>

## Главное правило

При любом задании, которое касается интерфейса (новый экран, новая форма, новая карточка, доработка существующего), агент работает строго через эту ДС. Новые экраны = композиция из существующих компонентов плюс существующих токенов. Прибитые цвета, размеры, радиусы и шрифты в обход Variables запрещены.

## Что значит «через ДС»

1. **Компоненты — только из UI-кита.** При сборке экрана агент берёт инстансы компонентов из SectionNode «Foundation» (на старте — Button, Input, Card, Modal, Navbar, IconButton, Badge). Не рисует новые с нуля под конкретный экран.
2. **Цвета — только через Semantic Variables.** Никаких `fills = SOLID #2563EB`. Только `setBoundVariable("fills", surface-action-primary)`. Если в коде получился прибитый hex — это баг, переделывается через Variable.
3. **Типографика — через Variables и стили.** Размеры, межстрочный, веса — из коллекции Primitive. Семейство шрифта — `font-sans` из Primitive.
4. **Радиусы и отступы — через Variables.** `cornerRadius` и `itemSpacing` через `setBoundVariable`, не прибитые числа.
5. **Auto Layout везде.** Любая секция экрана — Auto Layout, иначе при правке контента поедет.

## Что делать, если нужного нет

**Нет компонента под задачу** (например, понадобился Tooltip, а его в стартовом наборе нет):
1. Сначала добавить компонент в SectionNode «Foundation» по тем же правилам, что и базовые: имя латиницей, fills через Semantic, Auto Layout.
2. Записать строчкой в `ds/components.md` (если файла нет — создать): имя, назначение одной строкой, варианты, Node ID.
3. Только после этого использовать компонент на экране.

**Нет смыслового токена под задачу** (например, нужен `surface-warning-subtle`, а в Semantic его нет):
1. Добавить новый Variable в коллекцию Semantic с привязкой к существующему примитиву.
2. Если подходящего примитива нет — добавить и его в Primitive.
3. Записать в `ds/foundation.md` в соответствующий слой.
4. Только после этого использовать на экране.

**Нет паттерна композиции** (например, нужна типовая «карточка с заголовком, картинкой, телом и кнопками», а её формализованной нет):
1. Завести `ds/patterns.md` (если файла нет).
2. Описать паттерн: имя, из каких компонентов и токенов собирается, опционально — Node ID примера в Figma.
3. Использовать как референс при сборке экранов.

## Синхронизация Figma ↔ ds/*.md

`ds/foundation.md` и `ds/components.md` — индекс, по которому агент работает. Расхождение между индексом и Figma ломает следующие сборки.

- Правишь Variables или компоненты руками в Figma → сразу обновляешь соответствующий md-файл.
- Правишь md-файл и хочешь, чтобы это отразилось в Figma → перезапускаешь соответствующую фазу директивы (`ds_baseline` для фундамента и базовых компонентов, отдельная директива для расширения UI-кита).
- Не редактируешь Variables на канвасе руками без обновления `ds/foundation.md`. Иначе следующий прогон директивы откатит правки.

## Что запрещено

- Прибитые цвета (`fill = SOLID hex`) в новых компонентах или экранах.
- Прибитые размеры шрифта, line-height, радиусы, отступы — везде, где есть подходящий Variable.
- Создание нового компонента «на лету» в составе экрана, если его можно вынести в UI-кит.
- Перезапись существующих Variables новыми значениями без согласования (это ребрендинг, отдельный процесс).
- Параллельный второй проект с собственной ДС в этой же папке.

## Когда правила можно нарушить

Только при явной команде пользователя «здесь без ДС, ad-hoc» (например, для одноразового рендера для презентации). Тогда отдельный фрейм вне SectionNode, явно помеченный «ad-hoc, не часть продукта».
```

### Фаза 4.2: Указатель в корневом `CLAUDE.md` проекта

Проверь, есть ли в корне проекта `CLAUDE.md`. Если есть — добавь в конец блок-указатель. Если нет — создай минимальный с этим блоком.

**Блок к добавлению:**

```markdown
## Дизайн-система

В проекте поставлена дизайн-система. Все правила работы с интерфейсом — в `ds/CONTRACT.md`. При любых задачах, связанных с дизайном экранов, форм, компонентов:

1. Прочитай `ds/CONTRACT.md` целиком.
2. Прочитай `ds/foundation.md` и `ds/components.md` для текущего состояния токенов и UI-кита.
3. Действуй строго по правилам контракта.
```

Это даёт автоматическое поведение: любая будущая сессия Claude Code в этой папке начинается с прочтения `CLAUDE.md` → видит указатель → читает `CONTRACT.md` → работает по правилам.

### Фаза 4.3: Финальный отчёт

```
ДС поставлена и закреплена контрактом.

Артефакты в проекте:
  ds/brand-brief.md     — бриф
  ds/foundation.md      — токены (два слоя)
  ds/components.md      — каталог 7 базовых компонентов
  ds/CONTRACT.md        — правила работы с ДС в этом проекте
  CLAUDE.md             — указатель на контракт (создан или дополнен)

В Figma:
  Две коллекции Variables (Primitive, Semantic) с привязками
  SectionNode «Foundation» рядом с «Wireframes — low-fi»
  7 базовых компонентов с привязками к Semantic

Дальше любая команда «собери экран», «добавь форму» автоматически уходит на компоненты UI-кита и Variables. Если чего-то не хватает — сначала добавляется в ДС, потом используется на экране.

Расширение UI-кита (Table, Tabs, Tooltip, Dropdown), варианты и состояния (hover, disabled, loading) — отдельные директивы поверх этой.
```

---

## Формат результата

В папке проекта после прогона:

```
ds/
  brand-brief.md         — пять ответов брифа
  foundation.md          — два слоя токенов с разложенной структурой
  components.md          — каталог 7 базовых компонентов с Node ID
  CONTRACT.md            — правила работы с ДС
CLAUDE.md                — создан или дополнен указателем на CONTRACT
```

В Figma Design-файле:
- Две коллекции в Local Variables: Primitive, Semantic
- SectionNode «Foundation» рядом с «Wireframes — low-fi»
- Внутри Foundation: блоки Palette, Typography, Radii, Spacing + 7 базовых компонентов

---

## Правила работы

- **Никаких MCP-вызовов до апрува foundation.md.** Главное правило. Текстовые правки бесплатны, перезапуск отрисовки — два вызова `use_figma` и время.
- **Без фазы 4 директива не считается завершённой.** Без контракта ДС остаётся декорацией, агент при следующих задачах не обязан её использовать. Контракт — обязательная часть, не опция.
- **Variables всегда. Прибитые цвета — никогда.** Если в спешке сделал `fill = SOLID hex` — переделай через `setBoundVariable`. Иначе ребрендинг ломает всю ДС.
- **Смысловой слой ссылается на примитивный.** Прибитые значения в Semantic запрещены. Это инвариант.
- **Один Figma-файл на проект.** Wireframes, фундамент, базовые компоненты, дальше UI-кит и финальные экраны — всё в одном файле. Не плодить проекты.
- **Имена точно по `ds/foundation.md`.** Если в md написано `surface-action-primary` — в Figma строго `surface-action-primary`. Никаких `surface_action_primary` или `surfaceActionPrimary`.
- **Auto Layout везде.** Любая секция, любой компонент. Без исключений.
- **Кириллица, если локаль ru или ru+en.** Шрифт с поддержкой Щ/Ъ/Ь/Ы (Inter, IBM Plex Sans, Roboto, PT Root UI, Onest, Manrope, Ubuntu). Межстрочный +3-5% от базового. На крупных заголовках межбуквенный минус 0.5-1%.
- **Структурные правки — в `ds/foundation.md`, не на канвасе.** Если правишь Variables или компоненты руками в Figma — следующий прогон директивы откатит правки.
