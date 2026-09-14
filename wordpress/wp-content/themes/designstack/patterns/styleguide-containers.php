<?php
/**
 * Title: Витрина: контейнеры
 * Slug: designstack/styleguide-containers
 * Categories: designstack-styleguide
 * Inserter: no
 *
 * Сетку внутри сетки не показываем: состояния — по одной карточке в ячейке, а списки идут строкой во всю ширину,
 * где карточка выходит той же, что на сайте.
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<section class="sg-section" id="sg-containers">
	<h2 class="sg-section__title">Контейнеры</h2>
	<p class="sg-section__note">Карточка ресурса одна на все списки. Нижняя строка карточки — вопрос V1 в конце страницы.</p>

	<div class="sg-item">
		<h3 class="sg-item__title">resource-card · состояния</h3>
		<p class="sg-item__note">Порядок частей: логотип, название, подпись типа, состояние записи, вердикт, метки, теги, дата и кнопка.</p>
		<div class="sg-one-card">
			<?php echo designstack_styleguide_matrix( 'resource-card', 'ds-card', array( '' => 'по умолчанию', 'is-hover' => 'наведение', 'is-focus' => 'фокус' ) ); ?>
		</div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">resource-card · типы и состояния записи</h3>
		<p class="sg-item__note">Инструмент, учебный материал, ассет, сообщество; «Условия изменились», «Давно не проверяли», «Закрыт» с аналогом и без. У бесплатного ресурса метки оплаты нет.</p>
		<div class="sg-matrix sg-matrix--wide"><div class="sg-cell"><p class="sg-cell__label">сетка раздела: 3 колонки от 1200, 2 от 600, 1 меньше</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'resource-list' ); ?></div></div></div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">post-card</h3>
		<div class="sg-matrix sg-matrix--wide">
			<div class="sg-cell"><p class="sg-cell__label">по умолчанию</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'post-card' ); ?></div></div>
			<div class="sg-cell"><p class="sg-cell__label">наведение</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'post-card', 'ds-post-card', 'is-hover' ); ?></div></div>
		</div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">section-header</h3>
		<div class="sg-matrix sg-matrix--wide"><div class="sg-cell"><p class="sg-cell__label">простой, со строкой, со ссылкой</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'section-header' ); ?></div></div></div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">page-header</h3>
		<div class="sg-matrix sg-matrix--wide"><div class="sg-cell"><p class="sg-cell__label">с числом, с вводной строкой, с метой</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'page-header' ); ?></div></div></div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">entry-tiles</h3>
		<div class="sg-matrix sg-matrix--wide">
			<div class="sg-cell"><p class="sg-cell__label">по умолчанию</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'entry-tiles' ); ?></div></div>
			<div class="sg-cell"><p class="sg-cell__label">наведение</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'entry-tiles', 'ds-entry', 'is-hover' ); ?></div></div>
		</div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">issue-find и subscribe-cta</h3>
		<div class="sg-matrix sg-matrix--wide">
			<div class="sg-cell"><p class="sg-cell__label">находка недели</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'issue-find' ); ?></div></div>
			<div class="sg-cell"><p class="sg-cell__label">подписка</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'subscribe-cta' ); ?></div></div>
		</div>
	</div>
</section>
<!-- /wp:html -->
