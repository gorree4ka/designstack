# Конкурент: Refero (refero.design)

Дата разбора: 10.09.2026
Аналитик: Claude (Senior Product Designer / конкурентный анализ)
Метод: curl (страна IP того прогона не замерялась, O8 в `docs/DECISIONS.md`; адреса перепроверены 14.09.2026 с российского IP (RU, AS198610 Beget LLC) — `docs/research/ru-access/2026-09-14_12-05.md`, O8 закрыт) + веб-поиск.
Все факты — с URL; там где вывод мой, стоит пометка «оценка».

---

## Техническая база разбора

Refero — клиентский SPA на React (Create React App), **без SSR**: любой URL отдаёт один и тот же
HTML-каркас 4,6 КБ с общим `<title>Refero — UI/UX Design Inspiration for Your Next Project</title>`
и общим description (проверено: /pricing и /sitemap.xml побайтово идентичны каркасу главной, cmp → IDENTICAL).
Весь контент рисует бандл https://refero.design/static/js/main.ffc65e66.js (1,58 МБ).

- https://refero.design/robots.txt → 200: `User-agent: * Disallow:` (всё открыто), отдельно `User-agent: GPTBot Disallow: /`.
- https://refero.design/sitemap.xml → 200, но это HTML-каркас SPA, карты сайта фактически нет.
- Публичный API открыт без авторизации: https://api.refero.design/v1/... (проверено curl из РФ, 200). Все цифры ниже — оттуда.
- Роуты из бандла (React Router): /, /apps, /apps/:id, /apps/elements, /apps/pagetypes, /apps/patterns,
  /apps/search, /apps/search/flows, /elements, /elements/:id, /patterns, /patterns/:id, /pagetypes,
  /pagetypes/:id, /flows/:id, /flows/:id/:screenId, /screens/:uuid, /search, /search/flows, /research,
  /research/:id, /bookmarks, /:siteId-:domain, /ios-apps, /pricing, /checkout, /billing, /teams,
  /business, /mcp, /mcp/upgrade, /extended-trial, /affiliate, /referees, /mediakit, /how-it-works,
  /oauth/authorize, /stripe/callback.
- Позиционирование в og-теге: og:image:alt = "Refero — Design research for the AI era"; description:
  "The largest collection of UI/UX references and design inspiration for web and iOS. Explore tens of
  thousands of screenshots with advanced search capabilities".

---

## 1. Модель контента

**Типы записей** — все записи это скриншоты реальных продакшн-продуктов, не концепты:

