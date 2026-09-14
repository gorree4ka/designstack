<?php
/**
 * Title: Витрина: навигация
 * Slug: designstack/styleguide-navigation
 * Categories: designstack-styleguide
 * Inserter: no
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<section class="sg-section" id="sg-navigation">
	<h2 class="sg-section__title">Навигация</h2>
	<p class="sg-section__note">Шапка и подвал здесь — те же паттерны, что стоят на странице: сверху этой витрины видна настоящая шапка. Ссылку «Перейти к содержимому» ставит ядро WordPress, она первая в порядке фокуса.</p>

	<div class="sg-item">
		<h3 class="sg-item__title">site-header</h3>
		<p class="sg-item__note">До 900 меню сворачивается в кнопку «Меню» через details: без JavaScript меню просто раскрыто, а не пропадает.</p>
		<div class="sg-matrix sg-matrix--wide"><div class="sg-cell"><p class="sg-cell__label">шапка</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'site-header', '', '', true ); ?></div></div></div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">breadcrumbs</h3>
		<div class="sg-matrix sg-matrix--wide"><div class="sg-cell"><p class="sg-cell__label">крошки текущей страницы</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'breadcrumbs' ); ?></div></div></div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">pagination</h3>
		<?php echo designstack_styleguide_matrix( 'pagination', 'ds-pagination__page', array( '' => 'по умолчанию', 'is-hover' => 'наведение' ) ); ?>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">site-footer</h3>
		<div class="sg-matrix sg-matrix--wide"><div class="sg-cell"><p class="sg-cell__label">подвал</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'site-footer', '', '', true ); ?></div></div></div>
	</div>
</section>
<!-- /wp:html -->
