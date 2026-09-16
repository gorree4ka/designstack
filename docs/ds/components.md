# Библиотека паттернов DesignStack

Версия 1 от 12.09.2026 — этап 11, фаза 2. Входы: `docs/ds/foundation.md` (D51), `docs/brand/brand-direction.md` (D50), карточки `docs/ia/wireframes/` (D40–D46), инвентарь (D53), слово «грейд» (D54), логотипы (D55).

Каталог — источник для кода темы: паттерна без записи здесь не заводится, правка идёт сначала в каталог, потом в файл. Этап 12 повторяет разметку в `render.php` (раздел «Контракт разметки»), этап 13 собирает страницы только из этих паттернов.

**Статус:** утверждено. Состав, тексты и токены — в чате 12.09.2026 (D56, D57); внешний вид — отметками на листе 12.09.2026 (D58, D49). Паттерны собраны, витрина — http://localhost:8080/styleguide/ .

## Как читать запись

- **Назначение** — зачем паттерн и где его место.
- **Анатомия** — части сверху вниз.
- **Варианты** и **Состояния** — оси матрицы, **Матрица** — число ячеек на витрине. Больше 24 — паттерн показывается по частям.
- **Отступы** и **Токены** — только из `theme.json`: цвет `--wp--preset--color--*`, кегль `--wp--preset--font-size--*`, отступ `--wp--preset--spacing--*`, остальное `--wp--custom--*`. Имена ниже — как в `foundation.md`: `space-4`, `radius-md`, `size-control-md`.
- **Реализация** — файлы и механизм. **Классы** — разметка, которую повторяют этапы 12 и 13.
- **Тексты** — только слова из `docs/VOICE.md`; новые перечислены в разделе «Слова для словаря».
- **Где стоит** — по вайрфреймам; поле **Used in** заполняет этап 13.
- **Status** — planned → built (код есть, виден на витрине) → verified (лист отмечен ✔).

## Правила библиотеки

1. **Классы.** Блок — `ds-<паттерн>`, часть — `ds-<паттерн>__<часть>`, вариант — `ds-<паттерн>--<вариант>`, состояние — `is-<состояние>`. Классы серого прототипа (`resource-card`, `card-name`) в паттернах не используются: `assets/css/greybox.css` живёт до этапа 13 и уходит вместе с шаблонами-заглушками (D52).
2. **Состояния — селекторами, а не копиями разметки:** `:hover`, `:focus-visible`, `:active`, `[aria-current="page"]`, `[aria-pressed="true"]`, `[aria-expanded="true"]`, `[aria-invalid="true"]`, `[disabled]`, `[aria-busy="true"]`. Для витрины у каждого правила есть двойник-класс: `.ds-button:hover, .ds-button.is-hover { … }`.
3. **Только токены.** Hex, `rgb()`, px вне `@media`, имена шрифтов — баг; примитивы `--wp--custom--color--*` в `patterns.css` запрещены. Проверка — `python scripts/check_tokens.py`.
4. **Брейкпоинты — три:** `@media (min-width: 600px|900px|1200px)`. Другой порог — повод перестроить паттерн, а не завести четвёртый брейкпоинт; ширина своего контейнера — через `@container`.
5. **Переходы** — `color, background-color, border-color, box-shadow` за `duration-fast` с `ease-standard`, без сдвига и масштаба. Блок `@media (prefers-reduced-motion: reduce)` отключает переходы и анимацию.
6. **Фокус** — кольцо 2 px `border-focus-ring` с отступом 2 px, не убирается никогда. У карточки с растянутой ссылкой кольцо показывается на всей карточке (`:has(:focus-visible)`).
7. **Недоступно и отправка.** `disabled` — прозрачность 0,5 и курсор `not-allowed`. Отправка — `aria-busy="true"` и `aria-disabled="true"`: фон не бледнеет, меняется только подпись («Отправляем…»), потому что кнопка остаётся видимой и озвучивается чтецом.
8. **Кликабельное отличается формой** (D50): кнопка — рамка или заливка, ссылка — подчёркивание, карточка — рамка и её потемнение при наведении. У метки, вердикта, мета-строки и тегов нет ни рамки, ни подчёркивания, ни курсора-руки. Проверка — переключатель «Подсветить кликабельное» на витрине.
9. **Одна залитая кнопка на экран** (D50): «Применить» в фильтрах, «Перейти на сайт» на странице ресурса, «Предложить ресурс» в форме, «Сбросить фильтры» в пустой выдаче, «Найти» на главной. Остальные — контурные, в том числе «Подписаться» и кнопка в карточке.
10. **Статус — иконка и слово, цвет третий канал.** Тонированный фон бывает только у состояния записи.
11. **Компонент в списках разной ширины перестраивается по своему контейнеру** — `container-type: inline-size`; порог называется вместе с тем, что он меряет (`.claude/rules/wp-theme.md` §7).
12. **Отступы внутри паттерна задаёт сам паттерн:** глобальный `blockGap` остаётся 0 до этапа 13 (D52), поэтому у групп внутри паттернов `style.spacing.blockGap` выставляется пресетом.
13. **Тексты** — `esc_html__()` с text-domain `designstack`, слова из `docs/VOICE.md`, примеры данных — из placeholder карточек вайрфреймов (Figma, Penpot, «Проверено 3 сен 2026»), не lorem.
14. **Тёмная тема** — паттерн о ней не знает: цвета только семантические, тень — пресет `shadow-md`. На витрине каждый паттерн виден в обеих темах.

## Нужные токены — мини-цикл 10

Размеров компонентов в токенах нет: в сером прототипе они стояли в px (D52). Предлагаю семейство `size` в `settings.custom` — строка в `foundation.md`, значения в `theme.json`, сверка в `check_tokens.py`. Значения — утверждённая геометрия этапа 08 и правила D50, новых цветов, кеглей, отступов и радиусов не появляется.

| Токен | Значение | Где | Откуда значение |
|---|---|---|---|
| `size-control-sm` | 32px | чипсы, кнопка-иконка в шапке, малая кнопка в карточке | grey-box: чипсы и кнопки шапки 32 |
| `size-control-md` | 40px | кнопка, поле поиска в шапке, «Применить», номер страницы | grey-box 36 → шаг 8 |
| `size-control-lg` | 48px | поле и кнопка поиска на главной, поля и кнопка формы, «Перейти на сайт» | grey-box 44–48 |
| `size-icon-sm` | 16px | иконка в метке, ссылке, малой кнопке | D50 §7 |
| `size-icon-md` | 20px | иконка в кнопке, шапке, уведомлении; флажок | D50 §7 |
| `size-tile-sm` | 40px | плитка логотипа в карточке, аватар куратора | D50 §8, D55 |
| `size-tile-lg` | 64px | плитка логотипа на странице ресурса | `resource.md` |
| `size-header` | 64px | высота шапки | `tools.md` |
| `size-sidebar` | 280px | колонка фильтров, колонки подвала | `tools.md`, D41 |
| `size-form` | 640px | колонка формы | `suggest.md` (s1) |
| `size-search-header` | 240px | поле поиска в шапке от 1200 | `tools.md` |
| `size-search-home` | 560px | поле поиска на главной от 900 | `home.md` |
| `size-illustration` | 160px | ширина иллюстрации пустого состояния (высота 112 по пропорции) | D50 §8 |
| `size-measure` | 70ch | колонка текста | D50 §6 |
| `size-measure-lead` | 62ch | вводная строка крупным кеглем | grey-box |

Переменные: `--wp--custom--size--control-md` и так далее.

## Действия

### button

