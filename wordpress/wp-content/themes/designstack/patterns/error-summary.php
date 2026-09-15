<?php
/**
 * Title: Сводка ошибок формы
 * Slug: designstack/error-summary
 * Categories: designstack
 * Inserter: no
 *
 * Стоит над формой, получает фокус после отправки с ошибками, каждая строка — ссылка на своё поле (D46, WCAG 2.2 AA).
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<div class="ds-error-summary" tabindex="-1">
	<p class="ds-error-summary__title"><?php echo designstack_icon( 'circle-x' ); ?>Проверьте форму</p>
	<ul class="ds-error-summary__list">
		<li><a class="ds-link" href="#ds-field-url">Это не похоже на адрес сайта. Проверьте, нет ли пробела или опечатки, например: https://excalidraw.com</a></li>
		<li><a class="ds-link" href="#ds-field-consent">Без согласия с политикой данных предложение не отправить</a></li>
		<li><a class="ds-link" href="#ds-field-comment">Комментарий длиннее 1000 знаков на 120 — сократи его</a></li>
	</ul>
</div>
<!-- /wp:html -->
