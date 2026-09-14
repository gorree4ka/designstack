<?php
/**
 * Title: Витрина: действия
 * Slug: designstack/styleguide-actions
 * Categories: designstack-styleguide
 * Inserter: no
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<section class="sg-section" id="sg-actions">
	<h2 class="sg-section__title">Действия</h2>
	<p class="sg-section__note">Состояния показаны классами-двойниками: в ячейке «наведение» стоит тот же паттерн с классом is-hover, а не копия разметки.</p>

	<div class="sg-item">
		<h3 class="sg-item__title">button</h3>
		<p class="sg-item__note">По порядку: залитая «Применить», контурная «Перейти на сайт» с иконкой внешней ссылки, контурная малая для карточки, залитая большая, кнопка-иконка, отправка с aria-busy, недоступная.</p>
		<?php echo designstack_styleguide_matrix( 'button', 'ds-button', array( '' => 'по умолчанию', 'is-hover' => 'наведение', 'is-focus' => 'фокус' ) ); ?>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">link</h3>
		<?php echo designstack_styleguide_matrix( 'link', 'ds-link', array( '' => 'по умолчанию', 'is-hover' => 'наведение' ) ); ?>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">theme-toggle</h3>
		<p class="sg-item__note">Подпись одна — «Тёмная тема»; включена ли тема, сообщает состояние кнопки. Вторая кнопка показывает нажатое состояние.</p>
		<?php echo designstack_styleguide_matrix( 'theme-toggle', 'ds-theme-toggle', array( '' => 'светлая и тёмная', 'is-focus' => 'фокус' ) ); ?>
	</div>
</section>
<!-- /wp:html -->