- **Назначение:** действие на странице — применить, отправить, открыть панель, уйти на сайт ресурса. Переход внутри сайта оформляется ссылкой; исключения по вайрфреймам — «Показать аналог» и «Вернуться в каталог».
- **Анатомия:** заливка или рамка → иконка слева (необязательно) → подпись → иконка справа (`external-link` у перехода в новую вкладку).
- **Варианты:** `primary` — заливка `surface-action-primary`, одна на экран; `secondary` — контур `border-strong`, текст `text-action`; `icon` — квадрат с контуром и иконкой, подпись только для чтеца. Размеры: `sm` (`size-control-sm`, кегль `sm`), `md` (`size-control-md`, кегль `base`), `lg` (`size-control-lg`, кегль `base`).
- **Состояния:** default | hover | focus-visible | active | disabled | отправка (`aria-busy`, подпись «Отправляем…»). У `icon` ещё нажато (`aria-pressed`) и раскрыто (`aria-expanded`).
- **Матрица:** 3 варианта × 6 состояний + 3 размера = 21.
- **Отступы:** высота — `size-control-*`; поля по горизонтали `space-3` (sm), `space-4` (md), `space-6` (lg); зазор иконки и подписи `space-2`; у `icon` полей нет, сторона равна высоте.
- **Токены:** surface-action-primary, surface-action-primary-hover, text-on-action, surface-raised, border-strong, text-action, border-focus-ring; radius-sm; font-size sm/base, вес 600, line-height-snug; size-control-*, size-icon-sm/md; duration-fast, ease-standard.
- **Реализация:** `core/button` — primary в `theme.json` (уже есть), `register_block_style( 'core/button', 'secondary' )`; размер — класс `ds-button--sm`; кнопки вне блоков (шапка, панель фильтров) — `<button>` с теми же классами. Файл `patterns/button.php` (`Inserter: no`).
- **Классы:** `.ds-button`, `.ds-button--primary|secondary|icon`, `.ds-button--sm|lg`, `.ds-button__icon`, `.ds-button__label`.
- **Тексты:** «Применить», «Сбросить фильтры», «Перейти на сайт», «Показать аналог», «Найти», «Подписаться», «Предложить ресурс», «Отправляем…», «Вернуться в каталог», «Фильтры», «Меню», «Поиск», «Закрыть», «Тёмная тема»; скрытая подпись «откроется в новой вкладке».
- **Где стоит:** все страницы. **Наведение на контурную кнопку — вопрос листа (V2).** **Used in:** screens/home, screens/tools, screens/topic, screens/resource
- **Status:** verified

### link

- **Назначение:** переход внутри сайта и наружу.
- **Анатомия:** подпись с подчёркиванием → иконка `chevron-right` 16 у отдельной ссылки, `external-link` 16 и скрытая подпись у внешней.
- **Варианты:** `inline` — в тексте; `standalone` — отдельной строкой с шевроном; `external` — наружу, в новой вкладке.
- **Состояния:** default | hover (`text-link-hover`) | focus-visible | active. Посещённая ссылка не отличается: токена нет, а карточки ведут на наши же страницы.
- **Матрица:** 3 × 4 = 12.
- **Отступы:** зазор подписи и иконки `space-1`; подчёркивание толщиной `border-width-hairline` с отступом 0,2em.
- **Токены:** text-link, text-link-hover, border-focus-ring; size-icon-sm; border-width-hairline.
- **Реализация:** `styles.elements.link` в `theme.json` (уже есть), классы для отдельной и внешней; `patterns/link.php` (`Inserter: no`).
- **Классы:** `.ds-link`, `.ds-link--standalone`, `.ds-link--external`, `.ds-link__icon`, `.screen-reader-text`.
- **Тексты:** «Все подборки», «Все выпуски», «Предыдущий выпуск», «Следующий выпуск», «Предложить ресурс», «Обзоры», «Принципы оценки», «Политика данных»; «откроется в новой вкладке».
- **Где стоит:** все страницы. **Used in:** screens/home, screens/tools, screens/topic, screens/resource
- **Status:** verified

### theme-toggle

- **Назначение:** переключить светлую и тёмную тему (US-45); выбор хранится в `localStorage` (этап 10).
- **Анатомия:** кнопка-иконка `md` → иконка → подпись «Тёмная тема» для чтеца; состояние сообщает `aria-pressed`.
- **Варианты:** —
- **Состояния:** светлая (`aria-pressed="false"`) | тёмная (`true`) | hover | focus-visible.
- **Матрица:** 2 × 3 = 6.
- **Отступы:** как у `button--icon` md.
- **Токены:** surface-raised, border-strong, text-action, surface-selected и border-focus-ring у нажатой; size-control-md, size-icon-md.
- **Реализация:** разметка в `parts/header.html`, поведение — `assets/js/theme-toggle.js` этапа 10 без изменений; `patterns/theme-toggle.php` (`Inserter: no`).
- **Классы:** `.ds-theme-toggle`, `.ds-theme-toggle__moon`, `.ds-theme-toggle__sun` (видна та иконка, что отвечает текущей теме) плюс классы кнопки-иконки.
- **Тексты:** «Тёмная тема».
- **Где стоит:** шапка всех страниц. **Иконка — вопрос листа (V6).** **Used in:** screens/tools, screens/topic, screens/resource
- **Status:** verified

## Ввод

### search-form

- **Назначение:** поиск по каталогу из шапки, с главной и со страницы поиска (US-22, US-24; адрес `/search/?s=`, D36).
- **Анатомия:** поле с подсказкой «Поиск по каталогу» и скрытой подписью → кнопка «Найти».
- **Варианты:** `header` — поле `size-search-header`, высота md, кнопка secondary, от 1200; `header-collapsed` — кнопка-иконка «Поиск» на 900–1199 и в меню до 900, раскрывает поле на всю ширину шапки; `home` — поле до `size-search-home`, высота lg, кнопка primary; `results` — на странице поиска, поле с запросом.
- **Состояния:** default | focus-visible | заполнено | раскрыто (у `header-collapsed`).
- **Матрица:** 4 варианта × 3 состояния + раскрыто = 13.
- **Отступы:** зазор поля и кнопки `space-2`; поля поля `space-3`.
- **Токены:** surface-raised, border-strong, text-default, text-muted, border-focus-ring; radius-sm; size-control-md/lg, size-search-header, size-search-home, size-icon-md.
- **Реализация:** блок `core/search`; раскрытие без JS — `<details>` или popover, выбор пробой фазы 3; `patterns/search-form.php`.
- **Классы:** `.ds-search`, `.ds-search--header|home|results`, `.ds-search__field`, `.ds-search__button`, `.ds-search__toggle`.
- **Тексты:** «Поиск по каталогу», «Найти», «Поиск».
- **Где стоит:** шапка (кроме главной, D43), первый экран главной, страница поиска. **Used in:** screens/search, screens/not-found, screens/home, screens/tools, screens/topic, screens/resource
- **Status:** verified

### form-field

- **Назначение:** поле формы «Предложить ресурс» и флажок — в форме и в панели фильтров.
- **Анатомия:** подпись → пометка «необязательно» → поле → подсказка под полем → сообщение об ошибке с иконкой `circle-x`. Флажок: квадрат 20 → подпись справа → ошибка ниже.
- **Варианты:** `text` (адрес, название, почта), `textarea` (комментарий: 5 строк, растёт до 12, дальше прокрутка), `checkbox` (согласие, значение фильтра).
- **Состояния:** default | focus-visible | заполнено | ошибка (`aria-invalid="true"`, `aria-describedby`) | отмечен (флажок).
- **Матрица:** 4 + 4 + 5 = 13.
- **Отступы:** зазор подписи, поля, подсказки и ошибки `space-2`; поля поля `space-3`; между полями формы `space-6`; строка значения фильтра — высота `size-control-sm`.
- **Токены:** surface-raised, border-strong, border-error, text-error, icon-error, text-default, text-muted, border-focus-ring, surface-action-primary (`accent-color` флажка); radius-sm, radius-xs; size-control-lg, size-icon-sm/md; font-size base и sm, подпись — вес 600.
- **Реализация:** статичная разметка в `patterns/form-field.php` (`Inserter: no`) — эталон для блока формы и блока фильтров этапа 12. Блоков полей в ядре нет, поэтому это исключение из правила «структура блоками».
- **Классы:** `.ds-field`, `.ds-field--textarea|checkbox`, `.ds-field__label`, `.ds-field__optional`, `.ds-field__control`, `.ds-field__hint`, `.ds-field__error`, `.is-error`.
- **Тексты:** «Адрес ресурса», «Название», «Комментарий», «Почта», «необязательно», «https://», «Чем ресурс полезен и кому подойдёт», «Напишем, взяли ресурс в каталог или нет», «Соглашаюсь с политикой данных», тексты ошибок из `suggest.md`.
- **Где стоит:** форма, панель фильтров. **Вид поля с ошибкой — вопрос листа (V4).** **Used in:** screens/suggest
- **Status:** verified

### error-summary

- **Назначение:** сводка ошибок над формой; после отправки с ошибками на неё уходит фокус (s3).
- **Анатомия:** рамка `border-error` на `surface-raised` → иконка `circle-x` и заголовок «Проверь форму» → список ошибок ссылками на поля.
- **Варианты:** —
- **Состояния:** одна ошибка | три ошибки | получила фокус (`tabindex="-1"`).
- **Матрица:** 3.
- **Отступы:** поля `space-4`; зазор частей `space-2`; отступ списка `space-4`.
- **Токены:** surface-raised, border-error, icon-error, text-default, text-link, text-link-hover; radius-md; font-size lg и base; size-icon-md.
- **Реализация:** `patterns/error-summary.php` (`Inserter: no`).
- **Классы:** `.ds-error-summary`, `.ds-error-summary__title`, `.ds-error-summary__list`.
- **Тексты:** «Проверь форму» и тексты ошибок полей.
- **Где стоит:** форма «Предложить ресурс». **Used in:** screens/suggest
- **Status:** verified

