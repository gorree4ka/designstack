<?php
/**
 * Title: Витрина: ввод
 * Slug: designstack/styleguide-input
 * Categories: designstack-styleguide
 * Inserter: no
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<section class="sg-section" id="sg-input">
	<h2 class="sg-section__title">Ввод</h2>
	<p class="sg-section__note">Поля формы и фильтры показаны по одному разу: их состояния — отдельные экземпляры внутри паттерна, иначе на странице появились бы два поля с одним id.</p>

	<div class="sg-item">
		<h3 class="sg-item__title">search-form</h3>
		<p class="sg-item__note">В шапке — контурная кнопка «Найти», на главной — залитая и поле выше.</p>
		<div class="sg-matrix sg-matrix--wide"><div class="sg-cell"><p class="sg-cell__label">шапка и главная</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'search-form' ); ?></div></div></div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">form-field</h3>
		<p class="sg-item__note">Поле, поле с подсказкой, комментарий, поле с ошибкой и флажок согласия. Ошибку показывает иконка и текст, а не только цвет.</p>
		<div class="sg-matrix sg-matrix--wide"><div class="sg-cell"><p class="sg-cell__label">все состояния</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'form-field' ); ?></div></div></div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">error-summary</h3>
		<div class="sg-matrix sg-matrix--wide"><div class="sg-cell"><p class="sg-cell__label">три ошибки</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'error-summary' ); ?></div></div></div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">filter-chips</h3>
		<?php echo designstack_styleguide_matrix( 'filter-chips', 'ds-chip', array( '' => 'по умолчанию', 'is-hover' => 'наведение' ) ); ?>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">filter-panel</h3>
		<p class="sg-item__note">Колонка 280 от 900 px; до 900 та же панель выезжает снизу. Значение без ресурсов не показывается, поэтому недоступных флажков нет.</p>
		<div class="sg-matrix"><div class="sg-cell"><p class="sg-cell__label">колонка фильтров</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'filter-panel' ); ?></div></div></div>
	</div>
</section>
<!-- /wp:html -->
