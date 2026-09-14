> Отчёт субагента для `docs/research/grade-check.md`, 10.09.2026, перенесён без правок текста.
>
> **Сверка Claude в тот же день.** Все 60 ссылок отчёта скачаны заново и проверены скриптом. Из 171 фразы в «ёлочках» 9 — формулировки самого отчёта, а не цитаты. Из 162 цитат найдены в первоисточниках 159: 149 дословно, 3 с точностью до разметки, ещё 7 — через GitHub API (roadmap.sh), Europe PMC (Kruger и Dunning) и API Notion (страница Т-Банка). Не перепроверены 3 цитаты из баз Notion Т-Банка. Недоступность доменов app.vectorly.team и public.vectorly.team подтверждена. Сопоставление цен SkillsTeam с периодами оплаты отчёт делает по порядку блоков — не перепроверено, в выводы не берём.
>
> **Доступность из России в отчёте не проверялась.** Исходящий IP машины — не российский (см. O8 в `docs/DECISIONS.md`).

# Аналоги «проверки уровня» для дизайнеров интерфейсов

Дата проверки: 10.09.2026.

Как проверял. HTML каждой страницы скачан и просмотрен поиском по тексту. У SPA-страниц данные взяты из публичных JSON, которые эти страницы сами загружают: цены Uxcel, шаблоны Brimo, база Notion Т-Банка. Цитаты в «ёлочках» скопированы из HTML или PDF; пересказы WebFetch в кавычки не ставил. Если страница не открылась или факта на ней нет, пишу «не проверено». Что не открылось, перечислено в приложении Б.

Доступ из России во всех строках: «не проверено». Исходящий IP машины, с которой шла проверка, не российский (например, linkedin.com открылся с кодом 200). Поэтому доступность из РФ отсюда проверить нельзя.

Строки 3–5 (Progression, Vectorly, Brimo) добавлены по запросу: эти сервисы упоминает Ветров на dmpatterns.com/tools/skillknowledge.

## 1. Таблица аналогов