### suggest-form

- **Назначение:** форма «Предложить ресурс» целиком, во всех состояниях (US-42, D46) — эталон для блока формы этапа 12 и третья песочница витрины.
- **Анатомия:** сводка ошибок или уведомление → «Адрес ресурса» → «Название» → «Комментарий» → «Почта» → согласие → поле-ловушка → кнопка «Предложить ресурс» (primary lg).
- **Варианты:** —
- **Состояния:** по умолчанию | ошибки полей | отправка | сбой отправки | лимит | «уже есть в каталоге». Успех — переход на `/suggest/thanks/` (D33), это страница, а не состояние.
- **Матрица:** 6.
- **Отступы:** колонка до `size-form` по левому краю; между полями `space-6`; до 600 кнопка на всю ширину.
- **Токены:** из `form-field`, `error-summary`, `notice`, `button`.
- **Реализация:** `patterns/suggest-form.php` (`Inserter: no`); поле-ловушка — вне экрана, `tabindex="-1"`, `aria-hidden="true"`. Логика отправки — этап 12 и 14.
- **Классы:** `.ds-suggest-form`, `.ds-fields` (колонка полей шириной `size-form`), `.ds-suggest-form__trap`, `.ds-suggest-form__submit`.
- **Тексты:** раздел «Состояния формы» в `docs/ia/wireframes/suggest.md`.
- **Где стоит:** `/suggest/`. **Used in:** screens/suggest
- **Status:** verified

### filter-panel

- **Назначение:** фильтры раздела каталога (US-16–US-18): колонка слева от 900, панель снизу до 900.
- **Анатомия:** заголовок «Фильтры» и кнопка «Закрыть» (только в панели снизу) → группы `fieldset` с заголовком и флажками → «Применить»; в панели снизу внизу закреплены «Применить» и «Сбросить фильтры».
- **Варианты:** `sidebar` — колонка `size-sidebar`, лист с рамкой; `sheet` — панель снизу на всю ширину с тенью `shadow-md` и `z-modal`. Наборы групп: инструменты (Тема · Цена · Доступ из РФ · Оплата из РФ · Платформа · Грейд), учёба (Формат · Грейд · Язык · Цена), ассеты (Лицензия · Формат файла · Кириллица), сообщества (Платформа · Есть вакансии).
- **Состояния:** default | значения отмечены | focus-visible | 12 тем раскрыты (панель длиннее списка, не прилипает) | панель открыта и закрыта. Недоступных значений нет: значение без ресурсов не показывается (US-14).
- **Матрица:** sidebar 4 + sheet 2 = 6.
- **Отступы:** поля листа `space-4`; между группами `space-6`; внутри группы `space-2`; строка значения — высота `size-control-sm`.
- **Токены:** surface-raised, border-default, text-default, surface-action-primary, border-focus-ring, shadow-md; radius-md; size-sidebar, size-control-sm/md; z-modal.
- **Реализация:** `patterns/filter-panel.php` (`Inserter: no`) — эталон блока «фильтры архива» этапа 12. Панель снизу без JS: `popover` или `<dialog>` с кнопками-командами, выбор пробой фазы 3. Фокус внутри панели и Escape (US-18, критерий 2) доводит этап 14, если без JS не получится.
- **Классы:** `.ds-filters`, `.ds-filters--sidebar|sheet`, `.ds-filters__head`, `.ds-filters__title`, `.ds-filters__close`, `.ds-filters__group`, `.ds-filters__legend`, `.ds-filters__option`, `.ds-filters__actions`.
- **Тексты:** «Фильтры», «Закрыть», «Применить», «Сбросить фильтры», заголовки групп, значения — слова бейджей и подписи платформ.
- **Где стоит:** `/tools/`, `/learn/`, `/assets/`, `/community/`. **Used in:** screens/tools
- **Status:** verified

### sort

- **Назначение:** порядок выдачи в архиве (US-20, этап 14). Стоит над списком, рядом с числом найденного.
- **Анатомия:** подпись «Сортировка» → три чипса: «Сначала проверенные» · «По названию» · «Сначала новые». Текущий — `<span aria-current="true">`, остальные ссылки на тот же адрес с `?sort=`.
- **Варианты:** одного вида.
- **Состояния:** default | hover | focus-visible | текущий.
- **Матрица:** 1 × 4 = 4.
- **Отступы:** зазор `space-2`, подпись кеглем `sm`.
- **Токены:** text-muted (подпись); дальше токены чипса.
- **Реализация:** блок плагина `designstack/sort` → `designstack_core_render_sort()`; чипс тот же, что в `filter-chips`. Меньше двух записей в выдаче — блока нет.
- **Классы:** `.ds-sort`, `.ds-sort__label`, дальше `.ds-chip`.
- **Тексты:** «Сортировка», «Сначала проверенные», «По названию», «Сначала новые»; подпись области для чтеца «Порядок выдачи».
- **Где стоит:** архивы разделов и тем. **Used in:** screens/tools, screens/topic, screens/archives
- **Status:** built

### filter-chips

- **Назначение:** активные фильтры над списком (US-17) и фильтр по типу на странице темы (US-10).
- **Анатомия:** `removable` — ряд чипсов «Прототипирование ×», в конце ссылка «Сбросить фильтры», до 900 в начале кнопка «Фильтры (3)»; `choice` — ряд «Все · Инструменты · Учёба · Ассеты · Сообщества», текущий без ссылки.
- **Варианты:** removable | choice.
- **Состояния:** default | hover | focus-visible | текущий (`aria-current`) | переполнение: 8 чипсов переносятся, на 375 длинное значение обрезается многоточием.
- **Матрица:** 4 + 4 = 8.
- **Отступы:** зазор `space-2`; поля чипса `space-3`; высота `size-control-sm`.
- **Токены:** surface-subtle, border-default (рамка внутрь: «Край поверхности»), text-default, surface-selected, border-focus-ring, border-strong; radius-full; size-control-sm, size-icon-sm.
- **Реализация:** `patterns/filter-chips.php` (`Inserter: no`); чипс — ссылка на адрес без этого значения, крестик — часть ссылки.
- **Классы:** `.ds-chips`, `.ds-chips--removable|choice`, `.ds-chip`, `.ds-chip__label`, `.ds-chip__remove`, `.ds-chips__reset`, `.ds-chips__toggle`.
- **Тексты:** значения фильтров, «Сбросить фильтры», «Фильтры (3)», «Все»; скрытая подпись крестика «Снять фильтр: Бесплатно».
- **Где стоит:** разделы каталога, страница темы. **Used in:** screens/tools, screens/topic
- **Status:** verified

## Контейнеры

### resource-card

- **Назначение:** карточка ресурса во всех списках — разделы, тема, поиск, главная, подборка, выпуск, аналоги (US-26). Одна на все списки; клик по карточке ведёт на страницу ресурса (D16).
- **Анатомия** (D50): плитка логотипа `size-tile-sm` → название до двух строк (D42), под ним подпись типа → состояние записи, если есть → вердикт до трёх строк → метки цены, доступа и оплаты (у бесплатного метки оплаты нет, D28) → теги 2–3 подписями без ссылок (D35) → нижняя строка: «Проверено 3 сен 2026» моноширинным и контурная кнопка «Перейти на сайт»; у закрытого — «Показать аналог» или ничего (D31).
- **Варианты:** тип — инструмент | учебный материал | ассет | сообщество (меняется подпись типа; подпись стоит во всех карточках вместо переключателя D44).
- **Состояния:** default | hover (рамка `border-strong`) | focus-within (кольцо на всей карточке) | «Условия изменились» | «Давно не проверяли» | «Закрыт» с аналогом | «Закрыт» без аналога | бесплатный | переполнение (название 80 знаков, вердикт 120).
- **Матрица:** 4 типа + 8 состояний = 12.
- **Отступы:** поля `space-4`; между частями `space-3`; логотип и название `space-3`; метки — `space-1` по вертикали и `space-2` по горизонтали; нижняя строка — линия `border-default` сверху и `space-3` над содержимым.
- **Токены:** surface-raised, border-default, border-strong, border-focus-ring, text-default, text-muted, surface-subtle; font-size base (название, 600), sm (тип, теги, дата), lg (вердикт); radius-md; size-tile-sm; line-height-snug и base.
- **Реализация:** `patterns/resource-card.php` — статичный эталон; этап 12 повторяет разметку в `render.php` блока «список ресурсов».
- **Классы:** `.ds-card`, `.ds-card--tool|learning|asset|community`, `.ds-card__head`, `.ds-card__titles`, `.ds-card__logo`, `.ds-card__title`, `.ds-card__link`, `.ds-card__type`, `.ds-card__state`, `.ds-card__verdict`, `.ds-card__badges`, `.ds-card__tags`, `.ds-card__foot`, `.ds-card__date`, `.ds-card__action`, `.is-changed|is-stale|is-dead`.
- **Тексты:** «Инструмент», «Учебный материал», «Ассет», «Сообщество», слова статусов, «Проверено 3 сен 2026», «Перейти на сайт», «Показать аналог».
- **Где стоит:** все списки ресурсов. **Нижняя строка — вопрос листа (V1, D52).** **Used in:** screens/collection, screens/digest-issue, screens/home, screens/tools, screens/topic, screens/resource
- **Status:** verified

