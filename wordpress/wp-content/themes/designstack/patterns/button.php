<?php
/**
 * Title: Кнопки: залитая, контурная, иконка
 * Slug: designstack/button
 * Categories: designstack
 * Inserter: no
 *
 * Одна залитая кнопка на экран (D50); контурная — везде остальное. Размер sm стоит в карточке ресурса.
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<div class="ds-row">
	<a class="ds-button ds-button--primary" href="#">Применить</a>
	<a class="ds-button ds-button--secondary" href="#" target="_blank" rel="noopener">Перейти на сайт<?php echo designstack_icon( 'external-link' ); ?><span class="screen-reader-text">откроется в новой вкладке</span></a>
	<a class="ds-button ds-button--secondary ds-button--sm" href="#">Показать аналог</a>
	<a class="ds-button ds-button--primary ds-button--lg" href="#">Предложить ресурс</a>
	<button type="button" class="ds-button ds-button--icon"><?php echo designstack_icon( 'search' ); ?><span class="screen-reader-text">Поиск</span></button>
	<button type="button" class="ds-button ds-button--primary" aria-busy="true" aria-disabled="true">Отправляем…</button>
	<button type="button" class="ds-button ds-button--secondary" disabled>Сбросить фильтры</button>
</div>
<!-- /wp:html -->
