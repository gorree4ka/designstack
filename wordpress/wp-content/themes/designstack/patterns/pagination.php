<?php
/**
 * Title: Пагинация
 * Slug: designstack/pagination
 * Categories: designstack
 * Inserter: no
 *
 * Страницы с адресами, без бесконечной ленты (D17). От 600 — номера, до 600 — «Страница 1 из 3».
 * На страницах это блок core/query-pagination с теми же классами (этап 13).
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<nav class="ds-pagination" aria-label="Страницы">
	<span class="ds-button ds-button--secondary ds-button--sm is-disabled"><?php echo designstack_icon( 'chevron-left' ); ?>Назад</span>
	<span class="ds-pagination__numbers">
		<span class="ds-pagination__page" aria-current="page">1</span>
		<a class="ds-pagination__page" href="/tools/page/2/">2</a>
		<a class="ds-pagination__page" href="/tools/page/3/">3</a>
	</span>
	<span class="ds-pagination__summary ds-meta">Страница 1 из 3</span>
	<a class="ds-button ds-button--secondary ds-button--sm" href="/tools/page/2/">Вперёд<?php echo designstack_icon( 'chevron-right' ); ?></a>
</nav>
<!-- /wp:html -->
