# Сверка фактов · «Токены и темы» J/M/S · 06.10.2026

Каждое утверждение уроков сверено с первоисточником двумя агентами-сверщиками 06.10.2026; сеть не российская (Казахстан).
Справка Figma читалась через API справочного центра (`help.figma.com/api/v2/help_center/en-us/articles/<id>.json`), дата —
`edited_at`. Material 3 — из JSON, который загружает m3.material.io (контент 2026-09-23). Статьи Натана Кертиса на Medium
закрыты от робота (403) и прочитаны по снимкам Wayback той же страницы. Тарифы Figma не проверены из России, цены не приводятся.
Списки «Что почитать дальше» — `docs/research/reads/tokens-themes-*.md`.

## Figma (сверщик A, 06.10.2026, API справки)

| Утверждение | Урок | Источник (edited_at) | Цитата | Вердикт |
|---|---|---|---|---|
| Типов переменных шесть: color, number, string, boolean, timing, easing (timing и easing — для анимации); коллекция — набор переменных и режимов | J §2 | help.figma.com/…/14506821864087 «Overview of variables, collections, and modes» (03.09.2026) | «There are six types of variables.» «A collection is a set of variables and modes.» | да; первоначально в уроке было «четыре» — исправлено |
| Number — радиус, размеры с min/max, кегль, насыщенность (только числом), интерлиньяж, межбуквенное (в px), отступ абзаца, прозрачность, padding и gap, тени, обводка, текст слоя; string — семейство и начертание шрифта, текст, видимость при "true"/"false"; boolean — видимость слоя, вариант true/false | J §2 | …/14506821864087; …/15343107263511 «Apply variables to designs» (21.08.2026) | «Padding and gap»; «Corner radius and individual corner radius»; «Font size» | да |
| Detach variable; ручки отступа на холсте отвязывают числовую переменную | J §2, задание | …/15343107263511 | «Using on-canvas controls to change an auto layout frame’s padding or gap will detach any applied number variables.» | да |
| Имя переменной в поле свойства после привязки | — | — | в тексте справки не описано (интерфейс) | в урок не взято; вместо этого — как привязать по справке: «=» в числовом поле, вкладка Libraries для цвета |
| Стиль держит набор значений, переменная — одно значение на режим; переменные можно ставить в стили, стили в переменные — нет | J §2 | …/15871097384471 «The difference between variables and styles» (01.10.2025); …/14506821864087 | «Styles are built to hold a combination of values» «Variables can be applied to styles and other variables, but styles cannot be applied to either» | да |
| Косая черта в имени — группы | J §2 | …/15343816063383 «Modes for variables» (24.06.2026); …/38978644498199 (05.10.2026) | «Figma uses / as a separator to create nested groups» | да |
| Области применения (scope) для number, color, string; это фильтр выбора, а не запрет | M | …/15145852043927 «Create and manage variables and collections» (03.09.2026); developers.figma.com variables-types | «Scoping is available for number, color, and string variables.» «This only limits the variables that are shown in pickers within the Figma UI.» | да |
| Alias — ссылка на переменную того же типа | M §1 | …/14506821864087 | «Any variable can reference another variable of the same type.» | да |
| Режимы: Starter — нет (один режим), Professional — до 10 на коллекцию, Organization — до 20, Enterprise — без ограничения с расширенными коллекциями; есть на Education; переменные — на любом тарифе | M | …/360040328273 «Compare Figma plans and features» (02.10.2026); …/15343816063383 | «Up to 10 modes per collection» «Anyone on Education, Professional, Organization, and Enterprise plans can create and use modes» | да; тарифы не проверены из РФ |
| Новый режим получает копию значений первого (крайнего левого) столбца — режима по умолчанию | M §4 | …/15343816063383 | «Figma duplicates values from the first column to the new one.» «the default mode of a variable collection is the left-most column» | да |
| Режим ставят слою, группе, фрейму, компоненту, секции, странице; по умолчанию Auto — режим ближайшего родителя, иначе режим по умолчанию | M §3 | …/15343816063383 | «Objects with variables have their modes set to Auto by default. This means they take on the mode of their parent container.» | да |
| Встроенный импорт JSON в формате DTCG (каждый файл — режим; цвет, размеры в px, числа, строки, шрифт, длительность в s, ссылки) и экспорт одного или всех режимов коллекции в JSON; объявлено на Schema 2025, «available in November» | S | …/15343816063383; figma.com/blog/schema-2025-design-systems-recap/ (28.10.2025) | «Design tokens must be in a JSON file and follow the Design Tokens Community Group (DTCG) format.» «You can export variable modes to a JSON file.» | да; формат экспорта прямо не назван, сохранение alias при экспорте не описано |
| REST API переменных — только Enterprise, полноправные участники; гостям нет | S | developers.figma.com/docs/rest-api/variables/ (смотрели 06.10.2026) | «To use this API, you must have a Full seat in an Enterprise org; guests cannot use the API.» | да |
| Code syntax: по одному имени для Web, Android, iOS; видно в сниппетах Dev Mode (CSS, SwiftUI, Compose); Dev Mode — на платных тарифах, Full или Dev seat | S | …/15145852043927; …/27882809912471 «Variables in Dev Mode» (28.10.2025); …/15023124644247 | «You can create one name per platform, including Web, Android, and iOS.» «code snippets for variables are supported in CSS, SwiftUI, and Compose» «Dev Mode is not available on the Starter plan.» | да |
| Selection colors группирует цвета выделения по переменным, стилям и обычным заливкам; на любом тарифе; только при смешанных заливках | J §5 | …/360042553434 (26.09.2025) | «Figma groups colors by variable, style, and normal fills, and each fill only appears once.» | да |
| Extended collections — для нескольких брендов, Enterprise; своих переменных и режимов не добавить | S | …/36346281624471 (03.09.2026) | «Extended collections help you manage multi-brand design systems.» «Available on the Enterprise plan» | да |
| Публикация переменных в библиотеку — Education и платные тарифы | M/S | …/15339657135383 (20.11.2025) | «publishing variables to team libraries are available on the education plan and any paid plans» | да |
| Переменные в текстовых стилях | J §2 | …/15343107263511 | «You can also apply variables to properties in text styles and color styles.» | да |
| Check designs — находит вписанные цвета, текстовые стили, радиусы, отступы и предлагает переменную; Organization и Enterprise; в Dev Mode — Suggested variables | J §5 | …/39592284074263 «Check designs in Figma» (03.08.2026) | «Hard-coded values that can be replaced with variables or styles, such as: Colors, Text styles, Corner radius, Spacing and padding» «Available on Organization and Enterprise plans» | да |

