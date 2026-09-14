<?php
/**
 * Title: Витрина: фидбэк
 * Slug: designstack/styleguide-feedback
 * Categories: designstack-styleguide
 * Inserter: no
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<section class="sg-section" id="sg-feedback">
	<h2 class="sg-section__title">Фидбэк</h2>
	<p class="sg-section__note">Статус — иконка и слово, цвет третий канал. Тонированный фон только у состояния записи и давности проверки; у меток цены, грейда, доступа и оплаты фон нейтральный.</p>

	<div class="sg-item">
		<h3 class="sg-item__title">badge</h3>
		<div class="sg-matrix sg-matrix--wide"><div class="sg-cell"><p class="sg-cell__label">цена, грейд, доступ, оплата, состояние записи, давность</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'badge' ); ?></div></div></div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">notice</h3>
		<div class="sg-matrix sg-matrix--wide"><div class="sg-cell"><p class="sg-cell__label">закрыт, условия изменились, давность, сбой, лимит, дубликат</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'notice' ); ?></div></div></div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">empty-state</h3>
		<p class="sg-item__note">Иллюстрации — линия цветом text-muted и один акцентный предмет; цвета из переменных, поэтому одна картинка работает в обеих темах.</p>
		<div class="sg-matrix sg-matrix--wide"><div class="sg-cell"><p class="sg-cell__label">фильтры, раздел, поиск, 404</p><div class="sg-cell__body"><?php echo designstack_styleguide_pattern( 'empty-state' ); ?></div></div></div>
	</div>
</section>
<!-- /wp:html -->
