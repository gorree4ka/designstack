# uxtools.co — конкурентный разбор

Дата: 10.09.2026. Метод: WebFetch/curl страниц сайта, sitemap.xml, HTML категорийных страниц базы инструментов, Product Hunt, Similarweb, поиск. Пометка «оценка» — вывод аналитика, не подтверждённый источником напрямую. Reddit недоступен для загрузки инструментом; vc.ru/search отдаёт 404 — что не найдено поиском, так и помечено.

## 0. Паспорт

- URL: https://www.uxtools.co/ (без `www` часть путей отдаёт 404). Основан в 2016–2017 Taylor Palmer и Jordan Bowman (первый запуск на PH — «The UX Library», 28.11.2016), с 2023–2024 принадлежит Tommy Geoco («Father of five, Marine veteran, and indie builder», https://www.uxtools.co/about); студия «Internet Enjoyers». Компания «2–10 employees», Phoenix, AZ (LinkedIn). Копирайт «© 2017 - 2025 UX Tools».
- Product Hunt: 5 запусков 2016–2021 (The UX Library; 2017/2018/2021 Design Tools Survey; UX Challenges) — https://www.producthunt.com/products/ux-tools ; тег «Compare UX design tools side-by-side» — то, чем сайт был до 2023.
- Стек: Framer (`framerusercontent.com`), рассылка через Kit (`kit.com` в форме на главной), отдельный сайт опроса survey.uxtools.co, медиакит — Figma-дека (https://www.figma.com/deck/LuHwIZWSiao3WMV9vASSXa/UX-Tools-Media-Kit-2025 — без JS не читается).
- Позиционирование сменилось: из «сравнилки инструментов» (2016–2022) в медиа «The Strongest Signal in Design Tools» — рассылка + подкаст + ежегодный опрос. Каталог инструментов теперь второстепенный раздел.

## 1. Модель контента

**Типы записей** (sitemap https://www.uxtools.co/sitemap.xml , 190 URL): статьи блога — 70; страницы отчёта опроса — 44 (`/survey/*`); эпизоды подкаста — 36; челленджи — 19; категории базы инструментов — 9 (`/tools/*`); бандлы/ивенты — `/bundle`, `/summer-bundle-2026`, `/detach-2026`; сервисные. Отдельных страниц у инструментов нет — только строки в категорийных таблицах.

**Поля записи «инструмент»** (https://www.uxtools.co/tools/design , разбор HTML: компоненты `Usage percent`, `Usage votes`, `Rating`, `Rating votes`, `Award Winner Badge`): логотип, название, «Usage 82.3% (1620)», «Rating 4.57 (1603)», бейдж «Award Winner» (у Figma и Framer в UI Design), ссылка наружу. Нет описания, цены, платформы, тегов, даты. Пример строки: «Figma Usage 82.3% (1620) Rating 4.57 (1603)». Данные — из 2024 Design Tools Survey (2,220 респондентов, ноябрь 2024 — январь 2025, https://www.uxtools.co/survey/introduction/about-this-report).

**Таксономии.** 9 категорий базы — по этапам работы: UI Design (`/tools/design`), Basic Prototyping, Advanced Prototyping, Portfolio Builders, Whiteboarding, User Testing, Research Recruiting, Research Repository, Design Systems. Отчёт опроса режет данные ещё по «Shapes of Work» — 7 сегментов: Corporate (1000+), Growth Company (101–1000), Startup (2–100), Agency, Independent/Solo, Educators/Researchers, Students (https://www.uxtools.co/survey/introduction/methodology). Ценовой оси нет, ролевой нет, региона нет.

**Число записей.** Подсчёт уникальных внешних ссылок по 9 категорийным страницам: 11 + 11 + 10 + 10 + 10 + 10 + 10 + 10 + 10 = **92 инструмента**. В отчёте показаны только инструменты с «≥0.1% usage». Это топ-10 по категории, а не каталог.

**Кто наполняет.** Данные — краудсорс через опрос (2,220 ответов 2024; «since 2017 over 22,000 designers»; «No compensation was offered»; отсев «>80% incomplete or… low-effort»). Набор инструментов и «Award Winner» — редакция. Формы «предложить инструмент» нет. Вендоры — спонсоры отчёта (Maze, Framer, UserTesting, Dovetail, Mobbin) с заявлением: «They have no influence over our methodology, analysis, or findings. We maintain complete editorial independence in all our reporting».

**Частота.** База — раз в год, по итогам опроса; на 10.09.2026 данным ~20 месяцев. Параллельно отдельный «State of Prototyping: Spring 2026» (1,478 ответов, 14.03–06.04.2026, https://survey.uxtools.co/spring-2026) — в базу инструментов не влит. Статьи — 1–4 в месяц (май 2026: 18.05, 12.05, 05.05), подкаст «State of Play» — еженедельно/раз в две недели (июль 2025 — август 2026, 40+ эпизодов).

**Даты.** На странице базы дата данных не подписана; в шапке пункт меню «2024 Design Tools Survey» — единственный намёк. Мета-дата публикации Framer «Aug 18, 2026» вводит в заблуждение (это дата деплоя сайта, не данных).

**Мёртвые ссылки.** Старые URL, на которые ссылаются PH и внешние сайты, отдают 404 без редиректа: `uxtools.co/tools/`, `uxtools.co/compare/`, `uxtools.co/survey/2024/`, `www.uxtools.co/compare`, `www.uxtools.co/tools`, `/manifesto`. `uxtools.co/compare-tools/` открывает главную. Ссылки на Adobe идут через партнёрскую сеть Tradedoubler (`clk.tradedoubler.com/click?p=264355&a=3244998…`).

**Альтернативы на карточке.** Прямых нет; сама категория — это и есть список альтернатив, ранжированных по доле использования и рейтингу.

**Что нам с этого:** крауд-метрики «доля использования + рейтинг (N голосов)» — сильный формат для нашей оценки «кому/за что», но у нас нет 2,000 респондентов; заменитель — редакторская оценка плюс лёгкий голос «пользуюсь / работает из РФ» без регистрации. 92 записи против наших планов — значит uxtools закрывает только «топ-10 по категории», а «найти UI-кит с кириллицей» они не покрывают вовсе. Данные годичной давности без подписи даты — образец того, чего нам нельзя: у каждой записи должна быть видимая дата проверки.

## 2. Навигация и поиск

**Разделы первого уровня** (меню): Design tools (→ `/tools/design`), Articles (`/blog`), Episodes (`/episodes`), Subscribe (`/newsletter`), UX Challenges (`/challenges`), 2024 Design Tools Survey (`/survey/introduction/about-this-report`), About, Community («Coming soon»). Поиска на сайте нет вообще. Фильтров нет ни на главной, ни в базе, ни в блоге (в блоге — теги-категории: Techniques, Tools, Collaboration, Research, Community, Branding, Interactions, Psychology, Communication, Portfolio).

**База инструментов.** `/tools/design` — «Design Tools Database»: переключатель 9 категорий (ссылки `./basic-prototyping` и т. д.), таблица из 10–11 строк, отсортированная по Usage по убыванию. Фильтров, поиска, сортировки, пагинации нет — не нужны при 11 строках. Состояние = URL категории (индексируется: страницы категорий есть в Google — «UX Tools - Design Tools Database - UI Design»). Пустой выдачи не бывает.

**Отчёт опроса** (`/survey/*`, 44 страницы): навигация «Next: Methodology» по разделам; на странице категории — «Figma vs. Legacy Tools» (доля/рейтинг), «Figma adoption by Work Shape», комментарий редакции: «86.7% of designers reported that changing design tools would be "difficult" or "very difficult"». Год-к-году, «would recommend», намерение сменить — не показаны.

**Челленджи** (`/challenges`): 19 заданий в 4 группах (Understand 5, Ideate 3, Test 5, Implement 5). Страница задания (https://www.uxtools.co/challenges/user-interview): бриф, шаги, deliverable, «Extra Credit», рекомендованные инструменты внешними ссылками (Miro, Notion, Dovetail, Zoom), 4 внешних туториала; без логина и оплаты; механизма сдачи работы нет.

**Карточка.** Не открывается — строка таблицы целиком является ссылкой на внешний сайт, `target="_blank"` (подтверждено в HTML): `https://www.figma.com/?ref=uxtools`, `http://penpot.app/?ref=uxtools`, Adobe — через Tradedoubler. Из главной до внешнего сайта — 2 клика (Design tools → строка); со сменой категории — 3.

**Что нам с этого:** «категория = URL = индексируемая страница-рейтинг» — правильно; для нас это значит, что каждый набор фильтров должен быть URL. Отсутствие поиска терпимо при 92 записях и смертельно при тысяче. Формат челленджа (бриф → шаги → результат → инструменты) — готовый шаблон для нашего сценария «набор для старта»: не список инструментов, а задача с набором под неё.

## 3. Монетизация

**Бесплатно:** база, отчёты опросов, блог, подкаст, челленджи, рассылка. Пейволла и регистрации нет.

**Платно / доход:**
- Спонсорство рассылки и опроса — медиакит (Figma-дека, недоступна без JS); цены не опубликованы. Спонсоры отчёта 2024: Maze, Framer, UserTesting, Dovetail, Mobbin; Spring 2026: Mobbin, Framer, Magic Path AI, dScout, Magic Patterns, Dazl. Пометка — только на странице «About this report», на строках базы спонсоры никак не помечены; «Award Winner» — редакционная награда, не реклама (оценка).
- «UX Tools Discovery Bundle» (https://www.uxtools.co/bundle) — «$129 one-time», «First 1,000 only · Ends Sept 17», промокоды на 3–6 месяцев Pro для 10 сервисов (Perplexity, Play, Jitter, Notion, Framer, Magic Patterns, Weavy, Granola, Bolt, Mobbin), «codes expire Jan 1, 2026» — страница 2025 года всё ещё в проде. Платёжный провайдер в HTML не виден (Stripe/Gumroad/Lemon Squeezy — 0 совпадений; оценка: кнопка ведёт на внешний checkout).
- «Summer Bundle 2026» (https://www.uxtools.co/summer-bundle-2026) — «$129, ONE-TIME», при этом на живой странице «PAYMENT RAILS PENDING», «DATE, PARTNER LIST, PLAN NAMES, AND EXPIRATION WINDOW PENDING».
- Ивент «DETACH 2026 — 25 Lusk, San Francisco», 18.08.2026 (https://www.uxtools.co/detach-2026): партнёрские перки Mobbin (3 месяца Pro, 500 кодов), Subframe, Spline/Omma, Lovable.
- Gumroad: «2021 Design Tools Survey Data» (https://uxtools.gumroad.com/l/ukYSD) — продажа сырых данных опроса (цена не загрузилась).
- Партнёрские ссылки: `?ref=uxtools` на всех строках, Adobe через Tradedoubler. **Дисклеймера нет нигде**: ни на странице базы, ни в Privacy & Terms (https://www.uxtools.co/privacy-terms — проверено, упоминаний affiliate/commission нет).

**Из РФ.** Читать — сайт открыт (проверено из US-окружения; из РФ не проверял). Оплатить бандл — способ не раскрыт; оценка: западный checkout, российской картой не оплатить; коды на Notion/Framer/Bolt из РФ тоже частично бесполезны. Спонсорство — по медиакиту, оценка: invoice в USD.

**Что нам с этого:** заявление о независимости от спонсоров, вынесенное в отчёт, — брать дословно как принцип. Скрытые партнёрские ссылки без disclosure — не повторять: наша метка «оплачивается из России» рядом с партнёрской ссылкой без честной пометки обнулит доверие. «Бандл промокодов за $129» — модель, недоступная нашей аудитории по оплате; если делать deals, то только на сервисы с оплатой из РФ.

## 4. Дистрибуция

**Рассылка.** Заявлено «Join 90k+ readers» (главная), «100K+ designers» (/newsletter, /about), «95K newsletter subscribers» (методология опроса 2024). Еженедельно; контент — «Tool breakdowns. Insider leaks. In-depth interviews. Early access to new tools». Платформа — Kit. Веб-архива выпусков нет (архив = статьи блога). Тестимониалы на странице: Michael Riddering (Dive Club): «One of the only design newsletters I open and read every…»; Femke van Schoonhoven (Gusto), Dan Mall (Design System University).

**Подкаст «State of Play»** (https://www.uxtools.co/episodes): ведущий Tommy Geoco, 40+ эпизодов, июль 2025 — август 2026, видео на YouTube @designertom; примеры: «Ridd: The Most Trusted Man in Design» (27.10.25), «Pietro Schirano: He Solved Figma-to-Code…» (09.02.26), «AI Made Junior Designers Look Like Most Seniors: Hannah Ahn» (05.05.26).

**Соцсети.** Заявка в методологии: «1M+ social followers (Instagram, YouTube, TikTok, LinkedIn, Threads)» — сумма аккаунтов бренда и лично Tommy Geoco (оценка). Проверяемое: LinkedIn UX Tools — 64,080; X @uxtoolsco — 6,764 (поисковая выдача). Telegram-канала нет (t.me/uxtools — чужой испаноязычный канал про веб-дизайн, к uxtools.co не относится).

**SEO-форматы.** Индексируемые страницы категорий базы («UX Tools - Design Tools Database - UI Design»), страницы отчёта опроса (44 — главный SEO-актив: запросы вида «figma market share», «design tools survey»), челленджи («Competitive Analysis - UX Tools»). Блог — эссе и «how to»: «How to share your design work in 2026», «Stochastic vs. Deterministic Design», «Your team isn't AI-installed», «17 Tools That Will Streamline Your UX Research» (2021), «33 Activity Ideas for Remote UX Workshops». Форматов «best X» и «alternatives» практически нет.

**Трафик (оценка).** Similarweb, август 2026 (https://www.similarweb.com/website/uxtools.co/): ~35.1K визитов, ранг #895,033; Индия 26.5%, США 21.3%, Германия 7.2%; Direct 53.6%, далее Organic Search и Organic Social; отказы 43.9%, 1.81 стр./визит, 29 сек; «decreased by 43.43% compared to last month». Собственная заявка: «450K annual website visitors» (≈37K/мес) — согласуется. Hypestat — данные 2016 года (358K/мес), нерелевантны. Вывод: сайт — не место потребления; аудитория живёт в рассылке и соцсетях, сайт даёт ~1/3 от Toools.design.

**Что нам с этого:** их актив — не каталог, а рассылка на ~95K и ежегодный отчёт, который цитируют («82.3%»). Нам стоит завести свой «отчёт»: ежеквартальный срез «что из инструментов работает из РФ» — цитируемый, индексируемый, привязанный к каталогу. Подкаст и 1M соцподписчиков — не повторить; Telegram-канал как замена рассылки — да.

## 5. Отзывы

**Product Hunt** (https://www.producthunt.com/products/ux-tools , /reviews): 5.0 из 2 отзывов (оба ~2023):
- «Amazing resources for designers and UXers. I have found the Design Tool Comparison report to be very intriguing and insightful.» — zuhaib ashfaq.
- «love the reports they've done!» — Adella Christina.

**Похвалы на сайте** (тестимониалы, 20+): «One of the only design newsletters I open and read every…» — Michael Riddering; Femke van Schoonhoven, Dan Mall и другие (https://www.uxtools.co/newsletter). Повторяющиеся темы: (1) отчёты/данные опроса, (2) рассылка «которую реально читают», (3) инсайды о новых инструментах.

**Жалобы/критика:**
- Сам Tommy Geoco: «Getting comments that I talk about AI too much. It's a topic that is hard to avoid lately…» — https://x.com/designertom/status/1906050404317794338 ; в подкасте Fuego UX по адресу критиков: «if you don't like it, tough shit» (https://www.fuegoux.com/podcasts/tommy-geoco-on-taking-the-content-creator-leap). Повторяющаяся претензия читателей — перекос в AI-повестку (по его же словам).
- Reddit r/UXDesign: тредов по «uxtools.co» / «Design Tools Survey» поиском не найдено; прямая загрузка reddit заблокирована. Hacker News — только обсуждения Figma без ссылки на опрос.
- vc.ru / Habr / Telegram: упоминаний uxtools.co или русских пересказов опроса не найдено; vc.ru/search — 404.
- Методологическая уязвимость (оценка, не цитата): выборка — «owned audiences» самого UX Tools (соцсети, рассылка, сайт), без компенсации; 61.4% респондентов Spring 2026 вне Северной Америки, но по регионам данные 2024 не раскрыты.

Вывод: публичных отзывов о самом каталоге нет — хвалят отчёты и рассылку; единственная известная претензия — «слишком много AI».

**Что нам с этого:** доверие uxtools держится на цифрах опроса и личном бренде ведущего — оба нам недоступны; наш эквивалент — прозрачная методика проверки («проверено 03.09.2026, оплата с карты Мир — работает»). Претензия «слишком много AI» — сигнал держать AI-раздел отдельной категорией, а не смешивать с базовым набором для junior.

## 6. Флоу «главная → список с фильтром → карточка → переход»

Проход выполнен через WebFetch/curl (Framer-сайт, статический HTML читается без JS).

**Шаг 1. Главная (https://www.uxtools.co/).** Видно: hero «The Strongest Signal in Design Tools» / «Insider leaks. Early access to tools. Deep dives on where design is going.» / форма подписки «Join 90k+ readers»; далее NEW RELEASES (4 статьи), NEWEST EPISODES (5), ARTICLES (6), ARCHIVES (10), 20+ тестимониалов; меню из 8 пунктов. Поиска нет. Ни одной карточки инструмента на главной.
- Цель: новичок, пришедший «найти инструмент», не поймёт, что это каталог, — экран продаёт рассылку. Нет.
- Обнаружимость: пункт «Design tools» — первый в меню, но единственный намёк на каталог; конкурирует с формой подписки в hero. Частично.
- Связь: «Design tools» → база? Название читается как «инструменты дизайна» (тема), а не «каталог». Частично.
- Обратная связь: после подписки — «thank-you»; после перехода в базу — смена страницы, заголовок «Design Tools Database». Да.

**Шаг 2. Список (https://www.uxtools.co/tools/design).** Видно: заголовок «Design Tools Database», подзаголовок «Explore real-world ratings and usage stats for UI design tools, trusted by thousands of designers», переключатель 9 категорий, таблица из 11 строк «Figma Usage 82.3% (1620) Rating 4.57 (1603)», бейджи «Award Winner». Фильтров, поиска, сортировки нет.
- Цель: понять, что это рейтинг по категориям, — да.
- Обнаружимость: переключатель категорий заметен; чего нет — так это цены, платформы, описания: новичок не поймёт, что такое «Proto.io» или «UXPin», не кликнув. Частично.
- Связь: «Usage 82.3% (1620)» — без подписи «из 2,220 респондентов опроса 2024»; «Award Winner» — без пояснения, за что. Слабо.
- Обратная связь: смена категории меняет URL и заголовок — да; но нет никакого признака свежести данных. Частично.

**Шаг 3. Карточка.** Строка = логотип + название + usage + rating (+ Award Winner). Отдельного экрана нет; вся строка — внешняя ссылка в новой вкладке.
- Цель: решить, подходит ли инструмент, — нет: неизвестны цена, платформа, минусы.
- Обнаружимость: что строка кликабельна и уводит наружу — не обозначено (нет «Visit», нет иконки; проверено по HTML — кнопок-лейблов нет). Слабо.
- Связь: пользователь ожидает «подробнее» и получает сайт вендора. Нет.
- Обратная связь: только новая вкладка. Нет.

**Шаг 4. Переход.** `https://www.figma.com/?ref=uxtools`, `http://framer.com/?ref=uxtools` (без https), Adobe — через `clk.tradedoubler.com` (партнёрский редирект без пометки).

**Кликов до внешнего сайта:** 2 (главная → Design tools → строка); со сменой категории — 3. Пустой выдачи не бывает (фильтров нет). Зато «пустая» ситуация — 404 на старых адресах `/tools/`, `/compare/`, `/survey/2024/`, `/manifesto`: стандартная Framer-404 без подсказки и редиректа.

**Нарушения эвристик Нильсена (severity 1–4):**
1. H1 Видимость статуса — данные базы без подписи года и размера выборки прямо на странице; мета-дата «Aug 18, 2026» противоречит реальным данным 2024. **3**.
2. H1/H5 — страница бандла 2025 с «Ends Sept 17… codes expire Jan 1, 2026» и страница Summer Bundle 2026 с «PAYMENT RAILS PENDING» открыты в проде: пользователь может пытаться купить несуществующее. **3**.
3. H3 Свобода действий — старые URL (`/compare/`, `/tools/`, `/survey/2024/`) — 404 без редиректа; человек из Google/PH упирается в тупик. **3**.
4. H2 Соответствие реальному миру — «Usage 82.3% (1620)» и «Award Winner» без пояснений на месте; «Design tools» как имя пункта меню для базы. **2**.
5. H6 Узнавание — строки без описания и цены: нужно помнить, что такое каждый из 11 инструментов. **2**.
6. H8 Минимализм — главная: 20+ тестимониалов, подкаст, статьи; каталог отсутствует на главной вовсе, хотя сайт исторически про сравнение инструментов. **3** для сценария «найти инструмент».
7. H7 Гибкость — нет поиска, фильтров, сортировки, сравнения (обещанное PH «side-by-side» удалено). **2**.
8. H10/этика прозрачности — партнёрские ссылки (`?ref=`, Tradedoubler) без какого-либо disclosure. **2**.
9. H4 Согласованность — часть ссылок `http://` (framer.com, penpot.app), часть `https://`; `www` vs без `www` ведут себя по-разному. **1**.
10. H5 — «Community: Coming soon» в основном меню; кнопка подписки на обновления сообщества без формы. **1**.

**Что нам с этого:** брать — «категория как индексируемая страница-рейтинг», числовую оценку с числом голосов, формат челленджа «задача → шаги → инструменты», явное заявление о независимости от спонсоров. Избегать — устаревших данных без даты (severity 3), мёртвых старых адресов при редизайне (нужны 301-редиректы), непомеченных партнёрских ссылок, витрины-медиа вместо каталога на главной, «Coming soon» в меню.
