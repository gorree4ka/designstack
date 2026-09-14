<?php
/**
 * Title: Чипсы: активные фильтры и выбор типа
 * Slug: designstack/filter-chips
 * Categories: designstack
 * Inserter: no
 *
 * Снимаемые чипсы стоят над списком (US-17), выбор одного типа — на странице темы (US-10).
 * Крестик — часть ссылки, его смысл несёт скрытая подпись.
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<div class="ds-stack">
	<div class="ds-chips ds-chips--removable">
		<a class="ds-button ds-button--secondary ds-button--sm ds-chips__toggle" href="#">Фильтры (3)</a>
		<a class="ds-chip" href="#"><span class="ds-chip__label">Прототипирование</span><?php echo designstack_icon( 'x' ); ?><span class="screen-reader-text">Снять фильтр: Прототипирование</span></a>
		<a class="ds-chip" href="#"><span class="ds-chip__label">Бесплатно</span><?php echo designstack_icon( 'x' ); ?><span class="screen-reader-text">Снять фильтр: Бесплатно</span></a>
		<a class="ds-chip" href="#"><span class="ds-chip__label">Оплачивается из РФ</span><?php echo designstack_icon( 'x' ); ?><span class="screen-reader-text">Снять фильтр: Оплачивается из РФ</span></a>
		<a class="ds-link ds-chips__reset" href="/tools/">Сбросить фильтры</a>
	</div>
	<nav class="ds-chips ds-chips--choice" aria-label="Тип ресурса">
		<span class="ds-chip" aria-current="page">Все</span>
		<a class="ds-chip" href="#">Инструменты</a>
		<a class="ds-chip" href="#">Учёба</a>
		<a class="ds-chip" href="#">Ассеты</a>
		<a class="ds-chip" href="#">Сообщества</a>
	</nav>
</div>
<!-- /wp:html -->