### resource-list

- **Назначение:** список карточек ресурсов.
- **Анатомия:** сетка карточек; карточки в ряду одной высоты, последний неполный ряд прижат влево.
- **Варианты:** `grid` — 3 колонки от 1200, 2 от 600, 1 меньше, зазор `space-6`; `column` — карточки друг под другом с зазором `space-4` (колонка шага подборки для старта).
- **Состояния:** данные | пусто (вместо сетки — `empty-state`) | переполнение (одна карточка в ряду, 30 карточек в группе). Состояния загрузки нет (D53).
- **Матрица:** 2 × 3 = 6.
- **Отступы:** `space-4`, `space-6`.
- **Токены:** только отступы.
- **Реализация:** `patterns/resource-list.php` (`Inserter: no`) — эталон блока «список ресурсов» этапа 12.
- **Классы:** `.ds-resource-list`, `.ds-resource-list--grid|column`.
- **Тексты:** —
- **Где стоит:** разделы, тема, главная, подборка, выпуск, аналоги, поиск. **Used in:** screens/collection, screens/digest-issue, screens/home, screens/tools, screens/topic, screens/resource
- **Status:** verified

### post-card

- **Назначение:** карточка подборки на главной и в блоке «Другие подборки» (h7, c9). Не похожа на карточку ресурса: без логотипа, меток и кнопки.
- **Анатомия:** название ссылкой до двух строк (ссылка растянута на карточку) → описание до 120 знаков → мета «8 ресурсов · 5 сен 2026».
- **Варианты:** подборка. Выпуск и обзор появятся на этапе 13 вместе с архивами.
- **Состояния:** default | hover | focus-within | переполнение (название 80, описание 120 знаков).
- **Матрица:** 4.
- **Отступы:** поля `space-4`; между частями `space-2`; мета прижата к низу; сетка — 3 колонки от 900, 1 меньше, зазор `space-6`.
- **Токены:** surface-raised, border-default, border-strong, border-focus-ring, text-default, text-muted; font-size lg (600), base, sm; radius-md.
- **Реализация:** `patterns/post-card.php`.
- **Классы:** `.ds-post-card`, `.ds-post-card__title`, `.ds-post-card__link`, `.ds-post-card__desc`, `.ds-post-card__meta`, `.ds-post-list`.
- **Тексты:** мета «8 ресурсов · 5 сен 2026».
- **Где стоит:** главная, страница подборки. **Used in:** screens/search, screens/collection, screens/archives, screens/home
- **Status:** verified

### section-header

- **Назначение:** заголовок блока страницы, при необходимости со строкой под ним и ссылкой «все».
- **Анатомия:** H2 → строка под заголовком → ссылка «Все подборки» справа от 900 и под содержимым до 900.
- **Варианты:** `plain` | `sub` | `more`.
- **Состояния:** — (у ссылки — состояния `link`).
- **Матрица:** 3.
- **Отступы:** над блоком `space-12` от 900 и `space-8` до 900, под заголовком `space-6` (над заголовком воздуха вдвое больше, D50); строка — `space-2` под H2.
- **Токены:** text-default, text-muted; font-size 2xl (700) и base; space-2, 6, 8, 12.
- **Реализация:** `patterns/section-header.php`; вариант `more` — обёртка с областями «заголовок», «содержимое», «ссылка».
- **Классы:** `.ds-section`, `.ds-section__head`, `.ds-section__title`, `.ds-section__sub`, `.ds-section__body`, `.ds-section__more`.
- **Тексты:** «Подборка для старта», «Проверено на этой неделе», «Свежие подборки», «Другие подборки», «Все подборки», «Новое в каталоге», «Перепроверено за неделю», «Находки недели», «Оценка куратора», «Аналог из России».
- **Где стоит:** главная, подборка, выпуск, страница ресурса. **Used in:** screens/collection, screens/home, screens/resource
- **Status:** verified

### page-header

- **Назначение:** заголовок страницы и строка под ним.
- **Анатомия:** H1 → строка: число выдачи, вводная строка или мета.
- **Варианты:** `count` («50 ресурсов» в разделах и на теме), `lead` (вводная строка формы и страницы «Спасибо»), `meta` (описание и мета подборки и выпуска).
- **Состояния:** переполнение: заголовок 80 знаков переносится, не обрезается.
- **Матрица:** 3 + 1 = 4.
- **Отступы:** H1 и строка — `space-2`; от крошек — `space-2`.
- **Токены:** text-default, text-muted; font-size 5xl (fluid), lg, sm; letter-spacing-tight, line-height-tight; size-measure-lead.
- **Реализация:** `patterns/page-header.php`; на страницах H1 — `core/post-title` или `core/query-title` (этап 13).
- **Классы:** `.ds-page-header`, `.ds-page-header__title`, `.ds-page-header__count`, `.ds-page-header__lead`, `.ds-page-header__meta`.
- **Тексты:** «50 ресурсов», «8 ресурсов · 5 сен 2026», «5 новых ресурсов · 6 перепроверенных · 3 находки».
- **Где стоит:** разделы, тема, подборка, выпуск, форма, «Спасибо». **Used in:** screens/collection, screens/digest-issue, screens/archives, screens/tools, screens/topic
- **Status:** verified

### entry-tiles

- **Назначение:** четыре входа в разделы на главной (US-24) и на странице 404.
- **Анатомия:** плитка-ссылка: название раздела с подчёркиванием → строка «Редакторы, прототипы, тесты» (до 600 не выводится).
- **Варианты:** —
- **Состояния:** default | hover (рамка `border-strong`) | focus-visible | переполнение (длинное название переносится).
- **Матрица:** 4.
- **Отступы:** поля `space-4` (от 900) и `space-3`; зазор сетки `space-4` и `space-2`; 4 в ряд от 900, сетка 2×2 меньше.
- **Токены:** surface-raised, border-default, border-strong, border-focus-ring, text-default, text-muted; font-size lg (700) и sm; radius-md.
- **Реализация:** `patterns/entry-tiles.php`.
- **Классы:** `.ds-entries`, `.ds-entry`, `.ds-entry__title`, `.ds-entry__note`.
- **Тексты:** «Инструменты», «Учёба», «Ассеты», «Сообщества» и строки под ними из `home.md`.
- **Где стоит:** главная, 404. **Used in:** screens/not-found, screens/home
- **Status:** verified

### collection-group

- **Назначение:** группа ресурсов в подборке (c3); куратор вставляет её в запись.
- **Анатомия:** H2 → строка описания до 70 знаков → список ресурсов сеткой.
- **Варианты:** —
- **Состояния:** много карточек | одна карточка (прижата влево). Группа без опубликованных ресурсов не выводится.
- **Матрица:** 2.
- **Отступы:** над группой `space-12` от 900 и `space-8` до 900; описание `space-2`; до сетки `space-6`.
- **Токены:** как у `section-header` и `resource-list`.
- **Реализация:** `patterns/collection-group.php`, категория «DesignStack» — видна куратору в редакторе; список — заглушка до блока «список ресурсов» этапа 12.
- **Классы:** `.ds-collection-group` плюс классы секции и списка.
- **Тексты:** примеры групп из `collection.md`.
- **Где стоит:** страница подборки. **Used in:** в шаблонах не стоит — вставляет куратор в редакторе (`Inserter: yes`). Аудит 14.09.2026 проверил и записал это здесь, чтобы следующий не переспрашивал.
- **Status:** verified

### issue-find

- **Назначение:** находка недели в выпуске дайджеста (d7): статья или справка вне каталога; куратор вставляет в запись.
- **Анатомия:** H3 — заголовок-ссылка на источник в новой вкладке → текст куратора 2–4 предложения → строка «help.figma.com · справка».
- **Варианты:** —
- **Состояния:** default | hover и focus-visible заголовка | переполнение (заголовок 100 знаков).
- **Матрица:** 3.
- **Отступы:** между частями `space-2`; между находками `space-6`; ширина до `size-measure`.
- **Токены:** text-default, text-link, text-link-hover, text-muted; font-size lg (600), base, sm; size-icon-sm, size-measure.
- **Реализация:** `patterns/issue-find.php`, категория «DesignStack».
- **Классы:** `.ds-find`, `.ds-find__title`, `.ds-find__text`, `.ds-find__source`.
- **Тексты:** «откроется в новой вкладке»; примеры из `digest-issue.md`.
- **Где стоит:** выпуск дайджеста.
- **Status:** verified

