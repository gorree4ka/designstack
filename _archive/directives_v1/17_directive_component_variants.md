# Директива: Расширение матрицы variants и состояний (component_variants)

## Задача
Дополнить существующий компонент в дизайн-системе недостающими variants, состояниями и/или размерами. На входе — компонент в Figma и его строка в `ds/components.md`. На выходе — расширенный Component Set с матрицей `variants × states × sizes`, где все привязки идут через Semantic Variables, и обновлённые `ds/components.md` (актуальная матрица в строке компонента) и `ds/foundation.md` (новые Semantic-токены под состояния, если они потребовались).

Директива работает в двух режимах:
- **Single** — `component_variants <ComponentName>` для одного конкретного компонента
- **Bulk** — `component_variants` без аргумента: агент проходит по `ds/components.md`, находит компоненты с неполной матрицей и предлагает расширить каждый по очереди

Один компонент = один `use_figma`-вызов в обоих режимах. Bulk просто разбивает работу на серию single-прогонов под капотом.

## Роль
Дизайн-системный архитектор с опытом наращивания матрицы вариантов в существующей ДС. Знает, что write-tools плывут на больших матрицах, поэтому идёт по одному компоненту за прогон. Привычка добавлять новые Semantic-токены через alias к Primitive, не плодить прибитые hex.

> Адаптируй роль под продукт:
> - B2C веб → дизайнер с фокусом на состояния action-элементов (Button, Link), focus-кольца на полях ввода
> - B2B SaaS → дизайнер с фокусом на состояния в сложных формах, таблицах, dropdown'ах; широкий набор размеров под плотность
> - Мобильное приложение → дизайнер с фокусом на тач-состояния (pressed вместо hover), accessibility focus
> - Лендинг → размеры заголовков и кнопок под breakpoints, минимум состояний (default + hover)

---

## Выбор режима

### Single-режим: `component_variants <ComponentName>`

Используется когда:
- Точечно дорабатываешь один компонент, на котором сейчас собираешь экран
- Хочешь полный контроль над брифом (точно знаешь, что добавить)
- Демо или обучение

### Bulk-режим: `component_variants` (без аргумента)

Используется когда:
- ДС большая, нужно одним заходом пройтись по всему UI-киту
- Заранее не помнишь, у каких компонентов матрица неполная
- Готовишь UI-кит к этапу сборки экранов (урок 8)

В bulk агент:
1. Читает `ds/components.md`
2. Считает «неполные» компоненты — у которых нет строки `state:` либо она содержит только `default` и `error`, либо нет строки `size:`, либо variants ≤ 2
3. По каждому такому компоненту запускает короткий бриф в чате: «у Card сейчас 1 variant × 0 состояний. Расширяем? Если да — какие variants/состояния/размеры?»
4. На каждое «да» — отдельный single-прогон со всеми четырьмя фазами
5. На «нет» или «пропустить» — переходит к следующему

В bulk пользователь не теряет контроль над скопом — каждый компонент проходит через явный апрув брифа.

---

## Фаза 1. Read — что уже есть

### Фаза 1.1: Чтение `ds/components.md`

Найди строку компонента. Извлеки:
- Имя
- Node ID
- Текущую матрицу (`type:`, `state:`, `size:`, любые другие variant-оси)

Если строка отсутствует — переспроси: «компонента `<Name>` нет в `ds/components.md`. Это новый компонент? Тогда нужен `grow_ui_kit`, не `component_variants`. Запустить?»

### Фаза 1.2: Чтение компонента в Figma

