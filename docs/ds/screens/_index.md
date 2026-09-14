# Страницы: composition maps и статусы

Этап 13. Одна карта на страницу; шаблон может обслуживать несколько адресов. Партии те же, что на этапе 08:
1 — каталог, 2 — главная, 3 — редакция и архивы, 4 — форма и служебные страницы.

Лист решений публикуется на партию, апрув даётся в чате и переносится в карточку страницы.

| Страница | URL | Лист решений | Шаблон | Паттерны и блоки | Локальные композиции | Статус |
|---|---|---|---|---|---|---|
| [tools](tools.md) | `/tools/` `/learn/` `/assets/` `/community/` | [партия 1 «Каталог»](https://claude.ai/code/artifact/e5ebd45b-228c-44af-bf5b-18de4a8b4c0a) | `taxonomy-resource_type.html` | site-header, breadcrumbs, page-header, filter-panel, filter-chips, resource-card, resource-list, badge, meta-line, pagination, empty-state, site-footer · блоки `designstack/archive-header`, `filter-panel`, `filter-chips`, `resource-list`, `pagination` | `ds-archive` — вынесена в `patterns.css` (паттерн `page-layout`) | оживлено 14.09.2026 |
| [topic](topic.md) | `/topic/{slug}/` | [партия 1 «Каталог»](https://claude.ai/code/artifact/e5ebd45b-228c-44af-bf5b-18de4a8b4c0a) | `taxonomy-topic.html` | те же, кроме filter-panel; плюс `core/term-description` | нет | оживлено 14.09.2026 |
| [resource](resource.md) | `/resource/{slug}/` | [партия 1 «Каталог»](https://claude.ai/code/artifact/e5ebd45b-228c-44af-bf5b-18de4a8b4c0a) | `single-resource.html` | breadcrumbs, resource-hero, resource-facts, curator-review, resource-card, resource-list, badge, notice, meta-line, resource-logo, section-header · блоки `designstack/resource-hero`, `resource-meta`, `curator-review`, `resource-analogs` | `ds-detail` — вынесена в `patterns.css` (паттерн `page-layout`) | оживлено 14.09.2026 |
| [home](home.md) | `/` | [партия 2 «Главная»](https://claude.ai/code/artifact/6ff59253-6890-4af9-b9be-f0bb639f594a) | `front-page.html` | site-header, search-form, entry-tiles, section-header, resource-card, resource-list, post-card, badge, meta-line, resource-logo, subscribe-cta, site-footer · блоки `designstack/search-form`, `starter-set`, `checked-week`, `post-list`, `subscribe` | первый экран — группа `ds-stack`; `ds-steps` вынесены в `patterns.css` (паттерн `starter-steps`) | оживлено 14.09.2026 |
| [collection](collection.md) | `/collections/{slug}/` | [партия 3 «Редакция»](https://claude.ai/code/artifact/c7897884-1532-4490-85c9-585994515b4d) | `single.html` | site-header, breadcrumbs, page-header, prose, resource-card, resource-list, post-card, section-header, badge, meta-line, site-footer · блоки `designstack/entry-header`, `post-list` | `ds-prose` — вынесена в `patterns.css` (паттерн `prose`) | оживлено 14.09.2026 |
| [digest-issue](digest-issue.md) | `/digest/{slug}/` | [партия 3 «Редакция»](https://claude.ai/code/artifact/c7897884-1532-4490-85c9-585994515b4d) | `single.html` | те же плюс issue-nav и subscribe-cta · блоки `designstack/issue-nav`, `subscribe` | `ds-issue-nav` — вынесена в `patterns.css` (паттерн `issue-nav`) | оживлено 14.09.2026 |
| [archives](archives.md) | `/collections/` `/digest/` `/reviews/` | [партия 3 «Редакция»](https://claude.ai/code/artifact/c7897884-1532-4490-85c9-585994515b4d) | `category.html` | breadcrumbs, page-header, post-card, empty-state, pagination · блоки `designstack/archive-header`, `post-archive`, `pagination` | нет | оживлено 14.09.2026 |
| [suggest](suggest.md) | `/suggest/` `/suggest/thanks/` | [партия 4](https://claude.ai/code/artifact/5688787c-cad2-4791-985a-74275d0d973b) | `page-suggest.html`, `page.html` | site-header, breadcrumbs, page-header, prose, suggest-form, form-field, error-summary, notice, site-footer · блок `designstack/suggest-form` | нет | оживлено 14.09.2026 |
| [about](about.md) | `/about/` `/privacy/` | [партия 4](https://claude.ai/code/artifact/5688787c-cad2-4791-985a-74275d0d973b) | `page-about.html`, `page.html` | те же плюс post-card · блок `designstack/post-list` | нет | оживлено 14.09.2026 |
| [search](search.md) | `/search/?s=` | [партия 4](https://claude.ai/code/artifact/5688787c-cad2-4791-985a-74275d0d973b) | `search.html` | search-form, resource-card, post-card, empty-state, pagination · блоки `designstack/search-results`, `pagination` | нет | оживлено 14.09.2026 |
| [not-found](not-found.md) | любой несуществующий адрес | [партия 4](https://claude.ai/code/artifact/5688787c-cad2-4791-985a-74275d0d973b) | `404.html` | empty-state, search-form, entry-tiles · блоки `designstack/not-found`, `search-form` | нет | оживлено 14.09.2026 |

Серый прототип этапа 08 снесён 12.09.2026: 17 страниц-заглушек, 13 шаблонов `greybox-*.html` и `assets/css/greybox.css`.
Шаблон `index.html` остаётся как запасной: он повторяет архив записей.

## Что ещё не сделано на собранных страницах

- Фильтры, чипсы типа и поиск не выбирают: чтение параметров и выборку включает этап 14.
- Логотипы ресурсов — буквы-заглушки; картинки ставит этап 16.
- Метки доступа и оплаты в демо-данных взяты по открытым источникам, а не проверены с российского IP (O8).
- Описание темы и дочерние темы не выводятся, пока их нет в данных (этап 16).