- **Веб-экраны (desktop)** — полностраничные скриншоты сайтов. Всего **74 727 записей**
  (GET https://api.refero.design/v1/search → pagination.count = 74727, per_page 24, 3114 страниц).
- **Сайты (бренды)** — **427** (https://api.refero.design/v1/sites/available → count: 427).
  Это «родители» экранов: Wealthsimple, Stripe, Linear, Mercury, Wise, OpenAI, Faire, n8n и т. п.
- **iOS-приложения** — **303** (https://api.refero.design/v1/apps/available → count: 303),
  у каждого свои экраны, в записи есть store_url на App Store, иконка, фон.
- **Флоу** — последовательности экранов: роут /flows/:id/:screenId, у экрана в API есть flow_ids
  (напр. [8494, 8495]); отдельный поиск по флоу /search/flows и /apps/search/flows.
- **Элементы** (/elements), **паттерны** (/patterns), **типы страниц** (/pagetypes) — витрины по одной
  оси таксономии, а не самостоятельный контент.
- **Research** (/research/:id) — AI-режим: запрос к базе словами. Есть дневной лимит: строка из бандла
  «You've used all Research requests available today. Your limit will reset tomorrow.»
- Есть видео: в записях поиска присутствуют поля video_url и video_preview_url (анимации интерфейсов).

**Поля карточки в списке** (/v1/search, /v1/sites/available): thumbnail_url, preview_url, width/height,
single_screen (флаг «один экран» против длинной страницы), colors (5 доминирующих RGB), site с полями
domain, favicon_url, name, description, uuid. То есть в сетке видно только картинку и фавикон/домен
бренда — подписи «зачем это» нет.

**Поля карточки в детали** (GET https://api.refero.design/v1/screenshots/c72690ed-5480-4fd0-89c5-1a1cfbaf460c):
created_at (2025-11-09T10:25:52Z), полностраничный скриншот, нарезанный на тайлы .../0.jpg … N.jpg
(высота 18 808 px), preview_full_url, **page_url — ссылка на живую страницу**
(https://www.wealthsimple.com/en-ca), site (бренд), design_patterns (Email Subscription, Product
Features, Video Player), page_elements (Cards & Tiles, Button, Dropdown…), **fonts** (Futura PT,
Tiempos Headline), page_types (kind Marketing → Product Page & Landing, Home Page), flow_ids, colors,
bookmarked.

**Таксономия — три независимые оси плюс цвет и шрифт:**

- **Категории — 43** (https://api.refero.design/v1/categories/available), у каждой флаги
  mobile / desktop / marketing: AI Tool, Books, Business, Collaboration Tools, Communication Tools,
  Dating & Relationships, Design & Media Editing, Development Tools, Education, Electronic & Devices,
  Entertainment, Finance, Fitness, Food & Drink, Food Delivery, Fundraising, Health & Wellness,
  Home & Decor, Inspiration Board, Job Search, Kids, Lifestyle, Magazines & Newspapers,
  Map & Navigation, Marketplace, Music Streaming, News, Paperwork, Photo Stock, Portfolio,
  Productivity, Project Management, Real Estate, Reference, Scheduling Tools, Social Networking,
  Sports, Transport, Travel & Booking, Utility, Video Streaming, Weather, Web3 & Crypto.
- **Дизайн-паттерны — 87** в 8 группах, поле kind
  (https://api.refero.design/v1/design_patterns/available): page state (13: Empty State, Error,
  Loading & Connecting, Searching, Filter & Sorting, Success, Permission…), content (22: Kanban Board,
  Playlist, Testimonials, Suggestion & Similar Items, Checklist & To Do…), legal & other (14: Dark Mode,
  FAQ, Drag & Drop, Feedback & Survey…), social (13: Comments, Leaderboard, Reviews & Rating…),
  utility (14: AI Assistant, Calendar, Timer & Clock, Camera & Scanner…), commerce & finance (5:
  Billing & Plans, Payment Method, Trial & Freemium, Money Transfer, Shopping), marketing (5: Bento Grid,
  Email Subscription, Promo Code, Ads & Promo Offer, Product Features), onboarding (1: Quickstart Guide).
- **Элементы страницы — 69** в 6 группах
  (https://api.refero.design/v1/page_elements/available): layout (12: Table, Tree View, Carousel,
  Line & Bar Chart…), overlay (15: Bottom Sheet, Mega Menu, Notifications & Toast, iOS Alert…),
  input controls (14: Search Field, Wheel Picker, Switch & Toggle…), helper elements (11: Badge,
  Skeleton, Stepper, QR Code, Breadcrumb…), graphics (12: 3d Illustration, Gradient, Logo Wall…),
  bars (5: Footer, Navigation Bar, Sidebar & Drawer, Tabbar, Toolbar).
- У каждого паттерна и элемента в API есть **человеческое описание и синонимы (aliases)**: например у
  «Filter & Sorting» 14 алиасов — filter, sorting, organize, refine, narrow, arrange, categorize,
  prioritize, sort by, group, filter by, order, sift, rank. Это словарь, который кормит поиск.
- Дополнительные оси: **page_types** (kind Marketing и др.) и **fonts** (шрифты, распознанные на экране).

**Кто наполняет и как часто.** Публичной формы «предложить сайт» нет — строк Submit a site / Suggest
в бандле не найдено; запись создаётся автоматическим полностраничным скриншотом с последующей
разметкой по паттернам. Наполнение внутреннее, редакционно-роботизированное (оценка). Частота: в
выдаче соседствуют записи от 2022-06-11 и 2025-11-09, база явно пополняется постоянно (оценка).

**Даты.** created_at есть в API, но строк вида Added / Updated / Captured в интерфейсном бандле нет —
дату захвата пользователю, судя по всему, не показывают (оценка). Статуса «сайт жив / редизайн /
закрыт» нет вообще: page_url ведёт на живую страницу без какой-либо проверки актуальности.

**Похожие — есть:** GET /v1/screenshots/{id}/similar?page=N плюс отдельный appScreenshotsSimilar
для приложений; на детальной странице это блок похожих экранов с подгрузкой.

Что нам с этого: три независимые оси разметки (категория продукта × паттерн × элемент) со словарём
синонимов у каждого термина — готовая модель и для каталога ресурсов: «тип ресурса × задача ×
инструмент» плюс алиасы под поиск («фигма», «figma», «макет»). А их слабое место — ровно наши три
обещания: даты в UI нет, статуса ссылки нет, редакторского текста в карточке нет вообще (картинка и
авторазметка). Поле page_url без проверки живости — прямой контрпример к нашему «проверено 10.09.2026 /
работает / изменилось / закрыт».

---

## 2. Навигация и поиск

**Разделы** (роуты бандла): главная-лента веб-экранов /, мобильное — /ios-apps и /apps, витрины по
осям /patterns, /elements, /pagetypes (отдельно для приложений: /apps/patterns, /apps/elements,
/apps/pagetypes), поиск /search и /search/flows, AI-поиск /research, личное /bookmarks (папки, эндпоинт
/v1/bookmarks/folders), /teams, /business, /mcp, /pricing, /how-it-works, /mediakit, /affiliate.

**Фильтры.** Оси: категория, дизайн-паттерн, элемент страницы, тип страницы, цвет, шрифт, платформа
(desktop / iOS). Множественный выбор поддержан — в теле запроса массивы categories, design_patterns,
page_elements, sites. **В URL отражаются:** бандл формирует ключи q=, categories=, elements=,
patterns=, colors=, и API принимает их же. Проверено: https://api.refero.design/v1/search?query=pricing
→ count 6121 против 74727 без запроса, то есть фильтр реально сужает выдачу и ссылкой на выдачу можно
поделиться. **Но не индексируются:** SSR нет, у любого URL один и тот же title/description,
sitemap.xml — заглушка; ни одна страница фильтра в поиск не попадает.

**Поиск.** GET /v1/search?query=… Судя по словарю aliases у 87 паттернов и 69 элементов, поиск
семантический, по синонимам и описаниям, а не только по домену. Плюс отдельный AI-режим Research
(запрос словами → подборка, дневной лимит запросов).

**Пустая выдача.** Собственного текста «ничего не найдено, попробуйте…» в бандле не найдено
(Empty State там встречается только как название паттерна контента) — пустое состояние, судя по
всему, слабое (оценка).

**Сортировка.** Отдельного контрола нет: строк sort by / newest / popular в бандле нет. Порядок
ленты фиксированный, по релевантности и новизне (оценка).

**Пагинация.** API страничный (per_page 24, pagination.next), в UI бесконечная лента с подгрузкой
(?page=N у списков и у similar). Итого 3 114 страниц веб-экранов.

**Карточка — страницей, не модалкой:** у экрана свой URL /screens/:uuid, у шага флоу
/flows/:id/:screenId, у бренда /:siteId-:domain, у приложения /apps/:id. Ссылкой поделиться можно,
но из-за отсутствия SSR превью в мессенджере будет общей заглушкой Refero.

Что нам с этого: брать связку «фильтры живут в URL + у каждой записи собственный адрес» — она делает
подборки шарящимися. Но у нас WordPress отдаёт HTML на сервере, значит мы можем то, чего Refero не
может в принципе: превратить пересечение фильтров в индексируемую посадочную страницу («инструменты
для прототипирования, которые работают из России») с уникальным title/description и OG-картинкой.
Это самый крупный незакрытый фланг конкурента.

---

## 3. Монетизация

**Бесплатный лимит.**
- Анонимно видно **12 экранов** в любой сетке (и **3** в режиме флоу), дальше заглушка
  «Log In or Sign Up to See All» с числом скрытых записей — код из бандла:
  `f.count>12 && <Mw screenshotsCount={f.count-(o?3:12)}>"Log In or Sign Up to See All"`.
- Time-limited триала нет, вместо него постоянный Free-план. FAQ дословно: «We do not offer a
  time-limited trial. The Free plan lets you explore Refero before upgrading.» При этом в продукте
  живёт баннер «3-day free trial, then $96/year ($8/month)» — то есть у Pro-подписки есть 3-дневный
  пробный период при оформлении.
- Free — feature-limited: «Upgrade your plan to unlock full access and keep using Refero»,
  «Upgrade to PRO», «Get unlimited access to everything».
- У AI-режима Research отдельный **дневной лимит запросов**: «You've reached your daily limit» /
  «You've used all Research requests available today. Your limit will reset tomorrow.»

**Цены** (из FAQ и UI-строк бандла main.ffc65e66.js; страница https://refero.design/pricing
серверно пустая, поэтому источник — бандл):
- **Pro**: баннер «3-day free trial, then $96/year ($8/month)». Месячная цена в бандле не зашита —
  приходит из API /v1/subscriptions.
- **Team**, за место: **$20/мес или $140/год** за 1–5 мест, **$18 / $130** за 6–10, **$16 / $120** за 11+.
  В UI цена показывается как «$X/seat/mo × N seats».
- **Lifetime**: разовая покупка на одного пользователя, без продлений, включает Pro + Refero MCP.
- **Enterprise**: по запросу (SSO, договор, DPA, приоритетная поддержка), контакт mike@refero.design.
- **Скидка студентам 40%** на месячный и годовой Pro (заявка через Google Forms,
  https://forms.gle/7b3aACXDeD9uEpFw6); Team и Lifetime под скидку не попадают.
- **Партнёрка**: 35% комиссии, «Each annual subscription sale could earn you approximately $42» —
  из чего следует чек годовой продажи около $120 (оценка: либо Pro подорожал со $96, либо считается
  по месту Team).
- Есть отдельный **Business-тариф** для случая, когда Refero питает клиентскую функцию продукта или
  данные перепродаются (роут /business, док https://doc.refero.design/mcp/business).

**Где стоит пейволл** (по возрастанию):
1. 12-й экран в любой сетке → регистрация (стена «See All»).
2. Полный полноразмерный скриншот, флоу целиком, закладки и папки → аккаунт.
3. Unlimited-доступ ко всей библиотеке, **Refero MCP** и Refero Skill → Pro / Team / Lifetime
   («Pro, Team, and Lifetime include Refero MCP for each licensed user»).
4. Research-запросы сверх дневного лимита → апгрейд.
5. Командные функции (общие закладки, места, роли) → Team.

**Чем платят.** В коде живут сразу три платёжных контура: **Stripe** (window.Stripe, роут
/stripe/callback, эндпоинты /v1/subscriptions/create_payment_intent и create_setup_intent,
/v1/users/payment_methods, /v1/users/customer_portal), **Paddle** (window.Paddle, Paddle.Setup
vendor 1897 — в бандле остался инициализатор с Environment.set("sandbox"), явно легаси) и
**Lemon Squeezy** (referodesign.lemonsqueezy.com — checkout, billing, affiliates).
Актуальный ответ FAQ говорит только про Stripe: «Stripe Checkout shows the payment methods available
in your location. Any applicable tax or VAT is calculated at checkout… Receipts and invoices are
available from the Billing page».

**Оплата из РФ — проверка 10.09.2026 через curl; страна IP не замерялась (O8 в `docs/DECISIONS.md`); адреса перепроверены 14.09.2026 с российского IP (RU, AS198610 Beget LLC) — `docs/research/ru-access/2026-09-14_12-05.md`, O8 закрыт:**
- Сам сервис **отвечает** на curl: https://refero.design/ → 200, CDN картинок
  https://images.refero.design/... → 200, документация https://doc.refero.design/legal/terms-of-use → 200.
  Гео-блока на чтение с этого IP нет; с российского IP не проверено.
- А вот **оплатить нельзя**: Stripe Checkout не принимает карты российских банков (Stripe не работает
  с РФ), Lemon Squeezy — merchant of record с теми же санкционными ограничениями. Зашитая в бандл
  ссылка на чекаут Lemon Squeezy
  https://referodesign.lemonsqueezy.com/checkout/buy/111728f4-59c4-404a-8e95-10f0f87037e1
  отдаёт **404** (редирект на /checkout); 11.09.2026 так же из Казахстана, значит ссылка устарела, а не закрыта для России. Итог: карты «Мир», карты РФ-банков и российские
  юрлица не проходят; вариант оплаты — только зарубежная карта или посредник (оценка на основании
  того, какие провайдеры используются).
- Про обходы сам сервис ничего не пишет; в поддержке предлагается только индивидуальный разбор
  возврата (support@refero.design).

Что нам с этого: Refero — идеальный пример карточки в нашем каталоге со статусом «работает, но из
России не оплачивается». Причём честно: смотреть и искать можно бесплатно, стена начинается с
12-й карточки — значит в нашей записи должно быть не бинарное «доступен/нет», а два поля:
«доступ» (открывается ли из РФ) и «оплата» (нет, Stripe/Lemon Squeezy), плюс «что доступно бесплатно»
(12 экранов, поиск, категории). Модель «12 карточек, потом регистрация» стоит взять как мягкую стену
для собственной подписки/рассылки — она не ломает первое знакомство. Ценовые ориентиры для нашего
«локального аналога»: $8–20 в месяц за место, то есть 800–2000 ₽ — вилка, с которой мы сравниваем.

---

## 4. Дистрибуция

**Рассылки нет.** В бандле нет ни одной формы подписки на письма, ни ссылки на Substack/beehiiv —
только строки о свежести контента: «New screens weekly: Last update <today / N days ago>»,
«Fresh updates weekly», «+ app screens, growing weekly». Заметьте приём: дата последнего обновления
базы **вычисляется на лету** и показывается на лендинге как «Updated today».

**Соцсети.** В коде единственная соцссылка — X: https://x.com/intent/follow?screen_name=referodesign.
Плюс встроенные твиты-отзывы как соцдоказательство на лендинге (twitter.com/apsayar/status/1647627431359004673,
/leogln/status/1640606149308186625, /olimermet/status/1638865858746363905, /dannlealweb/status/1723311865110188374).
Отдельная страница пресс-кита /mediakit и партнёрская программа /affiliate (35% комиссии,
https://referodesign.lemonsqueezy.com/affiliates, «The affiliate program is open to everyone, no matter
the size of your audience»).

**Каналы вместо SEO:**
- **Product Hunt** — ключевая площадка: продукт https://www.producthunt.com/products/refero,
  запуски Refero 2.0 и Refero 3.0 (по данным hunted.space у Refero 3.0 216 апвоутов и 37 комментариев,
  https://hunted.space/product/refero-3-0-2).
- **Figma-плагин** — «Figma plugin: All references directly inside Figma» (строка лендинга),
  дистрибуция через маркетплейс плагинов.
- **Refero MCP** (https://api.refero.design/mcp, роуты /mcp и /mcp/upgrade) и **Refero Skill** — доступ
  к библиотеке из Claude Code, Codex, ChatGPT и Figma-агентов. Это их главная ставка 2026 года:
  og:image:alt прямо гласит «Design research for the AI era», а слоган — «Real product screens, flows,
  and patterns to help designers, builders and AI make better design decisions».
- **Partner/affiliate + промокоды инфлюенсерам**: «Let's create offers that truly resonate with your
  followers… tailored promo codes and exclusive giveaways».

**SEO-форматы фактически отсутствуют.** Нет блога, нет статей, нет коллекций-лендингов, нет
серверных страниц категорий; sitemap.xml — заглушка; GPTBot закрыт в robots.txt (при том что сам
продукт продаётся как источник данных для ИИ-агентов — противоречие).

**Трафик (оценка, данные Similarweb за июнь 2026, получены через поисковую выдачу
https://www.similarweb.com/website/refero.design/competitors/):** ~**659,9 тыс. визитов в месяц**,
средняя длительность визита 2 мин 43 с, 4,33 страницы за визит, отказы 39,98%.
Источники: direct 57,65%, органический поиск 24,16%, переходы 8,44%, соцсети 5,05%.
Топ-регионы: **Индия 11,98%, США 10,60%, Россия 6,21%** — то есть порядка **40 тыс. визитов в месяц
из России** (оценка) на сервис, который из России нельзя оплатить.

Что нам с этого: 6,2% трафика Refero — это Россия, десятки тысяч визитов в месяц людей, которые
упираются в неоплачиваемый пейволл. Это наша аудитория и наш поисковый спрос: запросы вида «аналог
Refero», «как оплатить Refero из России», «Refero бесплатно» никем толком не закрыты, а сам Refero
на них не отвечает и ответить не может — у него нет ни блога, ни серверных страниц. Второе: 57%
direct при 24% органики означает, что рост идёт запусками (Product Hunt), плагином для Figma и MCP,
а не контентом; нам, наоборот, доступен именно контентный вход. Третье, прикладное: показывать
на витрине живую дату «обновлено сегодня» — дешёвый и сильный сигнал актуальности, берём.

---

## 5. Отзывы

**Product Hunt — https://www.producthunt.com/products/refero/reviews : 4,9 из 5, 16 отзывов.**

Похвалы:
1. Abhishek Dutta: «Best place to get design inspiration, why rely on Dribbble when you can get ideas
   from real products» — ценность именно в живых продуктах, а не в концептах.
2. Linh Hwang: «Pattern search feels grounded in real products, not just Dribbble-style shots» —
   поиск по паттернам воспринимается как рабочий инструмент.
3. Abhishek Gharat: «Love the filter functionality the most — very helpful and easy to navigate» —
   фильтры названы главной сильной стороной.
4. Maria Porto: «Excellent tool for designers… to study patterns and follow up with real world, live
   websites» — ценят возможность уйти на живой сайт.
5. Anton Sutarmin: инструмент помогает ответить на вопрос «какой UI-паттерн использует Google / Figma /
   Miro» и экономит время.

Жалобы:
1. Roman Kungurtcev: экраны не собраны в целостный пользовательский опыт — при фильтрации выдача
   мешает разные продукты без контекста последовательности.
2. Roman Kungurtcev (второй пункт): непонятно, **как часто библиотека обновляется, когда продукт
   меняет дизайн** — заменяется скриншот или сохраняется история. Ровно наша тема актуальности.
3. Shubham Anand: просит больше флоу приложений, прямо сравнивая с Mobbin.
4. Сводно по отзывам: хотят более точных тегов и более частых обновлений по мере изменения продуктов.

**Рунет.**
5. Хабр, «23 сервиса для поиска дизайн-референсов, о которых молчат на Dribbble»
   (https://habr.com/ru/articles/983608/): «100 000+ high-resolution (@2x) скриншотов web и iOS
   интерфейсов с AI-powered организацией контента»; плюсом названа lifetime-подписка — «В отличие от
   месячных подписок конкурентов, Refero предлагает lifetime опцию»; цена в статье указана как
   **€14/месяц или €250/пожизненно** (расходится с зашитым в бандл «$96/year ($8/month)» — либо
   разные тарифы/валюты, либо разное время; фиксируем обе цифры). Минусы по статье: «Меньше мобильных
   примеров, чем у Mobbin» и «Нет видеозаписей флоу».
6. vc.ru и dsgners.ru упоминают Refero в подборках как «аналог Mobbin с упором на веб-приложения,
   удобная фильтрация по компонентам (модальные окна, формы, навигация)»
   (https://vc.ru/design/1717080-ultimativnaya-podborka-dlya-poiska-referensov-chast-pervaya,
   https://dsgners.ru/screen-gallery/7773-ultimativnaya-podborka-dlya-poiska-referensov-chast-pervaya).
   Отдельная деталь: автор одной из подборок отмечает, что фильтры у Refero удобнее, чем у Mobbin.
7. Тема оплаты в рунете обсуждается вокруг всего класса сервисов: по Mobbin есть целые гайды
   «Как оплатить из России» через посредников (https://dtf.ru/howto/4013360-oplata-mobbin-v-rossii,
   https://vc.ru/services/2202088-kak-oplatit-mobbin-iz-rossii-cherez-payholder) — «оплата с российских
   счетов отклоняется… причина в санкциях, политике международных платёжных систем и региональных
   настройках биллинга». Специализированного гайда «как оплатить Refero из России» в выдаче нет —
   ниша пустая.
8. Свежий сигнал развития: разбор Refero Styles (библиотека DESIGN.md из реальных продуктов для
   AI-агентов, https://pimenov.ai/knowledge/refero-styles-biblioteka-design-md/) — Refero уходит в
   сторону данных для ИИ, а не картинок для людей.

Отдельно замечу: 16 отзывов на Product Hunt при 660 тыс. визитов в месяц — сообщества вокруг продукта
почти нет, обратная связь собирается слабо (оценка).

Что нам с этого: две главные жалобы на Refero — «нет контекста, зачем этот экран» и «непонятно,
насколько это ещё актуально» — это дословно два из трёх наших обещаний. Значит формулировать
преимущество надо не абстрактно («у нас курируют»), а ровно этими словами: «дата проверки у каждой
записи» и «оценка куратора: кому, за что, минусы». Третье: пустая ниша запроса «как оплатить/чем
заменить из России» — готовый контентный вход, но нам нужна не статья-однодневка, а поле в карточке,
которое отвечает на этот вопрос у каждого сервиса.

---

## 6. Флоу: главная → список с фильтром → карточка → переход

Оговорка о методе: сайт — SPA без серверного рендера, curl-ом интерфейс не снять, поэтому шаги
восстановлены по коду бандла (строки UI, компоненты, условия показа пейволла) и по встроенному
онбордингу с видео (https://images.refero.design/videos/onboarding/step-1040-264-1.mp4 и далее).
Всё, что не подтверждено строкой кода, помечено «оценка».

**Онбординг сам описывает модель взаимодействия** (6 шагов, дословно из бандла): «Searching by tag» —
«Click on the search box at the top of any Refero page to see finely curated tagging system with
categories like Page Types, UX Patterns, and UI Elements»; «Combine Tags» — «you can add both tags to
the "Product Page & Landing" and "Illustration" search box»; «Searching by Text Content» — «you can
also search for text content on a page… search for "Airbnb login"»; «Searching by Site» — «enter the
site's address or name»; «Switch between Web and iOS» — тумблер платформы; «Start Exploring».
То есть **одно поле поиска совмещает три разных механики**: теги, полнотекстовый поиск по содержимому
скриншота и поиск по домену.

### Шаг 1. Главная — бесконечная сетка скриншотов

Видно: masonry-сетка полностраничных превью (thumbnail_url), у каждого фавикон и домен бренда,
сверху поле поиска с тегами и тумблер Web / iOS. Кликается: карточка, тег, тумблер, пункты меню
(Patterns, Elements, Page Types, Flows, Bookmarks, Pricing). Пейволла на этом шаге нет.

- **Цель:** да, «посмотреть, как выглядят живые интерфейсы» решается сразу — сетка и есть продукт.
- **Обнаружимость:** сетка очевидна, но **что именно перед глазами — непонятно**: нет ни счётчика
  «74 727 экранов», ни объяснения принципа отбора; в карточке нет ни названия страницы, ни даты.
- **Связь действия с целью:** клик по картинке очевидно ведёт к большему изображению — связь прямая.
- **Обратная связь:** есть только визуальная (карточка подсвечивается); что «карточка = страница
  сайта, а не работа дизайнера» — приходится догадываться (оценка).

Нарушения эвристик:
- «Видимость статуса системы» — пользователь не знает, где он в выдаче и сколько всего записей.
  **Severity 2.**
- «Соответствие системы реальному миру» — карточка без подписи не отвечает на вопрос «что это за
  экран»; связь скриншота с задачей дизайнера не проговорена. **Severity 2.**

### Шаг 2. Список с фильтром — теги в поле поиска

Видно: то же поле поиска, в котором висят выбранные теги; выдача сужается (проверено на API:
query=pricing → 6 121 из 74 727). Кликается: добавить/убрать тег, ввести текст, сменить платформу.
Параметры уходят в URL (q=, categories=, elements=, patterns=, colors=).

- **Цель:** «найти экраны с онбордингом в финтехе» решается, если пользователь догадался, что теги
  живут внутри поля поиска.
- **Обнаружимость:** **главная проблема** — фильтр не выглядит фильтром. Нет привычной панели
  фасетов слева с чекбоксами и счётчиками; всё спрятано в комбо-поле, и именно поэтому продукту
  понадобился видеоонбординг из шести шагов, объясняющий, как пользоваться поиском. Необходимость
  обучать базовому действию — сама по себе диагноз.
- **Связь:** сочетание тегов из трёх разных словарей (Page Types + UX Patterns + UI Elements) в одном
  поле не даёт понять, что с чем комбинируется по «И», а что по «ИЛИ» (оценка).
- **Обратная связь:** выдача перестраивается, но **счётчика найденного рядом с фильтром нет**
  (в коде количество используется только для текста стены «See All»), и нет кнопки «сбросить всё»
  (строки Clear all / Reset в бандле не нашлось).

Нарушения:
- «Распознавание вместо припоминания» — теги надо вызвать и вспомнить, вместо того чтобы увидеть
  список осей с количеством. **Severity 3.**
- «Свобода и контроль» — нет явного сброса фильтров и внятного «шага назад» в комбинированном поле.
  **Severity 2.**
- «Помощь и документация» вместо простоты интерфейса: шестишаговый видеотур подменяет понятный
  контрол. **Severity 2.**
- Пустая выдача: собственного текста «ничего не найдено, ослабьте фильтр» в бандле нет —
  «Помощь в распознавании и исправлении ошибок». **Severity 3** (оценка).

### Шаг 3. Стена на 12-й карточке

Видно: после 12-й карточки (в режиме флоу — после 3-й) сетка обрывается плашкой
«Log In or Sign Up to See All» с числом скрытых записей. Код: `f.count>12 && <Mw
screenshotsCount={f.count-(o?3:12)}>«Log In or Sign Up to See All»`. Кликается: регистрация/вход.
**Здесь первый пейволл** — регистрационный, не денежный.

- **Цель:** цель пользователя (посмотреть ещё) прерывается ровно в тот момент, когда он понял
  ценность — момент выбран грамотно.
- **Обнаружимость:** стена заметна, показ числа скрытых записей («ещё N») — сильный приём, он
  количественно объясняет, что теряешь.
- **Связь:** «зарегистрируйся → увидишь всё» читается однозначно.
- **Обратная связь:** после входа возврат в ту же выдачу (оценка); но **цена дальнейшего шага не
  названа** — что регистрация всё равно упрётся в Pro-подписку, на этом экране не сказано.

Нарушения:
- «Видимость статуса системы» / честность воронки: бесплатная регистрация выдаётся за доступ «ко
  всему» (See All), хотя полный доступ платный. **Severity 3.**

### Шаг 4. Карточка экрана — /screens/:uuid

Видно: полноразмерный скриншот, собранный из тайлов (у примера — 2732×18 808 px, 20+ файлов
`.../0.jpg … N.jpg`), сбоку/снизу — бренд с фавиконом и описанием, теги трёх осей (design_patterns,
page_elements, page_types), распознанные шрифты, палитра из 5 цветов, кнопки Download / Share /
закладка, блок «похожие» (/v1/screenshots/{id}/similar) со своей стеной «Log In or Sign Up to See All
Similar…». У страницы собственный URL — ссылкой делятся.

- **Цель:** «разобрать чужое решение» — да, и очень предметно: видно шрифты и цвета, которых нет ни
  у кого из конкурентов в таком виде.
- **Обнаружимость:** теги на карточке кликабельны и ведут в выдачу — хороший «горизонтальный»
  переход. Но **даты нет**: created_at (в примере 2025-11-09) в API есть, а в интерфейсе строк
  Added/Updated/Captured нет — пользователь не знает, свежий это скриншот или трёхлетний
  (в базе соседствуют записи от 2022-06-11). **Это ровно та жалоба, что звучит и в отзыве
  Roman Kungurtcev на Product Hunt.**
- **Связь:** непонятно, что делать с находкой дальше, кроме «скачать» — редакторского вывода
  («почему это решение работает, где оно ломается») нет вообще.
- **Обратная связь:** закладка требует аккаунта, скачивание — подписки (оценка); отклик на клик по
  тегу мгновенный.

Нарушения:
- «Видимость статуса системы» — нет даты и нет пометки «страница с тех пор изменилась».
  **Severity 3.**
- «Согласованность и стандарты» — тайловая склейка длинной страницы даёт медленную и рваную
  прокрутку на длинных лендингах (18 808 px = 20+ запросов картинок). **Severity 2** (оценка).
- «Эстетичный и минималистичный дизайн» — карточка целиком отдана картинке, а смысловой слой
  (зачем смотреть, что перенять) отсутствует. **Severity 2.**

### Шаг 5. Переход на живой продукт

Видно: page_url ведёт на исходную страницу (в примере https://www.wealthsimple.com/en-ca).
Кликается ссылка на сайт/App Store (store_url у приложений).

- **Цель:** «посмотреть вживую» решается одним кликом — сильная сторона.
- **Обнаружимость:** ссылка есть, но не выделена как главный следующий шаг (оценка).
- **Связь:** прямая — скриншот и живая страница один объект.
- **Обратная связь:** **никакой проверки, что ссылка ещё жива и что страница не переехала**.
  Пользователь узнаёт о редизайне или 404 уже на чужом сайте.

Нарушения:
- «Помощь в распознавании и восстановлении после ошибок» — битые и устаревшие переходы никак не
  помечены. **Severity 3.**

### Шаг 6. Денежный пейволл

Видно: модалка/портал «Upgrade to PRO», «Upgrade your plan to unlock full access and keep using
Refero», «Get unlimited access to everything», «Once the payment is completed, you'll regain full
access to all pro features!»; для Research — «You've reached your daily limit… Your limit will reset
tomorrow»; на тарифах — «3-day free trial, then $96/year ($8/month)» и «$X/seat/mo × N seats».
Оплата уходит в Stripe Checkout.

- **Цель:** «продолжить работу» — упирается в оплату, и **для пользователя из России здесь тупик**:
  карты РФ Stripe не принимает, а альтернативы (Lemon Squeezy) — тот же санкционный контур;
  зашитая ссылка на чекаут Lemon Squeezy отдаёт 404 — 11.09.2026 так же из Казахстана, ссылка устарела.
- **Обнаружимость:** цена показана до оплаты, отдельный /pricing с FAQ есть — прозрачно.
- **Связь:** апгрейд действительно снимает ограничение.
- **Обратная связь:** **об отказе оплаты по региону система заранее не предупреждает** — узнаёшь
  только на форме Stripe, потратив время на регистрацию и подбор тарифа.

Нарушения:
- «Помощь в распознавании и исправлении ошибок» + «Видимость статуса» — регион, из которого оплата
  невозможна, не обозначен нигде до формы оплаты. Для российского пользователя это провал сценария
  в самом конце воронки. **Severity 4.**
- «Гибкость и эффективность» — нет ни локальных способов оплаты, ни разовой покупки контента,
  только подписка/Lifetime. **Severity 3** (для РФ-аудитории).

Что нам с этого: главный вывод по флоу — у Refero отличная «горизонтальная» механика (теги на
карточке ведут в выдачу, «похожие» удерживают) и очень плохая смысловая: ни даты, ни статуса, ни
вывода куратора. Берём: стену с числом скрытых записей («ещё 312 записей») и кликабельные теги на
карточке. Не повторяем: спрятанный в поле поиска фильтр без счётчиков (severity 3), отсутствие даты
и статуса ссылки (severity 3), и главное — умолчание про невозможность оплаты из региона до самой
формы оплаты (severity 4). У нас об этом должно быть сказано в карточке, до всякого клика.