## Формат токенов, сборщики, CSS (сверщик B)

| Утверждение | Урок | Источник | Цитата | Вердикт |
|---|---|---|---|---|
| Design Tokens Format Module 2025.10 — первая стабильная версия, 28.10.2025; отчёт сообщества, не стандарт W3C | S §1 | designtokens.org/TR/2025.10/format/; w3.org/community/design-tokens/2025/10/28/… | «This specification is considered stable.» «It is not a W3C Standard nor is it on the W3C Standards Track» | да; в уроке сказано «не стандарт W3C, а отчёт сообщества» |
| $deprecated — true/false или строка с пояснением; обязательно только $value | S §5 | там же, §5.2.4 | «deprecated AND this is an explanation» | да |
| Ссылка на токен — "{group.token}"; группа — объект без $value | S §2, §5 | там же, §7.1.1, §6.1 | `"$value": "{colors.blue}"` | да |
| Тип duration есть в формате | S §4 | там же, §8 | список типов: color, dimension, fontFamily, fontWeight, duration, cubicBezier, number, … | да |
| Цвет в 2025.10 — объект (colorSpace, components, hex) | S §2 | там же, модуль Color | — | в примерах урока цвета только ссылками, кода цвета в JSON нет |
| Resolver Module (темы, режимы) выпущен вместе с 2025.10 и стабилен | — | designtokens.org/TR/2025.10/resolver/ | «a method to work with design tokens in multiple contexts (such as "light mode" and "dark mode" color themes)» | в урок не взято |
| Style Dictionary 5.x; DTCG поддерживается с v4, версия 2025.10 — не полностью | S §1, §2 | styledictionary.com/info/dtcg/; npm 5.6.0 (03.10.2026) | «As of version 4, Style Dictionary has first-class support for the DTCG format.» «the latest format 2025.10 does not have full support yet» | да; оговорка в уроке |
| Сборка в CSS, iOS (Swift), Android (XML, Compose); name/kebab, name/camel, size/pxToRem | S §2 | styledictionary.com/reference/hooks/formats/predefined/, …/transforms/predefined/ | «Scales non-zero numbers to rem… otherwise 16 (default web font size) will be used» | да |
| Tokens Studio синхронизирует с GitHub, GitLab, Bitbucket, Azure DevOps, JSONBin, URL и др.; синхронизация папкой из многих файлов, ветки, темы — платные; DTCG включается в настройках, по умолчанию legacy | S §1 | docs.tokens.studio/token-storage/remote/; …/get-started/pro-licence; …/manage-settings/token-format | «Sync Tokens as a folder with multiple files» (pro); «The default is legacy format» | да; в уроке — «платные функции» без цен |
| Необъявленный var() без запасного: свойство как unset; у background начальное значение — transparent | M §4 | developer.mozilla.org …/var (10.09.2026); w3.org/TR/css-variables-1/; MDN background-color | «the property is treated as if it has value unset» «Initial value transparent» | да |
| 1rem — размер шрифта корня, обычно 16px, если пользователь не менял | S §2, §3 | developer.mozilla.org …/length (08.07.2026) | «A common browser default is 16px, but user-defined preferences may modify this.» | да; оговорка в уроке |