| № | Аналог и URL | Язык | Тип | Механика: что спрашивают, сколько, что на выходе | План и материалы | Дата у материалов | Цена и регистрация | Обновление | Лицензия | Из России |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Uxcel Pulse и Skill Graph — https://uxcel.com/assess-skills | EN | интерактивный тест | 25 вопросов на знания из пула 2000+, 6 категорий. На выходе Skill Graph и Design Score (100 баллов, сравнение с 500K+ дизайнеров). Грейдов junior/middle/senior нет | есть «custom plan» и рекомендации курсов, но только собственных курсов Uxcel | у курсов не проверено. Со временем помечается устаревшим сам результат | Starter бесплатно, тест входит. Pro 24 USD в месяц или 180 USD в год. Регистрация не проверена | не видна | не указана | не проверено |
| 2 | roadmap.sh, UX Design — https://roadmap.sh/ux-design | EN | интерактивная карта-план, не тест | 94 темы, есть AI Tutor и Personalize. Уровня на выходе нет, квиза по UX нет | план = сама карта. У каждой темы ссылки на статьи и видео | у ссылок дат нет | карта открывается без входа. Цена AI-функций не проверена | репозиторий обновлён 10.09.2026 | запрещает переиспользование (только личное) | не проверено |
| 3 | Progression — https://progression.co/ (редирект с progressionapp.com) | EN | B2B-сервис карьерных фреймворков и check-ins | самооценка сотрудника и оценка менеджера по навыкам фреймворка: working towards / meeting / exceeding, затем согласование. На выходе сильные стороны и зоны роста | зоны роста есть. Ссылки на материалы не проверены | не проверено | Platform и Grow: «Talk to Us», цены нет. Бесплатный тариф есть, лимиты не проверены. Нужна регистрация | шаблоны дизайн-команд 03.05.2023 | не указана | не проверено |
| 4 | Vectorly — https://vectorly.team/ | EN (обзоры на RU) | B2B-сервис матриц и 360-ревью | самооценка + ревьюер или 360, уровни noob … master. Грейд считается автоматически | до 5 навыков на цикл и ссылки на материалы из базы знаний компании | не проверено | пробный период $9 за 14 дней. Annually, 10 пользователей: $5 / $9 / $14 per user / month (3 тарифа) | «© 2022», домены приложения не резолвятся | не указана | не проверено |
| 5 | Brimo — https://brimo.one/ | EN (шаблон Ветрова на RU) | B2B-сервис карт компетенций | ревью навыков руководителем, грейды, треки, цели. Шаблон «Дизайнер»: 60 навыков, 4 уровня владения, 496 критериев-артефактов, 10 грейдов | цели и трек есть. В шаблоне 0 материалов; ИИ-подбор книг и статей пока в «Future features» | нет | Free до 3 пользователей ($0). Enterprise без цены. Нужна регистрация | шаблон обновлён 06.11.2025 | не указана | не проверено |
| 6 | GitLab, Product Designer — https://handbook.gitlab.com/job-families/product/product-designer/ | EN | открытая матрица (job family) | обязанности и требования по 5 уровням, от Product Designer до Distinguished. Ссылка на таблицу Job Levels | нет | — | бесплатно, без регистрации | 19.07.2026 | не указана, на странице «All Rights Reserved» | не проверено |
| 7 | GOV.UK DDaT, Interaction designer — https://ddat-capability-framework.service.gov.uk/role/interaction-designer | EN | открытая матрица (госфреймворк) | 6 уровней роли × 7 навыков × 4 уровня владения (Awareness → Expert) | нет | — | бесплатно, без регистрации | 28.08.2026 | OGL v3.0: можно и коммерчески, с указанием источника | не проверено |
| 8 | progression.fyi — https://progression.fyi/ | EN | сборник открытых матриц | 75 фреймворков, у 21 есть дизайн-категории (Figma, Intercom, Monzo, Zendesk, UX Skills Matrix от Loblaw Digital и др.) | нет | — | бесплатно | не видна | у сборника не указана | не проверено |
| 9 | Figma, Product Design & Writing Career Levels и виджет Skills Chart — https://www.figma.com/blog/figma-design-team-career-levels/ | EN | открытая матрица + виджет самооценки в FigJam | 4 категории: Product Strategy, Collaboration, Craft, Impact. Виджет для самооценки и ревью. Число уровней не проверено | в статье нет | — | не проверено (страницы Community не открылись) | статья 23.03.2023 | не проверено | не проверено |
| 10 | Miro, Design Skills Matrix — https://miro.com/templates/design-skills-matrix/ | EN | шаблон самооценки | ставишь себе баллы по навыкам и выбираешь, что улучшать. Шкала не проверена | ссылки на курсы и книги вписывает сам пользователь | нет | не проверено | не видна | не указана | не проверено |
| 11 | Грейд-детектор от Pragmatica — https://t.me/seniordesigner_bot | RU | Telegram-бот, тест-квест | 11 ситуационных вопросов. На выходе градация грейдов, заявленная точность 92% | в статье нет | — | цена не указана, нужен Telegram | статья 17.11.2022 | не указана | не проверено |
| 12 | ToolFox, тест UI/UX-дизайнера — https://toolfox.ru/tools/ui-ux-design-test | RU | интерактивный тест знаний | 20 вопросов по 6 направлениям. На выходе общий уровень (от Новичка до Эксперта) и проценты по категориям | общие советы, что подтянуть; ссылок на материалы нет | — | бесплатно, без регистрации | не видна | не указана | не проверено |
| 13 | Skillbox, бесплатный мини-курс UX/UI — https://bootcamp.skillbox.ru/uxui | RU | входной тест в мини-курсе | тест определяет уровень знаний; число вопросов не проверено | бот подбирает материалы и задания мини-курса Skillbox | нет | бесплатно, запись через форму | не видна | не указана | не проверено |
| 14 | Авито, матрица компетенций дизайнеров — https://github.com/avito-tech/playbook/blob/master/design-levels.md | RU | открытая матрица | 4 уровня × 16 критериев, описано поведение на каждом уровне | нет | — | бесплатно, без регистрации | последний коммит по файлу 04.07.2025 | не указана (у репозитория нет лицензии) | не проверено |
| 15 | Т-Банк, матрица навыков — https://habr.com/ru/companies/tbank/articles/689214/ + Notion | RU | открытая матрица + шаблон самооценки | самооценка + оценка тимлида. Ранняя шкала 0–3; в Notion 27 утверждений-поведений и 13 дополнительных навыков | задания и чек-листы перехода Beginner → Medium → Hard → God, в основном внутренние | нет | бесплатно, без регистрации | Notion правился 25.09.2023 | не указана | не проверено |
| 16 | Магнит, карта навыков — https://habr.com/ru/articles/852706/ + Google Sheets | RU | открытая матрица + шаблон | 119 навыков в 6 категориях, шкала 0–4 по тому, как навык проявляется. Самооценка + калибровка лидом, грейд по порогам | ссылок на материалы не нашёл | — | бесплатно, без регистрации | 23.10.2024 | не указана | не проверено |
| 17 | SkillsTeam, матрица UX/UI-дизайнера — https://skillsteam.ru/designer | RU | B2B-сервис грейдов + шаблон матрицы | 120 навыков, 9 грейдов (junior-1 … senior-2). У навыка есть поля «Как защитить» и «Как принимать» (тестовые задания). Роли: руководитель, наставник, сотрудник; есть ИПР | компания сама прикрепляет к грейду ссылки на материалы | нет | тариф «Команда» (до 50 пользователей): 14 900 ₽ за 1 месяц. Шаблон присылают на e-mail | не видна | не указана | не проверено |

## 2. Детали по аналогам

