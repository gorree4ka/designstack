<?php
/**
 * Title: Витрина: песочницы
 * Slug: designstack/styleguide-sandboxes
 * Categories: designstack-styleguide
 * Inserter: no
 *
 * Паттерны рядом друг с другом: так видно ритм и то, что элементы не спорят между собой.
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<section class="sg-section" id="sg-sandboxes">
	<h2 class="sg-section__title">Песочницы</h2>
	<p class="sg-section__note">Три сборки из тех же паттернов: раздел каталога, карточка в трёх ширинах и форма со всеми сообщениями. Страницы из них соберёт этап 13.</p>

	<div class="sg-item">
		<h3 class="sg-item__title">Раздел каталога</h3>
		<div class="sg-sandbox">
			<?php echo designstack_styleguide_pattern( 'breadcrumbs' ); ?>
			<?php echo designstack_styleguide_pattern( 'filter-chips', '', '', true ); ?>
			<div class="sg-archive">
				<?php echo designstack_styleguide_pattern( 'filter-panel', '', '', true ); ?>
				<div class="ds-stack">
					<?php echo designstack_styleguide_pattern( 'resource-list' ); ?>
					<?php echo designstack_styleguide_pattern( 'pagination' ); ?>
				</div>
			</div>
		</div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">Карточка в разных ширинах</h3>
		<p class="sg-item__note">Карточка перестраивается по ширине своего контейнера, а не окна: слева — колонка шага на главной, справа — широкий ряд. Ширина раздела каталога (333 px) показана в вопросе V1.</p>
		<div class="sg-matrix">
			<div class="sg-cell sg-cell--narrow sg-one-card"><p class="sg-cell__label">узкая колонка</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'resource-card' ); ?></div></div>
			<div class="sg-cell sg-one-card"><p class="sg-cell__label">колонка витрины</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'resource-card' ); ?></div></div>
		</div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">Форма со всеми сообщениями</h3>
		<div class="sg-sandbox">
			<?php echo designstack_styleguide_pattern( 'error-summary' ); ?>
			<?php echo designstack_styleguide_pattern( 'suggest-form' ); ?>
			<?php echo designstack_styleguide_pattern( 'notice' ); ?>
		</div>
	</div>
</section>
<!-- /wp:html -->