### subscribe-cta

- **Назначение:** подписка на дайджест в Telegram (US-43). Пока канала нет, блока и кнопки нет.
- **Анатомия:** `block` — H2 «Дайджест раз в неделю» → текст → кнопка «Подписаться» (secondary, новая вкладка); `footer` — кнопка в подвале.
- **Варианты:** block | footer.
- **Состояния:** default | без канала — не выводится. Форма подписки по почте — v1.1 (F-66, O4).
- **Матрица:** 3.
- **Отступы:** поля `space-6` от 900 и `space-4` до 900; от 900 текст слева, кнопка справа в одну строку.
- **Токены:** surface-raised, border-default, text-default, text-muted; font-size 2xl и base; radius-md.
- **Реализация:** `patterns/subscribe-cta.php`; вывод по наличию адреса канала — этап 12.
- **Классы:** `.ds-subscribe`, `.ds-subscribe--footer`, `.ds-subscribe__text`, `.ds-subscribe__action`.
- **Тексты:** «Дайджест раз в неделю», «Новые ресурсы и то, что изменилось у старых, — одним постом в Telegram вместо двадцати каналов.», «Подписаться».
- **Где стоит:** главная, выпуск дайджеста, подвал. **Used in:** screens/digest-issue, screens/home
- **Status:** verified

## Навигация

### site-header

- **Назначение:** шапка всех страниц (brief §6, D35, D43).
- **Анатомия:** ссылка «К содержанию» (видна при фокусе) → логотип «DesignStack» → меню из семи пунктов → поиск → переключатель темы. До 900: логотип, кнопка «Поиск», переключатель темы, кнопка «Меню»; меню раскрывает те же семь пунктов и поле поиска.
- **Варианты:** `default` | `home` (без поиска в шапке, D43).
- **Состояния:** от 1200 | 900–1199, поиск свёрнут и раскрыт | до 900, меню закрыто и открыто | текущий пункт (`aria-current="page"`) | фокус на «К содержанию».
- **Матрица:** 2 варианта × 4 состояния = 8.
- **Отступы:** высота `size-header`; зазоры ряда и меню — от `space-2` до `space-6` по ширине окна. Ряд шапки проверяется на границах 900 и 1200 (`.claude/rules/wp-theme.md` §7): с Golos Text он уже вылезал на 11 и 21 px.
- **Токены:** surface-raised, border-default, text-default, surface-selected, border-focus-ring, shadow-md; font-size 2xl (логотип, 700) и base; size-header, size-control-md, size-search-header, size-icon-md; z-header, z-dropdown.
- **Реализация:** `parts/header.html`; вариант `home` — паттерн сам проверяет `is_front_page()` и не выводит поиск (D43, этап 13); меню — `core/navigation` с меню, созданным через WP-CLI, без оверлея ядра; раскрытие меню и поиска без JS (`<details>` или popover) — проба фазы 3. Витрина показывает part в состояниях: `patterns/site-header.php` (`Inserter: no`).
- **Классы:** `.ds-header`, `.ds-header__skip`, `.ds-header__bar`, `.ds-header__logo`, `.ds-header__nav`, `.ds-header__menu`, `.ds-header__menu-toggle`, `.ds-header__search`, `.ds-header__search-menu`, `.ds-header__search-toggle`, `.ds-header__controls`, `.ds-header__panel`.
- **Тексты:** «К содержанию», «DesignStack», семь пунктов меню, «Поиск», «Меню», «Тёмная тема»; подпись меню для чтеца «Разделы каталога».
- **Где стоит:** все страницы. **Вид текущего пункта — вопрос листа (V3).** **Used in:** screens/collection, screens/digest-issue, screens/archives, screens/home, screens/tools, screens/topic, screens/resource
- **Status:** verified

### site-footer

- **Назначение:** подвал всех страниц (brief §6, D35).
- **Анатомия:** подписка → ссылки «Обзоры», «Принципы оценки», «Предложить ресурс», «Политика данных» → «Темы» с 12 ссылками → «© 2026 DesignStack».
- **Варианты:** —
- **Состояния:** с каналом | без канала | текущая тема без ссылки (на странице темы).
- **Матрица:** 3.
- **Отступы:** от 900 три колонки `size-sidebar` · `size-sidebar` · остальное с зазором `space-8`; до 900 одна колонка с зазором `space-6`; поля по вертикали `space-8`; строка копирайта отделена линией `border-default` и `space-3`.
- **Токены:** border-default, text-default, text-link, text-muted; font-size base и sm.
- **Реализация:** `parts/footer.html`; витрина — `patterns/site-footer.php` (`Inserter: no`).
- **Классы:** `.ds-footer`, `.ds-footer__inner`, `.ds-footer__title`, `.ds-footer__subscribe`, `.ds-footer__links`, `.ds-footer__topics`, `.ds-footer__copy`.
- **Тексты:** «Подписаться», «Обзоры», «Принципы оценки», «Предложить ресурс», «Политика данных», «Темы», 12 тем, «© 2026 DesignStack».
- **Где стоит:** все страницы. **Used in:** screens/collection, screens/digest-issue, screens/archives, screens/home, screens/tools, screens/topic, screens/resource
- **Status:** verified

### breadcrumbs

- **Назначение:** путь на внутренних страницах (brief §6, D35: крошки темы без звена «Темы»).
- **Анатомия:** «Главная» → раздел → текущая страница без ссылки; разделитель — `chevron-right` 16, скрыт от чтеца.
- **Варианты:** два звена | три звена.
- **Состояния:** default | hover и focus-visible ссылки | текущее звено (`aria-current="page"`) | переполнение (длинное звено переносится).
- **Матрица:** 2 × 2 = 4.
- **Отступы:** высота строки `size-control-md`; зазор `space-1`.
- **Токены:** text-link, text-link-hover, text-muted, border-focus-ring; font-size sm; size-icon-sm.
- **Реализация:** блок `core/breadcrumbs` WordPress 7.1, если проба фазы 3 даст нужную разметку; иначе своя разметка. `patterns/breadcrumbs.php`.
- **Классы:** `.ds-breadcrumbs`, `.ds-breadcrumbs__item`, `.ds-breadcrumbs__sep`.
- **Тексты:** «Главная»; подпись для чтеца «Навигационная цепочка».
- **Где стоит:** все страницы, кроме главной. **Used in:** screens/collection, screens/digest-issue, screens/archives, screens/tools, screens/topic, screens/resource
- **Status:** verified

### pagination

- **Назначение:** страницы списка адресами (D17, US-20).
- **Анатомия:** от 600 — «Назад» · номера · «Вперёд»; до 600 — «Назад» · «Страница 1 из 3» · «Вперёд». Текущая страница выделена и не ссылка; на первой «Назад» неактивна, на последней — «Вперёд». Одна страница — блока нет.
- **Варианты:** `numbers` | `compact`.
- **Состояния:** default | hover | focus-visible | текущая | первая | последняя.
- **Матрица:** 2 × 4 = 8.
- **Отступы:** номер — квадрат `size-control-md`; зазор `space-2`; «Назад» и «Вперёд» — кнопка secondary md с шевроном.
- **Токены:** surface-raised, border-strong, text-action, surface-selected, border-focus-ring, text-default, text-muted; radius-sm; size-control-md, size-icon-sm.
- **Реализация:** `core/query-pagination` со стилями (этап 13); эталон — `patterns/pagination.php`.
- **Классы:** `.ds-pagination`, `.ds-pagination__prev`, `.ds-pagination__next`, `.ds-pagination__numbers`, `.ds-pagination__page`, `.ds-pagination__summary`, `.is-current`, `.is-disabled`.
- **Тексты:** «Назад», «Вперёд», «Страница 1 из 3»; подпись для чтеца «Страницы».
- **Где стоит:** все списки с пагинацией. **Used in:** screens/archives, screens/tools, screens/topic
- **Status:** verified

## Фидбэк

### badge