### 1. Uxcel Pulse и Skill Graph
- URL: https://uxcel.com/assess-skills, справка: https://help.uxcel.com/en/articles/10484277-how-to-build-and-maintain-your-design-score-and-skill-graph, тарифы: https://uxcel.com/pricing
- Механика. В тесте 25 вопросов («It is made up of 25 questions»), они берутся из «2,000+ question pool» и покрывают «over 100 UX design & product skills». Design Score описан так: «a 100-point metric that compares your design skills, knowledge, and capabilities with 500K+ designers worldwide». Грейдов junior/middle/senior на проверенных страницах нет.
- План. Главная страница обещает: «In just 15 minutes, get your Skill Graph and a custom plan to grow your skills and career.» В справке — «receive tailored course recommendations». Рекомендуются только курсы из собственной библиотеки: «learning library of 60+ courses», «8 guided career paths».
- Актуальность. Датируется не материал, а результат пользователя: «Over time, your reliability metric will naturally drop as new trends and knowledge are introduced.» Страницы курсов на даты не смотрел.
- Цена. Бесплатный Starter: «Access first levels of every course, take skill assessments, and join our Discord community.» Pro стоит 24 USD в месяц или 180 USD в год. Цифры взяты из публичного API https://api.uxcel.com/payments/public/pro-details — из него страница тарифов подставляет цены, в статическом HTML стоят нули. Пересдача: «Pro members get unlimited retakes; free users can retake every 7 days.» Оплата: «Pay securely with Visa, Mastercard, Google Pay, and Apple Pay.» Пройдут ли российские карты — не проверено.

