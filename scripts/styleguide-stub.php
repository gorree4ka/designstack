<?php
/**
 * Styleguide stub for directive 10, phase 4: /styleguide/ shows the design tokens on core blocks and every catalog status
 * as icon + word + colour in both themes.
 *
 * Run: tools/wp.cmd --path=wordpress eval-file scripts/styleguide-stub.php
 * Idempotent: the page styleguide is created or its content replaced. It renders with templates/page-styleguide.html by
 * the template hierarchy and carries meta _designstack_stub=1: stage 11 replaces it with the styleguide of patterns.
 * Content is saved without kses: inline Lucide icons and a style block that uses token variables only.
 *
 * @package designstack
 */

if ( ! defined( 'WP_CLI' ) ) {
	exit;
}

$designstack_content = <<<'HTML'
<!-- wp:group {"className":"styleguide","style":{"spacing":{"blockGap":"var:preset|spacing|8","margin":{"top":"var:preset|spacing|6"}}},"layout":{"type":"flex","orientation":"vertical","justifyContent":"stretch"}} -->
<div class="wp-block-group styleguide" style="margin-top:var(--wp--preset--spacing--6)"><!-- wp:html -->
<style>
.styleguide code{font-family:var(--wp--preset--font-family--mono);font-size:var(--wp--preset--font-size--sm)}
.styleguide .wp-block-list{padding-left:var(--wp--preset--spacing--6);list-style:disc}
.sg-row{display:flex;flex-wrap:wrap;align-items:center;gap:var(--wp--preset--spacing--2)}
.sg-panel{display:flex;flex-direction:column;gap:var(--wp--preset--spacing--3);padding:var(--wp--preset--spacing--4);border:var(--wp--custom--border-width--hairline) solid var(--wp--preset--color--border-default);border-radius:var(--wp--custom--radius--md);background:var(--wp--preset--color--surface-raised)}
.sg-label{min-width:calc(var(--wp--preset--spacing--16) + var(--wp--preset--spacing--12));color:var(--wp--preset--color--text-muted)}
.sg-badge{display:inline-flex;align-items:center;gap:var(--wp--preset--spacing--1);min-height:var(--wp--preset--spacing--6);padding:0 var(--wp--preset--spacing--2);border:var(--wp--custom--border-width--hairline) solid var(--wp--preset--color--border-default);border-radius:var(--wp--custom--radius--sm);background:var(--wp--preset--color--surface-raised);color:var(--wp--preset--color--text-default);font-size:var(--wp--preset--font-size--sm);font-weight:500;white-space:nowrap}
.sg-badge svg,.sg-message svg{flex:none;width:var(--wp--preset--spacing--4);height:var(--wp--preset--spacing--4)}
.sg-badge.is-warning{border-color:transparent;background:var(--wp--preset--color--bg-warning)}
.sg-badge.is-error{border-color:transparent;background:var(--wp--preset--color--bg-error)}
.sg-success svg{color:var(--wp--preset--color--icon-success)}
.sg-warning svg{color:var(--wp--preset--color--icon-warning)}
.sg-error svg{color:var(--wp--preset--color--icon-error)}
.sg-date{font-family:var(--wp--preset--font-family--mono);font-size:var(--wp--preset--font-size--sm);font-variant-numeric:tabular-nums;color:var(--wp--preset--color--text-muted)}
.sg-outline{display:inline-flex;align-items:center;padding:var(--wp--preset--spacing--2) var(--wp--preset--spacing--4);border:var(--wp--custom--border-width--hairline) solid var(--wp--preset--color--border-strong);border-radius:var(--wp--custom--radius--sm);background:var(--wp--preset--color--surface-raised);color:var(--wp--preset--color--text-action);font-weight:600;text-decoration:none}
.sg-chip{display:inline-flex;align-items:center;min-height:var(--wp--preset--spacing--8);padding:0 var(--wp--preset--spacing--3);border:var(--wp--custom--border-width--hairline) solid var(--wp--preset--color--border-default);border-radius:var(--wp--custom--radius--full);color:var(--wp--preset--color--text-default);text-decoration:none}
.sg-chip[aria-current]{border-color:var(--wp--preset--color--border-focus-ring);background:var(--wp--preset--color--surface-selected)}
.sg-disabled{opacity:.5;cursor:not-allowed}
.sg-field{display:flex;flex-direction:column;gap:var(--wp--preset--spacing--1)}
.sg-field label{font-weight:600}
.sg-field input{padding:var(--wp--preset--spacing--2) var(--wp--preset--spacing--3);border:var(--wp--custom--border-width--hairline) solid var(--wp--preset--color--border-strong);border-radius:var(--wp--custom--radius--sm);background:var(--wp--preset--color--surface-raised);color:var(--wp--preset--color--text-default);font:inherit}
.sg-field.has-error input{border-color:var(--wp--preset--color--border-error)}
.sg-message{display:flex;align-items:flex-start;gap:var(--wp--preset--spacing--1);color:var(--wp--preset--color--text-error);font-size:var(--wp--preset--font-size--sm)}
.sg-message svg{color:var(--wp--preset--color--icon-error)}
.sg-dropdown{box-shadow:var(--wp--preset--shadow--md)}
</style>
<!-- /wp:html -->

