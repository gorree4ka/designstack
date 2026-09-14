# Toools.design — конкурентный разбор

Дата: 10.09.2026. Метод: WebFetch/curl страниц сайта, sitemap.xml, исходник `/finder`, Product Hunt, Similarweb, поиск. Пометка «оценка» — вывод аналитика, не подтверждённый источником напрямую. Reddit недоступен для загрузки инструментом; vc.ru/search отдаёт 404 — что не найдено поиском, так и помечено.

## 0. Паспорт

- URL: https://www.toools.design/ . Владелец и единственный сотрудник — Pascal Strasche (product designer, Webflow-разработчик, indie maker; https://www.pascalstrasche.com/ , LinkedIn компании «1 employee» — https://www.linkedin.com/company/tooolsdesign).
- Запуск на Product Hunt 17.02.2022, 286 апвоутов, #7 дня — https://www.producthunt.com/products/toools-design/launches/toools-design
- Стек (из исходника https://www.toools.design/finder): Webflow CMS; кастомный JS-«finder» поверх self-hosted Meilisearch (`HOST = "https://search.pascal-strasche.de"`, `INDEX = "tools"`); поисковые запросы логируются в n8n-вебхук (`https://n8n.pascal-strasche.de/webhook/finder-log`); Google Analytics (gtag). Подключён Jetboost, но фильтрация в finder — своя.
- Рост базы: 900+ (2022, Dribbble) → 1,000+ (06.2023, AlternativeTo) → 1,500+ (описание на PH) → 2,000+ (/sponsor) → 2,200+ (главная, 09.2026).

## 1. Модель контента

**Типы записей.** Один основной тип — «ресурс/инструмент» (карточка-ссылка без собственной страницы). Вспомогательные: блог-посты (13, `/blog-posts/*`), выпуски рассылки (27 URL `/newsletter/*` в sitemap), купоны (`/deals`, 11 штук), ролевые подборки (`/for/*`, 8 штук). Sitemap содержит 75 URL и ни одного URL уровня «инструмент» — https://www.toools.design/sitemap.xml . Детальных страниц у записей нет вообще.

**Поля карточки.** Из запроса finder к Meilisearch: `attributesToRetrieve: ["name", "description", "url", "logo", "category", "pricing"]` — это и есть вся модель данных записи. В списке видно: логотип, название, описание (лимит формы предложения — «0 / 120 Max Characters», https://www.toools.design/suggest-a-tool), ценовая метка, бейдж «Partner*». «В деталях» — ничего, деталей нет.

**Ценовые метки (6):** Free, Freemium, Free + Paid, Free Trial, Paid, Beta. Распределение на https://www.toools.design/ai-design-tools (подсчёт по HTML): Freemium 154, Paid 33, Free 29, Free + Paid 28, Free Trial 26, Beta 7; бейджей Partner* — 36.

**Таксономии.**
- 18 категорий первого уровня (меню): AI Tools, Inspiration, Icons, Illustrations, Mocks + UI Kits, Stock Photos, Learning, Community, Blogs & Mags, Podcasts, Books, Productivity, Design Tools, UX Tools, Color Tools, Typography, Marketing, Web Builders.
- Подразделы внутри категории — якорные секции на странице: у Design Tools 14 (Design & Prototyping, Design System & Styleguides, Brand Management, Vector, Photo & Image, DTP, Motion, Video, 3D, Architecture & Interior, Presentation, Image Optimization, Generative & Experimental, Useful Helpers — https://www.toools.design/best-design-tools), у Typography 10 (Font Inspiration, Free Fonts & Libraries, Pairing, Pro Fonts & Foundries, Editors, Managers, Finders, Type Scale Calculators, Experimental, Additional — https://www.toools.design/font-library-and-inspiration). На PH в 2022 заявлено «18 categories and 88 subcategories».
- Вторая ось — 8 ролей: `/for/ui-designers`, `/for/ux-designers`, `/for/product-designers`, `/for/web-designers`, `/for/graphic-designers`, `/for/brand-designers`, `/for/motion-designers`, `/for/marketing-designers`.
- Третья ось — pricing. Платформа, лицензия, язык/кириллица, регион — отсутствуют (страница шрифтов: поддержка языков на карточках не указана).

**Число записей.** Заявлено «2,200+ design resources». Мой подсчёт уникальных внешних ссылок по 18 категорийным страницам — 2,361 (одна запись может стоять в нескольких категориях): AI Tools 281, Design Tools 260, Inspiration 209, Marketing 182, Web Builders 172, Typography 132, Illustrations 130, Books 121, Learning 114, UX Tools 113, Color 106, Productivity 105, Icons 85, Podcasts 78, Mockups 76, Stock 73, Blogs 69, Community 55. Заявка подтверждается.

**Кто наполняет.** Редакция из одного человека. UGC — форма https://www.toools.design/suggest-a-tool без регистрации: обязательны URL, название, описание ≤120 символов; опционально категория, pricing, email, сообщение. Модерация: «TOOOLS.design is carefully curated. Only design-related and genuinely useful tools will be considered after review»; срок: «If it's a match, it may take anywhere from a few days to several weeks to be published». Вендоры попадают через платные размещения (/sponsor) и партнёрки.

**Частота.** «Weekly updated for the community» (главная); рассылка каждый вторник; лента новых — https://www.toools.design/latest-resources (Show More + стандартная Webflow-пагинация).

**Даты.** Даты добавления или проверки нет ни на одной карточке. Проверено curl-ом по главной, `/latest-resources`, `/ai-design-tools`: 0 совпадений по паттернам «Added/Updated/Last checked» и датам. Единственный способ узнать «свежесть» — попасть в верх ленты `/latest-resources` или в выпуск рассылки.

**Мёртвые ссылки.** Политики нет, статуса «работает/закрыт» нет, в полях Meilisearch нет поля статуса. Оценка: куратор чистит вручную и молча; пользователь никогда не видит, что запись проверялась.

**Альтернативы на карточке.** Нет. Единственный «соседний» механизм — блок «Explore More» с перекрёстными ссылками на другие категории внизу категорийной страницы.

**Что нам с этого:** модель Toools — «ссылка + 120 символов + ценник». Наши три обещания (дата проверки/статус, доступность из РФ + аналог, редакторская оценка «кому/за что/минусы») — ровно те поля, которых у лидера ниши нет; их надо делать полями записи, а не текстом в описании, чтобы фильтровать и показывать в списке. Лимит 120 символов на описание — хороший дисциплинирующий приём для списка, но у нас должна быть и детальная страница.

## 2. Навигация и поиск

**Разделы первого уровня.** 18 категорий в меню + Newsletter, Blog, Deals; иконка поиска ведёт на `/finder`. В футере: Advertise (`/sponsor`), Suggest a tool, Affiliate disclosure, Legal, Privacy. На главной отдельный блок «Designer Toolkits» — 8 ролей.

**Два режима списка.**
(a) Категорийная страница — один длинный документ: 260–280 карточек в крупных категориях (`/ai-design-tools` — 298 КБ HTML), подразделы с якорным оглавлением; фильтров нет, сортировки нет, пагинации нет — всё на одной странице. Порядок внутри подраздела редакторский (Figma первая) — оценка. Спонсорская секция «Featured …» стоит первой.
(b) `/finder` — поле «Search TOOOLS.design» (autofocus) + две группы чекбоксов «Pricing:» (6) и «Category:» (18) + «Clear all». Чекбоксы → множественный выбор (оценка по типу `<input type="checkbox">`). Результаты по 40 (`var PAGE = 40`) + «Show More». Поиск полнотекстовый по name/description (оценка по составу индекса), Meilisearch по умолчанию терпит опечатки — оценка. Подсказок/автокомплита нет. Сортировки нет (в запросе к Meilisearch нет `sort`). Счётчика результатов нет (элемент `data-finder="count"` в шаблоне отсутствует). Состояние фильтров и запроса **не отражается в URL** — в коде нет `URLSearchParams`/`location.search`, `history.pushState` используется только для якорей → фильтрованные выдачи не индексируются, ссылкой не поделиться, кнопка «назад» теряет состояние. Ролевого фильтра в finder нет — роли только как отдельные страницы `/for/*`.

**Пустая выдача.** Текст «No Tools Found ...» + кнопка «Suggest a tool». Нет ни «сбросить фильтры», ни «похожие», ни подсказки по опечатке; кнопка «Show More» остаётся в разметке (оценка).

**Ролевые страницы `/for/*`.** «A hand-curated collection of the best interface design resources», ~100+ ресурсов в 10 разделах по стадиям работы: inspiration → tools → assets → fonts → color → patterns → blogs → podcasts → courses → books (https://www.toools.design/for/ui-designers). Ближайший аналог нашего сценария «набор для старта», но без выделения «обязательного минимума».

**Карточка.** Не открывается ни страницей, ни модалкой — клик уходит сразу на внешний сайт: `https://www.figma.com?ref=toools`, `https://mobbin.com/...?via=toools`, партнёрские — через редиректы (`framer.link/design_via_toools`, `go.streamlinehq.com/tooolsdesigntypography`). Из главной до внешнего сайта — 2 клика (категория → карточка), через finder — 3 (иконка → ввод/фильтр → карточка).

**Что нам с этого:** фильтры обязаны жить в URL (страницы вида «бесплатные UI-киты с кириллицей» — это и есть наш поисковый трафик); нужен счётчик результатов и умная пустая выдача («снять фильтр X», «показать аналоги»). Якорное оглавление длинной категории — приём хороший, но при 250+ карточках без фильтра не спасает; у нас категория должна быть отфильтрована по умолчанию хотя бы по «работает из РФ».

## 3. Монетизация

**Бесплатно:** всё для читателя — каталог, finder, рассылка, блог, deals. Пейволла и регистрации нет.

**Платно (для вендоров), https://www.toools.design/sponsor:**
- Homepage Feature — $200 за 4 недели, «150–300 clicks from high-intent visitors».
- Category Page Feature — цена по запросу, 4 недели, «100 to 1,000 clicks depending on the category».
- Newsletter Spotlight — $100 за выпуск, $175 за 2, $325 за 4; «image, description, and a link», «One sponsor per issue, no competing placements».
- Заявленная аудитория: ~40K уникальных/мес, 200K+ просмотров/мес, рассылка «3,700+ people every Tuesday», «47.1% open rate, 8.8% click rate».
- Контакт sponsor@toools.design; способ оплаты не раскрыт.

**Партнёрские ссылки.** https://www.toools.design/affiliate-disclosure : «Tools or sections with affiliate links are clearly marked as '*', 'PARTNER*', or 'AMAZON*'»; «fewer than 2% of listed tools include affiliate links»; «Every tool on this site is held to the same curatorial standard, whether it has an affiliate program or not»; партнёрства «may influence positioning but never determine inclusion»; участник Amazon Associates. Факт: на `/ai-design-tools` 36 Partner* из ~280 (≈13% — больше заявленных 2%, потому что партнёрки концентрируются в дорогих категориях); на `/for/ui-designers` Partner* у Mobbin, Framer, UICONS, Untitled UI, Beyond UI, Landify, Uxcel, Designlab, Coursera, IxDF. На странице шрифтов карточка Streamline подписана «Sponsor».

**Спонсорские блоки на главной:** «Featured Design Tools» (4), «Top Partner Picks» (10), «Partner AI Picks» (11), «Handpicked Partner Discounts» (6) — помечены словом Partner в заголовке секции и «*» со сноской в футере «Partner links are affiliate links, which help support this website».

**Купоны** https://www.toools.design/deals — 11 штук: Framer Pro 3 месяца (`pro-yearly-partner`), Uxcel Pro −25%, IxDF 3 месяца, Squarespace −10% (`TOOOLS10`), SaaSFrame −10%, LiveSurface −10%, Framify −30%, Pixelarticons −25%, Landify −10%, picjumbo −20%, Circum Icons Pro −10%.

**Из РФ.** Пользоваться — сайт открыт без гео-блока (проверено из US-окружения; из РФ не проверял — оценка: Webflow-хостинг из РФ доступен). Оплатить спонсорство — способ не объявлен, по переписке; оценка: счёт из Германии / PayPal / Stripe — российской картой не оплатить. Купоны — на западные сервисы (Framer, Squarespace, IxDF), оплата которых из РФ невозможна или затруднена; на карточках это никак не помечено.

**Что нам с этого:** модель «бесплатно для читателя, $100–200 за размещение вендору» работает при ~40K уникальных в месяц и одном человеке в штате — реалистичный ориентир. Прозрачность «Partner*» + отдельная страница disclosure — брать. Уязвимость Toools для нашей аудитории: их deals и партнёрские ссылки ведут на сервисы, которые из РФ не оплатить, — наша метка «оплачивается из России» превращает это в отличие.

## 4. Дистрибуция

**Рассылка.** «Join 3,800+ designers» (главная), «3,700+» (/sponsor); каждый вторник; формат — «2-minute read… No essays. No filler. Just new design and AI tools, handpicked reads and listens, the latest news, and one more thing» (https://www.toools.design/newsletter). На PH в 2022: «Weekly newsletter updates feature five curated resources». Архив на сайте — 24–27 выпусков с 31.03.2026 (sitemap: 27 URL `/newsletter/*`; оценка: веб-архив ведётся с весны 2026, сама рассылка старше). Платформа рассылки не раскрыта.

**Соцсети.** Instagram @toools.design — 26K подписчиков (поисковая выдача, оценка); X @TOOOLSdesign — 617; LinkedIn — 948. Telegram-канала нет. Основной канал — Instagram-карусели с подборками (оценка по формату аккаунта).

**SEO-форматы.**
- Слаги категорий заточены под запросы: `best-design-tools`, `best-ux-tools`, `best-color-inspiration-tools`, `best-design-podcasts`, `free-open-source-icon-libraries`, `free-open-source-illustrations`, `free-stock-images-videos`, `learn-ui-ux-design`, `best-no-code-website-builders`.
- Ролевые лендинги `/for/{role}-designers` — «Resources & Tools for UI Designers».
- Блог (https://www.toools.design/blog): 13 постов, 11 в формате «Best X» («9 Best AI Tools for UI+UX Designers in 2026: Deep Dive», «50 Best Figma Plugins for Designers», «Ultimate List: 100 Best Inspiration Sites…», «Best MCP Servers for Designers…», «Best Online UX Design Courses in 2026: Ranked and Compared»), 1 «vs» («Webflow vs Framer in 2025: An Honest and In-Depth Comparison»), 1 обзор («IxDF … Just Reinvented Itself»), 1 подарочный гид. Формата «X alternatives» нет.

**Трафик (оценка).** Similarweb, август 2026 (https://www.similarweb.com/website/toools.design/): ~112.9K визитов, глобальный ранг #365,422; страны: Индия 23.3%, США 6.3%, Франция 4.3%, ЮАР 4.0%, Великобритания 3.9%; источники: Direct 54.4%, далее Organic Search и Gen AI; отказы 42.7%, 1.94 стр./визит, 46 сек. Собственная заявка: 40K уникальных / 200K+ просмотров в месяц (/sponsor) — согласуется (113K × 1.94 ≈ 220K просмотров). Hypestat/SEMrush (данные ~3.5-летней давности): ~1,042 органических визитов/мес по 2,121 ключам — устарело, но показывает, что органика исторически была слабой, основной трафик прямой и из соцсетей. Россия в топ-5 стран не входит.

**Что нам с этого:** короткая еженедельная рассылка «5 новых ресурсов + 1 вещь» с 47% open rate — формат, который стоит повторить дословно (наш дайджест — сценарий из брифа). Слаги категорий с «best/free» — брать для русских запросов («лучшие бесплатные UI-киты»). Обязателен формат «аналоги X» — у Toools его нет, а у нас это сценарий пользователя. Индия 23% при США 6% — англоязычные каталоги собирают трафик из «дешёвых» гео; русскоязычная ниша ими не покрыта вообще.

## 5. Отзывы

**Product Hunt** (https://www.producthunt.com/products/toools-design , /reviews): рейтинг 5.0 из 2 отзывов, 286 апвоутов, 68 подписчиков; maker активно отвечал в треде.

Похвалы (повторяющиеся темы: «красиво», «порядок», «много», «бесплатно»):
- «Best directory out there. Great selection of tools and very appealing to the eye» — Leon Jacken (@ljckn_), https://www.producthunt.com/products/toools-design/reviews
- «Toootally awesome!... the platform is so nicely designed, with such a nice and clear order» — Maria, комментарии к запуску на PH.
- «Clean UI and well-curated», «notably different from similar sites» — Kartik Dashasahastra, PH.
- «love this tool, I love using it» — M (@mcabrav), PH review.
- Awwwards включил в коллекцию «Handy Tools and Apps for Designers» — https://www.awwwards.com/inspiration/toools-design-design-resources-archive-newsletter

Жалобы: публичных жалоб не найдено.
- Reddit: поиск `site:reddit.com toools.design` и вариации — 0 тредов; прямая загрузка reddit заблокирована инструментом.
- vc.ru / Habr / Telegram: поиск «toools.design» по-русски — 0 упоминаний; статья vc.ru «29 инструментов и сайтов для дизайнера…» (29.10.2020) сайт не упоминает; vc.ru/search — 404.
- Medium-обзор Adam Hassini («Streamline Your Design Process with toools.design») — 403, не прочитан.
- AlternativeTo: 4 лайка, 0 комментариев (https://alternativeto.net/software/toools-design/about/).

Вывод: узнаваемость в русскоязычной среде отсутствует; вся публичная обратная связь — 4–5 коротких похвал 2022 года. Ни один отзыв не упоминает актуальность, проверку ссылок или оценки — этих свойств у продукта нет, и никто их пока не ждёт.

**Что нам с этого:** пустое поле отзывов — не «всё хорошо», а «никто не обсуждает». В русскоязычной среде Toools неизвестен, конкурировать придётся не с ним, а с Telegram-подборками. Наш способ получить отзывы — дать повод их писать: статус «закрыт/изменилось» и метка РФ обсуждаемы, «2,200 ссылок» — нет.

## 6. Флоу «главная → список с фильтром → карточка → переход»

Проход выполнен через WebFetch/curl (без JS-рендера; поведение JS-фильтра восстановлено по исходнику `/finder`).

**Шаг 1. Главная (https://www.toools.design/).** Видно: hero «Discover the Best Design Resources & Tools» / «A growing directory of 2,200+ design resources, weekly updated for the community»; меню из 18 категорий; иконка поиска (→ /finder); секции сверху вниз: Featured Design Tools (4, спонсорские), Latest Design Resources (16), Essential AI Tools (18), Must-Know Resources (10), Trending Blog Posts (10), Designer Toolkits (8 ролей), подписка «Join 3,800+ designers…» — плюс партнёрские вставки Top Partner Picks (10), Partner AI Picks (11), Handpicked Partner Discounts (6). Кликается: категории, любая карточка (сразу наружу), роли, посты.
- Цель: новичок поймёт, что это каталог, — да; но что делать первым (искать, листать категорию или взять «toolkit для роли») — три равноправных входа без подсказки. Частично.
- Обнаружимость: категории в меню заметны; поиск — иконка без поля на главной (`nav_search-field` на главной отсутствует, есть только ссылка на /finder) — слабо. Блок «Designer Toolkits» (самый полезный для junior) — в самом низу, после 8 секций. Слабо.
- Связь: карточка выглядит как элемент каталога, а уводит на чужой сайт — новичок ждёт «подробнее». Нет.
- Обратная связь: после клика — новая вкладка стороннего сайта; никакого «вы посмотрели / добавить в набор». Нет.

**Шаг 2а. Список: категория (https://www.toools.design/best-design-tools).** Видно: заголовок «Design Tools», интро, якорное оглавление из 14 подразделов, затем спонсорская секция «Featured …», затем 260 карточек подряд. Фильтров, сортировки, счётчика, пагинации нет.
- Цель: понять, что нужно прокрутить до нужного подраздела, — да, если заметить оглавление.
- Обнаружимость: оглавление заметно; фильтр по цене искать бесполезно — его нет; ценник на карточке заметен. Частично.
- Связь: якорь → прыжок к секции — да.
- Обратная связь: после прыжка позиция меняется, но активный пункт оглавления не подсвечивается (оценка по разметке). Слабо.

**Шаг 2б. Список: finder (https://www.toools.design/finder).** Видно: поле «Search TOOOLS.design» с автофокусом, группы «Pricing:» (6 чекбоксов) и «Category:» (18), «Clear all», сетка результатов по 40, «Show More».
- Цель: выбрать «Free» + «Icons» — да, интерфейс понятен.
- Обнаружимость: сам finder обнаружим только через иконку в шапке; для человека, зашедшего из поиска на категорию, finder невидим. Слабо.
- Связь: чекбокс → результат перерисовывается (JS) — да.
- Обратная связь: нет счётчика «найдено N»; URL не меняется; при 0 результатов — «No Tools Found ...» и «Suggest a tool» без совета снять фильтр. Слабо.

**Шаг 3. Карточка.** Карточка = логотип + название + ≤120 символов + ценник (+ Partner*). Отдельного экрана нет: клик = внешний переход. Модалки нет.
- Цель: понять, подходит ли инструмент, — нет: 120 символов и «Freemium» не отвечают на «кому/за что/минусы»; нет платформы, лицензии, региона, даты.
- Обнаружимость: ценник и Partner* заметны; смысл «*» — только через сноску в футере.
- Связь: пользователь не знает, что клик уводит наружу (иконки внешней ссылки в разметке не нашёл — оценка).
- Обратная связь: только новая вкладка.

**Шаг 4. Переход на ресурс.** `https://www.figma.com?ref=toools` / `?via=toools` / партнёрский редирект `framer.link/design_via_toools`. Промежуточной страницы нет, предупреждения о платности/регионе нет.

**Кликов до внешнего сайта:** 2 (главная → категория → карточка) или 3 через finder (иконка → фильтр → карточка). Пустая выдача бывает только в finder: «No Tools Found ... / Suggest a tool».

**Нарушения эвристик Нильсена (severity 1–4):**
1. H1 Видимость статуса — нет даты добавления/проверки и статуса «работает/закрыт» ни на одной записи; нет счётчика результатов в finder. **3** (для сценария «найти аналог закрытого сервиса» задача не решается; для просмотра — трение).
2. H3 Свобода действий — состояние фильтров/поиска не в URL: «назад» и обновление сбрасывают выборку, ссылкой не поделиться. **2**.
3. H6 Узнавание вместо припоминания — категорийная страница из 250–280 карточек без фильтра и сортировки; человек должен держать в голове, что искал, пока листает. **3**.
4. H8 Минимализм — главная: 8 контентных секций + 4 партнёрских блока, спонсорский «Featured» стоит выше «Latest»; самый полезный для новичка блок «Designer Toolkits» — последний. **2**.
5. H9 Помощь при ошибке — пустая выдача не предлагает снять фильтр/исправить запрос, только «предложить инструмент». **2**.
6. H2 Соответствие реальному миру — пересекающиеся метки «Freemium» и «Free + Paid» без объяснения разницы; «Free Trial» vs «Paid». **2**.
7. H4 Согласованность — три обозначения партнёрства («Partner*», «Sponsor», «AMAZON*»); разнобой слагов (`best-design-tools`, `ai-design-tools`, `font-library-and-inspiration`), опечатка в слаге `productivity-tools-for-design-and-poduct-teams`. **1**.
8. H7 Гибкость — нет сортировки, нет «сравнить», нет сохранения набора, нет альтернатив. **2**.
9. H10 Помощь — легенда ценовых меток и смысл «*» не объяснены рядом с карточкой (только в футере/на отдельной странице). **1**.
10. H5 Предотвращение ошибок — карточка не предупреждает, что ссылка внешняя и что сервис может быть платным/недоступным в регионе. **2** (для РФ-пользователя — 3).

**Что нам с этого:** копировать — плотную карточку (лого + имя + 120 символов + ценник) и «toolkit по роли» как вход для новичка, но поднять его на первый экран; ролевую и ценовую оси сделать фильтрами в URL. Не копировать — «карточка = внешняя ссылка»: наша редакторская оценка требует детальной страницы (или как минимум раскрывающейся карточки) с датой проверки, статусом, меткой РФ и аналогами. Пустая выдача обязана предлагать «снять фильтр» и «показать аналоги».