### 2. roadmap.sh — UX Design
- URL: https://roadmap.sh/ux-design. Исходники и лицензия: https://github.com/nilbuild/developer-roadmap (старый адрес kamranahmedse/developer-roadmap перенаправляет сюда).
- Механика. Карта из 94 тем (файлы в папке roadmaps/ux-design/content), на странице есть «AI Tutor» и «Personalize». Теста уровня по UX нет: в списке квизов https://roadmap.sh/questions только разработка и данные (это видно через WebFetch).
- Материалы. Каждая тема заканчивается строкой «Visit the following resources to learn more:» и ссылками с пометкой типа, например «[@article@Business Model Canvas](https://www.interaction-design.org/literature/topics/business-model-canvas)». Дат проверки у ссылок нет. В подвале: «Community created roadmaps, best practices, projects, articles, resources and journeys».
- Лицензия запрещает переиспользование: «You are allowed to use this material for personal use but are not allowed to use it for any other purpose».

### 3. Progression (progressionapp.com → progression.co)
- URL: https://www.progressionapp.com/ отвечает 301 на https://progression.co/. Тарифы: https://progression.co/pricing/. Про check-ins: https://progression.co/blog/introducing-checkins/ (30.08.2019) и https://progression.co/features/check-ins/. Библиотека: https://progression.co/library
- Для кого. Сервис для команд и менеджеров («For managers and teams Have better career conversations»). Пользоваться одному можно, но с оговоркой: на вопрос «Can I use Progression on my own?» ответ «You can, using our free tier. However we recommend getting your manager involved too so you can ensure the framework you're using matches their expectations.»
- Механика. Check-in — это «an opportunity for a team member and manager to benchmark the team member's skills against those required of them by the framework». Шкала: «"working towards", "meeting" or "exceeding"». Процесс: «We ask the member and the manager to assess and then take them through a joint process where they reconcile any differences in assessment.» Результат — «a snapshot of how they compare against the framework and an indication of their strengths and growth areas». Привязан ли план к учебным материалам — не проверено.
- Шаблоны. В данных страницы библиотеки 159 записей от издателя Progression, в том числе шаблоны продуктовых дизайн-команд, например «Large Product Design Team» с описанием «Good for those looking to grow their product design team to 21+ people». На https://library.progressionapp.com/ шаблоны дизайн-команд обновлены 03.05.2023. «Skill matrix template» Ветрова в публичной библиотеке не нашёл: искал Vetrov, Ветров и skill matrix в HTML обеих страниц. Ссылка у Ветрова ведёт просто на главную.
- Цена. У тарифов Platform и Grow вместо цены стоит «Talk to Us». Бесплатный тариф упоминается, но его лимиты не проверены.

### 4. Vectorly
- URL: https://vectorly.team/, тарифы: https://www.vectorly.team/pricing. Обзоры: PINKMAN на vc.ru, 02.07.2020 — https://vc.ru/services/138900-kak-my-v-pinkman-ocenivaem-i-razvivaem-dizainerov-obzor-servisa-vectorly; SETTERS (дата не видна) — https://setters.education/blog/articles/kak-ocenivat-skilly-i-motivirovat-komandu-razvivatsya-opyt-setters-i-vectorly
- Для кого. Руководители команд: «Mentor your engineering team on autopilot with insights and recommendations». Дизайн-студии в обзорах используют его для дизайнеров.
- Механика. «Также по каждому из навыков дизайнер оценивает себя сам.» Уровни: «В Vectorly они по умолчанию называются noob, beginner, competent, advanced, master.» Грейд: «После ревью Vectorly высчитает грейд автоматически.»
- План и материалы. «Когда оценка проведена, вы можете выбрать до 5 навыков, которые сотруднику нужно развивать в следующем цикле и написать саммари. Дизайнеру сразу отправляются ссылки на те материалы из базы знаний, которые помогут в развитии по каждой компетенции.» База знаний у каждой компании своя. SETTERS: «Результатом ревью становится карта развития — это список навыков и материалов, которые помогают их прокачивать.»
- Цена. Пробный период «$9 for 14 days trial». При оплате Annually на 10 пользователей: Career Progression — $5 per user / month; Mentor & Grow (с «Growth plans» и «Learning recommendations») — $9 per user / month; People Ops Suite (плюс «Knowledge base») — $14 per user / month.
- Статус. В подвале «© 2022 Vectorly Inc. All rights reserved». Домены app.vectorly.team (кнопка входа) и public.vectorly.team (туда ведёт bit.ly-ссылка Ветрова на его шаблон) не резолвятся ни с этой машины, ни через WebFetch. Похоже, сервис не работает; стоит проверить вручную.

### 5. Brimo
- URL: https://brimo.one/. Шаблон Ветрова: https://brimo.one/cards/community/94. Страница — SPA, данные взяты из JSON https://brimo.one/api/cards/community/94, который она загружает. Английская версия шаблона: https://brimo.one/cards/community/417
- Для кого. Руководители и HR: «Brimo - Tool for teamleads and HR managers». Оценивает руководитель: «Select reviewees and start review to assess employee’s skills and provide valuable feedback». Грейды: «Allocate requirements from a skill map to each grade so your team members would know their grade within their team». Цели: «Choose a career track with your team member, define goals for them to achieve, and mark their achievements». Самооценка сотрудника на главной не описана.
- Шаблон «Дизайнер» (автор Yury Vetrov, пространство «Design Management Patterns»). 60 навыков в 16 группах и 3 категориях (Hard, Soft, Leadership). 4 уровня владения: Awareness, Ability, Expertise, Leadership. 496 критериев в виде артефактов, например «Создана карта сайта или приложения (1+ пример)». 10 грейдов — от Junior Product Designer до Design Director плюс ветка Communication Designer. 3 карьерных трека. Создан 11.04.2023, обновлён 06.11.2025, скопирован 135 раз.
- План и материалы. В шаблоне 0 материалов. Подбор чтения есть только в разделе «Future features in Brimo»: «AI will recommend books and articles to read to achieve next grade» (помечено Q3, год не указан).
- Цена. Бесплатный тариф: «Up to 3 users», «$ 0». Enterprise без цены. Регистрация: кнопка «Try for free» ведёт на /auth/start. В подвале «© 2026 LLC Brimo»; в отзывах «Art director Yandex», «Design Director Raiffeisen Bank».

### 6. GitLab — Product Designer
- URL: https://handbook.gitlab.com/job-families/product/product-designer/
- Механика. Уровни: Product Designer, Senior, Staff, Principal и Distinguished Product Designer. Для каждого описаны обязанности и требования и дана ссылка на таблицу Job Levels (Google Sheets). Самооценки, плана и учебных ссылок для дизайнера нет.
- Обновление: «Last modified July 19, 2026».
- Лицензия. На странице «© 2026 GitLab All Rights Reserved», Creative Commons в HTML не упоминается. LICENSE репозитория хендбука (https://gitlab.com/gitlab-com/content-sites/handbook/-/raw/main/LICENSE) — это MIT «With regard to the GitLab Software», к текстам он не относится. Вывод: лицензия контента не указана. Пересказ WebFetch упоминал CC BY-SA, но в исходном HTML этого нет.

### 7. GOV.UK DDaT — Interaction designer
- URL: https://ddat-capability-framework.service.gov.uk/role/interaction-designer
- Механика. 6 уровней роли, от Associate до Head of interaction design. 7 навыков: Design communication, Designing for everyone, Designing strategically, Designing together, Evidence-based design, Iterative design, Leading design. 4 уровня владения: «Awareness is the first of 4 ascending skill levels», затем Working, Practitioner, Expert.
- Плана и учебных ссылок на странице роли нет. Обновление: «Last updated 28 August 2026».
- Лицензия: «All content is available under the Open Government Licence v3.0, except where otherwise stated». По тексту OGL v3.0 (https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) материал можно копировать, адаптировать и использовать в том числе коммерчески, если указать источник.

### 8. progression.fyi
- URL: https://progression.fyi/
- Состав: «Displaying 1 - 75 of 75 in total»; «Progression.fyi is a collection of public and open source career frameworks and templates brought to you by Progression». У 21 карточки есть дизайн-категории, среди них Figma, Intercom, Monzo, Zendesk, dxw, Clearleft, GOV.UK DDaT, «UX Skills Matrix» от Loblaw Digital, «UX skills assessment» от Coryndon Luxmoore и «Product Designer Competency Matrix» от Ope.
- Плана и материалов нет. Это витрина чужих документов: лицензия у каждого своя, у самого сборника не указана.
- Сборник ведёт в продукт Progression: «Build your framework for free No credit card required.»

### 9. Figma — Product Design & Writing Career Levels и виджет Skills Chart
- URL: статья https://www.figma.com/blog/figma-design-team-career-levels/ (23.03.2023, Sara Culver), виджет https://www.figma.com/community/widget/1207836110040407856/Skills-Chart, файл https://www.figma.com/community/file/1220482745322443565/figma-product-design-writing-career-levels
- Модель из 4 категорий: «Product Strategy: Defining requirements, research, vision», «Collaboration: Communication, process and feedback, mindset», «Craft: Visual design, interaction design and prototyping, systems design», «Impact: Business impact, leadership, design citizenship».
- Самооценка: «developed a FigJam widget that would allow for easy (and delightful) self-assessments and performance reviews».
- Не проверено: число уровней, цена, лицензия и популярность. Страницы Figma Community ответили 403 или 202 и без браузера не открылись. Учебных материалов в статье нет.

### 10. Miro — Design Skills Matrix
- URL: https://miro.com/templates/design-skills-matrix/, автор Attilio Raiteri («Experience design Senior Manager»).
- Механика: «Think about your skills, give them a score and create your path of growth and improvement. Create a list of skills you want to improve and paste links to courses, certifications, and books that will help you reach your goals.» Ещё одна строка оттуда: «You have to be honest and sincere with yourself, lying won't do you any good.»
- Шкалу и число навыков не проверял: сама доска не открывалась. Ссылки на материалы вписывает пользователь.
- Популярность по данным страницы: 7734 просмотра и 101 лайк. Лицензия не указана, цена и дата не проверены.

### 11. Грейд-детектор (Pragmatica)
- URL: бот https://t.me/seniordesigner_bot (страница открывается, название «Senior Designer Bot»), статья https://vc.ru/design/540890-kak-opredelit-svoi-greid-bez-eichara-poleznyi-bot-dlya-dizainerov (17.11.2022)
- Механика: «В тесте всего 11 вопросов, а в конце дизайнеры получают смешную картинку с жабкой.» Это квест по рабочим ситуациям: «В конце теста дизайнеры видят градацию и могут определить, к чему тяготеют больше.»
- Точность: «В анонсах мы писали, что детектор определяет грейд с точностью 92% и это почти правда.» Основа — «несколько таблиц с грейдами известных продуктов и студий». Методики нет.
- Охват: «За полгода грейд-детектор прошли 9546 человек». В описании бота: «проходи тесты Прагматрица, Грейд-детектор и Зарплата-вычислятор». Плана развития в статье нет. Работает ли бот сейчас — не проверено.

### 12. ToolFox — тест UI/UX-дизайнера
- URL: https://toolfox.ru/tools/ui-ux-design-test
- Проверено только через WebFetch: два прогона дали одинаковый результат. Скачать страницу напрямую не удалось — сервер рвёт соединение. Поэтому цитат нет.
- Механика. 20 вопросов с вариантами ответа по 6 направлениям: теория и законы дизайна, UX-исследования, прототипирование, визуальный дизайн, инструменты, эмпатия к пользователям. На выходе общий уровень (от Новичка до Эксперта) и проценты по категориям.
- План. Общие советы, какие навыки подтянуть и с чего начать. Ссылок на конкретные материалы нет — школы названы без ссылок. Бесплатно, без регистрации; даты и лицензии нет.

### 13. Skillbox — бесплатный мини-курс UX/UI
- URL: https://bootcamp.skillbox.ru/uxui
- Механика и план: «Пройдите входное тестирование, которое определит ваш уровень знаний. На основе результатов бот подберет оптимальные материалы и задания именно для вас, чтобы обучение было максимально эффективным.» Число вопросов и уровни не проверены.
- Материалы только из мини-курса. Мини-курс ведёт к платным курсам: на странице обещают «скидка 10 000 ₽ на курсы».
- Цена: «Быстрый, короткий и бесплатный курс от Skillbox». Запись через форму.

### 14. Авито — матрица компетенций дизайнеров
- URL: https://github.com/avito-tech/playbook/blob/master/design-levels.md
- Механика. 4 уровня (Junior, Middle, Senior, Lead) × 16 критериев: знание продукта, самостоятельность, сложность задач, качество результата, взаимодействие с продактом, определение проблем, процесс решения задач, визуальный дизайн (UI), пользовательский опыт (UX), работа со смыслом, проверка решений, интеграция дизайна, эффективная коммуникация, работа в команде, наставничество, целеполагание. Для каждого уровня описано поведение; самооценки и материалов нет.
- Обновление: последний коммит по файлу — 04.07.2025 (по GitHub API). У репозитория playbook 2953 звезды.
- Лицензия. У репозитория её нет (GitHub API: license = null). По документации GitHub, без лицензии действуют обычные нормы авторского права: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository

### 15. Т-Банк — матрица навыков дизайнеров
- URL: статья https://habr.com/ru/companies/tbank/articles/689214/ (20.09.2022, Юля Кондратьева), шаблон в Notion https://yulyak.notion.site/yulyak/v-3-1-81df32f268354b3dbb796d06b9152095 («Матрица навыков v.3.1»).
- Механика. «Дизайнер в этой системе выставлял себе оценки, а потом сравнивал их с оценками, которые выставил тимлид.» Шкала: «Где 0 — нет знаний, 1 — нужно проверять, 2 — можно доверять, 3 — может научить». Сами авторы признают: «Оценить себя по такой матрице довольно сложно».
- Notion v3.1. База «Ключевые навыки» — 27 утверждений-поведений по уровням, например «Вовремя закрываю задачи на своем продукте, лид принимает их в большинстве случаев». База «Дополнительные навыки» — 13 навыков с полем «Моя оценка». Есть блок «Митинг ноутс после встречи с лидом».
- План и материалы. В статье: «для каждого навыка есть библиотека полезных заданий и материалов, чтобы его развивать». В Notion это чек-листы «Переход на следующий уровень» (Beginner → Medium → Hard → God) и списки «Что делать?», например «Прочитать книгу Спроси маму». Ссылки в основном внутренние (https://design.corp/).
- Дат у материалов нет. По метаданным Notion страница последний раз правилась 25.09.2023. Лицензия не указана.

### 16. Магнит — карта навыков продуктовых дизайнеров
- URL: часть 1 https://habr.com/ru/articles/850908/ (16.10.2024), часть 2 https://habr.com/ru/articles/852706/ (23.10.2024). Шаблон: https://docs.google.com/spreadsheets/d/1r_Wq8uW8DuSKAD7gPmmYAPJbDBIzoLv6YMRlEkbZn3E/edit?usp=sharing — открывается по ссылке, первый лист — форма обратной связи. Автор — Ваня Соловьёв, руководитель продуктового дизайна в «Магните».
- Механика. «119 навыков разбитых на 6 категорий». Шкала: «0 — не проявляется», «1 — учится и есть теория», «2 — проявляется иногда», «3 — проявляется постоянно», «4 — безупречно владеет и делится знаниями». Процесс: «сотрудник оценивает свои навыки, дизайн-лид проводит калибровку».
- Грейды по пороговой системе, софты/харды: «30/40 — Джун», «65/90 — Мидл», «130/180 — Сеньор», «170/235 — Ведущий», «190/235 — Дизайн-лид».
- Наблюдение про самооценку: «Больше всего вопросов вызвала оценка 4 „безупречно владеет и делится знаниями“». Инструменты: «Notion для заполнения самооценки и составления индивидуальных планов развития. После ухода Notion мы перешли на Ynote.» Ссылок на материалы не нашёл, лицензия не указана.

### 17. SkillsTeam — матрица UX/UI-дизайнера
- URL: https://skillsteam.ru/designer, тарифы https://skillsteam.ru/tariff, главная https://skillsteam.ru/
- Шаблон. На странице указаны 120 навыков и 9 грейдов «от junior-1 до senior-2». У навыка есть поля «Описание», «Как защитить» и «Как принимать», например «Тестовые задания: Построение карты опыта на примере заказа и доставки пиццы.» Матрицу выдают за e-mail: «Введите e-mail и мы отправим вам файл с матрицей компетенций!» На странице дизайнерской матрицы остался чужой текст: «готовую матрицу компетенций для инженеров по тестированию».
- Сервис. Роли — руководитель, наставник, сотрудник; есть индивидуальный план развития. Про материалы: «В нашей системе для любого грейда можно указать ссылку на любые материалы, которые нужны для обучения.» Материалы задаёт сама компания.
- Цена. Тарифы: «Команда» (до 50 пользователей), «Компания» (до 100), «Энтерпрайс» (до 200). Периоды: «1 месяц», «3 месяца -10%», «12 месяцев -40%». Цены по блокам: 14 900 / 24 900 / 34 900 ₽; 39 000 / 69 000 / 99 000 ₽; 99 000 / 199 000 / 299 000 ₽. Какой блок к какому периоду относится, я определил по порядку блоков на странице, а не по подписи. Коробочная версия — по заявке.

## 3. Что это значит для нас

### Главный ответ: связки «оценка уровня → план → живой проверенный каталог» нет
В проверенной выборке из 17 аналогов ни у кого нет полной цепочки. Нет такого, чтобы оценка уровня давала план, а план вёл в публичный кураторский каталог, где у материала видна дата проверки и отмечена доступность из России. Гипотеза подтверждается — но только в пределах этой выборки, это не доказательство отсутствия. Ближе всех четыре варианта:
- Uxcel: тест → Skill Graph → «custom plan» и рекомендации курсов. Каталог закрытый (только свои курсы), платный, на английском. Даты проверки на страницах курсов не смотрел; устаревшей помечается только оценка пользователя.
- Vectorly: самооценка и ревью → грейд → карта развития со ссылками на базу знаний компании. Это B2B, материалы собирает сама команда, а сервис, судя по недоступным доменам приложения, не работает.
- Skillbox: входной тест → бот подбирает материалы мини-курса. Это воронка продаж без каталога.
- Т-Банк: матрица → задания и материалы по навыку в Notion. Всё статично, внутреннее, последняя правка в 2023 году.

Остальные даже близко не дают эту цепочку. Brimo — материалов в шаблоне 0, ИИ-подбор чтения только в планах. roadmap.sh — план с материалами, но без оценки и без дат. Miro — ссылки на курсы пользователь вписывает сам.

### Что на рынке уже есть
1. Тесты с ярлыком уровня: Uxcel, ToolFox, Грейд-детектор, KursHub (приложение А). Дают балл или грейд, а план в них либо общий совет, либо свои курсы, либо его нет.
2. B2B-сервисы для компаний: Brimo, Vectorly, Progression, SkillsTeam. Оценка через руководителя, ИПР, материалы из базы знаний компании. Дизайнеру без команды доступны только бесплатные тарифы Progression (с оговоркой «getting your manager involved») и Brimo (до 3 пользователей).
3. Открытые матрицы компаний: Авито, Т-Банк, Магнит, GitLab, GOV.UK, Figma и сборник progression.fyi. В них описаны уровни, но нет проверки и почти нет материалов.
4. Шаблоны самооценки «сделай сам»: Miro, виджет Figma, Notion Т-Банка, таблица Магнита.
5. Карта-план с материалами без оценки: roadmap.sh.

### Чего на рынке нет (в выборке)
- Русскоязычной бесплатной самопроверки для junior с понятными наблюдаемыми критериями и маршрутом по внешним материалам.
- Даты проверки и пометки доступности из России у материалов плана. Там, где материалы удалось посмотреть (roadmap.sh, Т-Банк, Brimo, SkillsTeam), этого нет. У Uxcel, Vectorly и Progression страницы с материалами не проверял.
- Честного объяснения ограничений результата. Грейд-детектор заявляет «92% и это почти правда» без методики, Uxcel сравнивает с «500K+ designers» без привязки к грейдам.

### Что можно переиспользовать легально
- GOV.UK DDaT (OGL v3.0) — единственная модель в выборке с явной открытой лицензией. Её можно адаптировать и использовать коммерчески с указанием источника. Годится как каркас: навык × 4 уровня владения (Awareness / Working / Practitioner / Expert). Минусы: роли британской госслужбы, английский язык, нужна адаптация под продуктовый дизайн.
- GitLab: на странице «All Rights Reserved», лицензия текстов не указана. Использовать только как ориентир со ссылкой.
- Авито: репозиторий без лицензии, то есть по умолчанию действуют обычные нормы авторского права. Т-Банк, Магнит, Miro, SkillsTeam и progression.fyi — лицензия не указана. roadmap.sh прямо запрещает переиспользование.
- Предлагаю: собственную модель компетенций пишем сами. Чужие матрицы берём как источник идей со ссылкой на автора. Если захотим брать формулировки дословно, например из Авито, Т-Банка или Магнита, просим у авторов письменное разрешение. Поправь, если видишь иначе.

### Риски
1. Самооценка новичков завышена, а наша первичная аудитория — как раз junior (источники ниже). Предлагаю: не шкалу «оцени себя от 1 до N», а наблюдаемые критерии и артефакты (как «1+ пример» в карточке Ветрова в Brimo или «проявляется постоянно» у Магнита) плюс короткие вопросы на знание. Итог подавать как профиль и следующие шаги, а не как вердикт «ты — middle».
2. Грейды в разных компаниях не совпадают. Даже в этой выборке число ступеней разное: 4 у Авито, 5 у Магнита и GitLab, 6 уровней роли у GOV.UK, 9 грейдов у SkillsTeam, 10 грейдов в карточке Ветрова в Brimo. Ярлык junior/middle/senior от нас может разойтись с грейдом в компании пользователя и подорвать доверие. Предлагаю формулировать «по модели DesignSite» и показывать, по каким критериям это получилось.
3. Юридический риск: копирование чужих матриц без лицензии (см. выше).
4. Такие инструменты быстро умирают и устаревают. Vectorly, похоже, не работает; Грейд-детектор описан в 2022 году; Notion Т-Банка не правился с 2023 года; Магнит пишет «После ухода Notion мы перешли на Ynote». Наше обещание актуальности должно касаться и самой модели: у неё тоже нужна дата ревизии.
5. Конкуренция. Uxcel ближе всех по механике, но он англоязычный, платный и замкнут на свои курсы. Школы (Skillbox, Практикум) используют тесты как воронку и могут быстро скопировать. B2B-сервисы (Brimo, SkillsTeam) уже держат модели компетенций и могут выйти к частным пользователям.

### Надёжность самооценки: источники
- Kruger, J. & Dunning, D. (1999). Unskilled and Unaware of It. Journal of Personality and Social Psychology, 77(6), 1121–1134. PDF: https://sites.lsa.umich.edu/sasi/wp-content/uploads/sites/275/2015/11/krugerdunning99.pdf. Из аннотации: «participants scoring in the bottom quartile on tests of humor, grammar, and logic grossly overestimated their test performance and ability. Although their test scores put them in the 12th percentile, they estimated themselves to be in the 62nd.» И ещё: «Paradoxically, improving the skills of participants, and thus increasing their metacognitive competence, helped them recognize the limitations of their abilities.» Исследование не про дизайнеров.
- Практика продуктовой команды, не исследование. Progression, 2019: «In v1 we allowed users to pick any skill level from 1 - 5 (beginner to master) for each skill required of them. This led to some users picking 5 for everything and creating an awkward conversation for their manager who needed to bring them back down to earth.» Источник: https://progression.co/blog/introducing-checkins/
- Грейды не совпадают — пока только мнение практика, не исследование. Хабр, 14.07.2025, https://habr.com/ru/articles/927426/: «Компетенции сложно подвести под одну гребенку, так как для дизайнера в разных компаниях или даже в разных продуктах в рамках одной компании они будут отличаться.» Сравнение лестниц Product Designer на levels.fyi (https://www.levels.fyi/PD/) проверить не удалось: страница отвечает 403.

## Приложение А. Проверено, но в таблицу не вошло
- KursHub, https://kurshub.ru/free-tests/ui-ux-design/ — бесплатный тест трёх уровней сложности: «10 вопросов · 10 мин.», 15 и 20 вопросов. На выходе: «По результатам вы увидите, в каких областях — исследования, визуальный дизайн или доступность — есть потенциал для роста.» Владелец — ИП Шарков Иван Сергеевич. Формат результата подробнее не проверен.
- «Россия — страна возможностей», https://rsv.ru/test/975/ — «Пройдите бесплатно онлайн-тест и определите свой уровень знаний UX-дизайна.» Сам тест работает на JavaScript, число вопросов и формат результата не проверены.
- Яндекс Практикум PRO, «Продуктовый подход для дизайнеров», https://practicum.yandex.ru/product-approach-for-designers/ — входной тест готовности к курсу, а не оценка уровня с планом: «Задания проверяют ваши навыки в Figma, понимание основ композиции, цвета, типографики, сеток и компонентного подхода. Тест займёт не более 30 минут.»
- Contented, https://live.contented.ru/design_test — профориентация: «Пройдите тест из 10 вопросов и узнайте, какая дизайн-профессия подходит лично вам», «Онлайн, бесплатно, без регистрации».
- Bang Bang Education, https://bangbangeducation.ru/proftest — профориентация: «Определите свои сильные стороны и подходящие профессии за 15 минут!»
- Нетология и Контур.Школа: поиск по их сайтам теста уровня для дизайнеров не нашёл; у Контур.Школы в выдаче курсы тестировщиков. Это не доказательство, что теста нет.
- hh.ru, https://career.hh.ru/assessment — тестов для дизайнеров нет: в HTML страницы не встречаются слова «дизайн» и «Figma».
- re-designer.ru, https://re-designer.ru/ux-matrix — статичная матрица (© Павел Óларь): уровни Junior, Mid-level, Senior, Lead, Principal, есть ссылка «База знаний». Лицензия не указана.
- Figma Community, шаблоны «Product Designer Self Assessment Template» (https://www.figma.com/community/file/1088219107812131592/product-designer-self-assessment-template) и «Product UX Designer Skills Self-assesment» (https://www.figma.com/community/file/1154829813044318647/product-ux-designer-skills-self-assesment). Проверено только, что страницы существуют (заголовок есть в HTML). Описание, популярность и лицензия без браузера не читаются — не проверено.

## Приложение Б. Что не открылось или проверено частично
- Figma Community (файлы и виджет): WebFetch — 403, curl — 202 или SPA, внутренний API — 404.
- levels.fyi/PD: 403 и через WebFetch, и через curl.
- toolfox.ru: curl и Python — сервер обрывает соединение; данные только из WebFetch, без цитат.
- app.vectorly.team и public.vectorly.team: домены не резолвятся.
- Библиотека Progression (SPA): просмотрены встроенные в HTML данные; шаблон Ветрова в них не найден.
- Uxcel pricing: цены в HTML — заглушки, реальные взяты из публичного API, которым пользуется сама страница.
- Доступность из России не проверялась нигде (причина — в начале отчёта).