- **Назначение:** метка свойства или статуса ресурса. Не кликается (D35).
- **Анатомия:** рамка `border-default` → иконка 16 (у статусов доступа и оплаты) → слово. Тонированная: фон `bg-warning` или `bg-error`, без рамки, иконка и слово.
- **Варианты по виду:** цена (нейтральная, без иконки) | грейд (нейтральная, без иконки) | доступ `ru_open` (нейтральная, цветная иконка) | оплата `ru_payment` (нейтральная, цветная иконка) | состояние записи `changed`, `dead` (тонированная) | давность проверки больше 90 дней (тонированная, `clock`). Тон в CSS — единственная ось: `success`, `warning`, `error` у иконки и `tint-warning`, `tint-error` у фона.
- **Состояния:** переполнение: в узкой колонке метка переносится внутри себя (случай этапа 10: «Открывается из РФ» вылезала на 4 px).
- **Матрица:** по видам 4 + 3 + 3 + 3 + 2 + 1 = 16.
- **Отступы:** поля `space-1` по вертикали и `space-2` по горизонтали; зазор иконки и слова `space-1`.
- **Токены:** border-default, text-default, icon-success, icon-warning, icon-error, bg-warning, bg-error; font-size sm (вес 500); radius-sm; size-icon-sm.
- **Реализация:** `patterns/badge.php` (`Inserter: no`); этап 12 выводит те же классы из полей ресурса.
- **Классы:** `.ds-badge`, `.ds-badge--success|warning|error|tint-warning|tint-error`, `.ds-badge__icon`, `.ds-badges`.
- **Тексты:** раздел «Статусы» в `docs/VOICE.md`.
- **Где стоит:** карточка, страница ресурса. **Used in:** screens/home, screens/tools, screens/topic, screens/resource
- **Status:** verified

### notice

- **Назначение:** уведомление на странице: состояние записи на странице ресурса (US-32, US-33) и сообщения формы (US-42, D46).
- **Анатомия:** иконка 20 → заголовок словом статуса → текст-расшифровка → действие (кнопка или ссылка, необязательно).
- **Варианты:** `dead` (фон `bg-error`, `circle-x`, «Закрыт», кнопка «Показать аналог», если аналог есть) | `changed` (`bg-warning`, `triangle-alert`) | `stale` (`bg-warning`, `clock`) | `info` (`bg-info` с рамкой `border-default`, иконка `info`: сбой отправки, лимит, «уже есть в каталоге» со ссылкой).
- **Состояния:** с действием | без действия.
- **Матрица:** 2 + 1 + 1 + 3 = 7.
- **Отступы:** поля `space-4`; зазор иконки и текста `space-3`; между заголовком, текстом и действием `space-2`.
- **Токены:** bg-error, bg-warning, bg-info, border-default, icon-error, icon-warning, icon-info, text-default; font-size base (заголовок 600); radius-md; size-icon-md.
- **Реализация:** `patterns/notice.php` (`Inserter: no`).
- **Классы:** `.ds-notice`, `.ds-notice--dead|changed|stale|info`, `.ds-notice__icon`, `.ds-notice__body`, `.ds-notice__title`, `.ds-notice__text`, `.ds-notice__action`.
- **Тексты:** расшифровки статусов из `docs/VOICE.md`; сбой, лимит и «уже есть в каталоге» — из `suggest.md`.
- **Где стоит:** страница ресурса, форма. **Used in:** screens/suggest, screens/resource
- **Status:** verified

### empty-state

- **Назначение:** пустая выдача и пустой список: причина словами и что сделать (US-19, US-21, US-23).
- **Анатомия:** иллюстрация `size-illustration` → H2 с причиной → текст, где названы фильтры → действия: «Сбросить фильтры» (primary) и ссылка «Предложить ресурс».
- **Варианты:** `filters` (пустая выдача фильтров) | `section` (раздел, тема или подборка без ресурсов) | `search` (поиск без результатов) | `not-found` (404; поиск и входы в разделы добавляет шаблон этапа 13).
- **Состояния:** с действиями | без действий.
- **Матрица:** 4 варианта × 2 = 6 (каждая ячейка — в обеих темах).
- **Отступы:** поля `space-6`; между частями `space-3`; зазор действий `space-4`.
- **Токены:** surface-raised, border-default, text-default, text-muted; в иллюстрации — text-muted (линия), surface-selected (заливка акцентного предмета), border-focus-ring (обводка); font-size 2xl и base; radius-md; size-illustration.
- **Реализация:** `patterns/empty-state.php`; иллюстрации — SVG в `assets/img/`, выводятся инлайном хелпером, цвета из переменных, поэтому одна картинка работает в обеих темах.
- **Классы:** `.ds-empty`, `.ds-empty--filters|section|search|not-found`, `.ds-empty__art`, `.ds-empty__title`, `.ds-empty__text`, `.ds-empty__actions`.
- **Тексты:** «По таким условиям ничего нет», «В разделе пока нет ресурсов», «В этой теме пока нет ресурсов», «В подборке пока нет ресурсов», «Сбросить фильтры», «Предложить ресурс», «Все подборки»; тексты поиска и 404 — новые, см. «Слова для словаря».
- **Где стоит:** разделы, тема, подборка, поиск, 404. **Иллюстрации — вопрос листа (V5).** **Used in:** screens/search, screens/not-found, screens/archives, screens/topic
- **Status:** verified

## Данные

### meta-line

- **Назначение:** даты и счётчики моноширинным шрифтом (D50): «Проверено 3 сен 2026», «50 ресурсов», «8 ресурсов · 5 сен 2026».
- **Анатомия:** значения через « · », табличные цифры.
- **Варианты:** `date` | `count` | `meta`.
- **Состояния:** —
- **Матрица:** 3.
- **Отступы:** —
- **Токены:** font-family mono, font-size sm (в карточке — вопрос V1), text-muted; `font-variant-numeric: tabular-nums`.
- **Реализация:** стиль блока `core/paragraph` «Мета» (`register_block_style`) и класс для разметки плагина; `patterns/meta-line.php` (`Inserter: no`).
- **Классы:** `.ds-meta`, `.ds-meta--xs` (кегль `xs` — дата в подвале карточки), `.is-style-meta`.
- **Тексты:** «Проверено 3 сен 2026», «50 ресурсов», «8 ресурсов · 5 сен 2026», «5 новых ресурсов · 6 перепроверенных · 3 находки».
- **Где стоит:** карточки, шапки страниц, подборка, выпуск. **Used in:** screens/collection, screens/digest-issue, screens/archives, screens/home, screens/tools, screens/topic, screens/resource
- **Status:** verified

### resource-logo

- **Назначение:** узнать ресурс в списке (D55, D50 §8).
- **Анатомия:** плитка `surface-subtle` с радиусом `radius-md` → логотип в WebP или первая буква названия. Рамка `border-default` внутрь — только когда плитка стоит на подложке страницы, в карточке её нет («Край поверхности»).
- **Варианты:** `sm` (`size-tile-sm`: карточка, аватар куратора) | `lg` (`size-tile-lg`: страница ресурса).
- **Состояния:** логотип | первая буква.
- **Матрица:** 2 × 2 = 4.
- **Токены:** surface-subtle, border-default, text-default; font-size lg и 3xl (буква, 700); radius-md; size-tile-sm, size-tile-lg.
- **Реализация:** часть `resource-card` и первого экрана ресурса; `patterns/resource-logo.php` (`Inserter: no`). Исходник 128×128, показ 40 и 64, `alt` — название ресурса.
- **Классы:** `.ds-logo`, `.ds-logo--sm|lg`, `.ds-logo--rimmed` (плитка на подложке страницы — с рамкой), `.ds-logo__img`, `.ds-logo__letter`.
- **Тексты:** —
- **Где стоит:** карточка, страница ресурса, подпись куратора. **Used in:** screens/home, screens/tools, screens/topic, screens/resource
- **Status:** verified

### resource-facts

- **Назначение:** факты ресурса парами «подпись — значение» (US-28); пустое необязательное поле не выводится.
- **Анатомия:** лист с рамкой → пары: Цена (значение и `price_note` строкой ниже) · Доступ из РФ (бейдж и расшифровка) · Оплата из РФ (бейдж и расшифровка; у бесплатного нет) · Язык · Грейд · Темы ссылками · поля своего типа.
- **Варианты:** инструмент (Платформы, Бесплатный тариф, ИИ-функции) | учебный материал (Формат, Длительность, Сертификат) | ассет (Лицензия, Формат файла, Кириллица, Количество) | сообщество (Платформа, Размер аудитории, Активность, Вакансии).
- **Состояния:** полный набор | без необязательных полей | узкая колонка (подпись над значением).
- **Матрица:** 4 типа + 2 = 6.
- **Отступы:** поля `space-4`; между парами `space-3`; подпись и значение — `space-4` рядом или `space-1` друг под другом.
- **Токены:** surface-raised, border-default, text-muted (подпись), text-default, text-link; font-size sm и base; radius-md.
- **Реализация:** `patterns/resource-facts.php` (`Inserter: no`) с `container-type: inline-size`: в узкой колонке подпись встаёт над значением. Эталон для этапов 12 и 13.
- **Классы:** `.ds-facts`, `.ds-facts__list`, `.ds-facts__label`, `.ds-facts__value`, `.ds-facts__note`.
- **Тексты:** подписи фактов — см. «Слова для словаря»; значения — из `docs/VOICE.md`.
- **Где стоит:** страница ресурса. **Раскладка узкой колонки — вопрос листа (V7).** **Used in:** screens/resource
- **Status:** verified