## Дизайн-системы и статьи (сверщик B)

| Утверждение | Урок | Источник | Цитата | Вердикт |
|---|---|---|---|---|
| Material 3: reference, system, component токены; md.sys.color.primary; компонентный токен кнопки | M §2 | JSON m3.material.io (контент 17.07.2026), таблица токенов | «There are three classes of tokens in Material» ; `md.comp.filled-button.container.color` — в наборе «[Deprecated] Button - Filled» | в уроке актуальное имя md.comp.button.filled.container.color |
| Atlassian: color.background.brand.bold.hovered; space.100 = 8px, space.200 = 16px | J §3, M §1–2 | atlassian.design/foundations/tokens/design-tokens; …/foundations/spacing; …/components/tokens/all-tokens | «space.100 … 0.5rem 8px» «space.200 … represents 16px» | да; утверждение «ролей отступам не заводит» снято — прямого высказывания нет |
| Nathan Curtis, «Naming Tokens in Design Systems», 15.10.2020: Namespace, Object, Base (category, concept, property), Modifier (variant, state, scale, mode — on-dark) | M §2 | medium.com/eightshapes-llc/naming-tokens-in-design-systems-9e86c7444676 (Wayback 02.01.2025) | «Modifier levels … variant (primary), state (hover), scale (100), and mode (on-dark)» | да; спор о режиме в имени назван в уроке |
| Nathan Curtis, «Space in Design Systems», 2016: inset, squish, stretch, stack, inline, grid | — | Wayback 03.01.2023 | «inset, inset squish, inset stretch, stack, inline, and grid» | в урок не взято |
| Термин «design tokens» — Jina Anne и Jon Levine, Salesforce | — | designtokens.org/TR/2025.10/; w3.org/community/design-tokens/2026/06/17/… | «the name comes from them (Jon & Jina)» | год 2014 первоисточником не подтверждён; в урок не взято |
| Gravity UI: темы light, dark, light-hc, dark-hc | — | github.com/gravity-ui/uikit | «`theme` values are `light \| dark \| light-hc \| dark-hc`» | в урок не взято |
| VKUI: базовые темы vkBase и vkBaseDark, --vkui--color_background_content | — | github.com/VKCOM/vkui-tokens; @vkontakte/vkui-tokens 4.93.0 | `--vkui--color_background_content: #ffffff;` | в урок не взято |
| Primer: токены в репозитории primer/primitives, собираются Style Dictionary | S §1 | github.com/primer/primitives README (05.05.2026) | «These tokens are compiled with style dictionary» | см. разбор чтения Senior |