<!-- wp:paragraph {"textColor":"text-muted"} -->
<p class="has-text-muted-color has-text-color">Заглушка этапа 10: токены на core-блоках в светлой и тёмной теме. Витрину паттернов собирает этап 11.</p>
<!-- /wp:paragraph -->

<!-- wp:group {"style":{"spacing":{"blockGap":"var:preset|spacing|3"}},"layout":{"type":"flex","orientation":"vertical","justifyContent":"stretch"}} -->
<div class="wp-block-group"><!-- wp:heading -->
<h2 class="wp-block-heading">Типографика</h2>
<!-- /wp:heading -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Заголовок h3 — кегль lg, 17 px</h3>
<!-- /wp:heading -->

<!-- wp:heading {"level":4} -->
<h4 class="wp-block-heading">Заголовок h4 — кегль base, 16 px</h4>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Съешь же ещё этих мягких французских булок, да выпей чаю. ЩИТ, ОБЪЁМ, ВЫБОР; «ёлочки» и „лапки“, 1&nbsp;290&nbsp;₽, №&nbsp;5. <a href="/tools/">Ссылка в тексте</a> — цвет текста с подчёркиванием, петроль при наведении.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph {"textColor":"text-muted","fontSize":"sm"} -->
<p class="has-text-muted-color has-text-color has-sm-font-size">Подпись text-muted, кегль sm: даты, подписи, теги, счётчики.</p>
<!-- /wp:paragraph --></div>
<!-- /wp:group -->

<!-- wp:group {"style":{"spacing":{"blockGap":"var:preset|spacing|3"}},"layout":{"type":"flex","orientation":"vertical","justifyContent":"stretch"}} -->
<div class="wp-block-group"><!-- wp:heading -->
<h2 class="wp-block-heading">Кнопки и выбор</h2>
<!-- /wp:heading -->

<!-- wp:buttons -->
<div class="wp-block-buttons"><!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="/tools/">Применить</a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons -->

<!-- wp:html -->
<div class="sg-row"><a class="sg-outline" href="https://www.figma.com/">Перейти на сайт</a><a class="sg-chip" href="/topic-prototyping/">Все</a><a class="sg-chip" href="/topic-prototyping/?resource_type=tool" aria-current="page">Инструменты</a><button type="button" class="wp-element-button sg-disabled" disabled>Применить</button></div>
<!-- /wp:html --></div>
<!-- /wp:group -->

<!-- wp:group {"style":{"spacing":{"blockGap":"var:preset|spacing|3"}},"layout":{"type":"flex","orientation":"vertical","justifyContent":"stretch"}} -->
<div class="wp-block-group"><!-- wp:heading -->
<h2 class="wp-block-heading">Список и разделитель</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul class="wp-block-list"><!-- wp:list-item -->
<li>Инструменты — редакторы, прототипы, тесты</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li>Учёба — курсы, книги, статьи, видео</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li>Сообщества — каналы, чаты, рассылки</li>
<!-- /wp:list-item --></ul>
<!-- /wp:list -->

<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator --></div>
<!-- /wp:group -->

<!-- wp:group {"style":{"spacing":{"blockGap":"var:preset|spacing|3"}},"layout":{"type":"flex","orientation":"vertical","justifyContent":"stretch"}} -->
<div class="wp-block-group"><!-- wp:heading -->
<h2 class="wp-block-heading">Поле формы</h2>
<!-- /wp:heading -->

<!-- wp:html -->
<div class="sg-field"><label for="sg-url">Адрес ресурса</label><input type="url" id="sg-url" value="https://excalidraw.com"></div>
<div class="sg-field has-error"><label for="sg-url-error">Адрес ресурса</label><input type="url" id="sg-url-error" value="excalidraw com" aria-invalid="true" aria-describedby="sg-url-error-message"><span class="sg-message" id="sg-url-error-message">{{circle-x}}Это не похоже на адрес сайта. Проверь, нет ли пробела или опечатки, например: https://excalidraw.com</span></div>
<!-- /wp:html --></div>
<!-- /wp:group -->

