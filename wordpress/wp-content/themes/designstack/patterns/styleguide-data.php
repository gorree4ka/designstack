<?php
/**
 * Title: Витрина: данные
 * Slug: designstack/styleguide-data
 * Categories: designstack-styleguide
 * Inserter: no
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<section class="sg-section" id="sg-data">
	<h2 class="sg-section__title">Данные</h2>
	<p class="sg-section__note">Даты и счётчики — моноширинным с табличными цифрами. Факты ресурса показаны в широкой и в узкой колонке: в узкой подпись встаёт над значением по ширине самой колонки, а не окна.</p>

	<div class="sg-item">
		<h3 class="sg-item__title">meta-line и resource-logo</h3>
		<div class="sg-matrix">
			<div class="sg-cell"><p class="sg-cell__label">мета-строки</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'meta-line' ); ?></div></div>
			<div class="sg-cell"><p class="sg-cell__label">плитки логотипа: 40, 40 с краем, 64</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'resource-logo' ); ?></div></div>
		</div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">resource-facts</h3>
		<div class="sg-matrix">
			<div class="sg-cell"><p class="sg-cell__label">широкая колонка</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'resource-facts' ); ?></div></div>
			<div class="sg-cell sg-cell--narrow"><p class="sg-cell__label">узкая колонка</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'resource-facts' ); ?></div></div>
		</div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">curator-review</h3>
		<div class="sg-matrix sg-matrix--wide"><div class="sg-cell"><p class="sg-cell__label">три части и подпись</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'curator-review' ); ?></div></div></div>
	</div>
</section>
<!-- /wp:html -->