### curator-review

- **Назначение:** оценка автора из трёх частей с подписью «Анастасия Дорожкина» (US-29, US-30, D32, D134).
- **Анатомия:** H2 «Оценка куратора» → «Кому подходит» и текст → «За что» и текст → «Когда не подойдёт» и текст → подпись: плитка `size-tile-sm` и «Куратор DesignStack» ссылкой на `/about/#curator` (имени человека нет, пока оно не выбрано — O2, решение r5). Имя — заглушка до O2.
- **Варианты:** —
- **Состояния:** default | hover и focus-visible подписи | длинная оценка (ширина до `size-measure`).
- **Матрица:** 3.
- **Отступы:** между частями `space-4`; подзаголовок и текст `space-1`; подпись — `space-6` сверху, зазор `space-3`.
- **Токены:** text-default, text-link, text-link-hover, surface-subtle, border-default; font-size 2xl, base (подзаголовок 600), sm; size-tile-sm, size-measure.
- **Реализация:** `patterns/curator-review.php`; эталон для этапов 12 и 13.
- **Классы:** `.ds-review`, `.ds-review__part`, `.ds-review__label`, `.ds-review__text`, `.ds-review__sign`.
- **Тексты:** «Оценка куратора», «Кому подходит», «За что», «Когда не подойдёт».
- **Где стоит:** страница ресурса. **Used in:** screens/resource
- **Status:** verified

## Раскладки страниц

Появились на этапе 13: страница собирается из паттернов, но сами колонки страницы паттернами не были.

### page-layout

- **Назначение:** две колонки страницы — раздел каталога (панель фильтров и выдача) и страница ресурса (чтение и факты).
- **Анатомия:** `ds-archive` — колонка `size-sidebar` и выдача; `ds-detail` — области «шапка», «факты», «оценка».
- **Варианты:** `archive` | `detail`.
- **Состояния:** от 900 две колонки | до 900 одна колонка в порядке разметки.
- **Матрица:** 2 × 2 = 4.
- **Отступы:** зазор колонок `space-8`.
- **Токены:** size-sidebar, space-8.
- **Реализация:** только CSS в `patterns.css`, раздел «раскладки страниц»; шаблоны ставят классы на `core/group`. Порядок в разметке — шапка, факты, оценка: он же читается в одну колонку до 900, а от 900 `grid-template-areas` кладёт оценку под шапку.
- **Классы:** `.ds-archive`, `.ds-detail`, `.ds-detail__hero`, `.ds-detail__facts`, `.ds-detail__review`, `.ds-chips__toggle` (кнопка «Фильтры» видна только до 900).
- **Тексты:** —
- **Где стоит:** разделы каталога, тема, страница ресурса. **Used in:** screens/tools, screens/topic, screens/resource
- **Status:** built

### starter-steps

- **Назначение:** четыре шага подборки для старта на главной (US-25): маршрут «исследование → прототип → интерфейс → портфолио» виден одним взглядом.
- **Анатомия:** колонка шага: H3 с номером и названием → список карточек `resource-list --column`.
- **Варианты:** —
- **Состояния:** четыре шага | шаг без ресурсов не выводится | одна карточка в шаге.
- **Матрица:** 3.
- **Отступы:** зазор колонок и между шагами `space-8`; внутри шага `space-4`.
- **Токены:** text-default; font-size lg (700); space-4, space-8.
- **Реализация:** `designstack_core_render_starter()` в плагине, блок `designstack/starter-set`; CSS в `patterns.css`. Шаги — темы каталога, отбор по грейду Junior; ресурс не повторяется между шагами.
- **Классы:** `.ds-steps`, `.ds-steps__step`, `.ds-steps__title`.
- **Тексты:** «Подборка для старта», «1. Исследование», «2. Прототип», «3. Интерфейс», «4. Портфолио».
- **Где стоит:** главная. **Used in:** screens/home
- **Status:** built

### prose

- **Назначение:** текст записи редакции: подборка, выпуск, обзор. Читают текст, сканируют списки — ширины разные.
- **Анатомия:** абзацы, заголовки и списки не шире `size-measure`; блоки каталога внутри записи идут во всю ширину.
- **Варианты:** —
- **Состояния:** текст | текст со вставленными блоками | пустое содержимое.
- **Матрица:** 3.
- **Отступы:** между блоками `space-6`.
- **Токены:** size-measure; space-6.
- **Реализация:** класс на `core/post-content` в `single.html`; CSS в `patterns.css`.
- **Классы:** `.ds-prose`.
- **Тексты:** —
- **Где стоит:** подборка, выпуск, обзор. **Used in:** screens/suggest, screens/about, screens/collection, screens/digest-issue
- **Status:** built

### issue-nav

- **Назначение:** переход между выпусками дайджеста (d8).
- **Анатомия:** «Предыдущий выпуск» и неделя под ним → «Все выпуски» → «Следующий выпуск».
- **Варианты:** —
- **Состояния:** оба соседа | только предыдущий | только следующий | ни одного — остаётся «Все выпуски».
- **Матрица:** 4.
- **Отступы:** от содержимого `space-6` и линия сверху; зазор в ряду `space-6`, в колонке `space-4`.
- **Токены:** text-link, text-muted, border-default; space-1/4/6; border-width-hairline.
- **Реализация:** `designstack_core_render_issue_nav()` в плагине, блок `designstack/issue-nav`; на не-выпусках не выводится.
- **Классы:** `.ds-issue-nav`, `.ds-issue-nav__prev`, `.ds-issue-nav__next`, `.ds-issue-nav__all`.
- **Тексты:** «Предыдущий выпуск», «Следующий выпуск», «Все выпуски».
- **Где стоит:** выпуск дайджеста. **Used in:** screens/digest-issue
- **Status:** built

### resource-hero

- **Назначение:** первый экран страницы ресурса: узнать ресурс, прочитать вердикт, увидеть состояние и уйти на сайт.
- **Анатомия:** плитка логотипа `size-tile-lg` → H1 → подпись типа → вердикт крупнее текста → метки цены, доступа и оплаты → плашка состояния → кнопка «Перейти на сайт» и дата проверки.
- **Варианты:** —
- **Состояния:** активен | «Закрыт» (кнопки перехода нет, в плашке «Показать аналог») | «Условия изменились» | «Давно не проверяли» | бесплатный (метки оплаты нет).
- **Матрица:** 5.
- **Отступы:** между частями `space-4`; логотип и заголовок `space-4`; в строке действий `space-4`.
- **Токены:** text-default, text-muted, surface-action-primary, text-on-action; size-tile-lg, size-control-lg, size-measure-lead; font-size xl (вердикт), sm (тип).
- **Реализация:** `designstack_core_render_hero()` в плагине, блок `designstack/resource-hero`. Заголовок внутри блока: логотип, название и подпись типа стоят одной строкой, отдельным `core/post-title` её не разорвать.
- **Классы:** `.ds-hero`, `.ds-hero__head`, `.ds-hero__titles`, `.ds-hero__title`, `.ds-hero__type`, `.ds-hero__verdict`, `.ds-hero__actions`.
- **Имя занято:** `ds-hero*` — только этот паттерн. Баннер карты компетенций живёт на `ds-banner*`: с 15 по 16.09.2026 он носил те же имена и своим тёмным фоном гасил текст на всех карточках каталога (D157).
- **Тексты:** «Перейти на сайт», «Показать аналог», «Проверено 3 сен 2026», слова состояний.
- **Где стоит:** страница ресурса. **Used in:** screens/resource
- **Status:** built

## Утилиты раскладки

Три класса без собственного паттерна — ими паттерны и страницы выкладывают свои части. Новый утилитарный класс заводится здесь же, до кода.

- `.ds-row` — ряд с переносом, зазор `space-3`, элементы по центру: кнопка с иконкой, подпись со значением.
- `.ds-stack` — колонка с зазором `space-6`; `.ds-stack > *` получает `min-width: 0`, иначе длинное слово внутри растягивает колонку.
- `.ds-fields` — колонка полей формы шириной `size-form`: строка ввода шире читаемой меры не растёт.
- `.ds-icon`, `.ds-icon--md` — размер иконки из спрайта: 16 по умолчанию, 20 в кнопках, шапке и уведомлениях. Ставит хелпер `designstack_icon()`.
- `.ds-art-accent` — акцентный предмет в иллюстрации пустого состояния: заливка `surface-selected`, обводка `border-focus-ring` (D50 §8).

## Иконки и иллюстрации