<!-- wp:group {"style":{"spacing":{"blockGap":"var:preset|spacing|3"}},"layout":{"type":"flex","orientation":"vertical","justifyContent":"stretch"}} -->
<div class="wp-block-group"><!-- wp:heading -->
<h2 class="wp-block-heading">Статусы</h2>
<!-- /wp:heading -->

<!-- wp:html -->
<div class="sg-panel">
<div class="sg-row"><code class="sg-label">ru_open</code><span class="sg-badge sg-success">{{circle-check}}Открывается из РФ</span><span class="sg-badge sg-warning">{{triangle-alert}}Только с VPN</span><span class="sg-badge sg-error">{{circle-x}}Недоступен из РФ</span></div>
<div class="sg-row"><code class="sg-label">ru_payment</code><span class="sg-badge sg-success">{{circle-check}}Оплачивается из РФ</span><span class="sg-badge sg-success">{{circle-check}}Российский</span><span class="sg-badge sg-error">{{circle-x}}Не оплатить из РФ</span></div>
<div class="sg-row"><code class="sg-label">status</code><span class="sg-badge is-warning sg-warning">{{triangle-alert}}Условия изменились</span><span class="sg-badge is-error sg-error">{{circle-x}}Закрыт</span></div>
<div class="sg-row"><code class="sg-label">checked_at</code><span class="sg-date">Проверено 3&nbsp;сен&nbsp;2026</span><span class="sg-badge is-warning sg-warning">{{clock}}Давно не проверяли</span></div>
<div class="sg-row"><code class="sg-label">pricing</code><span class="sg-badge">Бесплатно</span><span class="sg-badge">Есть бесплатный тариф</span><span class="sg-badge">Платно</span><span class="sg-badge">Пробный период</span></div>
<div class="sg-row"><code class="sg-label">level</code><span class="sg-badge">Junior</span><span class="sg-badge">Middle</span><span class="sg-badge">Senior</span></div>
</div>
<!-- /wp:html --></div>
<!-- /wp:group -->

<!-- wp:group {"style":{"spacing":{"blockGap":"var:preset|spacing|3"}},"layout":{"type":"flex","orientation":"vertical","justifyContent":"stretch"}} -->
<div class="wp-block-group"><!-- wp:heading -->
<h2 class="wp-block-heading">Тень</h2>
<!-- /wp:heading -->

<!-- wp:html -->
<div class="sg-panel sg-dropdown"><code>shadow-md</code><span>Выезжающие панели: фильтры на телефоне, выпадающие списки.</span></div>
<!-- /wp:html --></div>
<!-- /wp:group --></div>
<!-- /wp:group -->
HTML;

$designstack_icons = array(
	'circle-check'   => '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
	'triangle-alert' => '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
	'circle-x'       => '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
	'clock'          => '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
);
foreach ( $designstack_icons as $designstack_name => $designstack_paths ) {
	$designstack_svg     = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' . $designstack_paths . '</svg>';
	$designstack_content = str_replace( '{{' . $designstack_name . '}}', $designstack_svg, $designstack_content );
}
if ( false !== strpos( $designstack_content, '{{' ) ) {
	WP_CLI::error( 'unknown icon placeholder left in the styleguide content' );
}

kses_remove_filters();

$designstack_args = array(
	'post_type'    => 'page',
	'post_status'  => 'publish',
	'post_title'   => 'Витрина дизайн-системы',
	'post_name'    => 'styleguide',
	'post_content' => $designstack_content,
	'meta_input'   => array( '_designstack_stub' => '1' ),
);

$designstack_existing = get_page_by_path( 'styleguide', OBJECT, 'page' );
if ( $designstack_existing ) {
	$designstack_args['ID'] = $designstack_existing->ID;
	$designstack_id         = wp_update_post( $designstack_args, true );
} else {
	$designstack_id = wp_insert_post( $designstack_args, true );
}

if ( is_wp_error( $designstack_id ) ) {
	WP_CLI::error( 'styleguide: ' . $designstack_id->get_error_message() );
}

$designstack_icon_count = substr_count( $designstack_content, '<svg' );
$designstack_saved      = get_post_field( 'post_content', $designstack_id );
if ( substr_count( $designstack_saved, '<svg' ) !== $designstack_icon_count || false === strpos( $designstack_saved, '<style>' ) ) {
	WP_CLI::error( 'styleguide: icons or style block were stripped on save' );
}
WP_CLI::log( sprintf( 'styleguide page ID %d, %d bytes of content, %d icons, stub', $designstack_id, strlen( $designstack_saved ), $designstack_icon_count ) );
