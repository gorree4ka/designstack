---
name: "wp-theme"
description: "Создание и развитие собственной блочной темы `designstack` (theme.json, шаблоны, паттерны, стили). Использовать, когда нужно сверстать сайт, страницу или компонент темы."
allowed-tools: Bash Read Write Edit Glob Grep
---

# Тема `designstack` (блочная, FSE)

Путь: `wordpress/wp-content/themes/designstack/`. Требования WordPress 7.x, PHP 8.3.

## Минимальная структура

```
designstack/
  style.css          # заголовок темы (Theme Name, Text Domain: designstack, Requires at least, Version)
  theme.json         # $schema, version 3: settings.color.palette, typography.fontFamilies, spacing, layout, styles
  functions.php      # add_theme_support, регистрация паттернов/стилей, wp_enqueue_*
  templates/         # index.html, front-page.html, single.html, page.html, archive.html, 404.html
  parts/             # header.html, footer.html
  patterns/          # hero.php, services.php, cta.php ... (заголовок: Title, Slug: designstack/hero, Categories)
  assets/            # css/, js/, fonts/, img/
  screenshot.png     # 1200x900
```

## Порядок работы

1. Сначала дизайн-токены в `theme.json` (палитра, шрифты, размеры, отступы) — затем шаблоны, затем паттерны.
2. Один паттерн = одна секция страницы. Собирать страницы из паттернов, не писать HTML руками в редакторе.
3. После каждого шага: `tools/wp.cmd --path=wordpress theme activate designstack` (один раз), затем `curl` страницы и проверка `debug.log` (см. skill `wp-dev`).
4. Проверка валидности: `tools/wp.cmd --path=wordpress eval 'print_r( wp_get_theme("designstack")->errors() );'` должно вернуть пусто; JSON — `python -m json.tool wordpress/wp-content/themes/designstack/theme.json`.
5. Контент для проверки создавать через WP-CLI (`post create`, `menu create`), не вручную.

## Сборка ассетов (если нужны SCSS/JS)

`npm init -y && npm i -D @wordpress/scripts` в папке темы; `npx wp-scripts build`. Без необходимости — обычный CSS в `assets/css/`, подключённый через `wp_enqueue_style`.

Правила кода — в `.claude/rules/wp-theme.md`.
