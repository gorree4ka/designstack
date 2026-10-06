# Сверка фактов · «Компоненты и варианты» J/M/S · 06.10.2026

Каждое утверждение уроков сверено с первоисточником двумя агентами-сверщиками 06.10.2026; сеть не российская (Казахстан).
Справка Figma читалась через API самого справочного центра (`help.figma.com/api/v2/help_center/en-us/articles/<id>.json`),
дата — `edited_at`, правка текста. Material 3 — из JSON, который сайт m3.material.io загружает сам (контент от 23.09.2026,
токены кнопок — версия 38.2.9 от 10.08.2026). Списки «Что почитать дальше» — `docs/research/reads/components-variants-*.md`.

## Figma

| Утверждение в уроке | Урок | Источник | Цитата | Вердикт |
|---|---|---|---|---|
| Экземпляр связан с главным компонентом и получает его правки | J §2 | help.figma.com/…/360038662654 (03.08.2026) | «Instances are linked to the main component and receive any updates made to the component.» | да |
| Правки в экземпляре остаются, когда главный меняют; в справке — overrides | J §2 | …/360039150733 «Apply changes to instances», раздел «Change preservation» (18.06.2026); …/360038665934 (25.04.2025) | «Overrides allow you to make superficial changes to instances» | да, как поведение; прямой фразы нет — в уроке без кавычек |
| Отвязать — Detach instance, Ctrl+Alt+B (Mac ⌥⌘B); привязать обратно нельзя | J §2 | …/360038665754; …/39635555294743 (17.04.2026) | «Remove the link to the original component.» «once an instance is detached, it can't be reconnected» | да |
| Варианты собирают в набор (component set), имя слоя «Свойство=Значение» | J §3 | …/360056440594 (14.08.2026) | «Figma places variants in a single container called a component set.» «Property1=value, Property2=value» | да |
| Новое свойство Figma называет «Property 1», значения — «Variant2», «Variant3» | J §4 | …/39712951432343 (17.04.2026) | «a new component property called Property 1 … with default and Variant2 as available values» | да для «Add variant»; при «Combine as variants» первое свойство — «Variant» |
| Свойства компонента: переключатель, текст, замена вложенного экземпляра, вариант и слот | J §3 | …/5579474826519; …/38231200344599 (28.09.2026) | «Create a flexible area in a component where you can add, edit, and rearrange content.» | да, слот без пометки beta, на всех тарифах |
| Различия в содержимом решают свойствами, «не умножая число нужных вариантов» | J §3 | …/39747637290263 «Components collection: Tips for component management» (20.04.2026) | «Use component properties to handle changes at the content-level, without multiplying the number of variants needed» | да; в уроке названа эта статья |
| Называть компонент тем, что он есть, а не тем, как выглядит; сверять имена с кодом | J §4 | …/39747637290263 | «name components what they are, not how they currently appear»; раздел «Align names with your codebase» | да |
| Auto layout: Hug contents, наименьшая ширина (min width) | J §5 | …/360040451373 (02.10.2026) | «Add min width and Add max width» | да |
| Select matching layers, Ctrl+Alt+A, выделяет одинаковые слои | J §6 | …/360040449873 | «Matching objects are identical layers that exist across more than one frame or group.» | да — одинаковые, а не похожие; в уроке так |
| Обновление библиотеки владелец файла просматривает и принимает сам | S §4 | …/360039234193 «Review and accept library updates» (08.09.2026) | «Click Update next to an individual asset, or Update all to apply all updates.» «Available on any paid plan» | да |
| Удаление главного компонента не убирает экземпляры из файлов | S §4 | …/360038663154 | «Deleting a main component does not remove instances of that component from your files.» | да |
| Аналитика библиотеки: экземпляры, где стоят, отвязки; тарифы Organization и Enterprise | S §3 | …/360039238353 (27.08.2026) | «Available on the Organization and Enterprise plans.» «Detaches: The number of times someone has detached…» | да |
| Что будет с экземплярами при удалении варианта или переименовании свойства | — | — | в справке не описано | в урок не берём |

## Material 3, VKUI