- Библиотека одна — Lucide (ISC), штрих 1,75, скруглённые концы (D50 §7). Спрайт `assets/img/icons.svg`: `<symbol id="icon-<имя>">` со `stroke="currentColor"`. Хелпер `designstack_icon( string $name, string $label = '' ): string`: без подписи — `aria-hidden="true"`, с подписью — `role="img"` и `aria-label`.
- Двенадцать имён: `circle-check`, `triangle-alert`, `circle-x`, `clock`, `info` — статусы и уведомления; `search`, `menu`, `x`, `moon` — шапка, панель, чипсы; `chevron-left`, `chevron-right` — пагинация, крошки, отдельная ссылка; `external-link` — переход в новую вкладку.
- Размеры: 16 в метках и ссылках, 20 в кнопках, шапке и уведомлениях.
- Иллюстрации пустых состояний, 160×112 (D50 §8): `empty-filters.svg` — стопка карточек и лупа на краю передней; `empty-section.svg` — пустая полка; `not-found.svg` — ряд карточек с пустым местом. Линия `text-muted`, один акцентный предмет: заливка `surface-selected`, обводка `border-focus-ring`. Предметы не закрывают углы друг друга — проверка hit test (D50 §8).

## Контракт разметки для этапа 12

Плагин `designstack-core` повторяет разметку этих паттернов в `render.php`: `resource-card`, `resource-list`, `badge`, `notice`, `empty-state`, `filter-panel`, `filter-chips`, `suggest-form` с `form-field` и `error-summary`, `resource-facts`, `curator-review`, `meta-line`, `resource-logo`, `pagination`, `breadcrumbs`.

Повторяются: имена классов, порядок частей и атрибуты доступности — `aria-current`, `aria-invalid` и `aria-describedby`, `aria-busy`, `aria-pressed`, скрытые подписи. Новый класс в `render.php`, которого нет здесь, — баг; сначала строка в каталоге, потом код.

## Слова для словаря

### Утверждены в карточках этапа 08, вношу в `docs/VOICE.md` после апрува

- Фильтры: «Фильтры», «Фильтры (3)», «Применить», «Сбросить фильтры», «Все»; заголовки групп «Тема», «Цена», «Платформа», «Грейд», «Формат», «Язык», «Лицензия», «Формат файла», «Кириллица», «Есть вакансии»; платформы инструментов «Веб», «macOS», «Windows», «iOS», «Android», «Плагин Figma».
- Страница ресурса: подписи фактов «Цена», «Язык», «Грейд», «Темы», «Платформы», «Бесплатный тариф», «ИИ-функции», «Формат», «Длительность», «Сертификат», «Лицензия», «Формат файла», «Кириллица», «Количество», «Платформа», «Размер аудитории», «Активность», «Вакансии»; части оценки «Кому подходит», «За что», «Когда не подойдёт».
- Главная и редакция: «Подборка для старта», «Проверено на этой неделе», «Свежие подборки», «Все подборки», «Другие подборки», «В подборке пока нет ресурсов», «Новое в каталоге», «Перепроверено за неделю», «Находки недели», «Предыдущий выпуск», «Следующий выпуск», «Все выпуски», «Дайджест раз в неделю».
- Списки и пустые состояния: «50 ресурсов», «По таким условиям ничего нет», «В разделе пока нет ресурсов», «В этой теме пока нет ресурсов», «Назад», «Вперёд», «Страница 1 из 3», «Главная».
- Форма: «Проверь форму», «необязательно», «Отправляем…», «Спасибо!», «Вернуться в каталог», подписи и подсказки полей, тексты ошибок, сбоя, лимита и «уже есть в каталоге».

### Новые — нужен ответ

- «К содержанию» — ссылка пропуска к содержимому (WCAG 2.4.1).
- «Закрыть» — кнопка панели фильтров и меню.
- «Снять фильтр: Бесплатно» — скрытая подпись крестика чипса.
- «откроется в новой вкладке» — скрытая подпись внешней ссылки.
- «Разделы каталога», «Навигационная цепочка», «Страницы» — подписи областей для экранного чтеца.
- Поиск без результатов: «По запросу „экслидроу“ ничего нет» и «Попробуй короче или другими словами. Если ресурса нет в каталоге — предложи его.»
- Страница 404: «Такой страницы нет» и «Адрес мог измениться или в нём опечатка. Найди ресурс поиском или открой раздел.»
- Подписи поля доступа и оплаты: «Доступ из РФ» и «Оплата из РФ» — и в фактах, и в заголовках групп фильтров, вместо «Открывается из РФ» и «Оплачивается из РФ». Причина: сейчас подпись повторяет значение — «Открывается из РФ: Открывается из РФ». Слова бейджей и самих значений не меняются.
- Склонение чисел: «1 ресурс, 2 ресурса, 5 ресурсов», «1 находка, 2 находки, 5 находок», «1 новый ресурс, 2 новых ресурса, 5 новых ресурсов», «1 перепроверенный, 2 перепроверенных».

## Выбор на листе (D58)

Внешний вид утверждён отметками 12.09.2026: семь разделов и «Библиотека целиком» — ✔ без замечаний. Семь развилок решены так:

| # | Вопрос | Выбор |
|---|---|---|
| V1 | Нижняя строка карточки | Дата моноширинным `xs` и малая кнопка: строка помещается на 1440 |
| V2 | Наведение на контурную кнопку | Подложка `surface-subtle` |
| V3 | Текущий пункт меню | Подложка выбранного и рамка акцента |
| V4 | Поле с ошибкой | Тонкая рамка; ошибку несут иконка и текст |
| V5 | Иллюстрации | Приняты; у пустой выдачи фильтров лупа сдвинута левее |
| V6 | Иконка переключателя темы | Луна в светлой теме, солнце в тёмной |
| V7 | Факты в узкой колонке | Подпись над значением |

Варианты, которые не выбраны, удалены из `assets/css/styleguide.css` вместе с разделом вопросов витрины.

## Витрина `/styleguide/`

- Страница создана на этапе 10 как заглушка; метку `_designstack_stub` снимаю — витрина остаётся после этапа 13. Заголовок «Витрина дизайн-системы», `noindex`, в меню и карте сайта её нет, ссылка — в админ-баре.
- Шаблон `templates/page-styleguide.html`: шапка → `styleguide-foundation` (палитра, шрифты, отступы, радиусы, тень и размеры из `wp_get_global_settings()`) → по одному `styleguide-<паттерн>` на паттерн: строки — варианты, столбцы — состояния, в ячейке — тот же `patterns/<паттерн>.php` через `do_blocks()` с классом состояния, а не копия разметки → три песочницы: «архив» (крошки, шапка страницы, чипсы, панель, список, пагинация), «карточка и закрытый ресурс», «форма во всех состояниях» → подвал.
- Переключатель «Подсветить кликабельное» (`aria-pressed`) обводит `a[href]`, `button`, `input`, `summary`, `[tabindex]` и оверлей карточки, остальное глушит.

## Не паттерны — композиции этапа 13

Первый экран главной, шаги подборки для старта, «Проверено на этой неделе», первый экран страницы ресурса, блок аналогов, описание и дочерние темы, первый экран и навигация выпуска, страница «Спасибо», текстовые страницы. Каждая из них встречается один раз и собирается из паттернов выше на этапе 13.

## Статус

30 паттернов — `built`: код в `wordpress/wp-content/themes/designstack/`, каждый виден на витрине во всех вариантах и состояниях.
Версия 2 от 14.09.2026 — аудит этапа 15: заведена запись `sort` (этап 14 добавил класс без неё), дописаны 22 класса, живших в коде без записи, и раздел «Утилиты раскладки». Разрыв «код → каталог» закрыт.
`verified` ставится после отметки «Библиотека целиком» на листе.

**Как собрано — отличия от плана:**

- Шапка и подвал живут в `parts/header.html` и `parts/footer.html`, а те состоят из одной строки — вставки паттернов `site-header` и `site-footer`: в части шаблона нельзя вызвать PHP-хелперы иконок, а в паттерне можно.
- Витрину собирают девять обёрток `patterns/styleguide-*.php` — по одной на раздел, а не на паттерн: ячейку состояния делает общий хелпер `designstack_styleguide_matrix()`, поэтому копий разметки нет.
- Состояние в ячейке ставит `WP_HTML_Tag_Processor`: он дописывает класс `is-hover` тому же паттерну. Содержимое паттерна ядро кэширует на запрос, поэтому число образцов внутри паттерна витрина меняет стилем, а не переменной.
- Меню — запись `wp_navigation` «Разделы каталога» (`scripts/navigation.php`); паттерн шапки ищет её по слагу и без неё печатает статический список.
- Ссылку «Перейти к содержимому» ставит ядро WordPress на `#ds-main`; своя не нужна.
- Крошки — блок `core/breadcrumbs`; подпись области и разделитель приводит к словарю фильтр `designstack_breadcrumbs_markup()`: свой разделитель ядра гасится, «›» рисует паттерн (этап 13).
- Иконок в спрайте 13: двенадцать из каталога плюс `sun` для варианта V6 на витрине.