Через `get_metadata` на Node ID:
- Получи текущий `ComponentSet` (если компонент уже в Set'е) или одиночный `Component`
- Извлеки `componentPropertyDefinitions` — это карта всех текущих variant-осей
- Сверь с тем, что в `ds/components.md` — должно совпадать. Если расхождение, пометь и выведи в чат: «в Figma у Button 3 variants, в `ds/components.md` записано 2. Что считаем правдой?»

Сохрани ответы в локальную переменную `currentMatrix` для использования в фазе 2.

---

## Фаза 2. Brief — что добавляем

Покажи пользователю текущую матрицу одной строкой:

```
Сейчас у <ComponentName>: <currentMatrix>
Например: type: primary | secondary; state: default; size: md
```

Задай три вопроса одним блоком:

```
1. Variants. Что добавить? (например: ghost; или пропускаем)
2. Состояния. Какие добавить? (например: hover, disabled, loading, focus; или пропускаем)
3. Размеры. Какие добавить? (например: sm, md, lg; или пропускаем)
```

Любая из категорий может быть пустой — агент пропускает её. Если все три пустые — закрывай прогон с сообщением «нечего добавлять, выходим».

> Если пользователь пишет неконкретно («все нужные», «по умолчанию») — переспроси. Дефолтов в этой директиве нет: добавление variants и состояний — продуктовое решение, не процедурное.

---

## Фаза 3. md-апдейт

### Фаза 3.1: Расчёт новой матрицы

Сложи `currentMatrix` + `briefAdditions`. Получи `newMatrix`.

Пример:
- было: `type: primary | secondary; state: default; size: md`
- добавили: `type: ghost; state: hover, disabled, loading; size: sm, lg`
- стало: `type: primary | secondary | ghost; state: default | hover | disabled | loading; size: sm | md | lg`

Посчитай размер матрицы — произведение количества значений по каждой оси. В примере: 3 × 4 × 3 = **36 ячеек**.

**Если 25+ ячеек:** предупреди пользователя. «Матрица 36 ячеек — write-tools на пределе, может частично сбоить. Дроблю прогон: первый — добавляем состояния (3 × 4 = 12 ячеек), второй — добавляем sizes к каждой комбинации (расширяем до 36). Подтверждаешь?» Если пользователь подтверждает — переходи в режим двух прогонов: фазы 3-4 повторяются дважды с промежуточным апрувом. Если пользователь говорит «один прогон» — соглашаешься, но за качество не ручаешься.

**Если ≤ 24 ячеек:** один прогон.

### Фаза 3.2: Семантические токены под состояния

Для каждого нового состояния пройдись по правилам:

| Состояние | Что обычно меняется | Какой Semantic нужен |
|-----------|---------------------|---------------------|
| `hover` | Фон action-элемента темнее на ~10-15% | `surface-action-<variant>-hover` |
| `disabled` | Opacity 0.4-0.5 на текущем `surface` (без отдельного Semantic) | — |
| `loading` | Тот же `surface`, контент скрыт под спиннером | — (или `surface-action-<variant>-loading` при специфичной логике) |
| `focus` | Outline 2px по контуру элемента | `border-focus-ring` |
| `selected` | Фон чуть отличается от default | `surface-<variant>-selected` |
| `error` (для Input) | Граница ярко-красная, фон может оставаться | `border-error` (может уже быть) |

Если нужного Semantic в `ds/foundation.md` нет:
- Добавь его в раздел Semantic с привязкой через alias к подходящему Primitive
- Например: `surface-action-primary-hover → accent-700` (если основной `surface-action-primary → accent-500`)
- Все добавления — alias-привязки, не прибитые значения. Это инвариант контракта из урока 5

Покажи пользователю предполагаемые добавления в Foundation:

```
В ds/foundation.md (Semantic) добавляются:
- surface-action-primary-hover → accent-700
- surface-action-secondary-hover → gray-100
- surface-action-ghost-hover → gray-50
- border-focus-ring → accent-500

Подтверждаешь?
```

Без апрува не идёшь дальше.

### Фаза 3.3: Описание новой матрицы

Собери Markdown с тремя секциями:
1. Имена слоёв через слэш для каждой ячейки матрицы (`Button/Primary/Default/Md`, `Button/Primary/Hover/Md` и т.д.)
2. Что меняется на каждом состоянии (текстом по табличке выше)
3. Что меняется на каждом размере (padding, font-size, height — через Primitive `space-*` и `size-*`)

Сохрани в `ds/.tmp/component_variants_<name>.md`. Покажи пользователю. Жди апрув.

---

## Фаза 4. Canvas — отрисовка

### Фаза 4.1: Получение файла и компонента

Если `fileKey` уже сохранён — используй. Иначе переспроси.

`get_metadata` на Node ID компонента — получи актуальный `ComponentSetNode` (или `ComponentNode`, если он одиночный — тогда первым делом промоутишь его в Set, см. ниже).

### Фаза 4.2: Промоут одиночного Component в Set

Если текущий компонент — одиночный `ComponentNode` без variants:
- Создай новый `ComponentSetNode` рядом
- Перенеси текущий компонент в него как первую ячейку с именем по новой схеме (`Button/Primary/Default/Md`)
- Обнови Node ID в `ds/components.md` на новый Set

### Фаза 4.3: Создание недостающих ячеек

Один `use_figma`-вызов. JS делает следующее:

```js
const componentSet = figma.getNodeById("<setNodeId>");

// Загрузка шрифтов (как обычно)
await figma.loadFontAsync({family: "Inter", style: "Regular"});
await figma.loadFontAsync({family: "Inter", style: "Medium"});

// Получение Variables по именам (через коллекцию Semantic)
const semanticCollection = figma.variables.getLocalVariableCollections()
  .find(c => c.name === "Semantic");
const surfaceActionPrimaryHover = figma.variables.getLocalVariables()
  .find(v => v.name === "surface-action-primary-hover" && v.variableCollectionId === semanticCollection.id);
// ... остальные нужные Variables

// Для каждой ячейки newMatrix:
for (const cell of newMatrixCells) {
  // Если ячейка уже существует в Set — пропускаем
  if (componentSet.children.some(c => c.name === cell.name)) continue;

  // Создаём новый Component внутри Set
  const variant = figma.createComponent();
  variant.name = cell.name; // например "Button/Primary/Hover/Md"
  variant.layoutMode = "HORIZONTAL";
  variant.primaryAxisSizingMode = "AUTO";
  variant.counterAxisSizingMode = "AUTO";
  // ... padding, gap из шкалы space-* через setBoundVariable

  // Заливка по матрице состояний
  variant.fills = [{type: "SOLID", color: {r: 0, g: 0, b: 0}}];
  if (cell.state === "hover" && cell.variant === "primary") {
    variant.setBoundVariable("fills", surfaceActionPrimaryHover);
  } else if (cell.state === "disabled") {
    // тот же surface, но opacity
    variant.setBoundVariable("fills", surfaceActionPrimary);
    variant.opacity = 0.4;
  }
  // ... остальные комбинации

  // Контент: текст / иконка / спиннер-плейсхолдер
  // (зависит от компонента, см. фазу 3.3)

  componentSet.appendChild(variant);
}

// componentPropertyDefinitions автоматически обновятся
// после appendChild ячеек с именами через слэш
```

**Правила отрисовки:**

1. **Все fills, strokes, effects — через `setBoundVariable` к Semantic.** Прибитый hex запрещён. Это инвариант.
2. **Размеры (padding, gap, font-size, line-height) — через Primitive Variables.** Не прибитые числа.
3. **Имена ячеек — строго через слэш.** `Button/Primary/Hover/Md`. Любой другой разделитель ломает Component Set.
4. **Auto Layout везде.** Любая ячейка матрицы — Auto Layout, иначе размеры не отработают корректно.
5. **Loading-состояние:** круглый плейсхолдер по центру (rect 12-16-20px по размеру компонента) под спиннер. Анимацию НЕ делать — Smart Animate / interactive components ставятся вручную, через MCP это нестабильно.
6. **Focus-состояние:** outline 2px через `strokes` + `setBoundVariable("strokes", borderFocusRing)`. `strokeAlign = "OUTSIDE"`, чтобы не съедал внутренние размеры.

### Фаза 4.4: Проверка после write

1. `get_screenshot` на ComponentSet, покажи пользователю.
2. Проверь точечно одну ячейку (например, `Button/Primary/Hover/Md`):
   - Открой через `get_metadata` или просто покажи в Figma
   - Убедись, что fill — Variable (`surface-action-primary-hover`), а не SOLID hex
   - Если хоть одна ячейка с прибитым hex — пересобирай эту ячейку через `setBoundVariable`
3. Проверь, что Component Set действительно собрался: в Figma должна быть одна группа с матрицей в правой панели properties, не отдельные компоненты с похожими именами.

---

## Фаза 5. Запись в каталог

### Фаза 5.1: Обновление `ds/components.md`

Найди строку компонента. Замени матрицу на актуальную:

```markdown
### Button
- **Назначение:** основная кнопка действий
- **Варианты:** type: primary | secondary | ghost; state: default | hover | disabled | loading; size: sm | md | lg
- **Node ID:** `1:234`
```

Если в результате прогона добавились новые состояния, в которых нужны были новые Semantic-токены — упомяни в комментарии под строкой:

```markdown
> Расширено в уроке 7: добавлены состояния hover/disabled/loading и размеры sm/md/lg.
> Новые Semantic в Foundation: surface-action-primary-hover, surface-action-secondary-hover, surface-action-ghost-hover, border-focus-ring.
```

### Фаза 5.2: Обновление `ds/foundation.md`

Если в фазе 3.2 пользователь подтвердил добавление Semantic-токенов — впиши их в раздел Semantic. Каждый — отдельной строкой с alias к Primitive:

```markdown
### Поверхности (расширено)
- surface-action-primary-hover → accent-700
- surface-action-secondary-hover → gray-100
- surface-action-ghost-hover → gray-50

### Обводки (расширено)
- border-focus-ring → accent-500
```

Не дублируй существующие токены. Если `border-focus-ring` уже есть — пропускай.

---

## Фаза 6. Финальный отчёт

### Single-режим:

```
Компонент <ComponentName> расширен:
- Матрица: <newMatrix>, <N> ячеек
- Новые Semantic в ds/foundation.md: <список или «не потребовались»>
- ds/components.md обновлён

Точечная проверка прошла, прибитых hex не найдено.
```

### Bulk-режим:

```
Прогон по ds/components.md завершён.

Расширено:
- Button: type × state × size (3 × 4 × 3 = 36 ячеек), +3 Semantic
- Input: state (1 × 5 = 5 ячеек), +1 Semantic
- Card: type × state на interactive (2 × 3 + 1 = 7 ячеек), 0 Semantic

Пропущено:
- Toast — пользователь сказал «достаточно текущей матрицы»
- Tooltip — пользователь пропустил
- Pagination — пользователь пропустил

ds/components.md обновлён по всем расширенным.
ds/foundation.md обновлён, добавлено 4 Semantic-токена.
```

---

## Формат результата

В папке проекта после прогона:

```
ds/
  components.md              — у затронутых компонентов матрица в строке обновлена
  foundation.md              — добавлены Semantic-токены под новые состояния (если потребовались)
  .tmp/
    component_variants_<name>.md  — черновики md-описаний по каждому прогону, можно удалить
```

В Figma:
- У каждого затронутого компонента — расширенный Component Set с матрицей `variants × states × sizes`
- Имена ячеек через слэш, Figma собрала в матрицу автоматически (видно в правой панели properties)
- Все fills, strokes, effects привязаны через `setBoundVariable` к Semantic Variables
- Прибитых hex нет

---

## Правила работы

- **Никаких MCP-вызовов до апрува md-описания и предлагаемых Semantic-токенов.** Главное правило. Структурную ошибку дешевле поймать в md, чем перерисовывать матрицу.
- **Один компонент за один `use_figma`-вызов.** Bulk — это серия single-прогонов под капотом, не пакет в одном вызове. Write-tools плывут на больших матрицах.
- **Прибитые hex запрещены.** Все цвета — через `setBoundVariable` к Semantic. Если в результате нашёлся прибитый hex — пересборка ячейки, не «допишу руками».
- **Имена ячеек строго через слэш.** `Button/Primary/Hover/Md`. Без слэша Figma не собирает Component Set, у тебя останутся отдельные компоненты с похожими именами.
- **Минимум variants на старте.** Если пользователь хочет сразу 5 variants × 5 состояний (25+ ячеек) — предупреди про дробление, предложи разбить на два прогона.
- **Loading без анимации.** Каркас (плашка под спиннер) — да, анимация — нет. MCP на анимации нестабилен.
- **Новые Semantic-токены добавляются как alias.** Никогда — как новое прибитое значение в Semantic. Если подходящего Primitive нет — сначала добавляешь Primitive, потом Semantic с привязкой.
- **Auto Layout везде.** Каждая ячейка матрицы — Auto Layout. Без этого размеры через Variables не работают.
- **Bulk не трогает компоненты, по которым пользователь сказал «нет».** Пропуск — это явное решение, не повод пересмотреть позже без запроса.
- **Структурные правки — в `ds/components.md`, не на канвасе руками.** Если правишь матрицу руками в Figma — обнови строку в каталоге. Иначе следующий прогон директивы откатит ручные правки или пропустит компонент как «уже расширенный».