| Утверждение | Урок | Источник | Цитата | Вердикт |
|---|---|---|---|---|
| Состояния: enabled, disabled, hover, focused, pressed, dragged | M §1 | m3.material.io/foundations/interaction/states/overview (17.07.2026) | шесть состояний на вкладке Overview; activated и selected — отдельно | да |
| Слой состояния: наведение 8 %, фокус 10 %, нажатие 10 % | M §1 | …/states/state-layers | «Hover +8% opacity Focus +10% opacity Press +10% opacity Drag +16% opacity» | да |
| Неактивная кнопка: подложка 10 %, подпись 38 % цвета on-surface | M §3 | m3.material.io/components/buttons/specs, токены 38.2.9 | `md.comp.button.filled.disabled.container.opacity` = 0.1, `…label-text.opacity` = 0.38 | да; 12 % — только в устаревших наборах |
| VKUI Button: mode primary, secondary, tertiary, outline, link; size s, m, l; appearance accent, positive, negative, neutral, overlay | J §4 | vkui.io/components/button/ (v8.4.1, 24.09.2026) | «"link" \| "primary" \| "secondary" \| "tertiary" \| "outline"» | да |

## Доступность и HTML

| Утверждение | Урок | Источник | Цитата | Вердикт |
|---|---|---|---|---|
| 2.4.7 Focus Visible, уровень AA | M §2 | w3.org/TR/WCAG22/#focus-visible | «Any keyboard operable user interface has a mode of operation where the keyboard focus indicator is visible.» | да |
| 2.4.11 Focus Not Obscured (Minimum), AA, новый в 2.2 | M §2 | …/#focus-not-obscured-minimum | «the component is not entirely hidden due to author-created content» | да |
| Состояния элемента — 3 : 1, неактивные исключены | M §2–3 | …/#non-text-contrast; Understanding 1.4.11 | «except for inactive components» | да |
| Текст неактивного элемента не требует контраста | M §3 | …/#contrast-minimum | «Text … that are part of an inactive user interface component … have no contrast requirement.» | да |
| disabled — нет фокуса и не уходит с формой | M §3 | developer.mozilla.org, атрибут disabled | «disabled controls cannot receive focus and are not submitted with the form» | да |
| aria-disabled оставляет элемент в порядке фокуса | M §3 | developer.mozilla.org, aria-disabled | «they will not be removed from the focus order of the web page» | да |

## GOV.UK, semver, жизненный цикл компонентов

| Утверждение | Урок | Источник | Цитата | Вердикт |
|---|---|---|---|---|
| Неактивных кнопок по возможности избегают | M §3 | design-system.service.gov.uk/components/button/ | «Disabled buttons have poor contrast and can confuse some users, so avoid them if possible. Only use disabled buttons if research shows it makes the user interface easier to understand.» | да |
| Пример «Оплатить» без неактивной кнопки и ошибка после нажатия | M §3 | — | на странице GOV.UK нет; подход — у Виталия Фридмана (Smashing, 2021): «keeping the “Continue” button accessible at all times, and using the click to communicate… what’s actually wrong» | пример урока, атрибуция — Фридман |
| Защита от двойного нажатия; думать и о сервере | M §3 | там же | «set the data-prevent-double-click attribute to true»; «you should also think about the issue server-side» | да |
| У GOV.UK неактивная кнопка — прозрачность 50 % | M §3 | CSS сайта GOV.UK (читатель) | `.govuk-button[disabled]{opacity:.5}` | да |
| Разделы «When to use / When not to use» у Radios, Details, Tabs; у Button только «When to use» | M §5 | …/components/radios/, /details/, /tabs/, /button/ | заголовки страниц | да, в уроке не обобщено на все страницы |
| Критерии вклада: useful, unique; перед публикацией usable, consistent, versatile | S §1 | …/community/contribution-criteria/ | «proposals need to show that the component or pattern being suggested would be useful and unique» | да |
| semver: MAJOR — несовместимое, MINOR — новое совместимое, PATCH — исправления; устаревание — минорная | S §5 | semver.org | «It MUST be incremented if any public API functionality is marked as deprecated.» | да |
| Перед удалением в мажорной — хотя бы одна минорная с пометкой «устарело» | S §5 | semver.org, FAQ | «there should be at least one minor release that contains the deprecation» | да |
| Atlassian: «намерение вывести», потом «устарел»; без объявленного срока не убирают | S §4 | atlassian.design/release-phases | «No General Availability feature will be removed from the system without a clearly announced deprecation period.» | да |
| Primer: у устаревшего — описание замены и предупреждение | S §4 | primer.style/product/getting-started/component-status/ | «Documentation exists for the deprecation, including any alternative components to use instead. When using the component, a warning is shown to the consumer.» | да; статусы сейчас Experimental, Ready, Deprecated |
