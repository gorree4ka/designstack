# Сверка фактов · уроки «Иконки и иллюстрации» · 29.09.2026

Проверено по первоисточникам 29.09.2026 двумя проверяющими (сеть не российская). Доступ из России — отдельным прогоном с сервера: 13 из 13 внешних ссылок открываются (`docs/research/ru-access/2026-09-29_16-14_icons.md`). Цен в утверждениях нет.

| № | Утверждение в уроке | Вердикт | Первоисточник |
|---|---|---|---|
| 1 | Material Design 2: холст 24, живое поле 20 × 20, отступ 2; опорные фигуры — круг 20, квадрат 18, прямоугольники 16 × 20 и 20 × 16 | подтверждено; в уроке оговорено «вторая версия», её больше не поддерживают | https://m2.material.io/design/iconography/system-icons.html |
| 2 | Material Design 2: иконки смотрят прямо, без наклона и объёма; правила показаны парами «так» и «не так» | подтверждено («Make icons face forward», «Don't tilt, rotate, or make icons appear dimensional») | там же |
| 3 | NN/g: почти всем понятны лишь дом, печать и лупа поиска, остальным иконкам нужна видимая подпись | подтверждено | Aurora Harley, «Icon Usability», 27.07.2014 — https://www.nngroup.com/articles/icon-usability/ |
| 4 | WCAG 2.2, 1.4.11 Non-text Contrast — AA, 3 : 1 для графики, нужной для понимания; 1.1.1 — декоративное скрывают от вспомогательных технологий | подтверждено | https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html · …/non-text-content.html |
| 5 | SVGOMG — интерфейс к SVGO; убирает служебные данные редактора и показывает результат рядом | подтверждено; автор Jake Archibald | https://jakearchibald.github.io/svgomg/ · https://svgo.dev/docs/introduction/ |
| 6 | Лицензии: Lucide — ISC (с частью под MIT от Feather), Tabler, Heroicons, Phosphor — MIT, условие — уведомление и текст лицензии во всех копиях | подтверждено | LICENSE в репозиториях lucide-icons/lucide, tabler/tabler-icons, tailwindlabs/heroicons, phosphor-icons/core |
| 7 | Material Symbols — Apache 2.0: приложить текст лицензии, пометить изменённые файлы | подтверждено; файла NOTICE в репозитории нет | https://github.com/google/material-design-icons · https://www.apache.org/licenses/LICENSE-2.0.txt |
| 8 | Remix Icon: с января 2026 года собственная лицензия; в продукте можно, продавать отдельным набором и делать на их основе свой набор нельзя; до этого Apache 2.0 | подтверждено; Remix Icon License v1.0, впервые в v4.9.0 (27.01.2026) | https://github.com/Remix-Design/RemixIcon/blob/master/License |
| 9 | Font Awesome Free: иконки — CC BY 4.0, указание автора уже стоит в комментариях скачанных файлов | подтверждено | https://fontawesome.com/license/free |
| 10 | unDraw: в коммерческом продукте без указания автора; нельзя раздавать наборами и воспроизводить сервис | подтверждено | https://undraw.co/license |
| 11 | Storyset: бесплатно при указании сайта как источника, без этого — подписка Flaticon Premium | подтверждено; в уроке исправлено с «Freepik» на «Flaticon Premium» | https://storyset.com/terms, раздел 6 |
| 12 | Humaaans и Open Peeps — CC0 | подтверждено | https://www.humaaans.com/ · https://www.openpeeps.com/ |
| 13 | CC BY 4.0 — указать автора, дать ссылку на лицензию, отметить изменения; CC BY-NC — только некоммерческое; CC0 не затрагивает права на товарные знаки | подтверждено | https://creativecommons.org/licenses/by/4.0/ · …/by-nc/4.0/ · …/publicdomain/zero/1.0/ |
| 14 | Heroicons: контурные 24 с линией 1,5, отдельные залитые наборы 20 и 16 | подтверждено | https://heroicons.com/ |
| 15 | Material Symbols: переменные оси, оптический размер от 20 до 48 | подтверждено; ось Grade у шрифта −50…200 (в урок не вошла) | https://developers.google.com/fonts/docs/material_symbols |
| 16 | Lucide: толщину линии можно зафиксировать в коде | подтверждено; свойство теперь `nonScalingStroke`, `absoluteStrokeWidth` устарело — в уроке исправлено | https://lucide.dev/guide/react/basics/stroke-width |
| 17 | Figma: обычное изменение размера сохраняет толщину линии, инструмент масштабирования (K) меняет её вместе с объектом | подтверждено | https://help.figma.com/hc/en-us/articles/360049283914-Apply-and-adjust-stroke-properties |
| 18 | Figma: слеш в имени раскладывает выгруженные файлы по папкам | подтверждено | https://help.figma.com/hc/en-us/articles/360040028114-Export-static-designs-from-Figma |
| 19 | Figma: свойство замены экземпляра (Instance swap), переменные цвета на штрихе | подтверждено | https://help.figma.com/hc/en-us/articles/5579474826519-Explore-component-properties · …/15343107263511-Apply-variables-to-designs |
| 20 | Lucide: чек-лист для присылающих иконку — зачем нужна, названа по изображённому, совпадает по размеру, плотности и оптическому весу; логотипы брендов не принимают | подтверждено | https://github.com/lucide-icons/lucide/blob/main/.github/pull_request_template.md · https://lucide.dev/brand-logo-statement |
| 21 | Material Symbols: логотипов сторонних компаний нет | подтверждено («due to legal reasons») | README google/material-design-icons |
| 22 | IBM: все присланные иконки проходят ревью перед публикацией | подтверждено | https://www.ibm.com/design/language/iconography/ui-icons/contribute/ |
| 23 | Atlassian: перед предложением иконки — вопрос, нужна ли она вообще; не рисовать новую, если подходящая есть | подтверждено | https://atlassian.design/foundations/iconography |
| 24 | Контраст на тёмной плитке (#0D1012, surface-scrim): точка #026172 — 2,69 : 1; акцент из токена — 3,80 (светлая тема) и 5,92 (тёмная); иконка #1A1C1F — 1,12 : 1 | посчитано по формуле WCAG самопроверкой урока | theme.json, тёмная тема `theme-dark.css` |
| 25 | Icon Utopia: статья о выравнивании по пиксельной сетке — целые координаты, размеры и толщины | подтверждено; автор Justas, 2015, обновлена 2020 | https://iconutopia.com/how-to-design-pixel-perfect-icons/ |

## Расхождения с карточками каталога — на решение заказчицы

- **Remix Icon** (`/resource/remix-icon/`): в карточке «набор открытый и бесплатный». С января 2026 года у набора собственная лицензия с запретами на продажу отдельным набором и на свой набор на их основе. Бесплатное использование в продукте осталось.
- **Storyset** (`/resource/storyset/`): в поле «цена» — «без указания — платная подписка Freepik». По условиям сайта это подписка Flaticon Premium.
